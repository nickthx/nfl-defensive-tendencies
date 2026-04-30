# Architecture Research

**Domain:** Solo-author tabular data-analytics portfolio project (Python + SQLite + Jupyter, pulling from `nfl_data_py`)
**Researched:** 2026-04-29
**Confidence:** HIGH for structure / data flow / reproducibility recommendations; MEDIUM for FTN+pbp row-volume estimates (verifiable in Phase 1 only); HIGH-but-cautionary on `nfl_data_py` deprecation (a real risk this project must absorb).

---

## Critical Up-Front Findings (read before anything else)

Two findings reshape the architecture. They are surfaced here, not buried.

### 1. `nfl_data_py` is deprecated as of Sept 2025 [VERIFIED: PyPI + nflverse README]

The library still works; the GitHub repo was archived 2025-09-25. The maintainers redirect users to **`nflreadpy`** (Polars-first, currently v0.1.5, marked **experimental** by its own authors). [VERIFIED: pypi.org/project/nflreadpy/, nflverse/nflreadpy README]

**Architectural consequence:** The SPEC says "pin `nfl_data_py` in `requirements.txt`." That decision is even more important than it looked, because the upstream package is in maintenance-only / archived state. Pin to **0.3.3** (last release, 2024-09-20). Don't auto-track. Add a comment in `requirements.txt` explaining the pin. [VERIFIED: pypi.org/project/nfl-data-py/]

A migration to `nflreadpy` is *not* recommended for this portfolio piece — it would force pandas → Polars, the upstream is v0.1.5 + experimental, and the SPEC's audience (recruiters) doesn't reward bleeding-edge tooling for this kind of work. Note the option in the README's "Future work" section and move on.

### 2. Neither FTN nor nflfastR pbp expose Cover 0–6 / man-zone labels [VERIFIED: nflreadr FTN dict, nflverse pbp dict]

FTN's full column list is 28 fields; the only defensive ones are **`n_blitzers`** and **`n_pass_rushers`**. No coverage label, no man/zone tag, no defenders-in-box, no pre-snap shell. [VERIFIED: nflreadr.nflverse.com/articles/dictionary_ftn_charting.html]

nflfastR pbp grep for "coverage" / "man_zone" / "blitz" / "defenders_in_box" / "pass_rush" returned **zero hits**. The pbp dictionary's defensive columns are limited to `defteam`, `defteam_score*`, `defteam_timeouts_remaining`, `pass_defense_1/2_player_*`, and the two-point/extra-point variants. [VERIFIED: github.com/nflverse/nflreadr/blob/main/data-raw/dictionary_pbp.csv via raw.githubusercontent.com]

**Architectural consequence:** The SPEC already names this risk and mandates a Phase 1 schema audit. The audit will confirm what this research already suggests: **the project must pivot from "coverage tendencies" to "broader defensive tendencies"** — blitz rate, pass-rusher count, play-action response, and EPA-allowed dimensions. The architecture below assumes this pivot. The repo name (`nfl-coverage-tendencies`) is a working title; both SPEC and PROJECT.md already explicitly defer the public name until after the audit.

This is not a blocker. The pivot path preserves every skill demonstrated and every business question except #1 and #6 ("Distribution baseline" and "Play-action vulnerability" rephrase trivially; #2 "Down & distance" → "blitz/pass-rusher rate by down & distance"; #3 "Field zone" → "blitz rate red-zone vs midfield"; etc.). The predictability score still works on `n_blitzers` or a discretized `n_pass_rushers` (4-/5-/6-/7+-rush bins).

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         SOURCE  (external)                        │
│   nfl_data_py.import_ftn_data()    nfl_data_py.import_pbp_data()  │
│            │                                  │                   │
└────────────┼──────────────────────────────────┼───────────────────┘
             ▼                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                      RAW CACHE  (data/raw/, parquet)              │
│        ftn_2022.parquet  ftn_2023.parquet  ftn_2024.parquet        │
│        pbp_2022.parquet  pbp_2023.parquet  pbp_2024.parquet        │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ETL  (etl/, Python)                            │
│   load_pbp.py  →  load_ftn.py  →  build_db.py  →  index.py        │
│   (read parquet, normalize, write SQLite)                         │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│              DATABASE  (data/nfl_coverage.db, SQLite)             │
│   ┌─────────┐   ┌──────────┐   ┌──────────┐                       │
│   │ games   │←──│  plays   │──→│ ftn_play │  (1:1 by play_id)     │
│   └─────────┘   └──────────┘   └──────────┘                       │
│         indexes: (down, ydstogo), (defteam, season),              │
│                  (yardline_100), (game_id, play_id) UNIQUE        │
└────────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                    ANALYSIS LAYER                                  │
│   queries/*.sql  ────────────►  analysis/*.ipynb                   │
│   (8–10 standalone SQL)         (3 notebooks: explore, model, viz) │
│                                              │                     │
└──────────────────────────────────────────────┼─────────────────────┘
                                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      OUTPUT                                        │
│   findings/images/*.png  →  findings/FINDINGS.md  →  README.md     │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|---------------|----------------|
| `data/raw/*.parquet` | Frozen snapshot of upstream data; the contract that protects you from `nfl_data_py` API drift | Parquet via `pyarrow`; written once, then read-only |
| `etl/load_pbp.py` | Pull pbp via `nfl_data_py`, write to `data/raw/pbp_<year>.parquet` if not present | Idempotent: skip if file exists unless `--force` |
| `etl/load_ftn.py` | Same for FTN | Same idempotent pattern |
| `etl/build_db.py` | Read parquet, normalize columns, write `data/nfl_coverage.db` | Drop & recreate tables on each run; deterministic |
| `etl/run.py` | Orchestrator: calls load_pbp → load_ftn → build_db → index in order | Single CLI entry point — the recruiter command |
| `schema/*.sql` | DDL for tables and indexes | Plain `.sql` files, applied by `build_db.py` |
| `data/nfl_coverage.db` | Joined, indexed analytical store | SQLite single file, ~50–100 MB |
| `queries/NN_*.sql` | One numbered SQL file per business question | Standalone, runnable via `sqlite3` CLI for verification |
| `analysis/*.ipynb` | Statistical work, visualizations, narrative | 3 notebooks (see Notebook Organization below) |
| `findings/images/*.png` | Static charts, exported from notebooks | Saved by notebook code (`fig.savefig`), checked in |
| `findings/FINDINGS.md` | Analyst memo with embedded PNGs | Hand-written, not auto-generated |
| `README.md` | 90-second value pitch + setup + 1–2 hero charts | Hand-written, links to FINDINGS.md |

---

## Recommended Project Structure

This refines (not replaces) the SPEC's structure. Changes called out below.

```
nfl-coverage-tendencies/
├── README.md
├── requirements.txt              # pinned: nfl_data_py==0.3.3, pandas, etc.
├── .gitignore                    # data/raw/, .ipynb_checkpoints/, __pycache__/, *.db-journal
├── .planning/                    # GSD process artifacts (committed; recruiter signal)
│
├── data/
│   ├── README.md                 # "How to acquire data" — points at etl/run.py
│   ├── raw/                      # gitignored; produced by etl/load_*.py
│   │   ├── pbp_2022.parquet
│   │   ├── pbp_2023.parquet
│   │   ├── pbp_2024.parquet
│   │   ├── ftn_2022.parquet
│   │   ├── ftn_2023.parquet
│   │   └── ftn_2024.parquet
│   └── nfl_coverage.db           # gitignored if >25 MB, else committed for one-click open
│
├── schema/
│   ├── 01_create_tables.sql      # CREATE TABLE games, plays, ftn_play
│   └── 02_indexes.sql            # CREATE INDEX for the situational query patterns
│
├── etl/
│   ├── __init__.py
│   ├── run.py                    # NEW: single CLI entry — `python -m etl.run`
│   ├── load_pbp.py               # nfl_data_py → data/raw/pbp_<year>.parquet
│   ├── load_ftn.py               # nfl_data_py → data/raw/ftn_<year>.parquet
│   ├── build_db.py               # parquet → SQLite (apply schema, INSERT)
│   └── columns.py                # NEW: column whitelist + rename map (single source of truth)
│
├── queries/
│   ├── 01_tendency_distribution_by_team.sql
│   ├── 02_blitz_rate_by_down_and_distance.sql
│   ├── 03_red_zone_vs_midfield.sql
│   ├── 04_epa_allowed_by_pass_rusher_count.sql
│   ├── 05_third_long_pressure_tendencies.sql
│   ├── 06_play_action_response.sql
│   ├── 07_situational_predictability_score.sql
│   └── 08_week_over_week_drift.sql
│   # Note: filenames hedge "coverage" → "tendency"/"blitz" pending Phase 1 audit
│
├── analysis/
│   ├── 01_exploratory.ipynb      # FTN schema audit + descriptive stats
│   ├── 02_predictability_modeling.ipynb  # entropy, chi-square, ranking
│   └── 03_visualizations.ipynb   # final figures, exports PNGs to findings/images/
│
└── findings/
    ├── FINDINGS.md
    └── images/                   # checked in (small PNGs, ~30–80 KB each)
        ├── 01_predictability_ranking.png
        ├── 02_blitz_by_down_distance.png
        └── ...
```

### Structure Rationale & Diffs vs SPEC

| Item | SPEC | Recommended | Why |
|------|------|-------------|-----|
| ETL entry point | 3 files (`load_ftn.py`, `load_pbp.py`, `join_and_normalize.py`) | Add `etl/run.py` as the single CLI | Recruiters run **one** command, not three. The 3 internal modules stay — `run.py` orchestrates them |
| Raw cache | Implicit ("freeze raw data dump") | Explicit `data/raw/*.parquet` | Decouples the ETL retry loop from network/API drift; parquet preserves dtypes losslessly |
| Schema-applied step | Implicit | `etl/build_db.py` reads `schema/*.sql` | Schema is data; checked-in DDL is reviewable evidence |
| Column normalization | "join_and_normalize.py" | Centralize in `etl/columns.py` | Single source of truth for column whitelisting + renaming; otherwise rename logic spreads across loaders |
| Query naming | Coverage-themed | "Tendency"-themed | Hedges against the FTN-audit pivot (Critical Finding #2) |
| `.planning/` in repo | Out of band | **Committed** | PROJECT.md already mandates this — visible engineering process is the recruiter signal |

---

## Architectural Patterns

### Pattern 1: Raw Cache (Parquet) Between Source and ETL

**What:** First ETL stage writes upstream API output verbatim to `data/raw/*.parquet`. All downstream stages read from parquet, never from `nfl_data_py` directly.

**When to use:** Whenever the upstream source has any non-zero risk of (a) API drift, (b) network flakiness, (c) being slow to re-pull on every dev iteration, or (d) being deprecated. All four conditions apply here. [VERIFIED: nfl_data_py archival status, pypi.org]

**Trade-offs:**
- **+** Network call happens once per season, not once per ETL iteration (~30s vs ~3–5 min full pull)
- **+** Reproducibility: same parquet → same DB → same charts, forever
- **+** Schema audit (Phase 1) reads parquet directly; no need to re-pull
- **−** ~150–250 MB of parquet files; gitignored, not committed
- **−** One extra concept for the recruiter to understand (mitigated: `data/README.md` explains it)

**Example (etl/load_pbp.py):**
```python
import nfl_data_py as nfl
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")

def load_pbp(years: list[int], force: bool = False) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for year in years:
        out = RAW / f"pbp_{year}.parquet"
        if out.exists() and not force:
            print(f"[skip] {out} exists")
            continue
        df = nfl.import_pbp_data([year], downcast=True)
        df.to_parquet(out, index=False)
        print(f"[wrote] {out} ({len(df):,} rows)")
```

### Pattern 2: Schema-as-SQL-File (not Python ORM)

**What:** Tables and indexes are declared in `schema/*.sql` as plain DDL. ETL applies them via `sqlite3.executescript()`.

**When to use:** When the audience explicitly cares about SQL skill (recruiters do); when the schema is small enough to fit in two files; when ORM overhead isn't justified. All three apply.

**Trade-offs:**
- **+** Recruiter can read `schema/01_create_tables.sql` and immediately understand the data model
- **+** No SQLAlchemy / ORM dependency — `sqlite3` from stdlib is enough
- **+** Schema reviewable in a 2-minute repo skim
- **−** No migration story; table changes mean wiping `nfl_coverage.db` and re-running ETL (acceptable: the data is regenerable in <5 min)

### Pattern 3: One-Query-Per-File SQL (not embedded in Python, not dbt)

**What:** Each business question is its own numbered `.sql` file with a header comment explaining the question, the result shape, and any caveats (sample-size flags, etc.).

**When to use:** When the count of analytical queries is small (8–10), when SQL skill is itself a deliverable, when the alternative reader is non-technical (recruiter scanning the repo).

**Trade-offs:**
- **+** A recruiter clicking through `queries/` sees exactly the SQL skill being claimed
- **+** Each query is independently testable from the `sqlite3` CLI
- **+** No tooling overhead (dbt would be over-engineering for 8 queries)
- **−** Notebooks must read these files via `Path("queries/05_third_long_pressure_tendencies.sql").read_text()` — easy pattern, costs one helper function
- **−** Some duplication between queries (CTEs for `regular_season_only` etc.) — acceptable at this scale

**Example header convention:**
```sql
-- Query 04: EPA allowed by pass rusher count, by team, 2022–2024
-- Returns: defteam, n_pass_rushers_bin, n_plays, mean_epa, stderr_epa
-- Sample-size flag: drops cells with n_plays < 15 (per SPEC quality bar)
-- Source: SQL skill demonstration — window function over team-bin partition
WITH ...
```

### Pattern 4: Notebook Triad (Explore / Model / Visualize)

**What:** Three notebooks, each with a distinct job. Not one giant narrative notebook, not five.

**Trade-offs:**
- **+** Each notebook is reviewable in 5 min; a single 2,000-line notebook is reviewable in 0
- **+** Clear separation: exploration is messy; modeling is rigorous; viz is polished
- **+** Visualizations notebook owns PNG export — single place, single convention
- **−** Some setup duplication across notebooks (SQLite connection, imports) — solved by a small `analysis/_common.py` helper

**Why not one comprehensive narrative notebook?**
Narrative belongs in `FINDINGS.md`. The notebooks are **work product**; FINDINGS.md is the **report**. A recruiter reads FINDINGS.md first; if intrigued, they spot-check `02_predictability_modeling.ipynb` to confirm the claimed entropy calculation is real. A single mega-notebook fails both audiences — too long for recruiters, too noisy for code reviewers.

### Anti-Patterns to Avoid

- **dbt for 8 queries.** Setup overhead exceeds analysis time. Plain SQL files win.
- **SQLAlchemy ORM for read-only analytical queries.** `sqlite3.connect()` + `pd.read_sql()` is two lines and zero dependency.
- **Auto-running notebooks via `papermill` in CI.** For an 8-query / 3-notebook portfolio piece, a one-time manual `Run All` before commit is sufficient. CI complexity > value. (See CI section below.)
- **One-file-per-source ETL with no orchestrator.** Three files with no `run.py` means three commands for the recruiter — fails the "≤5 commands" reproducibility budget from PROJECT.md.
- **Storing FTN tags as JSON blobs.** FTN's actual fields are scalar booleans and small integers (see Schema Design below) — JSON would be premature.

---

## Data Flow

### End-to-End Flow

```
[recruiter clones]
    ↓
git clone <repo>
cd nfl-coverage-tendencies
    ↓
pip install -r requirements.txt          # pinned versions
    ↓
python -m etl.run                         # ONE command, see below
    ├─ etl/load_pbp.py    → data/raw/pbp_<year>.parquet  (cached: skip if exists)
    ├─ etl/load_ftn.py    → data/raw/ftn_<year>.parquet  (cached: skip if exists)
    └─ etl/build_db.py    → data/nfl_coverage.db
        ├─ apply schema/01_create_tables.sql
        ├─ INSERT from parquet (chunked)
        └─ apply schema/02_indexes.sql
    ↓
jupyter notebook analysis/03_visualizations.ipynb
    └─ Run All → exports PNGs to findings/images/  (manual: notebook code does fig.savefig)
    ↓
[recruiter opens findings/FINDINGS.md]
[recruiter opens README.md, sees hero charts inline]
```

### Build-Order Dependency Graph (maps to phases)

```
Phase 1 ─ FTN schema audit
          (notebook hits import_ftn_data, prints columns, decides pivot)
              │
              ▼
Phase 2 ─ Schema design  ──►  ETL pipeline  ──►  SQLite build
          schema/*.sql       etl/load_*.py        etl/build_db.py
              │
              ▼
Phase 3 ─ SQL analysis layer (queries/01–08)
              │
              ▼
Phase 4 ─ Python analysis (notebooks, statistical tests, predictability score)
              │
              ▼
Phase 5 ─ Visualization + PNG export (analysis/03_visualizations.ipynb)
              │
              ▼
Phase 6 ─ FINDINGS.md memo  ──►  README.md (hero charts, tech stack, setup)
              │
              ▼
Phase 7 ─ Public repo via GitHub MCP (ship)
```

Phases 1 and 2 are strictly serial. Phases 3 and 4 can overlap once schema lands. Phase 5 is serial behind Phase 4 (notebooks own the figures). Phase 6 depends on the figures existing. Phase 7 is the ship.

### Key Data Flows

1. **Source → raw cache:** Parquet write protects against `nfl_data_py` deprecation/drift. Done once per season; idempotent.
2. **Raw → SQLite:** Column whitelist + rename in `etl/columns.py`; only the columns we use are loaded (~30 of pbp's ~370 columns), keeping DB small. [VERIFIED: nflverse pbp dictionary has hundreds of columns; we need maybe 25]
3. **SQLite → notebooks:** `pd.read_sql(Path("queries/04_*.sql").read_text(), conn)`. SQL does the heavy filtering / joining; pandas does the stats and plotting.
4. **Notebooks → PNGs:** `fig.savefig("findings/images/05_predictability.png", dpi=150, bbox_inches="tight")` inside the notebook. **Manual** (no `nbconvert`/`papermill` automation) — see Findings Workflow below.
5. **PNGs → FINDINGS.md / README.md:** Markdown image embeds, hand-written prose around them.

---

## Schema Design

### Recommended: Lightly Normalized (Three Tables)

```sql
-- schema/01_create_tables.sql

CREATE TABLE games (
    game_id      TEXT PRIMARY KEY,            -- nflverse_game_id (e.g. '2023_01_KC_DET')
    season       INTEGER NOT NULL,
    week         INTEGER NOT NULL,
    season_type  TEXT NOT NULL,               -- 'REG' (we filter to this in ETL)
    home_team    TEXT NOT NULL,
    away_team    TEXT NOT NULL
);

CREATE TABLE plays (
    -- identity / join
    game_id            TEXT NOT NULL REFERENCES games(game_id),
    play_id            INTEGER NOT NULL,
    -- situation
    posteam            TEXT,
    defteam            TEXT,
    qtr                INTEGER,
    down               INTEGER,
    ydstogo            INTEGER,
    yardline_100       INTEGER,
    score_differential INTEGER,
    -- play classification
    play_type          TEXT,                  -- 'pass', 'run', 'punt', 'field_goal', etc.
    pass               INTEGER,               -- 0/1
    rush               INTEGER,               -- 0/1
    -- outcome
    yards_gained       INTEGER,
    epa                REAL,
    PRIMARY KEY (game_id, play_id)
);

CREATE TABLE ftn_play (
    -- join key (1:1 with plays)
    game_id              TEXT NOT NULL,
    play_id              INTEGER NOT NULL,
    -- defensive context (the tendency dimensions)
    n_blitzers           INTEGER,
    n_pass_rushers       INTEGER,
    -- offensive context (situational filters)
    n_offense_backfield  INTEGER,
    qb_location          TEXT,                -- 'U' under center, 'S' shotgun, 'P' pistol
    is_no_huddle         INTEGER,             -- 0/1
    is_motion            INTEGER,
    is_play_action       INTEGER,
    is_screen_pass       INTEGER,
    is_rpo               INTEGER,
    is_qb_out_of_pocket  INTEGER,
    -- (other FTN booleans loaded as needed; see etl/columns.py whitelist)
    PRIMARY KEY (game_id, play_id),
    FOREIGN KEY (game_id, play_id) REFERENCES plays(game_id, play_id)
);
```

### Why this shape (not single denormalized, not heavily normalized)

| Option | Verdict | Reason |
|--------|---------|--------|
| Single `plays` table with FTN columns merged in | Rejected | Mixes source provenance — recruiter can't see "what FTN added vs what nflfastR provided." Source separation is a teaching opportunity. |
| **Lightly normalized: `games` + `plays` + `ftn_play`** | **Chosen** | Three small joins, source provenance preserved, schema readable in <2 min. Demonstrates 3NF without ceremony. |
| Heavily normalized: separate `teams`, `seasons`, `quarters`, `coverage_types` lookup, etc. | Rejected | Premature normalization; team and season are 32 and 3 values respectively; lookup tables add zero analytical value at this scale. |

### Coverage / Tendency Labels: how to store them

Given Critical Finding #2, FTN does **not** ship Cover 0–6 / man-zone labels. The relevant tendency dimensions are:

| Field | Type | Storage |
|-------|------|---------|
| `n_blitzers` | int 0–7 | INTEGER column on `ftn_play` |
| `n_pass_rushers` | int 3–8+ | INTEGER column on `ftn_play` |
| Bins (e.g. "3-rush", "4-rush", "5+-rush") | derived | **Compute in queries via CASE**, not stored — keeps schema flexible |

**Don't:** Store as JSON blob. The fields are scalar; JSON would block indexing.
**Don't:** Make a separate `coverage_types` lookup table. There are no labels to look up.
**Do:** Bin and label in the SQL query layer using `CASE WHEN n_pass_rushers >= 5 THEN '5+'`. This is itself a SQL skill demonstration.

If a future enhancement adds derived coverage proxies (e.g., a model trained on NGS to infer coverage), they would land as additional INTEGER/TEXT columns on `ftn_play` (or a sibling `derived_coverage` table) — not as JSON.

### Indexing Strategy

The dominant query shape is "filter on situation, group by team":

```sql
WHERE down = ? AND ydstogo BETWEEN ? AND ? AND yardline_100 < ?
GROUP BY defteam
```

```sql
-- schema/02_indexes.sql
CREATE INDEX idx_plays_situation ON plays (down, ydstogo, yardline_100);
CREATE INDEX idx_plays_defteam_season ON plays (defteam, game_id);   -- season via games join
CREATE INDEX idx_plays_play_type ON plays (play_type);
CREATE INDEX idx_ftn_n_pass_rushers ON ftn_play (n_pass_rushers);
CREATE INDEX idx_ftn_blitzers ON ftn_play (n_blitzers);
-- PRIMARY KEY (game_id, play_id) on both tables already gives the join index
```

Notes:
- The `(down, ydstogo, yardline_100)` composite covers most situational filters; SQLite will also use it for prefix queries on `down` alone.
- Don't over-index. With ~150k rows total, full table scans take ~50ms. Indexes pay off on repeated notebook iteration, not query latency. [ASSUMED based on SQLite scan rates of ~1M rows/sec on commodity laptops]

### Data Volume Estimates [VERIFIED partially — verify in Phase 1]

| Dataset | Rows / season | 4 seasons (2022-2025) | Notes |
|---------|---------------|-----------------------|-------|
| nflfastR pbp (regular season + playoffs, all play types) | ~49,000 | ~197,000 | [VERIFIED 2026-04-29: 4-season pull = 197,362 rows] |
| FTN charting (regular season + playoffs, all plays) | ~46,000 | ~185,000 | [VERIFIED 2026-04-29: 4-season pull = 185,215 rows] |
| `plays` table (post-filter to REG, ~30 cols) | — | ~185,000 | Estimated 40 MB in SQLite |
| `ftn_play` table (~15 cols) | — | ~185,000 | Estimated 20 MB |
| `games` table | 272 | 816 | <100 KB |
| **Total `nfl_coverage.db`** | — | — | **~50–80 MB estimated; verify in Phase 1** |

If the DB lands under ~25 MB after VACUUM, **commit it to git** so a recruiter can open it in DB Browser for SQLite without running ETL. If larger, `.gitignore` it and require ETL run. The ETL is fast enough (<5 min) that gitignoring is fine — but committing is friendlier when feasible.

---

## Notebook Organization

### Recommended: Three Notebooks, Distinct Roles

| Notebook | Role | Audience inside it | Outputs |
|----------|------|--------------------|---------|
| `01_exploratory.ipynb` | Schema audit (Phase 1!), descriptive stats, sample-size profiling | Author talking to themselves | None checked in (kept as evidence of process) |
| `02_predictability_modeling.ipynb` | Chi-square tests, Shannon entropy predictability score, ranking, validation | Code reviewer | Tables + intermediate figures |
| `03_visualizations.ipynb` | Final hero charts, formatted for FINDINGS.md / README | Recruiter spot-checking the chart code | **All PNGs in `findings/images/`** |

### Trade-offs vs single comprehensive notebook

| Pro of three | Con of three |
|--------------|--------------|
| Each is reviewable in 5 min | Some setup imports duplicated (mitigated by `analysis/_common.py`) |
| Clear separation: messy → rigorous → polished | Author must remember which notebook owns which figure |
| Recruiter spot-checks `02` for stats rigor; reads PNGs from `03` | — |

| Pro of one | Con of one |
|------------|------------|
| Single narrative file | 2,000 lines is unreviewable on GitHub's web view |
| No setup duplication | Mixing exploration scratch with polished output looks unprofessional |
| | Re-running mixes slow EDA cells with fast plotting cells |

**Recommendation: three notebooks.** The narrative lives in `FINDINGS.md`, where it belongs.

### Reproducibility within a notebook

- All notebooks must run end-to-end from a fresh kernel (`Restart & Run All` succeeds).
- No hidden state: every notebook starts by reconnecting to `data/nfl_coverage.db` and re-importing.
- Random seeds set explicitly where any sampling/permutation occurs.
- Cell ordering is the execution order — no out-of-order cells.

---

## Findings + Images Workflow

### The lightest-touch approach that produces clean checked-in PNGs

**Recommendation: manual `fig.savefig()` from the visualizations notebook. No `nbconvert`. No `papermill`.**

```python
# inside analysis/03_visualizations.ipynb
from pathlib import Path
IMG = Path("../findings/images")
IMG.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
# ... plotting ...
fig.tight_layout()
fig.savefig(IMG / "01_predictability_ranking.png", bbox_inches="tight")
```

### Why not nbconvert / papermill

| Tool | What it does | Why not here |
|------|--------------|--------------|
| `nbconvert --to script` | Notebook → `.py` | We *want* the notebook as the artifact; converting away from it loses the recruiter's path-of-least-resistance review |
| `nbconvert --execute --to html` | Run + render notebook to HTML | HTML duplicates the `.ipynb` — GitHub renders `.ipynb` natively |
| `papermill` | Parameterized notebook execution | We have one parameter set (2022–2024); no reason to parameterize |
| Manual `fig.savefig` from notebook | Direct, explicit | **Chosen** — one line per chart, paths visible, zero dependency |

### Workflow

1. Author iterates in `03_visualizations.ipynb` until figures look right.
2. Author runs `Restart & Run All` once before committing.
3. Notebook code calls `fig.savefig("../findings/images/<name>.png")` for each figure.
4. Author commits both the `.ipynb` (with outputs cleared via `jupyter nbconvert --clear-output --inplace`) and the `findings/images/*.png` files.
5. `FINDINGS.md` references the PNGs via `![alt](images/01_predictability_ranking.png)`.

**Why clear notebook outputs before commit?** Cell outputs (especially DataFrames and inline images) bloat the `.ipynb` JSON, make diffs unreadable, and double-store the figures (once in the notebook, once in `findings/images/`). Clearing outputs forces the convention "figures live in `findings/images/`, period."

Add a pre-commit hook only if the project hits friction; otherwise document the convention in `analysis/README.md` and trust the discipline. (Solo author, public repo — discipline is the lever.)

---

## Reproducibility Guarantee

### The recruiter contract

```
git clone <repo>
cd nfl-coverage-tendencies
python -m venv .venv && source .venv/bin/activate    # or .venv\Scripts\activate
pip install -r requirements.txt
python -m etl.run
jupyter notebook analysis/03_visualizations.ipynb
```

Five commands. The PROJECT.md budget is "≤ 5 commands and ≤ 10 min on a stock laptop." This hits both. [VERIFIED against PROJECT.md]

### How each layer guarantees determinism

| Layer | Determinism mechanism |
|-------|----------------------|
| `requirements.txt` | All versions pinned. `nfl_data_py==0.3.3`, `pandas==2.2.x`, `numpy==1.26.x`, `matplotlib==3.8.x`, `seaborn==0.13.x`, `jupyter==1.0.x`, `pyarrow==15.x` |
| Python version | `3.11` documented in `README.md`; `.python-version` file for `pyenv` users |
| `nfl_data_py` upstream drift | Mitigated by `data/raw/*.parquet` cache. After first successful pull, `data/raw/` files are the contract; subsequent ETL reads them, not the API |
| Schema | DDL in `schema/*.sql`; deterministic apply order |
| ETL | `etl/build_db.py` drops + recreates tables on each run; same parquet → same DB |
| SQL | Static `.sql` files; SQLite is deterministic |
| Notebooks | Random seeds explicit; fresh-kernel runs verified before commit |
| Figures | `fig.savefig` with explicit `dpi=150` and `bbox_inches="tight"` (no theme drift) |

### What can still break the contract

- Python 3.13+ on a recruiter laptop with newer pandas dropping nfl_data_py compatibility. Mitigation: pin pandas, document Python 3.11 explicitly, optionally add `python_requires` to a `pyproject.toml`.
- Network failure during first `nfl_data_py` pull. Mitigation: `data/README.md` explains the cache and links to nflverse data dumps as fallback.
- Operating-system path separators in notebook code. Mitigation: use `pathlib.Path` everywhere (Python's `os.sep` handles Windows ↔ POSIX).

### `data/raw/` policy

Gitignore. They're regenerable from `nfl_data_py`, total ~150 MB, and including them would balloon the repo. Document the regeneration step in `data/README.md`.

### `data/nfl_coverage.db` policy

**Conditional commit:** if final DB ≤ 25 MB after `VACUUM`, commit it; otherwise gitignore. Committing is the recruiter-friendliest option (instant DB Browser open, no ETL run required). Test once after Phase 2 lands.

---

## CI Recommendation

### Minimal CI is justified; full notebook-execution CI is not

**Recommendation: a single GitHub Actions workflow that runs `ruff` + a smoke test that imports each ETL module. No notebook execution. No full pipeline run.**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  lint-and-smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt ruff
      - run: ruff check etl/ analysis/
      - run: python -c "from etl import load_pbp, load_ftn, build_db, columns; print('imports ok')"
```

### Why this scope

| CI option | Verdict | Reason |
|-----------|---------|--------|
| No CI at all | Acceptable but missed signal | A green CI badge is itself a recruiter signal at low cost |
| Lint + import smoke (recommended) | **Chosen** | <30 sec wall clock, zero data dependency, catches typos and refactor breakage |
| Run full ETL in CI | Rejected | Pulls 150 MB from nflverse on every CI run; flaky on network; slow; adds nothing the import smoke doesn't |
| Execute notebooks via `nbconvert --execute` | Rejected | Runs ETL transitively, plus 2–3 min notebook overhead; recruiter doesn't see notebook CI; over-engineering |
| Build + publish to GitHub Pages | Rejected | Project is a repo, not a site; FINDINGS.md renders on GitHub natively |

The CI workflow is itself a portfolio signal — it shows the author thinks about reproducibility — without overshadowing the analytical work.

---

## Scaling Considerations

This is a fixed-data, single-user portfolio piece. Traditional "scale" doesn't apply, but there are two real scaling vectors worth documenting:

| Scale axis | At current size (4 seasons) | If extended (e.g. all of 2018+) |
|-----------|------------------------------|----------------------------------|
| Data volume | ~185k plays, ~110 MB DB | ~400k plays for 2018–2025, still <300 MB — SQLite handles it without changes |
| Notebook iteration speed | <2 sec for any single query against indexed `plays` | Same, with the existing index strategy |
| ETL re-pull time | ~3 min on warm cache, ~10 min cold | Linear scaling; raw cache mitigates |
| Recruiter clone size | If `nfl_coverage.db` committed (≤25 MB), ~30 MB total repo | Force-gitignore the DB, require ETL run |

### What breaks first if scaled?

1. **Repo size** — committing the DB at >25 MB makes the clone heavy. Fix: gitignore.
2. **Notebook memory** — pulling all plays into pandas at once if data grows >5x. Fix: SQL filters more aggressively before `read_sql`.
3. **`nfl_data_py` deprecation catching up** — if a future Python release breaks nfl_data_py 0.3.3 entirely, migration to `nflreadpy` becomes mandatory. Fix: the parquet raw cache means existing data still works; only refresh would need migration.

None of these are real concerns at the project's locked scope (4 seasons, 2022-2025).

---

## Anti-Patterns

### Anti-Pattern 1: "ETL as one big script"
**What people do:** Single `etl.py` that pulls, transforms, and loads in one function.
**Why it's wrong:** Re-pulling on every iteration is slow; failures lose all progress; recruiter can't see the stages.
**Do this instead:** Three modules (`load_pbp`, `load_ftn`, `build_db`) + an `etl/run.py` orchestrator. Each stage is independently runnable and idempotent.

### Anti-Pattern 2: "Notebook does ETL too"
**What people do:** Notebook starts with `nfl.import_pbp_data([2022, 2023, 2024, 2025])`, then does analysis.
**Why it's wrong:** Notebook re-pulls 150 MB on every run; couples analysis to network; can't be reviewed without running.
**Do this instead:** ETL writes to SQLite; notebooks read from SQLite. Strict one-way flow.

### Anti-Pattern 3: "Premature dbt"
**What people do:** Set up dbt-core for 8 SQL files because it's "more professional."
**Why it's wrong:** dbt's value is in incremental models, tests, and DAG management — none of which exist for 8 standalone analytical queries on a static dataset.
**Do this instead:** Plain `.sql` files in `queries/`, read by notebooks via `Path(...).read_text()`. Keep dbt for jobs where it earns its complexity.

### Anti-Pattern 4: "Notebooks committed with cell outputs"
**What people do:** Commit the full executed notebook including DataFrame outputs and embedded images.
**Why it's wrong:** Diffs are unreadable, repo bloats, figures get duplicated between `.ipynb` and `findings/images/`.
**Do this instead:** Clear outputs before commit (`jupyter nbconvert --clear-output --inplace analysis/*.ipynb`); rely on `findings/images/` for the canonical figures.

### Anti-Pattern 5: "Coverage labels as JSON"
**What people do:** When the schema audit finds limited defensive fields, store everything as a JSON blob "for flexibility."
**Why it's wrong:** Blocks indexing, blocks SQL filtering, defeats the point of using SQLite.
**Do this instead:** FTN's defensive fields are scalar (`n_blitzers`, `n_pass_rushers`); store as INTEGER columns. Bin via `CASE` in queries.

### Anti-Pattern 6: "Auto-execute notebooks in CI"
**What people do:** Use `nbconvert --execute` in GitHub Actions to "test" the notebooks.
**Why it's wrong:** Pulls 150 MB on every CI run, takes 5+ min, flaky on network. The notebook is the artifact; CI doesn't need to re-render it.
**Do this instead:** Lint + import smoke. Trust the author to run notebooks once before commit.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| `nfl_data_py` 0.3.3 (PyPI) | Direct import in `etl/load_*.py` | Pinned. Deprecated upstream. Parquet cache insulates. |
| nflverse data CDN (called by nfl_data_py) | Indirect via nfl_data_py | First pull only; cached thereafter |
| GitHub MCP | Used in ship phase | Repo creation, topic config, pinning — per PROJECT.md |
| GitHub Actions | Optional CI | Lint + smoke only, see above |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `nfl_data_py` ↔ `etl/load_*.py` | Function call → DataFrame → `to_parquet` | Single point of upstream contact |
| `etl/load_*.py` ↔ `etl/build_db.py` | Filesystem (parquet files) | Decoupled by design |
| `etl/build_db.py` ↔ `data/nfl_coverage.db` | SQLite file | Drop & recreate on each run |
| `queries/*.sql` ↔ notebooks | Notebook reads SQL via `Path.read_text()` | One-way: SQL is canonical, notebook just executes |
| Notebooks ↔ `findings/images/` | `fig.savefig` in notebook | One-way: notebooks produce, FINDINGS.md consumes |
| `FINDINGS.md` ↔ `README.md` | Hand-written links + duplicated hero chart | README links to FINDINGS.md for the long form |

---

## Open Questions for Phase 1

These are the architectural questions Phase 1 must close. They're listed here so the planner can scope Phase 1 explicitly.

1. **Confirm FTN defensive columns.** This research strongly suggests `n_blitzers` and `n_pass_rushers` are the only defensive scheme fields. Phase 1 verifies by calling `nfl.import_ftn_data([2022])` and printing `df.columns.tolist()`. [Resolution: notebook output documented in PROJECT.md]
2. **Verify FTN row counts match pbp row counts.** Architecture assumes 1:1 join on `(game_id, play_id)`. If FTN charts a subset, the join becomes 1:0..1 and `ftn_play` becomes optional via LEFT JOIN.
3. **Verify `nfl_data_py` 0.3.3 still installs cleanly on Python 3.11 in 2026.** Pre-flight before Phase 2 ETL build.
4. **Final repo name.** Locked only after Phase 1 confirms the pivot (or doesn't).

---

## Sources

### HIGH confidence (Verified)
- nflreadr FTN charting data dictionary — full 28-column schema confirmed: https://nflreadr.nflverse.com/articles/dictionary_ftn_charting.html
- nflverse pbp dictionary CSV (raw): https://raw.githubusercontent.com/nflverse/nflreadr/main/data-raw/dictionary_pbp.csv
- nfl_data_py PyPI page (versions, deprecation): https://pypi.org/project/nfl-data-py/
- nflverse/nfl_data_py GitHub README (archival notice): https://github.com/nflverse/nfl_data_py
- nflverse/nflreadpy GitHub (replacement library status): https://github.com/nflverse/nflreadpy
- nflreadpy PyPI (v0.1.5, experimental): https://pypi.org/project/nflreadpy/

### MEDIUM confidence
- nflfastR row counts per season ~47k: https://nflfastr.com/articles/nflfastR.html and https://www.sharpfootballanalysis.com/stats-nfl/nfl-coverage-schemes/

### LOW confidence / [ASSUMED]
- FTN row count exactly matches pbp row count for 2022–2024 — assumed; verify in Phase 1
- SQLite full-table-scan rate ~1M rows/sec on commodity laptop — based on general knowledge; not benchmarked for this project specifically

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | FTN charts every play (1:1 with pbp) | Schema Design / Data Volume | Schema joins become LEFT JOIN; some `ftn_play` rows missing — handled gracefully but changes query patterns |
| A2 | Combined SQLite DB ≤ 80 MB after VACUUM | Data Volume Estimates | If larger, must gitignore (no committed DB); recruiter must run ETL — still acceptable |
| A3 | SQLite scan speed adequate for ad-hoc notebook queries | Indexing Strategy | If too slow, add more indexes; not a structural issue |
| A4 | `nfl_data_py` 0.3.3 still installs on Python 3.11 in 2026 | Reproducibility | If broken, must migrate to `nflreadpy` — significant rework, but parquet cache shields existing data |
| A5 | Recruiter has Python 3.11 and Jupyter installed (or installs them via pip) | Reproducibility Contract | If not, README-documented `pyenv` and `pip install jupyter` are one-line fixes |
| A6 | Manual `fig.savefig` discipline holds across all chart authoring | Findings Workflow | If author drifts, add a pre-commit hook to verify all FINDINGS.md image references resolve to checked-in PNGs |

---

*Architecture research for: solo-author tabular data-analytics portfolio piece, Python + SQLite + Jupyter, sourcing from `nfl_data_py`*
*Researched: 2026-04-29*
