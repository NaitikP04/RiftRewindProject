"""
Rate limiter for AWS Bedrock API.
Implements exponential backoff with jitter for throttling errors.
"""
import asyncio
from datetime import datetime
from typing import List
import time

class BedrockRateLimiter:
    """
    Track Bedrock API requests to respect rate limits and implement backoff.
    
    AWS Bedrock Claude 3.5 Sonnet typical limits:
    - ~5-10 requests per second
    - Burst capacity varies by region
    """
    
    # Conservative limits to avoid throttling
    MAX_REQUESTS_PER_SECOND = 3  # Conservative to avoid throttling
    MIN_REQUEST_INTERVAL = 0.35  # Minimum 350ms between requests
    
    # Exponential backoff settings
    INITIAL_BACKOFF = 5.0  # Start with 5 second delay (increased from 2s)
    MAX_BACKOFF = 120.0  # Cap at 2 minutes (increased from 60s)
    BACKOFF_MULTIPLIER = 2.0
    JITTER_FACTOR = 0.1  # Add ±10% jitter
    
    def __init__(self):
        self.requests_last_second: List[datetime] = []
        self.last_request_time: float = 0
        self.consecutive_throttles = 0
        self.current_backoff = self.INITIAL_BACKOFF
        self._lock = asyncio.Lock()
    
    async def wait_if_needed(self, is_retry: bool = False):
        """
        Wait if we're about to exceed rate limits or if we need to backoff.
        
        Args:
            is_retry: True if this is a retry after a throttling error
        """
        async with self._lock:
            now = datetime.now()
            current_time = time.time()
            
            # If this is a retry after throttling, apply exponential backoff
            if is_retry:
                self.consecutive_throttles += 1
                wait_time = min(
                    self.current_backoff * (self.BACKOFF_MULTIPLIER ** (self.consecutive_throttles - 1)),
                    self.MAX_BACKOFF
                )
                
                # Add jitter to avoid thundering herd
                import random
                jitter = wait_time * self.JITTER_FACTOR * (2 * random.random() - 1)
                wait_time = wait_time + jitter
                
                print(f"🔄 Bedrock throttled (attempt {self.consecutive_throttles}), backing off for {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                self.current_backoff = wait_time
                return
            
            # Reset throttle counter on successful request
            if self.consecutive_throttles > 0 and (current_time - self.last_request_time) > 5:
                self.consecutive_throttles = 0
                self.current_backoff = self.INITIAL_BACKOFF
            
            # Clean up old timestamps
            self.requests_last_second = [
                ts for ts in self.requests_last_second 
                if (now - ts).total_seconds() < 1
            ]
            
            # Enforce minimum interval between requests
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.MIN_REQUEST_INTERVAL:
                wait_time = self.MIN_REQUEST_INTERVAL - time_since_last
                await asyncio.sleep(wait_time)
            
            # Check requests per second limit
            if len(self.requests_last_second) >= self.MAX_REQUESTS_PER_SECOND:
                print(f"⏳ Bedrock rate limit ({self.MAX_REQUESTS_PER_SECOND} req/s) approaching, pausing...")
                await asyncio.sleep(1.1)  # Wait just over 1 second
                # Clean again after waiting
                now = datetime.now()
                self.requests_last_second = [
                    ts for ts in self.requests_last_second 
                    if (now - ts).total_seconds() < 1
                ]
    
    def record_request(self, success: bool = True):
        """
        Record that we made a request.
        
        Args:
            success: Whether the request was successful (not throttled)
        """
        now = datetime.now()
        self.last_request_time = time.time()
        self.requests_last_second.append(now)
        
        # Reset throttle counter on success
        if success and self.consecutive_throttles > 0:
            print(f"✅ Bedrock request successful after {self.consecutive_throttles} throttles, resetting backoff")
            self.consecutive_throttles = 0
            self.current_backoff = self.INITIAL_BACKOFF
    
    def record_throttle(self):
        """Record that we were throttled."""
        self.consecutive_throttles += 1
    
    def get_stats(self) -> dict:
        """Get current rate limit usage."""
        now = datetime.now()
        
        recent_second = [
            ts for ts in self.requests_last_second 
            if (now - ts).total_seconds() < 1
        ]
        
        return {
            "requests_last_second": len(recent_second),
            "capacity_1s": f"{len(recent_second)}/{self.MAX_REQUESTS_PER_SECOND}",
            "consecutive_throttles": self.consecutive_throttles,
            "current_backoff": f"{self.current_backoff:.1f}s"
        }

# Global rate limiter instance
bedrock_rate_limiter = BedrockRateLimiter()
