import logging

from fastapi import APIRouter, Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Auth.api_key import get_api_key
from app.Database.session_factory import get_db

from app.schema import ReadPlayer

from app.Database.models import Player

players_router = APIRouter(prefix="/api/v1", tags=["Players"])
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

@players_router.get("/players", response_model=list[ReadPlayer])
async def get_players(
    api_key: dict = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/players")

    # Return the players
    stmt = select(Player)
    players = db.execute(stmt).scalars().all()

    return players