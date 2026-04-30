"""Per-year idempotent pbp loader (ETL-01).

Iterates SEASONS, pulls each year via nfl_data_py.import_pbp_data, applies the
PBP_COLUMNS whitelist at pull-time, asserts row count > 40_000 (per
02-CONTEXT.md specifics), and writes parquet to data/raw/pbp_{year}.parquet.

Idempotent: skips a year whose parquet already exists (per D-11). Resilient
to single-year network failures -- re-running picks up where it left off.

Fail-fast on network errors per D-15: nfl_data_py exceptions bubble up; no
retry-with-backoff. The recruiter recovery is "re-run the command" and the
parquet cache means already-pulled years aren't re-fetched.
"""

import logging
from pathlib import Path

import nfl_data_py as nfl

from etl.columns import PBP_COLUMNS, SEASONS

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
MIN_ROWS_PER_YEAR = 40_000  # per 02-CONTEXT.md specifics


def load_pbp() -> None:
    """Pull pbp year-by-year and cache to parquet. Idempotent."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year in SEASONS:
        out = RAW_DIR / f"pbp_{year}.parquet"
        if out.exists():
            logger.info("[skip] pbp_%d.parquet already cached", year)
            continue
        logger.info("Pulling pbp %d ...", year)
        df = nfl.import_pbp_data([year], columns=PBP_COLUMNS, downcast=True)
        assert len(df) > MIN_ROWS_PER_YEAR, (
            f"pbp {year} returned {len(df):,} rows; expected > {MIN_ROWS_PER_YEAR:,} "
            f"(regular season alone is ~46k; with playoffs ~49k). Possible silent "
            f"CDN failure -- see PITFALLS.md #17."
        )
        df.to_parquet(out, index=False)
        logger.info("Wrote pbp_%d.parquet (%s rows)", year, f"{len(df):,}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    load_pbp()
