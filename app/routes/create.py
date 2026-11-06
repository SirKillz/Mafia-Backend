import logging
from datetime import datetime

from fastapi import APIRouter, Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Database.session_factory import get_db
from app.Database.models import Team, Game, Role, Player, GameParticipant

from app.Auth.api_key import get_api_key
from app.schema import GamePayload, GameRead, PlayerSchema


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

def get_roles(db: Session):
    """
    Returns a list of all roles
    """
    stmt = select(Role)
    return db.execute(stmt).scalars().all()

def get_players(db: Session) -> list[Player]:
    """
    Returns a list of all players
    """
    stmt = select(Player)
    return db.execute(stmt).scalars().all()

def create_game(db: Session, payload: GamePayload) -> Game:
    """
    Creates a new game
    """

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

def create_game_participants(db: Session, game_id: int, game_players: list[PlayerSchema]) -> list[GameParticipant]:
    """
    Creates the participants for a given game
    """
    roles = get_roles(db)
    role_data = {r.role_name: r.role_id for r in roles}

    MAFIA = 1 
    INNOCENT = 2

    existing_db_players = {p.name: p for p in get_players(db)}
    

    game_participants = []
    for game_player in game_players:

        # Create players that do NOT already exist in the db
        player = existing_db_players.get(game_player.name)
        if not player:
            player = Player(name=game_player.name)
            db.add(player)
            db.flush()            # ← assigns player.player_id
            existing_db_players[game_player.name] = player

        # Compute constants per-player
        role_id = role_data[game_player.role]
        team_id = MAFIA if game_player.isMafia else INNOCENT

        spy_stats        = game_player.spy_stats()
        medic_stats      = game_player.medic_save_stats()
        medic_self_stats = game_player.medic_self_save_stats()
        assassin_stats   = game_player.assassin_stats()

        # Add the Game Participant
        game_participant = GameParticipant(
            game_id = game_id,
            player_id = player.player_id,
            role_id = role_id,
            team_id = team_id,
            days_survived = game_player.daysSurvived,
            nights_survived = game_player.nightsSurvived,
            successful_spy_checks = spy_stats["numerator"],
            spy_check_opportunities = spy_stats["denominator"],
            medic_self_saves = medic_self_stats["numerator"],
            successful_medic_saves = medic_stats["numerator"],
            medic_save_opportunities = medic_stats["denominator"],
            successful_assassin_shots = assassin_stats["numerator"],
            assassin_shot_attempts = assassin_stats["denominator"],
        )

        db.add(game_participant)
        db.commit()
        db.refresh(game_participant)

        game_participants.append(game_participant)

    return game_participants

@create_results_router.post("/create", response_model=GameRead)
async def create_results(
    payload: GamePayload, 
    api_key: dict = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/game/create")

    game = create_game(db, payload)
    create_game_participants(db, game.game_id, payload.players)
    return game