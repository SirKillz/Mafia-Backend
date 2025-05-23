from typing import Optional

from pydantic import BaseModel

class PlayerSchema(BaseModel):
    player_id: int
    name:      Optional[str] = None

    class Config:
        orm_mode = True
