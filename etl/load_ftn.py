"""Per-year idempotent FTN charting loader (ETL-02).

Iterates SEASONS, pulls each year via nfl_data_py.import_ftn_data, applies the
FTN_COLUMNS whitelist at pull-time, asserts row count > 38_000 (per
02-CONTEXT.md specifics), and writes parquet to data/raw/ftn_{year}.parquet.

Idempotent: skips a year whose parquet already exists (per D-11). Resilient
to single-year network failures -- re-running picks up where it left off.

Fail-fast on network errors per D-15: nfl_data_py exceptions bubble up; no
retry-with-backoff.
"""

import logging
from pathlib import Path

import nfl_data_py as nfl

from etl.columns import FTN_COLUMNS, SEASONS

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
MIN_ROWS_PER_YEAR = 38_000  # per 02-CONTEXT.md specifics


def load_ftn() -> None:
    """Pull FTN charting year-by-year and cache to parquet. Idempotent."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year in SEASONS:
        out = RAW_DIR / f"ftn_{year}.parquet"
        if out.exists():
            logger.info("[skip] ftn_%d.parquet already cached", year)
            continue
        logger.info("Pulling FTN %d ...", year)
        df = nfl.import_ftn_data([year], columns=FTN_COLUMNS, downcast=True)
        assert len(df) > MIN_ROWS_PER_YEAR, (
            f"FTN {year} returned {len(df):,} rows; expected > {MIN_ROWS_PER_YEAR:,} "
            f"(FTN charts ~46k plays per season). Possible silent CDN failure -- "
            f"see PITFALLS.md #17."
        )
        df.to_parquet(out, index=False)
        logger.info("Wrote ftn_%d.parquet (%s rows)", year, f"{len(df):,}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    load_ftn()
