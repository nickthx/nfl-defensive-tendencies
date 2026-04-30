# Phase 2: Data Layer (ETL + SQLite Schema) - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

A reproducible parquet → SQLite pipeline driven by a single command (`python -m etl.run`) that produces `data/nfl_defensive_tendencies.db` with three lightly-normalized tables (`games`, `plays`, `ftn_play`), composite indexes on the situational query patterns, and the project-wide `competitive_plays` SQL view. The ETL pulls 2022–2025 (REG + POST) from `nfl_data_py.import_pbp_data` and `nfl_data_py.import_ftn_data`, caches per-year parquet in `data/raw/`, joins FTN to pbp on `(nflverse_game_id, nflverse_play_id)` with `validate='one_to_one'` and a `>0.95` match-rate assertion, applies the column whitelist, and writes the SQLite database with composite indexes and the `competitive_plays` view.

Out of scope for this phase: any analytical query against `competitive_plays` (Phase 3), any visualization or notebook beyond what already exists from Phase 1's audit (Phase 3 / Phase 4), README setup-block prose (Phase 4 / DOC-05), GitHub Actions workflow (Phase 4 / SHIP-01), the public repo creation step (Phase 4 / SHIP-03).

</domain>

<decisions>
## Implementation Decisions

### `competitive_plays` view (SCHEMA-03)

The single source of truth for play-type and win-probability filtering across every analytical query in Phase 3.

- **D-01: Q4 crunch time stays IN.** The view does NOT exclude `qtr=4 AND half_seconds_remaining<300`. Rationale: the WP `0.05–0.95` filter already removes blowouts; competitive Q4 is precisely where coordinator tendencies matter most. Excluding it would shrink Situation 1 (3rd-and-long) and Situation 4 (2nd-and-medium) samples without an analytical justification. PITFALLS #6 lists this exclusion as defensible-but-optional; we elect not to apply it.

- **D-02: 2-minute drill cutoff is end-of-half-only.** The view filters `NOT (qtr IN (2,4) AND half_seconds_remaining <= 120)`. Drops hurry-up at end of H1 and end of regulation. Does not drop the entire 2-minute window in Q1 / Q3 (game-state irrelevant there).

- **D-03: `competitive_plays` is a SQL VIEW, not a materialized table.** Defined once in `schema/03_views.sql`. Always reflects underlying `plays` data, no rebuild step, no extra storage. SQLite handles indexed lookups through the view at this scale (~140k filtered rows of ~197k base) without measurable overhead.

- **D-04: Play classification uses `play_type` only.** The view filters `play_type IN ('pass','run')` — does NOT also require `pass_attempt=1` OR `rush_attempt=1`. Sacks count as `play_type='pass'` and ARE meaningful for blitz analysis; the strict-attempt mode would silently drop them. PITFALLS #7 acknowledges this as the canonical convention.

**Final view definition (locked for Plan 02-01 / SCHEMA-03):**
```sql
CREATE VIEW competitive_plays AS
SELECT *
FROM plays
WHERE play_type IN ('pass','run')
  AND wp BETWEEN 0.05 AND 0.95
  AND qtr <= 4                                          -- exclude OT
  AND NOT (qtr IN (2,4) AND half_seconds_remaining <= 120)  -- exclude end-of-half hurry-up
;
```

### Schema column scope (SCHEMA-01, SCHEMA-02, ETL-03)

- **D-05: `season` and `week` are denormalized onto `plays`.** Storage cost ~2–3 MB across 197k rows. Critical: SCHEMA-02's locked composite index `(defteam, season)` only fires if `season` lives on `plays`. Every Phase 3 situational query avoids a 3-way join through `games`. Matches the universal nflfastR analysis convention.

- **D-06: `plays` whitelist is the broader ~24-column set, not the tendency-minimum 18.** Identity (`game_id`, `play_id`, `season`, `week`), teams (`posteam`, `defteam`), situation (`qtr`, `down`, `ydstogo`, `yardline_100`, `score_differential`), time (`half_seconds_remaining`), classification (`play_type`, `pass`, `rush`), outcome (`yards_gained`, `epa`), filter inputs (`wp`), plus the broader analytical layer: `pass_attempt`, `rush_attempt`, `cpoe`, `xpass`, `success`, `air_yards`. Estimated `plays` size ~32 MB. The extra columns enable richer Phase 3 / STAT-08 sensitivity checks (e.g., blitz on dropbacks via `pass_attempt=1` vs all `play_type='pass'`) without a re-build.

- **D-07: REG + POST games are both included; `season_type` lives on `games`.** Matches PROJECT.md D-10 framing ("four seasons through Super Bowl LX") and the STATE.md row counts (80,782 pass / 59,824 run / 140,606 competitive across 4 seasons already include POST). Phase 3 queries can filter `season_type='REG'` if a specific question needs regular-season-only.

- **D-08: `games` is identity-only, ~6 columns.** `game_id` (PK), `season`, `week`, `season_type`, `home_team`, `away_team`. No final scores, no roof / surface / weather. Final scores are not referenced by any pre-registered Phase 3 hypothesis; if a v2 expansion adds game-outcome analyses, they land here.

**FTN column whitelist for `ftn_play` (locked from Phase 1 D-01..D-04 — all 8 candidates survived 30% NaN cutoff):**
- `nflverse_game_id`, `nflverse_play_id` (renamed to `game_id`, `play_id` for the PK)
- `n_blitzers`, `n_pass_rushers` (INTEGER)
- `is_play_action`, `is_screen_pass`, `is_rpo` (INTEGER 0/1)
- `qb_location` (TEXT — values 'U' / 'S' / 'P')
- `n_offense_backfield` (INTEGER)
- `starting_hash` (TEXT)

### ETL CLI ergonomics + idempotency (ETL-01, ETL-02, ETL-05, ETL-06)

- **D-09: `build_db.py` always DROP+CREATE tables on every invocation.** No `--force` flag, no skip-if-exists logic. Parquet cache is the source of truth; rebuild from parquet is ~30 s and deterministic. Same parquet → same DB, every time. Wiping a populated DB is harmless because the parquet underneath it is unchanged.

- **D-10: Zero CLI flags on `etl/run.py`.** The recruiter contract is exactly `python -m etl.run` — one of the 5 commands in the locked DOC-05 setup block. Seasons (`[2022, 2023, 2024, 2025]`) live as a module-level constant in `etl/columns.py` (the canonical etl-config module per ARCHITECTURE.md). Nick edits the constant for dev; the CLI exposes nothing to fiddle.

- **D-11: Year-by-year loop with per-year parquet idempotency.** `load_pbp.py` and `load_ftn.py` iterate `for year in SEASONS:`, each iteration: (a) check if `data/raw/pbp_{year}.parquet` (or `ftn_{year}.parquet`) exists, (b) skip with a log line if so, (c) otherwise call `nfl.import_pbp_data([year])` (single-year list), assert row count, write parquet. Resilient: a network failure on 2024 doesn't lose 2022/2023; re-run picks up exactly where it left off. Matches ARCHITECTURE.md Pattern 1 verbatim.

- **D-12: Assertions live inline in the modules they guard.** Per-year row-count assertions in `load_pbp.py` / `load_ftn.py` (e.g., `assert len(df) > 40_000` per year). FTN↔pbp match-rate + post-join row-count assertions in `build_db.py` (`assert match_rate > 0.95`, `assert len(joined) > 130_000`). Plain `assert` statements — `AssertionError` propagates, exits non-zero, fails CI cleanly. Concrete thresholds derived from STATE.md verified totals (4-season ~197k pbp / ~185k FTN / 0.9999 match rate).

### Runtime UX — logging + failure modes (cross-cutting on ETL-05, ETL-06)

- **D-13: stdlib `logging` at INFO.** No new deps. `etl/run.py` (and each loader/builder it invokes) uses `logging.getLogger(__name__).info(...)` for stage transitions ("Pulling pbp 2022...", "Wrote pbp_2022.parquet (49,287 rows)", "Joined FTN→pbp: match_rate=0.9999"). `nfl_data_py.import_*` already shows a tqdm progress bar internally on the slow network step, so the ~10-min cold cache run is never visually silent.

- **D-14: Log format is `%(asctime)s %(levelname)s %(message)s`.** Configured once in `etl/run.py` via `logging.basicConfig`. Recruiter scanning a 10-min run can timestamp-grep to find the slow stage. Format is the standard "professional Python" look.

- **D-15: Fail-fast on network errors.** No retry-with-backoff, no `tenacity` dep. If `nfl_data_py` raises (404 from nflverse CDN, connection timeout, etc.), the exception bubbles through the loader and crashes `etl.run` with a clean traceback. The recruiter's recovery is "re-run the command" — and the year-by-year parquet cache means already-pulled years aren't re-fetched. Row-count assertions (D-12) catch the silent-empty-success case (PITFALLS #17) which retry doesn't address.

- **D-16: `etl/run.py` ends with a structured multi-line summary log.** After `build_db.py` returns, log a fixed-format summary block:
  ```
  Database built: data/nfl_defensive_tendencies.db
    games:               816 rows
    plays:           197,362 rows
    ftn_play:        185,215 rows
    match_rate:       0.9999
    competitive_plays: 140,606 rows
    duration:         4m 12s
  ```
  Recruiter glance-test confirms a clean build. Doubles as the row-count evidence that DOC-05 README setup-block can reference if needed.

### Folded Todos

None. STATE.md "Pending Todos" was empty going into this discussion.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (gsd-phase-researcher, gsd-planner) MUST read these before planning or implementing.**

### Project-level constraints (read first)

- `CLAUDE.md` — Locked stack, file-organization rules (`/etl`, `/schema` for source; never repo root), audience voice. Non-negotiables. **In particular** the "Project Realities to Remember" section (FTN↔pbp join keys, `competitive_plays` SSOT, `.db` gitignored) directly governs Phase 2 deliverables.
- `.planning/PROJECT.md` — Vision, Out of Scope, Key Decisions table (especially D-10: 4-season scope 2022–2025).
- `.planning/REQUIREMENTS.md` — `ETL-01..06` + `SCHEMA-01..03` acceptance criteria with exact column lists, file paths, and assertion thresholds. `SCHEMA-03` predicate is reified above; the rest of the criteria stay authoritative.
- `.planning/ROADMAP.md` §Phase 2 — Phase boundary, success criteria (1–5), plan ordering (02-01 Schema || 02-02 ETL early, converge at `build_db.py`), in-phase parallelism rules.

### Research backbone (read in this order)

- `.planning/research/SUMMARY.md` §Consolidated Stack (lines 67–91) — verbatim pin block; do not drift to other versions of the stack.
- `.planning/research/ARCHITECTURE.md` — §Component Responsibilities (table at line 80), §Pattern 1 Raw Cache (lines 170–201, the loader pattern Phase 2 implements), §Schema Design (lines 327–443, including the three-table DDL excerpt and indexing strategy), §Reproducibility Guarantee (lines 524–565).
- `.planning/research/PITFALLS.md` — **#3** FTN join keys + `validate='one_to_one'`, **#4** NaN on run plays for blitz columns (already informed Phase 1; Phase 2 carries the column-keep decision), **#6** garbage-time / WP filter (the `competitive_plays` foundation), **#7** ST / `no_play` contamination, **#14** big `.db` (gitignored), **#16** `requirements.txt` pinning (already done in Phase 1; Phase 2 must not regress), **#17** silent ETL pull failures (assertion-driven).
- `.planning/research/STACK.md` — Pin rationale; the `[tool.ruff]` config (already in `pyproject.toml` from Phase 1).
- `.planning/research/FEATURES.md` — Anti-features list; `data/README.md` is a Phase 4 deliverable but Phase 2 may need a placeholder if the audit-doc trail demands it.

### Phase 1 outputs (this is what Phase 2 builds on)

- `.planning/phases/01-foundation-ftn-pivot-calibration/01-CONTEXT.md` — Phase 1 D-01..D-10 (anchor dimensions, situations, repo name, scope expansion). The 4 anchors and 8 FTN whitelist columns flow directly into D-06 above.
- `.planning/phases/01-foundation-ftn-pivot-calibration/01-PATTERNS.md` — Phase 1 pattern map; `analysis/00_data_audit.ipynb` cells 4 (FTN↔pbp join) and 5 (NaN profile) are the analog Phase 2's `etl/build_db.py` reproduces and extends.
- `docs/ftn-schema-audit.md` — Anchor dimension narrative; the 8 FTN columns Phase 2 keeps.
- `docs/analysis-plan.md` — 4 pre-registered situations + cross-cutting `is_play_action` modifier. Defines what `competitive_plays` must support; informs the WHERE-clause sanity-check (every situation's filter must run cleanly against the view).
- `audit/ftn_null_profile.csv` — Per-column NaN rate by `play_type`. The whitelist in D-06 / D-07 above must not include any FTN column with a contradictory NaN profile.
- `analysis/00_data_audit.ipynb` (and paired `.py`) — The canonical join-and-assert pattern; ETL must reproduce its `validate='one_to_one'` + match-rate assertion verbatim.

### Existing populated artifacts

- `data/raw/*.parquet` — Already populated with 4 seasons (verified during Phase 1 audit and the D-10 scope-expansion check). Phase 2 ETL development runs warm-cache from day 1; a from-scratch cold-cache validation is the final acceptance test (ETL-06).
- `requirements.txt`, `pyproject.toml`, `.python-version`, `.gitignore`, `venv/` — All Phase 1 outputs; Phase 2 must not modify the stack pins.
- `SPEC.md` — Post-pivot AUDIT-06 rewrite; not a primary input for Phase 2 but the schema must support its rewritten business questions when Phase 3 reaches them.

### No external ADRs

Same as Phase 1: this project doesn't use a `docs/decisions/adr-*.md` system. If Phase 2 surfaces a Phase-2-locked decision worth promoting beyond CONTEXT.md, it goes into `.planning/PROJECT.md` Key Decisions, not a new ADR file.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets (already on disk from Phase 1)

- **`analysis/00_data_audit.ipynb`** + paired `.py` — Establishes the FTN↔pbp join pattern Phase 2's `etl/build_db.py` will reproduce: `left_on=['nflverse_game_id','nflverse_play_id']` / `right_on=['game_id','play_id']`, `validate='one_to_one'`, post-join match-rate assertion. Copy the join idiom directly; do not reinvent.
- **`data/raw/*.parquet`** — 4 seasons of pbp + FTN parquet already cached from Phase 1 D-10 scope expansion. ETL development runs warm-cache; the from-scratch cold-cache run is the ETL-06 ≤10-min budget check at the end of the phase, not on every dev iteration.
- **`requirements.txt`** — Stack is locked. The two-step install workaround (non-`nfl_data_py` deps with strict resolver, then `nfl_data_py==0.3.3 --no-deps` + `appdirs>1`, `fastparquet>0.5`) is documented in STATE.md and was applied to the project venv. Phase 2 inherits a working environment; Phase 4 / DOC-05 README setup block encodes the install for recruiters.
- **`pyproject.toml`** — `[tool.ruff]` config only. Phase 2 source code (etl/, schema/) lints clean against this config.
- **`.gitignore`** — `data/raw/`, `*.db`, `__pycache__/`, `.ipynb_checkpoints/`, `venv/`, `scratch*` all already excluded. Phase 2 does not modify.

### Established patterns

- **Path management:** `pathlib.Path` throughout (per `00_data_audit.ipynb`). Cross-platform path separators handled. ETL code in `etl/` should also use `Path` exclusively.
- **`nfl_data_py` invocation:** `nfl.import_pbp_data([year])` and `nfl.import_ftn_data([year])` — single-year lists in a year-by-year loop (per D-11). The `00_data_audit.ipynb` cell 2/3 pattern of `nfl.import_*([2022, 2023, 2024, 2025])` was a one-shot for the audit; Phase 2 ETL switches to the per-year idempotent pattern.
- **Assertion style:** plain `assert` statements with f-string error messages (per `00_data_audit.ipynb` cell 4). No custom exception classes; no `raise ValueError(...)`. Match-rate / row-count assertions follow the same idiom.
- **Notebook output discipline:** `analysis/00_data_audit.ipynb` was committed with outputs cleared (`nbconvert --clear-output --inplace`). Phase 2 doesn't add notebooks, so this rule is dormant — but Phase 3 will inherit the convention.

### Integration points

- **`etl/run.py` ↔ `nfl_data_py`:** Sole upstream contact. `import nfl_data_py as nfl`; `nfl.import_pbp_data`, `nfl.import_ftn_data`. No retry/backoff (D-15). Row-count assertion immediately post-pull.
- **`etl/load_*.py` ↔ `data/raw/*.parquet`:** Filesystem boundary. `df.to_parquet(path, index=False)`; `pd.read_parquet(path)` on read. `pyarrow` is the engine (transitively pulled by `nfl_data_py`).
- **`etl/build_db.py` ↔ `schema/*.sql`:** `Path("schema/01_create_tables.sql").read_text()` then `conn.executescript(...)`. The schema files are static; build_db is the applier.
- **`etl/build_db.py` ↔ `data/nfl_defensive_tendencies.db`:** SQLite single-file output via stdlib `sqlite3.connect()`. DROP+CREATE on every run (D-09).
- **`etl/columns.py` ↔ everything:** Single-source-of-truth module. Owns `SEASONS = [2022, 2023, 2024, 2025]`, the pbp column whitelist (D-06), the FTN column whitelist + rename map (D-07), and the join keys. Every other ETL file imports from here.
- **`schema/*.sql` ↔ `competitive_plays` consumers:** The view in `03_views.sql` is the public contract for Phase 3. Once Plan 02-01 lands, Phase 3 plans can import it via `Path("schema/03_views.sql")` for inline documentation, but the view itself is read from the SQLite DB by every analytical query.

### Greenfield within Phase 2

- `etl/`, `schema/`, `queries/` directories exist but are empty. Phase 2 fills `etl/` (5 files) and `schema/` (3 files). `queries/` stays empty until Phase 3.
- No existing Python modules in `etl/` to mirror; `etl/__init__.py` (empty), `etl/columns.py`, `etl/load_pbp.py`, `etl/load_ftn.py`, `etl/build_db.py`, `etl/run.py` are all greenfield. The patterns established here (year-by-year loop, inline asserts, stdlib logging, year-list constant in `columns.py`) become the analog Phase 3's `analysis/_common.py` will reference.

</code_context>

<specifics>
## Specific Ideas

- **The `competitive_plays` view definition is final.** The exact SQL block above (D-04 closing) is what `schema/03_views.sql` must contain. Don't refactor the predicate set during planning or execution — every Phase 3 query depends on these exact filters.

- **Concrete row-count assertion thresholds, derived from STATE.md verified Phase 1 totals:**
  - per-year pbp: `assert len(df) > 40_000` (regular season alone is ~46k; with playoffs ~49k; floor at 40k catches a partial pull cleanly)
  - per-year FTN: `assert len(df) > 38_000` (FTN charts ~46k/season; floor at 38k catches 80%+ shortfall)
  - post-join: `assert len(joined) > 130_000` (4-season verified 185,215 — generous floor leaves room for FTN's normal small undercharting)
  - match-rate: `assert match_rate > 0.95` (verified 0.9999 — the >0.95 floor in ETL-04 has ~5pp headroom)
  - competitive_plays count: not asserted in ETL (it's a view, lazily evaluated); the summary log line (D-16) reports it for glance-checking against the verified 140,606.

- **`qb_location` is TEXT, not INTEGER.** FTN values are character codes ('U' under-center, 'S' shotgun, 'P' pistol). Architecture explicitly TEXT; do not turn into a categorical-as-INTEGER lookup table (over-normalization for 3 distinct values).

- **`is_*` boolean columns store as INTEGER 0/1.** SQLite has no native BOOL; using INTEGER + the convention `WHERE is_play_action = 1` is the SQLite idiom. Architecture confirms.

- **The DB filename is `nfl_defensive_tendencies.db`, not `nfl_coverage.db`.** ROADMAP success criterion 1 names it explicitly with the post-pivot name. The architecture doc still references the old `nfl_coverage.db` (pre-D-09 lock); ROADMAP is authoritative.

- **`etl/__init__.py` is empty.** Per CLAUDE.md "this is an analysis repo, not a library" — no package metadata, no `__all__` list. Just an empty file so `python -m etl.run` works.

- **`schema/*.sql` files are applied via `executescript()`, not parameterized statements.** They are static DDL; no string interpolation needed. Each file is one logical unit (`01_create_tables.sql` defines all 3 tables, `02_indexes.sql` defines all indexes, `03_views.sql` defines `competitive_plays`).

- **Match-rate calculation matches `00_data_audit.ipynb` cell 4 exactly.** `match_rate = joined['play_type'].notna().mean()` (where `play_type` came from the pbp side of the join). Not `joined['nflverse_play_id'].notna().mean()` — that's the FTN-side key, which is always non-null after a left join from FTN. The pbp-side `play_type` is the one that will be NaN if the join misses.

</specifics>

<deferred>
## Deferred Ideas

These came up during discussion (or research) but are out of Phase 2 scope. Capture them so future phases / v2 don't re-discover.

- **Sample DB quickstart (`data/sample.db`).** ARCHITECTURE.md mentions a tiny one-team-one-season DB committed to git for instant DB-Browser-for-SQLite open without running ETL. Defer to v2 — full ETL is fast enough (≤10 min cold) that the recruiter signal is "I provide a one-command rebuild" not "I commit a sample".

- **`etl_metadata` table tracking pull date / source library version.** Recruiter signal of "this analyst captures provenance". Adds a row-per-pull table inside the SQLite DB. Not in REQUIREMENTS.md. Defer to v2 / V2-DOC-01 family.

- **Materialized `competitive_plays` table (vs view).** Performance optimization. At ~140k filtered rows the view is fast; if Phase 3 query latency on a recruiter's 8 GB laptop is >2 s on common queries, revisit. Not a v1 concern.

- **`--force` / `--years` / `--no-cache` CLI flags on `etl/run.py`.** Power-user dev ergonomics. Nick edits the seasons constant in `etl/columns.py` for dev iteration. If the constant-edit pattern friction-points later, add flags then. Not a v1 concern.

- **Network retry-with-backoff in loaders.** Discussed and rejected (D-15) — over-engineering for a stable nflverse CDN; row-count assertions catch the real risk (silent-empty-success per PITFALLS #17), not transient failure. If a future phase hits CDN flakiness in CI, revisit.

- **Sensitivity-check `all_plays` view.** Phase 3 STAT-08 ("same headline finding with vs without `competitive_plays` filter") can query the base `plays` table directly. No additional view needed in Phase 2. If Phase 3 finds the SQL repetition annoying, an `all_plays` view is a one-line addition.

- **Schema FK enforcement (`PRAGMA foreign_keys = ON`).** SQLite defaults to FKs disabled. The `ftn_play.FOREIGN KEY (game_id, play_id) REFERENCES plays(game_id, play_id)` declaration in SCHEMA-01 is documentation-only unless the pragma is enabled. Defer the pragma decision to Plan 02-01 (executor's call): turning it on costs a per-INSERT validation that may not matter at this scale. Not a recruiter-visible decision.

- **Parquet write tuning (compression, row groups, snappy vs zstd).** `df.to_parquet(path, index=False)` uses pyarrow defaults (snappy compression, default row-group size). Adequate for ~50k rows/year. If Phase 4 / SHIP-02 fresh-clone reproducibility surfaces a slow first-load, revisit.

- **Reviewed Todos (not folded)**

None — STATE.md "Pending Todos" was empty going into this phase.

</deferred>

---

*Phase: 02-data-layer-etl-sqlite-schema*
*Context gathered: 2026-04-29*
