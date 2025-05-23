from datetime import datetime

from sqlalchemy.orm import sessionmaker

from .db_connection import Database
from .db_models import *

from mafia_backend.payload_models import GamePayload

class QueryService(Database):
    def __init__(self):
        super().__init__()
        self.engine  = self.get_engine()
        self.Session = sessionmaker(bind=self.engine)

    def _get_winning_team_id(self, winning_team):
        """
        Given a winning team name, return the corresponding DB ID
        """

        with self.Session() as session:
            team: Team = session.query(Team).filter(Team.name == winning_team).first()
            if team is None:
                raise ValueError(f"No team found with name {winning_team}")
            return team.team_id

    def create_game(self, game_payload: GamePayload):
        played_at = datetime.now()
        player_count = len(game_payload.players)
        
        mafia_count = 0
        for player in game_payload.players:
            if player.isMafia:
                mafia_count += 1

        winning_team_id = self._get_winning_team_id(game_payload.winningTeam)

        with self.Session() as session:
            game = Game(
                played_at = played_at,
                winning_team = winning_team_id,
                player_count = player_count,
                mafia_count = mafia_count,
                mafia_kill_power = game_payload.initialMafiaKillPower,
                day_count = game_payload.dayCount,
                night_count = game_payload.nightCount
            )
            session.add(game)
            session.commit()
            return game.game_id

    def get_players(self):
        with self.Session() as session:
            return session.query(Player).all()       

