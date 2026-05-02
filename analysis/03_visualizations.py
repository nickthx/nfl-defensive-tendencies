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
# # Visualizations - VIZ-01..05 (Phase 4)
#
# Exports three PNGs to `findings/images/` using `_style.py` rcParams:
# - `01_predictability_ranking.png` - hero leaderboard (32 teams, portrait 8x11,
#   fixed 0-100 x-axis, top-3 + bottom-3 highlighted, league-avg dashed line). VIZ-02.
# - `02_kl_vs_h_scatter.png` - rank-rank scatter (D-15 divergence; 8 callouts
#   via adjustText; inverted axes per D-22). VIZ-03.
# - `01_predictability_ranking_top12.png` - 1280x640 landscape, top-12 only,
#   social-preview source for SHIP-04. Same parameterized leaderboard function
#   as the hero, just `top_n=12`. D-34.
#
# Outputs are cleared via `nbconvert --clear-output --inplace` before commit
# per CLAUDE.md File-Organization Rules. Hero PNGs live only in `findings/images/`,
# never inside committed notebook outputs.

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

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402, F401
from adjustText import adjust_text  # noqa: E402
from scipy import stats  # noqa: E402, F401

from analysis._common import DB_PATH, SEED, get_conn, min_n_filter  # noqa: E402, F401
from analysis._style import apply_style  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
apply_style()
np.random.seed(SEED)

assert DB_PATH.exists(), f"Phase 2 DB not found at {DB_PATH}; run `python -m etl.run` first"

QUERIES_DIR = _REPO_ROOT / "queries"
IMAGES_DIR = _REPO_ROOT / "findings" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Predictability leaderboard - hero data prep (D-27..D-33)
#
# Reads QUERY-07 raw inputs (per-team-per-situation blitz_count + no_blitz_count +
# total_pass_plays), aggregates across seasons to a (team, situation) cell,
# applies the N >= 30 cell-level dropout per Phase 3 D-05, computes
# H/log(2) entropy per cell, and aggregates to a per-team scalar via
# sample-size-weighted mean of `(1 - H/log(2)) * 100`.
#
# DEVIATION (Rule 1 - bug fix): plan scaffold assumed QUERY-07 exposes `entropy`
# and `n` columns directly. Actual QUERY-07 returns blitz_count, no_blitz_count,
# total_pass_plays (one row per defteam x season x situation). Entropy is computed
# here in the notebook, consistent with the pattern in 02_predictability_modeling.py
# (compute_predictability_index inlines the same formula). No query changes needed.

# %%
SQL_PRED_RAW = (QUERIES_DIR / "07_situational_predictability_score.sql").read_text(encoding="utf-8")

with get_conn() as conn:
    raw = pd.read_sql_query(SQL_PRED_RAW, conn)

# Aggregate across seasons within (team, situation) so the cell matrix is 32 x 4,
# not 32 x 4 x 4 — mirrors 02_predictability_modeling.py lines 145-153.
K_SUPPORT = 2  # blitz/no-blitz binary
team_sit = raw.groupby(["defteam", "situation_id"], as_index=False).agg(
    blitz_count=("blitz_count", "sum"),
    no_blitz_count=("no_blitz_count", "sum"),
    total_pass_plays=("total_pass_plays", "sum"),
)
team_sit["n"] = team_sit["total_pass_plays"]

# Compute Shannon entropy H (natural log base) and normalize: (1 - H/log(2)) * 100.
# Cells with N < 30 yield NaN (min_n_filter drops them below).
from scipy.stats import entropy as _scipy_entropy  # noqa: E402


def _pred_score(blitz: int, no_blitz: int) -> float:
    n = blitz + no_blitz
    if n < 30:  # noqa: PLR2004
        return float("nan")
    h = _scipy_entropy([blitz, no_blitz], base=None)  # natural log
    return float((1.0 - h / np.log(K_SUPPORT)) * 100.0)


team_sit["pred_score"] = team_sit.apply(
    lambda r: _pred_score(int(r["blitz_count"]), int(r["no_blitz_count"])), axis=1
)

# min_n_filter drops cells with N < 30 (Phase 3 D-05 floor).
filtered = min_n_filter(team_sit, n_col="n", n_threshold=30)

# Per-team aggregate scalar: N-weighted mean of pred_score over surviving cells.
leaderboard = (
    filtered.groupby("defteam")
    .apply(lambda g: np.average(g["pred_score"], weights=g["n"]), include_groups=False)
    .reset_index(name="pred_score")
    .sort_values("pred_score", ascending=False)
    .reset_index(drop=True)
)
league_avg = float(leaderboard["pred_score"].mean())
print(leaderboard.head(5).to_string(index=False))
print(leaderboard.tail(5).to_string(index=False))
print(f"League average predictability index: {league_avg:.2f}")

# %% [markdown]
# ## Parameterized leaderboard renderer (D-27..D-34)
#
# Same code path renders the 32-team portrait hero (VIZ-02) and the
# top-12 landscape social preview (SHIP-04 source). Color encoding:
# top-3 in palette index 0 (blue), bottom-3 in palette index 1 (orange,
# deliberately non-red per D-28), middle 26 in palette index 7 (gray).
# League-average vertical dashed line; 1-decimal annotations on top-3 + bottom-3 only.


# %%
def render_leaderboard(
    df: pd.DataFrame,
    top_n: int,
    figsize: tuple[float, float],
    savepath: Path,
    title: str,
    subtitle: str,
    exact_pixels: tuple[int, int] | None = None,
) -> None:
    # exact_pixels=(w, h): when set, overrides bbox="tight" so savefig hits the
    # precise pixel count (e.g., 1280x640 for the social preview). The figsize
    # already encodes the target at 200 DPI; tight-layout is skipped in this mode
    # to avoid the tight-bbox trim that shifts pixel counts.
    palette = sns.color_palette("colorblind")
    top_color = palette[0]  # blue   #0173b2
    bottom_color = palette[1]  # orange #de8f05  (NON-RED per D-28)
    neutral = palette[7]  # gray   #949494

    view = df.head(top_n).copy()
    n = len(view)
    # Color array: top-3 blue, bottom-3 orange, rest gray.
    # For the top_n=12 social preview, "bottom-3" of the displayed slice still
    # gets the bottom highlight per D-34 (parameterized leaderboard renders
    # whatever slice is passed; the social preview shows top-12 only and uses
    # the same color logic on its 12-row view).
    colors = [neutral] * n
    for i in range(min(3, n)):
        colors[i] = top_color
    for i in range(max(0, n - 3), n):
        if colors[i] is neutral:
            colors[i] = bottom_color

    fig, ax = plt.subplots(figsize=figsize)
    # Bars sorted descending by score; reverse for plotting so highest is at top.
    y_positions = np.arange(n)[::-1]
    ax.barh(y_positions, view["pred_score"].values, color=colors, edgecolor="none")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(view["defteam"].values, fontsize=9)
    ax.set_xlim(0, 100)  # FIXED 0-100 per D-30
    ax.set_xlabel("Predictability index (0-100; higher = more predictable)")
    # Headline (large) — pad in points keeps spacing stable across both figsizes
    ax.set_title(title, fontsize=14, loc="left", pad=22)
    # Subhead (small, gray) sits just above the axes top, below the headline
    ax.text(
        0.0,
        1.0,
        subtitle,
        transform=ax.transAxes,
        fontsize=10,
        color="#444444",
        va="bottom",
        ha="left",
    )

    # League-average dashed vertical line + label.
    # Reserve a 1-unit headroom band above the top bar so the label sits in
    # clear space adjacent to the line (was overlapping the PHI bar pre-fix).
    ax.set_ylim(-0.6, n + 0.5)
    ax.axvline(league_avg, linestyle="--", color="#666666", linewidth=1.0)
    ax.text(
        league_avg + 1.5,
        n,
        f"League avg = {league_avg:.1f}",
        fontsize=9,
        color="#444444",
        va="center",
    )

    # 1-decimal annotations on top-3 + bottom-3 only per D-31.
    annotate_indices = list(range(min(3, n))) + list(range(max(0, n - 3), n))
    annotate_indices = sorted(set(annotate_indices))
    for i in annotate_indices:
        score = view["pred_score"].iloc[i]
        ax.text(
            score + 1.0,
            y_positions[i],
            f"{score:.1f}",
            fontsize=9,
            va="center",
        )

    if exact_pixels is not None:
        # For exact pixel dimensions: override the global savefig.bbox rcParam which
        # _style.py sets to "tight". Setting savefig.bbox=None in an rc_context
        # prevents the tight-crop trim so figsize*dpi gives the exact pixel count.
        # figsize=(6.4, 3.2) @ dpi=200 → exactly 1280x640 (verified empirically).
        import matplotlib as mpl  # noqa: PLC0415

        with mpl.rc_context({"savefig.bbox": None}):
            fig.savefig(savepath)
    else:
        fig.tight_layout()
        fig.savefig(savepath)
    plt.close(fig)
    print(f"Wrote {savepath} ({savepath.stat().st_size // 1024} KB)")


# %%
HERO_TITLE = "Some NFL Defenses Are More Predictable Than Others"
HERO_SUBTITLE = (
    "32 NFL defenses, blitz rate on 4 pre-registered situations, 2022-2025; "
    "0-100 predictability index, higher = more predictable."
)
render_leaderboard(
    leaderboard,
    top_n=32,
    figsize=(8, 11),
    savepath=IMAGES_DIR / "01_predictability_ranking.png",
    title=HERO_TITLE,
    subtitle=HERO_SUBTITLE,
)

# %%
SOCIAL_TITLE = "Some NFL Defenses Are More Predictable Than Others (Top 12)"
SOCIAL_SUBTITLE = "Most Predictable Defenses 2022-2025."
render_leaderboard(
    leaderboard,
    top_n=12,
    figsize=(6.4, 3.2),
    savepath=IMAGES_DIR / "01_predictability_ranking_top12.png",
    title=SOCIAL_TITLE,
    subtitle=SOCIAL_SUBTITLE,
    exact_pixels=(1280, 640),
)

# %% [markdown]
# ## VIZ-03: KL-vs-H rank-rank scatter (D-15 divergence made visible)
#
# Per 04-CONTEXT D-21..D-26. VIZ-03 is satisfied via this rank-rank scatter
# (non-bar-chart, adds analytical depth on top of the leaderboard) rather
# than a heatmap or small-multiples grid. Both axes are inverted so rank 1
# sits at top-left, matching rankings convention (D-22). The y=x diagonal
# is the "perfect agreement" reference (rho = 1.0). Eight teams are called
# out: top-5 disagreers (MIN, TB, PIT, MIA, DET) plus three FINDINGS
# leaderboard anchors (PHI, SF, IND); MIN and TB are double-duty.

# %%
# Reuse the leaderboard prepared above for H/log(2) ranks; recompute KL ranks.
# KL universe: per-team blitz rate from competitive_plays JOIN ftn_play, against
# the league baseline. Read QUERY-01 raw inputs to get per-team rates.
SQL_TEAM_BLITZ = (QUERIES_DIR / "01_tendency_distribution_by_team.sql").read_text(encoding="utf-8")
with get_conn() as conn:
    team_blitz = pd.read_sql_query(SQL_TEAM_BLITZ, conn)
# team_blitz has columns: defteam, blitz_rate (or equivalent league-baseline
# comparison). Verify the shape at execution time; QUERY-01 is the per-team
# league-baseline tendency query.
print(team_blitz.head(5).to_string(index=False))

# KL divergence from the league baseline for each team's blitz/no-blitz dist.
# If team_blitz already exposes a kl column, use it; otherwise compute
# closed-form from blitz_rate against league mean.
league_blitz_rate = float(team_blitz["blitz_rate"].mean())  # ~0.2945


def kl_binary(p: float, q: float) -> float:
    # KL(p || q) for a Bernoulli with rate p against baseline rate q.
    # Add a tiny epsilon to guard log(0) on degenerate teams.
    eps = 1e-12
    p, q = max(min(p, 1 - eps), eps), max(min(q, 1 - eps), eps)
    return p * np.log(p / q) + (1 - p) * np.log((1 - p) / (1 - q))


team_blitz["kl"] = team_blitz["blitz_rate"].apply(lambda p: kl_binary(p, league_blitz_rate))

# Build rank columns: rank 1 = most predictable on H, most extreme on KL.
h_ranks = leaderboard.copy()
h_ranks["rank_H"] = h_ranks["pred_score"].rank(ascending=False, method="min").astype(int)
h_ranks = h_ranks[["defteam", "rank_H"]]

kl_ranks = team_blitz[["defteam", "kl"]].copy()
kl_ranks["rank_KL"] = kl_ranks["kl"].rank(ascending=False, method="min").astype(int)
kl_ranks = kl_ranks[["defteam", "rank_KL"]]

ranks = h_ranks.merge(kl_ranks, on="defteam", how="inner", validate="one_to_one")
print(f"Teams in rank-rank join: {len(ranks)} (expect 32)")
rho, p_rho = stats.spearmanr(ranks["rank_H"], ranks["rank_KL"])
print(f"Spearman rho = {rho:.3f}  (p = {p_rho:.3f})")

# %%
# Render the scatter. Inverted axes per D-22 (rank 1 top-left).
fig, ax = plt.subplots(figsize=(8, 8))

palette = sns.color_palette("colorblind")
point_color = palette[0]
diag_color = "#888888"

ax.scatter(
    ranks["rank_H"],
    ranks["rank_KL"],
    s=42,
    color=point_color,
    edgecolor="white",
    linewidth=0.6,
    zorder=3,
)
# Inverted axes: rank 1 at top-left of both axes per D-22.
ax.set_xlim(33, 0)
ax.set_ylim(33, 0)
ax.set_xlabel("Rank by H/log(2) concentration  (1 = most predictable)")
ax.set_ylabel("Rank by KL-from-league-baseline  (1 = most extreme deviation)")

# y=x diagonal labeled per D-23.
ax.plot([0, 33], [0, 33], linestyle="--", color=diag_color, linewidth=1.0, zorder=1)
ax.text(
    32,
    32,
    "perfect agreement (rho = 1.0)",
    fontsize=9,
    color="#555555",
    ha="left",
    va="bottom",
    rotation=45,
)

ax.set_title("Two Definitions of Predictable Disagree", fontsize=13, loc="left")
ax.text(
    0.0,
    1.02,
    "Spearman rho = -0.111 between H/log(2) and KL-from-league-baseline rankings; "
    "32 NFL defenses, 2022-2025.",
    transform=ax.transAxes,
    fontsize=10,
    color="#444444",
    va="bottom",
)

# 8 callouts per D-24: top-5 disagreers + 3 leaderboard anchors.
callout_teams = ["MIN", "TB", "PIT", "MIA", "DET", "PHI", "SF", "IND"]
text_objs = []
for team in callout_teams:
    row = ranks.loc[ranks["defteam"] == team]
    if row.empty:
        print(f"WARNING: callout team {team} not in ranks; skipping label")
        continue
    x = float(row["rank_H"].iloc[0])
    y = float(row["rank_KL"].iloc[0])
    text_objs.append(ax.text(x, y, team, fontsize=10, fontweight="bold"))

# adjust_text places labels with collision avoidance per D-24.
adjust_text(
    text_objs,
    ax=ax,
    arrowprops=dict(arrowstyle="-", color="#666666", lw=0.6),
    only_move={"text": "xy"},
)

fig.tight_layout()
scatter_path = IMAGES_DIR / "02_kl_vs_h_scatter.png"
# Use bbox=None so the 8x8 figsize @ 200 DPI produces a square 1600x1600 output.
# The tight-crop trim from _style.py's savefig.bbox='tight' shaves X and Y
# asymmetrically when adjust_text shifts labels, making the output non-square.
import matplotlib as _mpl  # noqa: E402, PLC0415

with _mpl.rc_context({"savefig.bbox": None}):
    fig.savefig(scatter_path)
plt.close(fig)
print(f"Wrote {scatter_path} ({scatter_path.stat().st_size // 1024} KB)")
