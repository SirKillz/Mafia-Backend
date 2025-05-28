import logging
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from mafia_backend.Auth.api_key import get_api_key
from mafia_backend.response_models import AverageStatsSchema
from mafia_backend.Database.query_service import QueryService

average_stats_router = APIRouter(prefix="/v1/mafia")
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

@average_stats_router.get("/players/stats/average", response_model=AverageStatsSchema)
async def get_players(api_key: dict = Depends(get_api_key)):
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/players/stats/average")

    # Return the players
    query_service = QueryService()
    average_stats = query_service.get_average_stat_rates_raw()
    return average_stats