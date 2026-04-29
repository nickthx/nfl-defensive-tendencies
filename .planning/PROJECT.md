# NFL Defensive Coverage Tendencies

## What This Is

A public, portfolio-grade data analytics project that examines how NFL defenses deploy coverage (and broader scheme) tendencies situationally — using `nfl_data_py` FTN charting + nflfastR play-by-play for the 2022–2024 seasons. Audience: data-analyst recruiters and sports-analytics teams reviewing entry-level applicants. The deliverable is a public GitHub repo with a reproducible Python+SQLite ETL, ~8 SQL analyses, Jupyter notebooks, and an analyst-memo-style FINDINGS.md.

## Core Value

A recruiter can clone the repo, run a single command, and within 2 minutes understand both the analytical insight and the engineering rigor behind it.

Everything else (depth of statistical work, breadth of business questions, sophistication of the predictability score) is downstream of that one experience working.

## Requirements

### Validated

(None yet — ship to validate)

### Active

<!-- Hypotheses until shipped. Detailed REQ-IDs live in REQUIREMENTS.md. -->

- [ ] FTN schema audit confirms (or invalidates) coverage-label availability before any ETL design
- [ ] Reproducible ETL pipeline pulls FTN + nflfastR via `nfl_data_py` and lands SQLite
- [ ] Normalized SQLite schema joining FTN + nflfastR at the play level
- [ ] 8–10 SQL analysis queries answering the situational tendency questions
- [ ] Python notebooks with at least one statistical test (chi-square) and an entropy-based predictability score
- [ ] FINDINGS.md memo with 5–7 insights and embedded static charts (PNGs)
- [ ] README that conveys the project's value in under 90 seconds
- [ ] Public GitHub repo created via the GitHub MCP at ship time

### Out of Scope

- **Streamlit / web dashboard** — adds deployment overhead without improving recruiter signal for this analytical project; static notebook + memo conveys the same skills more cleanly.
- **Big Data Bowl tracking data + Kaggle dependency** — replaced by FTN via `nfl_data_py`; eliminates manual download friction.
- **Postgres / DuckDB / Docker / cloud DB** — SQLite is sufficient and zero-friction for a recruiter clone-and-run.
- **Play-call prediction model** — scope creep; tendency analysis is the ceiling for v1.
- **Betting / wagering angle** — keep the tone analytical, not speculative.
- **Real-time / in-season auto-updating** — static analysis on fixed seasons.
- **PFF or other paid data** — not redistributable in a public portfolio repo.
- **Video / film breakdown** — out of scope for a tabular-data project.

## Context

**Author profile:** This is one of Nick's portfolio pieces aimed at entry-level data-analyst roles, distinct from his Whitflow lead-gen automation work. Audience is non-football, non-domain recruiters — README and FINDINGS.md must convey value without assuming NFL knowledge.

**Data shape (assumed, to be verified):**
- `nfl_data_py.import_ftn_data(years)` — FTN charting data, available for 2022+ seasons. Assumed to expose defensive coverage labels (Cover 0/1/2/3/4/6, man/zone) and additional defensive context (blitz, pass rushers, defenders in box). **Unverified — Phase 1 will audit the actual schema.**
- `nfl_data_py.import_pbp_data(years)` — full play-by-play with EPA, situational context (down, distance, field position, score, time), and play outcomes. Joinable to FTN on `game_id` + `play_id`.

**Pivot path if Phase 1 audit fails:** If FTN does not expose Cover 0–6 labels, the project pivots to whatever broader defensive tendency dimensions FTN does support (blitz rate, pass-rusher count, defenders in box, pressure events). The repo name and findings narrative will be calibrated to that result. **Aborting is not the default** — the pivot path is preferred because the underlying skills demonstrated are unchanged.

**Domain primer:** A defensive coverage describes how secondary players are aligned post-snap. Cover 0 (no deep safety, all-out blitz), Cover 1 (one deep safety, man underneath), Cover 2 (two deep safeties), Cover 3 (three deep zones), Cover 4 (four deep quarters), Cover 6 (split-field hybrid). Modern offenses exploit known coverage tendencies — analyzing those tendencies is real work done by NFL analytics departments.

**Sample-size discipline:** With ~270 regular-season games × 32 teams across 3 seasons, team-situation cells get thin fast. Minimum N=15 plays for any tendency claim; smaller cells are flagged in both notebooks and FINDINGS.md.

## Constraints

- **Tech stack**: Python 3.11+, SQLite, pandas, matplotlib/seaborn, Jupyter, `nfl_data_py` — pinned in `requirements.txt` to insulate from `nfl_data_py` API drift.
- **No external infra**: no Docker, no cloud DB, no managed services, no API keys. A recruiter clone-and-run on a stock laptop must succeed.
- **Public-repo discipline**: nothing checked in that we'd be embarrassed for a recruiter to read — no PFF/paid data, no scratch files, no noisy commit history. Working name is `nfl-coverage-tendencies` but the **public GitHub repo name is locked only after the Phase 1 FTN audit** (it may become `nfl-defensive-tendencies` if the project pivots).
- **Ship via GitHub MCP**: the public repo is created and populated through the connected GitHub MCP, not manual `git push origin`. Ship phase plans must use GitHub MCP tools.
- **Reproducibility budget**: the recruiter "from clone to first chart" path must be ≤ 5 commands and complete on a stock laptop in ≤ 10 minutes (excluding initial `nfl_data_py` data download).
- **Scope budget**: this is a portfolio piece, not an SaaS. Six core deliverables (README, ETL, schema, queries, notebooks, FINDINGS.md). Stretch goals stay stretch goals until core is shipped.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FTN charting via `nfl_data_py` (not Big Data Bowl) | Eliminates Kaggle manual-download friction; FTN labels every play, not a subset | — Pending (validated by Phase 1 audit) |
| SQLite (not Postgres / DuckDB) | Zero-setup, single file, ideal for clone-and-run portfolio piece | — Pending |
| Jupyter + matplotlib/seaborn (not Streamlit dashboard) | A static analytical memo conveys the same skill signal without deployment overhead | — Pending |
| Quality model profile for planning agents | Portfolio piece; depth of research and roadmap pays off | — Pending |
| Coarse phase granularity, parallel execution | 3–5 broad phases keeps a solo project moving; parallelism shortens total clock time | — Pending |
| Commit `.planning/` to git | Visible engineering process is itself a recruiter signal | — Pending |
| Pivot (not abort) if FTN lacks Cover 0–6 labels | Skills demonstrated are scheme-agnostic; broader defensive tendencies still answer the same business questions | — Pending |
| Public repo name decided after Phase 1 | Avoids re-naming if the FTN audit forces a pivot | — Pending |
| Ship via GitHub MCP | The connected MCP enables repo creation, topic configuration, and pinning in one flow | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-29 after initialization*
