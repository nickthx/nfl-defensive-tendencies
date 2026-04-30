---
status: passed
phase: 03-analytical-layer-sql-python
verified: 2026-04-30T00:00:00Z
must_haves_passed: 15/15
requirements_passed: 17/17
---

# Phase 3: Analytical Layer (SQL + Python) — Verification Report

**Phase Goal (ROADMAP §Phase 3):** Every business question from the analysis plan has a SQL artifact and Python statistical evidence — including the normalized predictability index, at least one chi-square test, and sample-size-disciplined claims.

**Verified:** 2026-04-30
**Status:** passed
**Re-verification:** No — initial verification

---

## Phase Goal Verification (ROADMAP Success Criteria 1–5)

### Criterion 1: All 8 queries reference `competitive_plays`, run end-to-end, and use window functions + CTEs + cross-source join with header documentation

**Status:** PASS

Evidence:
- All 8 SQL files exist with the locked D-07 filenames in `queries/`:
  - `01_tendency_distribution_by_team.sql`
  - `02_blitz_rate_by_situation.sql` (D-07 renaming from `_by_down_and_distance`)
  - `03_red_zone_vs_midfield.sql`
  - `04_epa_allowed_by_blitz.sql` (D-07 renaming from `_by_<dim>`)
  - `05_third_long_pressure_tendencies.sql`
  - `06_play_action_response.sql`
  - `07_situational_predictability_score.sql`
  - `08_blitz_rate_trend_by_season.sql` (D-07 renaming from `_week_over_week_drift`)
- `competitive_plays` referenced in all 8 files (18 total occurrences across the slate).
- D-08 6-section header docblock present in every file: 48 total prefix matches across 8 files (8 × 6 = 48).
- Window function evidence: `OVER ()` in `queries/01_tendency_distribution_by_team.sql` (lines 16, 18) — `AVG(...) OVER ()` for inline league-average.
- CTE evidence: `WITH ... AS (` in 4 files (02, 04, 06, 07).
- Cross-source FTN↔pbp join `JOIN ftn_play USING (game_id, play_id)` in all 8 files.
- Behavioral spot-check: `python scripts/_verify_queries_run.py` exits 0 with row counts: Q1=32, Q2=512, Q3=2, Q4=8, Q5=32, Q6=8, Q7=512, Q8=132 — matches 03-02 SUMMARY exactly.

### Criterion 2: Cell 1 of `02_predictability_modeling.ipynb` defines + applies the normalization scheme; predictability index conditional on situation; surfaced as 0–100 per-team metric

**Status:** PASS

Evidence (literal-formula audit of `analysis/02_predictability_modeling.py`):
- `K_SUPPORT: int = 2` — line 98
- `MIN_N_FOR_CELL: int = 30` — line 99
- `SPEARMAN_VALIDATION_GATE: float = 0.85` — line 100
- `H = stats.entropy([blitz_count, no_blitz_count], base=np.e)` — line 111
- `(1 - H / np.log(K_SUPPORT)) * 100` — line 112
- `compute_predictability_index()` and `compute_kl_from_league()` defined; smoke-checked in-notebook (uniform → 0, deterministic → 100, below-N → NaN)
- 32×4 matrix surfaced via `team_sit.pivot(index="defteam", columns="situation_id", values="pred_index")`
- Per-team aggregate scalar via sample-size-weighted mean (per_team_scalar leaderboard)
- All 128 (defteam × situation) cells clear N≥30 — zero exclusions

### Criterion 3: ≥1 chi-square test on a pre-registered situation reports test statistic, effect size, AND Wilson 95% CI on the proportion

**Status:** PASS

Evidence (in `analysis/02_predictability_modeling.py` Cell 13, lines ~285–325):
- Pre-registered situation: S1 (`down=3 AND ydstogo>=7 AND play_type='pass'` from `competitive_plays`) — D-09 compliant
- 2×2 contingency: PA × blitz league-aggregate (NOT 32×2 omnibus) — D-09 compliant
- `stats.chi2_contingency(table)` called (line 301)
- Effect size = odds ratio + 95% CI: `odds_ratio = (a * d) / (b * c)` (line 307); log-OR + 1.96·SE closed-form CI
- Wilson 95% CI on `P(blitz | PA=1, S1)` via closed-form (lines 314–322; no statsmodels — D-12 compliant)
- Empirical numbers from notebook execution (per 03-03 SUMMARY): chi2=3.4643, p=0.0627, OR=0.648 [0.418, 1.003], Wilson CI=[0.176, 0.336], N=109 PA=1 plays

### Criterion 4: `_common.py` exposes SEED=42, SQLite connection helper, `min_n_filter`; `min_n_filter` applied to every analytical claim

**Status:** PASS

Evidence:
- `analysis/_common.py` line 20: `SEED: int = 42`
- Line 23: `DB_PATH: Path = Path(__file__).resolve().parent.parent / "data" / "nfl_defensive_tendencies.db"`
- Line 28: `def get_conn(db_path: Path | str = DB_PATH) -> sqlite3.Connection:` — returns plain `sqlite3.Connection` with `PARSE_DECLTYPES`
- Lines 40–72: `def min_n_filter(df, n_col="n", n_threshold=30) -> pd.DataFrame:` — emits `logger.warning` listing dropped (defteam, situation_id, season) tuples; does not raise
- `min_n_filter` applied in:
  - `analysis/01_exploratory.py` line 141: `min_n_filter(team_situation_n, n_col="n", n_threshold=30)`
  - `analysis/02_predictability_modeling.py` (3 distinct call sites — predictability per-team aggregation, KL aggregation, sensitivity helper `_per_team_scalar`)
- Behavioral smoke check: `from analysis._common import ...; min_n_filter(df=[(A,10),(B,40)])` correctly drops A and emits WARNING.

### Criterion 5: ≥1 sensitivity check — same headline finding computed with vs without `competitive_plays` filter — both numbers documented

**Status:** PASS

Evidence (in `analysis/02_predictability_modeling.py` Cells 15–16):
- D-13 scope: predictability-index leaderboard (NOT chi-square) recomputed twice — confirmed
- `SQL_PRED_UNFILTERED` constant defined (line 343) with `FROM plays p` (line 353) — bypasses `competitive_plays` view
- Both leaderboards computed via `_per_team_scalar(raw)` (with-filter) and `_per_team_scalar(raw_unf)` (without-filter)
- Spearman ρ between leaderboards printed: `stats.spearmanr(merged["rank_with"], merged["rank_without"])` (line 411)
- Universe sizes verified empirically against the live DB:
  - With-filter (competitive_plays JOIN ftn_play, pass): 58,178 plays
  - Unfiltered (plays JOIN ftn_play, pass): 80,782 plays — matches 03-03 SUMMARY claim and D-13 scope exactly
- Per 03-03 SUMMARY: rank delta + Spearman ρ = 0.982, max |delta| = 4 — leaderboard robust to wp/qtr filter

---

## REQ-ID Coverage (17/17)

| REQ-ID | Source Plan | Artifact / Evidence | Status |
|--------|-------------|---------------------|--------|
| QUERY-01 | 03-02 | `queries/01_tendency_distribution_by_team.sql` — 32 rows, league blitz rate 29.4% | SATISFIED |
| QUERY-02 | 03-02 | `queries/02_blitz_rate_by_situation.sql` — 512 rows, CTE | SATISFIED |
| QUERY-03 | 03-02 | `queries/03_red_zone_vs_midfield.sql` — 2 rows, RZ pressure 36.2% vs midfield 26.7% | SATISFIED |
| QUERY-04 | 03-02 | `queries/04_epa_allowed_by_blitz.sql` — 8 rows, CTE | SATISFIED |
| QUERY-05 | 03-02 | `queries/05_third_long_pressure_tendencies.sql` — 32 rows, DET leads at 52.3% | SATISFIED |
| QUERY-06 | 03-02 | `queries/06_play_action_response.sql` — 8 rows, CTE | SATISFIED |
| QUERY-07 | 03-02 | `queries/07_situational_predictability_score.sql` — 512 rows, CTE | SATISFIED |
| QUERY-08 | 03-02 | `queries/08_blitz_rate_trend_by_season.sql` — 132 rows incl. 4 LEAGUE rows | SATISFIED |
| QUERY-09 | 03-02 | All queries reference `competitive_plays` + 6-section header; window in Q1, CTEs in Q2/Q4/Q6/Q7, cross-source join in all 8; `scripts/_verify_queries_run.py` exits 0 | SATISFIED |
| STAT-01 | 03-01 | `analysis/_common.py`: SEED=42, get_conn(), min_n_filter() with locked signatures | SATISFIED |
| STAT-02 | 03-01 | `analysis/_style.py`: PALETTE='colorblind', savefig.dpi=200, apply_style() | SATISFIED |
| STAT-03 | 03-01 | `analysis/01_exploratory.ipynb`: descriptive stats per S1/S2/S3/S4; 0 cells dropped at N≥30 | SATISFIED |
| STAT-04 | 03-03 | Cell 1 of `02_predictability_modeling.ipynb` defines H/log(2) + KL secondary + 0–100 mapping verbatim | SATISFIED |
| STAT-05 | 03-03 | Predictability index per-(team × situation), 32×4 matrix + per-team aggregate scalar leaderboard | SATISFIED |
| STAT-06 | 03-03 | S1 PA × blitz chi-square: chi2=3.46, p=0.063, OR=0.648 [0.418,1.003], Wilson CI [0.176,0.336] | SATISFIED |
| STAT-07 | 03-03 | `min_n_filter` applied to per-team aggregation, KL aggregation, sensitivity helper | SATISFIED |
| STAT-08 | 03-03 | Sensitivity: with-filter 58k vs unfiltered 80,782 pass plays; Spearman ρ=0.982 | SATISFIED |

**No orphaned requirements.** All 17 Phase 3 REQ-IDs appear in plan frontmatter (03-01: STAT-01..03; 03-02: QUERY-01..09; 03-03: STAT-04..08) and have corresponding code artifacts on disk.

---

## Must-Have Audit

### 03-01 (analysis scaffold)

| Truth | File / Evidence | Status |
|-------|-----------------|--------|
| `_common.py` exposes SEED=42, get_conn, min_n_filter with locked signatures | `analysis/_common.py` lines 20–72 | PASS |
| `_style.py` defines savefig.dpi=200 + 'colorblind' palette | `analysis/_style.py` lines 19, 26, 42–45 | PASS |
| `01_exploratory.ipynb` profiles per-situation N for S1–S4, emits WARNING for N<30 cells | `analysis/01_exploratory.py` lines 87, 92, 120, 141, 164 | PASS |
| jupytext pairing `formats: ipynb,py:percent` | Header on both `.py` files line 4 | PASS |
| Notebook outputs cleared on disk | JSON inspection: 0/5 + 0/10 cells with outputs | PASS |

### 03-02 (SQL slate)

| Truth | File / Evidence | Status |
|-------|-----------------|--------|
| All 8 .sql files with locked D-07 filenames | `ls queries/*.sql` shows exact 8 names; 3 D-07 renamings present | PASS |
| Every file references `competitive_plays` | 8/8 files match | PASS |
| 6-section D-08 header on every file | 48 header prefix matches across 8 files (8×6) | PASS |
| Every file executes against the DB and returns non-empty | `scripts/_verify_queries_run.py`: 8 OK lines + ALL CHECKS PASSED | PASS |
| QUERY-09 slate-collective: ≥1 window, ≥1 CTE, ≥1 cross-source join | Window in Q1; CTE in Q2/Q4/Q6/Q7; cross-source join in all 8 | PASS |

### 03-03 (predictability modeling)

| Truth | File / Evidence | Status |
|-------|-----------------|--------|
| Cell 1 methodology lock with all 5 locked literals verbatim | Lines 98–112 (K_SUPPORT, MIN_N_FOR_CELL, SPEARMAN_VALIDATION_GATE, entropy formula, 0–100 mapping) | PASS |
| Predictability index = 32×4 matrix + per-team scalar | `team_sit.pivot(...)` + `per_team_scalar` leaderboard | PASS |
| STAT-06 chi-square prints chi2 + OR + 95% CI + Wilson CI | Lines 301, 307, 314–322 | PASS |
| STAT-08 sensitivity recomputes leaderboard on competitive_plays vs unfiltered | `SQL_PRED_UNFILTERED` w/ `FROM plays p` (lines 343, 353); Spearman line 411 | PASS |
| `min_n_filter` applied to every analytical claim | 3+ call sites in modeling notebook | PASS |
| jupytext pairing `formats: ipynb,py:percent` | Header line 4 | PASS |
| Notebook outputs cleared on disk | JSON inspection: 0/10 cells with outputs | PASS |

---

## Documented Findings Worth Highlighting (Phase 4 FINDINGS.md feed)

These are **substantive findings**, not gaps. They are the analytical output Phase 3 was supposed to produce and should feature in the FINDINGS.md memo.

1. **`n_blitzers` threshold correction (independent rediscovery by both Wave 2 agents).**
   The plan-doc threshold of `n_blitzers > 4` produced only 7 blitz plays in the entire 58k-pass-play universe (0.012%) — analytically meaningless. FTN's `n_blitzers` counts *extra rushers above the base 4-man front*, not total pass rushers. Both 03-02 and 03-03 agents independently caught the bug; corrected to `n_blitzers > 0`. Empirical league blitz rate under the corrected threshold = 29.4% (consistent with NFL norms). All 8 SQL files + the inline notebook SQL strings now use `n_blitzers > 0`. This is documented in 03-02 SUMMARY § Deviations and 03-03 SUMMARY § Deviations — COMPLIANT (Rule 1 bug fix), not a gap.

2. **Spearman ρ = -0.111 between H/log(k) and KL leaderboards (validation gate FAILED, but DOCUMENTED per D-01).**
   D-01 explicitly says: "if Spearman ρ < 0.85, treat as substantive finding to investigate, NOT papered over." The gate is *defined* in Cell 3 (line 100) and *applied* in Cell 11 (line 242). The empirical ρ = -0.111 reveals that H/log(k) (concentration) and KL (deviation-from-baseline) measure orthogonal concepts — MIN/TB blitz at extreme rates (high KL) yet do so with maximum variance (low predictability). This is a feature of the analysis, not a bug. The requirement says "defines and applies the normalization scheme" — both are satisfied.

3. **STAT-06 chi-square: marginal p=0.0627, OR=0.648 (defenses blitz LESS against PA on 3rd-and-long).**
   chi2=3.46, expected min cell=36.6 (assumption holds), OR 95% CI=[0.418, 1.003] crosses 1 marginally. Wilson CI on P(blitz|PA=1, S1)=[0.176, 0.336] (N=109). Observed gap = -8.94pp exceeds the pre-registered ≥5pp gate but underpowered (PA=1 N=109 limits power). The requirement says "reports test statistic, effect size, AND Wilson 95% CI" — all three present. Statistical significance was never the criterion.

4. **STAT-08 sensitivity Spearman ρ = 0.982 — leaderboard robust to wp filter.**
   Top-5 (PHI, SF, IND, HOU, TEN) identical across both universes; max rank delta = 4. The competitive_plays wp/qtr filter does not materially change the predictability ranking — strengthens the FINDINGS.md narrative.

5. **All 128 (defteam × situation) cells clear N≥30 across S1/S2/S3/S4.**
   No dropouts in the predictability index aggregate. The 4-season scope provides sufficient per-team volume even in the smallest situation (S1: 9,925 plays / 32 teams ≈ 310 plays/team avg). The `min_n_filter` WARNING mechanism is in place but never triggered for this slate.

---

## Anti-Pattern Scan

| Pattern | Result |
|---------|--------|
| TODO / FIXME / HACK / placeholder text in delivered code | None |
| `return null` / `return []` / `return {}` stubs | None |
| Hardcoded empty data passed to rendering | N/A (no rendering layer) |
| Forbidden libraries (statsmodels / plotly / bokeh / streamlit) | None — only mentions are explicit "no statsmodels" comments |
| Notebook outputs leaked into committed `.ipynb` | 0 of 5 (`01_exploratory`) and 0 of 10 (`02_predictability_modeling`) code cells contain outputs |
| `data/nfl_defensive_tendencies.db` committed | Not committed (only `data/README.md` is tracked); covered by `.gitignore` |

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `_common.py` imports cleanly + behavior correct | `python -c "from analysis._common import SEED, get_conn, min_n_filter; ..."` | SEED=42, get_conn returns sqlite3.Connection, min_n_filter drops below-30 with WARNING | PASS |
| `_style.py` applies rcParams | `apply_style(); mpl.rcParams['savefig.dpi']==200; PALETTE=='colorblind'` | PASS | PASS |
| All 8 SQL files execute end-to-end | `python scripts/_verify_queries_run.py` | All 8 OK + ALL CHECKS PASSED + QUERY-09 meta-compliance | PASS |
| Sensitivity universe sizes match SUMMARY claims | DB query: competitive_plays JOIN ftn_play pass = 58,178; plays JOIN ftn_play pass = 80,782 | Matches 03-03 SUMMARY (D-13 scope) | PASS |
| Corrected blitz rate ≈ 29% (league) | `SUM(n_blitzers > 0) / COUNT(*)` on competitive pass plays | 17,131 / 58,178 = 29.45% | PASS |
| Broken `> 4` threshold confirms documented bug | `SUM(n_blitzers > 4)` on same universe | 7 plays — confirms n_blitzers encoding (extra-above-base, not total) | PASS |

---

## CLAUDE.md Compliance

| Rule | Status |
|------|--------|
| Source code in `analysis/`, `queries/`, `scripts/` (not repo root) | PASS — 0 source files at repo root |
| No `tests/` cargo-cult | PASS — no `tests/` directory |
| `.db` gitignored, not committed | PASS — only `data/README.md` tracked |
| Locked stack (scipy, numpy, pandas, seaborn, matplotlib) | PASS — no statsmodels/plotly/bokeh/streamlit imports |
| No AI-template emoji headers in summaries | PASS — SUMMARYs use plain markdown |

---

## Out-of-Scope Discipline (Phase 4 work NOT in this phase)

| Item | Status |
|------|--------|
| `findings/FINDINGS.md` | Not created (correct — Phase 4 / DOC-01) |
| `findings/images/*.png` | Empty directory with `.gitkeep` (correct) |
| `analysis/03_visualizations.ipynb` | Not created (correct — Phase 4 / VIZ-01) |
| README rewrites in this phase's commits | Phase 3 commits (b941ecc → f17effe) touch only `analysis/`, `queries/`, `scripts/`, `.planning/` |
| GitHub MCP repo creation | Not attempted (correct — Phase 4 / SHIP-03) |

---

## Documented Deviations vs Gaps

All deviations documented in the SUMMARY files are **COMPLIANT**, not gaps:

1. **`n_blitzers > 4` → `> 0` correction** — documented Rule 1 bug fix in both 03-02 SUMMARY and 03-03 SUMMARY. Both agents independently caught and corrected. Evidence-driven (9 plays under broken threshold vs 29.4% league rate under corrected). **Compliant.**
2. **Spearman ρ = -0.111 (gate failure)** — documented per D-01 explicit instruction "treat as substantive finding to investigate, NOT papered over." Gate is *defined and applied* — that is what STAT-04 requires. **Compliant.**
3. **3 ruff/Path auto-fixes in 03-01** — `Path(__file__)` undefined in .ipynb cells (switched to `Path.cwd()` walk); ruff F401 unused imports; ruff E402 post-sys.path imports given `# noqa: E402`. All standard auto-fixes. **Compliant.**
4. **Marginal p=0.063 in chi-square** — STAT-06 requires "reports test statistic", not "achieves significance at α=0.05". The reported numbers ARE the deliverable. **Compliant.**
5. **REQUIREMENTS.md still shows pre-D-07 filenames** (`02_blitz_rate_by_down_and_distance.sql`, `04_epa_allowed_by_<dim>.sql`, `08_week_over_week_drift.sql`) — D-07 in 03-CONTEXT.md locks the renamings; plan frontmatter and code use the corrected names. REQUIREMENTS.md was authored at Phase-1 init before the dimension was chosen ("(or equivalent — exact dimension chosen in AUDIT-03)" appears in the QUERY-02 entry). The plans honor the contract; the requirements doc has the original placeholder text. Not a gap. (Could be propagated to REQUIREMENTS.md as an editorial cleanup in Phase 4 if desired.)

---

## Gaps Found

None.

---

## Status Decision

**Status: passed.**

Reasoning:
- All 5 ROADMAP success criteria PASS with concrete evidence (file paths + line numbers + behavioral spot-checks).
- All 17 Phase 3 REQ-IDs (QUERY-01..09 + STAT-01..08) appear in plan frontmatter and have corresponding code artifacts on disk that satisfy the acceptance criteria.
- All 15 plan-frontmatter must-haves PASS (5 in 03-01, 5 in 03-02, 7 in 03-03 with 2 jupytext/output-clear truths shared).
- Behavioral spot-checks confirm: imports work, queries run end-to-end, universe sizes match SUMMARY claims, blitz threshold correction is empirically grounded (7 plays under broken threshold, 17,131 under corrected).
- All anti-patterns scan clean. CLAUDE.md compliance clean. Out-of-scope discipline clean (no Phase 4 work crept in).
- Documented deviations (n_blitzers correction, Spearman gate failure, ruff auto-fixes, marginal p-value) are COMPLIANT per the explicit instructions in 03-CONTEXT.md (D-01) and the requirement wording (STAT-06 says "reports", not "rejects null").

Phase 3 is ready for `/gsd-update-roadmap` and proceed to Phase 4.

---

_Verified: 2026-04-30_
_Verifier: Claude (gsd-verifier)_
