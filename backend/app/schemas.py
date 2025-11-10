"""
Pydantic schemas for type-safe API responses.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ========== Profile Schemas ==========

class RankInfo(BaseModel):
    tier: str
    division: str
    lp: int
    wins: int
    losses: int
    win_rate: float
    display: str

class ProfileData(BaseModel):
    puuid: str
    display_name: str
    profile_icon_url: str
    summoner_level: int
    rank: RankInfo
    main_role: str

class ProfileResponse(BaseModel):
    success: bool
    profile: Optional[ProfileData] = None
    error: Optional[str] = None

# ========== Analysis Schemas ==========

class ChampionStats(BaseModel):
    name: str
    games: int
    winRate: float
    kda: Optional[float] = None

class Highlight(BaseModel):
    stat: str
    value: str

class AnalysisData(BaseModel):
    displayName: str
    profilePicture: str
    mainRole: str
    topChampions: List[ChampionStats]
    highlights: List[Highlight]
    aiInsight: str
    personality: str
    rank: str
    matchesAnalyzed: int

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[AnalysisData] = None
    error: Optional[str] = None
    progress: Optional[str] = None  # For progress updates
    analysis_id: Optional[str] = None  # For SSE progress tracking

class AnalysisRequest(BaseModel):
    num_matches: int = Field(default=100, ge=10, le=200, description="Number of matches to analyze")

# ========== Health Check Schema ==========

class RateLimiterStats(BaseModel):
    requests_last_second: int
    requests_last_2_minutes: int
    capacity_1s: str
    capacity_2min: str

class CacheStats(BaseModel):
    total_matches: int
    fresh_matches: int
    total_profiles: int
    cache_size_mb: float

class HealthResponse(BaseModel):
    status: str
    rate_limiter: RateLimiterStats
    cache: Optional[CacheStats] = None
    config_valid: bool

# ========== Error Response ==========

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
