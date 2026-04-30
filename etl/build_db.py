"""Read parquet caches, join FTN <-> pbp, apply schema, write SQLite (ETL-04).

Reads data/raw/pbp_{year}.parquet and data/raw/ftn_{year}.parquet for each
year in SEASONS, joins on (nflverse_game_id, nflverse_play_id) == (game_id,
play_id) with validate='one_to_one' (per PITFALLS.md #3), asserts post-join
match_rate > 0.95 and post-join len > 130_000 (per 02-CONTEXT.md D-12),
applies all three schema files via executescript, then INSERTs games / plays /
ftn_play.

Per D-09: every invocation DROP+CREATE the SQLite database file. Same parquet
input -> same SQLite output, deterministic.

Per D-10 + ROADMAP: DB filename is nfl_defensive_tendencies.db (NOT
nfl_coverage.db -- the architecture doc still references the old name).
"""

import logging
import sqlite3
from pathlib import Path

import pandas as pd

from etl.columns import (
    FTN_PLAY_COLUMNS,
    FTN_RENAME,
    GAMES_COLUMNS,
    PBP_KEYS,
    PLAYS_COLUMNS,
    SEASONS,
)

logger = logging.getLogger(__name__)

DB_PATH = Path("data/nfl_defensive_tendencies.db")
RAW_DIR = Path("data/raw")
SCHEMA_DIR = Path("schema")
SCHEMA_FILES = [
    SCHEMA_DIR / "01_create_tables.sql",
    SCHEMA_DIR / "02_indexes.sql",
    SCHEMA_DIR / "03_views.sql",
]

MIN_POSTJOIN_ROWS = 130_000  # per 02-CONTEXT.md specifics (verified Phase 1: 185,215)
MIN_MATCH_RATE = 0.95         # per ETL-04 (verified Phase 1: 0.9999)


def _read_parquet_concat(prefix: str) -> pd.DataFrame:
    """Read data/raw/{prefix}_{year}.parquet for each year in SEASONS and concat."""
    frames = []
    for year in SEASONS:
        path = RAW_DIR / f"{prefix}_{year}.parquet"
        assert path.exists(), f"Missing {path}; run load_{prefix}() first."
        frames.append(pd.read_parquet(path))
    df = pd.concat(frames, ignore_index=True)
    logger.info("Loaded %s: %s rows from %d parquet files",
                prefix, f"{len(df):,}", len(SEASONS))
    return df


def build_db() -> dict[str, int | float]:
    """Read parquet, join, apply schema, write SQLite. Returns row-count summary dict."""
    # Step 1: load parquet caches
    pbp = _read_parquet_concat("pbp")
    ftn = _read_parquet_concat("ftn")

    # Step 2: join FTN -> pbp on nflverse keys (per PITFALLS.md #3)
    # left_on=PBP_KEYS, right_on=FTN_KEYS keeps all pbp rows; FTN may not chart
    # every play. validate='one_to_one' raises if a key is duplicated either side.
    logger.info("Joining FTN to pbp on (nflverse_game_id, nflverse_play_id) ...")
    joined = pbp.merge(
        ftn,
        left_on=PBP_KEYS,
        right_on=["nflverse_game_id", "nflverse_play_id"],
        how="left",
        validate="one_to_one",
    )

    # Match-rate calculation per CONTEXT specifics:
    # joined['play_type'].notna().mean() -- the pbp-side play_type, which goes
    # NaN when a row was right-only (would only happen with how='right' or
    # 'outer'; with how='left' it's effectively an FTN-coverage rate computed
    # against the pbp universe, which matches the Phase 1 audit pattern).
    match_rate = joined["play_type"].notna().mean()
    logger.info("Joined: %s rows, match_rate=%.4f", f"{len(joined):,}", match_rate)
    assert match_rate > MIN_MATCH_RATE, (
        f"FTN<->pbp match_rate {match_rate:.4f} below {MIN_MATCH_RATE} threshold; "
        f"check PITFALLS.md #3 (wrong join keys cause silent mis-joins)."
    )
    assert len(joined) > MIN_POSTJOIN_ROWS, (
        f"Post-join row count {len(joined):,} below {MIN_POSTJOIN_ROWS:,} threshold; "
        f"verified Phase 1 4-season total was 185,215."
    )

    # Step 3: derive the three target frames
    # 3a. games -- identity-only, one row per game (per D-08).
    games = (
        pbp[GAMES_COLUMNS]
        .drop_duplicates(subset=["game_id"])
        .reset_index(drop=True)
    )
    logger.info("games frame: %s rows", f"{len(games):,}")

    # 3b. plays -- broader analytical whitelist (per D-06).
    plays = pbp[PLAYS_COLUMNS].copy()

    # 3c. ftn_play -- rename FTN-side keys to canonical (game_id, play_id), then select.
    ftn_renamed = ftn.rename(columns=FTN_RENAME)
    ftn_play = ftn_renamed[FTN_PLAY_COLUMNS].copy()

    # Step 4: DROP+CREATE the database file (per D-09)
    if DB_PATH.exists():
        logger.info("Removing existing %s (D-09: DROP+CREATE every invocation)", DB_PATH)
        DB_PATH.unlink()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Step 5: connect, apply schema, insert
    with sqlite3.connect(DB_PATH) as conn:
        for sql_file in SCHEMA_FILES:
            assert sql_file.exists(), f"Missing schema file {sql_file}"
            logger.info("Applying %s", sql_file)
            conn.executescript(sql_file.read_text())

        # to_sql with if_exists='append' inserts into the empty tables created above.
        # method='multi' batches inserts; chunksize keeps memory bounded.
        games.to_sql("games", conn, if_exists="append", index=False,
                     method="multi", chunksize=500)
        plays.to_sql("plays", conn, if_exists="append", index=False,
                     method="multi", chunksize=500)
        ftn_play.to_sql("ftn_play", conn, if_exists="append", index=False,
                        method="multi", chunksize=500)
        conn.commit()

        # Sanity: query competitive_plays count for the run.py summary log
        comp_count = conn.execute("SELECT COUNT(*) FROM competitive_plays").fetchone()[0]

    summary = {
        "games": len(games),
        "plays": len(plays),
        "ftn_play": len(ftn_play),
        "match_rate": match_rate,
        "competitive_plays": comp_count,
    }
    logger.info("DB built: %s", summary)
    return summary


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    build_db()
