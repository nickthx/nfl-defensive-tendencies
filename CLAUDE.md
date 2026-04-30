# Claude Code Instructions — NFL Defensive Tendencies

A public GitHub data-analytics portfolio piece for entry-level data-analyst job applications. The current project state, requirements, and roadmap live in `.planning/`. Read those before making non-trivial changes.

## Project at a Glance

- **What:** Situational analysis of NFL defensive tendencies (blitz, pressure, play-action, personnel) using `nfl_data_py` (FTN charting + nflfastR play-by-play) for 2022–2025 (four seasons through Super Bowl LX).
- **Why:** Recruiter-visible portfolio piece. The recruiter must clone the repo, run a single command, and within 2 minutes understand both the analytical insight and the engineering rigor behind it.
- **Audience:** Data-analyst recruiters and sports-analytics hiring managers — non-football-fluent. Memo style, not tutorial style.
- **Working folder:** `nfl-coverage-tendencies` (kept for git history). **Public GitHub repo name** is locked at end of Phase 1 (likely `nfl-defensive-tendencies`).

## Locked Stack — Do Not Drift

- **Python:** 3.11 only. NOT 3.12, NOT 3.13. `nfl_data_py` 0.3.x install fails on 3.13 (upstream issue #122, won't be fixed).
- **Library:** `nfl_data_py==0.3.3` is pinned. Upstream is archived; `nflreadpy` is the maintained successor but is **deferred to v2** (see `.planning/PROJECT.md` Key Decisions). Do not propose `nflreadpy` migration in v1.
- **NumPy:** `<2.0` is forced — `nfl_data_py` 0.3.x references `np.float_` which NumPy 2 removed.
- **Pandas:** `>=2.1,<2.3`.
- **Database:** SQLite via stdlib `sqlite3`. NO Postgres, DuckDB, SQLAlchemy, Docker, or cloud DB.
- **Visualization:** matplotlib + seaborn (static PNGs). NO Streamlit, NO Plotly Dash, NO web dashboard.
- **Notebooks:** JupyterLab + jupytext for clean git diffs.
- **Lint/format:** ruff only (replaces black + flake8 + isort).

The full justified stack lives in `.planning/research/STACK.md` and `.planning/research/SUMMARY.md` (Consolidated Stack section).

## Project Realities to Remember

- **Public FTN data has no Cover 0–6 / man-zone labels.** Verified by 4 independent research agents during init. The full coverage taxonomy is part of FTN's paid product. The project is about broader defensive tendencies (`n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`). If you find yourself writing `WHERE coverage = 'Cover 3'`, stop — that column does not exist.
- **FTN↔pbp join keys are `nflverse_game_id` + `nflverse_play_id`**, NOT `ftn_game_id` / `game_id` / `play_id`. The wrong keys silently mis-join. Use `validate='one_to_one'` and assert post-join match-rate `>0.95`.
- **`competitive_plays` view is the single source of truth** for play-type and win-probability filtering (`play_type IN ('pass','run')` AND `wp BETWEEN 0.05 AND 0.95`, excluding 2-minute-drill / OT). Every analytical query references it. Defined in `schema/03_views.sql`.
- **Predictability score must be normalized.** Raw Shannon entropy is bounded by `log(k)` and is not comparable across teams with different observed-category counts. Use `H/log(k)` over fixed support OR KL-from-league-baseline. This is the FIRST cell of `analysis/02_predictability_modeling.ipynb`, not a polish step.
- **Sample-size discipline is tiered:** N≥30 for tendency claims, N≥100 for "extreme" (>75%) claims, N≥15 only with explicit narrative flag. `min_n_filter()` lives in `analysis/_common.py` and is applied to every claim.
- **`.db` is gitignored.** 200–400 MB exceeds GitHub's 100 MiB hard limit. Recruiters regenerate via `python -m etl.run` on first clone (~2–5 min).
- **README is hand-written.** AI-generated boilerplate (emoji section headers, "Welcome to my project!" tone) is a negative recruiter signal — do not introduce it.

## Project Structure

```
nfl-coverage-tendencies/
├── README.md            # hand-written; hero PNG above fold; built in Phase 4
├── requirements.txt     # pinned per .planning/research/SUMMARY.md
├── pyproject.toml       # [tool.ruff] config only
├── .python-version      # 3.11
├── .gitignore           # data/raw/, *.db, .env*, __pycache__/, .ipynb_checkpoints/, venv/
├── .planning/           # GSD workflow artifacts (committed — visible engineering process)
│   ├── PROJECT.md
│   ├── REQUIREMENTS.md
│   ├── ROADMAP.md
│   ├── STATE.md
│   ├── config.json
│   └── research/        # STACK / FEATURES / ARCHITECTURE / PITFALLS / SUMMARY
├── data/
│   ├── raw/             # gitignored parquet cache from nfl_data_py
│   ├── nfl_*.db         # gitignored — recruiter regenerates
│   └── README.md
├── schema/              # SQL DDL: tables, indexes, competitive_plays view
├── etl/                 # nfl_data_py pull → parquet cache → SQLite
├── queries/             # 8 SQL files; every one references competitive_plays
├── analysis/            # _common.py, _style.py, 3 notebooks + 00_data_audit
└── findings/
    ├── FINDINGS.md      # analyst memo, 5–7 named insights
    └── images/          # checked-in PNGs (~30–80 KB each)
```

## File-Organization Rules (this repo)

- **Source code** lives in `etl/`, `analysis/`, `schema/`, `queries/`. Never in repo root.
- **Notebooks** live in `analysis/`. Outputs cleared before commit (`nbconvert --clear-output --inplace`); figures live only in `findings/images/`.
- **Documentation** lives in `findings/` (`FINDINGS.md`), `data/` (`README.md`), `docs/` (analysis-plan, schema-audit), and the project root (top-level `README.md`).
- **Planning** lives in `.planning/`. Do not write planning docs anywhere else.
- **Tests:** there is no `tests/` directory by default. Assertions live inside the ETL (`validate='one_to_one'`, match-rate >0.95, row-count guards). Do not add a cargo-cult `tests/` directory with trivial asserts.
- **Never save scratch / WIP files to repo root.** If you need throwaway work, put it in `scratch/` (gitignored).

## GSD Workflow

This project was initialized with the GSD (Get Shit Done) framework. The current state lives in `.planning/STATE.md`.

**Common commands:**
- `/gsd-progress` — show current phase + next action
- `/gsd-discuss-phase <N>` — clarify phase approach before planning
- `/gsd-plan-phase <N>` — create the detailed plan for phase N (research → plan → plan-check)
- `/gsd-execute-phase <N>` — run all plans in phase N
- `/gsd-verify-work` — confirm a phase delivered its success criteria

Workflow config in `.planning/config.json`: interactive mode, coarse granularity, parallelization on, quality model profile, all workflow agents enabled (research, plan-check, verifier).

**Next step:** `/gsd-plan-phase 1` — Foundation & FTN Pivot Calibration.

## Concurrency Rules (when running tools)

- Batch independent tool calls in a single message (file reads, file writes, bash commands).
- When spawning planning subagents (e.g., `gsd-roadmapper`), use `run_in_background: true` and trust them to return; do not poll status.
- For trivial commits / one-shot edits, use the direct tools (Edit / Write / Bash) — do NOT spin up a swarm.

## Security & Public-Repo Discipline

- **No secrets ever.** This project does not require API keys; if you find yourself adding one, pause and ask.
- **No PFF or paid data.** Not redistributable in a public repo.
- **No `data/raw/` or `*.db` commits.** They are gitignored; do not `git add -f` them.
- **Verify clean working tree** before any push. Use `git status` and inspect every file in the staging area.

## Audience Voice

When writing prose for `README.md`, `FINDINGS.md`, or any user-facing markdown:
- **Memo style**, not tutorial. The reader is a peer (recruiter, hiring manager, analyst), not a student.
- **No exclamation points, no emoji section headers, no "Welcome to my project!" greetings.**
- **Numbers first.** "The Bills blitz 38% on 3rd-and-long (N=247)." Not: "The Bills are an aggressive blitzing defense."
- **State sample size inline** with every claim.
- **Limitations section** is mandatory in `FINDINGS.md`. Name what the data CAN'T tell you.

## When in Doubt

Read `.planning/PROJECT.md` (Key Decisions table) and `.planning/research/SUMMARY.md` (TL;DR + Resolved Disagreements). Both were authored under user supervision and reflect locked decisions.
