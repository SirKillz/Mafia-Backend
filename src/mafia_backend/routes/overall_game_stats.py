import logging
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from mafia_backend.Auth.api_key import get_api_key
from mafia_backend.response_models import GameStatsSchema
from mafia_backend.Database.query_service import QueryService

game_stats_router = APIRouter(prefix="/v1/mafia")
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

@game_stats_router.get("/games/stats", response_model=GameStatsSchema)
async def get_players(api_key: dict = Depends(get_api_key)):
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/games/stats")

    # Return the players
    query_service = QueryService()
    game_stats = query_service.get_overall_team_win_rates_raw()
    return game_stats