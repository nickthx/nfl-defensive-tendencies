# Project Research Summary

**Project:** NFL Defensive Tendencies — A Situational Analysis (working repo name TBD post-Phase 1; pivoting away from "Coverage Tendencies")
**Domain:** Solo-author tabular data-analytics portfolio (Python + SQLite + Jupyter), entry-level data-analyst recruiter audience
**Researched:** 2026-04-29
**Confidence:** HIGH on stack, features, and pitfalls; MEDIUM on FTN per-column NaN rates (Phase 1 measures these)

---

## TL;DR (read this first)

- **The SPEC's headline framing — "Cover 0/1/2/3/4/6 + man/zone tendencies" — is unanswerable from public data.** The nflverse-distributed FTN subset is 28 columns and contains zero coverage labels. The full Cover-0–6 / man-zone taxonomy is part of FTN's paid product. The project pivots to broader **defensive tendencies** using the available FTN dimensions: `n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`. Repo name and SPEC title update accordingly.
- **`nfl_data_py==0.3.3` is LOCKED.** Library is archived upstream (2025-09-25) and recommends `nflreadpy`. The user has accepted the archived-package risk for v1 in exchange for SPEC-literal compatibility and faster ship time. `nflreadpy` migration is **considered and rejected for v1**, documented as a "Future Work" line in the README.
- **Python 3.11 + `numpy<2` is non-negotiable** because `nfl_data_py` 0.3.x references `np.float_` (removed in NumPy 2) and fails to install on Python 3.13 (open issue #122 will never be patched).
- **The SQLite database WILL exceed GitHub's 100 MiB limit** (estimated 200–400 MB for 3 seasons). It MUST be gitignored. Recruiters regenerate via `python -m etl.run` on first clone (~2–5 min).
- **Phase 1 is pivot calibration, not exploration.** It measures NaN rates per FTN defensive column for 2022–2024, picks the 3–4 strongest dimensions to anchor analysis, and locks the public repo name.
- **The README is the project.** Recruiters spend 30–90 seconds before bouncing. Hand-written voice (no AI-template emoji-section boilerplate), one hero PNG above the fold, and 3–4 stat-first bullet findings make or break the signal. Memo style, not tutorial, not academic.
- **The entropy-based predictability score is the "wow piece" — but it is broken without normalization.** Raw Shannon entropy is bounded by `log(k)`; teams with different observed-category counts get incomparable scores. Normalization (`H/log(k)` or KL-from-baseline) is the first cell of the modeling notebook, not an afterthought.

---

## Executive Summary

This is a **solo-author Python+SQLite+Jupyter analytics portfolio piece** for entry-level data-analyst recruiters. The body of research converges on a clear shape: a small, lightly normalized SQLite database fed by a Parquet-cached ETL from `nfl_data_py`, queried by ~8 standalone SQL files, with three Jupyter notebooks (explore / model / visualize) feeding a hand-written `FINDINGS.md` analyst memo and a `README.md` whose hero chart sells the project in under 90 seconds. The skill signal is breadth (ETL → SQL → pandas → stats → viz → writing), not depth in any one layer.

Two findings reshape the project relative to the original SPEC. First, **the public FTN subset does not contain the Cover 0–6 / man-zone labels the SPEC presumes** — those are part of FTN's paid commercial product. The project pivots to broader defensive tendencies (blitz rate, pass-rusher count, play-action response, etc.) on the columns FTN actually exposes. Phase 1 measures NaN rates by `play_type` and locks the 3–4 anchor dimensions. Second, **the data layer (`nfl_data_py`) was archived in September 2025**. The user has explicitly chosen to stay on the pinned `0.3.3` for v1; this is a documented decision, not an oversight, and the README will frame it as "we know, here's why, here's the migration path for v2."

Risk concentrates in three places: (1) the Phase 1 audit must actually be done before any ETL design — skipping it converts a recalibration into a rewrite; (2) the recruiter "clone-and-run" path must be tested on a fresh venv before ship — `requirements.txt` pinning is the single highest-leverage technical-debt vector, and `numpy<2` is the specific landmine; (3) every analytical claim must report N inline and survive a competitive-plays / win-probability sensitivity check, because junior portfolios uniformly fail on sample-size discipline.

---

## Resolved Disagreements Across Research Files

The four researchers diverged on a few load-bearing decisions. The user has locked decisions; this section records them so the roadmapper does not relitigate.

| Disagreement | Stack Researcher | Architecture Researcher | Locked Decision | Why |
|--------------|------------------|-------------------------|-----------------|-----|
| **`nfl_data_py` vs `nflreadpy`** | Recommended `nflreadpy` (Path B) — archival is a recruiter red flag | Acknowledged archival but recommended staying on `nfl_data_py==0.3.3` — `nflreadpy` is v0.1.5 and "experimental" by its own authors | **`nfl_data_py==0.3.3` LOCKED** | User accepts the archived-package risk for v1; SPEC-literal API; faster to ship. Documented as a Known Issue in README, with a one-paragraph "v2 migration path" reference. |
| **Default `pandas` pin range** | `>=2.2,<2.4` (forward-leaning, runs on the latest "safe" pre-3.0) | `==2.1.4` (matches the version known-good against `nfl_data_py` 0.3.3) | **`pandas>=2.1,<2.3`** | Compromise: lower bound matches Architecture (tested-with-nfl_data_py); upper bound stays under the `pandas` 2.3 deprecation noise. Pin tight in v1; loosen only if Phase 1 install testing demands it. |
| **Notebook reproducibility CI** | Lint + import smoke; explicitly NOT full-notebook execution | Optional — minimal CI is justified; full nbexecute is over-engineering | **Lint + import smoke ONLY** | Both researchers agree on the floor. Skip notebook-execute CI (pulls 150 MB on every run, flaky). Manual `Restart & Run All` before commit is enforced by Phase 5 ship checklist. |
| **DB commit policy** | Did not address directly | "Conditional commit if ≤25 MB after VACUUM" | **`.db` ALWAYS gitignored (LOCKED).** | Estimated 200–400 MB for 3 seasons; will exceed GitHub's 100 MiB hard limit. ETL regenerates in ~2–5 min on first clone. README documents this. |
| **`pyproject.toml` vs `requirements.txt`** | Both — `requirements.txt` for install (recruiter muscle memory), `pyproject.toml` only for `[tool.ruff]` config | Did not address | **Adopt Stack's recommendation** | Recruiters expect `pip install -r requirements.txt`. `pyproject.toml` exists but only houses the linter config. |

---

## Top 5 Must-Shape-the-Plan Findings

These are the highest-leverage findings from combined research. Each one drives concrete roadmap decisions.

1. **Phase 1 IS pivot calibration, not audit-or-pivot.** Public FTN has no coverage labels — this is verified, not hypothesized. The Phase 1 deliverable is the *calibrated set of defensive dimensions* (3–4 anchors picked from `n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`) plus the `audit/ftn_null_profile.csv` showing NaN rates by `play_type`, plus the locked public repo name. Without this artifact, every downstream phase rests on assumed columns.

2. **The FTN↔pbp join is a silent-failure trap.** FTN exposes `nflverse_game_id` / `nflverse_play_id` as join keys; nflfastR pbp uses `game_id` / `play_id`. A naïve `merge(on=['game_id','play_id'])` returns either zero rows or a silently mis-joined frame. The ETL phase MUST encode `validate='one_to_one'` and a post-join match-rate assertion (`>0.95`).

3. **Confounders dominate the analysis layer.** Garbage-time plays, 2-minute drills, special teams, `qb_kneel`/`qb_spike`, and `no_play` (with its known nflfastR miscoding bug) all contaminate raw-frame analyses. The fix is a single project-wide `competitive_plays` SQL view (filtering on `play_type IN ('pass','run')` AND `wp BETWEEN 0.05 AND 0.95` AND excluding 2-minute drill / OT) referenced by every analytical query. This is a Phase 2 schema deliverable, not a Phase 3 afterthought.

4. **The predictability score is a normalization problem, not a stats problem.** Raw Shannon entropy is bounded by `log(k)` where k is observed support — teams with different observed-category counts cannot be compared. Normalize via `H/log(k)` over a fixed support OR use KL-from-league-baseline. Then surface as a 0–100 "Predictability Index" for the README. Confound from game script must also be addressed by computing the score *conditional on situation*, not as a marginal — otherwise the score correlates with strength of schedule.

5. **README discipline beats analytical depth on the recruiter signal.** The 30-second test (problem statement + hero PNG + 3 stat-first bullets above the fold) and the 90-second test (5-command setup + Mermaid architecture diagram + glossary) are non-negotiable. AI-generated README boilerplate (emoji section headers, "Welcome to my project!" greetings) is a *negative* signal — recruiters spot it instantly. The README must be hand-written in the candidate's voice, even if the analysis is AI-assisted.

---

## Consolidated Stack (v1 ready)

This reconciles Stack and Architecture researcher version pins. Path A (LOCKED) is what ships.

```text
# requirements.txt — v1 LOCKED
# Data layer (archived upstream; intentional pin — see README "Known Issues")
nfl_data_py==0.3.3

# Numerical / data
pandas>=2.1,<2.3
numpy>=1.26,<2.0          # forced — nfl_data_py 0.3.x uses np.float_, removed in NumPy 2.0
pyarrow>=15,<22           # parquet I/O; required transitively by nfl_data_py

# Statistical
scipy>=1.13,<1.18         # chi2_contingency + entropy

# Visualization
matplotlib>=3.8,<3.11
seaborn==0.13.2           # exact pin — only release in 0.13.x line

# Notebooks
jupyterlab>=4.2,<4.6
ipykernel>=6.29,<8
jupytext>=1.16,<2         # paired .py representation for clean git diffs
nbconvert>=7.16,<8        # for one-time clear-output before commit

# Dev tooling
ruff>=0.6,<1.0
```

Plus a minimal `pyproject.toml` for `[tool.ruff]` config only (line-length=100, target=py311, lint select E/F/I/B/UP).

**Python:** 3.11 (NOT 3.12, NOT 3.13). `nfl_data_py` 3.13 install is broken (issue #122, won't be fixed). 3.11 is the safest recruiter-laptop target. Document in README and `.python-version` file.

**Database:** stdlib `sqlite3` only. No SQLAlchemy. Bulk loads via `pd.to_sql(..., method='multi', chunksize=5000)`.

**What is explicitly OUT:** Streamlit, FastAPI, Docker, Postgres, DuckDB, Polars (nflreadpy native — defer), `statsmodels`, `black`+`flake8`+`isort` (ruff replaces all three), pre-commit framework, CI/CD beyond a single lint+import-smoke workflow.

---

## Consolidated Feature Priority

Solo-author entry-level data-analyst portfolio. P1 = ship-blocking. P2 = strong-add. P3 = polish.

### P1 — Table Stakes (bounce-reason if missing)

- One-paragraph plain-English problem statement at top of README — no jargon in the first sentence
- Hero PNG chart visible above the fold — the most striking finding (likely the predictability-index leaderboard)
- 3–4 stat-first bullet findings — each contains a number, links into FINDINGS.md
- 5-command runnable setup block — clone, venv, pip install, `python -m etl.run`, jupyter
- Pinned `requirements.txt` — exact versions (per Consolidated Stack above)
- Repo description + 5–8 GitHub topics + social preview image — configured at ship via GitHub MCP
- Logical folder structure — `data/`, `etl/`, `schema/`, `queries/`, `analysis/`, `findings/`, `.planning/` committed
- Notebooks run end-to-end on fresh kernel — verified by Phase 5 ship gate
- Static charts checked in as PNGs in `findings/images/` (not just live notebook outputs)
- Glossary — 6 football terms (down, distance, EPA, blitz, RPO, predictability index) with one-line definitions
- Sample-size discipline visible — every claim has `(N=X)` inline; minimum N≥30 for tendency claims, N≥100 for "extreme" claims
- No WIP/TODO markers in shipped repo
- Substantive commit history (not one squashed "initial commit")

### P1 — Differentiators (move from "fine" to "memorable")

- Memo-style FINDINGS.md with 5–7 named insights (not tutorial, not academic) — modeled on Open Source Football
- Entropy-based normalized predictability score — the "wow" piece; surface as 0–100 Predictability Index in README
- Mermaid architecture diagram in README — data flow, not file tree
- Reproducibility budget callout ("clone-to-first-chart: 5 commands, ≤10 min")
- Tone-matched copy — analytical, no exclamation points, no emoji section headers, hand-written (not AI-template)
- Limitations section in FINDINGS.md — names what the data CAN'T tell you (pre-snap disguise, charter subjectivity, etc.)
- `.planning/` committed — visible engineering process is itself a recruiter signal
- FTN attribution in README — CC-BY-SA 4.0 requires it ("FTN Data via nflverse")
- nflverse / `nfl_data_py` credit — community etiquette; signals cultural awareness

### P2 — Add If Time Permits

- Phase 1 audit notebook kept in repo as `00_data_audit.ipynb` — shows pivot reasoning visibly
- One non-bar-chart visualization (heatmap or small-multiples grid)
- Single GitHub Actions workflow: `ruff check` + ETL-module import smoke (no notebook execution)
- One `make` or `python -m` target for "rebuild PNGs" to prevent stale-image drift

### P3 — Anti-Features (DO NOT BUILD — these LOOK good but hurt the signal)

- AI-generated README boilerplate (emoji-section-header + "Welcome to my project!" — biggest negative signal)
- Streamlit / web dashboard
- Docker / docker-compose
- Postgres / DuckDB
- ML model on top of tendency analysis (scope creep, leakage risk)
- Cargo-cult `tests/` directory with trivial asserts
- Excessive shields.io badge soup (>5)
- Tutorial-style writeup ("First we import pandas…")
- Academic structure (Abstract / Methods / Results / Discussion)
- Custom logo / branded header image
- Self-deprecating language ("This is just a small project…")
- Betting / DFS / wagering framing
- "Future work" laundry list

---

## Consolidated Architecture Sketch

Calibrated to the post-pivot reality (no coverage labels; defensive tendency dimensions only).

### Directory Tree

```
nfl-defensive-tendencies/                # name LOCKED post-Phase 1
├── README.md                             # hand-written, hero PNG above fold
├── requirements.txt                      # pinned per Consolidated Stack
├── pyproject.toml                        # [tool.ruff] config only
├── .python-version                       # "3.11"
├── .gitignore                            # data/raw/, *.db, .env*, .ipynb_checkpoints/, scratch*, __pycache__/
├── .planning/                            # committed — engineering-process signal
│
├── data/
│   ├── README.md                         # how to acquire data → points at etl/run.py
│   ├── raw/                              # GITIGNORED; parquet cache from nfl_data_py
│   │   ├── pbp_2022.parquet … pbp_2024.parquet
│   │   └── ftn_2022.parquet … ftn_2024.parquet
│   └── nfl_defensive_tendencies.db       # GITIGNORED (200–400 MB; exceeds GitHub 100 MiB)
│
├── schema/
│   ├── 01_create_tables.sql              # games, plays, ftn_play
│   ├── 02_indexes.sql                    # composite (down, ydstogo, yardline_100), defteam-season, etc.
│   └── 03_views.sql                      # competitive_plays view (the WP/play_type filter)
│
├── etl/
│   ├── __init__.py
│   ├── run.py                            # SINGLE CLI entry — `python -m etl.run`
│   ├── load_pbp.py                       # nfl_data_py → data/raw/pbp_<year>.parquet (idempotent)
│   ├── load_ftn.py                       # nfl_data_py → data/raw/ftn_<year>.parquet (idempotent)
│   ├── columns.py                        # column whitelist + rename map (single source of truth)
│   └── build_db.py                       # parquet → SQLite (apply schema, INSERT, validate joins, build indexes)
│
├── queries/
│   ├── 00_filters.sql                    # competitive_plays definition (referenced, not duplicated)
│   ├── 01_tendency_distribution_by_team.sql
│   ├── 02_blitz_rate_by_down_and_distance.sql
│   ├── 03_red_zone_vs_midfield.sql
│   ├── 04_epa_allowed_by_pass_rusher_count.sql
│   ├── 05_third_long_pressure_tendencies.sql
│   ├── 06_play_action_response.sql
│   ├── 07_situational_predictability_score.sql
│   └── 08_week_over_week_drift.sql
│
├── analysis/
│   ├── _common.py                        # SEED=42, db connection helper, shared imports
│   ├── _style.py                         # matplotlib portfolio rcParams (savefig.dpi=200, etc.)
│   ├── 00_data_audit.ipynb               # Phase 1 deliverable, kept
│   ├── 01_exploratory.ipynb              # descriptive stats, sample-size profiling
│   ├── 02_predictability_modeling.ipynb  # entropy normalization (FIRST cell), chi-square, ranking
│   └── 03_visualizations.ipynb           # final figures, exports PNGs to findings/images/
│
└── findings/
    ├── FINDINGS.md                       # memo style — 5–7 named insights
    └── images/                           # checked in (small PNGs, ~30–80 KB each)
        ├── 01_predictability_ranking.png
        ├── 02_blitz_by_down_distance.png
        └── ...
```

### Data Flow

```
nfl_data_py.import_pbp_data / .import_ftn_data
         ↓ (network call, ~30–90s; once per season)
data/raw/*.parquet              ← idempotent cache; survives nflverse drift
         ↓ (read parquet, apply column whitelist + rename, validate join)
SQLite: nfl_defensive_tendencies.db
   tables: games, plays, ftn_play (1:1 join on (game_id, play_id))
   views: competitive_plays (WP filter, play_type filter)
   indexes: (down, ydstogo, yardline_100), (defteam, season), (game_id, play_id) PK
         ↓ (notebook reads queries/*.sql via Path.read_text(); pd.read_sql)
analysis/*.ipynb (3 + audit notebook)
         ↓ (matplotlib fig.savefig with portfolio rcParams)
findings/images/*.png
         ↓ (markdown image embeds, hand-written prose)
findings/FINDINGS.md  →  README.md (hero chart embedded inline)
```

Five recruiter commands from clone to chart:

```bash
git clone <repo> && cd nfl-defensive-tendencies
python -m venv .venv && source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m etl.run                                     # ~2–5 min on first clone
jupyter lab analysis/03_visualizations.ipynb
```

---

## Consolidated Pitfalls Register (Top 10 the Roadmap Must Encode)

Phase mapping uses the suggested 5-phase structure below.

| # | Pitfall | Phase | Prevention |
|---|---------|-------|-----------|
| 1 | Skipping Phase 1 audit and writing SQL against assumed `coverage` columns | Phase 1 | Phase 1 deliverable is `audit/ftn_null_profile.csv` + locked dimension list + locked repo name. ETL phase is gated on this. |
| 2 | Wrong join keys (`ftn_game_id` vs `nflverse_game_id`) producing silent zero-row or mis-joined frames | Phase 2 | `etl/build_db.py` merges with `validate='one_to_one'` and asserts post-join match rate `>0.95`. |
| 3 | NaN on run plays for `n_blitzers` / `n_pass_rushers` silently dropping samples in chi-square | Phase 1 + 3 | `audit/ftn_null_profile.csv` documents expected NaN by `play_type`. All blitz/rush analyses filter to `play_type='pass'` first; documented in every cell. |
| 4 | Garbage time / 2-min drill / kneel-spike / no_play contaminating tendency claims | Phase 2 | `competitive_plays` SQL view (single source of truth) referenced by every analytical query. Sensitivity check on at least one headline finding (with vs without filter). |
| 5 | Sample-size collapse — "75% on 3rd-and-12 from own 5" with N=4 | Phase 3 + 4 | `min_n_filter()` helper. N≥30 for tendency, N≥100 for "extreme" claims. Every FINDINGS.md claim states N inline. Wilson 95% CI on extreme proportions. |
| 6 | Multiple-comparisons trap — scanning 32 teams × 50 situations and reporting "significant" cells | Phase 1 + 3 | `docs/analysis-plan.md` pre-registers 3–5 situations in Phase 1. Exploratory work is segregated and labeled. Effect size + N + CI together; never raw p-values across hundreds of comparisons. |
| 7 | Predictability score broken without normalization; reflects schedule not scheme | Phase 3 | First cell of `02_predictability_modeling.ipynb` defines fixed support and normalizer (`H/log(k)` or KL-from-baseline). Score is computed *conditional on situation*. Public-facing 0–100 Predictability Index. |
| 8 | `requirements.txt` not pinned tightly enough — recruiter's NumPy 2.0 breaks `np.float_` | Phase 0 + 5 | All packages pinned `==` (or tight range). `numpy<2` is locked. Phase 5 verifies install on fresh venv before push. Lint+import-smoke CI workflow runs `pip install -r requirements.txt` + `python -c "import nfl_data_py; ..."`. |
| 9 | `.db` committed to git, blowing past 100 MiB GitHub limit | Phase 0 + 2 | `.db` is in `.gitignore` from day 1. ETL regenerates in <5 min. README documents this. `du -sh .git/` < 50 MB at ship. |
| 10 | Notebook hidden state / out-of-order cells — clone-and-run fails | Phase 3 + 5 | Cells executed in order from fresh kernel before every commit. Outputs cleared via `jupyter nbconvert --clear-output --inplace` before commit (figures live only in `findings/images/`). Phase 5 ship gate verifies on fresh venv. |

**Honorable mentions (encode but not top-10):** README↔code drift after pivot (Phase 1 triggers README rewrite, not deferred to ship); FTN charter subjectivity (round to 1 decimal place; disclose in FINDINGS.md); jargon overload (glossary at hook level, not buried); FINDINGS.md format discipline (memo, not academic); random seed determinism (`SEED=42` in `analysis/_common.py`).

---

## Implications for Roadmap

### Suggested Phase Structure (Coarse — 5 Phases)

User has locked: coarse granularity (3–5 phases), parallel execution where possible, `.planning/` committed, all workflow agents on (research, plan-check, verifier), quality model profile.

#### Phase 0: Repo Bootstrap (foundation)

- **Rationale:** Some discipline is cheaper to install before any code lands than to retrofit (gitignore, repo structure, baseline `requirements.txt`). Avoids Pitfall #8, #9.
- **Delivers:** Skeleton repo (folders only), `.gitignore` (covers `data/raw/`, `*.db`, `.env*`, scratch), `requirements.txt` (per Consolidated Stack), `pyproject.toml` (ruff config only), `.python-version`, README skeleton (sections only, no claims yet).
- **Avoids:** Pitfall #8, #9. Lays groundwork for Pitfall #10.
- **Research needs:** None — research is complete.

#### Phase 1: FTN Pivot Calibration (NOT optional; gates everything)

- **Rationale:** Public FTN has no Cover 0–6 columns. This is verified, not hypothesized. The phase deliverable is the calibrated dimension set + locked repo name + null-rate profile that downstream phases build against. Without this, Phase 2 ETL is built on assumed columns.
- **Delivers:**
  - `notebooks/00_data_audit.ipynb` — calls `nfl.import_ftn_data([2022,2023,2024])`, prints `df.columns.tolist()`, computes per-column NaN rate by `play_type`
  - `audit/ftn_null_profile.csv` — null rates by play_type for every FTN column
  - `docs/ftn-schema-audit.md` — written narrative confirming the 28-column reality and naming the 3–4 anchor dimensions chosen
  - `docs/analysis-plan.md` — pre-registers the 3–5 situations FINDINGS.md will claim findings on (prevents Pitfall #6 multiple-comparisons trap)
  - **Locked:** public repo name (likely `nfl-defensive-tendencies`)
  - **Locked:** business-question rewrite (the SPEC's 8 questions reframed around blitz/pressure/play-action/personnel)
  - README hook rewritten in plain English to match
- **Avoids:** Pitfall #1, #2, #3, #5, #6, README-code drift.
- **Research needs:** None — pre-research is sufficient.

#### Phase 2: ETL + Schema (data layer)

- **Rationale:** Once dimensions are locked, the data layer is well-understood patterns (parquet cache → SQLite via stdlib sqlite3). The risk is in correctness (join keys, filters, indexes), not novelty.
- **Delivers:**
  - `etl/load_pbp.py`, `etl/load_ftn.py`, `etl/columns.py`, `etl/build_db.py`, `etl/run.py` (single CLI)
  - `schema/01_create_tables.sql`, `schema/02_indexes.sql`, `schema/03_views.sql` (the `competitive_plays` view)
  - Idempotent caching to `data/raw/*.parquet`
  - `validate='one_to_one'` on the FTN↔pbp join + `>0.95` match-rate assertion
  - Row-count assertions on the upstream pull (`assert len(ftn) > 100_000`)
  - `.gitignore` confirmed; `du -sh data/` checked (DB will be 200–400 MB; gitignored)
- **Avoids:** Pitfall #2, #4, #9, silent pull failure.
- **Research needs:** None. Standard patterns.

#### Phase 3: SQL + Python Analysis (the analytical work)

- **Rationale:** With the schema and competitive-plays view in place, the queries and notebooks can run in parallel internally. This is where the "wow" piece (predictability index) lives, and where sample-size and normalization discipline matter most.
- **Delivers:**
  - `queries/01-08_*.sql` — each references `competitive_plays`; each has a header documenting question + result shape + caveats
  - `analysis/_common.py` (SEED=42, db helper), `analysis/_style.py` (matplotlib portfolio rcParams)
  - `analysis/01_exploratory.ipynb` — descriptive stats, sample-size profiling
  - `analysis/02_predictability_modeling.ipynb` — first cell defines normalization (`H/log(k)` over fixed support OR KL-from-baseline); chi-square with effect-size; conditional-on-situation predictability index; 0–100 surfacing
  - `min_n_filter()` helper applied to every claim (N≥30 baseline, N≥100 for "extreme")
- **Avoids:** Pitfall #5, #6, #7, game-script confound, random seed.
- **Research needs:** Possible mid-phase research only if Phase 1 surfaces an unusual distributional shape that complicates normalization. Default: skip.

#### Phase 4: Visualization, FINDINGS.md, README (the story)

- **Rationale:** This is the recruiter-signal phase. The analysis exists; now it must read like a memo. Hand-written, memo style, hero chart, glossary, limitations, FTN attribution.
- **Delivers:**
  - `analysis/03_visualizations.ipynb` — exports all PNGs to `findings/images/` with consistent style
  - `findings/FINDINGS.md` — 5–7 named insights, each with headline / chart / why-it-matters / N+caveats; methodology in appendix; limitations section; FTN+nflverse attribution
  - `README.md` (full version) — hand-written, no AI-template emoji headers, hero PNG above fold, 3–4 stat-first bullets, Mermaid architecture diagram, 5-command setup, glossary, links to FINDINGS.md
  - Glossary block defining 6 football terms in plain English
- **Avoids:** jargon overload, stale PNGs, memo vs homework drift, README drift, FTN subjectivity disclosure.
- **Research needs:** None — FEATURES.md research already pulled exemplars.

#### Phase 5: Ship (public push via GitHub MCP)

- **Rationale:** The ship is itself a deliverable. Repo creation, topic config, social preview, pinning — all configured via GitHub MCP (per SPEC). Final reproducibility verification on fresh venv.
- **Delivers:**
  - Fresh-venv install + `python -m etl.run` + Restart-and-Run-All notebook test (all green) on a clean machine
  - Single-workflow GitHub Actions: `ruff check` + ETL-module import smoke
  - Public GitHub repo created via GitHub MCP with description (~70 chars), 5–8 topics (`nfl-analytics`, `data-analysis`, `python`, `sqlite`, `jupyter`, `nfl-data-py`, `sports-analytics`), social preview image (1280×640 from hero chart), pinned to profile
  - Commit history reviewed; any "WIP"/"asdf" squashed; `du -sh .git/` < 50 MB
  - Final push to `main`; verify on a non-author browser
- **Avoids:** Pitfall #8, #9, #10, public-repo discipline.
- **Research needs:** None — ship is execution.

### Phase Ordering Rationale

- **Phase 0 → 1** is strictly serial. The audit needs the skeleton to land artifacts in.
- **Phase 1 → 2** is strictly serial. ETL design depends on the calibrated dimension set.
- **Phase 2 → 3** is strictly serial (notebooks read from SQLite). Within Phase 3, queries and notebooks can be parallelized internally.
- **Phase 3 → 4** is strictly serial. Visualizations and FINDINGS.md depend on the predictability index existing.
- **Phase 4 → 5** is strictly serial. Ship is gated on the README and FINDINGS.md being complete.

User has indicated parallel execution preference. Within phases, parallelism is available (Phase 3: queries 01–08 can be written in parallel; Phase 4: README and FINDINGS.md can draft in parallel after `findings/images/` is locked). Across phases, the dependency graph is linear by nature of the data flow.

---

## Open Questions Phase 1 Must Answer

Phase 1's audit notebook + `docs/ftn-schema-audit.md` deliverable must close these. They are listed here so the roadmapper can scope Phase 1 explicitly.

1. What is the exact column list of `nfl.import_ftn_data([2022, 2023, 2024])` for these seasons? Confirm the 28-column inventory from nflreadr docs matches the live frame. Document any seasonal differences.
2. What is the per-column NaN rate, broken down by `play_type` (`pass`, `run`, `qb_kneel`, `qb_spike`, `no_play`)? This goes in `audit/ftn_null_profile.csv`. Confirm `n_blitzers` and `n_pass_rushers` are populated only on pass-context plays.
3. Which 3–4 defensive dimensions become the analysis anchors? Defensible choice from the available 8 (`n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`). The choice is downstream of the NaN profile (a column with 60%+ NaN on pass plays is unusable as an anchor).
4. Does FTN row-count match pbp row-count for 2022–2024? Architecture assumes 1:1 join; if FTN charts a subset, the join becomes 1:0..1 and `ftn_play` becomes a LEFT JOIN with documented match rate.
5. Does `nfl_data_py==0.3.3` install cleanly on Python 3.11 in 2026? Pre-flight before Phase 2. If broken, address before ETL design (escalate to user).
6. What is the locked public repo name? Default: `nfl-defensive-tendencies`.
7. What are the 3–5 pre-registered situations the analysis plan commits to? Lock in `docs/analysis-plan.md` BEFORE Phase 3.
8. Is the README's plain-English hook rewritten to match the pivot? Phase 1 outcome triggers the README rewrite — not deferred to Phase 5.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All package versions verified against PyPI 2026-04-29; `nfl_data_py==0.3.3` is locked by user; pandas/numpy compatibility is forced by `np.float_` constraint. |
| Features | HIGH | Recruiter-signal patterns converge across 8+ 2025–2026 sources; AI-template anti-pattern is explicitly cited in multiple hiring-manager guides. |
| Architecture | HIGH | Three-tier (parquet → SQLite → notebooks) is standard for tabular analytics portfolios. MEDIUM on row-volume estimates (~141k plays for 3 seasons) — Phase 1 verifies. HIGH on the FTN-coverage-labels-absence finding. |
| Pitfalls | HIGH | All 22 pitfalls are sourced — most via nflverse GitHub issues and nflfastR documentation. MEDIUM only on FTN per-column NaN rates (rates not published; Phase 1 measures). |

**Overall confidence:** HIGH. The project's biggest uncertainty (FTN schema) is itself a Phase 1 deliverable.

---

*Research synthesis for: NFL defensive tendency analysis (Python 3.11 + SQLite + Jupyter portfolio piece, public GitHub, entry-level data-analyst recruiter audience). Built on parallel research outputs from STACK, FEATURES, ARCHITECTURE, and PITFALLS researchers.*
*Researched: 2026-04-29*
*Ready for roadmap: yes*
*Valid until: ~2026-07-29 — re-verify before any Phase 1 audit work begins (pandas 3.0 ecosystem and nflreadpy v0.1.x maturity are the moving variables)*
