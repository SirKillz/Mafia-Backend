from datetime import datetime
from typing import List
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from .db_connection import Database
from .db_models import *

from mafia_backend.payload_models import PlayerSchema
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
                approved = 0,
                player_count = player_count,
                mafia_count = mafia_count,
                mafia_kill_power = game_payload.initialMafiaKillPower,
                day_count = game_payload.dayCount,
                night_count = game_payload.nightCount
            )
            session.add(game)
            session.commit()
            return game.game_id

    def create_player(self, player: PlayerSchema):
        with self.Session() as session:
            new_player = Player(name = player.name)
            session.add(new_player)
            session.commit()
            session.refresh(new_player)
            return new_player

    def get_players(self):
        with self.Session() as session:
            return session.query(Player).all()
        
    def get_roles(self):
        with self.Session() as session:
            return session.query(Role).all()

    def create_game_participants(self, game_id: int, game_players: List[PlayerSchema]):
        # preload your static lookups
        roles = self.get_roles()
        role_data = {r.role_name: r.role_id for r in roles}

        MAFIA = 1 
        INNOCENT = 2

        with self.Session() as session:
            # load the current set of players into a dict
            db_players = {p.name: p for p in session.query(Player).all()}

            for game_player in game_players:
                # 1) upsert the Player in this same session
                pl = db_players.get(game_player.name)
                if not pl:
                    pl = Player(name=game_player.name)
                    session.add(pl)
                    session.flush()            # ← assigns pl.player_id
                    db_players[game_player.name] = pl

                # 2) compute constants per‐player
                role_id = role_data[game_player.role]
                team_id = MAFIA if game_player.isMafia else INNOCENT

                spy_stats        = game_player.spy_stats()
                medic_stats      = game_player.medic_save_stats()
                medic_self_stats = game_player.medic_self_save_stats()
                assassin_stats   = game_player.assassin_stats()

                # 3) add the join‐row
                session.add(
                    GameParticipant(
                        game_id                   = game_id,
                        player_id                 = pl.player_id,
                        role_id                   = role_id,
                        team_id                   = team_id,
                        days_survived             = game_player.daysSurvived,
                        nights_survived           = game_player.nightsSurvived,
                        successful_spy_checks     = spy_stats["numerator"],
                        spy_check_opportunities   = spy_stats["denominator"],
                        medic_self_saves          = medic_self_stats["numerator"],
                        successful_medic_saves    = medic_stats["numerator"],
                        medic_save_opportunities  = medic_stats["denominator"],
                        successful_assassin_shots = assassin_stats["numerator"],
                        assassin_shot_attempts    = assassin_stats["denominator"],
                    )
                )

            session.commit()

    def get_player_stats(self, player_id: int) -> dict:
        """
        Run a single raw-SQL query to pull all stats for one player—
        including per-role game counts—and convert any Decimal rates
        to floats for JSON serialization.
        """
        sql = text("""
            SELECT
              p.player_id,
              p.name                                         AS player_name,

              -- total games
              COUNT(*)                                       AS games_played,

              -- role-specific game counts
              SUM(r.role_name = 'Spy')                       AS spy_games_played,
              SUM(r.role_name = 'Medic')                     AS medic_games_played,
              SUM(r.role_name = 'Assassin')                  AS assassin_games_played,

              -- team breakdown
              SUM(t.name = 'Mafia')                          AS mafia_games,
              SUM(t.name = 'Innocent')                       AS innocent_games,

              -- team win rates
              ROUND(
                SUM((t.name = 'Mafia') AND g.winning_team = gp.team_id)
                / NULLIF(SUM(t.name = 'Mafia'), 0)
              , 2)                                            AS mafia_win_rate,
              ROUND(
                SUM((t.name = 'Innocent') AND g.winning_team = gp.team_id)
                / NULLIF(SUM(t.name = 'Innocent'), 0)
              , 2)                                            AS innocent_win_rate,

              -- detailed rates
              CASE
                WHEN SUM(gp.spy_check_opportunities) > 0
                THEN ROUND(
                       SUM(gp.successful_spy_checks)
                       / SUM(gp.spy_check_opportunities)
                     , 2)
              END                                             AS spy_check_rate,
              CASE
                WHEN SUM(gp.medic_save_opportunities) > 0
                THEN ROUND(
                       SUM(gp.medic_self_saves)
                       / SUM(gp.medic_save_opportunities)
                     , 2)
              END                                             AS medic_self_save_rate,
              CASE
                WHEN SUM(gp.medic_save_opportunities) > 0
                THEN ROUND(
                       SUM(gp.successful_medic_saves)
                       / SUM(gp.medic_save_opportunities)
                     , 2)
              END                                             AS successful_medic_save_rate,
              CASE
                WHEN SUM(gp.assassin_shot_attempts) > 0
                THEN ROUND(
                       SUM(gp.successful_assassin_shots)
                       / SUM(gp.assassin_shot_attempts)
                     , 2)
              END                                             AS successful_assassin_shot_rate

            FROM players p
            JOIN game_participants gp ON p.player_id = gp.player_id
            JOIN teams t             ON gp.team_id    = t.team_id
            JOIN games g             ON gp.game_id    = g.game_id
            JOIN roles r             ON gp.role_id    = r.role_id

            WHERE p.player_id = :player_id
              AND g.approved = 1

            GROUP BY p.player_id, p.name
        """)

        with self.Session() as session:
            row = session.execute(sql, {"player_id": player_id}).mappings().one_or_none()
            if not row:
                raise ValueError(f"No stats found for player_id={player_id}")

            stats = dict(row)
            # Convert any Decimal → float so JSONResponse can serialize
            for key, val in stats.items():
                if isinstance(val, Decimal):
                    stats[key] = float(val)
            return stats

    def get_overall_team_win_rates_raw(self) -> dict:
        """
        Return overall Mafia and Innocent win rates via a raw SQL aggregation.
        """
        sql = text("""
            SELECT
              ROUND(
                SUM(t.name = 'Mafia') / COUNT(*)
              , 2) AS mafia_win_rate,
              ROUND(
                SUM(t.name = 'Innocent') / COUNT(*)
              , 2) AS innocent_win_rate
            FROM games g
            JOIN teams t
              ON g.winning_team = t.team_id
            WHERE g.approved = 1
        """)

        with self.Session() as session:
            row = session.execute(sql).mappings().one_or_none()
            if row is None:
                return {"mafia_win_rate": None, "innocent_win_rate": None}

            stats = dict(row)
            # convert any Decimal rates to float
            for k, v in stats.items():
                if isinstance(v, Decimal):
                    stats[k] = float(v)
            return stats    
        
    def get_average_stat_rates_raw(self) -> dict:
        """
        Compute the same average per-player rates via a raw SQL query.
        """
        sql = text("""
            WITH player_rates AS (
              SELECT
                gp.player_id,
                CASE
                  WHEN SUM(gp.spy_check_opportunities) > 0
                  THEN SUM(gp.successful_spy_checks)
                       / SUM(gp.spy_check_opportunities)
                END AS spy,
                CASE
                  WHEN SUM(gp.medic_save_opportunities) > 0
                  THEN SUM(gp.medic_self_saves)
                       / SUM(gp.medic_save_opportunities)
                END AS medic_self,
                CASE
                  WHEN SUM(gp.medic_save_opportunities) > 0
                  THEN SUM(gp.successful_medic_saves)
                       / SUM(gp.medic_save_opportunities)
                END AS medic_success,
                CASE
                  WHEN SUM(gp.assassin_shot_attempts) > 0
                  THEN SUM(gp.successful_assassin_shots)
                       / SUM(gp.assassin_shot_attempts)
                END AS assassin
              FROM game_participants gp
              JOIN games g
                ON gp.game_id = g.game_id
              WHERE g.approved = 1
              GROUP BY gp.player_id
            )
            SELECT
              ROUND(AVG(spy), 2)             AS avg_spy_check_rate,
              ROUND(AVG(medic_self), 2)      AS avg_medic_self_save_rate,
              ROUND(AVG(medic_success), 2)   AS avg_successful_medic_save_rate,
              ROUND(AVG(assassin), 2)        AS avg_successful_assassin_shot_rate
            FROM player_rates;
        """)

        with self.Session() as session:
            row = session.execute(sql).mappings().one_or_none()
            if row is None:
                return {
                  "avg_spy_check_rate": None,
                  "avg_medic_self_save_rate": None,
                  "avg_successful_medic_save_rate": None,
                  "avg_successful_assassin_shot_rate": None
                }

            result = dict(row)
            # Cast Decimal → float
            for k, v in result.items():
                if isinstance(v, Decimal):
                    result[k] = float(v)
            return result

