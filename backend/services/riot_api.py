"""
Riot API client with rate limiting.
"""
import os
import httpx
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from .rate_limiter import rate_limiter

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}


async def get_puuid_by_riot_id(game_name: str, tag_line: str) -> Optional[str]:
    """
    Convert Riot ID to PUUID.
    
    Args:
        game_name: Player name (before #)
        tag_line: Tag (after #)
    
    Returns:
        PUUID or None
    """
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    
    await rate_limiter.wait_if_needed()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=HEADERS)
            rate_limiter.record_request()
            
            if response.status_code == 200:
                return response.json().get("puuid")
            elif response.status_code == 404:
                return None
            else:
                print(f"Error fetching PUUID: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching PUUID: {e}")
            return None


async def get_match_details(match_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed match data.
    
    Args:
        match_id: Match ID
    
    Returns:
        Match data dict or None
    """
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}"
    
    await rate_limiter.wait_if_needed()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=HEADERS)
            rate_limiter.record_request()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Server-side rate limit (shouldn't happen with our limiter)
                retry_after = int(response.headers.get('Retry-After', 10))
                print(f"⚠️ Server rate limit hit, waiting {retry_after}s")
                await asyncio.sleep(retry_after)
                # Retry once
                return await get_match_details(match_id)
            else:
                print(f"Error fetching match {match_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching match {match_id}: {e}")
            return None


async def get_match_timeline(match_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch match timeline (for future use).
    
    Args:
        match_id: Match ID
    
    Returns:
        Timeline data or None
    """
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    
    await rate_limiter.wait_if_needed()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=HEADERS)
            rate_limiter.record_request()
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Exception fetching timeline: {e}")
            return None