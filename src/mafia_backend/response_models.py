from pydantic import BaseModel

class PlayerSchema(BaseModel):
    player_id: int
    player_name: str

    class Config:
        orm_mode = True
