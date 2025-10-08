# Rift Rewind

AI-powered League of Legends match analysis and year-end review generator. Creates personalized Spotify Wrapped-style reviews using player match history and performance data.

## Features

- **AI-Powered Analysis**: Uses AWS Bedrock (Claude) to generate personalized year-end reviews
- **Smart Match Fetching**: Prioritizes ranked matches for competitive insights
- **Performance Trends**: Analyzes KDA, CS, vision, and improvement patterns
- **Champion Pool Analysis**: Identifies main champions, win rates, and playstyle
- **Retry-Safe Caching**: Prevents re-fetching data on API throttling
- **Rate Limit Optimization**: Intelligent handling of Riot API and Bedrock limits

## Architecture

- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python
- **AI Agent**: AWS Bedrock (Claude 3 Haiku) with LangChain
- **Data Source**: Riot Games API
- **Caching**: In-memory retry-safe caching system

## Prerequisites

- Node.js (v18+)
- Python (v3.8+)
- Riot Games API Key
- AWS Account with Bedrock access

## Setup

### 1. Environment Configuration

Create `backend/.env`:

```env
RIOT_API_KEY=your_riot_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
```

### 2. Installation

```bash
# Install dependencies
npm install
cd backend && pip install -r requirements.txt
```

### 3. Run Application

```bash
# Backend (Terminal 1)
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (Terminal 2)
npm run dev
```

## API Endpoints

### Core Endpoints

- `GET /api/player/{game_name}/{tag_line}` - Get player PUUID
- `POST /api/year-rewind/{game_name}/{tag_line}` - Generate AI review
- `GET /api/health` - Health check with rate limiter stats

### Usage Example

```bash
curl -X POST "http://localhost:8000/api/year-rewind/Faker/KR1"
```

## Testing

```bash
# Run all tests
python tests/test_agent.py

# Test rate limits
python tests/test_rate_limits.py

# Test caching behavior
python tests/test_throttling_behavior.py
```

## Performance

| Metric              | Current     | Optimized           |
| ------------------- | ----------- | ------------------- |
| Analysis Time       | 3-5 minutes | 1-2 minutes         |
| Retry Overhead      | 0% (cached) | Previously 200-300% |
| Rate Limit Handling | Intelligent | Previously basic    |

## Current Limitations & Improvements

### Rate Limits

- **Riot API**: 20 req/s, 100 req/2min (Personal key)
- **Bedrock**: ~5-10 req/s (Default limits)

**Improvements**:

- Apply for Riot Production API key (500 req/s, 30k req/10min)
- Request Bedrock rate limit increase
- Switch to Claude 3.5 Sonnet for better quality

### Model Options

- **Current**: Claude 3 Haiku (fast, higher limits)
- **Upgrade**: Claude 3.5 Sonnet (better quality, lower limits)
- **Premium**: Claude 3 Opus (highest quality, lowest limits)

### Future Enhancements

- **OP.GG MCP Integration**: Real-time meta insights and build recommendations
- **Champion Synergy Analysis**: Team composition suggestions
- **Trend Analysis**: Performance improvement tracking over time
- **Multi-Region Support**: Support for all Riot regions

## Project Structure

```
RiftRewindProject/
├── app/                    # Next.js frontend
├── backend/
│   ├── app/main.py        # FastAPI application
│   ├── services/
│   │   ├── year_rewind_agent.py    # Main AI agent
│   │   ├── agent_tools.py          # Analysis tools
│   │   ├── riot_api.py             # Riot API client
│   │   ├── rate_limiter.py         # Riot API rate limiting
│   │   └── bedrock_rate_limiter.py # Bedrock rate limiting
│   └── .env               # Environment variables
├── tests/                 # Test suite
└── README.md
```

## Contributing

1. **Model Experimentation**: Test different models for quality and speed
2. **OP.GG Integration**: Add real-time meta analysis using OP.GG MCP
3. **Performance Optimization**: Figure out a way to reduce analysis time.
4. **UI/UX**: Improve frontend design and user experience
5. **Additional Features**: Champion recommendations, team analysis, etc.
6. **Tool and System Prompts**: Work on finding errors and enhancing the prompts for the agent tools and the system prompt that initalises the workflow.

## Rate Limit Optimization

The system includes intelligent rate limiting for both APIs:

- **Riot API**: Respects 20 req/s and 100 req/2min limits
- **Bedrock**: Handles throttling with exponential backoff
- **Caching**: Prevents re-fetching on retries (major performance improvement)

## Troubleshooting

### Issues

- **Bedrock Throttling**: Switch to Claude 3 Haiku or request limit increase
- **Riot Rate Limits**: Apply for Production API key
- **Long Analysis Time**: Expected 3-5 minutes for 50+ matches

### Debug Commands

```bash
# Check rate limiter stats
curl http://localhost:8000/api/health

# Test with specific player
curl -X POST "http://localhost:8000/api/year-rewind/YourName/TAG"
```

## License

MIT License - see LICENSE file for details.
