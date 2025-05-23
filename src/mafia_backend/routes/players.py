import logging
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from mafia_backend.Auth.api_key import get_api_key
from mafia_backend.response_models import PlayerSchema
from mafia_backend.Database.query_service import QueryService

players_router = APIRouter(prefix="/v1/mafia")
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

@players_router.get("/players", response_model=List[PlayerSchema])
async def get_players(api_key: dict = Depends(get_api_key)):
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/players")

    # Return the players
    players = QueryService().get_players()
    return players