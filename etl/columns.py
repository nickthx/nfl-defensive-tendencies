"""Canonical column whitelists, rename map, join keys, and season scope for the ETL.

Single source of truth (per ARCHITECTURE.md Component Responsibilities and
.planning/phases/02-data-layer-etl-sqlite-schema/02-CONTEXT.md D-06..D-08, D-10).

All other etl/ modules import constants from here. Editing the SEASONS list is
the one and only knob a developer turns to re-scope the pull (per D-10:
zero CLI flags on etl/run.py).
"""

# Season scope (per CONTEXT D-10 + PROJECT.md Key Decision D-10: 4 seasons through Super Bowl LX)
SEASONS: list[int] = [2022, 2023, 2024, 2025]

# Join keys (per PITFALLS #3 -- pbp uses game_id/play_id; FTN uses nflverse_game_id/nflverse_play_id)
PBP_KEYS: list[str] = ["game_id", "play_id"]
FTN_KEYS: list[str] = ["nflverse_game_id", "nflverse_play_id"]

# Pull-time pbp column whitelist passed to nfl.import_pbp_data(columns=...).
# Per D-06: broader ~24-column set covering identity, situation, classification,
# outcome, and analytical extras for STAT-08 sensitivity. Includes season_type
# so games-table population (D-07) can split REG vs POST. Includes home_team
# and away_team so the games table can be derived in build_db.py without a
# second nflverse pull.
PBP_COLUMNS: list[str] = [
    # identity
    "game_id",
    "play_id",
    "season",
    "week",
    "season_type",       # 'REG' / 'POST' -- per D-07
    "home_team",         # populates games.home_team
    "away_team",         # populates games.away_team
    # teams
    "posteam",
    "defteam",
    # situation
    "qtr",
    "down",
    "ydstogo",
    "yardline_100",
    "score_differential",
    # time (consumed by competitive_plays D-02 end-of-half cutoff)
    "half_seconds_remaining",
    # play classification
    "play_type",
    "pass",
    "rush",
    "pass_attempt",
    "rush_attempt",
    # outcome
    "yards_gained",
    "epa",
    "success",
    # analytical extras (D-06)
    "cpoe",
    "xpass",
    "air_yards",
    # filter input (consumed by competitive_plays view's wp predicate)
    "wp",
]

# Pull-time FTN column whitelist passed to nfl.import_ftn_data(columns=...).
# Per D-07 + Phase 1 D-AUDIT: the 8 charting columns surviving the 30% NaN
# cutoff, plus the join-key pair. nflverse_game_id and nflverse_play_id are
# RENAMED to game_id / play_id below for ftn_play table insertion.
FTN_COLUMNS: list[str] = [
    "nflverse_game_id",
    "nflverse_play_id",
    "n_blitzers",
    "n_pass_rushers",
    "is_play_action",
    "is_screen_pass",
    "is_rpo",
    "qb_location",
    "n_offense_backfield",
    "starting_hash",
]

# After the FTN parquet is loaded and (in build_db.py) joined to pbp via
# left_on=PBP_KEYS, right_on=FTN_KEYS, the FTN-side keys are renamed to the
# canonical (game_id, play_id) pair before INSERT into ftn_play. This rename
# happens AFTER the merge -- see build_db.py for the call site.
FTN_RENAME: dict[str, str] = {
    "nflverse_game_id": "game_id",
    "nflverse_play_id": "play_id",
}

# Columns selected from pbp for the games table (per D-08: identity-only, 6 cols).
# Derived in build_db.py via drop_duplicates on (game_id, season, week, season_type, home_team, away_team).
GAMES_COLUMNS: list[str] = [
    "game_id",
    "season",
    "week",
    "season_type",
    "home_team",
    "away_team",
]

# Columns inserted into the plays table (per D-05 + D-06).
# Drops home_team and away_team (those go into games, not plays).
# Order matches schema/01_create_tables.sql exactly so DataFrame.to_sql with
# if_exists='append' inserts cleanly.
PLAYS_COLUMNS: list[str] = [
    "game_id",
    "play_id",
    "season",
    "week",
    "posteam",
    "defteam",
    "qtr",
    "down",
    "ydstogo",
    "yardline_100",
    "score_differential",
    "half_seconds_remaining",
    "play_type",
    "pass",
    "rush",
    "pass_attempt",
    "rush_attempt",
    "yards_gained",
    "epa",
    "success",
    "cpoe",
    "xpass",
    "air_yards",
    "wp",
]

# Columns inserted into the ftn_play table (post-rename).
# Order matches schema/01_create_tables.sql exactly.
FTN_PLAY_COLUMNS: list[str] = [
    "game_id",
    "play_id",
    "n_blitzers",
    "n_pass_rushers",
    "is_play_action",
    "is_screen_pass",
    "is_rpo",
    "qb_location",
    "n_offense_backfield",
    "starting_hash",
]
