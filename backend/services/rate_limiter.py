"""
Rate limiter for Riot API Personal Keys.
Limits: 20 req/s, 100 req/2min
"""
import asyncio
from datetime import datetime
from typing import List

class RateLimiter:
    """Track API requests to respect Riot API rate limits."""
    
    # Rate limits - you can increase these if you have higher limits
    # Personal Key: 20/s, 100/2min
    # Production Key: 500/s, 30000/10min
    MAX_REQUESTS_PER_SECOND = 20
    MAX_REQUESTS_PER_2_MINUTES = 100
    
    def __init__(self, requests_per_second=None, requests_per_2min=None):
        """Initialize with custom rate limits if provided."""
        if requests_per_second:
            self.MAX_REQUESTS_PER_SECOND = requests_per_second
        if requests_per_2min:
            self.MAX_REQUESTS_PER_2_MINUTES = requests_per_2min
            
        self.requests_last_second: List[datetime] = []
        self.requests_last_2_minutes: List[datetime] = []
        self._lock = asyncio.Lock()
        
        print(f"🔧 Rate limiter initialized: {self.MAX_REQUESTS_PER_SECOND}/s, {self.MAX_REQUESTS_PER_2_MINUTES}/2min")
    
    async def wait_if_needed(self):
        """Wait if we're about to exceed rate limits."""
        async with self._lock:
            now = datetime.now()
            
            # Clean up old timestamps
            self.requests_last_second = [
                ts for ts in self.requests_last_second 
                if (now - ts).total_seconds() < 1
            ]
            self.requests_last_2_minutes = [
                ts for ts in self.requests_last_2_minutes 
                if (now - ts).total_seconds() < 120
            ]
            
            # Check if we need to wait
            if len(self.requests_last_second) >= self.MAX_REQUESTS_PER_SECOND:
                await asyncio.sleep(1.1)  # Wait just over 1 second
                # Clean again after waiting
                now = datetime.now()
                self.requests_last_second = [
                    ts for ts in self.requests_last_second 
                    if (now - ts).total_seconds() < 1
                ]
            
            if len(self.requests_last_2_minutes) >= self.MAX_REQUESTS_PER_2_MINUTES:
                # Wait until oldest request is > 2 minutes old
                oldest = min(self.requests_last_2_minutes)
                wait_time = 121 - (now - oldest).total_seconds()
                if wait_time > 0:
                    print(f"⏳ Rate limit (100 req/2min) approaching, waiting {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
    
    def record_request(self):
        """Record that we made a request."""
        now = datetime.now()
        self.requests_last_second.append(now)
        self.requests_last_2_minutes.append(now)
    
    def get_stats(self) -> dict:
        """Get current rate limit usage."""
        now = datetime.now()
        
        recent_second = [
            ts for ts in self.requests_last_second 
            if (now - ts).total_seconds() < 1
        ]
        recent_2min = [
            ts for ts in self.requests_last_2_minutes 
            if (now - ts).total_seconds() < 120
        ]
        
        return {
            "requests_last_second": len(recent_second),
            "requests_last_2_minutes": len(recent_2min),
            "capacity_1s": f"{len(recent_second)}/{self.MAX_REQUESTS_PER_SECOND}",
            "capacity_2min": f"{len(recent_2min)}/{self.MAX_REQUESTS_PER_2_MINUTES}"
        }

# Global rate limiter instance 
rate_limiter = RateLimiter(
    requests_per_second=20,    
    requests_per_2min=100    
)