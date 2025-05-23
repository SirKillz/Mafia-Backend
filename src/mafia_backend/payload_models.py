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
    spyMafiaHitPercentage: list
    medicSavePercentage: list
    medicSelfSavePercentage: list
    assassinMafiaHitPercentage: list

    def spy_stats(self):
        positive_actions = 0
        total_opps = len(self.spyMafiaHitPercentage)

        for action in self.spyMafiaHitPercentage:
            if action:
                positive_actions += 1
        
        return {
            "numerator": positive_actions,
            "denominator": total_opps
        }
    
    def medic_save_stats(self):
        positive_actions = 0
        total_opps = len(self.medicSavePercentage)

        for action in self.medicSavePercentage:
            if action:
                positive_actions += 1
        
        return {
            "numerator": positive_actions,
            "denominator": total_opps
        }
    
    def medic_self_save_stats(self):
        positive_actions = 0
        total_opps = len(self.medicSelfSavePercentage)

        for action in self.medicSelfSavePercentage:
            if action:
                positive_actions += 1
        
        return {
            "numerator": positive_actions,
            "denominator": total_opps
        }
    
    def assassin_stats(self):
        positive_actions = 0
        total_opps = len(self.assassinMafiaHitPercentage)

        for action in self.assassinMafiaHitPercentage:
            if action:
                positive_actions += 1
        
        return {
            "numerator": positive_actions,
            "denominator": total_opps
        }



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
