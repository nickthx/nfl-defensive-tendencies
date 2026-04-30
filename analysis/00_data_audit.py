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
# # FTN Pivot Calibration Audit
#
# This notebook is the Phase 1 deliverable that closes the eight Phase-1 open
# questions in `.planning/research/SUMMARY.md`. It pulls the 28-column FTN
# charting subset distributed via nflverse for 2022-2024, joins it to nflfastR
# play-by-play on the canonical play key, measures per-column NaN rates by
# `play_type`, and applies the D-02 30%-NaN cutoff to the eight candidate
# defensive dimensions named in `.planning/phases/01-foundation-ftn-pivot-calibration/01-CONTEXT.md`.
#
# The narrative interpretation lives in `docs/ftn-schema-audit.md`. The
# persistent artifact this notebook writes is `audit/ftn_null_profile.csv`
# (Pitfall #4 evidence; AUDIT-02 deliverable).
#
# Outputs are cleared before commit per `CLAUDE.md` File-Organization Rules.

# %%
import nfl_data_py as nfl
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

SEASONS = [2022, 2023, 2024]
AUDIT_DIR = Path("../audit")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# %% [markdown]
# ## Cell 2 - Pull FTN charting data
#
# Per Pitfall #17, a row-count assertion catches silent CDN failures
# (a zero-row pull with no error code is the failure mode this assert
# guards against).

# %%
ftn = nfl.import_ftn_data(SEASONS)
print(f"FTN frame: {len(ftn):,} rows x {len(ftn.columns)} columns")
print("Columns:", ftn.columns.tolist())
assert len(ftn) > 100_000, f"FTN pull returned {len(ftn)} rows; expected >100k for 3 seasons"

# %% [markdown]
# ## Cell 3 - Pull pbp subset (for play_type lookup)
#
# We only need `game_id`, `play_id`, `play_type`, and `season` for the
# join. Pulling the full pbp frame would be wasteful for an audit pass.

# %%
pbp = nfl.import_pbp_data(SEASONS, columns=['game_id', 'play_id', 'play_type', 'season'])
print(f"pbp frame: {len(pbp):,} rows")

# %% [markdown]
# ## Cell 4 - Join FTN to pbp on the canonical play key
#
# Per Pitfall #3: FTN exposes `nflverse_game_id` / `nflverse_play_id` as the
# join key (NOT `ftn_game_id` / `ftn_play_id`, NOT bare `game_id` / `play_id`).
# `validate='one_to_one'` raises if the join is wrong; the post-join match
# rate must exceed 0.95. This same pattern propagates to Phase 2 ETL-04.

# %%
joined = ftn.merge(
    pbp,
    left_on=['nflverse_game_id', 'nflverse_play_id'],
    right_on=['game_id', 'play_id'],
    how='left',
    validate='one_to_one',
)
match_rate = joined['play_type'].notna().mean()
print(f"FTN <-> pbp match rate: {match_rate:.4f}")
assert match_rate > 0.95, f"Match rate {match_rate:.3f} below 0.95 threshold"

# %% [markdown]
# ## Cell 5 - Per-column NaN rate by play_type
#
# This is the AUDIT-02 deliverable. The CSV survives output-clearing
# because it is a side-effect file written by `to_csv`, not a notebook cell
# output. Per Pitfall #4, `n_blitzers` and `n_pass_rushers` are populated
# only on pass-context plays - a ~100% NaN rate on `play_type='run'` for
# these columns is expected, not a data quality issue.

# %%
null_profile = (
    joined.groupby('play_type', dropna=False)
    .apply(lambda g: g.isna().mean())
    .T
    .round(3)
)
null_profile.to_csv(AUDIT_DIR / "ftn_null_profile.csv")
print(null_profile)

# %% [markdown]
# ## Cell 6 - Visualize NaN rate
#
# Heatmap is for in-notebook display only (no `savefig` in Phase 1; the
# `findings/images/` figures land in Phase 4 / VIZ-01 with `_style.py`
# rcParams).

# %%
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(null_profile, annot=True, cmap='Reds', vmin=0, vmax=1, ax=ax,
            cbar_kws={'label': 'NaN rate'})
ax.set_title("FTN per-column NaN rate by play_type, 2022-2024")
fig.tight_layout()
plt.show()

# %% [markdown]
# ## Cell 7 - Apply the D-02 30% NaN cutoff
#
# Per `.planning/phases/01-foundation-ftn-pivot-calibration/01-CONTEXT.md`:
#
# - **D-01:** Selection rule = NaN-cutoff + story tiebreaker. Drop any FTN
#   column with >30% NaN on the relevant `play_type`. Among survivors, curate
#   for cross-category diversity.
# - **D-02:** NaN-rate ceiling = 30% on the relevant `play_type`.
# - **D-03:** Anchor count target = aim for 4, accept 3 if NaN cuts one.
# - **D-04:** Empty-category contingency: document the gap, fill 4th from
#   surplus.
#
# Pressure / play-fakery columns are evaluated on `play_type='pass'` rows
# only (Pitfall #4). Personnel / location columns are evaluated on
# competitive plays (`play_type IN ('pass','run')`).

# %%
candidate_cols = {
    'pressure': ['n_blitzers', 'n_pass_rushers'],
    'play_fakery': ['is_play_action', 'is_screen_pass', 'is_rpo'],
    'personnel_location': ['qb_location', 'n_offense_backfield', 'starting_hash'],
}

pass_nan = (
    joined[joined['play_type'] == 'pass']
    .isna()
    .mean()
    .round(3)
)
competitive_nan = (
    joined[joined['play_type'].isin(['pass', 'run'])]
    .isna()
    .mean()
    .round(3)
)

print("Survivors of D-02 30% cutoff (per category):")
for category, cols in candidate_cols.items():
    for col in cols:
        if category in ('pressure', 'play_fakery'):
            rate = pass_nan.get(col, np.nan)
            scope = "play_type='pass'"
        else:
            rate = competitive_nan.get(col, np.nan)
            scope = "competitive plays"
        survives = rate <= 0.30
        verdict = 'SURVIVES' if survives else 'DROPPED (>30%)'
        print(f"  [{category}] {col} ({scope}): {rate:.3f} {verdict}")
