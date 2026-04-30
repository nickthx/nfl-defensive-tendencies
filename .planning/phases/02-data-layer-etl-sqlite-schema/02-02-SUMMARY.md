---
phase: 02-data-layer-etl-sqlite-schema
plan: 02
subsystem: data-layer
tags:
  - etl
  - nfl_data_py
  - sqlite
  - parquet
  - idempotency
requires:
  - .planning/phases/02-data-layer-etl-sqlite-schema/02-CONTEXT.md (D-05..D-16)
  - .planning/phases/02-data-layer-etl-sqlite-schema/02-01-SUMMARY.md (schema)
  - .planning/phases/01-foundation-ftn-pivot-calibration/01-CONTEXT.md (D-AUDIT)
  - .planning/REQUIREMENTS.md (ETL-01..06)
  - schema/01_create_tables.sql, 02_indexes.sql, 03_views.sql (Plan 02-01)
provides:
  - etl/__init__.py (package marker)
  - etl/columns.py (SSOT: SEASONS, PBP_KEYS, FTN_KEYS, PBP_COLUMNS, FTN_COLUMNS, FTN_RENAME, GAMES_COLUMNS, PLAYS_COLUMNS, FTN_PLAY_COLUMNS)
  - etl/load_pbp.py (per-year idempotent pbp loader, > 40_000 row floor)
  - etl/load_ftn.py (per-year idempotent FTN loader, > 38_000 row floor)
  - etl/build_db.py (join + DROP+CREATE + executescript + INSERT)
  - etl/run.py (zero-flag CLI: `python -m etl.run`)
  - data/nfl_defensive_tendencies.db (gitignored; recruiter regenerates)
affects:
  - All Phase 3 queries read from competitive_plays (105,556 rows; see Note 1 below)
  - Phase 4 / DOC-05 README setup block (`python -m etl.run` is one of 5 locked recruiter commands)
  - Phase 4 / SHIP-08 placeholder ship-guard (.db must remain gitignored)
tech-stack:
  added: []
  patterns:
    - "year-by-year idempotent parquet caching (skip-if-exists) for resilience to single-year network failures"
    - "validate='one_to_one' on the FTN <-> pbp merge (PITFALLS.md #3 mitigation)"
    - "DROP+CREATE on every build (D-09): same parquet -> same DB, deterministic"
    - "stdlib logging at INFO with format '%(asctime)s %(levelname)s %(message)s' (D-14)"
    - "fail-fast on network errors -- no retry/backoff (D-15); inline row-count asserts catch silent-empty-success (PITFALLS.md #17)"
    - "structured 6-line summary block at end-of-run (D-16) for recruiter glance-test"
key-files:
  created:
    - etl/__init__.py
    - etl/columns.py
    - etl/load_pbp.py
    - etl/load_ftn.py
    - etl/build_db.py
    - etl/run.py
  modified: []
decisions:
  - "match_rate semantic clarified: joined['play_type'].notna().mean() after pbp.merge(ftn, how='left') measures pbp's own play_type non-null rate (0.9705), not the FTN/pbp join coverage rate (0.9999) the Phase 1 audit reported. Both numbers exceed the 0.95 floor; the plan's CONTEXT specifics explicitly mandate this formula. Phase 3 / future maintainers must understand which number this is."
  - "competitive_plays view returns 105,556 rows on the verified Phase 1 dataset, NOT the > 130,000 the plan's Task 6 acceptance assumed. The 140,606 figure Phase 1 reported was pre-wp-filter (just play_type IN ('pass','run')). The locked D-04 predicate set (wp 0.05-0.95 + qtr<=4 + end-of-half hurry-up exclusion) trims the count by ~25%. View body is byte-exact to D-04 lock; threshold was miscalibrated."
  - "Windows runtime adjustments: scratch/etl_run_*.log instead of /tmp/; Python sqlite3 module instead of sqlite3 CLI (not on PATH on this machine); .venv/Scripts/python.exe used throughout (system python is 3.14, fails on nfl_data_py)."
metrics:
  duration: "~25m (including cold-cache pull)"
  completed: 2026-04-29
  task_commits: 5
  total_commits: 6
  cold_run_seconds: 36
  warm_run_seconds: 9
  end_to_end_games: 1139
  end_to_end_plays: 197362
  end_to_end_ftn_play: 185215
  end_to_end_match_rate: 0.9705
  end_to_end_competitive_plays: 105556
---

# Phase 2 Plan 02: ETL Pipeline (parquet + SQLite) Summary

Authored the six-file ETL pipeline that populates `data/nfl_defensive_tendencies.db` from `nfl_data_py` via a single recruiter-runnable command (`python -m etl.run`). The pipeline pulls 4 seasons (2022-2025) of pbp + FTN charting from the nflverse CDN year-by-year, caches to per-year parquet files (idempotent skip-if-exists), joins FTN to pbp with `validate='one_to_one'`, applies the three schema files from Plan 02-01, and writes the SQLite database. End-to-end cold-cache run completed in 36 seconds (well under the 10-minute ETL-06 budget); warm-cache idempotent re-run in 9 seconds.

## What Was Built

| File | Role | Lines | Key Constants / Behavior |
|------|------|-------|---------------------------|
| `etl/__init__.py` | Empty package marker | 0 | Lets `python -m etl.run` resolve `etl` as a package |
| `etl/columns.py` | SSOT for ETL configuration | 124 | `SEASONS=[2022,2023,2024,2025]`, `PBP_COLUMNS` (27), `FTN_COLUMNS` (10), `FTN_RENAME`, `PLAYS_COLUMNS` (24), `GAMES_COLUMNS` (6), `FTN_PLAY_COLUMNS` (10), `PBP_KEYS`, `FTN_KEYS` |
| `etl/load_pbp.py` | Per-year idempotent pbp loader | 52 | `load_pbp()` skips existing parquet; pulls one year at a time via `nfl.import_pbp_data([year], columns=PBP_COLUMNS, downcast=True)`; asserts `len(df) > 40_000` per year |
| `etl/load_ftn.py` | Per-year idempotent FTN loader | 51 | Mirror of `load_pbp.py`; threshold `> 38_000` (FTN charts ~46k/season) |
| `etl/build_db.py` | Read parquet -> join -> apply schema -> SQLite | 152 | `pbp.merge(ftn, left_on=PBP_KEYS, right_on=['nflverse_game_id','nflverse_play_id'], how='left', validate='one_to_one')`; asserts `match_rate > 0.95` AND `len(joined) > 130_000`; DROP+CREATEs `data/nfl_defensive_tendencies.db`; applies all three `schema/*.sql` files in order via `executescript`; inserts via `to_sql(if_exists='append', method='multi', chunksize=500)` |
| `etl/run.py` | Zero-flag CLI orchestrator | 55 | Configures `logging.basicConfig` with the D-14 format ONCE; calls `load_pbp -> load_ftn -> build_db`; emits the D-16 6-line summary block |

## End-to-End Run Actuals

Cold-cache run (clean state — `data/raw/` empty, no DB):

```
2026-04-29 23:10:31  INFO === ETL: nfl_defensive_tendencies ===
2026-04-29 23:10:39  INFO Wrote pbp_2022.parquet (49,434 rows)
2026-04-29 23:10:43  INFO Wrote pbp_2023.parquet (49,665 rows)
2026-04-29 23:10:47  INFO Wrote pbp_2024.parquet (49,492 rows)
2026-04-29 23:10:54  INFO Wrote pbp_2025.parquet (48,771 rows)
2026-04-29 23:10:55  INFO Wrote ftn_2022.parquet (41,643 rows)
2026-04-29 23:10:55  INFO Wrote ftn_2023.parquet (48,225 rows)
2026-04-29 23:10:56  INFO Wrote ftn_2024.parquet (48,031 rows)
2026-04-29 23:10:57  INFO Wrote ftn_2025.parquet (47,316 rows)
2026-04-29 23:10:58  INFO Loaded pbp: 197,362 rows from 4 parquet files
2026-04-29 23:10:58  INFO Loaded ftn: 185,215 rows from 4 parquet files
2026-04-29 23:10:58  INFO Joined: 197,362 rows, match_rate=0.9705
2026-04-29 23:11:07  INFO Database built: data/nfl_defensive_tendencies.db
                       games:                1,139 rows
                       plays:              197,362 rows
                       ftn_play:           185,215 rows
                       match_rate:          0.9705
                       competitive_plays:  105,556 rows
                       duration:            0m 36s
```

Warm-cache idempotency re-run (immediately after cold):

```
2026-04-29 23:12:21  INFO [skip] pbp_2022.parquet already cached
... 8 [skip] lines total ...
2026-04-29 23:12:22  INFO Removing existing data/nfl_defensive_tendencies.db (D-09: DROP+CREATE every invocation)
2026-04-29 23:12:31  INFO   duration:            0m 09s
```

Counts byte-stable across cold/warm runs (1,139 / 197,362 / 185,215 / 0.9705 / 105,556).

| Metric | Value | Threshold | Pass? |
|--------|-------|-----------|-------|
| games | 1,139 | > 800 | yes |
| plays | 197,362 | > 190,000 | yes |
| ftn_play | 185,215 | > 180,000 | yes |
| match_rate | 0.9705 | > 0.95 | yes (see Note 2) |
| competitive_plays | 105,556 | > 130,000 | **no** (see Note 1) |
| 5 named indexes present | yes | exact | yes |
| 1 view (competitive_plays) | yes | exact | yes |
| 3 tables (ftn_play, games, plays) | yes | exact | yes |
| Cold-cache duration | 0m 36s | < 10m | yes |
| Warm-cache duration | 0m 09s | < 5m | yes |
| Idempotency: only [skip] log lines on warm run | confirmed | required | yes |
| `git status --porcelain` excludes .db and parquet | empty | required | yes |

## Locked Invariants Honored

- **Join uses `validate='one_to_one'`** on `(nflverse_game_id, nflverse_play_id)` per PITFALLS.md #3. The merge raises `MergeError` if either side has duplicate keys; verified clean for the 4-season pull.
- **Match-rate calculation is exactly `joined['play_type'].notna().mean()`** per CONTEXT specifics (NOT the FTN-side key). See Note 2 below for the semantic interpretation.
- **DROP+CREATE on every invocation** (D-09): `DB_PATH.unlink()` runs unconditionally if the file exists. Same parquet input -> same DB, deterministic. Wiping a populated DB is harmless because parquet underneath is unchanged.
- **`competitive_plays` view body is byte-exact to D-04 lock** (Plan 02-01 SUMMARY confirmed; `executescript` of `schema/03_views.sql` reproduces the four predicates verbatim).
- **DB filename is `nfl_defensive_tendencies.db`** (NOT `nfl_coverage.db`) per ROADMAP success criterion 1 and CONTEXT D-10. The architecture doc's stale `nfl_coverage.db` reference was not propagated.
- **No `tests/` directory created.** Verification is inline assertions in the ETL plus the Task 6 acceptance script.
- **No modifications to `schema/`, `requirements.txt`, `pyproject.toml`, `.gitignore`, `STATE.md`, `ROADMAP.md`** during this plan. The locked stack from Phase 1 stands; Plan 02-01's schema files are read-only inputs.
- **Zero CLI flags on `etl/run.py`** per D-10. No argparse, no click, no sys.argv. Recruiter contract is exactly `python -m etl.run`.
- **Fail-fast on network errors** per D-15: no retry, no backoff, no tenacity dep. nfl_data_py exceptions bubble up; the year-by-year parquet cache means re-running picks up exactly where it left off.

## Notes & Deviations from Plan

### Note 1: `competitive_plays` count is 105,556, not the > 130,000 the plan assumed (Rule 1 -- plan-data calibration)

The plan's Task 6 acceptance criterion `competitive_plays > 130_000` was authored against Phase 1's reported count of 140,606 competitive plays. That Phase 1 figure (logged in STATE.md and PROJECT.md D-10) was measured as `play_type IN ('pass','run')` over the joined frame -- the simple two-predicate filter, NOT the full D-04 predicate stack.

The locked `competitive_plays` view (`schema/03_views.sql`) applies four predicates in sequence:

| Step | Predicate | Rows kept | Drops |
|------|-----------|-----------|-------|
| Total | -- | 197,362 | -- |
| 1 | `play_type IN ('pass','run')` | 140,708 | 56,654 (kickoffs, FGs, no_play, etc.) |
| 2 | + `wp BETWEEN 0.05 AND 0.95` | 119,787 | 20,921 (blowouts) |
| 3 | + `qtr <= 4` | 118,910 | 877 (OT plays) |
| 4 | + `NOT (qtr IN (2,4) AND half_seconds_remaining <= 120)` | **105,556** | 3,354 (end-of-half hurry-up) |

Phase 1's 140,606 stopped at step 1. The view's count of 105,556 is the correct outcome of applying the D-04 lock as written. The view definition is byte-exact to CONTEXT D-04; the threshold in the plan's acceptance criterion (`> 130_000`) was the wrong number.

**Action taken:** No code changes -- the view, the build, and the dataset are all correct. Documenting here so Phase 3 plans the situational queries against a 105,556-row competitive universe (not 140k). Phase 3 sample-size discipline (N>=30 / N>=100 tiered) is unaffected; the universe is large enough that the situational sub-samples remain comfortably within the discipline.

### Note 2: `match_rate=0.9705` is pbp's play_type non-null rate, NOT the FTN/pbp join coverage (Rule 1 -- semantic clarification)

The plan computes match_rate via `joined['play_type'].notna().mean()` where `joined = pbp.merge(ftn, how='left')`. Because pbp is the LEFT side of the merge, every pbp row is preserved -- and `play_type` is a pbp-side column. So `play_type` is NaN if and only if pbp's source data had play_type=None for that row (kickoffs, no_play rows, certain ST plays).

The Phase 1 audit (`analysis/00_data_audit.py` cell 4) computed match_rate the OTHER direction: `ftn.merge(pbp, how='left')`. There, pbp's `play_type` is NaN exactly when an FTN row had no pbp match -- the actual FTN/pbp join coverage rate, which Phase 1 measured as 0.9999.

The plan's CONTEXT specifics explicitly mandate the build_db formula and the merge direction (`pbp.merge(ftn)` to keep all pbp rows for plays-table population). Both numbers are >0.95, so the assertion fires correctly in either direction. The 0.9705 figure is the pbp-play_type-non-null rate over 197,362 pbp rows -- which is also a meaningful quality signal (it's the rate at which pbp rows have a parseable play classification, before any wp/situational filtering).

**Action taken:** Code matches the plan's literal action body; no change made. Documenting here so any future executor maintaining `etl/build_db.py` understands which match-rate semantic this is. If a future plan needs the actual FTN/pbp join coverage, that's a separate calculation against `joined['_merge'].eq('both')` after using `indicator=True`, or by reversing the merge.

### Note 3: Windows path adjustments (Rule 4 -- runtime detail recovery)

The plan was authored with POSIX-style path conventions. Three adjustments were applied during Task 6 verification:

1. **`/tmp/etl_run.log` -> `scratch/etl_run_cold.log` and `scratch/etl_run_warm.log`.** On Windows MINGW64, `/tmp/` resolves under `C:\Users\geoca\AppData\Local\Temp\` via the MSYS layer. Using a project-local `scratch/` path (which is gitignored per `.gitignore` line `scratch/`) keeps the logs visible to the executor for inspection without leaking into git.
2. **`sqlite3` CLI not on PATH.** The plan's Task 6 verify step calls `sqlite3 data/nfl_defensive_tendencies.db "..."`. The CLI is not installed on this machine. Replaced with `.venv/Scripts/python.exe -c "import sqlite3; ..."` invocations -- the Python sqlite3 module handles `COUNT(*)` queries identically to the CLI.
3. **`.venv/Scripts/python.exe` used throughout** instead of bare `python`. System `python` resolves to 3.14 on this Windows 11 machine, which fails on `nfl_data_py` (upstream issue #122 -- locked stack pins at 3.11). The `.venv` was created with `py -3.11 -m venv .venv` per Plan 01-01, and the two-step `nfl_data_py==0.3.3 --no-deps` install pattern is in place.

None of these adjustments touch the ETL code itself; they only affect the executor's verify-step shell commands. The recruiter contract `python -m etl.run` works identically on Windows with the `.venv` active and on POSIX systems via the same `python -m etl.run` invocation.

### Note 4: Minor docstring tensions with literal acceptance greps

Two minor mismatches between the plan's literal acceptance greps and the plan's prescribed docstring text:

1. `etl/load_pbp.py` and `etl/load_ftn.py` docstrings contain the literal string "retry-with-backoff" in the explanation of D-15 fail-fast posture ("no retry-with-backoff"). The plan's acceptance criterion says `grep -E "tenacity|retry|backoff" etl/load_pbp.py` does NOT match. The docstring text is verbatim from the plan's `<action>` block. The substantive intent (no actual retry logic, no tenacity import, no `@retry` decorator, no while-loop with backoff) is satisfied -- the prose just discusses the absence of those things. No change made.
2. `etl/build_db.py` docstring contains the literal string `nfl_coverage.db` in the explanation of D-10 ("DB filename is nfl_defensive_tendencies.db (NOT nfl_coverage.db -- the architecture doc still references the old name)"). The plan's acceptance criterion says `! grep -E "nfl_coverage\.db" etl/build_db.py`. The docstring text is verbatim from the plan. The substantive intent (the DB_PATH constant points to `nfl_defensive_tendencies.db`) is satisfied: line 34 reads `DB_PATH = Path("data/nfl_defensive_tendencies.db")`. No change made.

Both docstring fragments serve a regression-prevention purpose -- naming the deprecated label so a future reader doesn't backslide. If the over-broad greps cause issues for an automated check in a future phase, the docstrings could be reworded ("the deprecated coverage-era label" instead of `nfl_coverage.db`) without behavioral change. Not action-required for this plan.

## Plan 02-02 Handoff to Phase 3

Phase 3 plans (analytical SQL + Python notebooks) consume:

```python
import sqlite3
conn = sqlite3.connect("data/nfl_defensive_tendencies.db")
# Every analytical query reads from competitive_plays:
df = pd.read_sql("SELECT * FROM competitive_plays WHERE down=3 AND ydstogo>=7", conn)
```

| Phase 3 expectation | Confirmed value |
|---|---|
| `competitive_plays` row count | **105,556** (NOT 140,606 -- see Note 1) |
| `plays` row count | 197,362 |
| `ftn_play` row count | 185,215 |
| Joining plays + ftn_play on (game_id, play_id) | 1:1 inner join, 185,215 rows expected |
| Indexes available for situational queries | `idx_plays_situation`, `idx_plays_defteam_season`, `idx_plays_play_type` |
| Indexes on FTN aggregations | `idx_ftn_n_pass_rushers`, `idx_ftn_n_blitzers` |
| Composite PK on plays/ftn_play | `(game_id, play_id)` -- implicit autoindex |

The four pre-registered situations from Phase 1 D-AUDIT (S1 3rd-and-long, S2 red zone, S3 1st-and-10, S4 2nd-and-medium) all resolve cleanly against `competitive_plays` -- verified during Task 6 acceptance via spot-check queries (not committed; Phase 3 will commit the actual queries to `queries/`).

The data layer is locked. Phase 3 modifies neither this ETL nor the schema files.

## Commits (this plan)

| Task | Commit | Message |
|------|--------|---------|
| 1 | `74f740d` | `feat(02-02): etl/columns.py -- SSOT for SEASONS, whitelists, join keys` |
| 2 | `7daab03` | `feat(02-02): etl/load_pbp.py -- per-year idempotent pbp parquet loader` |
| 3 | `f1dadac` | `feat(02-02): etl/load_ftn.py -- per-year idempotent FTN parquet loader` |
| 4 | `884fde8` | `feat(02-02): etl/build_db.py -- join FTN<->pbp and write SQLite` |
| 5 | `9a366af` | `feat(02-02): etl/run.py -- zero-flag CLI orchestrator + D-16 summary log` |
| 6 + summary | (pending) | `chore(02-02): end-to-end build verified -- 1139 games / 197362 plays / 185215 ftn_play / 105556 competitive (cold 0m36s, warm 0m09s) + summary` |

## Self-Check: PASSED

- `etl/__init__.py` -- FOUND (commit `74f740d`)
- `etl/columns.py` -- FOUND (commit `74f740d`)
- `etl/load_pbp.py` -- FOUND (commit `7daab03`)
- `etl/load_ftn.py` -- FOUND (commit `f1dadac`)
- `etl/build_db.py` -- FOUND (commit `884fde8`)
- `etl/run.py` -- FOUND (commit `9a366af`)
- `data/nfl_defensive_tendencies.db` -- present on disk; gitignored (`git check-ignore` confirms)
- All 4 pbp parquet + 4 FTN parquet present in `data/raw/`; gitignored
- All five commit hashes appear in `git log --oneline`
- `git status --porcelain` returns empty (no leaked artifacts)
- `ruff check etl/` -- 0 errors
- All 6 ETL files lint clean
- No files written outside `etl/` (and the gitignored `data/` and `scratch/`)
- No `tests/` directory created
- No modifications to `schema/`, `requirements.txt`, `pyproject.toml`, `.gitignore`, `.python-version`, `STATE.md`, `ROADMAP.md`
