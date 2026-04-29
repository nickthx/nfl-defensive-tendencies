# Project: NFL Defensive Coverage Tendencies — A Situational Analysis

## Objective
Build a portfolio-grade data analytics project examining how NFL defenses deploy coverage schemes situationally, and which tendencies are exploitable. Combine FTN charting data (defensive coverage labels and tags) with nflfastR play-by-play (situational context) for the 2022–2024 seasons. Target audience: data analyst recruiters and sports analytics teams reviewing entry-level applicants.

## Why This Project
Coverage tendency analysis is real work done by NFL analytics departments and betting markets. Pairing FTN charting with nflfastR demonstrates the candidate can:
- Work with multiple data sources of different shapes and join them coherently
- Translate domain questions into SQL and Python
- Build statistical analyses with proper context (sample size, confidence)
- Communicate findings to a non-technical audience

## Audience & Framing
This is a **public GitHub portfolio piece for entry-level data analyst job applications**. Prioritize:
- Readability for a non-football recruiter (clear narrative, glossary where needed)
- Reproducibility on a recruiter's laptop (single `pip install -r requirements.txt`, single ETL command, no Docker required)
- A polished README that conveys value in under 90 seconds

## Data Sources
1. **FTN charting data** via `nfl_data_py.import_ftn_data(years)` — manually charted defensive labels for every play. **Primary source for coverage tendencies.**
2. **nflfastR play-by-play** via `nfl_data_py.import_pbp_data(years)` — every regular season play, with EPA, situational context, score, time, field position.

**Seasons in scope:** 2022, 2023, 2024 (regular season).

**Open research question (Phase 1):** Confirm exactly which defensive coverage / scheme columns FTN exposes for these seasons. The downstream business questions assume Cover 0/1/2/3/4/6 + man/zone tagging, but the actual FTN schema must be audited before ETL design. If FTN's defensive labeling is thinner than assumed, the project pivots to the strongest tendency dimensions FTN actually supports (e.g., blitz rate, pass rusher count, defenders in box).

## Tech Stack
- **Language:** Python 3.11+
- **Database:** SQLite (single file, portable, zero setup — ideal for a recruiter clone-and-run)
- **ETL & analysis:** `nfl_data_py`, `pandas`, `sqlite3` / `sqlalchemy`
- **Notebooks:** Jupyter
- **Visualization:** `matplotlib` + `seaborn` (static charts embedded in notebooks and findings.md); `plotly` only if a chart genuinely needs interactivity inside a notebook
- **No Docker, no cloud DB, no Kaggle dependency, no web dashboard.**

## Deliverables
1. **Public GitHub repo** with professional README (created via GitHub MCP at ship time)
2. **SQLite database** with normalized schema joining FTN + nflfastR
3. **ETL pipeline** (Python) that pulls both data sources via `nfl_data_py` and loads SQLite
4. **SQL analysis layer** — 8–10 queries answering specific tendency questions
5. **Python analysis notebooks** (Jupyter) — deeper statistical work, visualizations, modeling, with embedded narrative
6. **Findings report** (`FINDINGS.md`) — written like an analyst memo, 5–7 key insights with embedded static charts (PNGs)

## Repo Structure
```
nfl-coverage-tendencies/
├── README.md
├── data/
│   ├── nfl_coverage.db          # SQLite (gitignored if large; checked in if small)
│   └── README.md                # How to acquire data (nfl_data_py, no manual download)
├── schema/
│   ├── 01_create_tables.sql
│   └── 02_indexes.sql
├── etl/
│   ├── load_ftn.py
│   ├── load_pbp.py
│   └── join_and_normalize.py
├── queries/
│   ├── 01_coverage_distribution_by_team.sql
│   ├── 02_coverage_by_down_and_distance.sql
│   ├── 03_red_zone_vs_midfield.sql
│   ├── 04_epa_allowed_by_coverage.sql
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
│   └── images/                  # Static PNGs exported from notebooks
└── requirements.txt
```
*Final folder names may shift slightly based on Phase 1 FTN audit results.*

## Business Questions to Answer
Each becomes a SQL query, Python analysis, or both. Final wording will be calibrated to whichever defensive dimensions FTN actually supports.

1. **Distribution baseline:** What's the league-wide defensive tendency mix? How does each team deviate from baseline?
2. **Down & distance:** Which teams are most predictable on 3rd-and-long? 1st down? Goal-to-go?
3. **Field zone:** How do tendencies change in the red zone vs between the 20s? Backed-up vs midfield?
4. **EPA allowed:** Which defensive looks give up the most EPA per play? Per team?
5. **Predictability score:** Build a single metric per team measuring how predictable their defense is given situation. Rank all 32 teams.
6. **Play-action vulnerability:** Which defensive looks are most exploited by play-action? Which teams stay disciplined?
7. **Drift over time:** Do coordinators adapt week-over-week, or do tendencies stay sticky?
8. **Exploitable matchups:** Identify 2–3 specific team-situation combos with extreme tendencies (>75% one look)

## Technical Requirements
- **SQL queries** must include: window functions, CTEs, joins across both data sources, situational filtering
- **Python analysis** must include: pandas data manipulation, at least one statistical test (chi-square for tendency vs. random), matplotlib/seaborn or plotly visualizations
- **Predictability score** uses entropy (Shannon) or a comparable information-theoretic measure — this is the "wow" piece
- All analysis includes sample size disclosure — small-sample situations flagged
- Minimum N=15 plays for any tendency claim

## README Requirements
- One-paragraph hook: "What does this project show?"
- Tech stack badges: Python, SQLite, pandas, matplotlib/seaborn, nfl_data_py, Jupyter
- "Key findings" with 3–4 punchy stats teasing the full report
- Architecture diagram (simple — `nfl_data_py` → ETL → SQLite → notebooks → FINDINGS.md)
- Setup instructions: clone, `pip install`, run ETL script, open notebooks
- 1–2 hero charts inline (the most striking finding visualized)
- Link to full FINDINGS.md report

## Quality Bar
- Findings doc reads like an NFL analytics memo, not a tutorial
- All claims backed by sample size and statistical context
- README readable in under 90 seconds
- Notebooks run end-to-end on a fresh clone (no hidden state, no manual cell ordering)
- Code commented but not over-commented (assume reader is technical)
- Tendency labels mapped consistently and the mapping documented in the README

## Out of Scope
- No play-call prediction model (tempting, but scope creep — save for v2)
- No betting/wagering angle (keep it analytical, not speculative)
- No video/film breakdown
- No real-time / in-season auto-updating (static analysis on fixed seasons)
- No comparison to PFF data (paid, not redistributable)
- No Big Data Bowl tracking data, no Kaggle dependency, no Docker, no cloud DB
- **No Streamlit / web dashboard.** Deliverable is Jupyter notebooks + FINDINGS.md with static charts. The dashboard layer adds deployment overhead and surface area without improving the recruiter signal for this project.

## Risks & Mitigations
- **FTN defensive labeling may be thinner than assumed (no Cover 0–6 column)** → Phase 1 schema audit resolves this *before* ETL design; project pivots to the strongest dimensions FTN supports.
- **Tendency taxonomy varies** → standardize labels in ETL, document mapping in README.
- **Small samples per team-situation cell** → require minimum N=15 plays for any tendency claim, flag below threshold.
- **`nfl_data_py` data refresh / API drift** → pin package version in `requirements.txt`; freeze raw data dump in `data/raw/` after first successful pull.

## Stretch Goals (do AFTER core ships)
- Add personnel grouping context (11 personnel, 12 personnel) to tendency analysis
- Train a simple defensive-tendency classifier using situational features
- Animated play visualization (only if a tracking source becomes available)

## Ship Plan
- Final repo is **public** on GitHub and created via the GitHub MCP during the ship phase
- README, hero charts, and FINDINGS.md are all in place at first push (no "WIP" portfolio repo)
- Repo description, topics, and pinned status configured for portfolio visibility
