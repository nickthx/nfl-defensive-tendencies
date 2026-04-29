# Requirements: NFL Defensive Tendencies

**Defined:** 2026-04-29
**Core Value:** A recruiter can clone the repo, run a single command, and within 2 minutes understand both the analytical insight and the engineering rigor behind it.

REQ-IDs are grouped by architectural layer. Phase mapping is filled in by the roadmapper (Traceability section).

---

## v1 Requirements

### Bootstrap (foundation discipline)

- [x] **BOOT-01**: Skeleton repo created with directory tree per `.planning/research/SUMMARY.md` (data/, etl/, schema/, queries/, analysis/, findings/, .planning/ committed)
- [x] **BOOT-02**: `requirements.txt` pins the Consolidated Stack: `nfl_data_py==0.3.3`, `pandas>=2.1,<2.3`, `numpy>=1.26,<2.0`, `pyarrow>=15,<22`, `scipy>=1.13,<1.18`, `matplotlib>=3.8,<3.11`, `seaborn==0.13.2`, `jupyterlab>=4.2,<4.6`, `ipykernel>=6.29,<8`, `jupytext>=1.16,<2`, `nbconvert>=7.16,<8`, `ruff>=0.6,<1.0`
- [x] **BOOT-03**: `.gitignore` excludes `data/raw/`, `*.db`, `.env*`, `__pycache__/`, `.ipynb_checkpoints/`, scratch files, `venv/`
- [x] **BOOT-04**: `pyproject.toml` houses `[tool.ruff]` config only (line-length=100, target=py311, select E/F/I/B/UP)
- [x] **BOOT-05**: `.python-version` pinned to `3.11`
- [x] **BOOT-06**: README skeleton with empty section headers (no claims yet)
- [x] **BOOT-07**: `requirements.txt` install verified clean on a fresh Python 3.11 venv (with documented two-step install workaround for nfl_data_py upstream metadata mismatch)

### FTN Audit / Pivot Calibration

- [ ] **AUDIT-01**: `analysis/00_data_audit.ipynb` calls `nfl.import_ftn_data([2022, 2023, 2024])`, prints column inventory, computes per-column NaN rates by `play_type`
- [ ] **AUDIT-02**: `audit/ftn_null_profile.csv` lands NaN rates per FTN column × play_type for 2022–2024
- [ ] **AUDIT-03**: `docs/ftn-schema-audit.md` written narrative confirming the public-FTN reality and naming the 3–4 anchor dimensions chosen
- [ ] **AUDIT-04**: `docs/analysis-plan.md` pre-registers 3–5 situations the FINDINGS.md memo will claim findings on (multiple-comparisons discipline)
- [ ] **AUDIT-05**: Public GitHub repo name locked (default: `nfl-defensive-tendencies`)
- [ ] **AUDIT-06**: SPEC's 8 business questions reframed to anchor dimensions chosen in AUDIT-03 (in-place rewrite of SPEC.md or addendum)
- [ ] **AUDIT-07**: README hook rewritten to match the post-pivot framing (plain-English problem statement)

### ETL Pipeline

- [ ] **ETL-01**: `etl/load_pbp.py` pulls nflfastR play-by-play via `nfl_data_py.import_pbp_data` to `data/raw/pbp_<year>.parquet` (idempotent — skips if cached)
- [ ] **ETL-02**: `etl/load_ftn.py` pulls FTN charting via `nfl_data_py.import_ftn_data` to `data/raw/ftn_<year>.parquet` (idempotent)
- [ ] **ETL-03**: `etl/columns.py` defines column whitelist + rename map as the single source of truth for the curated schema
- [ ] **ETL-04**: `etl/build_db.py` reads parquet caches, applies whitelist, joins FTN↔pbp on `nflverse_game_id` + `nflverse_play_id` with `validate='one_to_one'` AND post-join match-rate assertion `>0.95`
- [ ] **ETL-05**: `etl/run.py` is a single CLI entry — `python -m etl.run` runs load_pbp + load_ftn + build_db end-to-end with progress logging
- [ ] **ETL-06**: ETL completes on a stock laptop in ≤5 minutes after raw caches are populated; ≤10 minutes from a cold cache

### SQLite Schema

- [ ] **SCHEMA-01**: `schema/01_create_tables.sql` defines `games`, `plays`, `ftn_play` (lightly normalized; `(game_id, play_id)` PK on `plays` and `ftn_play`)
- [ ] **SCHEMA-02**: `schema/02_indexes.sql` creates composite indexes for situational queries: `(down, ydstogo, yardline_100)`, `(defteam, season)`, plus the PKs
- [ ] **SCHEMA-03**: `schema/03_views.sql` defines `competitive_plays` view filtering on `play_type IN ('pass','run')` AND `wp BETWEEN 0.05 AND 0.95` AND excluding 2-minute-drill / OT — referenced by every analytical query

### SQL Analysis Layer

- [ ] **QUERY-01**: `queries/01_tendency_distribution_by_team.sql` — league baseline + team deviation on the chosen anchor dimension(s)
- [ ] **QUERY-02**: `queries/02_blitz_rate_by_down_and_distance.sql` (or equivalent — exact dimension chosen in AUDIT-03)
- [ ] **QUERY-03**: `queries/03_red_zone_vs_midfield.sql` — field-zone slicing
- [ ] **QUERY-04**: `queries/04_epa_allowed_by_<dim>.sql` — EPA allowed by tendency dimension
- [ ] **QUERY-05**: `queries/05_third_long_pressure_tendencies.sql` — 3rd-and-long pressure / blitz rate
- [ ] **QUERY-06**: `queries/06_play_action_response.sql` — defensive response to play-action
- [ ] **QUERY-07**: `queries/07_situational_predictability_score.sql` — entropy by team × situation (raw inputs for the index)
- [ ] **QUERY-08**: `queries/08_week_over_week_drift.sql` — within-season tendency drift
- [ ] **QUERY-09**: All queries reference `competitive_plays`, include header documenting question + result shape + caveats, use window functions + CTEs + at least one cross-source join

### Python Statistical Layer

- [ ] **STAT-01**: `analysis/_common.py` exposes `SEED=42`, a SQLite connection helper, and a `min_n_filter(df, n_threshold)` helper
- [ ] **STAT-02**: `analysis/_style.py` defines portfolio matplotlib rcParams (savefig.dpi=200, font sizes, color palette)
- [ ] **STAT-03**: `analysis/01_exploratory.ipynb` — descriptive stats + sample-size profiling per situation; flags any cells <N=30
- [ ] **STAT-04**: `analysis/02_predictability_modeling.ipynb` first cell defines the normalization scheme — `H/log(k)` over fixed support OR KL-from-league-baseline — with rationale
- [ ] **STAT-05**: Predictability Index computed *conditional on situation*, surfaced as a 0–100 per-team metric
- [ ] **STAT-06**: At least one chi-square test (with effect size + Wilson 95% CI on the proportion) on a pre-registered situation from `docs/analysis-plan.md`
- [ ] **STAT-07**: `min_n_filter()` applied to every analytical claim — N≥30 for tendency, N≥100 for "extreme" (>75%) claims, N≥15 only with explicit narrative flag
- [ ] **STAT-08**: At least one sensitivity check — same headline finding computed with vs without the `competitive_plays` filter; both numbers documented

### Visualizations

- [ ] **VIZ-01**: `analysis/03_visualizations.ipynb` exports all final PNGs to `findings/images/` using `_style.py` rcParams (consistent look)
- [ ] **VIZ-02**: Hero chart (predictability index leaderboard or equivalent) saved as `findings/images/01_predictability_ranking.png` and embedded in README first scroll
- [ ] **VIZ-03**: At least one non-bar-chart visualization (heatmap or small-multiples grid) for analytical depth
- [ ] **VIZ-04**: All notebooks have outputs cleared via `nbconvert --clear-output --inplace` before commit (figures live only in `findings/images/`)
- [ ] **VIZ-05**: All notebooks run end-to-end on a fresh kernel from a clean clone — verified at ship gate

### Documentation (FINDINGS + README + data README)

- [ ] **DOC-01**: `findings/FINDINGS.md` memo structured TL;DR → 5–7 named insights → methodology appendix → limitations section → FTN + nflverse attribution
- [ ] **DOC-02**: Every FINDINGS.md claim states N inline; tiered sample-size discipline visible (N≥30 / 100 / 15-with-flag)
- [ ] **DOC-03**: `README.md` hand-written (no AI-template emoji section headers, no "Welcome to my project!" tone), hero PNG above the fold, 3–4 stat-first bullet findings
- [ ] **DOC-04**: README has a Mermaid architecture diagram (data flow, not file tree)
- [ ] **DOC-05**: README has a 5-command setup block + reproducibility budget callout (≤5 commands, ≤10 minutes on a stock laptop)
- [ ] **DOC-06**: README has a glossary block defining 6 football terms (down, distance, EPA, blitz, RPO, predictability index) in plain English
- [ ] **DOC-07**: README includes FTN + nflverse CC-BY-SA attribution and a Known Issues section noting `nfl_data_py` archival
- [ ] **DOC-08**: `data/README.md` documents the gitignored `.db`, the regeneration path, and the parquet cache layout

### Ship

- [ ] **SHIP-01**: Single GitHub Actions workflow runs `ruff check` + ETL-module import smoke on push (no notebook execution)
- [ ] **SHIP-02**: Fresh-venv install + `python -m etl.run` + Restart-and-Run-All on every notebook passes on a clean machine before push
- [ ] **SHIP-03**: Public GitHub repo created via the GitHub MCP with description (~70 chars), 5–8 topics (`nfl-analytics`, `data-analysis`, `python`, `sqlite`, `jupyter`, `nfl-data-py`, `sports-analytics`)
- [ ] **SHIP-04**: Social preview image (1280×640, derived from hero chart) configured via the GitHub MCP
- [ ] **SHIP-05**: Repo pinned to Nick's GitHub profile via the MCP
- [ ] **SHIP-06**: Commit history reviewed and clean (no `WIP`, no `asdf`); `du -sh .git/` < 50 MB
- [ ] **SHIP-07**: Final push to `main` verified on a non-author browser session (link works, hero chart loads, glossary visible)

---

## v2 Requirements (deferred — tracked but not in v1 roadmap)

### Library Migration

- **V2-LIB-01**: Migrate from `nfl_data_py` to `nflreadpy` once it stabilizes; add `.to_pandas()` boundary in loaders
- **V2-LIB-02**: Re-pin `numpy>=2.0` once the loader migration removes the `np.float_` constraint

### Analytical Depth

- **V2-PERS-01**: Add personnel-grouping context (11 personnel, 12 personnel, etc.) as additional analysis dimension
- **V2-ML-01**: Train a simple defensive-tendency classifier on situational features (logistic regression baseline)
- **V2-VIZ-01**: Animated play visualization (only if a tracking-data source becomes available)

### Polish

- **V2-DOC-01**: Inter-rater agreement disclosure for FTN's subjective fields (`is_play_action`, `is_rpo`) beyond rounding
- **V2-DOC-02**: Custom hero-chart social preview iteration based on first-month repo analytics

---

## Out of Scope (explicitly excluded)

| Feature | Reason |
|---------|--------|
| Cover 0/1/2/3/4/6, man/zone labels | Not in public FTN data — part of FTN's paid commercial product; not redistributable |
| Streamlit / Plotly Dash / web dashboard | Deployment overhead without recruiter-signal upside; static notebook + memo conveys the same skills |
| Big Data Bowl tracking data + Kaggle dependency | Replaced by `nfl_data_py`; eliminates manual download friction |
| Postgres / DuckDB / Docker / cloud DB | SQLite is sufficient and zero-friction for clone-and-run |
| Committing the `.db` file | 200–400 MB exceeds GitHub's 100 MiB hard limit; ETL regeneration is part of the demo |
| `nflreadpy` migration in v1 | Considered (maintained successor) and rejected for v1; deferred to V2-LIB-01 |
| Play-call prediction model | Scope creep; tendency analysis is the v1 ceiling |
| Betting / wagering / DFS framing | Out of audience scope; keeps tone analytical, not speculative |
| Real-time / in-season auto-updating | Static analysis on fixed seasons (2022–2024) |
| PFF or other paid data | Not redistributable in a public portfolio repo |
| Video / film breakdown | Out of scope for a tabular-data project |
| AI-generated README boilerplate (emoji section headers, "Welcome" tone) | Negative recruiter signal — explicitly avoided per features research |
| `tests/` directory with trivial cargo-cult asserts | Would waste signal; assertions live inside ETL (validate=one_to_one, match-rate >0.95) |
| Custom logo / branded header image | Visual noise without analytical signal |
| Excessive shields.io badge soup (>5 badges) | Pattern that recruiters associate with unfinished portfolios |
| Notebook-execution CI (`nbconvert --execute` in GitHub Actions) | Pulls 150 MB on every run, flaky; ship gate handles this manually |

---

## Traceability

Populated by the roadmapper after `ROADMAP.md` is written. Each v1 requirement maps to exactly one phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BOOT-01 | Phase 1 | Complete |
| BOOT-02 | Phase 1 | Complete |
| BOOT-03 | Phase 1 | Complete |
| BOOT-04 | Phase 1 | Complete |
| BOOT-05 | Phase 1 | Complete |
| BOOT-06 | Phase 1 | Complete |
| BOOT-07 | Phase 1 | Complete |
| AUDIT-01 | Phase 1 | Pending |
| AUDIT-02 | Phase 1 | Pending |
| AUDIT-03 | Phase 1 | Pending |
| AUDIT-04 | Phase 1 | Pending |
| AUDIT-05 | Phase 1 | Pending |
| AUDIT-06 | Phase 1 | Pending |
| AUDIT-07 | Phase 1 | Pending |
| ETL-01 | Phase 2 | Pending |
| ETL-02 | Phase 2 | Pending |
| ETL-03 | Phase 2 | Pending |
| ETL-04 | Phase 2 | Pending |
| ETL-05 | Phase 2 | Pending |
| ETL-06 | Phase 2 | Pending |
| SCHEMA-01 | Phase 2 | Pending |
| SCHEMA-02 | Phase 2 | Pending |
| SCHEMA-03 | Phase 2 | Pending |
| QUERY-01 | Phase 3 | Pending |
| QUERY-02 | Phase 3 | Pending |
| QUERY-03 | Phase 3 | Pending |
| QUERY-04 | Phase 3 | Pending |
| QUERY-05 | Phase 3 | Pending |
| QUERY-06 | Phase 3 | Pending |
| QUERY-07 | Phase 3 | Pending |
| QUERY-08 | Phase 3 | Pending |
| QUERY-09 | Phase 3 | Pending |
| STAT-01 | Phase 3 | Pending |
| STAT-02 | Phase 3 | Pending |
| STAT-03 | Phase 3 | Pending |
| STAT-04 | Phase 3 | Pending |
| STAT-05 | Phase 3 | Pending |
| STAT-06 | Phase 3 | Pending |
| STAT-07 | Phase 3 | Pending |
| STAT-08 | Phase 3 | Pending |
| VIZ-01 | Phase 4 | Pending |
| VIZ-02 | Phase 4 | Pending |
| VIZ-03 | Phase 4 | Pending |
| VIZ-04 | Phase 4 | Pending |
| VIZ-05 | Phase 4 | Pending |
| DOC-01 | Phase 4 | Pending |
| DOC-02 | Phase 4 | Pending |
| DOC-03 | Phase 4 | Pending |
| DOC-04 | Phase 4 | Pending |
| DOC-05 | Phase 4 | Pending |
| DOC-06 | Phase 4 | Pending |
| DOC-07 | Phase 4 | Pending |
| DOC-08 | Phase 4 | Pending |
| SHIP-01 | Phase 4 | Pending |
| SHIP-02 | Phase 4 | Pending |
| SHIP-03 | Phase 4 | Pending |
| SHIP-04 | Phase 4 | Pending |
| SHIP-05 | Phase 4 | Pending |
| SHIP-06 | Phase 4 | Pending |
| SHIP-07 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 55 total
- Mapped to phases: 55 ✓
- Unmapped: 0

**Phase distribution:**
- Phase 1 (Foundation & FTN Pivot Calibration): 14 requirements (BOOT-01..07, AUDIT-01..07)
- Phase 2 (Data Layer): 9 requirements (ETL-01..06, SCHEMA-01..03)
- Phase 3 (Analytical Layer): 17 requirements (QUERY-01..09, STAT-01..08)
- Phase 4 (Story & Ship): 20 requirements (VIZ-01..05, DOC-01..08, SHIP-01..07)

---

*Requirements defined: 2026-04-29*
*Last updated: 2026-04-29 — Traceability table populated by roadmapper (4-phase coarse roadmap)*
