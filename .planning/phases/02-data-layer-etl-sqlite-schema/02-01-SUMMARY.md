---
phase: 02-data-layer-etl-sqlite-schema
plan: 01
subsystem: data-layer
tags:
  - sqlite
  - schema
  - ddl
  - competitive_plays
requires:
  - .planning/phases/02-data-layer-etl-sqlite-schema/02-CONTEXT.md (D-01..D-08)
  - .planning/REQUIREMENTS.md (SCHEMA-01, SCHEMA-02, SCHEMA-03)
  - .planning/research/ARCHITECTURE.md (Schema Design + Indexing Strategy)
provides:
  - schema/01_create_tables.sql (3 tables: games, plays, ftn_play)
  - schema/02_indexes.sql (5 named composite/single indexes)
  - schema/03_views.sql (competitive_plays view, project-wide SSOT)
affects:
  - Plan 02-02 (etl/build_db.py) consumes these three files via Path(...).read_text() + executescript()
  - All Phase 3 queries read from competitive_plays
tech-stack:
  added: []
  patterns:
    - "static SQL DDL applied via sqlite3.executescript()"
    - "PRIMARY KEY (game_id, play_id) composite on plays AND ftn_play"
    - "denormalize season + week onto plays (D-05) so situational queries skip a join"
    - "INTEGER 0/1 for is_* booleans (SQLite has no native BOOL)"
    - "TEXT for qb_location ('U'/'S'/'P') -- not lookup-tableized"
    - "competitive_plays as a VIEW, not a materialized table (D-03)"
key-files:
  created:
    - schema/01_create_tables.sql
    - schema/02_indexes.sql
    - schema/03_views.sql
  modified: []
decisions:
  - "competitive_plays predicate set transcribed verbatim from 02-CONTEXT.md D-04 closing block"
  - "FTN whitelist locked at exactly 8 charting columns per Phase 1 D-AUDIT"
  - "Five indexes only -- no over-indexing at this scale per ARCHITECTURE.md"
  - "FOREIGN KEY clauses are documentation-only (PRAGMA foreign_keys left OFF per CONTEXT Deferred)"
metrics:
  duration: "~10m"
  completed: 2026-04-29
  task_commits: 3
  total_commits: 4
  lines_of_sql: 114
---

# Phase 2 Plan 01: SQLite Schema (Tables, Indexes, competitive_plays View) Summary

Authored the three static SQL DDL files that lock the project-wide data layer: `schema/01_create_tables.sql` (games, plays, ftn_play with composite PKs and the season/week denormalization that makes `(defteam, season)` indexable), `schema/02_indexes.sql` (five composite/single indexes targeting the dominant Phase 3 query shape), and `schema/03_views.sql` (the `competitive_plays` view transcribed verbatim from 02-CONTEXT.md D-04). All three files apply cleanly in sequence against an empty in-memory SQLite database. Plan 02-02 can now consume them via `Path("schema/<file>").read_text()` + `executescript()`.

## What Was Built

| File | Object Count | Key Invariants |
|------|--------------|----------------|
| `schema/01_create_tables.sql` | 3 tables | `games` (6 cols, identity-only); `plays` (24 cols incl. season/week/half_seconds_remaining/wp); `ftn_play` (10 cols = 2 PK + 8 FTN charting); composite PK `(game_id, play_id)` on both `plays` and `ftn_play` |
| `schema/02_indexes.sql` | 5 indexes | `idx_plays_situation (down, ydstogo, yardline_100)`; `idx_plays_defteam_season`; `idx_plays_play_type`; `idx_ftn_n_pass_rushers`; `idx_ftn_n_blitzers` |
| `schema/03_views.sql` | 1 view | `competitive_plays`: `play_type IN ('pass','run')` AND `wp BETWEEN 0.05 AND 0.95` AND `qtr <= 4` AND `NOT (qtr IN (2,4) AND half_seconds_remaining <= 120)` |

## Locked Invariants Honored

- **`competitive_plays` view body is byte-exact to 02-CONTEXT.md D-04 closing block.** The four predicates appear verbatim in `schema/03_views.sql` lines 18–21. Acceptance criteria assert each one with grep; the view's own `executescript` apply against an empty `plays` table returns 0 rows (queryable, parses against the real schema).
- **`season` and `week` are denormalized onto `plays`** (D-05). Verified end-to-end by `idx_plays_defteam_season` applying cleanly: that composite cannot exist if `season` lives only on `games`. Phase 3 situational queries skip the 3-way join through `games`.
- **FTN whitelist is exactly the 8 charting columns** that survived Phase 1's 30% NaN cutoff (D-AUDIT): `n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`. NOT the broader 28-column FTN frame. The PK pair `(game_id, play_id)` brings `ftn_play` to exactly 10 columns.
- **`qb_location` is TEXT, not INTEGER.** FTN ships character codes (`'U'` under-center, `'S'` shotgun, `'P'` pistol). No lookup-tableization for 3 distinct values.
- **`is_*` booleans store as INTEGER 0/1.** SQLite has no native BOOL; the standard SQLite idiom `WHERE is_play_action = 1` is what Phase 3 queries will use.
- **Five indexes only** — no over-indexing at this scale (~197k plays). PK indexes on `(game_id, play_id)` are implicit on both `plays` and `ftn_play` and are not re-declared.
- **No `pass_attempt` / `rush_attempt` predicate in the view.** D-04 explicitly rejects the strict-attempt mode because sacks (`play_type='pass'`) are meaningful for blitz analysis and would be silently dropped (PITFALLS.md #7).

## Verification Results

End-to-end combined-apply against an empty in-memory SQLite database (all three files in sequence):

```
tables:  ['ftn_play', 'games', 'plays']
indexes: ['idx_ftn_n_blitzers', 'idx_ftn_n_pass_rushers',
          'idx_plays_defteam_season', 'idx_plays_play_type',
          'idx_plays_situation']
views:   ['competitive_plays']
SELECT COUNT(*) FROM competitive_plays  -> 0   (empty base; view is queryable)
```

Per-task `<verify>` blocks all returned `OK`:

| Task | Verify Output |
|------|---------------|
| 1 | `OK` — three tables present; `plays` carries season/week/half_seconds_remaining/wp |
| 2 | `OK` — five named indexes present; PK indexes correctly excluded |
| 3 | `OK` — `competitive_plays` view present; queryable; no attempt-mode substring in file |

## Deviations from Plan

**1. [Rule 3 — Blocking] Reworded D-04 explanatory comment in `schema/03_views.sql` to avoid `pass_attempt` / `rush_attempt` substrings.**
- **Found during:** Task 3 verify
- **Issue:** Task 3's `<verify>` block asserts `'pass_attempt' not in sql and 'rush_attempt' not in sql` over the entire file text. The plan's `<action>` block transcribed the column names into the comment header explaining D-04 ("strict pass_attempt/rush_attempt mode would silently drop them"). The literal substrings appeared in the comment, failing the verify.
- **Fix:** Rewrote the comment fragment as "strict attempt-mode classification would silently drop them" — semantically identical, no behavioral change, no change to the view body. The view body itself was already verbatim from D-04 closing.
- **Files modified:** `schema/03_views.sql` (comment lines 8–10 only; CREATE VIEW body untouched)
- **Commit:** `21d29c4` (the fix landed in the same commit as the file's initial creation; the rewording happened before the first commit of this file)
- **Why this isn't a D-04 violation:** D-04 lock is on the predicate set in the view's WHERE clause, not on prose in a comment header. The four predicates remain byte-exact verbatim. The acceptance criteria for the predicates (each grepped individually) all match.

No other deviations. The schema and indexes files match the plan's action blocks exactly. Comment-header wording inside the SQL files is non-functional executor latitude (per the plan's `<output>` block, which explicitly calls these out as expected judgment calls).

## Plan 02-02 Handoff

Plan 02-02 (`etl/build_db.py`) can now consume:

```python
import sqlite3, pathlib
conn = sqlite3.connect("data/nfl_defensive_tendencies.db")
conn.executescript(pathlib.Path("schema/01_create_tables.sql").read_text())
conn.executescript(pathlib.Path("schema/02_indexes.sql").read_text())
conn.executescript(pathlib.Path("schema/03_views.sql").read_text())
```

Order matters: tables before indexes (indexes target columns); tables before view (the view's `SELECT * FROM plays` requires `plays` to exist). The combined-apply gate above proves the order works; Plan 02-02's DROP+CREATE-on-every-run idiom (D-09) means each invocation walks all three files in this exact sequence.

The schema is locked. Plan 02-02 modifies neither this DDL nor the view predicate set.

## Self-Check: PASSED

- `schema/01_create_tables.sql` — FOUND (`feat(02-01)` commit `e340291`)
- `schema/02_indexes.sql` — FOUND (`feat(02-01)` commit `cca0010`)
- `schema/03_views.sql` — FOUND (`feat(02-01)` commit `21d29c4`)
- All three commits visible in `git log --oneline`
- Combined-apply gate (3 tables + 5 indexes + 1 view) passes
- No files written outside `schema/`
- No `tests/` directory created
- No modifications to `etl/`, `requirements.txt`, `pyproject.toml`, STATE.md, or ROADMAP.md
