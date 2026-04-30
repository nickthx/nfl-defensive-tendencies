# NFL Defensive Tendencies

## What This Is

A public, portfolio-grade data analytics project that examines how NFL defenses deploy scheme tendencies situationally — using `nfl-data-py==0.3.3` (FTN charting + nflfastR play-by-play) for the 2022–2025 seasons (four full seasons including the 2025 regular season and playoffs through Super Bowl LX). Audience: data-analyst recruiters and sports-analytics teams reviewing entry-level applicants. The deliverable is a public GitHub repo with a reproducible Python+SQLite ETL, ~8 SQL analyses, Jupyter notebooks, and an analyst-memo-style FINDINGS.md.

The original framing centered on coverage scheme labels (Cover 0/1/2/3/4/6, man/zone). Project research confirmed those labels are NOT in public FTN data — they are part of FTN's paid product. The project pivots to broader defensive tendencies (blitz rate, pass-rusher count, play-action response, screen rate, RPO usage, QB location, backfield personnel, hash starting position). Phase 1 picks the final 3–4 dimensions to anchor analysis.

## Core Value

A recruiter can clone the repo, run a single command, and within 2 minutes understand both the analytical insight and the engineering rigor behind it.

Everything else (depth of statistical work, breadth of business questions, sophistication of the predictability score) is downstream of that one experience working.

## Requirements

### Validated

(None yet — ship to validate)

### Active

<!-- Hypotheses until shipped. Detailed REQ-IDs live in REQUIREMENTS.md after the requirements pass. -->

- [ ] Phase 1 calibration: profile FTN NaN rates per defensive column for 2022–2025, pick 3–4 anchor dimensions, lock public repo name
- [ ] Reproducible ETL pipeline pulls FTN + nflfastR via `nfl-data-py==0.3.3`, caches parquet, lands SQLite (gitignored)
- [ ] Lightly-normalized SQLite schema joining FTN to nflfastR on `nflverse_game_id` + `nflverse_play_id`
- [ ] 8–10 SQL analysis queries answering the situational tendency questions (window fns, CTEs, joins)
- [ ] Python notebooks: chi-square test on at least one situation; normalized-entropy predictability score with KL-from-baseline alternative
- [ ] FINDINGS.md memo with 5–7 insights, tiered sample-size disclosure (N≥30 / ≥100 / ≥15-with-flag), embedded static PNG charts
- [ ] README that conveys the project's value in under 90 seconds, hand-written (no AI boilerplate), with a hero chart in the first scroll
- [ ] Public GitHub repo created and configured (description, topics, pinned) via the GitHub MCP at ship time
- [ ] `nbconvert` smoke-test verifies all notebooks run end-to-end on a fresh kernel

### Out of Scope

- **Cover 0–6 / man-zone labels** — not in public FTN; the FTN paid product would be required and is not redistributable. Pivot path is the project.
- **`nflreadpy` migration** — considered (maintained successor) and rejected for v1; documented as v2 candidate.
- **Streamlit / web dashboard** — adds deployment overhead without improving recruiter signal for an analytical project.
- **Big Data Bowl + Kaggle dependency** — replaced by `nfl_data_py`; eliminates manual download friction.
- **Postgres / DuckDB / Docker / cloud DB** — SQLite is sufficient and zero-friction for a recruiter clone-and-run.
- **Committing the `.db` file** — 200–400 MB exceeds GitHub's 100 MiB limit; recruiters regenerate via ETL.
- **Play-call prediction model** — scope creep; tendency analysis is the ceiling for v1.
- **Betting / wagering angle** — keep the tone analytical, not speculative.
- **Real-time / in-season auto-updating** — static analysis on fixed seasons.
- **PFF / paid data** — not redistributable in a public portfolio repo.
- **Video / film breakdown** — out of scope for a tabular-data project.

## Context

**Author profile:** This is one of Nick's portfolio pieces aimed at entry-level data-analyst roles, distinct from his Whitflow lead-gen automation work. Audience is non-football, non-domain recruiters — README and FINDINGS.md must convey value without assuming NFL knowledge.

**Data shape (verified by project research):**
- `nfl_data_py.import_ftn_data(years)` returns a 29-column FTN charting frame for 2022+ (the Phase 1 audit on 2026-04-29 surfaced one column — `n_defense_box` — beyond the 28 the original research enumerated). Defensive context is limited to `n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`. **No Cover 0–6, no man/zone, no defenders-in-box-as-coverage-shell columns** in the public dataset.
- `nfl_data_py.import_pbp_data(years)` returns the full nflfastR play-by-play (~47k plays/season) with EPA, win probability, situational context, and outcomes. Joinable to FTN on `nflverse_game_id` + `nflverse_play_id` (NOT `ftn_game_id` / `ftn_play_id`).
- `nfl-data-py` itself was archived 2025-09-25; we pin `==0.3.3` and accept the risk for SPEC-literal compatibility.

**Domain primer (for the FINDINGS.md / README audience):** A defensive tendency is the rate at which a defense plays a particular look in a specific situation. Even without coverage labels, observable tendency dimensions include: how often a defense brings a blitz (`n_blitzers > 4`), how many pass rushers it sends, how it responds to play-action, how often it allows screens / RPOs to gain leverage, and how it positions vs offensive personnel. Modern offenses exploit known defensive tendencies — analyzing those tendencies is real work done by NFL analytics departments.

**Sample-size discipline (tiered):**
- **N≥30** for tendency claims (e.g., "the Bills blitz 38% of the time on 3rd-and-long")
- **N≥100** for "extreme" claims (e.g., ">75% one look")
- **N≥15** allowed only with an explicit low-sample flag in narrative

**Garbage-time / low-leverage filtering** is a project-wide view (`wp BETWEEN 0.05 AND 0.95`), not per-query. Multiple-comparisons discipline: pre-register 3–5 situations in `docs/analysis-plan.md` before scanning all 32 × all situations.

## Constraints

- **Python**: 3.11 only (cap; `nfl-data-py==0.3.3` install fails on 3.13 per upstream issue #122)
- **Locked tech stack**: `nfl-data-py==0.3.3`, `numpy<2.0` (forced by upstream `np.float_` reference), `pandas>=2.1,<2.3`, SQLite, Jupyter, matplotlib/seaborn, scipy. NO Streamlit, NO Postgres / DuckDB / Docker / cloud DB, NO `nflreadpy` for v1.
- **Reproducibility budget**: clone → first chart in ≤ 5 commands, ≤ 10 minutes on a stock laptop (excluding initial `nfl_data_py` data pull).
- **Public-repo discipline**: nothing checked in we'd be embarrassed for a recruiter to read — no scratch files, no AI-generated README boilerplate, no PFF/paid data. nflverse CC-BY-SA attribution required in README.
- **`.db` is gitignored**: 200–400 MB > 100 MiB GitHub limit; recruiter regenerates via ETL.
- **Ship via GitHub MCP**: the public repo is created and populated through the connected GitHub MCP. Ship phase plans must use GitHub MCP tools.
- **Working folder name** is `nfl-coverage-tendencies` (kept for git history); **public repo name** is locked at the end of Phase 1 (likely `nfl-defensive-tendencies`).
- **Scope budget**: portfolio piece, not SaaS. Six core deliverables (README, ETL, schema, queries, notebooks, FINDINGS.md). Stretch goals stay stretch goals until core is shipped.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pin `nfl-data-py==0.3.3` (not `nflreadpy`) | SPEC-literal compatibility, faster ship, frozen scope; archived risk acceptable | — Pending |
| Project pivots to broader defensive tendencies (no Cover 0–6) | Public FTN has no man/zone or coverage-shell labels; pivot preserves all the demonstrated skills | ✓ Locked (validated by 4 independent research agents) |
| FTN charting via `nfl_data_py` (not Big Data Bowl / Kaggle) | Eliminates manual-download friction; FTN labels every play | — Pending |
| SQLite (not Postgres / DuckDB) | Zero-setup, single file, ideal for clone-and-run portfolio piece | — Pending |
| Jupyter + matplotlib/seaborn (not Streamlit dashboard) | Static analytical memo conveys the same skill signal without deployment overhead | — Pending |
| `.db` gitignored, recruiter regenerates via ETL | 200–400 MB exceeds GitHub 100 MiB limit; ETL is the demo anyway | — Pending |
| Quality model profile for planning agents | Portfolio piece; depth of research and roadmap pays off | — Pending |
| Coarse phase granularity (3–5 phases), parallel execution | Keeps a solo project moving; parallelism shortens total clock time | — Pending |
| Commit `.planning/` to git | Visible engineering process is a recruiter signal | — Pending |
| Phase 1 = pivot calibration, not blank-slate FTN audit | Researchers have already confirmed the FTN public schema; Phase 1 measures NaN rates and picks dimensions | — Pending |
| Public repo name decided at end of Phase 1 | Avoids re-naming after final dimension choice | — Pending |
| Ship via GitHub MCP | Connected MCP enables repo creation, topic configuration, pinning in one flow | — Pending |
| Tiered sample-size discipline (N≥15 / 30 / 100) | Single threshold loses analytical nuance; tiered system surfaces "extreme" claims with proper rigor | — Pending |
| Normalized Shannon entropy (H/log(k)) for predictability score | Raw entropy isn't comparable across different support sizes; normalization is the rigorous default | — Pending |
| D-09: Public GitHub repo name | Locked to `nfl-defensive-tendencies` after Phase 1 audit confirmed the public-FTN pivot; `coverage` framing in original repo name no longer accurate. Working folder stays `nfl-coverage-tendencies` for git history continuity. | Locked 2026-04-29 |
| D-10: Scope expanded from 2022–2024 to 2022–2025 | The 2025 NFL season completed February 2026 with Super Bowl LX. A pre-pivot data-quality check (`scratch/verify_2025.py`, 2026-04-29) confirmed: full 18-week regular season + 4-round playoffs present in FTN and pbp; no FTN columns added or removed; 4-season FTN↔pbp `validate='one_to_one'` match rate 0.9999 (vs 0.9998 for 3 seasons); all 8 candidate FTN columns re-validate against the 30% NaN cutoff at essentially zero NaN; 4-season totals 80,782 pass plays / 59,824 run plays / 140,606 plays in the play-type-only universe (Phase 2's locked `competitive_plays` view applies wp / OT / end-of-half predicates and trims this to 105,556 — the analytical universe Phase 3 reads from). Including 2025 adds current-season recency for recruiters without disturbing the locked anchor set. | Locked 2026-04-29 |

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
*Last updated: 2026-04-29 after Phase 1 D-09 lock, pandas pin alignment, and D-10 scope expansion to 2022-2025*
