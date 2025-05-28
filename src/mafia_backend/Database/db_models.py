from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Team(Base):
    __tablename__ = "teams"
    team_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), nullable=False)

class Player(Base):
    __tablename__ = "players"
    player_id = Column(Integer, primary_key=True)
    name = Column(String(256))

class Game(Base):
    __tablename__ = "games"
    game_id = Column(BigInteger, primary_key=True)
    played_at = Column(DateTime, nullable=False)
    approved = Column(Boolean, nullable=False)
    winning_team = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    player_count = Column(Integer)
    mafia_count = Column(Integer)
    mafia_kill_power = Column(Integer)
    day_count = Column(Integer)
    night_count = Column(Integer)

class GameParticipant(Base):
    __tablename__ = "game_participants"
    game_id = Column(BigInteger, ForeignKey("games.game_id"), primary_key=True)
    player_id = Column(Integer, ForeignKey("players.player_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.team_id"), nullable=False)
    days_survived = Column(Integer)
    nights_survived = Column(Integer)
    successful_spy_checks = Column(Integer)
    spy_check_opportunities = Column(Integer)
    medic_self_saves = Column(Integer)
    successful_medic_saves = Column(Integer)
    medic_save_opportunities = Column(Integer)
    successful_assassin_shots = Column(Integer)
    assassin_shot_attempts = Column(Integer)
