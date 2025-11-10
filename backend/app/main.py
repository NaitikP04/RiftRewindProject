"""
FastAPI backend for Rift Rewind.
League of Legends match analysis and year-end review generator.
"""
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import sys
import os
import uuid
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import riot_api, profile_service, structured_analysis_service
# from services import year_rewind_agent  # Commented out - uses old LangChain API
from services.config import config
from services.cache_manager import cache_manager
from services.progress_tracker import progress_tracker
from . import schemas

app = FastAPI(title="Rift Rewind API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    print("\n" + "="*60)
    print("🚀 Rift Rewind API Starting...")
    print("="*60)
    
    is_valid, error = config.validate()
    if not is_valid:
        print(f"\n❌ Configuration Error:\n{error}\n")
        print("="*60 + "\n")
        # Continue anyway for development, but warn
    else:
        print(config.get_summary())
        cache_stats = cache_manager.get_cache_stats()
        print(f"📦 Cache Status:")
        print(f"   Matches: {cache_stats['total_matches']} ({cache_stats['fresh_matches']} fresh)")
        print(f"   Profiles: {cache_stats['total_profiles']}")
        print(f"   Size: {cache_stats['cache_size_mb']:.2f} MB")
        print("="*60 + "\n")


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


# DEPRECATED: Old endpoint using year_rewind_agent (LangChain compatibility issues)
# Use /api/analysis instead
"""
@app.post("/api/year-rewind/{game_name}/{tag_line}")
async def generate_year_rewind(game_name: str, tag_line: str):
    # This endpoint uses the old year_rewind_agent which has LangChain version conflicts
    # Use /api/analysis/{game_name}/{tag_line} instead
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Use /api/analysis/{game_name}/{tag_line} instead"
    )
"""


@app.get("/api/health")
async def health_check() -> schemas.HealthResponse:
    """Check if API and services are healthy."""
    from services.rate_limiter import rate_limiter
    
    stats = rate_limiter.get_stats()
    cache_stats = cache_manager.get_cache_stats()
    is_valid, _ = config.validate()
    
    return schemas.HealthResponse(
        status="healthy" if is_valid else "degraded",
        rate_limiter=schemas.RateLimiterStats(**stats),
        cache=schemas.CacheStats(**cache_stats),
        config_valid=is_valid
    )


@app.get("/api/profile/{game_name}/{tag_line}")
async def get_profile(game_name: str, tag_line: str) -> schemas.ProfileResponse:
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
            return schemas.ProfileResponse(
                success=False,
                error=result.get('error', 'Failed to fetch profile')
            )
        
        profile_data = result['profile']
        
        return schemas.ProfileResponse(
            success=True,
            profile=schemas.ProfileData(**profile_data)
        )
        
    except Exception as e:
        print(f"Error in profile endpoint: {e}")
        return schemas.ProfileResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/analysis/{game_name}/{tag_line}")
async def generate_analysis(
    game_name: str, 
    tag_line: str, 
    background_tasks: BackgroundTasks,
    request: schemas.AnalysisRequest = schemas.AnalysisRequest()
) -> schemas.AnalysisResponse:
    """
    Generate structured AI analysis for dashboard.
    Returns analysis ID for progress tracking via SSE.
    
    Expected time: 3-6 minutes depending on match count.
    
    Args:
        game_name: Player name (before #)
        tag_line: Tag (after #)
        background_tasks: FastAPI background tasks
        request: Analysis configuration (num_matches)
    
    Returns:
        Structured analysis data for frontend with analysis_id
    """
    # Generate unique analysis ID for progress tracking
    analysis_id = str(uuid.uuid4())
    
    try:
        # Start analysis with progress tracking
        result = await structured_analysis_service.generate_structured_analysis(
            game_name=game_name,
            tag_line=tag_line,
            num_matches=request.num_matches,
            analysis_id=analysis_id  # Pass for progress tracking
        )
        
        if not result.get('success'):
            return schemas.AnalysisResponse(
                success=False,
                error=result.get('error', 'Analysis failed')
            )
        
        response = schemas.AnalysisResponse(
            success=True,
            data=schemas.AnalysisData(**result['data'])
        )
        response.analysis_id = analysis_id
        return response
        
    except Exception as e:
        print(f"Error in analysis endpoint: {e}")
        return schemas.AnalysisResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/analysis/{analysis_id}/progress")
async def stream_analysis_progress(analysis_id: str):
    """
    Stream real-time progress updates via Server-Sent Events (SSE).
    Frontend can subscribe to this to show progress bar.
    
    Args:
        analysis_id: Unique analysis identifier
        
    Returns:
        SSE stream with progress updates
    """
    return StreamingResponse(
        progress_tracker.stream_progress(analysis_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )