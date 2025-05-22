from typing import List, Optional
from pydantic import BaseModel

class PlayerSchema(BaseModel):
    name: str
    id: int
    role: str
    isAlive: bool
    canPerformAction: bool
    daysSurvived: int
    nightsSurvived: int
    isInnocent: bool
    isMafia: bool
    isSpecialInnocent: bool
    isSpecialMafia: bool

class GamePayload(BaseModel):
    players: List[PlayerSchema]
    gamePhase: str
    aliveCount: int
    innocentCount: int
    mafiaCount: int
    startingMafiaCount: int
    dayCount: int
    nightCount: int
    mafiaKillPower: int
    previousMedicSave: Optional[int] = None
    previousEnforcerBlock: Optional[int] = None
    previousBossSilence: Optional[int] = None
    consiHasChecked: bool
    assassinHasShot: bool
    attorneyHasDefended: bool
    lastNightRoutine: Optional[str] = None
    winningTeam: int
