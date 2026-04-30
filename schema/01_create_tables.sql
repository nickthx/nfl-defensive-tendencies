-- schema/01_create_tables.sql -- DDL for the three project tables: games, plays, ftn_play.
-- Source decisions: 02-CONTEXT.md D-05 (season + week denormalized onto plays),
-- D-06 (broader ~24-column plays whitelist), D-07 (REG + POST included; season_type
-- on games), D-08 (games is identity-only, ~6 columns). FTN whitelist is the 8
-- charting columns that survived Phase 1's 30% NaN cutoff (D-AUDIT).
-- Applied by etl/build_db.py via conn.executescript().

CREATE TABLE games (
    game_id      TEXT PRIMARY KEY,            -- nflverse game_id, e.g. '2023_01_KC_DET'
    season       INTEGER NOT NULL,
    week         INTEGER NOT NULL,
    season_type  TEXT NOT NULL,               -- 'REG' or 'POST' (per D-07)
    home_team    TEXT NOT NULL,
    away_team    TEXT NOT NULL
);

CREATE TABLE plays (
    -- identity (per D-05: season + week denormalized so situational queries skip the games join)
    game_id              TEXT NOT NULL,
    play_id              INTEGER NOT NULL,
    season               INTEGER NOT NULL,
    week                 INTEGER NOT NULL,
    -- teams
    posteam              TEXT,
    defteam              TEXT,
    -- situation
    qtr                  INTEGER,
    down                 INTEGER,
    ydstogo              INTEGER,
    yardline_100         INTEGER,
    score_differential   INTEGER,
    -- time (used by competitive_plays view's end-of-half cutoff per D-02)
    half_seconds_remaining INTEGER,
    -- play classification
    play_type            TEXT,                -- 'pass', 'run', 'punt', 'field_goal', etc.
    pass                 INTEGER,             -- 0/1
    rush                 INTEGER,             -- 0/1
    pass_attempt         INTEGER,             -- 0/1 (per D-06 broader whitelist; STAT-08 sensitivity)
    rush_attempt         INTEGER,             -- 0/1
    -- outcome
    yards_gained         INTEGER,
    epa                  REAL,
    success              INTEGER,             -- 0/1 (per D-06)
    -- analytical extras (per D-06 broader whitelist)
    cpoe                 REAL,                -- completion percentage over expected
    xpass                REAL,                -- expected pass probability
    air_yards            INTEGER,
    -- filter input (consumed by competitive_plays view)
    wp                   REAL,                -- win probability
    PRIMARY KEY (game_id, play_id),
    FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE ftn_play (
    game_id              TEXT NOT NULL,
    play_id              INTEGER NOT NULL,
    -- pressure / front (anchor dimensions S1, S2, S4 per Phase 1 D-AUDIT)
    n_blitzers           INTEGER,
    n_pass_rushers       INTEGER,
    -- play-fakery
    is_play_action       INTEGER,             -- 0/1 SQLite has no native BOOL (per CONTEXT specifics)
    is_screen_pass       INTEGER,
    is_rpo               INTEGER,
    -- personnel / location
    qb_location          TEXT,                -- 'U' under-center / 'S' shotgun / 'P' pistol (TEXT per CONTEXT specifics)
    n_offense_backfield  INTEGER,
    starting_hash        TEXT,
    PRIMARY KEY (game_id, play_id),
    FOREIGN KEY (game_id, play_id) REFERENCES plays(game_id, play_id)
);
