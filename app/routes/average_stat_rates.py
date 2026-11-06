import logging
from decimal import Decimal

from fastapi import APIRouter, Depends

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.Database.session_factory import get_db

from app.Auth.api_key import get_api_key
from app.response_models import AverageStatsSchema

average_stats_router = APIRouter(prefix="/v1/mafia")
logger = logging.getLogger("app_logger") # Configure inside src/app/__main__.py

@average_stats_router.get("/players/stats/average", response_model=AverageStatsSchema)
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

    result = db.execute(sql).fetchone()

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