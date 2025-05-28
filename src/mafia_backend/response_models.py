from typing import Optional

from pydantic import BaseModel

class PlayerSchema(BaseModel):
    player_id: int
    name:      Optional[str] = None

    class Config:
        orm_mode = True


class PlayerStatsSchema(BaseModel):
    player_id: int
    player_name: str
    games_played: int
    mafia_games: int
    innocent_games: int
    mafia_win_rate: float | None
    innocent_win_rate: float | None
    spy_check_rate: float | None
    medic_self_save_rate: float | None
    successful_medic_save_rate: float | None
    successful_assassin_shot_rate: float | None

    model_config = {
        "from_attributes": True
    }

class GameStatsSchema(BaseModel):
    mafia_win_rate: float | None
    innocent_win_rate: float | None
