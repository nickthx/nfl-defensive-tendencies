---
phase: 03-analytical-layer-sql-python
plan: "01"
subsystem: analysis-scaffolding
tags: [python, sqlite, jupytext, matplotlib, seaborn, sample-size]
dependency_graph:
  requires:
    - "data/nfl_defensive_tendencies.db (Phase 2 — 1,139 games / 197,362 plays / 105,556 competitive_plays)"
    - "schema/03_views.sql (competitive_plays view — locked, not modified)"
    - "etl/columns.py (SEASONS, PBP_KEYS, FTN_KEYS — not redefined here)"
  provides:
    - "analysis/_common.py — SEED, DB_PATH, get_conn, min_n_filter (imported by every Phase 3+4 notebook)"
    - "analysis/_style.py — apply_style() (imported by every Phase 3+4 notebook)"
    - "analysis/01_exploratory.ipynb — STAT-03 descriptive stats + sample-size profiling"
    - "analysis/01_exploratory.py — jupytext-paired source"
  affects:
    - "03-02 (SQL queries) — reads from competitive_plays, can import _common"
    - "03-03 (predictability modeling) — imports SEED, get_conn, min_n_filter, apply_style"
    - "Phase 4 notebooks — same import pattern"
tech_stack:
  added: []
  patterns:
    - "sqlite3.connect(detect_types=PARSE_DECLTYPES) for all DB connections"
    - "min_n_filter() returns filtered DataFrame + logs WARNING; does not raise"
    - "Path.cwd() walk for sys.path in notebooks (Path(__file__) undefined in .ipynb)"
    - "jupytext py:percent pairing; outputs cleared via nbconvert before commit"
key_files:
  created:
    - analysis/_common.py
    - analysis/_style.py
    - analysis/01_exploratory.ipynb
    - analysis/01_exploratory.py
  modified: []
decisions:
  - "SEED=42 as module-level int constant in _common.py; imported and reseeded at top of each notebook"
  - "DB_PATH resolved via Path(__file__).resolve().parent.parent / 'data' / 'nfl_defensive_tendencies.db'"
  - "get_conn() returns plain sqlite3.Connection (no SQLAlchemy, no caching)"
  - "min_n_filter() emits logging.WARNING listing (defteam, situation_id) tuples for dropped rows; does not raise"
  - "PALETTE='colorblind'; savefig.dpi=200; per-team 32-color palette deferred to Phase 4/VIZ-01"
  - "sys.path setup in notebook uses Path.cwd() walk — deviation from plan's Path(__file__) suggestion"
metrics:
  duration: "~18m"
  completed: "2026-04-30"
  tasks_completed: 3
  files_created: 4
---

# Phase 3 Plan 01: Analytical Scaffolding Summary

**One-liner:** Python analytical scaffold — `sqlite3` connection helper + `min_n_filter` + seaborn `colorblind` rcParams + jupytext-paired exploratory notebook with competitive_plays S1/S2/S3/S4 sample-size profiling.

## What Was Built

Three source files deliver the shared API that every Phase 3 and Phase 4 notebook imports:

**`analysis/_common.py`** — The DB/seed/filter module. Exports:
- `SEED: int = 42`
- `DB_PATH: Path` — resolves to `data/nfl_defensive_tendencies.db` via `__file__`
- `get_conn(db_path=DB_PATH) -> sqlite3.Connection` — opened with `detect_types=PARSE_DECLTYPES`
- `min_n_filter(df, n_col='n', n_threshold=30) -> pd.DataFrame` — drops rows below threshold, emits `logging.WARNING` with (defteam, situation_id) tuples; does NOT raise

**`analysis/_style.py`** — The matplotlib/seaborn defaults module. Exports:
- `PALETTE: str = 'colorblind'`
- `RCPARAMS: dict` — savefig.dpi=200, figure.figsize=(8,5), no top/right spines, analyst-memo font sizes
- `apply_style() -> None` — applies rcParams + palette; no side effects at import time

**`analysis/01_exploratory.ipynb` + `analysis/01_exploratory.py`** — STAT-03 deliverable. Cells:
1. Imports, `apply_style()`, `np.random.seed(SEED)`, DB exists assert
2. SITUATIONS dict (S1–S4 WHERE clauses from `docs/analysis-plan.md`)
3. Universe N count (`competitive_plays`: 105,556) + per-situation counts (S1=9,925; S2=15,559; S3=41,901; S4=10,513)
4. Per-(defteam × situation) N rollup + `.describe()` summary
5. `min_n_filter` call with dropout count report
6. League blitz rate anchor (`n_blitzers > 4` on `play_type='pass'`) via `competitive_plays JOIN ftn_play`
7. Firewall section "Exploratory; not a headline finding"

## Sample-Size Dropout Signal (Phase 4 Narrative Input)

All 128 (defteam × situation) cells across 4 seasons clear the N≥30 floor:

| Situation | Teams | N<30 dropped | Result |
|-----------|-------|--------------|--------|
| S1 — 3rd-and-long | 32 | 0 | All teams eligible |
| S2 — Red zone | 32 | 0 | All teams eligible |
| S3 — 1st-and-10 | 32 | 0 | All teams eligible |
| S4 — 2nd-and-medium | 32 | 0 | All teams eligible |

**No cells require the N/A treatment in the FINDINGS.md methodology appendix.** The 4-season scope (2022–2025, D-10) provides sufficient per-team volume even in the smallest situation (S1: 9,925 plays ÷ 32 teams = ~310 plays/team on average). The `min_n_filter` WARNING mechanism is in place for future analysis with tighter stratifications (e.g., PA-stratified S1/S4 cells in a hypothetical v2).

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Task 1: `_common.py` | b941ecc | `analysis/_common.py` |
| Task 2: `_style.py` | 8bd08c9 | `analysis/_style.py` |
| Task 3: `01_exploratory.ipynb` | a6a46bd | `analysis/01_exploratory.ipynb`, `analysis/01_exploratory.py` |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Unused imports in notebook cell removed for ruff compliance**
- **Found during:** Task 3 (ruff check on `01_exploratory.py`)
- **Issue:** The plan's Cell 2 included `import sqlite3`, `from pathlib import Path`, and `import seaborn as sns`. None of these were used in the notebook body (`sqlite3` is wrapped by `get_conn`, `Path` comes from `_common.DB_PATH`, `seaborn` is applied by `apply_style()`). Ruff F401 flagged all three.
- **Fix:** Removed the three unused imports. The `sys.path` setup added later re-introduced `Path` and `sys`, which are used.
- **Files modified:** `analysis/01_exploratory.py`
- **Commit:** a6a46bd

**2. [Rule 3 - Blocking] `Path(__file__)` undefined in .ipynb cells — switched to `Path.cwd()` walk**
- **Found during:** Task 3 (nbconvert execution failure)
- **Issue:** The plan's deviation protocol explicitly documents this risk: "`Path(__file__)` doesn't work in `.ipynb`; use `Path.cwd()` or hardcoded relative paths." The notebook's sys.path setup used `Path(__file__)` which raises `NameError` in Jupyter kernels. nbconvert execution failed on cell 1.
- **Fix:** Replaced `Path(__file__).resolve().parent.parent` with a `Path.cwd()` walk — climbs candidate directories until one containing an `analysis/` subdirectory is found. Works correctly when nbconvert is invoked from the repo root (the standard invocation).
- **Files modified:** `analysis/01_exploratory.py`, `analysis/01_exploratory.ipynb` (re-synced)
- **Commit:** a6a46bd

**3. [Rule 1 - Bug] ruff E402 on post-sys.path imports — added `# noqa: E402`**
- **Found during:** Task 3 (ruff check after sys.path block was added)
- **Issue:** `import numpy`, `import pandas`, `from analysis._common import ...`, `from analysis._style import ...` all appear after the sys.path manipulation block. Ruff E402 ("module level import not at top of file") flagged all four.
- **Fix:** Added `# noqa: E402` to the four affected imports. This is the canonical suppression pattern for intentional post-path-setup imports in Jupyter-adjacent scripts.
- **Files modified:** `analysis/01_exploratory.py`
- **Commit:** a6a46bd

## Known Stubs

None. All data reads from the live Phase 2 SQLite DB; no hardcoded placeholder values.

## Threat Flags

None. The new files are read-only analytics against a local SQLite file: no new network endpoints, no auth paths, no file write surface, no PII. SQL WHERE clauses in the exploratory notebook are hardcoded literals in the SITUATIONS dict (not user input). Threat model from PLAN.md holds as-is.

## Self-Check: PASSED

| Item | Status |
|------|--------|
| `analysis/_common.py` exists | FOUND |
| `analysis/_style.py` exists | FOUND |
| `analysis/01_exploratory.ipynb` exists | FOUND |
| `analysis/01_exploratory.py` exists | FOUND |
| commit b941ecc (_common.py) | FOUND |
| commit 8bd08c9 (_style.py) | FOUND |
| commit a6a46bd (01_exploratory) | FOUND |
