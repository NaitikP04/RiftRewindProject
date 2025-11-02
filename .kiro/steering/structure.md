# Project Structure

## Data Flow Patterns

### Agent Analysis Flow

```python
# In year_rewind_agent.py
async def generate_year_rewind(puuid: str, riot_id: str):
    """
    Main entry point for AI analysis.

    Flow:
    1. Reset global state (_current_matches_data, _current_puuid)
    2. Invoke LangChain agent with prompt
    3. Agent uses tools sequentially:
       a. fetch_player_matches(puuid) → match IDs
       b. get_detailed_match_data(match_ids) → full match objects
       c. analyze_performance_trends(puuid) → KDA, CS, vision trends
       d. analyze_champion_pool(puuid) → champion mastery
       e. identify_playstyle(puuid) → personality profile
    4. Agent synthesizes findings into review
    5. Return structured response

    Error Handling:
    - Rate limit throttles: Exponential backoff + retry
    - Missing data: Graceful degradation (e.g., "No trend data available")
    - API failures: Partial results with warnings
    """
```

### Tool Design Pattern

All agent tools follow this structure:

1. **Input validation**: Check for required data
2. **State management**: Read from/write to global `_current_matches_data`
3. **Error handling**: Return JSON with error messages, never throw
4. **Structured output**: Always return JSON strings for consistent parsing

Example:

```python
@tool
async def analyze_performance_trends(puuid: str) -> str:
    """Tool docstring for agent (describes when to use this)."""
    global _current_matches_data

    if not _current_matches_data:
        return json.dumps({"error": "No data loaded"})

    results = agent_tools.calculate_performance_trends(_current_matches_data, puuid)
    return json.dumps(results, default=str)
```

## Critical Conventions

### State Management

- **Global state**: `_current_matches_data` holds all match details for current analysis
- **Single-threaded**: FastAPI can handle concurrent requests, but each has isolated state
- **Stateless tools**: Tools operate on global state but don't maintain internal state

### Rate Limit Coordination

- **Sequential processing**: Agent tools run sequentially, not in parallel
- **Centralized limiters**: Both rate limiters are singletons
- **Retry-safe caching**: Match data persists in `_current_matches_data` across retries

### Error Propagation

- **Tools**: Return JSON errors, never raise exceptions
- **Agent executor**: `handle_parsing_errors=True` to recover from bad tool outputs
- **Endpoint**: Catches exceptions and returns HTTP error responses

## Root Directory Layout

```
RiftRewindProject/
├── app/                    # Next.js frontend (App Router)
├── backend/                # FastAPI Python backend
├── tests/                  # Test suite
├── .kiro/                  # Kiro IDE configuration
├── .next/                  # Next.js build output
├── node_modules/           # Frontend dependencies
├── package.json            # Frontend package configuration
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── setup.bat              # Windows setup script
├── start_test.bat         # Backend development server script
└── README.md              # Project documentation
```

## Frontend Structure (`app/`)

Uses Next.js App Router pattern:

```
app/
├── globals.css            # Global Tailwind styles
├── layout.tsx             # Root layout component
└── page.tsx               # Home page component
```

**Conventions:**

- Server components by default
- Client components only when needed (use `'use client'`)
- Dark theme as default (`bg-gray-900 text-white`)
- Tailwind utility classes for styling

## Backend Structure (`backend/`)

```
backend/
├── app/
│   └── main.py            # FastAPI application entry point
├── services/              # Business logic and external integrations
│   ├── year_rewind_agent.py      # Main LangChain AI agent
│   ├── agent_tools.py             # Analysis tools for the agent
│   ├── riot_api.py                # Riot Games API client
│   ├── rate_limiter.py            # Riot API rate limiting
│   └── bedrock_rate_limiter.py    # AWS Bedrock rate limiting
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── __init__.py           # Python package marker
```

**Conventions:**

- All API endpoints use async/await
- Services are modular and importable
- Rate limiters handle external API constraints
- Environment variables for all secrets and configuration

## Test Structure (`tests/`)

```
tests/
├── test_agent.py                    # AI agent functionality tests
├── test_rate_limits.py              # Rate limiting tests
├── test_throttling_behavior.py      # Throttling behavior tests
├── test_guide.md                    # Testing documentation
└── year_review_*.txt                # Sample output files
```

**Conventions:**

- Test files prefixed with `test_`
- Integration tests for external APIs
- Sample outputs for validation

## Configuration Files

### Frontend Configuration

- `package.json`: Dependencies and npm scripts
- `tsconfig.json`: TypeScript with relaxed strict mode
- `tailwind.config.js`: Tailwind CSS setup for app directory
- `next-env.d.ts`: Next.js type definitions

### Backend Configuration

- `requirements.txt`: Python dependencies
- `.env`: Environment variables (local only)
- `.env.example`: Template for required environment variables

## Import Patterns

### Backend Imports

```python
# Relative imports within backend
from services import riot_api, year_rewind_agent
from .rate_limiter import rate_limiter

# External libraries
from fastapi import FastAPI, HTTPException
import boto3
```

### Frontend Imports

```typescript
// Next.js and React
import { Metadata } from "next";
import "./globals.css";

// Relative imports
import Component from "./components/Component";
```

## API Patterns

### Endpoint Structure

- `/api/player/{game_name}/{tag_line}` - Player lookup
- `/api/year-rewind/{game_name}/{tag_line}` - Generate review
- `/api/health` - Health check with rate limiter stats

### Response Patterns

```python
# Success response
return {
    "success": True,
    "data": result,
    "metadata": {...}
}

# Error response
raise HTTPException(
    status_code=404,
    detail="Player not found"
)
```

## Development Workflow

1. **Frontend changes**: Edit files in `app/`, auto-reload on `npm run dev`
2. **Backend changes**: Edit files in `backend/`, auto-reload with uvicorn
3. **New features**: Add services in `backend/services/`, import in `main.py`
4. **Testing**: Run tests from project root with `python tests/test_*.py`
5. **Environment**: Always use `.env` for secrets, never commit credentials

## File Naming Conventions

- **Python**: `snake_case.py` for modules, `PascalCase` for classes
- **TypeScript**: `kebab-case.tsx` for components, `camelCase` for variables
- **Configuration**: Standard names (`package.json`, `tsconfig.json`, etc.)
- **Tests**: `test_feature_name.py` pattern
