# Phase 2: Data Layer (ETL + SQLite Schema) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 02-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 02-data-layer-etl-sqlite-schema
**Areas discussed:** competitive_plays predicates, plays whitelist + denormalization, ETL CLI + idempotency, runtime UX (progress + assertions)

---

## Gray-Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| competitive_plays predicates | Beyond ROADMAP's `play_type IN ('pass','run')` AND `wp BETWEEN 0.05 AND 0.95` AND OT-exclusion AND 2-min-drill exclusion, lock the exact predicate set since this view is the SSOT for every Phase 3 query. | ✓ |
| plays column whitelist + season denormalization | Minimal ~20 cols (strict 3NF) vs pragmatic ~30 cols with season/week denormalized so the locked `(defteam, season)` index fires. Drives DB size and query speed. | ✓ |
| etl.run CLI ergonomics + idempotency | Zero-arg vs `--force` / `--years` flags; on re-run does build_db DROP+CREATE or skip if DB exists. | ✓ |
| Progress reporting + assertion strategy | tqdm vs stdlib logging vs print; assertions inline in build_db.py vs separate `_validators.py`. | ✓ |

**User's choice:** All 4 areas selected.

---

## Area 1: competitive_plays predicates

### Q1: Q4 crunch time (last 5 min of regulation)

| Option | Description | Selected |
|--------|-------------|----------|
| Include crunch time | Keep `qtr=4 AND half_seconds_remaining<300` IN. WP filter already drops blowouts; competitive Q4 is exactly where coordinator tendency matters most. PITFALLS #6 lists this exclusion as optional. | ✓ |
| Exclude crunch time | Drop `qtr=4 AND half_seconds_remaining<300`. Cleaner "normal-flow" signal but discards real S1/S4 plays; loses ~8-12% of competitive sample. | |

**User's choice:** Include crunch time (Recommended).

### Q2: 2-minute drill cutoff

| Option | Description | Selected |
|--------|-------------|----------|
| Drop end-of-half only | `NOT (qtr IN (2,4) AND half_seconds_remaining <= 120)`. Matches PITFALLS #6 default; preserves Q1/Q3 hurry-up-adjacent plays where game state is irrelevant. | ✓ |
| Drop entire 2-min warning window | `half_seconds_remaining > 120` regardless of quarter. Slightly cleaner but drops 1H-end plays where game state doesn't matter. | |
| Use `qb_kneel`/`qb_spike` flag instead | Skip seconds-based filter; rely on `play_type` already excluding kneels/spikes. Less surgical — leaves clock-burn pass attempts in. | |

**User's choice:** Drop end-of-half only (Recommended).

### Q3: View materialization

| Option | Description | Selected |
|--------|-------------|----------|
| SQL VIEW | `CREATE VIEW competitive_plays AS SELECT ...`. Defined in `schema/03_views.sql`, no storage cost, always reflects underlying data. | ✓ |
| Materialized table | `CREATE TABLE competitive_plays AS SELECT ...` rebuilt by build_db. Adds ~30 MB, slightly faster queries. Adds rebuild step. | |

**User's choice:** SQL VIEW (Recommended).

### Q4: Strict play-attempt enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| play_type only | `play_type IN ('pass','run')` is sufficient — already excludes no_play, kneels, spikes, ST. Sacks count as pass (correct for blitz analysis). | ✓ |
| Require attempt flags too | `(play_type='pass' AND pass_attempt=1) OR (play_type='run' AND rush_attempt=1)`. Stricter but loses sacks. PITFALLS #7 flags this as nuanced. | |

**User's choice:** play_type only (Recommended).

**Notes:** All four Area-1 picks accepted the recommended option. The locked view definition is reified in 02-CONTEXT.md §D-04.

---

## Area 2: plays column whitelist + season denormalization

### Q1: Denormalize season/week onto plays?

| Option | Description | Selected |
|--------|-------------|----------|
| Denormalize | Adds 2 cols, ~2-3 MB. Required for SCHEMA-02's `(defteam, season)` index to fire without a 3-way join. Universal nflfastR analysis convention. | ✓ |
| Strict 3NF | Cleaner normalization; index moves to games-side or changes shape. Every query becomes a 3-way join. | |

**User's choice:** Denormalize (Recommended).

### Q2: plays column scope

| Option | Description | Selected |
|--------|-------------|----------|
| Tendency-minimum ~18 cols | Identity + teams + situation + time + classification + outcome + filter. ~25 MB. Hits every pre-registered situation + STAT-08 sensitivity. | |
| Broader ~24 cols | Adds pass_attempt, rush_attempt, cpoe, xpass, success, air_yards. Useful for STAT-08 sensitivity richness and analytical depth. ~32 MB. | ✓ |
| Full pbp ~50 cols | Most of nflfastR's ~370 cols. Recruiter risk: looks unfocused. | |

**User's choice:** Broader ~24 cols. Locked column set in 02-CONTEXT.md §D-06.

### Q3: REG vs REG+POST

| Option | Description | Selected |
|--------|-------------|----------|
| REG + POST, season_type on games | Matches PROJECT.md "four seasons through Super Bowl LX" framing; STATE.md row totals already include POST. | ✓ |
| REG only | Simpler, ~6% smaller. But STATE.md totals would need revising and PROJECT.md framing becomes inaccurate. | |

**User's choice:** REG + POST (Recommended).

### Q4: games table scope

| Option | Description | Selected |
|--------|-------------|----------|
| Identity-only ~6 cols | game_id PK, season, week, season_type, home_team, away_team. Matches ARCHITECTURE.md. | ✓ |
| Add final scores | home_score, away_score, total, result. Tendency analysis is per-snap, not per-game outcome. | |

**User's choice:** Identity-only (Recommended).

**Notes:** Q1, Q3, Q4 took the recommendation. Q2 took the slightly-wider option, trading ~7 MB of DB size for richer Phase 3 / STAT-08 sensitivity-check material (pass_attempt, rush_attempt) and analytical depth (cpoe, xpass, success, air_yards).

---

## Area 3: etl.run CLI ergonomics + idempotency

### Q1: Re-run behavior when DB exists

| Option | Description | Selected |
|--------|-------------|----------|
| Always rebuild from parquet | DROP+CREATE every time. Parquet cache prevents re-downloads. Deterministic; no flag. | ✓ |
| Skip if DB exists, require --force | Defensive, but wiping is harmless because parquet is the source of truth. Adds a flag. | |
| Detect parquet mtime, rebuild if changed | Smart but adds state-comparison logic. Probably over-engineered. | |

**User's choice:** Always rebuild (Recommended).

### Q2: CLI flag surface

| Option | Description | Selected |
|--------|-------------|----------|
| Zero flags | `python -m etl.run` only. Years constant in `etl/columns.py`. One command, one behavior. | ✓ |
| `--force` only | One escape hatch — re-pull parquet from nfl_data_py even if cached. | |
| Full argparse | --years, --force, --seasons-from. Configurable, but recruiter-facing simplicity erodes. | |

**User's choice:** Zero flags (Recommended).

### Q3: Multi-year pull strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Year-by-year loop, idempotent per year | Skip if `data/raw/pbp_{year}.parquet` exists, else pull that year only. ARCHITECTURE.md Pattern 1. Resilient to partial failures. | ✓ |
| Single batched pull | `nfl.import_pbp_data([2022,2023,2024,2025])` once. Slightly faster but partial-failure means starting over. | |

**User's choice:** Year-by-year loop (Recommended).

### Q4: Where assertions live

| Option | Description | Selected |
|--------|-------------|----------|
| Inline in build_db.py with `assert` | Plain assert statements. Fail-loud: AssertionError stops build, exits non-zero, fails CI. Recruiter-readable. Matches PITFALLS #17 + ETL-04 language. | ✓ |
| Separate `etl/_validators.py` | Reusable validators. Cleaner separation but extra file for ~10 lines. | |

**User's choice:** Inline assert (Recommended).

**Notes:** All four Area-3 picks took the recommendation. Per-year row-count assertions go in `load_pbp.py` / `load_ftn.py`; FTN↔pbp match-rate + post-join row-count assertions go in `build_db.py`. Concrete thresholds in 02-CONTEXT.md §Specifics.

---

## Area 4: Progress reporting + assertion strategy

### Q1: Progress reporting library

| Option | Description | Selected |
|--------|-------------|----------|
| stdlib `logging` at INFO | No new deps. Per-stage one-liners. nfl_data_py shows tqdm internally on the slow part. | ✓ |
| Plain `print()` | Even simpler, no formatter. But mixes with nfl_data_py's tqdm output. | |
| Add `tqdm` to requirements | Native progress bars. New runtime dep (tqdm is transitively pulled by nfl_data_py — technically free). ETL stages are mostly fast except network. | |

**User's choice:** stdlib logging at INFO (Recommended).

### Q2: Log format

| Option | Description | Selected |
|--------|-------------|----------|
| Timestamp + level | `2026-04-29 14:32:18 INFO Pulling pbp 2022...`. Standard professional Python; recruiter-grep-friendly. | ✓ |
| Bare one-liner | `Pulling pbp 2022...`. Cleaner output but no temporal info; harder to diagnose slow stage. | |

**User's choice:** Timestamp + level (Recommended).

### Q3: Network failure handling

| Option | Description | Selected |
|--------|-------------|----------|
| Fail-fast — propagate exception | Exception bubbles up, recruiter re-runs (parquet cache may already have prior years). Row-count assertion catches PITFALLS #17 silent-empty-success. | ✓ |
| Retry with exponential backoff | 3 retries with `time.sleep(2**n)`. Resilient but adds code/dep. PITFALLS #17 risk is silent success on empty result, which retry doesn't address. | |

**User's choice:** Fail-fast (Recommended).

### Q4: Final summary at end of etl.run

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — multi-line summary block | Structured summary log (DB path, table row counts, match rate, competitive_plays count, duration). Recruiter glance-test confirms clean build. | ✓ |
| No — exit 0 silently | Last log line is whatever build_db emitted. Cleaner but no glance-test confirmation. | |

**User's choice:** Multi-line summary (Recommended). Exact format reified in 02-CONTEXT.md §D-16.

**Notes:** All four Area-4 picks took the recommendation.

---

## Claude's Discretion

None — all 16 decisions across the 4 areas were made by the user (16-for-16 took the recommended option except for Area 2 / Q2 where the user picked the slightly-wider whitelist over the tendency-minimum). No "you decide" deferrals.

---

## Deferred Ideas

Captured in 02-CONTEXT.md §`<deferred>`:
- Sample DB quickstart (`data/sample.db`)
- `etl_metadata` table tracking pull date / source library version
- Materialized `competitive_plays` table
- `--force` / `--years` / `--no-cache` CLI flags
- Network retry-with-backoff
- Sensitivity-check `all_plays` view
- Schema FK enforcement pragma
- Parquet write tuning (compression / row groups)
