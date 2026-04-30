"""Single CLI entry: `python -m etl.run` (ETL-05).

Zero CLI flags (per 02-CONTEXT.md D-10) -- the seasons constant in etl/columns.py
is the only knob a developer turns. Calls load_pbp -> load_ftn -> build_db,
emits a structured summary log block at the end (per D-16).

Performance budget (ETL-06): cold-cache run completes in <=10 minutes; warm-cache
run completes in <=5 minutes. Both budgets verified by the duration line in the
summary log.
"""

import logging
import time

from etl.build_db import DB_PATH, build_db
from etl.load_ftn import load_ftn
from etl.load_pbp import load_pbp

logger = logging.getLogger(__name__)


def _format_duration(seconds: float) -> str:
    """Format seconds as 'Xm YYs' for the D-16 summary line."""
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m {secs:02d}s"


def main() -> None:
    """Run the ETL end-to-end: load_pbp -> load_ftn -> build_db -> summary."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    start = time.monotonic()

    logger.info("=== ETL: nfl_defensive_tendencies ===")
    load_pbp()
    load_ftn()
    summary = build_db()

    duration = time.monotonic() - start

    # Structured summary block -- exact format per D-16.
    # Width-aligned for recruiter glance-test readability.
    logger.info("Database built: %s", DB_PATH)
    logger.info("  games:           %s rows", f"{summary['games']:>9,}")
    logger.info("  plays:           %s rows", f"{summary['plays']:>9,}")
    logger.info("  ftn_play:        %s rows", f"{summary['ftn_play']:>9,}")
    logger.info("  match_rate:      %s", f"{summary['match_rate']:>9.4f}")
    logger.info("  competitive_plays: %s rows", f"{summary['competitive_plays']:>9,}")
    logger.info("  duration:        %s", _format_duration(duration).rjust(9))


if __name__ == "__main__":
    main()
