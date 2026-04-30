"""Shared analytical scaffolding — DB connection, sample-size filter, RNG seed.

Per .planning/phases/03-analytical-layer-sql-python/03-CONTEXT.md Claude's Discretion:
- SEED is module-level and must be reseeded at the top of every notebook
- DB_PATH points to the gitignored Phase 2 SQLite build
- get_conn() returns a plain sqlite3.Connection (no SQLAlchemy)
- min_n_filter() returns a filtered DataFrame and emits logging.WARNING for drops
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import pandas as pd

# Random seed used for any stochastic step in downstream notebooks.
# Per CLAUDE.md "Project Realities" + STAT-01: notebooks reseed numpy at top via np.random.seed(SEED).
SEED: int = 42

# Resolved at import time; analysis/_common.py -> analysis/ -> repo-root -> data/<db>.
DB_PATH: Path = Path(__file__).resolve().parent.parent / "data" / "nfl_defensive_tendencies.db"

logger = logging.getLogger(__name__)


def get_conn(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    """Open a sqlite3.Connection to the Phase 2 build.

    PARSE_DECLTYPES is enabled so any future TIMESTAMP columns hydrate cleanly.
    Notebook usage:

        with get_conn() as conn:
            df = pd.read_sql_query(SQL_PATH.read_text(), conn)
    """
    return sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)


def min_n_filter(
    df: pd.DataFrame,
    n_col: str = "n",
    n_threshold: int = 30,
) -> pd.DataFrame:
    """Drop rows where df[n_col] < n_threshold; emit a WARNING listing dropouts.

    Per STAT-07 + CLAUDE.md sample-size discipline: N>=30 for any tendency claim.
    The N>=15 narrative-flag exception lives in the FINDINGS.md cell that emits
    the claim, NOT in this helper. The helper does NOT raise — it returns the
    filtered DataFrame and logs the dropouts so the notebook can display them.

    Identifying columns ('defteam', 'situation_id', 'season') are echoed in the
    log line when present; missing columns are silently skipped.
    """
    if n_col not in df.columns:
        raise KeyError(f"min_n_filter: column {n_col!r} not in df.columns={list(df.columns)}")

    mask = df[n_col] >= n_threshold
    dropped = df.loc[~mask]
    if len(dropped) > 0:
        id_cols = [c for c in ("defteam", "situation_id", "season") if c in dropped.columns]
        if id_cols:
            tuples = dropped[id_cols].apply(tuple, axis=1).tolist()
        else:
            tuples = [f"row_{i}" for i in dropped.index.tolist()]
        logger.warning(
            "min_n_filter dropped %d rows below N>=%d: %s",
            len(dropped),
            n_threshold,
            tuples,
        )
    return df.loc[mask].reset_index(drop=True)
