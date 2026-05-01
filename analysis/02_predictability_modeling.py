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

# %% [markdown]
# ## Per-(team × season × situation) raw rollup
#
# Source: queries/07_situational_predictability_score.sql.
# Columns: defteam, season, situation_id, blitz_count, no_blitz_count, total_pass_plays.

# %%
with get_conn() as conn:
    raw = pd.read_sql_query(SQL_PRED_RAW, conn)

print(f"Raw rollup: {len(raw):,} rows, {raw['defteam'].nunique()} teams, {raw['situation_id'].nunique()} situations")
print(raw.head())

# Aggregate across seasons within (team, situation) so the matrix is 32 x 4, not 32 x 4 x 4.
team_sit = (
    raw.groupby(["defteam", "situation_id"], as_index=False)
       .agg(
           blitz_count=("blitz_count", "sum"),
           no_blitz_count=("no_blitz_count", "sum"),
           total_pass_plays=("total_pass_plays", "sum"),
       )
)
team_sit["n"] = team_sit["total_pass_plays"]
team_sit["pred_index"] = team_sit.apply(
    lambda r: compute_predictability_index(int(r["blitz_count"]), int(r["no_blitz_count"])),
    axis=1,
)
team_sit["blitz_rate"] = team_sit["blitz_count"] / team_sit["total_pass_plays"]
print(
    f"team x situation cells: {len(team_sit)}; "
    f"below N>={MIN_N_FOR_CELL}: {team_sit['pred_index'].isna().sum()}"
)

# %% [markdown]
# ## 32 × 4 matrix view (D-03 FINDINGS appendix artifact)

# %%
matrix = team_sit.pivot(index="defteam", columns="situation_id", values="pred_index")
print(f"Matrix shape: {matrix.shape}")
print(matrix.round(1).head(10))
print(f"Excluded cells (N<{MIN_N_FOR_CELL}): {matrix.isna().sum().sum()} of {matrix.size}")

# %% [markdown]
# ## Per-team aggregate scalar (D-03 hero-chart leaderboard input)

# %%
# Sample-size-weighted mean over surviving cells per D-05.
filtered = min_n_filter(team_sit, n_col="n", n_threshold=MIN_N_FOR_CELL)


def _weighted_mean(group: pd.DataFrame) -> float:
    return float(np.average(group["pred_index"], weights=group["n"]))


per_team_scalar = filtered.groupby("defteam", as_index=False).apply(
    _weighted_mean, include_groups=False
)
# pandas can name the apply result inconsistently across versions; normalize.
per_team_scalar.columns = ["defteam", "pred_index_scalar"]
per_team_scalar = per_team_scalar.sort_values("pred_index_scalar", ascending=False).reset_index(
    drop=True
)

print(f"Per-team scalar: {len(per_team_scalar)} teams")
print(per_team_scalar.head(10).to_string(index=False))
print("...")
print(per_team_scalar.tail(5).to_string(index=False))

# %% [markdown]
# ## KL-from-league secondary + Spearman validation gate (D-01)

# %%
# League blitz rate per situation (denominator for KL).
league = (
    team_sit.groupby("situation_id", as_index=False)
            .agg(
                blitz_count=("blitz_count", "sum"),
                total_pass_plays=("total_pass_plays", "sum"),
            )
)
league["league_blitz_p"] = league["blitz_count"] / league["total_pass_plays"]

t = team_sit.merge(league[["situation_id", "league_blitz_p"]], on="situation_id")
t["team_blitz_p"] = t["blitz_count"] / t["total_pass_plays"]


def _kl_row(row: pd.Series) -> float:
    if row["n"] < MIN_N_FOR_CELL:
        return float("nan")
    return compute_kl_from_league(float(row["team_blitz_p"]), float(row["league_blitz_p"]))


t["kl_div"] = t.apply(_kl_row, axis=1)

# Per-team KL scalar = sample-size-weighted mean over surviving cells.
kl_filtered = min_n_filter(t.dropna(subset=["kl_div"]).copy(), n_col="n", n_threshold=MIN_N_FOR_CELL)


def _kl_weighted(group: pd.DataFrame) -> float:
    return float(np.average(group["kl_div"], weights=group["n"]))


per_team_kl = kl_filtered.groupby("defteam", as_index=False).apply(
    _kl_weighted, include_groups=False
)
per_team_kl.columns = ["defteam", "kl_scalar"]

both = per_team_scalar.merge(per_team_kl, on="defteam")
both["rank_h"] = both["pred_index_scalar"].rank(ascending=False, method="min")
both["rank_kl"] = both["kl_scalar"].rank(ascending=False, method="min")
spearman_rho, spearman_p = stats.spearmanr(both["rank_h"], both["rank_kl"])

print(f"Spearman ρ between H/log(k) and KL leaderboards: {spearman_rho:.3f} (p={spearman_p:.4f})")
print(f"Validation gate: ρ >= {SPEARMAN_VALIDATION_GATE} ? {spearman_rho >= SPEARMAN_VALIDATION_GATE}")
if spearman_rho < SPEARMAN_VALIDATION_GATE:
    print("WARNING: Validation gate FAILED — divergence is a substantive finding to investigate.")
    print("Top 5 disagreers (largest |rank_h - rank_kl|):")
    both["rank_delta"] = (both["rank_h"] - both["rank_kl"]).abs()
    print(both.sort_values("rank_delta", ascending=False).head(5).to_string(index=False))

# %% [markdown]
# ## STAT-06 chi-square headline: PA × blitz on S1 (D-09 + D-11 + D-12)
#
# League-aggregate 2×2 contingency on S1 (3rd-and-long) pass plays from `competitive_plays`:
# rows = `n_blitzers >= 1` (y/n), cols = `is_play_action` (y/n).
# Tests the pre-registered PA cross-cutting hypothesis from `docs/analysis-plan.md`.
#
# DEVIATION (Rule 1 — bug fix): plan specified `n_blitzers > 4` (nflfastR convention for
# n_pass_rushers), but FTN's `n_blitzers` column counts dedicated extra rushers above the
# base 4-man line, not total rushers. With n_blitzers ranging 0–6, the correct blitz boolean
# is n_blitzers >= 1 (any non-lineman rushed). The plan's threshold produced only 7 blitz
# plays across 58k competitive pass plays — analytically degenerate. Corrected threshold
# aligns with FTN column semantics; blitz rate ~29% is consistent with NFL norms.

# %%
S1_PA_BLITZ_SQL = """
SELECT
    f.is_play_action,
    SUM(CASE WHEN f.n_blitzers >= 1 THEN 1 ELSE 0 END)  AS blitz_count,
    SUM(CASE WHEN f.n_blitzers = 0 THEN 1 ELSE 0 END)   AS no_blitz_count
FROM competitive_plays cp
JOIN ftn_play f USING (game_id, play_id)
WHERE cp.down = 3 AND cp.ydstogo >= 7
  AND cp.play_type = 'pass'
  AND f.is_play_action IS NOT NULL
GROUP BY f.is_play_action
"""

with get_conn() as conn:
    s1 = pd.read_sql_query(S1_PA_BLITZ_SQL, conn)

print(s1)

# Build the 2x2 contingency in the order required by D-09:
#   [[blitz=1 & PA=1, blitz=0 & PA=1],
#    [blitz=1 & PA=0, blitz=0 & PA=0]]
row_pa = s1.loc[s1["is_play_action"] == 1].iloc[0]
row_no = s1.loc[s1["is_play_action"] == 0].iloc[0]
a = int(row_pa["blitz_count"])
b = int(row_pa["no_blitz_count"])
c = int(row_no["blitz_count"])
d = int(row_no["no_blitz_count"])
table = np.array([[a, b], [c, d]])
print(f"S1 PA x blitz contingency:\n{table}")
print(
    f"N total: {table.sum()} "
    f"(gate: chi-square requires expected cell count >= 5; with N ~ 10k this is comfortably met)"
)

chi2, p, _, expected = stats.chi2_contingency(table)
print(f"chi2 = {chi2:.4f}")
print(f"p-value = {p:.6f}")
print(f"expected cells (min={expected.min():.1f}): chi-square assumption holds")

# Odds ratio + 95% CI per D-11.
odds_ratio = (a * d) / (b * c)
log_or = np.log(odds_ratio)
se_log_or = np.sqrt(1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d)
or_lo = float(np.exp(log_or - 1.96 * se_log_or))
or_hi = float(np.exp(log_or + 1.96 * se_log_or))
print(f"OR={odds_ratio:.3f}  95% CI=[{or_lo:.3f}, {or_hi:.3f}]")

# Wilson 95% CI on P(blitz | is_play_action=1) per D-12 (closed-form, no statsmodels).
p_hat = a / (a + b)
n_pa = a + b
z = 1.96
z2 = z * z
denom = 1.0 + z2 / n_pa
centre = (p_hat + z2 / (2 * n_pa)) / denom
half = (z * np.sqrt(p_hat * (1 - p_hat) / n_pa + z2 / (4 * n_pa * n_pa))) / denom
wilson_lo, wilson_hi = float(centre - half), float(centre + half)
print(f"P(blitz | PA=1, S1) = {p_hat:.4f}  Wilson CI=[{wilson_lo:.4f}, {wilson_hi:.4f}]  (N={n_pa})")
# Paired number per D-12: P(blitz | PA=0, S1).
p_no = c / (c + d)
print(f"Paired: P(blitz | PA=0, S1) = {p_no:.4f}  (N={c + d})")
print(
    f"Pre-registered prediction (analysis-plan.md): |gap| >= 5pp; "
    f"observed gap = {(p_hat - p_no) * 100:+.2f}pp"
)

# %% [markdown]
# ## EXPLORATORY: PA x blitz on S3 (1st-and-10) - NOT pre-registered in docs/analysis-plan.md
#
# Per Phase 4 / 04-CONTEXT D-10..D-15. The S1 chi-square (above) is the
# pre-registered headline; this cell is the exploratory follow-up that tests
# the same mechanism on the situation where PA actually fires (PA rate on S3
# = 46.49% vs 1.235% on S1). The S3 universe gives the chi-square inferential
# power the S1 N=109 stratum cannot.
#
# Universe: competitive_plays JOIN ftn_play, down=1 AND ydstogo=10 AND play_type='pass'.
# Verified counts (2026-04-30): N total = 18,609; N(PA=1) = 8,652; N(PA=0) = 9,957.
#
# Reporting structure mirrors S1 (chi^2 + p, expected min cell, OR + 95% CI,
# Wilson CI on P(blitz | PA=1, S3), paired P(blitz | PA=0, S3), observed pp gap)
# PLUS first-class OR delta vs S1 per D-11.

# %%
S3_PA_BLITZ_SQL = """
SELECT
    f.is_play_action,
    SUM(CASE WHEN f.n_blitzers >= 1 THEN 1 ELSE 0 END)  AS blitz_count,
    SUM(CASE WHEN f.n_blitzers = 0 THEN 1 ELSE 0 END)   AS no_blitz_count
FROM competitive_plays cp
JOIN ftn_play f USING (game_id, play_id)
WHERE cp.down = 1 AND cp.ydstogo = 10
  AND cp.play_type = 'pass'
  AND f.is_play_action IS NOT NULL
GROUP BY f.is_play_action
"""

with get_conn() as conn:
    s3 = pd.read_sql_query(S3_PA_BLITZ_SQL, conn)

print(s3)

# Build the 2x2 contingency in the order required by D-09 (mirror S1):
#   [[blitz=1 & PA=1, blitz=0 & PA=1],
#    [blitz=1 & PA=0, blitz=0 & PA=0]]
row_pa = s3.loc[s3["is_play_action"] == 1].iloc[0]
row_no = s3.loc[s3["is_play_action"] == 0].iloc[0]
a3 = int(row_pa["blitz_count"])
b3 = int(row_pa["no_blitz_count"])
c3 = int(row_no["blitz_count"])
d3 = int(row_no["no_blitz_count"])
table_s3 = np.array([[a3, b3], [c3, d3]])
print(f"S3 PA x blitz contingency:\n{table_s3}")

chi2_s3, p_s3, _, expected_s3 = stats.chi2_contingency(table_s3)
print(f"chi2 = {chi2_s3:.4f}")
print(f"p-value = {p_s3:.6f}")
print(f"expected cells (min={expected_s3.min():.1f}): chi-square assumption holds")

odds_ratio_s3 = (a3 * d3) / (b3 * c3)
log_or_s3 = np.log(odds_ratio_s3)
se_log_or_s3 = np.sqrt(1.0 / a3 + 1.0 / b3 + 1.0 / c3 + 1.0 / d3)
or_lo_s3 = float(np.exp(log_or_s3 - 1.96 * se_log_or_s3))
or_hi_s3 = float(np.exp(log_or_s3 + 1.96 * se_log_or_s3))
print(f"OR={odds_ratio_s3:.3f}  95% CI=[{or_lo_s3:.3f}, {or_hi_s3:.3f}]")

# Wilson CI on P(blitz | PA=1, S3); reuse the closed-form pattern from S1.
p_hat_s3 = a3 / (a3 + b3)
n_pa_s3 = a3 + b3
z = 1.96
z2 = z * z
denom = 1.0 + z2 / n_pa_s3
centre = (p_hat_s3 + z2 / (2 * n_pa_s3)) / denom
half = (z * np.sqrt(p_hat_s3 * (1 - p_hat_s3) / n_pa_s3 + z2 / (4 * n_pa_s3 * n_pa_s3))) / denom
wilson_lo_s3, wilson_hi_s3 = float(centre - half), float(centre + half)
print(
    f"P(blitz | PA=1, S3) = {p_hat_s3:.4f}  "
    f"Wilson CI=[{wilson_lo_s3:.4f}, {wilson_hi_s3:.4f}]  (N={n_pa_s3})"
)
p_no_s3 = c3 / (c3 + d3)
print(f"Paired: P(blitz | PA=0, S3) = {p_no_s3:.4f}  (N={c3 + d3})")
print(f"Observed pp gap (S3) = {(p_hat_s3 - p_no_s3) * 100:+.2f}pp")

# Per 04-CONTEXT D-11: report OR delta between S1 and S3 as a first-class output.
# The S1 OR is in scope as `odds_ratio` from the S1 cell above; this cell MUST
# run after the S1 cell so the variable is in the kernel namespace.
or_delta = odds_ratio_s3 - odds_ratio
print(f"OR delta (S3 - S1) = {or_delta:+.3f}  (S1 OR={odds_ratio:.3f}, S3 OR={odds_ratio_s3:.3f})")
direction_match = (
    "yes"
    if (odds_ratio < 1 and odds_ratio_s3 < 1) or (odds_ratio > 1 and odds_ratio_s3 > 1)
    else "no"
)
print(f"Direction agreement (both OR < 1 or both OR > 1): {direction_match}")

# %% [markdown]
# ## STAT-08 sensitivity: Predictability Index leaderboard with vs without `competitive_plays` (D-13)
#
# Recompute the per-team predictability scalar on two universes:
# 1. `competitive_plays` (locked headline; ~57k pass plays after wp/qtr filter)
# 2. `plays WHERE play_type='pass'` (unfiltered; ~80k pass plays, bypasses the view)
#
# Report rank delta and Spearman correlation between the two leaderboards.

# %%
# Unfiltered universe: bypass the competitive_plays view; query plays directly.
SQL_PRED_UNFILTERED = """
WITH situations AS (
    SELECT p.defteam, p.season, p.game_id, p.play_id, p.play_type,
           CASE
               WHEN p.down = 3 AND p.ydstogo >= 7              THEN 'S1_3rd_and_long'
               WHEN p.yardline_100 <= 20                       THEN 'S2_red_zone'
               WHEN p.down = 1 AND p.ydstogo = 10              THEN 'S3_1st_and_10'
               WHEN p.down = 2 AND p.ydstogo BETWEEN 3 AND 6   THEN 'S4_2nd_and_medium'
               ELSE NULL
           END AS situation_id
    FROM plays p
)
SELECT
    s.defteam, s.season, s.situation_id,
    SUM(CASE WHEN f.n_blitzers >= 1 THEN 1 ELSE 0 END)   AS blitz_count,
    SUM(CASE WHEN f.n_blitzers = 0 THEN 1 ELSE 0 END)   AS no_blitz_count,
    COUNT(*)                                             AS total_pass_plays
FROM situations s
JOIN ftn_play f USING (game_id, play_id)
WHERE s.situation_id IS NOT NULL AND s.play_type = 'pass'
GROUP BY s.defteam, s.season, s.situation_id
"""

with get_conn() as conn:
    raw_unf = pd.read_sql_query(SQL_PRED_UNFILTERED, conn)

print(
    f"Unfiltered (play_type='pass' bypassing competitive_plays): "
    f"{raw_unf['total_pass_plays'].sum():,} pass plays"
)

# %%


def _per_team_scalar(rollup: pd.DataFrame) -> pd.DataFrame:
    agg = (
        rollup.groupby(["defteam", "situation_id"], as_index=False)
              .agg(
                  blitz_count=("blitz_count", "sum"),
                  no_blitz_count=("no_blitz_count", "sum"),
                  total_pass_plays=("total_pass_plays", "sum"),
              )
    )
    agg["n"] = agg["total_pass_plays"]
    agg["pred_index"] = agg.apply(
        lambda r: compute_predictability_index(int(r["blitz_count"]), int(r["no_blitz_count"])),
        axis=1,
    )
    surviving = min_n_filter(agg, n_col="n", n_threshold=MIN_N_FOR_CELL)
    out = surviving.groupby("defteam", as_index=False).apply(
        lambda g: float(np.average(g["pred_index"], weights=g["n"])),
        include_groups=False,
    )
    out.columns = ["defteam", "pred_index_scalar"]
    return out.sort_values("pred_index_scalar", ascending=False).reset_index(drop=True)


with_filter = _per_team_scalar(raw)        # competitive_plays universe (from Task 2)
without_filter = _per_team_scalar(raw_unf)  # plays universe (this task)

with_filter["rank_with"] = with_filter["pred_index_scalar"].rank(ascending=False, method="min")
without_filter["rank_without"] = without_filter["pred_index_scalar"].rank(
    ascending=False, method="min"
)

merged = with_filter.merge(without_filter, on="defteam", suffixes=("_with", "_without"))
merged["rank_delta"] = (merged["rank_with"] - merged["rank_without"]).astype(int)

rho_lb, rho_lb_p = stats.spearmanr(merged["rank_with"], merged["rank_without"])
print(f"STAT-08 sensitivity: Spearman ρ between leaderboards = {rho_lb:.3f} (p={rho_lb_p:.4f})")
print(f"Largest |rank_delta|: {merged['rank_delta'].abs().max()}")
print("Top-5 by with-filter ranking:")
print(merged.head(5)[["defteam", "rank_with", "rank_without", "rank_delta"]].to_string(index=False))
print("Top-5 by without-filter ranking:")
print(
    merged.sort_values("rank_without")
          .head(5)[["defteam", "rank_with", "rank_without", "rank_delta"]]
          .to_string(index=False)
)

# %% [markdown]
# ## Limitations + sample-size discipline summary

# %%
print("Phase 3 / 02_predictability_modeling.ipynb — methodology lock satisfied.")
print(
    f"  Universe: competitive_plays JOIN ftn_play, play_type='pass' "
    f"({raw['total_pass_plays'].sum():,} pass plays)"
)
print(
    f"  Per-(team, situation) cells: {len(team_sit)}; "
    f"below N>={MIN_N_FOR_CELL}: {team_sit['pred_index'].isna().sum()}"
)
print(
    f"  Spearman validation gate (H vs KL): ρ = {spearman_rho:.3f}  "
    f"(gate: >= {SPEARMAN_VALIDATION_GATE})"
)
print(
    f"  STAT-06 chi-square (S1 PA x blitz): chi2={chi2:.3f}, p={p:.4f}, "
    f"OR={odds_ratio:.3f} [{or_lo:.3f}, {or_hi:.3f}]"
)
print(f"  Wilson CI on P(blitz | PA=1, S1): [{wilson_lo:.4f}, {wilson_hi:.4f}]")
print(f"  STAT-08 sensitivity: Spearman ρ between leaderboards = {rho_lb:.3f}")
print(
    f"S3 (exploratory): PA x blitz on 1st-and-10  N={a3 + b3 + c3 + d3}  "
    f"chi2={chi2_s3:.3f}  p={p_s3:.3f}  OR={odds_ratio_s3:.3f}  "
    f"OR delta vs S1={or_delta:+.3f}"
)
