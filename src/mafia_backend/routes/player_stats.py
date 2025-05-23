import logging
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from mafia_backend.Auth.api_key import get_api_key
from mafia_backend.response_models import PlayerStatsSchema
from mafia_backend.Database.query_service import QueryService

player_stats_router = APIRouter(prefix="/v1/mafia")
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

@player_stats_router.get("/player/stats/{player_id}", response_model=PlayerStatsSchema)
async def get_players(player_id: int, api_key: dict = Depends(get_api_key)):
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/player/stats for player with id: {player_id}")

    print(player_id)

    # Return the players
    query_service = QueryService()
    player_stats = query_service.get_player_stats(player_id=player_id)
    return JSONResponse(
        content=player_stats
    )