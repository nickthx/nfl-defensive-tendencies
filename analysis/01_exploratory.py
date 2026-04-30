# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Exploratory: Descriptive Stats + Sample-Size Profiling (S1–S4)
#
# This is the STAT-03 deliverable. It performs descriptive statistics per
# pre-registered situation and profiles per-(defteam × situation × season)
# sample sizes, flagging any cell that falls below the N≥30 project floor.
#
# The 4-situation slate is locked in `docs/analysis-plan.md`:
# - S1 — 3rd-and-long (`down=3 AND ydstogo>=7`)
# - S2 — Red zone (`yardline_100<=20`)
# - S3 — 1st-and-10 (`down=1 AND ydstogo=10`)
# - S4 — 2nd-and-medium (`down=2 AND ydstogo BETWEEN 3 AND 6`)
#
# Any analysis outside this slate is labeled "Exploratory; not a headline
# finding" per the firewall convention in `docs/analysis-plan.md`.
#
# Outputs are cleared via `nbconvert --clear-output --inplace` before commit
# per CLAUDE.md File-Organization Rules. Hero PNGs (Phase 4 / VIZ-01) live
# only in `findings/images/`, never inside committed notebook outputs.

# %%
import logging
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `analysis.*` imports resolve regardless of
# the kernel's working directory. `__file__` is not defined in .ipynb cells, so
# we use Path.cwd() which resolves to the repo root when run via nbconvert or
# JupyterLab launched from the repo root. This is a documented deviation from
# the plan's `Path(__file__)` suggestion — see 03-01-SUMMARY.md.
_REPO_ROOT = Path.cwd()
# Walk up until we find analysis/ or hit the filesystem root (defensive).
for _candidate in [_REPO_ROOT, _REPO_ROOT.parent, _REPO_ROOT.parent.parent]:
    if (_candidate / "analysis").is_dir():
        _REPO_ROOT = _candidate
        break
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analysis._common import DB_PATH, SEED, get_conn, min_n_filter  # noqa: E402
from analysis._style import apply_style  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
apply_style()
np.random.seed(SEED)

assert DB_PATH.exists(), f"Phase 2 DB not found at {DB_PATH}; run `python -m etl.run` first"

# %% [markdown]
# ## Situation definitions
#
# Filters are copied verbatim from `docs/analysis-plan.md` "Live counts" table.
# Phase 2 verified counts (from data/nfl_defensive_tendencies.db):
# - S1 (3rd-and-long):  9,925 competitive plays
# - S2 (red zone):     15,559 competitive plays
# - S3 (1st-and-10):   41,901 competitive plays
# - S4 (2nd-and-med):  10,513 competitive plays

# %%
SITUATIONS: dict[str, str] = {
    "S1_3rd_and_long":   "down = 3 AND ydstogo >= 7",
    "S2_red_zone":       "yardline_100 <= 20",
    "S3_1st_and_10":     "down = 1 AND ydstogo = 10",
    "S4_2nd_and_medium": "down = 2 AND ydstogo BETWEEN 3 AND 6",
}

with get_conn() as conn:
    universe_n = pd.read_sql_query(
        "SELECT COUNT(*) AS n FROM competitive_plays", conn
    )["n"].iloc[0]

    situation_n = {
        sid: pd.read_sql_query(
            f"SELECT COUNT(*) AS n FROM competitive_plays WHERE {where}",
            conn,
        )["n"].iloc[0]
        for sid, where in SITUATIONS.items()
    }

print(f"Total competitive plays: {universe_n:,}")
for sid, n in situation_n.items():
    print(f"  {sid}: {n:,}")

# Sanity check against docs/analysis-plan.md "Live counts" table.
assert universe_n > 100_000, f"competitive_plays universe = {universe_n} < expected ~105k"

# %% [markdown]
# ## Per-team per-situation N profile
#
# Surface which (defteam × situation) cells are most at risk of falling below
# the N≥30 floor. Any cell that drops is a "narrative low-N flag" candidate
# per `docs/analysis-plan.md` sample-size discipline. Dropped cells are
# documented in the FINDINGS.md methodology appendix as "N/A — below N≥30 floor".

# %%
records = []
with get_conn() as conn:
    for sid, where in SITUATIONS.items():
        df = pd.read_sql_query(
            f"""
            SELECT defteam, COUNT(*) AS n
            FROM competitive_plays
            WHERE {where}
            GROUP BY defteam
            """,
            conn,
        )
        df["situation_id"] = sid
        records.append(df)

team_situation_n = pd.concat(records, ignore_index=True)
print("Per-(team, situation) N — descriptive summary:")
print(team_situation_n.groupby("situation_id")["n"].describe().round(1))

# %% [markdown]
# ## Apply min_n_filter
#
# Rows where N < 30 are dropped from downstream aggregates. The `logging.WARNING`
# from `min_n_filter` surfaces the specific (defteam, situation_id) tuples so
# Phase 3 narrative work knows which cells need the low-N flag treatment.

# %%
filtered = min_n_filter(team_situation_n, n_col="n", n_threshold=30)
print(f"Cells passing N>=30 filter: {len(filtered)} of {len(team_situation_n)}")
print(f"Cells dropped (see WARNING above): {len(team_situation_n) - len(filtered)}")

# %% [markdown]
# ## Anchor distribution snapshot — league blitz rate by situation
#
# League-aggregate blitz rate (`n_blitzers > 4` on `play_type='pass'`) per
# pre-registered situation. This is the baseline that per-team predictability
# indexes are measured against in `02_predictability_modeling.ipynb`.
#
# Cross-source join: `competitive_plays` (pbp) JOIN `ftn_play` on
# `(game_id, play_id)` — the canonical FTN↔pbp key per PITFALLS.md #3.

# %%
with get_conn() as conn:
    blitz_rate_rows = []
    for sid, where in SITUATIONS.items():
        df = pd.read_sql_query(
            f"""
            SELECT
                AVG(CASE WHEN n_blitzers > 4 THEN 1.0 ELSE 0.0 END) AS blitz_rate,
                COUNT(*) AS n
            FROM competitive_plays cp
            JOIN ftn_play f USING (game_id, play_id)
            WHERE {where} AND cp.play_type = 'pass'
            """,
            conn,
        )
        df["situation_id"] = sid
        blitz_rate_rows.append(df)

league_anchor = pd.concat(blitz_rate_rows, ignore_index=True)
print(league_anchor[["situation_id", "n", "blitz_rate"]].to_string(index=False))

# %% [markdown]
# ---
# ## Exploratory; not a headline finding
#
# Any further analysis below this divider falls outside the locked 4-situation
# slate and must be labeled "Exploratory; not a headline finding" before use in
# any narrative document. The section header is present even when empty to
# preserve the firewall convention for future additions.
