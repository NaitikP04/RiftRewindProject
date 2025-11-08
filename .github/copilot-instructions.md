# Rift Rewind - AI Agent Instructions

League of Legends year-end review generator with AI analysis. FastAPI backend + Next.js frontend creating Spotify Wrapped-style dashboards.

## Architecture Overview

**Two-Phase Data Flow:**
1. **Profile Service** (`backend/services/profile_service.py`) - Fast (<5s): summoner info, rank, main role
2. **Analysis Service** (`backend/services/structured_analysis_service.py`) - Deep (3-6 min): match history + Claude Sonnet 4 AI insights

**Key Components:**
- `backend/services/riot_api.py` - Riot API client with rate limiting (20/s, 100/2min)
- `backend/services/rate_limiter.py` - Riot API rate limiter (Personal Key limits)
- `backend/services/bedrock_rate_limiter.py` - AWS Bedrock throttling handler with exponential backoff
- `backend/services/agent_tools.py` - Match data extraction and champion/playstyle analysis functions
- `backend/services/structured_analysis_service.py` - Main AI analysis coordinator using Claude Sonnet 4
- `frontend/lib/api-client.ts` - Backend API client with typed responses

## Critical Patterns

### Rate Limiting Strategy
**All Riot API calls MUST go through `rate_limiter`:**
```python
await rate_limiter.wait_if_needed()  # BEFORE request
rate_limiter.record_request()         # AFTER successful request
```

**All Bedrock calls MUST use `bedrock_rate_limiter`:**
```python
await bedrock_rate_limiter.wait_if_needed(is_retry=False)
bedrock_rate_limiter.record_request(success=True)
```
- Uses exponential backoff (5s → 120s max) with jitter on throttling
- Track throttles with `record_throttle()` for backoff adjustment

### Retry-Safe Caching (Critical!)
The `year_rewind_agent.py` implements a **global cache** (`_analysis_cache`) that survives Bedrock throttling retries:
```python
# Cache prevents re-fetching Riot data on AI retries
_analysis_cache = {
    "matches_data": [],          # Match details (expensive to fetch)
    "performance_trends": None,  # Calculated stats
    "champion_pool": None,       # Champion analysis
    "playstyle": None,           # Playstyle personality
    "current_puuid": None        # Player ID for cache validation
}
```
**When adding new tools**: Check cache first, compute only if missing. This is why retries don't cause 200-300% slowdown.

### AI Model Selection
- **Current**: Claude Sonnet 4 via inference profile `us.anthropic.claude-sonnet-4-20250514-v1:0`
- **Alternative**: Claude 3 Haiku `anthropic.claude-3-haiku-20240307-v1:0` (higher limits, lower quality)
- Located in `structured_analysis_service.py` line ~305

### Match Data Flow
```
User Input → riot_api.get_puuid_by_riot_id()
           → agent_tools.fetch_matches_intelligently()  # Prioritizes ranked
           → agent_tools.get_match_details_batch()      # Batch fetching
           → agent_tools.calculate_performance_trends() # Stats extraction
           → _generate_deep_ai_analysis()               # AI insights
           → Frontend Dashboard
```

## Development Workflows

### Local Development (Windows)
```bash
# Terminal 1 - Backend with hot reload
start_backend.bat
# Or: cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend with hot reload
start_frontend.bat
# Or: cd frontend && npm run dev
```

**Environment Files Required:**
- `backend/.env` - RIOT_API_KEY, AWS credentials
- `frontend/.env.local` - NEXT_PUBLIC_API_URL=http://localhost:8000

### Testing Workflow
```bash
cd tests

# Test AI agent with retry-safe caching
python test_agent.py

# Test rate limiter behavior
python test_rate_limits.py

# Test structured analysis endpoint
python test_structured_analysis.py

# Check Bedrock throttling handling
python test_throttling_behavior.py
```

**Test accounts in `test_agent.py`**: Use real NA region Riot IDs

### Debugging AI Quality
**Modify AI prompt** in `structured_analysis_service.py` line ~200:
```python
async def _generate_deep_ai_analysis(...):
    prompt = f"""You are an expert League of Legends analyst...
    # Edit this prompt to improve insight quality
    """
```
Backend auto-reloads with `--reload` flag. Test via dashboard or `test_structured_analysis.py`.

### API Health Check
```bash
curl http://localhost:8000/api/health
```
Returns Riot API rate limiter stats (requests/second, requests/2min capacity).

## Project-Specific Conventions

### Backend Service Boundaries
- **DO NOT** make direct Riot API calls from `main.py` - use service modules
- **DO NOT** import `agent_tools` directly in endpoints - go through analysis services
- **ALWAYS** use async/await for external API calls (Riot, Bedrock)

### Frontend Fetch Pattern
Use typed API client (`lib/api-client.ts`), never direct fetch in components:
```typescript
import { fetchProfile, fetchAnalysis } from "@/lib/api-client"
// Returns typed ProfileResponse or AnalysisResponse
```

### Error Handling Pattern
```python
# Backend endpoints return structured errors
return {
    "success": False,
    "error": "descriptive message"
}
```
Frontend checks `success` field before accessing `data`/`profile`.

### Champion Data
- Champion names come from match data (no static data dependency)
- Champion IDs NOT used - display names only
- Icon URLs built from DDragon CDN (see `avatar-utils.ts`)

## Integration Points

### Riot API Dependencies
- **Account-V1**: Riot ID → PUUID conversion (regional endpoint: `americas.api.riotgames.com`)
- **Match-V5**: Match history and detailed match data (regional endpoint)
- **Summoner-V4**: Profile icon, level (platform endpoint: `na1.api.riotgames.com`)
- **League-V4**: Ranked stats (tier, division, LP, W/L)

**Region Scope**: NA only (`na1` platform, `americas` routing). Expansion requires platform detection logic.

### AWS Bedrock Integration
- **Service**: `bedrock-runtime`
- **Region**: us-east-1 (inference profile region)
- **Model**: Claude Sonnet 4 via cross-region inference profile (reduces throttling)
- **Auth**: IAM credentials via boto3 (from env vars)
- **Error Handling**: Catch `ThrottlingException`, `TooManyRequestsException` and retry with backoff

### Frontend → Backend Communication
- **CORS**: Backend allows `http://localhost:3000` only
- **Endpoints**: `/api/profile/` (fast), `/api/analysis/` (slow with POST)
- **Timeout**: Frontend uses 300s timeout for analysis endpoint (expected 3-6 min)

## Common Pitfalls

1. **Adding new match analysis**: Update `agent_tools.extract_comprehensive_player_data()`, not endpoints
2. **Changing rate limits**: Edit `rate_limiter.py` constructor, not inline calls
3. **AI prompt changes**: Must restart backend (or save file with `--reload`)
4. **Missing .env**: Backend startup script checks and fails fast with clear message
5. **Cache invalidation**: Call `clear_analysis_cache()` in `year_rewind_agent.py` for fresh analysis
6. **Throttling loops**: Always use `is_retry=True` when calling `bedrock_rate_limiter.wait_if_needed()` in retry blocks

## Key Files for Common Tasks

**Improve AI insights**: `backend/services/structured_analysis_service.py` line ~200-280  
**Add new stats**: `backend/services/agent_tools.py` → `extract_comprehensive_player_data()`  
**Change rate limits**: `backend/services/rate_limiter.py` class attributes  
**Modify dashboard layout**: `frontend/features/dashboard/DashboardContainer.tsx`  
**Add UI components**: `frontend/components/ui/` (shadcn-based)  
**Update API types**: `frontend/lib/types.ts` + `api-client.ts` interfaces

## Performance Characteristics

- **Profile load**: <5 seconds (3-4 Riot API calls)
- **Analysis**: 3-6 minutes (50-100 matches → 100-200 API calls + 1 Bedrock call)
- **Match fetching**: ~30-60s (rate limited by Riot API)
- **AI generation**: ~10-30s (Claude Sonnet 4 inference)
- **Retry overhead**: 0% (thanks to retry-safe caching)

**Bottleneck**: Riot API rate limits (20/s, 100/2min on Personal Key). Production key (500/s, 30k/10min) eliminates this.
