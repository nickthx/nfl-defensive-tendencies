# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-29)

**Core value:** A recruiter can clone the repo, run a single command, and within 2 minutes understand both the analytical insight and the engineering rigor behind it.
**Current focus:** Phase 1 — Foundation & FTN Pivot Calibration

## Current Position

Phase: 1 of 4 (Foundation & FTN Pivot Calibration) — COMPLETE
Plan: 2 of 2 in Phase 1 — COMPLETE; ready to execute Plan 02-01 (Schema) and Plan 02-02 (ETL) in Phase 2
Status: Phase 1 complete — all 14 requirements (BOOT-01..07 + AUDIT-01..07) met
Last activity: 2026-04-29 — Plan 01-02 executed (AUDIT-01..07 complete; 4 anchor dimensions locked; 4 situations pre-registered; D-09 repo name locked; PROJECT.md pandas pin aligned)

Progress: [██░░░░░░░░] 25%

## Performance Metrics

**Velocity:**
- Total plans completed: 2
- Average duration: 17.5m
- Total execution time: 35m

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Foundation & FTN Pivot Calibration | 2 / 2 (COMPLETE) | 35m | 17.5m |
| 2. Data Layer (ETL + Schema) | 0 | — | — |
| 3. Analytical Layer (SQL + Python) | 0 | — | — |
| 4. Story & Ship | 0 | — | — |

**Recent Trend:**
- Last 5 plans: 01-01 Bootstrap (10m, 3 task commits, 2 deviations auto-fixed); 01-02 FTN Audit (25m, 3 task commits, 0 Rule-1/2/3 deviations, 1 setup-procedure reapplication, 2 documented findings flagged for v2)
- Trend: on-pace; Phase 1 closed cleanly with all 14 requirements met

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
- **D-09 public GitHub repo name locked: `nfl-defensive-tendencies`** (Plan 01-02). Working folder stays `nfl-coverage-tendencies` for git history continuity. Phase 4 / SHIP-03 GitHub MCP repo creation uses `nfl-defensive-tendencies`.
- **4 anchor defensive dimensions locked** (Plan 01-02 / AUDIT-03): `n_blitzers` (pressure, S1 + S4 lead), `n_pass_rushers` (pressure, S2 lead), `is_play_action` (cross-cutting D-07 modifier), `n_offense_backfield` (personnel, S3 + S4). All 8 candidates survived the 30% NaN cutoff; selection became editorial (D-01 story tiebreaker).
- **4 pre-registered situations locked** (Plan 01-02 / AUDIT-04, `docs/analysis-plan.md`): S1 3rd-and-long (`down=3 AND ydstogo>=7`), S2 red zone (`yardline_100<=20`), S3 1st-and-10 (`down=1 AND ydstogo=10`), S4 2nd-and-medium (`down=2 AND ydstogo BETWEEN 3 AND 6`). FINDINGS.md headline insights firewalled to these 4.
- **FTN<->pbp match rate observed 0.9998** (Plan 01-02). Phase 2 ETL-04 keeps the > 0.95 floor; observed value gives ~5pp of headroom.
- **PROJECT.md pandas pin aligned** (Plan 01-02 / Pitfall #20 prevention): stale `pandas>=2.2,<2.4` corrected to `pandas>=2.1,<2.3`. PROJECT.md, requirements.txt, SUMMARY.md, PATTERNS.md now agree.
- **v2 candidate flagged**: pbp now exposes ngs-derived `defense_coverage_type` (0.025 NaN on pass) and `defense_man_zone_type` (0.023 NaN on pass) at populated rates. v1 stays as locked because pivot decision is in writing (D-09); using these would re-open the man-zone framing the project deliberately stepped away from. Documented in `docs/ftn-schema-audit.md`.

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
Stopped at: Plan 01-02 (FTN Audit) executed cleanly — 3 task commits + SUMMARY (`ba1f131` audit notebook + null profile + schema-audit narrative, `c8ddff3` pre-registered analysis plan, `64219fb` D-09 lock + pandas pin fix + SPEC reframe + README hook fill). FTN<->pbp match rate observed 0.9998 across 137,899 rows. **Phase 1 complete.**
Resume file: .planning/phases/02-data-layer-etl-schema/02-01-PLAN.md — ready for Phase 2 planning (Plan 02-01 Schema and Plan 02-02 ETL); run `/gsd-plan-phase 2` to generate the plans.
