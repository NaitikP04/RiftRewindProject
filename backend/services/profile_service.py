"""
Profile Service - Player profile, rank, and summoner data
Fetches core player information for North American players.
"""
import os
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from .rate_limiter import rate_limiter

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# Data Dragon version
DD_VERSION = "14.22.1"
DD_BASE_URL = f"https://ddragon.leagueoflegends.com/cdn/{DD_VERSION}"

# Role display names
ROLE_DISPLAY = {
    "TOP": "Top",
    "JUNGLE": "Jungle",
    "MIDDLE": "Mid",
    "BOTTOM": "ADC",
    "UTILITY": "Support",
    "NONE": "Fill"
}


async def get_player_profile(game_name: str, tag_line: str) -> Dict[str, Any]:
    """
    Get complete player profile including summoner data, rank, and main role.
    
    Args:
        game_name: Player name (before #)
        tag_line: Tag (after #)
    
    Returns:
        Dictionary with profile data or error
    """
    try:
        print(f"\n{'='*60}")
        print(f"📋 Fetching profile for {game_name}#{tag_line}")
        print(f"{'='*60}\n")
        
        # North America region configuration
        platform = "na1"
        region = "americas"
        
        # Step 1: Get PUUID
        puuid = await _get_puuid(game_name, tag_line, region)
        if not puuid:
            return {
                "success": False,
                "error": f"Player {game_name}#{tag_line} not found"
            }
        
        print(f"✓ PUUID: {puuid[:20]}...")
        
        # Step 2: Get summoner data (for icon, level)
        summoner = await _get_summoner_by_puuid(puuid, platform)
        if not summoner:
            return {
                "success": False,
                "error": "Failed to fetch summoner data"
            }
        
        print(f"✓ Summoner Level: {summoner['summonerLevel']}")
        
        # Step 3: Get rank
        rank = await _get_summoner_rank(puuid, platform)
        
        print(f"✓ Rank: {rank['display']}")
        
        # Step 4: Determine main role from recent matches
        main_role = await _determine_main_role(puuid, region, platform)
        
        print(f"✓ Main Role: {main_role}")
        print(f"\n{'='*60}")
        print(f"✅ Profile fetched successfully!")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "profile": {
                "puuid": puuid,
                "riot_id": f"{game_name}#{tag_line}",
                "display_name": f"{game_name}#{tag_line}",
                "summoner_level": summoner['summonerLevel'],
                "profile_icon_id": summoner['profileIconId'],
                "profile_icon_url": f"{DD_BASE_URL}/img/profileicon/{summoner['profileIconId']}.png",
                "rank": rank,
                "main_role": main_role
            }
        }
        
    except Exception as e:
        print(f"❌ Error in get_player_profile: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Internal error: {str(e)}"
        }


async def _get_puuid(game_name: str, tag_line: str, region: str = "americas") -> Optional[str]:
    """Get player PUUID from Riot ID."""
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    
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


async def _get_summoner_by_puuid(puuid: str, platform: str = "na1") -> Optional[Dict[str, Any]]:
    """Get summoner data from PUUID."""
    url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    
    await rate_limiter.wait_if_needed()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=HEADERS)
            rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Error fetching summoner: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching summoner: {e}")
            return None


async def _get_summoner_rank(puuid: str, platform: str = "na1") -> Dict[str, Any]:
    """
    Get player's ranked stats.
    Returns unranked if no ranked data found.
    """
    url = f"https://{platform}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
    
    await rate_limiter.wait_if_needed()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=HEADERS)
            rate_limiter.record_request()
            
            if response.status_code == 200:
                entries = response.json()
                
                # Find ranked solo/duo queue
                ranked_solo = next(
                    (entry for entry in entries if entry['queueType'] == 'RANKED_SOLO_5x5'),
                    None
                )
                
                if ranked_solo:
                    wins = ranked_solo['wins']
                    losses = ranked_solo['losses']
                    total_games = wins + losses
                    win_rate = (wins / total_games * 100) if total_games > 0 else 0
                    
                    return {
                        "tier": ranked_solo['tier'],
                        "division": ranked_solo['rank'],
                        "lp": ranked_solo['leaguePoints'],
                        "wins": wins,
                        "losses": losses,
                        "win_rate": round(win_rate, 1),
                        "display": f"{ranked_solo['tier'].capitalize()} {ranked_solo['rank']} • {ranked_solo['leaguePoints']} LP"
                    }
                else:
                    # Unranked
                    return {
                        "tier": "UNRANKED",
                        "division": "",
                        "lp": 0,
                        "wins": 0,
                        "losses": 0,
                        "win_rate": 0,
                        "display": "Unranked"
                    }
            else:
                print(f"Error fetching rank: {response.status_code}")
                return {
                    "tier": "UNRANKED",
                    "division": "",
                    "lp": 0,
                    "wins": 0,
                    "losses": 0,
                    "win_rate": 0,
                    "display": "Unranked"
                }
        except Exception as e:
            print(f"Exception fetching rank: {e}")
            return {
                "tier": "UNRANKED",
                "division": "",
                "lp": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "display": "Unranked"
            }


async def _determine_main_role(puuid: str, region: str = "americas", platform: str = "na1", sample_size: int = 10) -> str:
    """
    Determine player's main role from recent match history.
    Analyzes last 10 matches to find most frequently played role.
    """
    try:
        # Fetch recent match IDs
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"start": 0, "count": sample_size}
        
        await rate_limiter.wait_if_needed()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=HEADERS, params=params)
            rate_limiter.record_request()
            
            if response.status_code != 200:
                return "Fill"
            
            match_ids = response.json()
            
            if not match_ids:
                return "Fill"
            
            # Fetch match details to get roles
            role_counts = {}
            
            for match_id in match_ids[:sample_size]:
                match_data = await _get_match_for_role(match_id, puuid, region)
                
                if match_data:
                    role = match_data.get('teamPosition', 'NONE')
                    if role and role != 'NONE':
                        role_counts[role] = role_counts.get(role, 0) + 1
            
            # Find most common role
            if role_counts:
                main_role = max(role_counts, key=role_counts.get)
                return ROLE_DISPLAY.get(main_role, main_role)
            else:
                return "Fill"
                
    except Exception as e:
        print(f"Error determining main role: {e}")
        return "Fill"


async def _get_match_for_role(match_id: str, puuid: str, region: str = "americas") -> Optional[Dict[str, Any]]:
    """Fetch match data and extract player's role."""
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    
    await rate_limiter.wait_if_needed()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=HEADERS)
            rate_limiter.record_request()
            
            if response.status_code == 200:
                match_data = response.json()
                participants = match_data['info']['participants']
                
                # Find player in match
                player = next((p for p in participants if p['puuid'] == puuid), None)
                return player
            else:
                return None
        except Exception as e:
            return None
