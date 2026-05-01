---
phase: 04-story-and-ship
plan: 01
subsystem: visualization
tags: [matplotlib, seaborn, adjustText, jupytext, scipy, chi-square, png, leaderboard]

# Dependency graph
requires:
  - phase: 03-analytical-layer-sql-python
    provides: "queries/07_situational_predictability_score.sql, queries/01_tendency_distribution_by_team.sql, analysis/02_predictability_modeling.py, data/nfl_defensive_tendencies.db"
provides:
  - "findings/images/01_predictability_ranking.png (hero leaderboard, portrait 1845x2178)"
  - "findings/images/01_predictability_ranking_top12.png (social preview, exactly 1280x640)"
  - "findings/images/02_kl_vs_h_scatter.png (rank-rank scatter, square 1600x1600)"
  - "analysis/03_visualizations.py + .ipynb (VIZ-01..05 pipeline, cleared outputs)"
  - "analysis/02_predictability_modeling.py S3 exploratory chi-square cells appended"
  - "requirements.txt with adjustText>=1.0,<2 pin"
affects: [04-02-PLAN, 04-03-PLAN]

# Tech tracking
tech-stack:
  added: ["adjustText==1.3.0 (8-callout label placement)"]
  patterns:
    - "rc_context(savefig.bbox=None) to bypass tight-crop for exact pixel output"
    - "exact_pixels param on render_leaderboard() for social preview vs hero"
    - "S3 exploratory chi-square mirroring S1 cell structure with OR-delta first-class output"

key-files:
  created:
    - "analysis/03_visualizations.py"
    - "analysis/03_visualizations.ipynb"
    - "findings/images/01_predictability_ranking.png"
    - "findings/images/01_predictability_ranking_top12.png"
    - "findings/images/02_kl_vs_h_scatter.png"
  modified:
    - "requirements.txt (adjustText pin added)"
    - "analysis/02_predictability_modeling.py (S3 cells + Limitations summary line)"
    - "analysis/02_predictability_modeling.ipynb (cleared outputs)"

key-decisions:
  - "rc_context(savefig.bbox=None) chosen to hit exact 1280x640 pixel count for social preview — tight-crop trimmed asymmetrically, shifting pixel counts off target"
  - "Same rc_context pattern applied to scatter PNG to keep 8x8 figsize exactly square (1600x1600)"
  - "include_groups=False added to groupby apply in leaderboard aggregation — pandas deprecation warning surfaced during execution"
  - "S3 chi-square contradicts S1 direction: OR=1.210 vs S1 OR=0.648 (blitz MORE likely with PA on 1st-and-10)"

patterns-established:
  - "render_leaderboard() parameterized with exact_pixels flag — same function renders hero and social preview"
  - "QUERY-07 raw blitz_count/no_blitz_count used; entropy computed inline consistent with 02_predictability_modeling.py"

requirements-completed: [VIZ-01, VIZ-02, VIZ-03, VIZ-04, VIZ-05]

# Metrics
duration: 55min
completed: 2026-04-30
---

# Phase 4 Plan 01: Visualizations + S3 Chi-Square Summary

**Three PNGs (hero leaderboard portrait, 1280x640 social preview, KL-vs-H scatter) plus S3 exploratory chi-square cells appended to 02_predictability_modeling.py — all VIZ requirements satisfied and both notebooks run end-to-end on the live DB with cleared committed outputs**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-04-30T21:45Z
- **Completed:** 2026-04-30T22:40Z
- **Tasks:** 4 of 4
- **Files modified:** 7

## Accomplishments

- Built `analysis/03_visualizations.py` + paired `.ipynb` with complete jupytext scaffold, adjustText import, apply_style(), DB assertion, IMAGES_DIR resolution
- Rendered 3 PNGs: hero leaderboard (1845x2178 portrait), social preview (exactly 1280x640), KL-vs-H rank-rank scatter (exactly 1600x1600 square)
- Appended S3 exploratory chi-square cells to `02_predictability_modeling.py` with full reporting battery + OR-delta first-class output; both notebooks cleared and verified running end-to-end
- Added adjustText>=1.0,<2 pin to requirements.txt; adjustText 1.3.0 installed and version-asserted

## Task Commits

1. **Task 1: Scaffold + adjustText pin** - `bb02935` (feat)
2. **Task 2: Leaderboard + hero PNG + social preview** - `8e3c82c` (feat)
3. **Task 3: KL-vs-H scatter + clear notebook outputs** - `8746e6e` (feat)
4. **Task 4: S3 exploratory chi-square cells** - `76ef3ad` (feat)

## Files Created/Modified

- `requirements.txt` — Added adjustText>=1.0,<2 pin under Visualization block
- `analysis/03_visualizations.py` — New jupytext source: scaffold + leaderboard renderer + scatter (374 lines)
- `analysis/03_visualizations.ipynb` — Paired notebook; cleared outputs (21.8 KB)
- `findings/images/01_predictability_ranking.png` — Hero leaderboard, 1845x2178 portrait, 114 KB
- `findings/images/01_predictability_ranking_top12.png` — Social preview, 1280x640, 55 KB
- `findings/images/02_kl_vs_h_scatter.png` — KL-vs-H scatter, 1600x1600 square, 139 KB
- `analysis/02_predictability_modeling.py` — S3 exploratory cells inserted + Limitations summary line
- `analysis/02_predictability_modeling.ipynb` — Cleared outputs (32 KB)

## PNG Paths and Dimensions

| File | Dimensions | Size | Portrait/Square |
|------|-----------|------|----------------|
| `findings/images/01_predictability_ranking.png` | 1845x2178 | 114 KB | Portrait (height > width) |
| `findings/images/01_predictability_ranking_top12.png` | 1280x640 | 55 KB | Landscape (exact 1280x640) |
| `findings/images/02_kl_vs_h_scatter.png` | 1600x1600 | 139 KB | Square |

## Color Palette Usage

Palette indices matched recommendation exactly:
- `palette[0]` (blue #0173b2) — top-3 teams on hero leaderboard
- `palette[1]` (orange #de8f05) — bottom-3 teams (non-red per D-28)
- `palette[7]` (gray #949494) — middle 26 teams
- No `palette[3]` (red) used anywhere

## Empirically Computed League Average

**League average predictability index: 14.28** (rendered as the dashed vertical line label). Note: the plan estimated ~12.5 based on the Phase 3 brief, but the live computation from QUERY-07 via the weighted mean aggregation yields 14.28. The plan's estimate was approximate; the live DB value is authoritative.

## S3 Chi-Square Output Values

Universe: `competitive_plays JOIN ftn_play, down=1 AND ydstogo=10 AND play_type='pass'`
Threshold: `n_blitzers >= 1` (corrected per D-14)

| Metric | Value |
|--------|-------|
| N total | 18,609 |
| N(PA=1) | 8,652 (46.49%) |
| N(PA=0) | 9,957 |
| chi2 | 33.4632 |
| p-value | <0.000001 (highly significant) |
| OR | 1.210 |
| 95% CI | [1.135, 1.291] |
| P(blitz\|PA=1, S3) | 0.2938 |
| P(blitz\|PA=0, S3) | 0.2558 |
| Observed pp gap | +3.80pp |
| OR delta vs S1 | +0.562 (S1 OR=0.648, S3 OR=1.210) |
| Direction agreement with S1 | **no** |

**Interpretation (5-scenario rule D-13, Scenario 3 — contradicts):** OR > 1 regardless of p. On 1st-and-10, defenses are MORE likely to blitz against play-action (+3.80pp, OR=1.210, highly significant). This contradicts the S1 direction (where PA was associated with LESS blitzing, OR=0.648). The OR delta of +0.562 between situations is a first-class FINDINGS input for insight #4.

## QUERY-01 Column Shape

`team_blitz["blitz_rate"]` column existed as expected. QUERY-01 returns: `defteam, n_pass_plays, blitz_count, blitz_rate, league_blitz_rate, deviation_pp`. KL divergence was computed inline via `kl_binary()` against the mean of `blitz_rate` across teams (~0.2938). No column substitution or SQL modification required.

## adjustText Label Resolution

`adjust_text()` was called with `arrowprops=dict(arrowstyle="-", color="#666666", lw=0.6)` and `only_move={"text": "xy"}`. All 8 callout teams (MIN, TB, PIT, MIA, DET, PHI, SF, IND) were found in the ranks DataFrame and labeled without manual offset. The scatter output is square (1600x1600) so labels have room to disperse without collision.

## Notebook Output Status

| Notebook | Post-clear size | Limit |
|----------|----------------|-------|
| `analysis/02_predictability_modeling.ipynb` | 32 KB | <60 KB |
| `analysis/03_visualizations.ipynb` | 21.8 KB | <50 KB |

Both run end-to-end on the live DB (VIZ-05 verified). Both have cleared outputs in committed form.

## Decisions Made

- `rc_context(savefig.bbox=None)` pattern chosen to bypass `_style.py`'s `savefig.bbox='tight'` rcParam, which was trimming pixels asymmetrically and breaking the 1280x640 exact pixel requirement for the social preview. Same pattern applied to the scatter to ensure exactly square output.
- Leaderboard aggregation updated with `include_groups=False` to suppress a pandas deprecation warning that appeared at execution time (groupby apply on grouping columns).
- Entropy computed inline in `03_visualizations.py` from raw `blitz_count`/`no_blitz_count` columns — QUERY-07 does not expose a pre-computed entropy column; this matches the pattern in `02_predictability_modeling.py`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] QUERY-07 missing `entropy` and `n` columns assumed by plan scaffold**
- **Found during:** Task 1 (scaffold) / Task 2 (execution)
- **Issue:** Plan's leaderboard data-prep cell assumed QUERY-07 returns `entropy` and `n` columns. Actual QUERY-07 returns `blitz_count`, `no_blitz_count`, `total_pass_plays` (one row per defteam x season x situation). The plan's code would have raised a KeyError.
- **Fix:** Added season-level aggregation to (team, situation) cells, then computed entropy inline via `scipy.stats.entropy` — identical to the formula in `02_predictability_modeling.py:compute_predictability_index()`. No query changes needed.
- **Files modified:** `analysis/03_visualizations.py`
- **Committed in:** `bb02935` (Task 1), `8e3c82c` (Task 2)

**2. [Rule 1 - Bug] Social preview PNG pixel dimensions off-target (1255x611 then 1255x664 instead of 1280x640)**
- **Found during:** Task 2 (PNG dimension verification)
- **Issue:** `_style.py` sets `savefig.bbox='tight'` as a global rcParam; this trims pixels asymmetrically around chart elements, making `figsize=(6.4, 3.2) @ 200 DPI` produce fewer than 1280x640 pixels.
- **Fix:** Added `exact_pixels` parameter to `render_leaderboard()`. When set, saves with `mpl.rc_context({'savefig.bbox': None})` to bypass the tight-crop trim. Verified empirically: produces exactly 1280x640.
- **Files modified:** `analysis/03_visualizations.py`
- **Committed in:** `8e3c82c` (Task 2)

**3. [Rule 1 - Bug] Scatter PNG not square (1674x1576, diff=98 > 50px threshold)**
- **Found during:** Task 3 (PNG dimension verification)
- **Issue:** Same `savefig.bbox='tight'` issue asymmetrically trimmed the 8x8 figure after `adjust_text()` displaced labels outside axes bounds.
- **Fix:** Added `mpl.rc_context({'savefig.bbox': None})` to scatter save call. Output: exactly 1600x1600.
- **Files modified:** `analysis/03_visualizations.py`
- **Committed in:** `8746e6e` (Task 3)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs in plan scaffold or matplotlib interaction)
**Impact on plan:** All fixes necessary for correctness (KeyError prevention, exact pixel dimensions). No scope creep. The `rc_context` pattern is a clean matplotlib idiom; the inline entropy computation matches existing project patterns exactly.

## Issues Encountered

- pandas `include_groups` deprecation warning appeared in the groupby apply for leaderboard aggregation; added `include_groups=False` inline.
- matplotlib `bbox_inches="standard"` is not a valid value (raises `AttributeError`); the working solution is `rc_context({'savefig.bbox': None})`.

## Known Stubs

None. All three PNGs are produced from live DB data via the actual queries. The S3 chi-square cells compute from the live DB. No hardcoded placeholders or empty values flow to any output.

## Threat Flags

None. This plan is read-only against the DB (no writes), creates static PNGs, and appends analytical cells to an existing notebook. No new network endpoints, auth paths, file access patterns beyond the existing DB path, or schema changes.

## Next Phase Readiness

- **04-02 (FINDINGS + README):** Hero PNG exists at `findings/images/01_predictability_ranking.png` (prerequisite for README embed above the fold). S3 chi-square numbers are available for authoring insight #4: chi2=33.46, p<0.000001, OR=1.210 [1.135, 1.291], OR delta vs S1=+0.562, direction=contradicts.
- **04-03 (CI + Ship):** Social preview PNG exists at `findings/images/01_predictability_ranking_top12.png` (1280x640, ready for SHIP-04 upload).
- No blockers.

## Self-Check

### Created files exist

- `findings/images/01_predictability_ranking.png` — FOUND (114 KB)
- `findings/images/01_predictability_ranking_top12.png` — FOUND (55 KB, 1280x640)
- `findings/images/02_kl_vs_h_scatter.png` — FOUND (139 KB, 1600x1600)
- `analysis/03_visualizations.py` — FOUND
- `analysis/03_visualizations.ipynb` — FOUND (21.8 KB, cleared)
- `analysis/02_predictability_modeling.ipynb` — MODIFIED (32 KB, cleared)

### Commits exist

- `bb02935` — FOUND (Task 1)
- `8e3c82c` — FOUND (Task 2)
- `8746e6e` — FOUND (Task 3)
- `76ef3ad` — FOUND (Task 4)

## Self-Check: PASSED

---
*Phase: 04-story-and-ship*
*Completed: 2026-04-30*
