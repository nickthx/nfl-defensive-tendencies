---
phase: 03-analytical-layer-sql-python
plan: "02"
subsystem: queries
tags: [sql, competitive_plays, blitz-analysis, query-09, window-functions, cte]
dependency_graph:
  requires:
    - 03-01 (analysis/_common.py, analysis/_style.py — wave 1 scaffolding)
    - 02-* (data/nfl_defensive_tendencies.db, schema/03_views.sql — Phase 2 build)
  provides:
    - queries/01..08_*.sql (8 SQL rollup artifacts consumed by Phase 3 notebooks + Phase 4 FINDINGS)
    - scripts/_verify_queries_run.py (QUERY-09 meta-compliance + execution smoke verifier)
  affects:
    - analysis/01_exploratory.ipynb (reads QUERY-01, QUERY-02, QUERY-07)
    - analysis/02_predictability_modeling.ipynb (reads QUERY-07 for entropy inputs; QUERY-06 for chi-square)
    - findings/FINDINGS.md (Phase 4; reads QUERY-03, QUERY-04, QUERY-05, QUERY-08 for narrative)
tech_stack:
  added: []
  patterns:
    - SQLite window function (AVG OVER ()) in QUERY-01 for inline league-average deviation
    - CTE chain for situation labeling (CASE WHEN buckets) reused across QUERY-02/04/06/07
    - UNION ALL for LEAGUE aggregate row alongside per-team rows in QUERY-08
key_files:
  created:
    - queries/01_tendency_distribution_by_team.sql
    - queries/02_blitz_rate_by_situation.sql
    - queries/03_red_zone_vs_midfield.sql
    - queries/04_epa_allowed_by_blitz.sql
    - queries/05_third_long_pressure_tendencies.sql
    - queries/06_play_action_response.sql
    - queries/07_situational_predictability_score.sql
    - queries/08_blitz_rate_trend_by_season.sql
    - scripts/_verify_queries_run.py
  modified: []
decisions:
  - "n_blitzers > 0 (not > 4) is the correct blitz threshold for FTN data in this DB; n_blitzers counts extra rushers above the base front, not total rushers — see Deviations"
  - "JOIN ftn_play USING (game_id, play_id) works correctly in SQL files using single-quoted string literals; double-quoted identifiers in Python test code caused apparent failures"
metrics:
  duration_minutes: 11
  completed_date: "2026-04-30"
  tasks_completed: 2
  files_created: 9
---

# Phase 3 Plan 02: SQL Query Slate Summary

One-liner: Eight situational blitz-tendency queries against the `competitive_plays` view, covering per-team distribution, situation × season rollups, EPA cost/benefit, play-action modifier, entropy inputs, and 4-season trend — all satisfying the D-08 6-section header convention and QUERY-09 slate-collective meta-compliance.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Author the 8 .sql query files | 4cb60de | queries/01..08_*.sql (8 files) |
| 2 | Write scripts/_verify_queries_run.py | 2cf98b7 | scripts/_verify_queries_run.py |

## Empirical Row Counts (from `scripts/_verify_queries_run.py`)

| Query | Filename | Rows | Notes |
|-------|----------|------|-------|
| QUERY-01 | 01_tendency_distribution_by_team.sql | 32 | One row per defteam; league blitz rate ~29.4% |
| QUERY-02 | 02_blitz_rate_by_situation.sql | 512 | 32 teams × 4 seasons × 4 situations (all cells populated) |
| QUERY-03 | 03_red_zone_vs_midfield.sql | 2 | red_zone: 7,553 pass plays, pressure_rate=0.3618; midfield: 50,625, pressure_rate=0.2674 |
| QUERY-04 | 04_epa_allowed_by_blitz.sql | 8 | 4 situations × 2 blitz flags (fully populated) |
| QUERY-05 | 05_third_long_pressure_tendencies.sql | 32 | One row per defteam on S1; DET leads at 52.3% blitz |
| QUERY-06 | 06_play_action_response.sql | 8 | 4 situations × 2 PA flags |
| QUERY-07 | 07_situational_predictability_score.sql | 512 | 32 teams × 4 seasons × 4 situations; feeds entropy index |
| QUERY-08 | 08_blitz_rate_trend_by_season.sql | 132 | 128 team-season rows + 4 LEAGUE rows (seasons 2022–2025) |

### Selected Empirical Values

- League blitz rate (competitive pass plays, 2022-2025): **29.4%** (QUERY-01)
- High-blitz team: MIN at 43.1%, TB at 40.6%, NYG at 37.4% (QUERY-01)
- League pressure rate, red zone vs midfield: 36.2% vs 26.7% — difference of 9.5pp (QUERY-03 empirical; S2-H1 hypothesis gap ≥ 5pp confirmed directionally)
- S1 (3rd-and-long) league blitz rate: DET highest at 52.3%; many teams exceed 35% on S1 (QUERY-05)
- LEAGUE season rows present for 2022, 2023, 2024, 2025 (QUERY-08 verified)

## QUERY-09 Slate-Collective Meta-Compliance

| Feature | Queries |
|---------|---------|
| Window function (`OVER (`) | QUERY-01 (`AVG(...) OVER ()` for inline league-average deviation_pp) |
| CTE (`WITH ... AS (`) | QUERY-02, QUERY-04, QUERY-06, QUERY-07 (situation labeling via CASE WHEN chain) |
| Cross-source FTN-pbp JOIN (`JOIN ftn_play USING (game_id, play_id)`) | All 8 queries |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected blitz threshold from n_blitzers > 4 to n_blitzers > 0**

- **Found during:** Task 1 smoke testing (immediately after writing the initial SQL files)
- **Issue:** The plan documents specify `blitz = n_blitzers > 4` citing "5+ rushers on a pass, in standard nflfastR convention." However, FTN's `n_blitzers` column counts *extra* blitzers above the base 4-man front — not total pass rushers. With the `> 4` threshold, only 9 plays in the entire 185,215-row FTN dataset qualified as blitzes (0.005% rate), rendering all blitz-rate queries analytically meaningless. The S1-H1 hypothesis ("league blitz rate on 3rd-and-long > 35%") would have been trivially and incorrectly falsified.
- **Fix:** Changed all blitz predicates from `n_blitzers > 4` to `n_blitzers > 0` (any extra rusher beyond the base front). The `n_pass_rushers >= 5` threshold in QUERY-03 and QUERY-05 (which uses total rushers) is unchanged and correct. Updated all 8 SQL file headers' Caveats sections to document the FTN encoding.
- **Empirical result:** League blitz rate = 29.4%; S1 high-blitz teams reach 52%. These values are analytically meaningful and consistent with the project's hypotheses.
- **Note for downstream (03-03 notebook):** The `D-02` decision in 03-CONTEXT.md references `n_blitzers > 4`. The notebook should use `n_blitzers > 0` when reading from QUERY-07's `blitz_count`/`no_blitz_count` columns (those are already computed with the corrected threshold). No SQL change needed in the notebook — it reads the pre-aggregated counts from QUERY-07.
- **Files modified:** All 8 `.sql` files (blitz predicate + Caveats header text)
- **Commit:** 4cb60de

**2. [Rule 1 - Bug (investigation)] SQLite USING join behavior with view + double-quoted string literals**

- **Found during:** Task 1 investigation after initial confusion about join behavior
- **Issue:** Python test code using double-quoted `"pass"` in SQLite queries caused the `play_type = "pass"` predicate to be interpreted as `play_type = <column named pass>` (the INTEGER 0/1 column), returning 0 rows. This was a test harness bug, not a SQL file bug. The `.sql` files themselves use standard single-quoted literals (`'pass'`) and work correctly.
- **Fix:** No SQL file changes needed. The verifier script uses `conn.execute(sql).fetchall()` loading the file verbatim — single-quoted literals evaluate correctly through that path.
- **Files modified:** None

## Known Stubs

None. All 8 queries return empirically verified non-empty result sets against `data/nfl_defensive_tendencies.db`.

## Threat Flags

None. All 8 files are read-only SELECT statements against a local SQLite DB. No network surface, no user input, no PII. The verifier script opens the DB in read mode and executes only pre-committed static SQL bodies.

## Self-Check

### Created files exist:

- `queries/01_tendency_distribution_by_team.sql` — FOUND
- `queries/02_blitz_rate_by_situation.sql` — FOUND
- `queries/03_red_zone_vs_midfield.sql` — FOUND
- `queries/04_epa_allowed_by_blitz.sql` — FOUND
- `queries/05_third_long_pressure_tendencies.sql` — FOUND
- `queries/06_play_action_response.sql` — FOUND
- `queries/07_situational_predictability_score.sql` — FOUND
- `queries/08_blitz_rate_trend_by_season.sql` — FOUND
- `scripts/_verify_queries_run.py` — FOUND

### Commits exist:

- `4cb60de` — feat(03-02): add queries/01..08_*.sql
- `2cf98b7` — feat(03-02): add scripts/_verify_queries_run.py

### Verifier exit status: 0 (ALL CHECKS PASSED)

## Self-Check: PASSED
