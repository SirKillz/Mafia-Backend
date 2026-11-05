import logging
from datetime import datetime

from fastapi import APIRouter, Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Database.session_factory import get_db
from app.Database.models import Team, Game

from app.Auth.api_key import get_api_key
from app.schema import GamePayload, GameRead


create_results_router = APIRouter(prefix="/v1/mafia/results")
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

def get_team_id_by_name(db: Session, team_name: str) -> int:
    """
    Attempts to find a team by name wihtin the database
    """

    stmt = select(Team).where(Team.name == team_name)
    team = db.execute(stmt).scalars().first()

    if team is None:
        raise ValueError(f"No team found with name {team_name}")

    return team.team_id

@create_results_router.post("/create", response_model=GameRead)
async def create_results(
    payload: GamePayload, 
    api_key: dict = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    
    
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/game/create")

    # Derived Values
    played_at = datetime.now()
    player_count = len(payload.players)
    mafia_count = len([p for p in payload.players if p.isMafia])
    winning_team_id = get_team_id_by_name(db, payload.winningTeam)

    game = Game(
        played_at = played_at,
        approved = False,
        winning_team = winning_team_id,
        player_count = player_count,
        mafia_count = mafia_count,
        mafia_kill_power = payload.initialMafiaKillPower,
        day_count = payload.dayCount,
        night_count = payload.nightCount
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    return game