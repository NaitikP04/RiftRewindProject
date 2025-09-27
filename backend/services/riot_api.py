import os
import httpx
from dotenv import load_dotenv

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

# Turns a Riot ID (e.g., "PlayerName#NA1") into a PUUID
async def get_puuid_by_riot_id(game_name: str, tag_line: str) -> str | None:
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("puuid")
        return None

# Gets a list of match IDs for a given PUUID
async def get_match_ids_by_puuid(puuid: str) -> list[str]:
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        return []