# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-29)

**Core value:** A recruiter can clone the repo, run a single command, and within 2 minutes understand both the analytical insight and the engineering rigor behind it.
**Current focus:** Phase 1 — Foundation & FTN Pivot Calibration

## Current Position

Phase: 1 of 4 (Foundation & FTN Pivot Calibration)
Plan: 1 of 2 in current phase
Status: Plan 01-01 (Bootstrap) complete — ready to execute Plan 01-02 (FTN Audit)
Last activity: 2026-04-29 — Plan 01-01 executed (BOOT-01..07 complete; locked stack verified on fresh Python 3.11 venv)

Progress: [█░░░░░░░░░] 13%

## Performance Metrics

**Velocity:**
- Total plans completed: 1
- Average duration: 10m
- Total execution time: 10m

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Foundation & FTN Pivot Calibration | 1 / 2 | 10m | 10m |
| 2. Data Layer (ETL + Schema) | 0 | — | — |
| 3. Analytical Layer (SQL + Python) | 0 | — | — |
| 4. Story & Ship | 0 | — | — |

**Recent Trend:**
- Last 5 plans: 01-01 Bootstrap (10m, 3 task commits, 2 deviations auto-fixed)
- Trend: on-pace; in-phase parallelism deferred (this was the serial bootstrap)

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Phase 1 = pivot calibration, not blank-slate audit (researchers have already confirmed the FTN public schema; Phase 1 measures NaN rates and locks 3–4 anchor dimensions)
- Public repo name decided at end of Phase 1 (likely `nfl-defensive-tendencies`); working folder stays `nfl-coverage-tendencies` for git history continuity
- Coarse phase granularity adopted: 4 phases (synthesizer's 6-phase prior consolidated; rationale in ROADMAP.md Overview)
- `competitive_plays` SQL view is a Phase 2 SCHEMA deliverable (single source of truth for play-type and win-probability filtering across all analytical queries)
- Predictability score normalization (`H/log(k)` over fixed support OR KL-from-baseline) MUST be the FIRST cell of `02_predictability_modeling.ipynb` (Phase 3)
- Ship via GitHub MCP (Phase 4): repo creation, topic config, social preview, pinning all use GitHub MCP tools — not manual `git push`
- **`nfl_data_py` two-step install pattern is the standard nflverse-community workaround** (Plan 01-01): upstream `0.3.3` metadata declares `pandas<2.0` which conflicts with our locked `pandas>=2.1,<2.3`. Install non-`nfl_data_py` deps first with strict resolver, then `nfl_data_py==0.3.3 --no-deps` (plus `appdirs>1`, `fastparquet>0.5`). Pin block stays as researched; install procedure adapts. Phase 4 / DOC-05 README setup block and SHIP-02 fresh-venv script MUST encode this.
- **Windows Python 3.11 launcher dispatch** (Plan 01-01): system `python` resolves to 3.14 by default on Windows 11; use `py -3.11` for venv creation. Cross-platform docs should reference `python3.11` or `py -3.11` (Windows) explicitly.

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Deferred Items

Items acknowledged and carried forward (v2 backlog from REQUIREMENTS.md):

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Library | V2-LIB-01: migrate from `nfl_data_py` to `nflreadpy` | Deferred to v2 | Roadmap creation |
| Library | V2-LIB-02: re-pin `numpy>=2.0` post-migration | Deferred to v2 | Roadmap creation |
| Analysis | V2-PERS-01: add personnel-grouping context | Deferred to v2 | Roadmap creation |
| Analysis | V2-ML-01: simple defensive-tendency classifier | Deferred to v2 | Roadmap creation |
| Viz | V2-VIZ-01: animated play visualization (if tracking data appears) | Deferred to v2 | Roadmap creation |
| Docs | V2-DOC-01: inter-rater agreement on FTN subjective fields | Deferred to v2 | Roadmap creation |
| Docs | V2-DOC-02: custom hero-chart social preview iteration | Deferred to v2 | Roadmap creation |

## Session Continuity

Last session: 2026-04-29
Stopped at: Plan 01-01 (Bootstrap) executed cleanly — 3 task commits + SUMMARY (`36e1c5c` config files, `520cde0` directory tree + README skeleton, `496fac2` BOOT-07 verification). Locked stack verified on fresh Python 3.11.9 venv.
Resume file: .planning/phases/01-foundation-ftn-pivot-calibration/01-02-PLAN.md — ready for Plan 01-02 (FTN Audit) execution.
