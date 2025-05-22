from typing import List, Optional
from pydantic import BaseModel

class PlayerSchema(BaseModel):
    name: str
    id: str
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
    initialMafiaKillPower: int
    previousMedicSave: Optional[str] = None
    previousEnforcerBlock: Optional[str] = None
    previousBossSilence: Optional[str] = None
    consiHasChecked: bool
    assassinHasShot: bool
    attorneyHasDefended: bool
    lastNightRoutine: Optional[dict] = None
    winningTeam: str
