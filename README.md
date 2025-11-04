# Rift Rewind# Rift Rewind



AI-powered League of Legends year-end review generator for Riot Games API Challenge 2025. Creates personalized Spotify Wrapped-style dashboards with deep AI insights using Claude Sonnet 4.AI-powered League of Legends match analysis and year-end review generator. Creates personalized Spotify Wrapped-style reviews using player match history and performance data.



## Features## Features



- **Two-Phase Data Flow**: Fast profile load (<5s) + deep AI analysis (3-6 min)- **AI-Powered Analysis**: Uses AWS Bedrock (Claude) to generate personalized year-end reviews

- **Accurate Match Statistics**: Real champion stats from match history (not estimates)- **Smart Match Fetching**: Prioritizes ranked matches for competitive insights

- **Deep AI Insights**: Claude Sonnet 4 generates unique, personalized analysis with specific numbers- **Performance Trends**: Analyzes KDA, CS, vision, and improvement patterns

- **Challenge System Integration**: Extracts Riot's challenge data for deeper insights- **Champion Pool Analysis**: Identifies main champions, win rates, and playstyle

- **Polished Frontend**: Glass-morphism UI with smooth animations and responsive design- **Retry-Safe Caching**: Prevents re-fetching data on API throttling

- **Rate Limit Optimization**: Intelligent handling of Riot API (20/s, 100/2min) and Bedrock limits- **Rate Limit Optimization**: Intelligent handling of Riot API and Bedrock limits



## Architecture## Architecture



- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind CSS + Framer Motion- **Frontend**: Next.js with TypeScript and Tailwind CSS

- **Backend**: FastAPI (Python 3.12)- **Backend**: FastAPI with Python

- **AI**: AWS Bedrock - Claude Sonnet 4 (`anthropic.claude-sonnet-4-20250514-v1:0`)- **AI Agent**: AWS Bedrock (Claude 3 Haiku) with LangChain

- **Data Source**: Riot Games API (Match-V5, Summoner-V4, League-V4)- **Data Source**: Riot Games API

- **Region**: North America only (for hackathon scope)- **Caching**: In-memory retry-safe caching system



## Prerequisites## Prerequisites



- Node.js (v18+)- Node.js (v18+)

- Python 3.12+- Python (v3.8+)

- Riot Games API Key (Personal Key sufficient)- Riot Games API Key

- AWS Account with Bedrock access to Claude Sonnet 4- AWS Account with Bedrock access



## Quick Start## Setup



### 1. Environment Setup### 1. Environment Configuration



**Backend** - Create `backend/.env`:Create `backend/.env`:



```env```env

RIOT_API_KEY=your_riot_api_key_hereRIOT_API_KEY=your_riot_api_key_here

AWS_ACCESS_KEY_ID=your_aws_access_keyAWS_ACCESS_KEY_ID=your_aws_access_key

AWS_SECRET_ACCESS_KEY=your_aws_secret_keyAWS_SECRET_ACCESS_KEY=your_aws_secret_key

AWS_REGION=us-east-1AWS_REGION=us-west-2

``````



**Frontend** - Create `frontend/.env.local`:### 2. Installation



```env```bash

NEXT_PUBLIC_API_URL=http://localhost:8000# Install dependencies

```npm install

cd backend && pip install -r requirements.txt

### 2. Installation & Run```



**Option A: Using startup scripts (Windows)**### 3. Run Application

```bash

# Terminal 1 - Backend```bash

start_backend.bat# Backend (Terminal 1)

cd backend

# Terminal 2 - Frontend  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

start_frontend.bat

```# Frontend (Terminal 2)

npm run dev

**Option B: Manual**```

```bash

# Install backend dependencies## API Endpoints

cd backend

pip install -r requirements.txt### Core Endpoints



# Install frontend dependencies- `GET /api/player/{game_name}/{tag_line}` - Get player PUUID

cd ../frontend- `POST /api/year-rewind/{game_name}/{tag_line}` - Generate AI review

npm install- `GET /api/health` - Health check with rate limiter stats



# Run backend (Terminal 1)### Usage Example

cd backend

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000```bash

curl -X POST "http://localhost:8000/api/year-rewind/Faker/KR1"

# Run frontend (Terminal 2)```

cd frontend

npm run dev## Testing

```

```bash

### 3. Access Application# Run all tests

python tests/test_agent.py

- **Frontend**: http://localhost:3000

- **Backend API**: http://localhost:8000# Test rate limits

- **API Docs**: http://localhost:8000/docspython tests/test_rate_limits.py



### 4. Test It# Test caching behavior

python tests/test_throttling_behavior.py

Enter a Riot ID on the landing page:```

- Format: `GameName#TAG`

- Example: `i will int#akali` (NA region)## Performance



## API Endpoints| Metric              | Current     | Optimized           |

| ------------------- | ----------- | ------------------- |

### User-Facing Endpoints| Analysis Time       | 3-5 minutes | 1-2 minutes         |

| Retry Overhead      | 0% (cached) | Previously 200-300% |

- `GET /api/profile/{game_name}/{tag_line}` - Fast profile fetch (<5s)| Rate Limit Handling | Intelligent | Previously basic    |

  - Returns: Summoner icon, level, rank, main role

  ## Current Limitations & Improvements

- `POST /api/analysis/{game_name}/{tag_line}` - Deep AI analysis (3-6 min)

  - Returns: Top champions, stat highlights, AI insights, personality### Rate Limits

  - Query param: `num_matches` (default: 100)

- **Riot API**: 20 req/s, 100 req/2min (Personal key)

### System Endpoints- **Bedrock**: ~5-10 req/s (Default limits)



- `GET /api/health` - Health check with rate limiter stats**Improvements**:

- `GET /` - API version info

- Apply for Riot Production API key (500 req/s, 30k req/10min)

## Data Flow- Request Bedrock rate limit increase

- Switch to Claude 3.5 Sonnet for better quality

```

User Input (Riot ID)### Model Options

    ↓

Phase 1: Profile Service (fast)- **Current**: Claude 3 Haiku (fast, higher limits)

    - Get PUUID from Riot ID- **Upgrade**: Claude 3.5 Sonnet (better quality, lower limits)

    - Fetch summoner data (icon, level)- **Premium**: Claude 3 Opus (highest quality, lowest limits)

    - Get ranked stats (tier, division, LP, winrate)

    - Determine main role (last 10 matches)### Future Enhancements

    ↓

Phase 2: Analysis Service (deep)- **OP.GG MCP Integration**: Real-time meta insights and build recommendations

    - Fetch 50-100 match history- **Champion Synergy Analysis**: Team composition suggestions

    - Extract comprehensive stats (KDA, CS, vision, damage, gold)- **Trend Analysis**: Performance improvement tracking over time

    - Analyze champion pool (games, winrates, playstyles)- **Multi-Region Support**: Support for all Riot regions

    - Extract challenge data (lane dominance, vision advantage)

    - Calculate timeline patterns (early vs late game)## Project Structure

    - Generate AI insights with Claude Sonnet 4

    ↓```

Frontend DashboardRiftRewindProject/

    - Display profile with rank├── app/                    # Next.js frontend

    - Show top 3 champions (accurate stats)├── backend/

    - Highlight 3 best stats│   ├── app/main.py        # FastAPI application

    - Show AI-generated deep insight│   ├── services/

    - Display personality type│   │   ├── year_rewind_agent.py    # Main AI agent

```│   │   ├── agent_tools.py          # Analysis tools

│   │   ├── riot_api.py             # Riot API client

## Project Structure│   │   ├── rate_limiter.py         # Riot API rate limiting

│   │   └── bedrock_rate_limiter.py # Bedrock rate limiting

```│   └── .env               # Environment variables

RiftRewindProject/├── tests/                 # Test suite

├── frontend/                   # Next.js application└── README.md

│   ├── app/                    # App router pages```

│   ├── components/             # UI components

│   ├── features/               # Feature modules## Contributing

│   ├── lib/                    # Utilities

│   │   ├── api-client.ts      # Backend API integration1. **Model Experimentation**: Test different models for quality and speed

│   │   └── usePlayerDataFetch.ts2. **OP.GG Integration**: Add real-time meta analysis using OP.GG MCP

│   └── .env.local             # Frontend config3. **Performance Optimization**: Figure out a way to reduce analysis time.

│4. **UI/UX**: Improve frontend design and user experience

├── backend/                    # FastAPI application5. **Additional Features**: Champion recommendations, team analysis, etc.

│   ├── app/6. **Tool and System Prompts**: Work on finding errors and enhancing the prompts for the agent tools and the system prompt that initalises the workflow.

│   │   └── main.py            # API endpoints

│   ├── services/## Rate Limit Optimization

│   │   ├── profile_service.py          # Fast profile fetching

│   │   ├── structured_analysis_service.py  # AI analysisThe system includes intelligent rate limiting for both APIs:

│   │   ├── agent_tools.py              # Data extraction tools

│   │   ├── riot_api.py                 # Riot API client- **Riot API**: Respects 20 req/s and 100 req/2min limits

│   │   ├── rate_limiter.py             # Riot API rate limiting- **Bedrock**: Handles throttling with exponential backoff

│   │   └── bedrock_rate_limiter.py     # Bedrock throttling- **Caching**: Prevents re-fetching on retries (major performance improvement)

│   └── .env                   # Backend config

│## Troubleshooting

├── tests/                      # Test scripts

├── start_backend.bat          # Backend startup script### Issues

└── start_frontend.bat         # Frontend startup script

```- **Bedrock Throttling**: Switch to Claude 3 Haiku or request limit increase

- **Riot Rate Limits**: Apply for Production API key

## Testing- **Long Analysis Time**: Expected 3-5 minutes for 50+ matches



```bash### Debug Commands

# Test profile service

cd tests```bash

python test_profile.py# Check rate limiter stats

curl http://localhost:8000/api/health

# Test structured analysis

python test_structured_analysis.py# Test with specific player

curl -X POST "http://localhost:8000/api/year-rewind/YourName/TAG"

# Test rate limiting```

python test_rate_limits.py

```## License



## Performance MetricsMIT License - see LICENSE file for details.


| Metric | Target | Notes |
|--------|--------|-------|
| Profile Load | <5 seconds | Initial data for header |
| Full Analysis | 3-6 minutes | 100 matches with AI |
| Match Fetching | ~30s | Riot API rate limited |
| AI Generation | ~10-30s | Claude Sonnet 4 inference |

## Current Scope (Hackathon)

✅ **Implemented**
- NA region only
- Profile + Analysis endpoints
- Top 3 champions with accurate stats
- AI-generated insights with Claude Sonnet 4
- Challenge system data extraction
- Clean, production-ready codebase

🚧 **Future Enhancements**
- Multi-region support
- Historical progress/growth charts
- Champion recommendations
- Rank timeline visualization
- Share/export functionality
- Performance optimization (<2 min total)

## Known Limitations

1. **Analysis Time**: 3-6 minutes for 100 matches (rate limit constrained)
2. **Region**: NA only (easily expandable)
3. **AI Quality**: Still being refined based on feedback
4. **Growth Charts**: Mock data (needs historical tracking implementation)

## Contributing

Priority areas for improvement:
1. **AI Prompt Engineering**: Enhance insight quality and variety
2. **Performance**: Optimize match fetching and caching
3. **Multi-Region**: Add support for other regions
4. **Historical Data**: Implement rank/performance timeline tracking
5. **UI Polish**: Refine animations and responsive design

## Troubleshooting

### Backend Won't Start
- Check `.env` file exists in `backend/` directory
- Verify AWS credentials have Bedrock access
- Ensure Riot API key is valid

### Frontend Shows "Player not found"
- Verify player exists in NA region
- Check backend is running on port 8000
- Check browser console for API errors

### Analysis Takes Too Long
- Expected for first-time analysis (3-6 minutes)
- Check `/api/health` for rate limiter stats
- Consider reducing `num_matches` parameter

## License

MIT License - See LICENSE file for details.

---

**Built for Riot Games API Challenge 2025**
