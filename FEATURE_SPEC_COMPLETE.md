# Feature Specification: Card-Based Review System - Part 2

## Cost & Performance Analysis (continued)

**Cost optimization strategies:**
- Cache unique stats (don't regenerate on every profile visit)
- Offer "quick analysis" (50 matches, $0.30) vs. "deep dive" (200 matches, $1.00)
- Batch processing during off-peak hours
- Use cheaper models for stat calculations, Claude for synthesis only

### Riot API Rate Limits

**Development Key Limits:**
- 20 requests/second
- 100 requests/2 minutes

**Typical request breakdown (100-match analysis):**
- PUUID lookup: 1 request
- Summoner data: 1 request
- Rank data: 1 request
- Match IDs: 1-2 requests (100 per call)
- Match details: 100 requests (bottleneck)
- **Total: ~105 requests over 2+ minutes**

**Timeline analysis (if enabled):**
- +100 requests for timelines
- **Total: ~205 requests over 4+ minutes**

**Optimization:**
- Fetch match IDs in bulk (100 per call)
- Parallel match detail fetching with rate limiter
- Cache match data (avoid re-fetching for 24 hours)

### Performance Targets

**Profile endpoint:** <5 seconds
- 3 requests (PUUID + summoner + rank)
- Unique stat uses existing match cache when possible

**Structured analysis:** 3-6 minutes
- 50 matches: ~2-3 minutes (mostly Riot API)
- 100 matches: ~4-5 minutes (Riot API + Bedrock)
- 200 matches: ~6-8 minutes (rate limit bound)

**Optimization opportunities:**
- WebSocket streaming for progress updates
- Progressive loading (show partial results)
- Background processing with job queue

---

## Implementation Checklist

### Phase 1: Core Cards (Week 1-2) ✓ Priority

**Backend Tasks:**
- [ ] Create `profile_service.py`
  - [ ] Implement `get_player_profile()`
  - [ ] Implement `_get_summoner_by_puuid()`
  - [ ] Implement `_get_summoner_rank()`
  - [ ] Implement `_generate_unique_stat()` with all categories
  - [ ] Add unit tests for unique stat generation

- [ ] Create `structured_analysis_service.py`
  - [ ] Implement `generate_structured_analysis()`
  - [ ] Add caching layer for repeated requests

- [ ] Modify `year_rewind_agent.py`
  - [ ] Add `output_format` parameter ("text" | "structured")
  - [ ] Create `STRUCTURED_ANALYSIS_PROMPT` template
  - [ ] Add `select_best_stat_highlights` agent tool
  - [ ] Test structured JSON output parsing

- [ ] Update `agent_tools.py`
  - [ ] Implement `calculate_all_stat_highlights()`
  - [ ] Implement percentile calculations for stats
  - [ ] Add rank-based benchmarks (Gold avg KDA, etc.)
  - [ ] Improve coaching insight specificity

- [ ] Update `main.py`
  - [ ] Add `GET /api/profile/{game_name}/{tag_line}` endpoint
  - [ ] Add `POST /api/analysis/structured/{game_name}/{tag_line}` endpoint
  - [ ] Add error handling and validation

- [ ] Testing
  - [ ] Write `test_profile_service.py`
  - [ ] Write `test_structured_analysis.py`
  - [ ] Test with various player profiles (ranked, unranked, one-tricks, etc.)
  - [ ] Validate JSON schema compliance

**Frontend Tasks (teammate):**
- [ ] Create profile page UI
- [ ] Create card components (champion mastery, stat highlights, coaching)
- [ ] Add loading states and animations
- [ ] Implement responsive design

**Success Criteria:**
- ✓ Profile endpoint returns valid data in <5 seconds
- ✓ Structured analysis endpoint returns valid JSON in <6 minutes
- ✓ Unique stat is interesting and accurate
- ✓ Stat highlights are diverse (not all same category)
- ✓ Coaching insights cite specific numbers and provide clear actions

---

### Phase 2: Enhanced Analysis (Week 3) - Medium Priority

**Backend Tasks:**
- [ ] Implement timeline analysis
  - [ ] Create `timeline_service.py`
  - [ ] Parse frame-by-frame events
  - [ ] Identify gold swings (>2000 gold)
  - [ ] Classify event types (teamfight, objective, solo kill)
  - [ ] Generate coaching notes for critical moments

- [ ] Add timeline endpoint
  - [ ] `GET /api/match/{match_id}/timeline/{puuid}`
  - [ ] Return structured timeline data

- [ ] Integrate timeline data into coaching insights
  - [ ] Reference specific game moments
  - [ ] Show timestamp links (e.g., "At 19:00, you...")

- [ ] Add rank progression tracking
  - [ ] Store historical rank data
  - [ ] Calculate rank changes over time
  - [ ] Provide chart data endpoint

**Testing:**
- [ ] Test timeline parsing on various game types
- [ ] Validate gold swing calculations
- [ ] Test coaching note generation quality

**Success Criteria:**
- ✓ Timeline analysis identifies 3-5 key moments per game
- ✓ Coaching insights reference specific timestamps
- ✓ Gold swing calculations are accurate

---

### Phase 3: OPGG/Meta Integration (Week 4) - Low Priority

**Backend Tasks:**
- [ ] Research OPGG MCP or API options
  - [ ] Test data availability and quality
  - [ ] Evaluate rate limits and costs

- [ ] Create `opgg_service.py`
  - [ ] Implement meta build fetching
  - [ ] Implement rank benchmark fetching
  - [ ] Add caching (update per patch)

- [ ] Add meta comparison agent tool
  - [ ] `compare_to_meta(champion, player_build)`
  - [ ] Calculate win rate differences

- [ ] Integrate into coaching insights
  - [ ] Reference meta builds when relevant
  - [ ] Show percentile rankings vs. rank average

**Testing:**
- [ ] Validate meta build accuracy
- [ ] Test caching and refresh logic
- [ ] Ensure coaching insights use meta data appropriately

**Success Criteria:**
- ✓ Meta builds are accurate and up-to-date
- ✓ Rank benchmarks show realistic percentiles
- ✓ Coaching insights reference meta when relevant

---

### Phase 4: Polish & Charts (Week 5) - Low Priority

**Backend Tasks:**
- [ ] Create `charts_service.py`
  - [ ] Calculate rank progression data
  - [ ] Calculate KDA trend with moving average
  - [ ] Format data for frontend chart libraries

- [ ] Add charts endpoint
  - [ ] `GET /api/charts/{game_name}/{tag_line}`
  - [ ] Return all chart data in one call

**Frontend Tasks (teammate):**
- [ ] Implement rank progression chart (Recharts)
- [ ] Implement champion win rate chart
- [ ] Implement KDA improvement curve
- [ ] Add chart interactivity (tooltips, zooming)
- [ ] Add social share buttons
- [ ] Polish animations and transitions

**Success Criteria:**
- ✓ Charts load smoothly with data
- ✓ Charts are interactive and responsive
- ✓ Share functionality works

---

## Data Schema Definitions

### Profile Response Schema

```typescript
interface ProfileResponse {
  success: boolean;
  profile?: {
    puuid: string;
    riot_id: string;
    summoner_id: string;
    summoner_icon_id: number;
    summoner_icon_url: string;
    summoner_level: number;
    rank: {
      tier: string;
      division: string;
      lp: number;
      wins: number;
      losses: number;
      win_rate: number;
      display: string;
    };
    unique_stat: {
      title: string;
      description: string;
      icon: string;
      category: string;
      value: number;
      percentile: number;
    };
  };
  error?: string;
}
```

### Structured Analysis Response Schema

```typescript
interface StructuredAnalysisResponse {
  success: boolean;
  analysis?: {
    highest_wr_champion: {
      name: string;
      champion_id: number;
      icon_url: string;
      games: number;
      wins: number;
      win_rate: number;
      avg_kda: number;
      primary_role: string;
      key_strength: string;
    };
    stat_highlights: Array<{
      id: string;
      category: 'vision' | 'combat' | 'mastery' | 'economy';
      title: string;
      value: string;
      unit: string;
      percentile: number;
      comparison: string;
      icon: string;
      trend: {
        direction: 'improving' | 'declining' | 'stable';
        change: string;
      } | null;
    }>;
    coaching_insights: Array<{
      id: string;
      priority: number;
      title: string;
      category: 'macro' | 'micro' | 'vision' | 'itemization' | 'mental';
      summary: string;
      data_points: string[];
      action_items: Array<{
        action: string;
        reasoning: string;
        difficulty: 'easy' | 'medium' | 'hard';
      }>;
    }>;
    metadata: {
      matches_analyzed: number;
      date_range: {
        start: string;
        end: string;
      };
      analysis_quality: string;
      processing_time_seconds: number;
    };
  };
  error?: string;
}
```

---

## Error Handling Patterns

### Common Error Scenarios

**1. Player Not Found (404)**
```json
{
  "success": false,
  "error": "Player Doublelift#NA1 not found"
}
```

**2. Rate Limited (429)**
```json
{
  "success": false,
  "error": "Rate limit exceeded. Please try again in 2 minutes.",
  "retry_after": 120
}
```

**3. Analysis Failed (500)**
```json
{
  "success": false,
  "error": "Analysis failed: Insufficient match data",
  "details": "Player has only 5 games, minimum 20 required"
}
```

**4. Bedrock Throttled (503)**
```json
{
  "success": false,
  "error": "AI service temporarily unavailable. Please retry.",
  "retry_after": 60
}
```

### Error Handling in Code

```python
# In profile_service.py
async def get_player_profile(game_name: str, tag_line: str) -> Dict[str, Any]:
    try:
        puuid = await riot_api.get_puuid_by_riot_id(game_name, tag_line)
        if not puuid:
            return {
                "success": False,
                "error": f"Player {game_name}#{tag_line} not found"
            }
        
        # ... rest of implementation
        
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timeout. Riot API is slow, please retry."
        }
    except Exception as e:
        print(f"Error in get_player_profile: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": "Internal server error. Please try again.",
            "details": str(e) if os.getenv('DEBUG') else None
        }
```

---

## Caching Strategy

### Cache Layers

**1. Match Data Cache (in-memory)**
- Cache match details for 24 hours
- Key: `match:{match_id}`
- Reduces repeated Riot API calls

**2. Profile Cache (in-memory)**
- Cache profile data for 1 hour
- Key: `profile:{puuid}`
- Allows quick page reloads

**3. Unique Stat Cache (in-memory)**
- Cache unique stat for 6 hours
- Key: `unique_stat:{puuid}`
- Expensive to calculate, changes slowly

**4. Analysis Cache (database/Redis)**
- Cache full analysis for 24 hours
- Key: `analysis:{puuid}:{date}`
- Allow users to revisit without re-analyzing

### Implementation Example

```python
# Simple in-memory cache with TTL
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expires_at = self._cache[key]
            if datetime.now() < expires_at:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int):
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expires_at)
    
    def clear(self):
        self._cache.clear()

# Global cache instance
cache = SimpleCache()

# Usage in profile_service.py
async def get_player_profile(game_name: str, tag_line: str) -> Dict[str, Any]:
    cache_key = f"profile:{game_name}#{tag_line}"
    
    # Check cache
    cached = cache.get(cache_key)
    if cached:
        print(f"✓ Profile cache hit for {game_name}#{tag_line}")
        return cached
    
    # Fetch fresh data
    profile = await _fetch_profile_data(game_name, tag_line)
    
    # Cache for 1 hour
    if profile.get('success'):
        cache.set(cache_key, profile, ttl_seconds=3600)
    
    return profile
```

---

## Monitoring & Observability

### Key Metrics to Track

**Performance Metrics:**
- Endpoint response times (p50, p95, p99)
- Riot API request count per minute
- Bedrock API request count per minute
- Cache hit rates
- Error rates by type

**Business Metrics:**
- Profiles generated per day
- Analyses completed per day
- Average matches analyzed per user
- Most common unique stats
- Most common coaching insights

### Logging Strategy

```python
import logging
import time
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def log_timing(func_name: str):
    """Decorator to log function execution time."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                logger.info(f"{func_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"{func_name} failed after {duration:.2f}s: {e}")
                raise
        return wrapper
    return decorator

# Usage
@log_timing("profile_generation")
async def get_player_profile(game_name: str, tag_line: str):
    # ... implementation
    pass
```

### Health Check Enhancement

```python
# In main.py
@app.get("/api/health")
async def health_check():
    """Enhanced health check with detailed status."""
    from services.rate_limiter import rate_limiter
    from services.bedrock_rate_limiter import bedrock_rate_limiter
    
    riot_stats = rate_limiter.get_stats()
    bedrock_stats = bedrock_rate_limiter.get_stats()
    
    # Calculate availability
    riot_available = riot_stats['tokens_available'] > 5
    bedrock_available = bedrock_stats.get('requests_available', True)
    
    status = "healthy" if (riot_available and bedrock_available) else "degraded"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "services": {
            "riot_api": {
                "status": "healthy" if riot_available else "limited",
                "requests_available": riot_stats['tokens_available'],
                "rate_limit": f"{riot_stats['requests_in_window']}/{riot_stats['window_limit']} in 2min"
            },
            "bedrock": {
                "status": "healthy" if bedrock_available else "throttled",
                "recent_throttles": bedrock_stats.get('throttle_count', 0)
            }
        },
        "cache": {
            "profile_hits": cache._cache.get('stats_profile_hits', 0),
            "profile_misses": cache._cache.get('stats_profile_misses', 0)
        }
    }
```

---

## Deployment Considerations

### Environment Variables

```bash
# backend/.env
RIOT_API_KEY=RGAPI-xxxxx-xxxxx-xxxxx
AWS_ACCESS_KEY_ID=AKIAXXXXX
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_REGION=us-east-1

# Optional
ENABLE_CACHE=true
CACHE_TTL_SECONDS=3600
DEBUG=false
MAX_MATCHES_LIMIT=200
```

### Docker Setup (Future)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### AWS Lambda Deployment (Future)

**Challenges:**
- Cold start times (3-5 seconds)
- 15-minute execution limit (may not be enough for 200 matches)
- Memory limits (need 2GB+ for match processing)

**Recommendation:** Use EC2 or ECS instead for this workload

---

## Future Enhancements

### Short-term (Next 3 months)
1. **Progressive Loading**: Stream results as they're generated
2. **Comparison Mode**: Compare two players side-by-side
3. **Team Analysis**: Analyze full team performance in a game
4. **Custom Date Ranges**: Analyze specific time periods

### Medium-term (3-6 months)
1. **Clip Integration**: Show highlight clips from key moments
2. **Voice Narration**: AI-generated audio commentary
3. **Champion-Specific Insights**: Matchup-specific advice
4. **Build Recommendations**: Optimal item paths based on game state

### Long-term (6+ months)
1. **Live Game Analysis**: Real-time coaching during matches
2. **Replay Analysis**: Parse actual game replays (not just API data)
3. **Mobile App**: Native iOS/Android apps
4. **Social Features**: Share, compare, compete with friends

---

## Risk Mitigation

### Technical Risks

**Risk 1: Bedrock Throttling**
- **Impact:** Users get errors, poor experience
- **Mitigation:** Implement queue system, retry logic, show progress
- **Fallback:** Use cached results, offer "quick analysis" mode

**Risk 2: Riot API Rate Limits**
- **Impact:** Can't fetch match data, analysis fails
- **Mitigation:** Aggressive caching, batch requests, exponential backoff
- **Fallback:** Analyze fewer matches (50 instead of 100)

**Risk 3: Cost Overruns**
- **Impact:** AWS bills exceed budget
- **Mitigation:** Set billing alerts, rate limit users, implement freemium model
- **Fallback:** Disable service temporarily, require registration

### Quality Risks

**Risk 1: Generic Coaching Insights**
- **Impact:** Users don't find value, don't share
- **Mitigation:** Improve prompts, add examples, validate specificity
- **Fallback:** Manual review and prompt refinement

**Risk 2: Inaccurate Stats**
- **Impact:** Users lose trust, negative reviews
- **Mitigation:** Extensive testing, validation checks, user feedback loop
- **Fallback:** Add disclaimer, allow users to report issues

---

## Success Metrics

### MVP Success Criteria (End of Phase 1)

**Technical:**
- ✓ Profile endpoint <5 second response time
- ✓ Analysis endpoint <6 minute response time
- ✓ <1% error rate on valid requests
- ✓ All endpoints return valid schema-compliant JSON

**Quality:**
- ✓ 80%+ of unique stats are interesting/accurate (manual review)
- ✓ 90%+ of coaching insights cite specific numbers
- ✓ 100% of action items are specific and actionable

**User Experience:**
- ✓ Frontend teammate can build UI with API responses
- ✓ API documentation is complete and accurate
- ✓ Error messages are helpful and actionable

### Post-Launch Success Metrics

**Engagement:**
- 100+ unique users in first week
- 10+ shares on social media
- Average 2+ analyses per returning user

**Quality:**
- Net Promoter Score (NPS) > 40
- <5% negative feedback rate
- User-reported accuracy issues <2%

**Performance:**
- 99% uptime
- <0.5% error rate
- p95 response time <7 minutes

---

## Summary & Next Steps

### What We've Designed

A comprehensive card-based analysis system that:
1. Shows player profile with rank and unique stat
2. Generates structured, actionable coaching insights
3. Highlights top champion and interesting stats
4. Provides specific, data-driven improvement recommendations
5. Scales to handle rate limits and costs

### Immediate Next Steps

**Week 1: Backend Foundation**
1. Create `profile_service.py` and implement unique stat generation
2. Modify `year_rewind_agent.py` for structured output
3. Create `structured_analysis_service.py`
4. Add new endpoints to `main.py`
5. Write unit tests

**Week 2: Testing & Refinement**
1. Test with 10+ diverse player profiles
2. Refine coaching insight prompts based on output quality
3. Validate JSON schema compliance
4. Document API for frontend team
5. Deploy to development environment

**Week 3: Frontend Integration**
1. Frontend teammate builds UI components
2. Integrate backend API with frontend
3. Add loading states and error handling
4. Test end-to-end flow
5. Gather initial feedback

### Questions to Answer Before Starting

1. **Caching strategy:** In-memory only or add Redis/database?
2. **Rate limiting:** Should we limit users (e.g., 3 analyses per day)?
3. **Cost management:** Set per-user analysis limit? Require registration?
4. **Timeline analysis:** Include in Phase 1 or defer to Phase 2?
5. **OPGG integration:** Is MCP available? Do we need it for MVP?

---

## Appendix: Example API Responses

### Example Profile Response

```json
{
  "success": true,
  "profile": {
    "puuid": "RCT8OLZKBBhtGFHE6y4z3NWaGCGQwExqXZwvvCf6sBRQOQxvHFaxO-DZlLQ_L4Dng9xI3DHDmXmWQg",
    "riot_id": "Doublelift#NA1",
    "summoner_id": "hNk_abcdefg123456",
    "summoner_icon_id": 4392,
    "summoner_icon_url": "https://ddragon.leagueoflegends.com/cdn/14.1.1/img/profileicon/4392.png",
    "summoner_level": 347,
    "rank": {
      "tier": "MASTER",
      "division": "I",
      "lp": 247,
      "wins": 156,
      "losses": 132,
      "win_rate": 54.2,
      "display": "Master I • 247 LP"
    },
    "unique_stat": {
      "title": "ADC Specialist",
      "description": "87 games on Jinx with 62% win rate - True mastery",
      "icon": "🎯",
      "category": "mastery",
      "value": 87,
      "percentile": 95
    }
  }
}
```

### Example Structured Analysis Response

```json
{
  "success": true,
  "analysis": {
    "highest_wr_champion": {
      "name": "Jinx",
      "champion_id": 222,
      "icon_url": "https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Jinx.png",
      "games": 87,
      "wins": 54,
      "win_rate": 62.1,
      "avg_kda": 6.2,
      "primary_role": "BOTTOM",
      "key_strength": "Consistent damage output with 28% team damage share and excellent late-game scaling"
    },
    "stat_highlights": [
      {
        "id": "high_kda",
        "category": "combat",
        "title": "Elite KDA",
        "value": "5.8",
        "unit": "KDA",
        "percentile": 92,
        "comparison": "Top 8% of Master ADCs (avg 4.2)",
        "icon": "⚔️",
        "trend": {
          "direction": "improving",
          "change": "+1.2 from first 50 games"
        }
      },
      {
        "id": "vision_excellence",
        "category": "vision",
        "title": "Vision Excellence",
        "value": "1.4",
        "unit": "vision/min",
        "percentile": 88,
        "comparison": "Excellent for ADC role (avg 0.9)",
        "icon": "👁️",
        "trend": {
          "direction": "stable",
          "change": "Consistent across season"
        }
      },
      {
        "id": "jinx_mastery",
        "category": "mastery",
        "title": "Jinx One-Trick",
        "value": "87",
        "unit": "games on Jinx",
        "description": "62% win rate demonstrates championship-level mastery",
        "icon": "🎯",
        "trend": null
      }
    ],
    "coaching_insights": [
      {
        "id": "early_game_consistency",
        "priority": 1,
        "title": "Reduce Early Deaths",
        "category": "micro",
        "summary": "Your laning phase deaths (2.1 per game before 15 min) are high for Master tier. 73% occur during 2v2 trades when enemy jungler arrives. This costs you 450-600 gold in lost CS and experience.",
        "data_points": [
          "Deaths 0-15 min: 2.1 per game (Master ADC avg: 1.3)",
          "73% of early deaths from enemy jungler ganks",
          "Average gold deficit after early death: -520 gold",
          "Games with 0-1 early deaths: 71% win rate vs. 48% with 2+"
        ],
        "action_items": [
          {
            "action": "Ward tribush or river at 2:45 (before first gank timing)",
            "reasoning": "Enemy junglers typically path bot at 3:00-3:30, your ward timing is late (avg 3:15)",
            "difficulty": "easy"
          },
          {
            "action": "Track enemy jungler clear: if blue side, expect bot gank at 3:15",
            "reasoning": "73% of your early deaths are preventable with proper jungle tracking",
            "difficulty": "medium"
          },
          {
            "action": "Back off when support roams - 18% of deaths happen in 1v2",
            "reasoning": "You stay in lane for CS but die solo, losing more gold than you farm",
            "difficulty": "easy"
          }
        ]
      },
      {
        "id": "objective_setup",
        "priority": 2,
        "title": "Improve Baron Setup",
        "category": "macro",
        "summary": "Your Baron control (3.8 per 10 games) is low for Master tier (avg 5.2). Games with Baron secured have 89% win rate, but you're missing opportunities. Vision setup at 22-24 minutes is inconsistent.",
        "data_points": [
          "Baron control: 3.8 per 10 games (Master avg: 5.2)",
          "Win rate with Baron: 89% vs. 42% without",
          "Vision score 20-25 min: 6.2 (low for Baron setup phase)",
          "Baron attempts without vision: 4 (resulted in 3 losses)"
        ],
        "action_items": [
          {
            "action": "Place deep ward in enemy jungle at 20:00 (before Baron spawns)",
            "reasoning": "You have no vision in enemy jungle during Baron window (20-25 min)",
            "difficulty": "medium"
          },
          {
            "action": "Buy control ward every back from 18 minutes onward",
            "reasoning": "Control ward purchases drop 40% after 20 min, exactly when Baron fights happen",
            "difficulty": "easy"
          }
        ]
      }
    ],
    "metadata": {
      "matches_analyzed": 187,
      "date_range": {
        "start": "2024-01-15",
        "end": "2024-12-20"
      },
      "analysis_quality": "high",
      "processing_time_seconds": 324
    }
  }
}
```

---

## End of Specification

This feature spec provides a complete blueprint for implementing the card-based review system. Focus on Phase 1 first (core cards), then iterate based on user feedback and performance data.

**Key takeaways:**
1. Structured output enables beautiful UI components
2. AI must cite specific numbers for credibility
3. Unique stats create shareability and engagement
4. Caching and rate limiting are critical for scale
5. Testing and validation ensure quality

Good luck with implementation! 🚀
