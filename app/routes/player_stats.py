import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.Auth.api_key import get_api_key
from app.Database.session_factory import get_db
from app.response_models import PlayerStatsSchema


player_stats_router = APIRouter(prefix="/v1/mafia")
logger = logging.getLogger("app_logger")  # Configure inside src/app/__main__.py


@player_stats_router.get("/player/stats/{player_id}", response_model=PlayerStatsSchema)
async def get_player_stats(
    player_id: int,
    api_key: dict = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    logger.info(
        f"[{api_key['api_key']}] - Received Request at "
        f"/v1/mafia/player/stats for player with id: {player_id}"
    )

    sql = text("""
        SELECT
          p.player_id,
          p.name AS player_name,
          COUNT(*) AS games_played,
          COUNT(*) FILTER (WHERE r.role_name = 'Spy') AS spy_games_played,
          COUNT(*) FILTER (WHERE r.role_name = 'Medic') AS medic_games_played,
          COUNT(*) FILTER (WHERE r.role_name = 'Assassin') AS assassin_games_played,
          COUNT(*) FILTER (WHERE t.name = 'Mafia') AS mafia_games,
          COUNT(*) FILTER (WHERE t.name = 'Innocent') AS innocent_games,
          ROUND(
            COUNT(*) FILTER (WHERE t.name = 'Mafia' AND g.winning_team = gp.team_id)::numeric
            / NULLIF(COUNT(*) FILTER (WHERE t.name = 'Mafia'), 0)
          , 2) AS mafia_win_rate,
          ROUND(
            COUNT(*) FILTER (WHERE t.name = 'Innocent' AND g.winning_team = gp.team_id)::numeric
            / NULLIF(COUNT(*) FILTER (WHERE t.name = 'Innocent'), 0)
          , 2) AS innocent_win_rate,
          CASE
            WHEN SUM(gp.spy_check_opportunities) > 0
            THEN ROUND(
              SUM(gp.successful_spy_checks)::numeric
              / SUM(gp.spy_check_opportunities)
            , 2)
          END AS spy_check_rate,
          CASE
            WHEN SUM(gp.medic_save_opportunities) > 0
            THEN ROUND(
              SUM(gp.medic_self_saves)::numeric
              / SUM(gp.medic_save_opportunities)
            , 2)
          END AS medic_self_save_rate,
          CASE
            WHEN SUM(gp.medic_save_opportunities) > 0
            THEN ROUND(
              SUM(gp.successful_medic_saves)::numeric
              / SUM(gp.medic_save_opportunities)
            , 2)
          END AS successful_medic_save_rate,
          CASE
            WHEN SUM(gp.assassin_shot_attempts) > 0
            THEN ROUND(
              SUM(gp.successful_assassin_shots)::numeric
              / SUM(gp.assassin_shot_attempts)
            , 2)
          END AS successful_assassin_shot_rate
        FROM players p
        JOIN game_participants gp ON p.player_id = gp.player_id
        JOIN teams t ON gp.team_id = t.team_id
        JOIN games g ON gp.game_id = g.game_id
        JOIN roles r ON gp.role_id = r.role_id
        WHERE p.player_id = :player_id
          AND g.approved = TRUE
        GROUP BY p.player_id, p.name
    """)

    result = db.execute(sql, {"player_id": player_id}).mappings().one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail=f"No stats found for player_id={player_id}")

    stats = dict(result)
    for key, value in stats.items():
        if isinstance(value, Decimal):
            stats[key] = float(value)

    return PlayerStatsSchema(**stats)
