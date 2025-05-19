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
  player_name VARCHAR(256)
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
