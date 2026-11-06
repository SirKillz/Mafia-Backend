from datetime import date, datetime

from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class ReadPlayer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    player_id: int
    name: str | None = None

class GameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_id: int
    played_at: datetime
    approved: bool
    winning_team: int
    player_count: int
    mafia_count: int
    mafia_kill_power: int
    day_count: int
    night_count: int


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


class GameStatsSchema(BaseModel):
    mafia_win_rate: float | None
    innocent_win_rate: float | None


class AverageStatsSchema(BaseModel):
    avg_spy_check_rate: float | None
    avg_medic_self_save_rate: float | None
    avg_successful_medic_save_rate: float | None
    avg_successful_assassin_shot_rate: float | None


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
