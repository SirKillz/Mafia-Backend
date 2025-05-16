CREATE TABLE IF NOT EXISTS teams (
    team_id INT AUTOINCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE roles (
    role_id SMALLINT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
);

CREATE TABLE players (
    player_id BIGINT AUTO_INCREMENT PRIAMRY KEY,
    player_name VARCHAR(256),
);

CREATE TABLE IF NOT EXISTS games (
  game_id BIGINT AUTO_INCREMENT, PRIMARY KEY,
  played_at DATETIME NOT NULL,
  winning_team BIGINT NOT NULL REFERENCES teams(team_id),
  player_count INT,
  mafia_count INT,
  mafia_kill_power INT,
  day_count INT,
  night_count INT,
);

CREATE TABLE IF NOT EXISTS game_participants (
  game_id    BIGINT NOT NULL  REFERENCES games(game_id),
  player_id  BIGINT NOT NULL  REFERENCES players(player_id),
  role_id    SMALLINT NOT NULL  REFERENCES roles(role_id),
  team_id    BIGINT NOT NULL  REFERENCES teams(team_id),
  survived_full_game SMALLINT(0),
  PRIMARY KEY (game_id, player_id)
  /* you can also add common stats columns here, see below */

  successful_spy_checks     INT DEFAULT NULL,
  spy_check_opportunities   INT DEFAULT NULL,
  medic_self_saves          INT DEFAULT NULL,
  successful_medic_saves    INT DEFAULT NULL,
  medic_save_opportunities  INT DEFAULT NULL,
  successful_assassin_shots INT DEFAULT NULL,
  assassin_shot_attempts    INT DEFAULT NULL,
);