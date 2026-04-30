# Phase 3: Analytical Layer (SQL + Python) - Context

**Gathered:** 2026-04-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Every business question from `docs/analysis-plan.md` (the locked 4-situation slate + cross-cutting `is_play_action` modifier) gets a SQL artifact AND Python statistical evidence. The deliverables, in directory terms:

- `queries/01_*.sql` … `queries/08_*.sql` — 8 SQL files, each reading from the `competitive_plays` view (Phase 2 SCHEMA-03), each with a structured 6-section header docblock, satisfying QUERY-09 meta-compliance (window functions + CTEs + cross-source FTN↔pbp join).
- `analysis/_common.py` — `SEED=42`, SQLite connection helper, `min_n_filter()` helper.
- `analysis/_style.py` — matplotlib rcParams (savefig.dpi=200, font sizes, color palette).
- `analysis/01_exploratory.ipynb` — descriptive stats + sample-size profiling per situation; flags any cell falling below N=30.
- `analysis/02_predictability_modeling.ipynb` — normalization scheme in cell 1, predictability index, chi-square + odds ratio + Wilson 95% CI, sensitivity check.

Out of scope for this phase: `analysis/03_visualizations.ipynb` and `findings/images/*.png` (Phase 4 / VIZ-01..05), `findings/FINDINGS.md` memo (Phase 4 / DOC-01..02), README hand-rewrite (Phase 4 / DOC-03..07), GitHub Actions workflow (Phase 4 / SHIP-01), public repo creation (Phase 4 / SHIP-03).

</domain>

<decisions>
## Implementation Decisions

### Predictability Index design (STAT-04, STAT-05, STAT-07, STAT-08)

The headline analytical artifact. Cell 1 of `02_predictability_modeling.ipynb` locks the methodology before any team-level computation runs.

- **D-01 Normalization = `H/log(k)` headline + KL secondary.** Cell 1 of `02_predictability_modeling.ipynb` defines the primary metric as Shannon entropy normalized by `log(k)` over fixed support `k=2`. KL divergence from the league baseline is computed in a follow-on cell against the same per-team distributions.
  - **Validation gate:** Spearman rank correlation between the H/log(k)-derived ranking and the KL-derived ranking is reported in the comparison table. **Spearman ρ ≥ 0.85** = the two rankings agree; KL serves as the methodological sensitivity check (STAT-08 contribution). **Spearman ρ < 0.85** = the divergence is treated as a substantive finding to investigate, NOT papered over.
  - **Rationale:** H/log(k) and KL measure different things — concentration vs. deviation-from-league. For the headline "predictability" framing, concentration is the right concept (a team that always does what the league does is still predictable, even though their KL would be zero).

- **D-02 Input dimension = blitz boolean (`n_blitzers > 4`).** k=2 fixed support. Computed on `play_type='pass'` rows only (the operational definition from `docs/ftn-schema-audit.md`). Cleanest defensive-tendency signal; the most recruiter-recognizable; the only single anchor that fits in the README glossary in one sentence.

- **D-03 Aggregation = both: per-team-per-situation matrix in FINDINGS + aggregate scalar in hero chart.**
  - The 32-team × 4-situation matrix is the FINDINGS.md methodology-appendix artifact (table or heatmap).
  - The per-team aggregate scalar is the headline hero-chart leaderboard (`findings/images/01_predictability_ranking.png`, locked in Phase 1 D-09 / VIZ-02).
  - Same data, two views, two consumers (analyst-narrative reader vs. recruiter glance-test).

- **D-04 0–100 mapping = `(1 − H/log(k)) × 100`.** High score = more predictable. 0 = uniform (truly unpredictable, 50/50 blitz/no-blitz league-wide); 100 = always one choice (deterministic). Inverts the raw entropy ratio so the leaderboard reads naturally for a non-football recruiter ("the 49ers' defense scores 78/100 on predictability"). The README glossary defines the metric in one sentence using this mapping.

- **D-05 Aggregate scalar weighting = sample-size weighted with min-N gate at N≥30.** Per-team aggregate score = sample-size-weighted mean of the per-(team × situation) indexes across the 4 pre-registered situations, **excluding** any per-(team × situation) cell where the team's N for that situation falls below the project-wide baseline tier (N≥30 from CLAUDE.md / STAT-07). Dropped cells are documented in the methodology appendix table (the team's matrix row shows the dropped cell as "N/A — below N≥30 floor"). Cleaner than down-weighting low-N cells to near-zero; explicit about which teams have how much data.

- **D-06 `is_play_action` treatment in the index = ignore at the index level.** The index uses raw blitz boolean across ALL pass plays in each situation — not stratified by PA. PA stays as the Phase 1 D-07 cross-cutting modifier for the chi-square test (D-09 below) and FINDINGS.md narrative analysis only. Keeps the headline metric explainable in the README glossary in one sentence; avoids double-counting the predictability signal across PA strata when small-N cells (S1/S4 PA-stratified) would force partial dropouts.

### 8-query slate (QUERY-01 through QUERY-09)

The locked filename slate, organized as rollup MATERIALS — SQL produces tables, notebooks compute hypothesis tests:

- **D-07 Locked slate:**

  | # | Filename | Question / coverage |
  |---|----------|---------------------|
  | 01 | `queries/01_tendency_distribution_by_team.sql` | League baseline + per-team blitz rate (KL input for predictability index) |
  | 02 | `queries/02_blitz_rate_by_situation.sql` | **renamed** from `_by_down_and_distance`; one row per (defteam × situation) covering S1/S2/S3/S4 explicitly |
  | 03 | `queries/03_red_zone_vs_midfield.sql` | S2 hypothesis material (red zone vs outside-the-20 comparator) |
  | 04 | `queries/04_epa_allowed_by_blitz.sql` | **renamed** from `_by_<dim>`; EPA-allowed when defense blitzes vs not, by situation; dimension = blitz boolean (mirrors D-02 input) |
  | 05 | `queries/05_third_long_pressure_tendencies.sql` | S1 deep-dive with both pressure anchors (`n_blitzers` AND `n_pass_rushers`) |
  | 06 | `queries/06_play_action_response.sql` | Cross-cutting D-07 modifier — defensive blitz rate against PA vs straight dropback per situation |
  | 07 | `queries/07_situational_predictability_score.sql` | Per-team-per-situation entropy raw inputs (`defteam`, `situation`, `blitz_count`, `no_blitz_count`, `total`) — feeds D-01..D-06 |
  | 08 | `queries/08_blitz_rate_trend_by_season.sql` | **renamed** from `_week_over_week_drift`; per-season league + per-team blitz rate 2022→2025 (D-10 four-season scope narrative) |
  | 09 | meta-compliance | All queries reference `competitive_plays`, structured 6-section header, slate-collective coverage of window fns + CTEs + cross-source FTN↔pbp join |

- **D-08 Header convention = structured 6-section comment block at the top of every `.sql` file:**
  ```sql
  -- ---
  -- Question:    [the analytical question, 1 sentence]
  -- Filter:      [the subset of competitive_plays this query operates on]
  -- Result shape: [output columns with types and meaning]
  -- Hypothesis:  [analysis-plan.md hypothesis ID if applicable, e.g., "S1-H1"; "n/a" if rollup material]
  -- Caveats:     [low-N risk, NaN-on-run-plays note for blitz queries, etc.]
  -- N expected:  [order of magnitude based on Phase 2 verified counts]
  -- ---
  ```
  Scan-friendly, recruiter can read the question without parsing SQL. Doubles as the input the QUERY-09 meta-compliance check parses.

### Chi-square + Wilson CI + sensitivity (STAT-06, STAT-08)

- **D-09 Chi-square headline target = PA cross-cutting on S1 (blitz × `is_play_action` 2×2 on 3rd-and-long pass plays).** League-aggregate 2×2 contingency: `n_blitzers > 4` (y/n) × `is_play_action` (y/n) on `down=3 AND ydstogo>=7 AND play_type='pass'` rows of `competitive_plays`. Tests the analysis-plan.md PA cross-cutting hypothesis ("league blitz rate against play-action vs straight dropback gap ≥ 5pp"). Activates the cross-cutting D-07 (Phase 1) modifier in the headline test; both anchor categories (pressure + play-fakery) feature simultaneously.

- **D-10 Test scope = league-aggregate 2×2.** Single contingency on all 32 teams pooled. Matches the analysis-plan.md hypothesis phrasing ("league-wide rate"). Team-by-team variance lives in the predictability index (D-01..D-06), not in the chi-square. NO supplemental 32×2 omnibus team-variance test.

- **D-11 Effect size = odds ratio + 95% CI.** Football-analytics-native interpretation ("defenses are X.Y× more likely to blitz on PA"). Direct, recruiter-readable; pairs naturally with the Wilson 95% CI on the proportion (D-12). Cramér's V is not also reported — odds ratio + Wilson CI is the locked pair.

- **D-12 Wilson 95% CI on the league blitz rate against play-action.** The Wilson CI per STAT-06 goes on the proportion `P(blitz | is_play_action=1, S1, competitive_plays)` — the "treatment" condition that drives the headline narrative. The complementary proportion (against straight dropback) is reported as a paired number alongside; only the play-action proportion gets the explicit CI cell.

- **D-13 STAT-08 sensitivity target = Predictability Index leaderboard.** Recompute the per-team predictability scalar AND the per-(team × situation) matrix twice:
  1. On the `competitive_plays` universe (locked headline; ~57k pass plays after wp/qtr filter).
  2. On the unfiltered `play_type='pass'` universe (~80k pass plays, no wp/qtr filter — bypasses the `competitive_plays` view entirely).

  Report rank delta and Spearman correlation between the two leaderboards in the methodology appendix. Tests whether the headline rests on the wp filter; doubles as a methodology-rigor signal in FINDINGS.md ("the leaderboard's top-5 is identical across filters; ranks 6–32 shift by ≤2 positions"). The chi-square headline is NOT also re-run on both universes — STAT-08 requires only one sensitivity check.

### Claude's Discretion

The user explicitly skipped the `_common.py` helper API gray area at the top of this discussion (4-area selection rejected option D). Claude has flexibility on the following during planning/execution; defaults documented for the planner:

- **`_common.py` connection helper:** Default to a function `get_conn(db_path: Path | str = DB_PATH) -> sqlite3.Connection` that returns a plain `sqlite3.Connection` opened with `detect_types=sqlite3.PARSE_DECLTYPES`. Notebook usage: `with get_conn() as conn: df = pd.read_sql_query(SQL_PATH.read_text(), conn)`. No SQLAlchemy. Path constant lives in `_common.py`: `DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nfl_defensive_tendencies.db"`.
- **`min_n_filter()` signature:** Default to `min_n_filter(df: pd.DataFrame, n_col: str = "n", n_threshold: int = 30) -> pd.DataFrame` returning the filtered DataFrame (rows where `df[n_col] >= n_threshold`). Does NOT raise — emits a `logging.WARNING` listing the dropped (defteam, situation) tuples. The narrative low-N flag for the N≥15 exception lives in the FINDINGS.md cell that emits the claim, not in the helper.
- **`SEED=42` placement:** Module-level constant in `_common.py`. Imported and reseeded at the top of every notebook (`np.random.seed(SEED)`).
- **`_style.py` color palette:** Default to a neutral analyst palette (seaborn `colorblind`-derived 6-color set). Per-team 32-color palette is NOT required for v1; if Phase 4 hero chart wants per-team colors, that's a Phase 4 / VIZ-01 decision.
- **Exploratory notebook scope (STAT-03):** Stay close to the requirement — descriptive stats per situation, sample-size profiling, flag-cells-below-N=30. Add per-team play counts and anchor-distribution plots if execution has slack. Anything beyond the 4 pre-registered situations is labeled "Exploratory; not a headline finding" per the analysis-plan.md firewall.
- **QUERY-09 distribution:** Slate-collective coverage is sufficient (at least one query has a window function, at least one has a CTE, at least one has a cross-source FTN↔pbp join). Most pressure queries naturally need all three; demanding all three in every query is mild over-engineering, harmless if it happens.
- **Schema for QUERY-07 predictability raw inputs:** Default columns `(defteam, season, situation_id, blitz_count, no_blitz_count, total_pass_plays)` where `situation_id` ∈ {S1, S2, S3, S4}. Notebook computes per-team distributions from this rollup.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (gsd-phase-researcher, gsd-planner) MUST read these before planning or implementing.**

### Project-level constraints (read first)

- `CLAUDE.md` — Locked stack, file-organization rules (`/queries`, `/analysis`; never repo root), audience voice. Non-negotiables. **In particular** the "Project Realities to Remember" section (predictability normalization MUST be cell 1; sample-size discipline tiers; `competitive_plays` as SSOT) directly governs Phase 3 deliverables.
- `.planning/PROJECT.md` — Vision, Out of Scope, Key Decisions table. **D-10 (4-season scope 2022–2025)** is the narrative anchor for QUERY-08.
- `.planning/REQUIREMENTS.md` — `QUERY-01..09` + `STAT-01..08` acceptance criteria. The placeholder filenames in REQUIREMENTS.md are SUPERSEDED by the locked slate in D-07 above (3 renamings: QUERY-02, QUERY-04, QUERY-08); REQ-IDs are unchanged.
- `.planning/ROADMAP.md` §Phase 3 — Phase boundary, success criteria (1–5), plan ordering (03-01 scaffolding → 03-02 queries || 03-03 predictability modeling), in-phase parallelism rules.

### Pre-registered analytical scope (the firewall)

- `docs/analysis-plan.md` — **THE locked situational slate.** S1/S2/S3/S4 filters + falsifiable hypotheses + cross-cutting PA modifier + sample-size discipline tiers + live N counts against the Phase 2 build. The chi-square headline (D-09) tests the PA cross-cutting hypothesis from this doc; the predictability index (D-01..D-06) operates inside the 4-situation slate. **Anything outside this slate stays in `01_exploratory.ipynb` and is labeled "Exploratory; not a headline finding."**
- `docs/ftn-schema-audit.md` — Anchor dimension narrative; the operational definition `blitz = n_blitzers > 4` (used in D-02 and D-09) is locked here; NaN-rate notes for run plays (the blitz queries filter `play_type='pass'` first per the audit).

### Research backbone (read in this order)

- `.planning/research/SUMMARY.md` §"Top 5 Must-Shape-the-Plan Findings" #4 (predictability normalization is the open methodology problem; D-01 closes it) and §"TL;DR" (predictability normalization MUST be cell 1).
- `.planning/research/PITFALLS.md` — **#9** multiple-comparisons trap (the 4-situation firewall is the substitute for Bonferroni; predictability index treats the slate as locked, not scanned), **#8** sample-size discipline (N≥30/100/15-flag tiers; STAT-07 enforcement; D-05 min-N gate), **#11** entropy normalization (the H/log(k) primary in D-01 directly addresses this), **#13** chi-square assumptions (expected cell count ≥ 5 — relevant to D-09 if any cell underflows; fall back to Fisher's exact only if it does).
- `.planning/research/ARCHITECTURE.md` — `analysis/` directory layout, notebook output discipline (clear-output before commit; figures live only in `findings/images/`).
- `.planning/research/STACK.md` — `scipy>=1.13,<1.18` for `chi2_contingency` and `entropy`; `seaborn==0.13.2` for `heatmap`; `numpy<2.0` constraint propagates.
- `.planning/research/FEATURES.md` — Anti-features list (no Streamlit, no excessive viz; FINDINGS.md is memo, not tutorial — applies to the methodology-appendix tables driven by D-03 and D-13).

### Phase 1 + Phase 2 outputs (this is what Phase 3 reads from)

- `.planning/phases/01-foundation-ftn-pivot-calibration/01-CONTEXT.md` — Phase 1 D-01..D-10 (anchor dimensions, 4 situations, repo name, scope expansion). The 4 anchors and 4-situation slate flow directly into D-02, D-07, and D-09 above.
- `.planning/phases/02-data-layer-etl-sqlite-schema/02-CONTEXT.md` — Phase 2 D-01..D-16 (`competitive_plays` view definition, schema column whitelists, ETL idempotency). The view body in `schema/03_views.sql` is the byte-exact contract every Phase 3 query reads from.
- `schema/03_views.sql` — The locked `competitive_plays` view definition. Phase 3 must NOT relax or modify these predicates; all 8 queries reference the view.
- `schema/01_create_tables.sql` — `plays` and `ftn_play` table column lists. The cross-source join in D-07 (slate-collective; specifically QUERY-04, QUERY-05, QUERY-06, QUERY-07, QUERY-08) is `competitive_plays` (pbp) ⨯ `ftn_play` (ftn) on `(game_id, play_id)`.
- `data/nfl_defensive_tendencies.db` — The verified Phase 2 build (1,139 games / 197,362 plays / 185,215 ftn_play / 105,556 competitive_plays). N expected values in the QUERY-09 headers should reference these counts as the order-of-magnitude.
- `analysis/00_data_audit.ipynb` — The Phase 1 audit notebook. Phase 3 notebooks (`01_exploratory`, `02_predictability_modeling`) follow the same conventions: jupytext-paired `.py`, outputs cleared before commit, plain `df.describe()` style + seaborn for non-hero visualizations.

### No external ADRs

Same as Phases 1 and 2: this project doesn't use a `docs/decisions/adr-*.md` system. Decisions live in `.planning/PROJECT.md` Key Decisions and these CONTEXT.md files.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets (already on disk from Phases 1 + 2)

- **`schema/03_views.sql`** — The `competitive_plays` view body is byte-exact to Phase 2 D-04. Every Phase 3 query reads from `competitive_plays`; reading from `plays` directly is reserved for the STAT-08 sensitivity check (D-13).
- **`etl/columns.py`** — Owns `SEASONS = [2022, 2023, 2024, 2025]`. `analysis/_common.py` should NOT redefine seasons; if a notebook needs to filter, it imports `from etl.columns import SEASONS`.
- **`data/nfl_defensive_tendencies.db`** — The verified DB regenerable via `python -m etl.run`. Phase 3 development reads from this; the DB is gitignored. `_common.py:DB_PATH` points here.
- **`analysis/00_data_audit.ipynb` + paired `.py`** — Establishes the notebook conventions: `import nfl_data_py as nfl` for live pulls (rare in Phase 3 — DB is the read source), jupytext pairing, `nbconvert --clear-output --inplace` before commit, plain matplotlib + seaborn (no Plotly, no Bokeh).
- **`requirements.txt`** — Stack is locked. `scipy>=1.13,<1.18` provides `scipy.stats.chi2_contingency`, `scipy.stats.fisher_exact` (fallback for D-09 if any 2×2 cell underflows the chi-square assumption), `scipy.stats.entropy`. `numpy<2.0` constraint is inherited.

### Established patterns

- **Path management:** `pathlib.Path` throughout (per `00_data_audit.ipynb`). `_common.py:DB_PATH` is a `Path`; `SQL_PATH = Path(__file__).resolve().parent.parent / "queries" / "07_situational_predictability_score.sql"` is the loading idiom.
- **SQL loading idiom (notebook):** `sql = (Path(__file__).parent.parent / "queries" / "07_situational_predictability_score.sql").read_text(); df = pd.read_sql_query(sql, conn)`. Each `.sql` file is one logical query; no f-string interpolation into SQL bodies.
- **Notebook output discipline:** Clear outputs via `nbconvert --clear-output --inplace` before commit. Hero PNGs (Phase 4 / VIZ-01..05) live ONLY in `findings/images/`, never inside committed notebook outputs.
- **Assertion style:** plain `assert` statements with f-string error messages (per `00_data_audit.ipynb` and the Phase 2 ETL pattern). `min_n_filter()` does NOT use `assert` — it returns a filtered DataFrame and logs warnings (per Claude's Discretion above).

### Integration points

- **`_common.py` ↔ `data/nfl_defensive_tendencies.db`:** Sole DB read boundary. `get_conn()` returns `sqlite3.Connection`; notebooks use `with get_conn() as conn: ...`. No SQLAlchemy.
- **Notebook ↔ `queries/*.sql`:** Read SQL bodies via `Path.read_text()`; execute via `pd.read_sql_query`. Notebook owns post-processing (entropy calc, chi-square test, Wilson CI); SQL owns rollup-shape production.
- **`02_predictability_modeling.ipynb` ↔ `queries/07_situational_predictability_score.sql`:** Cell 1 reads the rollup, computes H per (team × situation), normalizes by `log(k=2)`, applies the 0–100 mapping (D-04), and produces both the per-(team × situation) matrix and the aggregate scalar (D-03, D-05).
- **`02_predictability_modeling.ipynb` ↔ chi-square + sensitivity:** Subsequent cells in the same notebook execute D-09..D-13. NOT split into a separate notebook; STAT-04..08 stay in `02_predictability_modeling.ipynb` per REQUIREMENTS.md.
- **`01_exploratory.ipynb` ↔ `queries/`:** Reads multiple queries (likely QUERY-01, QUERY-02, QUERY-07) for descriptive stats + sample-size profiling per situation. Stays inside the 4-situation slate firewall.

### Greenfield within Phase 3

- `queries/` is empty. All 8 SQL files in D-07 are greenfield.
- `analysis/_common.py`, `analysis/_style.py`, `analysis/01_exploratory.ipynb`, `analysis/02_predictability_modeling.ipynb` are all greenfield. The only existing files in `analysis/` are `00_data_audit.ipynb` + paired `.py` (Phase 1).
- The patterns established here (`_common.py` API, header docblock convention, notebook structure) become the analog Phase 4's `03_visualizations.ipynb` will reference and extend.

</code_context>

<specifics>
## Specific Ideas

- **The validation gate for KL secondary check is Spearman ρ ≥ 0.85.** This is a substantive methodological commitment, not a sensitivity-check footnote. Cell 1 of `02_predictability_modeling.ipynb` writes the gate explicitly; the comparison table prints the observed ρ alongside the rank delta. If observed ρ < 0.85, FINDINGS.md treats the divergence as a substantive insight — investigate which teams/situations drive the disagreement, document, and decide whether the H/log(k) headline still holds. Do not paper over.

- **The 0–100 mapping inverts entropy on purpose.** `(1 − H/log(k)) × 100` reads naturally as "predictability score" for a recruiter — high score = more predictable. The mathematically literal `H/log(k) × 100` would read backwards (high score = more random, contradicting the README hook). Cell 1 documents the inversion in the rationale paragraph.

- **Aggregate scalar drops cells below N≥30, does NOT down-weight them.** Per D-05: a (team × situation) cell with N<30 is excluded from the team's aggregate score (and the matrix shows "N/A — below floor"). This is cleaner than continuous down-weighting because the threshold is the same as the project-wide claim threshold (CLAUDE.md / STAT-07). The methodology-appendix table makes the dropouts visible.

- **The chi-square headline is the PA cross-cutting test on S1, not S2-H1.** D-09 picks PA × blitz on 3rd-and-long because (a) it activates the cross-cutting D-07 (Phase 1) modifier in the headline, (b) both anchor categories (pressure + play-fakery) feature simultaneously, and (c) it's the most recruiter-readable football question ("does play-action change how often defenses blitz on 3rd-and-long?"). S2-H1 (red zone pressure differential) and S1-H1 (3rd-and-long blitz benchmark) are tested as descriptive comparisons in the FINDINGS.md narrative without a formal chi-square / odds ratio.

- **Odds ratio is the primary effect-size measure, not Cramér's V.** D-11 picks odds ratio because it reads as a multiplicative interpretation in the FINDINGS narrative ("defenses are 1.4× more likely to blitz against play-action"). Cramér's V would read as an abstract association strength on [0,1] and require a glossary entry. Wilson 95% CI on the proportion (D-12) is reported as a paired number; the narrative cites both ("blitz rate against PA = 47% [95% CI 44–50%]; OR vs straight dropback = 1.4×").

- **STAT-08 sensitivity is the predictability index leaderboard, not the chi-square.** D-13 picks the index leaderboard because it IS the headline visual — the rank-delta + Spearman comparison directly answers "did your filter change the leaderboard?" The chi-square is NOT also re-run on both universes; the requirement specifies one sensitivity check, the index gets it.

- **Sensitivity-check denominators are concrete.** With-filter universe = `competitive_plays` pass plays only ≈ 57k rows (D-04 trims competitive_plays to 105,556 total; pass-only is ~57k). Without-filter universe = `plays WHERE play_type='pass'` ≈ 80,782 pass plays (the verified 4-season pass-play count from PROJECT.md / STATE.md). The sensitivity-check cell in `02_predictability_modeling.ipynb` runs both queries against the SQLite DB; reports per-team rank delta + Spearman ρ.

- **`queries/02_blitz_rate_by_situation.sql` produces 4 situation rollups in one query.** Output rows: `(defteam, season, situation_id ∈ {S1, S2, S3, S4}, blitz_count, no_blitz_count, total_pass_plays, blitz_rate)`. Notebook filters to a single situation as needed; SQL produces all 4 in one CTE chain. Reduces 4 separate queries to 1 — efficient and the result-shape contract reads cleanly in the header.

- **`queries/07_situational_predictability_score.sql` is the predictability index's data source.** Schema: `(defteam, season, situation_id, blitz_count, no_blitz_count, total_pass_plays)`. The notebook computes H per row, normalizes, aggregates per D-05. SQL does NOT compute entropy itself — that's a notebook responsibility. Keeps the SQL portable; recruiters can re-run the entropy calc with a different normalization scheme without rewriting SQL.

- **QUERY-08 cross-season trend is per-(season × team) rollup, not per-week.** Output: `(defteam, season, blitz_count, no_blitz_count, total_pass_plays, blitz_rate)`. League aggregate row included (`defteam='LEAGUE'` or NULL convention — planner's call). Recruiter narrative: "is the league trending more aggressive year-over-year?" Plus per-team trend lines for the top-5 most-predictable defenses (Phase 4 visualization decision, not Phase 3).

</specifics>

<deferred>
## Deferred Ideas

These came up during discussion (or are implied by the locked decisions) but are out of Phase 3 scope. Capture so future phases / v2 don't re-discover.

- **`_common.py` API discussion.** User explicitly skipped this gray area (Area 4 of 4 deselected). Defaults are documented under Claude's Discretion above. If Plan 03-01 surfaces an actual API mismatch with downstream notebook needs, revisit during execution; otherwise the defaults stand.

- **Per-anchor parallel predictability indexes.** D-02 picks blitz boolean as the headline input. Computing parallel indexes on `n_pass_rushers` (binned) or `n_offense_backfield` (multi-category) is a v2 enrichment; would surface "which dimension drives predictability" as a richer narrative but multiplies the methodology-appendix footprint.

- **Stratified-by-PA predictability index.** D-06 ignores PA at the index level. A future v2 enrichment could compute an 8-cell-per-team (4 situations × 2 PA strata) index with appropriate small-N handling. Risk: PA-stratified S1/S4 cells fall below N≥30 for many teams; the dropout count would dwarf the analytical signal.

- **Team-level 32×2 omnibus chi-square.** D-10 picks league-aggregate 2×2. A team-variance omnibus (32×2 contingency, "is at least one team different from the league?") is interesting but doesn't match analysis-plan.md hypothesis phrasing; redundant with the predictability index variance signal. Not in v1.

- **Cramér's V alongside odds ratio.** D-11 picks odds ratio + Wilson CI as the locked pair. Cramér's V would generalize past 2×2 if a supplemental test is ever added; not needed in v1.

- **Chi-square assumption fallback (Fisher's exact).** Per PITFALLS #13, chi-square requires expected cell count ≥ 5. The S1 PA × blitz 2×2 has ~10k pass plays in the denominator; cell counts are deeply above the floor. If the cell count ever underflows in a future variant, fall back to `scipy.stats.fisher_exact`. Not a v1 concern.

- **QUERY-08 within-season week-over-week drift.** D-08 reframes QUERY-08 to cross-season trend. The within-season week-over-week version (the original REQUIREMENTS.md placeholder) is a v2 enrichment — interesting for "in-season tendency stability" but harder to fit into the 5–7 named insight FINDINGS.md slot.

- **Per-team color palette in `_style.py`.** Default to a neutral analyst palette (Claude's Discretion). Per-team 32-color palette is a Phase 4 / VIZ-01 decision if the hero chart wants per-team colors; v2 if the analytical narrative needs per-team identity in non-hero charts.

- **Caching the `_common.py` `get_conn()` result.** SQLite `connect()` is cheap; no caching needed at this scale. If a future Phase 3 notebook makes 50+ queries in a tight loop, revisit. Not a v1 concern.

- **Schema FK enforcement (`PRAGMA foreign_keys = ON`).** Phase 2 deferred this to executor's call. Phase 3 reads from the DB; doesn't write. Not a Phase 3 concern.

- **Reviewed Todos (not folded)**

  None — STATE.md "Pending Todos" was empty going into this phase.

</deferred>

---

*Phase: 03-analytical-layer-sql-python*
*Context gathered: 2026-04-30*
