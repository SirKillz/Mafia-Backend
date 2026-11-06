import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.Auth.api_key import get_api_key
from app.Database.session_factory import get_db
from app.schema import PlayerStatsSchema, GameStatsSchema, AverageStatsSchema


stats_router = APIRouter(prefix="/api/v1/stats", tags=["Stats"])
logger = logging.getLogger("app_logger")  # Configure inside src/app/__main__.py


# Get average players stats
@stats_router.get("/players/average", response_model=AverageStatsSchema)
async def get_average_player_stats(
    api_key: dict = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    logger.info(f"[{api_key['api_key']}] -  Received Request at /v1/mafia/players/stats/average")

    # Computer the same average per-player tates via a raw SQL query.

    sql = text("""
            WITH player_rates AS (
              SELECT
                gp.player_id,
                CASE
                  WHEN SUM(gp.spy_check_opportunities) > 0
                  THEN SUM(gp.successful_spy_checks)::numeric
                       / SUM(gp.spy_check_opportunities)
                END AS spy,
                CASE
                  WHEN SUM(gp.medic_save_opportunities) > 0
                  THEN SUM(gp.medic_self_saves)::numeric
                       / SUM(gp.medic_save_opportunities)
                END AS medic_self,
                CASE
                  WHEN SUM(gp.medic_save_opportunities) > 0
                  THEN SUM(gp.successful_medic_saves)::numeric
                       / SUM(gp.medic_save_opportunities)
                END AS medic_success,
                CASE
                  WHEN SUM(gp.assassin_shot_attempts) > 0
                  THEN SUM(gp.successful_assassin_shots)::numeric
                       / SUM(gp.assassin_shot_attempts)
                END AS assassin
              FROM game_participants gp
              JOIN games g
                ON gp.game_id = g.game_id
              WHERE g.approved = TRUE
              GROUP BY gp.player_id
            )
            SELECT
              ROUND(AVG(spy), 2)             AS avg_spy_check_rate,
              ROUND(AVG(medic_self), 2)      AS avg_medic_self_save_rate,
              ROUND(AVG(medic_success), 2)   AS avg_successful_medic_save_rate,
              ROUND(AVG(assassin), 2)        AS avg_successful_assassin_shot_rate
            FROM player_rates;
        """)

    result = db.execute(sql).mappings().one_or_none()

    if result is None:
        return AverageStatsSchema(
            avg_spy_check_rate=None,
            avg_medic_self_save_rate=None,
            avg_successful_medic_save_rate=None,
            avg_successful_assassin_shot_rate=None,
        )
    
    result_dict = dict(result)
    # convert any Decimal rates to float
    for k, v in result_dict.items():
        if isinstance(v, Decimal):
            result_dict[k] = float(v)

    return AverageStatsSchema(**result_dict)



# Get an individual player's stats
@stats_router.get("/players/{player_id}", response_model=PlayerStatsSchema)
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



# Get overall Team Stats (Innocent Win Rate, Mafia Win Rate)
@stats_router.get("/teams", response_model=GameStatsSchema)
async def get_team_stats(
    api_key: dict = Depends(get_api_key),
    db: Session = Depends(get_db),
):
    logger.info(f"[{api_key['api_key']}] - Received Request at /v1/mafia/games/stats")

    sql = text("""
        SELECT
          ROUND(
            COUNT(*) FILTER (WHERE t.name = 'Mafia')::numeric / NULLIF(COUNT(*), 0)
          , 2) AS mafia_win_rate,
          ROUND(
            COUNT(*) FILTER (WHERE t.name = 'Innocent')::numeric / NULLIF(COUNT(*), 0)
          , 2) AS innocent_win_rate
        FROM games g
        JOIN teams t
          ON g.winning_team = t.team_id
        WHERE g.approved = TRUE
    """)

    result = db.execute(sql).mappings().one_or_none()

    if result is None:
        return GameStatsSchema(mafia_win_rate=None, innocent_win_rate=None)

    result_dict = dict(result)
    for key, value in result_dict.items():
        if isinstance(value, Decimal):
            result_dict[key] = float(value)

    return GameStatsSchema(**result_dict)
