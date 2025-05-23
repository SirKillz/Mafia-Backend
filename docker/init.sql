CREATE TABLE IF NOT EXISTS teams (
  team_id INT AUTO_INCREMENT PRIMARY KEY,
  name    VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS roles (
  role_id   INT AUTO_INCREMENT PRIMARY KEY,
  role_name VARCHAR(50)       NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
  player_id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS games (
  game_id          BIGINT      AUTO_INCREMENT PRIMARY KEY,
  played_at        DATETIME    NOT NULL,
  winning_team     INT       NOT NULL,
  player_count     INT,
  mafia_count      INT,
  mafia_kill_power INT,
  day_count        INT,
  night_count      INT,
  FOREIGN KEY (winning_team) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS game_participants (
  game_id                 BIGINT NOT NULL,
  player_id               INT    NOT NULL,
  role_id                 INT    NOT NULL,
  team_id                 INT    NOT NULL,

  survived_full_game      TINYINT(1) DEFAULT 0,
  days_survived             INT    DEFAULT NULL,
  nights_survived           INT    DEFAULT NULL,
  successful_spy_checks     INT    DEFAULT NULL,
  spy_check_opportunities   INT    DEFAULT NULL,
  medic_self_saves          INT    DEFAULT NULL,
  successful_medic_saves    INT    DEFAULT NULL,
  medic_save_opportunities  INT    DEFAULT NULL,
  successful_assassin_shots INT    DEFAULT NULL,
  assassin_shot_attempts    INT    DEFAULT NULL,

  PRIMARY KEY (game_id, player_id),

  FOREIGN KEY (game_id)   REFERENCES games(game_id),
  FOREIGN KEY (player_id) REFERENCES players(player_id),
  FOREIGN KEY (role_id)   REFERENCES roles(role_id),
  FOREIGN KEY (team_id)   REFERENCES teams(team_id)
);

INSERT into teams (name)
VALUES ("Mafia");

INSERT into teams (name)
VALUES ("Innocent");

INSERT into roles (role_name)
VALUES ("Innocent");

INSERT into roles (role_name)
VALUES ("Spy");

INSERT into roles (role_name)
VALUES ("Medic");

INSERT into roles (role_name)
VALUES ("Assassin");

INSERT into roles (role_name)
VALUES ("Attorney");

INSERT into roles (role_name)
VALUES ("Undercover Cop");

INSERT into roles (role_name)
VALUES ("Guild Member");

INSERT into roles (role_name)
VALUES ("Mafia");

INSERT into roles (role_name)
VALUES ("Mafia Boss");

INSERT into roles (role_name)
VALUES ("Consigliere");

INSERT into roles (role_name)
VALUES ("Enforcer");

INSERT INTO players (name)
VALUES 
  ('Nick Killeen'),
  ('Luke Hecht'),
  ('Ryan O''Meara'),
  ('Cole Bateman'),
  ('Connor Burns'),
  ('Colin Leschman'),
  ('Matt Bovard'),
  ('Mike Bovard'),
  ('Curt Hasan'),
  ('Billy Roche'),
  ('Kyle Norton'),
  ('Jared Guzzi'),
  ('Gavin Burns'),
  ('Jonah Farrar'),
  ('Aaron Gowaski'),
  ('Ronaldho Cadenillas'),
  ('Ryan Everly'),
  ('Dan Bornstein');
