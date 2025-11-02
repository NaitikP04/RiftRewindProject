# Technology Stack

## Architecture Overview

Full-stack application with separate frontend and backend services:

- **Frontend**: Next.js 15+ with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python 3.8+
- **AI/ML**: AWS Bedrock (Claude 3.5 Sonnet) with LangChain
- **Data Sources**: Riot Games API
- **Caching**: In-memory retry-safe caching system

## Frontend Stack

- **Framework**: Next.js 15+ with App Router
- **Language**: TypeScript with relaxed strict mode
- **Styling**: Tailwind CSS 4.1+
- **UI**: React 18+ with server components
- **Build**: Next.js built-in bundling and optimization

## Backend Stack

- **Framework**: FastAPI with async/await support
- **Language**: Python 3.8+
- **HTTP Client**: httpx for async requests
- **AI Framework**: LangChain with AWS Bedrock integration
- **Environment**: python-dotenv for configuration
- **Data Processing**: pandas and numpy for match analysis

## AI Architecture (DETAILED)

### LangChain Agent System

- **Framework**: LangChain with tool-calling agent pattern
- **Model**: Claude 3.5 Sonnet v2 (anthropic.claude-3-5-sonnet-20241022-v2:0)
- **Agent Tools**:
  - `fetch_player_matches`: Smart match ID retrieval with ranked prioritization
  - `get_detailed_match_data`: Batch fetching with rate limit handling
  - `analyze_performance_trends`: Temporal analysis of KDA, CS, vision, gold efficiency
  - `analyze_champion_pool`: Champion mastery, role distribution, win rates
  - `identify_playstyle`: Personality profiling (Duelist, Carry, Vision Master, etc.)

### Rate Limiting Strategy

**Two-Layer System:**

1. **Riot API Rate Limiter** (`rate_limiter.py`)

   - Personal key limits: 20 req/s, 100 req/2min
   - Token bucket algorithm with request queuing
   - Automatic retry with exponential backoff on 429s

2. **Bedrock Rate Limiter** (`bedrock_rate_limiter.py`)
   - Dynamic throttling based on observed patterns
   - Exponential backoff on ThrottlingException
   - Retry-safe: Doesn't re-fetch Riot data on AI throttles

**Typical Performance:**

- 50 matches: ~2 minutes (mostly Riot API)
- 200 matches: ~4-5 minutes (Riot API + AI analysis)
- Bedrock calls: 5-15 invocations per review (tool calls + synthesis)

### Data Pipeline

````
User Input (Riot ID)
    ↓
PUUID Lookup (Riot Account API)
    ↓
Match ID Fetching (intelligent sampling)
    ├─ Prioritize ranked games
    ├─ Sample match types
    └─ Select optimal subset
    ↓
Batch Match Detail Fetching (rate limited)
    ↓
Data Enrichment (extract player stats, challenges, timelines)
    ↓
LangChain Agent Analysis
    ├─ Tool 1: Fetch matches
    ├─ Tool 2: Load details
    ├─ Tool 3: Analyze trends
    ├─ Tool 4: Examine champion pool
    ├─ Tool 5: Identify playstyle
    └─ Synthesis: Generate review
    ↓
Structured Output (JSON + Markdown review)

## Key Dependencies

### Frontend

```json
{
  "next": "^15.5.4",
  "react": "^18.0.0",
  "tailwindcss": "^4.1.13",
  "typescript": "5.9.2"
}
````

### Backend

```
fastapi
uvicorn[standard]
httpx
python-dotenv
boto3
langchain
langchain-aws
pydantic
numpy
pandas
```

## Development Commands

### Setup

```bash
# Full project setup
npm run setup

# Manual setup
npm install
cd backend && pip install -r requirements.txt
```

### Development

```bash
# Frontend (port 3000)
npm run dev

# Backend (port 8000)
npm run backend
# OR manually:
cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Testing

```bash
# Run tests
npm test
# OR manually:
python tests/test_agent.py
python tests/test_rate_limits.py
python tests/test_throttling_behavior.py
```

### Production

```bash
# Build frontend
npm run build
npm start
```

## Environment Configuration

Required environment variables in `backend/.env`:

```env
RIOT_API_KEY=your_riot_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
```

## Rate Limiting & Performance

- **Riot API**: 20 req/s, 100 req/2min (Personal key limits)
- **AWS Bedrock**: ~5-10 req/s with intelligent throttling
- **Analysis Time**: 3-5 minutes for 200+ matches
- **Caching**: Retry-safe to prevent re-fetching on failures

## Code Style Guidelines

- **Python**: Follow FastAPI patterns, use async/await, type hints with Pydantic
- **TypeScript**: Use strict typing, prefer server components, minimal client-side JS
- **Styling**: Tailwind utility classes, dark theme default
- **Error Handling**: Comprehensive try/catch with meaningful HTTP status codes
