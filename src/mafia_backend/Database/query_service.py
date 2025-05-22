from datetime import datetime

from db_connection import Database
from .db_models import *

from mafia_backend.payload_models import GamePayload

class QueryService(Database):
    def __init__(self):
        super().__init__()

    def create_game(self, game_payload: GamePayload):
        played_at = datetime.now()
        player_count = len(game_payload.players)
        
        mafia_count = 0
        for player in game_payload.players:
            if player.isMafia:
                mafia_count += 1


        with self.Session() as session:
            game = Game(
                played_at = played_at,
                winning_team = game_payload.winningTeam,
                player_count = player_count,
                mafia_count = mafia_count,
                mafia_kill_power = game_payload.mafiaKillPower,
                day_count = game_payload.dayCount,
                night_count = game_payload.nightCount
            )
            session.add(game)
            session.commit()
            

