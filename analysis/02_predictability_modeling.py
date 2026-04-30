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
# # Predictability Index — methodology lock (cell 1)
#
# This is the STAT-04 / STAT-05 deliverable. Phase 3 / 03-CONTEXT D-01..D-06 lock
# the methodology before any team-level computation runs. The decisions:
#
# - **Normalization (D-01).** Headline metric is Shannon entropy normalized
#   by log(k) over fixed support k=2 (blitz vs not-blitz). KL divergence from
#   the league baseline is the secondary metric, computed in a follow-on cell
#   against the same per-team distributions.
#
# - **Validation gate (D-01).** Spearman rank correlation between the
#   H/log(k)-derived leaderboard and the KL-derived leaderboard. **Spearman
#   ρ ≥ 0.85** = the two rankings agree; KL is treated as the methodological
#   sensitivity check. **Spearman ρ < 0.85** = the divergence is a substantive
#   finding, NOT papered over.
#
# - **Input dimension (D-02).** k=2 fixed support: blitz boolean
#   `n_blitzers > 4` evaluated on `play_type='pass'` rows only. Per
#   `docs/ftn-schema-audit.md`, `n_blitzers` is NaN on run plays — the
#   pass-only filter is mandatory.
#
# - **0–100 mapping (D-04).** `pred_index = (1 - H / log(k)) * 100`. The
#   inversion is intentional: high score reads naturally as "more
#   predictable." 0 = uniform (truly random, 50/50 blitz rate); 100 =
#   deterministic (always one choice).
#
# - **Aggregation + min-N gate (D-03 + D-05).** Per-(team × situation) cells
#   with N < 30 are EXCLUDED from the team's aggregate scalar (not down-
#   weighted). The 32 × 4 matrix shows excluded cells as NaN with the
#   underlying N still reported in the methodology appendix (FINDINGS.md).
#   Per-team aggregate = sample-size-weighted mean over surviving cells.
#
# - **PA stratification (D-06).** The index uses raw blitz boolean across
#   ALL pass plays in each situation — NOT stratified by play-action. PA
#   stays as the cross-cutting modifier for the chi-square test (D-09) and
#   the FINDINGS narrative.
#
# The next code cell defines `compute_predictability_index()` and prints the
# constants this notebook uses; subsequent cells consume them.

# %%
import logging
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `analysis.*` imports resolve regardless of
# the kernel's working directory. `__file__` is not defined in .ipynb cells, so
# we use Path.cwd() which resolves to the repo root when run via nbconvert or
# JupyterLab launched from the repo root.
_REPO_ROOT = Path.cwd()
# Walk up until we find analysis/ or hit the filesystem root (defensive).
for _candidate in [_REPO_ROOT, _REPO_ROOT.parent, _REPO_ROOT.parent.parent]:
    if (_candidate / "analysis").is_dir():
        _REPO_ROOT = _candidate
        break
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import matplotlib.pyplot as plt  # noqa: E402, F401
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402, F401
import seaborn as sns  # noqa: E402, F401
from scipy import stats  # noqa: E402

from analysis._common import DB_PATH, SEED, get_conn, min_n_filter  # noqa: E402, F401
from analysis._style import apply_style  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
apply_style()
np.random.seed(SEED)

assert DB_PATH.exists(), f"Phase 2 DB not found at {DB_PATH}; run `python -m etl.run` first"

QUERIES_DIR = _REPO_ROOT / "queries"
SQL_PRED_RAW = (QUERIES_DIR / "07_situational_predictability_score.sql").read_text(encoding="utf-8")
SQL_PA_BLITZ = (QUERIES_DIR / "06_play_action_response.sql").read_text(encoding="utf-8")  # noqa: F841

# %%
# Methodology lock per .planning/phases/03-analytical-layer-sql-python/03-CONTEXT.md.
# These constants and functions are the headline contract for STAT-04/05.

K_SUPPORT: int = 2  # blitz vs not-blitz; fixed support per D-02
MIN_N_FOR_CELL: int = 30  # per-(team, situation) cell dropout floor per D-05
SPEARMAN_VALIDATION_GATE: float = 0.85  # KL-vs-H/log(k) ranking-agreement threshold per D-01

print(f"K_SUPPORT={K_SUPPORT}  MIN_N_FOR_CELL={MIN_N_FOR_CELL}  SPEARMAN_GATE={SPEARMAN_VALIDATION_GATE}")


def compute_predictability_index(blitz_count: int, no_blitz_count: int) -> float:
    """Per D-04: pred_index = (1 - H / log(k)) * 100. Returns NaN if N < min."""
    n = blitz_count + no_blitz_count
    if n < MIN_N_FOR_CELL:
        return float("nan")
    # H computed on raw counts (scipy.stats.entropy normalizes internally).
    H = stats.entropy([blitz_count, no_blitz_count], base=np.e)
    return float((1 - H / np.log(K_SUPPORT)) * 100)


def compute_kl_from_league(team_blitz_p: float, league_blitz_p: float) -> float:
    """Per D-01 secondary: KL(team || league) over the same {blitz, no-blitz} support."""
    return float(
        stats.entropy(
            [team_blitz_p, 1 - team_blitz_p],
            qk=[league_blitz_p, 1 - league_blitz_p],
            base=np.e,
        )
    )


# Smoke checks — guard the formulas before the team-level loop runs.
assert compute_predictability_index(50, 50) == 0.0, "uniform 50/50 must yield pred_index = 0"
assert compute_predictability_index(100, 0) == 100.0, "deterministic must yield pred_index = 100"
assert np.isnan(compute_predictability_index(10, 5)), "below-N cells must yield NaN"
print("methodology-lock smoke checks passed")
