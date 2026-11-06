import logging
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.Auth.api_key import get_api_key
from app.Database.session_factory import get_db
from app.response_models import GameStatsSchema


game_stats_router = APIRouter(prefix="/v1/mafia")
logger = logging.getLogger("app_logger")  # Configure inside src/app/__main__.py


@game_stats_router.get("/games/stats", response_model=GameStatsSchema)
async def get_team_win_rates(
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

    result = db.execute(sql).fetchone()

    if result is None:
        return GameStatsSchema(mafia_win_rate=None, innocent_win_rate=None)

    result_dict = dict(result)
    for key, value in result_dict.items():
        if isinstance(value, Decimal):
            result_dict[key] = float(value)

    return GameStatsSchema(**result_dict)