"""QUERY-09 meta-compliance check + execution smoke for Phase 3 SQL slate.

Per .planning/phases/03-analytical-layer-sql-python/03-CONTEXT.md:
- D-07: 8-query slate with locked filenames.
- D-08: every .sql opens with the 6-section structured header.
- QUERY-09: slate-collective coverage of window functions + CTEs + cross-source FTN<->pbp JOIN.

Run via:  python scripts/_verify_queries_run.py
Exits 0 if every check passes, 1 otherwise.
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "data" / "nfl_defensive_tendencies.db"
QUERIES = REPO / "queries"

EXPECTED_FILES = [
    "01_tendency_distribution_by_team.sql",
    "02_blitz_rate_by_situation.sql",
    "03_red_zone_vs_midfield.sql",
    "04_epa_allowed_by_blitz.sql",
    "05_third_long_pressure_tendencies.sql",
    "06_play_action_response.sql",
    "07_situational_predictability_score.sql",
    "08_blitz_rate_trend_by_season.sql",
]

HEADER_PREFIXES = (
    "-- Question:",
    "-- Filter:",
    "-- Result shape:",
    "-- Hypothesis:",
    "-- Caveats:",
    "-- N expected:",
)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    if not DB.exists():
        fail(f"Phase 2 DB not found at {DB}; run `python -m etl.run` first")

    on_disk = sorted(p.name for p in QUERIES.glob("*.sql"))
    if on_disk != sorted(EXPECTED_FILES):
        fail(f"Filename slate mismatch.\n  expected: {EXPECTED_FILES}\n  on disk:  {on_disk}")

    has_window = False
    has_cte = False
    has_cross_join = False

    with sqlite3.connect(str(DB)) as conn:
        for fname in EXPECTED_FILES:
            path = QUERIES / fname
            sql = path.read_text(encoding="utf-8")

            for prefix in HEADER_PREFIXES:
                if prefix not in sql:
                    fail(f"{fname}: missing header section {prefix!r}")

            if re.search(r"OVER\s*\(", sql):
                has_window = True
            if re.search(r"(?im)^\s*WITH\s+\w+\s+AS\s*\(", sql):
                has_cte = True
            if "JOIN ftn_play" in sql and "USING (game_id, play_id)" in sql:
                has_cross_join = True

            try:
                rows = conn.execute(sql).fetchall()
            except sqlite3.Error as e:
                fail(f"{fname}: SQL execution failed: {e}")

            if len(rows) == 0:
                fail(f"{fname}: returned an empty result set")

            print(f"OK  {fname}  ({len(rows)} rows)")

    if not has_window:
        fail("QUERY-09 meta-compliance: no slate query uses a window function (OVER ...)")
    if not has_cte:
        fail("QUERY-09 meta-compliance: no slate query uses a CTE (WITH ...)")
    if not has_cross_join:
        fail("QUERY-09 meta-compliance: no slate query performs the cross-source FTN<->pbp JOIN")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
