"""
FastAPI backend for Rift Rewind.
League of Legends match analysis and year-end review generator.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import riot_api, year_rewind_agent, profile_service

app = FastAPI(title="Rift Rewind API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Rift Rewind API is running",
        "version": "1.0.0"
    }


@app.get("/api/player/{game_name}/{tag_line}")
async def get_player(game_name: str, tag_line: str):
    """
    Get basic player info (PUUID).
    
    Args:
        game_name: Player name (before #)
        tag_line: Tag (after #)
    
    Returns:
        Player PUUID
    """
    try:
        puuid = await riot_api.get_puuid_by_riot_id(game_name, tag_line)
        
        if not puuid:
            raise HTTPException(
                status_code=404,
                detail=f"Player {game_name}#{tag_line} not found"
            )
        
        return {
            "puuid": puuid,
            "riot_id": f"{game_name}#{tag_line}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/year-rewind/{game_name}/{tag_line}")
async def generate_year_rewind(game_name: str, tag_line: str):
    """
    Generate AI-powered year-end review with retry-safe caching.
    
    This endpoint:
    1. Fetches player's match history (last 365 days) with caching
    2. Prioritizes ranked matches for competitive insights
    3. Uses AI agent with throttling protection
    4. Generates personalized Spotify Wrapped-style review
    
    Features retry-safe caching to prevent re-fetching data on Bedrock throttling.
    Expected time: 3-5 minutes for 200 matches (no slowdown on retries).
    
    Args:
        game_name: Player name (before #)
        tag_line: Tag (after #)
    
    Returns:
        Comprehensive year-end review
    """
    try:
        # Get player PUUID
        puuid = await riot_api.get_puuid_by_riot_id(game_name, tag_line)
        
        if not puuid:
            raise HTTPException(
                status_code=404,
                detail=f"Player {game_name}#{tag_line} not found"
            )
        
        riot_id = f"{game_name}#{tag_line}"
        
        # Generate review using AI agent with retry-safe caching
        review = await year_rewind_agent.generate_year_rewind(puuid, riot_id)
        
        if not review.get('success'):
            raise HTTPException(
                status_code=500,
                detail=review.get('error', 'Failed to generate review')
            )
        
        return review
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in year-rewind endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Check if API and services are healthy."""
    from services.rate_limiter import rate_limiter
    
    stats = rate_limiter.get_stats()
    
    return {
        "status": "healthy",
        "rate_limiter": stats
    }


@app.get("/api/profile/{game_name}/{tag_line}")
async def get_profile(game_name: str, tag_line: str):
    """
    Get player profile with summoner info, rank, and main role.
    Fast endpoint (<5 seconds) for initial profile display.
    
    Args:
        game_name: Player name (before #)
        tag_line: Tag (after #)
    
    Returns:
        Profile data with summoner icon, level, rank, and main role
    """
    try:
        result = await profile_service.get_player_profile(game_name, tag_line)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=404,
                detail=result.get('error', 'Profile not found')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in profile endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))