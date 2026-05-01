# Roadmap: NFL Defensive Tendencies

**Created:** 2026-04-29
**Granularity:** coarse (3–5 phases)
**Parallelization:** enabled (within-phase)
**Coverage:** 56 / 56 v1 requirements mapped

---

## Overview

The journey: bootstrap a clean Python 3.11 repo and audit the actual public FTN schema (Phase 1), build a reproducible parquet→SQLite data layer with the project-wide `competitive_plays` view (Phase 2), execute the SQL + Python analytical work that produces a normalized predictability index and chi-square evidence on pre-registered situations (Phase 3), and ship a hand-written FINDINGS.md memo + README to a public GitHub repo via the GitHub MCP (Phase 4). Phases run serially; plans within each phase parallelize where the dependency graph allows.

**Bundling rationale (relative to the synthesizer's 6-phase prior):**
- **Bootstrap + FTN Audit → Phase 1.** They share a single context (one venv, one new repo) and AUDIT-01 can start the moment BOOT-07 verifies a clean install. Splitting them adds a phase boundary with no real handoff.
- **ETL + Schema → Phase 2.** SCHEMA-03 (`competitive_plays`) is the single source of truth for every analytical query and lives downstream of `etl/build_db.py`'s table creation. They are one data-layer phase.
- **SQL + Python → Phase 3.** Once SQLite + the view exist, queries and notebooks are independent build targets that converge on the same artifacts (`min_n_filter`, predictability index). Bundled to surface in-phase parallelism.
- **Visualization + Documentation + Ship → Phase 4.** Visualizations feed FINDINGS.md and README; both gate the ship. Keeping these as one phase lets the "story" success criteria stay coherent (hero chart visible, glossary defined, attribution present, repo live).

This collapses the 6-phase prior to 4 phases per the **coarse** granularity constraint without losing any deliverable.

---

## Phases

- [x] **Phase 1: Foundation & FTN Pivot Calibration** - Bootstrap the repo and lock the 3–4 anchor defensive dimensions (completed 2026-04-29; 4 anchors locked: n_blitzers, n_pass_rushers, is_play_action, n_offense_backfield)
- [x] **Phase 2: Data Layer (ETL + SQLite Schema)** - Reproducible parquet→SQLite pipeline with `competitive_plays` view (completed 2026-04-29; 1,139 games / 197,362 plays / 185,215 ftn_play / 105,556 competitive_plays)
- [x] **Phase 3: Analytical Layer (SQL + Python)** - 8 queries, predictability index, chi-square evidence (completed 2026-04-30; 11 execution commits, 17/17 REQ-IDs delivered, 4 substantive findings — see STATE.md D-14..D-17)
- [ ] **Phase 4: Story & Ship (Viz + Docs + Public GitHub)** - FINDINGS.md memo, hand-written README, public repo via GitHub MCP

---

## Phase Details

### Phase 1: Foundation & FTN Pivot Calibration
**Goal**: Repo skeleton, pinned environment, and the calibrated dimension set are in place — every downstream phase builds on a verified public-FTN schema reality.
**Depends on**: Nothing (first phase)
**Requirements**: BOOT-01, BOOT-02, BOOT-03, BOOT-04, BOOT-05, BOOT-06, BOOT-07, AUDIT-01, AUDIT-02, AUDIT-03, AUDIT-04, AUDIT-05, AUDIT-06, AUDIT-07
**Success Criteria** (what must be TRUE):
  1. A fresh Python 3.11 venv installs `requirements.txt` cleanly and imports `nfl_data_py` without error (BOOT-02, BOOT-05, BOOT-07).
  2. `audit/ftn_null_profile.csv` exists and shows per-column NaN rate by `play_type` for FTN columns across 2022–2025 (AUDIT-01, AUDIT-02).
  3. `docs/ftn-schema-audit.md` names the 3–4 chosen anchor defensive dimensions with a defensible, NaN-rate-aware rationale (AUDIT-03).
  4. `docs/analysis-plan.md` pre-registers 3–5 situations the FINDINGS.md memo will claim findings on (AUDIT-04).
  5. The public repo name is locked in writing and the README hook is rewritten in plain English to match the post-pivot framing (AUDIT-05, AUDIT-06, AUDIT-07).
**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md — Bootstrap (BOOT-01..07): repo skeleton, pinned `requirements.txt`, `.gitignore`, `pyproject.toml` ruff config, `.python-version`, README skeleton, fresh-venv install verification (completed 2026-04-29)
- [x] 01-02-PLAN.md — FTN Audit (AUDIT-01..07): `00_data_audit.ipynb`, null-profile CSV, schema-audit narrative, pre-registered analysis plan, lock repo name, rewrite SPEC business questions and README hook to post-pivot framing (completed 2026-04-29)

**In-phase parallelism:** 01-01 (Bootstrap) and 01-02 (Audit) are **serial** — the audit notebook needs the repo skeleton (`analysis/`, `audit/`, `docs/` directories from BOOT-01) and a working venv (BOOT-07) before it can run. Within 01-01, all artifact files (`requirements.txt`, `.gitignore`, `pyproject.toml`, `.python-version`, README skeleton) are independent and parallel-writable; install verification (BOOT-07) is the single serial gate at the end. Within 01-02, AUDIT-01 → AUDIT-02 → AUDIT-03 are serial (each depends on the previous artifact); AUDIT-04 (analysis plan), AUDIT-05 (repo name), AUDIT-06 (SPEC rewrite), AUDIT-07 (README hook) can run in parallel after AUDIT-03 lands.
**UI hint**: no

---

### Phase 2: Data Layer (ETL + SQLite Schema)
**Goal**: A single command (`python -m etl.run`) produces a verified, indexed SQLite database with the `competitive_plays` view — the reproducible foundation every analytical query reads from.
**Depends on**: Phase 1 (anchor dimensions and column whitelist must be locked)
**Requirements**: ETL-01, ETL-02, ETL-03, ETL-04, ETL-05, ETL-06, SCHEMA-01, SCHEMA-02, SCHEMA-03
**Success Criteria** (what must be TRUE):
  1. Running `python -m etl.run` on a fresh clone produces `data/nfl_defensive_tendencies.db` with non-empty `games`, `plays`, and `ftn_play` tables; cold-cache run completes in ≤10 minutes, warm-cache in ≤5 (ETL-05, ETL-06).
  2. The FTN↔pbp join uses `validate='one_to_one'` on `(nflverse_game_id, nflverse_play_id)` and post-join match-rate exceeds 0.95 — verified by an in-script assertion that fails loudly if violated (ETL-04).
  3. Re-running `python -m etl.run` on a populated cache is idempotent (no re-downloads, no duplicate rows) (ETL-01, ETL-02).
  4. `SELECT COUNT(*) FROM competitive_plays` returns a non-zero row count, filtered to `play_type IN ('pass','run')` AND `wp BETWEEN 0.05 AND 0.95` AND excluding 2-minute drill / OT (SCHEMA-03).
  5. Composite indexes on `(down, ydstogo, yardline_100)` and `(defteam, season)` plus `(game_id, play_id)` PKs exist on `plays` and `ftn_play` (SCHEMA-01, SCHEMA-02).
**Plans:** 2 plans

Plans:
- [ ] 02-01-PLAN.md — SQLite Schema (SCHEMA-01..03): `schema/01_create_tables.sql`, `schema/02_indexes.sql`, `schema/03_views.sql` with the locked `competitive_plays` view definition (project-wide single source of truth)
- [ ] 02-02-PLAN.md — ETL Pipeline (ETL-01..06): `etl/__init__.py`, `etl/columns.py` (SSOT), `etl/load_pbp.py`, `etl/load_ftn.py` (year-by-year idempotent), `etl/build_db.py` (`validate='one_to_one'` + match-rate assert), `etl/run.py` (zero-flag CLI + D-16 summary log)

**In-phase parallelism:** 02-01 (Schema) and 02-02 (ETL) **start in parallel** — schema files are static SQL and the ETL loaders (`load_pbp.py`, `load_ftn.py`, `columns.py`) don't depend on schema. They **converge serially** at `build_db.py`, which executes the schema files and applies the column whitelist. Within 02-02, `load_pbp.py`, `load_ftn.py`, and `columns.py` are independent and parallel; `build_db.py` is serial after them; `run.py` is the final assembly. SCHEMA-03 (`competitive_plays`) MUST be complete before any QUERY-* requirement starts in Phase 3 — this is enforced by the phase boundary.
**UI hint**: no

---

### Phase 3: Analytical Layer (SQL + Python)
**Goal**: Every business question from the analysis plan has a SQL artifact and Python statistical evidence — including the normalized predictability index, at least one chi-square test, and sample-size-disciplined claims.
**Depends on**: Phase 2 (SQLite + `competitive_plays` view must exist)
**Requirements**: QUERY-01, QUERY-02, QUERY-03, QUERY-04, QUERY-05, QUERY-06, QUERY-07, QUERY-08, QUERY-09, STAT-01, STAT-02, STAT-03, STAT-04, STAT-05, STAT-06, STAT-07, STAT-08
**Success Criteria** (what must be TRUE):
  1. All 8 queries (`queries/01_*.sql` … `queries/08_*.sql`) reference `competitive_plays`, run end-to-end against the SQLite DB, and use window functions + CTEs + at least one cross-source join with header documentation (QUERY-01..09).
  2. The first cell of `analysis/02_predictability_modeling.ipynb` defines and applies the normalization scheme — `H/log(k)` over fixed support OR KL-from-league-baseline — with explicit rationale; the predictability index is computed *conditional on situation* and surfaced as a 0–100 per-team metric (STAT-04, STAT-05).
  3. At least one chi-square test on a pre-registered situation from `docs/analysis-plan.md` reports test statistic, effect size, and a Wilson 95% CI on the proportion (STAT-06).
  4. `analysis/_common.py` exposes `SEED=42`, a SQLite connection helper, and `min_n_filter()`; `min_n_filter` is applied to every analytical claim (N≥30 baseline, N≥100 for "extreme", N≥15 only with explicit narrative flag) (STAT-01, STAT-07).
  5. At least one sensitivity check exists — same headline finding computed with vs without the `competitive_plays` filter — with both numbers documented in the notebook (STAT-08).
**Plans:** 3 plans

Plans:
- [x] 03-01-PLAN.md — Python analytical scaffolding (STAT-01, STAT-02, STAT-03) — `_common.py`, `_style.py`, `01_exploratory.ipynb` (descriptive stats + sample-size profiling, flags cells <N=30) (completed 2026-04-30)
- [x] 03-02-PLAN.md — SQL Analysis Layer (QUERY-01..09) — 8 query files with documented headers, all referencing `competitive_plays` (completed 2026-04-30)
- [x] 03-03-PLAN.md — Predictability Modeling (STAT-04, STAT-05, STAT-06, STAT-07, STAT-08) — `02_predictability_modeling.ipynb` with normalization in cell 1, chi-square + effect size + Wilson CI on a pre-registered situation, sensitivity check, `min_n_filter` enforcement (completed 2026-04-30)

**In-phase parallelism:** 03-01 (scaffolding) is the serial **prerequisite** — `_common.py`, `_style.py`, and the exploratory notebook must exist before 03-02 and 03-03 can import from them. After 03-01 completes, **03-02 (queries) and 03-03 (predictability modeling) run in parallel** — they read from the same SQLite tables but produce independent artifacts. Within 03-02, all 8 query files are independent and parallel-writable; QUERY-09 (cross-cutting compliance check on header docs / `competitive_plays` references) is the final serial verification. Within 03-03, STAT-04 (normalization scheme — FIRST cell) gates STAT-05/STAT-06/STAT-07/STAT-08; once locked, the chi-square (STAT-06) and sensitivity check (STAT-08) can run in parallel.
**UI hint**: no

---

### Phase 4: Story & Ship (Viz + Docs + Public GitHub)
**Goal**: The recruiter signal is delivered — a hand-written README with hero chart above the fold, a memo-style FINDINGS.md, and a public GitHub repo configured via the GitHub MCP (description, topics, social preview, pinned).
**Depends on**: Phase 3 (predictability index + chi-square evidence must exist for the story)
**Requirements**: VIZ-01, VIZ-02, VIZ-03, VIZ-04, VIZ-05, DOC-01, DOC-02, DOC-03, DOC-04, DOC-05, DOC-06, DOC-07, DOC-08, SHIP-01, SHIP-02, SHIP-03, SHIP-04, SHIP-05, SHIP-06, SHIP-07, SHIP-08
**Success Criteria** (what must be TRUE):
  1. Opening the public repo URL in a non-author browser shows the hero chart above the fold, 3–4 stat-first bullet findings, a Mermaid architecture diagram, a 5-command setup block, and a 6-term glossary — all hand-written, no AI-template emoji headers (DOC-03, DOC-04, DOC-05, DOC-06, VIZ-02).
  2. `findings/FINDINGS.md` renders on GitHub as a memo (TL;DR → 5–7 named insights with N inline → methodology appendix → limitations → FTN+nflverse attribution); every claim states N inline with the tiered N≥30/100/15-flag discipline visible (DOC-01, DOC-02, DOC-07).
  3. A fresh clone on a clean machine runs `pip install -r requirements.txt` + `python -m etl.run` + `Restart and Run All` on every notebook with no errors; all PNGs in `findings/images/` regenerate; notebook outputs are cleared on disk (VIZ-01, VIZ-04, VIZ-05, SHIP-02).
  4. A single GitHub Actions workflow runs `ruff check` + ETL-module import smoke on push (no notebook execution) and is green on the first push to `main` (SHIP-01).
  5. The public GitHub repo is created via the GitHub MCP with description (~70 chars), 5–8 topics, social preview image (1280×640 from hero chart), and is pinned to Nick's profile via the MCP — verified in a non-author browser (SHIP-03, SHIP-04, SHIP-05, SHIP-07).
  6. `du -sh .git/` is under 50 MB and commit history contains no `WIP` / `asdf` / scratch messages (SHIP-06).
**Plans:** 3 plans

Plans:
- [x] 04-01-PLAN.md — Visualizations + S3 exploratory chi-square (VIZ-01..05) — `analysis/03_visualizations.ipynb` exports hero PNG (`findings/images/01_predictability_ranking.png`, portrait 8x11, fixed 0-100 axis), KL-vs-H rank-rank scatter (`findings/images/02_kl_vs_h_scatter.png`, inverted axes, 8 callouts via adjustText), top-12 social-preview source (`findings/images/01_predictability_ranking_top12.png`, 1280x640); appends S3 PA × blitz exploratory chi-square cells to `analysis/02_predictability_modeling.py` with OR-delta-vs-S1 first-class output; pins `adjustText` in requirements.txt (completed 2026-04-30)
- [ ] 04-02-PLAN.md — Documentation + cross-doc reconciliation (DOC-01..08) — `findings/FINDINGS.md` memo (TL;DR + 6 named insights + 3 thematic methodology blocks + 4 appendix tables + 5-item Limitations + attribution); README hand-rewrite (hero PNG above the fold, Mermaid data-flow diagram, 5-command setup, 6-term glossary, attribution, Known Issues); `data/README.md` extension; D-48 5-site `n_blitzers > 0` reconciliation sweep (PROJECT.md L58 / 03-CONTEXT.md D-02 / docs/ftn-schema-audit.md / README glossary / analysis/01_exploratory.py L163) with D-49 post-sweep grep verification
- [ ] 04-03-PLAN.md — CI workflow + ship sequence (SHIP-01..08) — `.github/workflows/ci.yml` (single job: ruff + import smoke + SHIP-08 placeholder regex; push+PR triggers; concurrency cancel-in-progress); fresh-venv reproducibility scripts (POSIX + Windows); `LICENSE` (MIT); private-then-public GitHub MCP ship flow with branch protection on main gated on `lint-and-import-smoke`; social preview + profile pin (MCP-or-UI fallback path logged); commit-history audit (SHIP-06); incognito desktop + mobile non-author verification (SHIP-07, D-42)

**In-phase parallelism:** 04-01 (Visualizations) is the serial **prerequisite** — the hero PNG must exist before README and FINDINGS.md can embed it. After 04-01 completes, **04-02 (Documentation) draft can run in parallel with the early steps of 04-03** (the GitHub Actions workflow file SHIP-01 and the fresh-venv reproducibility script SHIP-02 don't need the README to be complete). The actual ship gate (SHIP-03..05 — repo creation via GitHub MCP, social preview upload, pinning) is **strictly serial after 04-02 completes** — you can't push to a public repo with a half-written README. SHIP-06 (commit-history audit) and SHIP-07 (non-author browser verification) are the final serial gates. Within 04-02, FINDINGS.md and README can draft in parallel after 04-01 locks the image filenames; `data/README.md` (DOC-08) is independent and parallel.
**UI hint**: no

---

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4. Decimal phases inserted only via `/gsd-insert-phase` if urgent issues arise.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & FTN Pivot Calibration | 2/2 | Complete | 2026-04-29 |
| 2. Data Layer (ETL + SQLite Schema) | 2/2 | Complete | 2026-04-29 |
| 3. Analytical Layer (SQL + Python) | 3/3 | Complete | 2026-04-30 |
| 4. Story & Ship (Viz + Docs + Public GitHub) | 1/3 | In Progress | - |

---

## Coverage Validation

| Phase | Requirement IDs | Count |
|-------|----------------|-------|
| 1 | BOOT-01..07, AUDIT-01..07 | 14 |
| 2 | ETL-01..06, SCHEMA-01..03 | 9 |
| 3 | QUERY-01..09, STAT-01..08 | 17 |
| 4 | VIZ-01..05, DOC-01..08, SHIP-01..08 | 21 |
| **Total** | | **56 / 56** |

**Orphans:** none.
**Duplicates:** none.

---

*Roadmap created: 2026-04-29*
*Granularity: coarse (4 phases). Parallelization: enabled within phases. Cross-phase ordering: strictly serial by data-flow dependency.*
