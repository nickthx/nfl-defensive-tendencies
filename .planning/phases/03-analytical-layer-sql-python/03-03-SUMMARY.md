---
phase: 03-analytical-layer-sql-python
plan: "03"
subsystem: analysis
tags: [predictability-index, chi-square, wilson-ci, sensitivity-check, jupytext, scipy]
dependency_graph:
  requires:
    - 03-01  # _common.py, _style.py scaffold
    - 03-02  # queries/07_situational_predictability_score.sql
  provides:
    - analysis/02_predictability_modeling.ipynb
    - analysis/02_predictability_modeling.py
  affects:
    - findings/FINDINGS.md  # Phase 4 reads empirical numbers from this notebook
    - findings/images/01_predictability_ranking.png  # Phase 4 hero chart
tech_stack:
  added: []
  patterns:
    - jupytext py:percent paired notebook
    - scipy.stats.entropy with base=np.e for Shannon entropy
    - scipy.stats.chi2_contingency for 2x2 contingency test
    - closed-form Wilson CI (no statsmodels)
    - closed-form log-OR + SE(log-OR) for odds ratio CI
    - scipy.stats.spearmanr for rank-correlation validation gate
    - sample-size-weighted groupby.apply with include_groups=False (pandas 2.2)
key_files:
  created:
    - analysis/02_predictability_modeling.ipynb
    - analysis/02_predictability_modeling.py
  modified:
    - queries/07_situational_predictability_score.sql  # blitz definition corrected (n_blitzers > 4 -> n_blitzers >= 1)
decisions:
  - "Blitz boolean corrected from n_blitzers > 4 to n_blitzers >= 1 (FTN n_blitzers counts dedicated extra rushers, not total pass rushers)"
  - "KL validation gate failure (rho=-0.111) treated as substantive finding per D-01 -- not papered over"
  - "QUERIES_DIR resolved via Path.cwd() walk (not Path(__file__)) per established notebook pattern from 01_exploratory.py"
metrics:
  duration: "8 minutes"
  completed: "2026-04-30"
  tasks_completed: 3
  tasks_total: 3
  files_created: 2
  files_modified: 1
requirements_satisfied:
  - STAT-04
  - STAT-05
  - STAT-06
  - STAT-07
  - STAT-08
---

# Phase 3 Plan 03: Predictability Modeling Notebook Summary

**One-liner:** Shannon entropy predictability index (H/log(2) normalized, 0-100 inverted) computed per 32 teams x 4 situations; KL gate failed (rho=-0.111) as substantive finding; S1 PA x blitz chi-square p=0.063, OR=0.648; STAT-08 leaderboard stability rho=0.982.

## What Was Built

`analysis/02_predictability_modeling.ipynb` (+ jupytext-paired `.py`) — the headline analytical artifact of Phase 3. The notebook executes end-to-end against the Phase 2 SQLite build and produces all STAT-04 through STAT-08 deliverables.

**Notebook structure (18 cells, alternating markdown/code):**

| Cell | Type | Content |
|------|------|---------|
| 1 | markdown | Methodology lock narrative (D-01..D-06) |
| 2 | code | Imports, sys.path walk, DB assert, SQL file loads |
| 3 | code | K_SUPPORT=2, MIN_N_FOR_CELL=30, SPEARMAN_VALIDATION_GATE=0.85; compute_predictability_index(); compute_kl_from_league(); smoke checks |
| 4 | markdown | Per-(team x season x situation) rollup section header |
| 5 | code | Load SQL_PRED_RAW; aggregate to 32x4 (team x situation) cells; apply pred_index formula |
| 6 | markdown | 32x4 matrix section header |
| 7 | code | Pivot to matrix; print excluded cell count |
| 8 | markdown | Per-team aggregate scalar section header |
| 9 | code | min_n_filter + sample-size-weighted mean; per_team_scalar leaderboard |
| 10 | markdown | KL secondary + Spearman validation gate section header |
| 11 | code | KL-from-league per (team x situation); Spearman rho gate |
| 12 | markdown | STAT-06 chi-square section header |
| 13 | code | S1_PA_BLITZ_SQL inline; 2x2 contingency; chi2; OR + 95% CI; Wilson CI; paired proportion |
| 14 | markdown | STAT-08 sensitivity section header |
| 15 | code | SQL_PRED_UNFILTERED (bypasses competitive_plays view, reads plays directly) |
| 16 | code | _per_team_scalar() helper; with/without filter leaderboards; rank delta; Spearman rho |
| 17 | markdown | Limitations + sample-size discipline summary header |
| 18 | code | Methodology lock satisfaction summary with all empirical numbers |

## Methodology Lock Confirmation

All five locked literals present verbatim in `analysis/02_predictability_modeling.py`:

1. `K_SUPPORT: int = 2` — fixed support per D-02
2. `MIN_N_FOR_CELL: int = 30` — dropout floor per D-05
3. `SPEARMAN_VALIDATION_GATE: float = 0.85` — KL-vs-H/log(k) gate per D-01
4. `H = stats.entropy([blitz_count, no_blitz_count], base=np.e)` — entropy formula
5. `(1 - H / np.log(K_SUPPORT)) * 100` — 0-100 inverted mapping per D-04

## Empirical Numbers (from notebook execution 2026-04-30)

### Per-team predictability scalar leaderboard (top-5 / bottom-5)

| Rank | Team | pred_index_scalar |
|------|------|------------------|
| 1 | PHI | 23.53 |
| 2 | SF | 23.48 |
| 3 | IND | 22.37 |
| 4 | HOU | 22.01 |
| 5 | TEN | 21.61 |
| ... | ... | ... |
| 28 | NE | 6.54 |
| 29 | KC | 6.21 |
| 30 | MIA | 5.91 |
| 31 | TB | 4.07 |
| 32 | MIN | 1.53 |

### 32x4 matrix stats

- Matrix shape: 32 x 4
- Excluded cells (N < 30): 0 of 128
- All 128 (team x situation) cells had N >= 30 — no dropouts

### KL secondary + Spearman validation gate (D-01)

- Spearman rho between H/log(k) and KL leaderboards: **-0.111** (p=0.546)
- Validation gate (rho >= 0.85): **FAILED**
- Top 5 disagreers: MIN (rank_h=32, rank_kl=1, delta=31), TB (31,2,29), PIT (26,3,23), MIA (30,8,22), DET (27,5,22)
- Interpretation: H/log(k) measures concentration (how close to 50/50 blitz rate). KL measures deviation from league baseline. MIN/TB have the most deviant blitz rates from league average (high KL) yet the most variable blitz patterns (low predictability index). These are opposite concepts — the divergence is a substantive finding for FINDINGS.md, not a methodological failure.

### STAT-06 chi-square: S1 PA x blitz (D-09 + D-11 + D-12)

- Filter: `competitive_plays`, down=3, ydstogo>=7, play_type='pass'
- N total: 8,825 pass plays (S1 universe)
- Contingency: [[27, 82], [2938, 5778]] (PA=1 row, PA=0 row; blitz / no-blitz cols)
- chi2 = 3.4643, p-value = 0.0627 (not significant at alpha=0.05)
- Expected min cell = 36.6 — chi-square assumption holds
- OR = 0.648, 95% CI = [0.418, 1.003]
- P(blitz | PA=1, S1) = 0.2477, Wilson CI = [0.1762, 0.3364] (N=109)
- Paired: P(blitz | PA=0, S1) = 0.3371 (N=8,716)
- Observed gap = -8.94pp (exceeds the pre-registered 5pp threshold in direction; defenses blitz LESS against play-action on 3rd-and-long)
- Note: p=0.063 is marginal (not significant at alpha=0.05); the small PA=1 cell (N=109) limits power

### STAT-08 sensitivity (D-13)

- With-filter universe (competitive_plays): 36,569 pass plays with ftn_play join
- Without-filter universe (plays directly): 51,170 pass plays with ftn_play join
- Spearman rho between leaderboards: **0.982** (p<0.0001)
- Max |rank_delta|: 4
- Top-5 stable (PHI/SF/IND/HOU/TEN identical, order PHI↔HOU swap)
- Conclusion: leaderboard headline is robust to the competitive_plays wp/qtr filter

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Blitz boolean threshold corrected: n_blitzers > 4 → n_blitzers >= 1**

- **Found during:** Task 3 (notebook execution failure — ZeroDivisionError in OR computation because a=0)
- **Issue:** Plan specified `n_blitzers > 4` following the nflfastR convention for `n_pass_rushers` (total rushers > 4 = blitz). FTN's `n_blitzers` column is a dedicated count of *extra rushers beyond the base 4-man defensive line* — any `n_blitzers >= 1` means a blitz was sent. With the `> 4` threshold, only 7 of 58k competitive pass plays qualified as blitzes (max n_blitzers in DB = 6), producing degenerate contingency cells and ZeroDivisionError.
- **Fix:** Changed all blitz boolean conditions from `n_blitzers > 4` to `n_blitzers >= 1` in:
  - `queries/07_situational_predictability_score.sql` (SQL file on disk)
  - `analysis/02_predictability_modeling.py` inline `S1_PA_BLITZ_SQL`
  - `analysis/02_predictability_modeling.py` inline `SQL_PRED_UNFILTERED`
- **Corrected blitz rate:** ~29% of competitive pass plays on 3rd-and-long (consistent with NFL norms)
- **Commits:** `bf2aba0` (notebook Task 3)

Note: The 03-02 parallel agent independently discovered the same issue and updated query 07 to `n_blitzers > 0` (equivalent to `>= 1`). Both fixes converge on the correct threshold.

**2. [Substantive Finding] KL validation gate failed (Spearman rho=-0.111 vs gate 0.85)**

- **Finding during:** Task 2 / Cell 11 execution
- **Per D-01:** Not papered over. H/log(k) and KL measure fundamentally different things — concentration vs. deviation-from-league-baseline. A team (e.g., MIN) can be maximally unpredictable in blitz rate (close to 50/50, low pred_index) while simultaneously deviating maximally from the league blitz average (high KL). These are orthogonal signals. The divergence is documented here and will require FINDINGS.md treatment in Phase 4.
- **Action:** Gate failure logged as warning in notebook Cell 11; top-5 disagreers printed with analysis. Not a methodological failure — both metrics are valid, they answer different questions.

### Coordination Note

Parallel 03-02 agent (queries) was in-flight during execution. Query 07 was present on disk as an untracked file when Task 2 executed. Both agents independently corrected the `n_blitzers > 4` bug; the 03-02 agent's version (`n_blitzers > 0`) superseded my corrected version (`n_blitzers >= 1`) via linter update — these are equivalent.

## Known Stubs

None. All data flows are wired to the Phase 2 DB. The notebook reads live from `competitive_plays` and `plays` via `get_conn()`.

## Threat Flags

None. Read-only SELECT queries against a local SQLite DB. All SQL strings are static literals. No new network endpoints, auth paths, or PII. Outputs cleared before commit per plan.

## Self-Check: PASSED

- `analysis/02_predictability_modeling.py` exists: FOUND
- `analysis/02_predictability_modeling.ipynb` exists: FOUND
- Commit 8ec47f3 (Task 1): FOUND
- Commit cef2649 (Task 2): FOUND
- Commit bf2aba0 (Task 3): FOUND
- All 13 locked-literal grep checks: PASSED
- ruff: CLEAN
- Notebook outputs cleared (all code cell outputs == []): CONFIRMED
- Notebook executed exit 0: CONFIRMED
