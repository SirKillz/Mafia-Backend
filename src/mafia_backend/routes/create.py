import logging

from fastapi import APIRouter, Depends

from mafia_backend.Auth.api_key import get_api_key
from mafia_backend.payload_models import GamePayload, PlayerSchema
from mafia_backend.Database.query_service import QueryService

create_router = APIRouter(prefix="/v1/mafia/game")
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

@create_router.post("/create")
async def create_game(payload: GamePayload, api_key: dict = Depends(get_api_key)):
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/game/create")

    # Create the game instance in the database
    query_service = QueryService()
    query_service.create_game(payload)




    return {"message": "Hello World"}