from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import riot_api

app = FastAPI()

# Allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/matches/{game_name}/{tag_line}")
async def get_matches_by_riot_id(game_name: str, tag_line: str):
    try:
        puuid = await riot_api.get_puuid_by_riot_id(game_name, tag_line)
        if not puuid:
            raise HTTPException(status_code=404, detail="Player not found")

        match_ids = await riot_api.get_match_ids_by_puuid(puuid)
        return {"puuid": puuid, "matches": match_ids}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))