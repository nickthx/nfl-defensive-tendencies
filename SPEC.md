# Project: NFL Defensive Tendencies — A Situational Analysis

## Objective
Build a portfolio-grade data analytics project examining how NFL defenses deploy schemes situationally, and which tendencies are exploitable. Use FTN charting + nflfastR play-by-play (both via `nfl-data-py==0.3.3`) for the 2022–2025 seasons (four seasons through Super Bowl LX). Target audience: data-analyst recruiters and sports-analytics teams reviewing entry-level applicants.

> **Working folder name:** `nfl-coverage-tendencies` (kept for git history continuity).
> **Public GitHub repo name:** locked at the end of Phase 1 (likely `nfl-defensive-tendencies`).

## Why This Project
Defensive tendency analysis is real work done by NFL analytics departments and betting markets. Pairing FTN charting with nflfastR demonstrates the candidate can:
- Work with multiple data sources of different shapes and join them coherently
- Translate domain questions into SQL and Python
- Build statistical analyses with proper context (sample size, confidence)
- Communicate findings to a non-technical audience

## Audience & Framing
This is a **public GitHub portfolio piece for entry-level data-analyst job applications**. Prioritize:
- Readability for a non-football recruiter (clear narrative, glossary where needed)
- Reproducibility on a recruiter's laptop (single `pip install -r requirements.txt`, single ETL command, no Docker required)
- A polished README that conveys value in under 90 seconds
- Memo style, not tutorial style. AI-generated boilerplate is a negative recruiter signal — README is hand-written.

## Data Sources
1. **FTN charting** via `nfl_data_py.import_ftn_data(years)` — manually charted play tags. **Public columns confirmed do NOT include Cover 0/1/2/3/4/6 or man/zone labels** (those are part of FTN's paid product). Available defensive / play-context columns include `n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`. Phase 1 will profile NaN rates and pick 3–4 dimensions to anchor analysis.
2. **nflfastR play-by-play** via `nfl_data_py.import_pbp_data(years)` — every regular-season play with EPA, win probability, situational context (down, distance, field position, score, time, play_type), and outcomes. Joinable to FTN on `nflverse_game_id` + `nflverse_play_id`.

**Seasons in scope:** 2022, 2023, 2024, 2025 (regular season + playoffs through Super Bowl LX). Estimated combined size after ETL: ~185k plays, SQLite ~250–500 MB.

## Tech Stack (pinned)
- **Language:** Python 3.11 (cap; `nfl-data-py` install fails on 3.13)
- **Core libs:** `nfl-data-py==0.3.3` (archived upstream — accepted risk for SPEC-literal compatibility), `numpy<2.0` (forced by `nfl-data-py` referencing `np.float_`), `pandas>=2.1,<2.3`
- **Database:** SQLite (single file, zero-setup, no Postgres / DuckDB / Docker / cloud DB)
- **Notebooks:** Jupyter (jupyterlab or notebook — recruiter compat over preference)
- **Visualization:** `matplotlib` + `seaborn` for static charts embedded in notebooks and FINDINGS.md
- **Stats:** `scipy.stats` (chi-square, normalized entropy)
- **No Streamlit / web dashboard, no Kaggle, no cloud infra.**

A draft `requirements.txt` is finalized in Phase 2; the consolidated stack lives in `.planning/research/SUMMARY.md`.

## Deliverables
1. **Public GitHub repo** with professional README (created via the GitHub MCP at ship time)
2. **SQLite database** (gitignored — 200–400 MB exceeds GitHub's 100 MiB limit) regenerated via ETL
3. **ETL pipeline** (Python) that pulls both data sources via `nfl_data_py`, caches raw parquet locally, normalizes, and lands SQLite
4. **SQL analysis layer** — 8–10 queries answering specific tendency questions
5. **Python analysis notebooks** (Jupyter) — deeper statistical work, visualizations, modeling, with embedded narrative
6. **Findings report** (`FINDINGS.md`) — written like an analyst memo, 5–7 key insights with embedded static charts (PNGs)

## Repo Structure
```
nfl-coverage-tendencies/                  # local folder; public repo name set in Phase 1
├── README.md
├── data/
│   ├── raw/                              # gitignored parquet cache from nfl_data_py
│   ├── nfl_tendencies.db                 # gitignored — recruiter regenerates via ETL
│   └── README.md                         # how to acquire data via nfl_data_py
├── schema/
│   ├── 01_create_tables.sql
│   └── 02_indexes.sql
├── etl/
│   ├── load_ftn.py
│   ├── load_pbp.py
│   ├── join_and_normalize.py
│   └── run.py                            # single-command orchestrator
├── queries/
│   ├── 01_tendency_distribution_by_team.sql
│   ├── 02_tendency_by_down_and_distance.sql
│   ├── 03_red_zone_vs_midfield.sql
│   ├── 04_epa_allowed_by_tendency.sql
│   ├── 05_third_long_tendencies.sql
│   ├── 06_play_action_response.sql
│   ├── 07_situational_predictability_score.sql
│   └── 08_week_over_week_drift.sql
├── analysis/
│   ├── 01_exploratory.ipynb
│   ├── 02_predictability_modeling.ipynb
│   └── 03_visualizations.ipynb
├── findings/
│   ├── FINDINGS.md
│   └── images/                           # static PNGs exported from notebooks
└── requirements.txt
```
*Final folder names may shift slightly based on Phase 1 calibration.*

## Business Questions to Answer
Each becomes a SQL query, Python analysis, or both. Anchored on the four dimensions named in `docs/ftn-schema-audit.md`: `n_blitzers` and `n_pass_rushers` (pressure, on `play_type='pass'`), `is_play_action` (cross-cutting D-07 modifier), and `n_offense_backfield` (personnel, on competitive plays).

1. **Distribution baseline:** What is the league-wide blitz rate (`n_blitzers > 0` — any FTN-charted extra rusher above the 4-man base front; D-14 calibration) and pass-rusher count (`n_pass_rushers`) distribution on `play_type='pass'`, and how does each team's rate deviate from the league baseline? How does the `n_offense_backfield` distribution shift between 1st-and-10 and 3rd-and-long?
2. **Down & distance:** Which teams have the most predictable blitz rate on 3rd-and-long (S1)? On 1st-and-10 (S3)? On 2nd-and-medium (S4)? Predictability is computed against a normalized Shannon entropy over the chosen anchor's support.
3. **Field zone:** How does `n_pass_rushers` distribution change in the red zone (S2 — `yardline_100 <= 20`) vs midfield, controlling for down and distance? Which teams have the largest red-zone-vs-midfield gap?
4. **EPA allowed:** Which `n_pass_rushers` count (4-rusher vs 5+-rusher) gives up the most EPA per play league-wide? Per team? Across the 4 pre-registered situations only (firewall per D-05).
5. **Predictability score:** Build a single 0-100 Predictability Index per team, computed *conditional on situation* using `H/log(k)` over fixed anchor support OR KL-from-league-baseline (chosen in Phase 3 / STAT-04). Rank all 32 teams.
6. **Play-action stratification (D-07):** Within each pre-registered situation, how does each team's blitz rate differ between `is_play_action=true` and `is_play_action=false` pass plays? Reported only when both stratum sizes meet N>=30. Cross-cutting modifier across the 4 situations rather than its own slate item.
7. **Drift over time:** Do coordinators' anchor-dimension rates (blitz rate, pass-rusher distribution, `n_offense_backfield` mix) drift week-over-week within a season, or stay sticky? Measured as week-to-week rate variance with N>=30 per team-week.
8. **Exploitable matchups (firewall):** Within the 4 pre-registered situations only, identify the team-situation combos where the chosen anchor rate is "extreme" (>75% one look) with N>=100 across 2022-2025. Anything outside the 4-situation slate stays exploratory and is not a headline finding.

## Technical Requirements
- **SQL queries** must include: window functions, CTEs, joins across both data sources, situational filtering
- **Python analysis** must include: pandas data manipulation, at least one statistical test (chi-square for tendency vs. random), matplotlib/seaborn visualizations
- **Predictability score** uses **normalized** Shannon entropy (`H / log(k)` against fixed support, or KL-from-baseline) — raw entropy is meaningless across different support sizes
- All analysis includes sample-size disclosure with tiered thresholds:
  - **N≥30** for tendency claims
  - **N≥100** for "extreme" / >75% claims
  - **N≥15** allowed only with explicit low-N flag in narrative
- Garbage-time / low-leverage filtering (`wp BETWEEN 0.05 AND 0.95`) is a project-wide view, not per-query
- Multiple-comparisons discipline: pre-register 3–5 situations in `docs/analysis-plan.md` before scanning

## README Requirements
- One-paragraph hero hook: "What does this project show?"
- Hero chart in the first scroll (the most striking finding visualized)
- Tech stack badges: Python 3.11, SQLite, pandas, matplotlib/seaborn, nfl_data_py, Jupyter
- "Key findings" with 3–4 punchy stats teasing the full report
- Architecture diagram (simple — `nfl_data_py` → ETL → SQLite → notebooks → FINDINGS.md)
- Setup instructions: clone, `pip install`, run ETL script, open notebooks (≤ 5 commands, ≤ 10 min on stock laptop)
- Link to full FINDINGS.md report
- Hand-written, not AI-boilerplate (no emoji headers, no "Welcome to my project!" tone)

## Quality Bar
- FINDINGS.md reads like an NFL analytics memo (TL;DR top, methodology appendix bottom), not a tutorial or homework write-up
- All claims backed by sample size and statistical context
- README readable in under 90 seconds
- Notebooks run end-to-end on a fresh kernel from a clean clone (no hidden state, no manual cell ordering, smoke-tested via `nbconvert`)
- Code commented but not over-commented (assume reader is technical)
- Tendency labels mapped consistently and the mapping documented in the README

## Out of Scope
- **Cover 0–6 / man-zone labels** — not in public FTN; we don't pay for FTN's premium product or PFF
- **Streamlit / web dashboard** — adds deployment overhead without improving recruiter signal; static notebook + memo conveys the same skills
- **Big Data Bowl tracking data + Kaggle dependency** — replaced by FTN via `nfl_data_py`; no manual download
- **Postgres / DuckDB / Docker / cloud DB** — SQLite is sufficient and zero-friction
- **`nflreadpy` migration** — considered (the maintained successor) and rejected for v1; SPEC-literal compatibility wins for a frozen-scope portfolio piece. Documented as a v2 candidate.
- **Play-call prediction model** — scope creep; tendency analysis is the ceiling for v1
- **Betting / wagering angle** — keep tone analytical, not speculative
- **Real-time / in-season auto-updating** — static analysis on fixed seasons
- **PFF or other paid data** — not redistributable in a public repo
- **Video / film breakdown** — out of scope for a tabular-data project

## Risks & Mitigations
- **`nfl-data-py` archived (2025-09-25)** → pin `==0.3.3`; freeze parquet cache after first successful pull; document the package risk as Key Decision; revisit `nflreadpy` for v2.
- **FTN public columns thinner than recruiters might assume** → README and FINDINGS.md are explicit about FTN's *public* scope and which dimensions were chosen; analytical insight does not depend on Cover 0–6.
- **Small samples per team-situation cell** → tiered N thresholds (15 / 30 / 100) with explicit narrative flagging.
- **SQLite > 100 MiB GitHub limit** → `.db` is gitignored; recruiter regenerates via single ETL command; make this part of the README's "first run" workflow.
- **Notebook reproducibility (hidden state, random seeds, sort order)** → `nbconvert --to notebook --execute` smoke-test in CI; explicit seed + sort key on any non-deterministic step.

## Stretch Goals (do AFTER core ships)
- Add personnel-grouping context (11 personnel, 12 personnel) to tendency analysis
- Train a simple defensive-tendency classifier using situational features
- Migrate to `nflreadpy` for a v2 if `nfl_data_py` causes friction post-ship

## Ship Plan
- Final repo is **public** on GitHub and created via the GitHub MCP during the ship phase
- README, hero charts, and FINDINGS.md are all in place at first push (no "WIP" portfolio repo)
- Repo description, topics, and pinned status configured for portfolio visibility
- nflverse data attribution (CC-BY-SA) included in README and `data/README.md`
