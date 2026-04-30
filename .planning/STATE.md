# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-29)

**Core value:** A recruiter can clone the repo, run a single command, and within 2 minutes understand both the analytical insight and the engineering rigor behind it.
**Current focus:** Phase 4 — Story & Ship (Viz + Docs + Public GitHub) — Phase 3 complete, ready to discuss Phase 4

## Current Position

Phase: 3 of 4 (Analytical Layer — SQL + Python) — COMPLETE
Plan: All 3 plans landed. Wave 1 = 03-01 scaffolding (4 commits b941ecc..6218d9e). Wave 2 = 03-02 SQL queries (3 commits 4cb60de..f17effe) and 03-03 predictability modeling (4 commits 8ec47f3..524d345) executed in parallel on disjoint file sets. Verifier PASS (`03-VERIFICATION.md`): 15/15 must-haves, 17/17 REQ-IDs (QUERY-01..09 + STAT-01..08), 5/5 ROADMAP success criteria.
Status: Phase 3 COMPLETE. Analytical layer delivered: 8 SQL queries on `competitive_plays` with locked D-07 filenames + D-08 6-section headers; `analysis/_common.py` (SEED=42, get_conn, min_n_filter); `analysis/_style.py` (apply_style, colorblind palette); `analysis/01_exploratory.ipynb` + `02_predictability_modeling.ipynb` (jupytext-paired, outputs cleared). 4 substantive findings recorded for Phase 4 FINDINGS.md (see Decisions D-14..D-17 below).
Last activity: 2026-04-30 — Phase 3 fully executed and verified. 11 execution commits + 1 planning commit landed since pre-execution. Total Phase 3 wall-clock: ~37m (Wave 1: 18m, Wave 2: 11m + 8m parallel). Working tree clean.

Progress: [████████░░] 75%

## Performance Metrics

**Velocity:**
- Total plans completed: 7
- Average duration: 12.9m
- Total execution time: 90.5m (Phase 1: 35m / Phase 2: 18.5m / Phase 3: 37m)

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Foundation & FTN Pivot Calibration | 2 / 2 (COMPLETE) | 35m | 17.5m |
| 2. Data Layer (ETL + Schema) | 2 / 2 (COMPLETE) | 18.5m | 9.25m |
| 3. Analytical Layer (SQL + Python) | 3 / 3 (COMPLETE) | 37m | 12.3m |
| 4. Story & Ship | 0 | — | — |

**Recent Trend:**
- Phase 3 closed cleanly. 11 execution commits landed across 3 plans; verifier PASS first iteration with 15/15 must-haves, 17/17 REQ-IDs, 5/5 ROADMAP criteria. Wave 2 ran with both agents on the main working tree (no worktree isolation — Python venv is gitignored on Windows); the brief git index lock was the only concurrency surface and resolved cleanly. The disjoint-file-set decision held: `queries/`+`scripts/` (03-02) vs `analysis/02_*` (03-03) produced no merge conflicts.
- Phase 3 surfaced 4 substantive findings — see Decisions D-14..D-17. The most consequential is D-14 (n_blitzers threshold correction): both Wave 2 agents independently caught and fixed a misreading of the FTN column semantics during execution, which means the locked CONTEXT.md threshold (`> 4`) and the now-corrected operational threshold (`> 0`) disagree. Phase 4 must reconcile this in PROJECT.md operational definition (line 58), `docs/ftn-schema-audit.md` operational definition, and the README glossary before ship.
- Phase 2 plans landed in well under budget — 02-01 (Schema, 3 commits, 1 documented Rule-3 deviation on a comment substring); 02-02 (ETL, 6 commits, 4 documented deviations: 2 calibration findings against plan thresholds + 2 Windows runtime adjustments). Cold-cache end-to-end build was 36s vs 10m budget; warm-cache was 9s vs 5m budget.
- Trend: ahead of pace; project is 3/4 phases complete with the analytical content fully delivered. Phase 4 is FINDINGS.md memo + README hand-rewrite + GitHub MCP ship.

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Phase 1 = pivot calibration, not blank-slate audit (researchers have already confirmed the FTN public schema; Phase 1 measures NaN rates and locks 3–4 anchor dimensions)
- Public repo name decided at end of Phase 1 (likely `nfl-defensive-tendencies`); working folder stays `nfl-coverage-tendencies` for git history continuity
- Coarse phase granularity adopted: 4 phases (synthesizer's 6-phase prior consolidated; rationale in ROADMAP.md Overview)
- `competitive_plays` SQL view is a Phase 2 SCHEMA deliverable (single source of truth for play-type and win-probability filtering across all analytical queries)
- Predictability score normalization (`H/log(k)` over fixed support OR KL-from-baseline) MUST be the FIRST cell of `02_predictability_modeling.ipynb` (Phase 3)
- Ship via GitHub MCP (Phase 4): repo creation, topic config, social preview, pinning all use GitHub MCP tools — not manual `git push`
- **`nfl_data_py` two-step install pattern is the standard nflverse-community workaround** (Plan 01-01): upstream `0.3.3` metadata declares `pandas<2.0` which conflicts with our locked `pandas>=2.1,<2.3`. Install non-`nfl_data_py` deps first with strict resolver, then `nfl_data_py==0.3.3 --no-deps` (plus `appdirs>1`, `fastparquet>0.5`). Pin block stays as researched; install procedure adapts. Phase 4 / DOC-05 README setup block and SHIP-02 fresh-venv script MUST encode this.
- **Windows Python 3.11 launcher dispatch** (Plan 01-01): system `python` resolves to 3.14 by default on Windows 11; use `py -3.11` for venv creation. Cross-platform docs should reference `python3.11` or `py -3.11` (Windows) explicitly.
- **D-09 public GitHub repo name locked: `nfl-defensive-tendencies`** (Plan 01-02). Working folder stays `nfl-coverage-tendencies` for git history continuity. Phase 4 / SHIP-03 GitHub MCP repo creation uses `nfl-defensive-tendencies`.
- **4 anchor defensive dimensions locked** (Plan 01-02 / AUDIT-03): `n_blitzers` (pressure, S1 + S4 lead), `n_pass_rushers` (pressure, S2 lead), `is_play_action` (cross-cutting D-07 modifier), `n_offense_backfield` (personnel, S3 + S4). All 8 candidates survived the 30% NaN cutoff; selection became editorial (D-01 story tiebreaker).
- **4 pre-registered situations locked** (Plan 01-02 / AUDIT-04, `docs/analysis-plan.md`): S1 3rd-and-long (`down=3 AND ydstogo>=7`), S2 red zone (`yardline_100<=20`), S3 1st-and-10 (`down=1 AND ydstogo=10`), S4 2nd-and-medium (`down=2 AND ydstogo BETWEEN 3 AND 6`). FINDINGS.md headline insights firewalled to these 4.
- **FTN<->pbp match rate observed 0.9998** (Plan 01-02). Phase 2 ETL-04 keeps the > 0.95 floor; observed value gives ~5pp of headroom.
- **PROJECT.md pandas pin aligned** (Plan 01-02 / Pitfall #20 prevention): stale `pandas>=2.2,<2.4` corrected to `pandas>=2.1,<2.3`. PROJECT.md, requirements.txt, SUMMARY.md, PATTERNS.md now agree.
- **v2 candidate flagged**: pbp now exposes ngs-derived `defense_coverage_type` (0.025 NaN on pass) and `defense_man_zone_type` (0.023 NaN on pass) at populated rates. v1 stays as locked because pivot decision is in writing (D-09); using these would re-open the man-zone framing the project deliberately stepped away from. Documented in `docs/ftn-schema-audit.md`.
- **D-10: Scope expanded 2022-2024 → 2022-2025** (post-Phase-1 cleanup, commit 182ff15). The 2025 NFL season completed February 2026 with Super Bowl LX. Pre-pivot data-quality check (`scratch/verify_2025.py`) confirmed full schema parity (29 columns, no adds/removes), 4-season match rate 0.9999, all 8 anchor candidates re-validated against the 30% NaN cutoff. 4-season totals: 80,782 pass / 59,824 run / 140,606 competitive plays. Audit notebook re-run end-to-end; CSV regenerated. Adds current-season recency for recruiters without disturbing the locked anchor set or the 4-situation slate.
- **SHIP-08 filed** (post-Phase-1 cleanup): placeholder ship-guard requirement — `! grep -qE '<[A-Z_]{4,}>' README.md` and same for FINDINGS.md must hold before push. Enforced as a step in the SHIP-01 GitHub Actions workflow. Phase 4 count went from 20 → 21; total v1 reqs 55 → 56.
- **D-11 Phase 2 calibration: competitive_plays universe is 105,556 (not 140,606)** (Plan 02-02 end-to-end build, commit d680e09). Phase 1's 140,606 figure was measured pre-wp-filter (only `play_type IN ('pass','run')` applied). The locked D-04 predicate stack (wp 0.05-0.95 + qtr<=4 + end-of-half hurry-up exclusion) trims ~25% of competitive plays. View body in `schema/03_views.sql` is byte-exact to CONTEXT D-04. Phase 3 must reference 105,556 as the competitive universe — N≥30 / N≥100 sample-size discipline still has ample headroom (S1 3rd-and-long alone returns N=9,925).
- **D-12 Phase 2 calibration: match_rate semantic in build_db.py is pbp-play-type-coverage, not FTN/pbp join coverage** (Plan 02-02, commit 884fde8). With `pbp.merge(ftn, how='left')`, `joined['play_type'].notna().mean()` is the rate of non-null play_type on the pbp side (NaN for kickoffs / no_play / etc.) — observed 0.9705. Phase 1's 0.9999 was measured the OTHER direction (`ftn.merge(pbp)`). Both exceed the 0.95 floor; CONTEXT specifics explicitly mandated this exact formula. Phase 3 won't quote match_rate, but any future build_db maintainer needs to know the assertion does NOT verify FTN coverage of pbp — for that, query `(SELECT COUNT(*) FROM plays p LEFT JOIN ftn_play f USING (game_id, play_id) WHERE f.game_id IS NULL) / COUNT(plays)`. Flagged for v2 follow-up.
- **Phase 3 D-01..D-13 locked** (discuss-phase, commit 931b062): Predictability Index = H/log(k) headline + KL secondary with **Spearman ρ ≥ 0.85** validation gate (≥ = sensitivity check, < = substantive finding); blitz boolean (`n_blitzers > 4`) on `play_type='pass'` as the k=2 input dimension; both per-team-per-situation matrix (FINDINGS appendix) AND aggregate scalar (hero chart) shipped; `(1 − H/log(k)) × 100` mapping (high = predictable); sample-size-weighted aggregation with **min-N=30 dropout gate** (cells below floor are excluded, not down-weighted); PA ignored at index level (stays as Phase 1 D-07 stratifier for chi-square + narrative). 8-query slate hybrid path: 3 renamings (QUERY-02 `_by_situation`, QUERY-04 `_by_blitz`, QUERY-08 `_trend_by_season`); structured 6-section `.sql` header docblock locked (Question / Filter / Result shape / Hypothesis / Caveats / N expected). STAT-06 chi-square = **PA cross-cutting on S1** (blitz × is_play_action 2×2 on 3rd-and-long pass plays, league-aggregate scope, **odds ratio + Wilson 95% CI**, no Cramér's V). STAT-08 sensitivity = **Predictability Index leaderboard** recomputed with vs without `competitive_plays` (rank delta + Spearman ρ reported). `_common.py` API stays as Claude's Discretion with defaults documented in 03-CONTEXT.md.
- **D-14 Phase 3 calibration: blitz operational definition `n_blitzers > 4` corrected to `n_blitzers > 0`** (Plan 03-02 commit 4cb60de + Plan 03-03 commit cef2649; both agents caught it independently). FTN's `n_blitzers` column counts EXTRA rushers above the base 4-man front, NOT total pass rushers. Empirical evidence: `> 4` matched only 7–9 plays across 185,215 FTN rows (≈0.005%); corrected `> 0` yields a 29.4% league baseline blitz rate consistent with public benchmarks and the S1-H1 hypothesis. The `n_pass_rushers >= 5` threshold (total rushers) used in QUERY-03/05 is a separate definition and is unchanged. **Phase 4 must reconcile cross-doc threshold language**: PROJECT.md line 58 (operational definition), `docs/ftn-schema-audit.md` operational definition, README glossary, and FINDINGS.md narrative all currently reference the stale `> 4`. The corrected definition is what's in the queries and the predictability index, so the on-disk analytical surface is internally consistent — only the prose doc-set lags. Document this calibration prominently in FINDINGS.md so a recruiter can verify the threshold against the SQL.
- **D-15 Phase 3 finding: Spearman ρ = -0.111 between H/log(k) and KL leaderboards — D-01 validation gate FAILED (vs ≥ 0.85)** (Plan 03-03 commit cef2649). Per the locked D-01 protocol ("if observed ρ < 0.85, treat as substantive finding to investigate, NOT papered over"), this is a real result, not a regression. H/log(k) measures concentration of a defense's blitz pattern (how lopsided is its blitz/no-blitz mix?); KL divergence from the league baseline measures deviation from the average defense's mix. The two are orthogonal in this dataset — MIN ranks 32nd on concentration but 1st on KL deviation, because MIN's blitz rate sits far above league average without being internally lopsided. **Phase 4 FINDINGS.md must address this divergence head-on as a named methodology insight** ("the two natural definitions of 'predictable' disagree across this league" is itself a finding). Both leaderboards ship: H/log(k) is the headline 0–100 scalar (`(1 − H/log(2)) × 100`); KL is presented as the methodology-appendix sensitivity with the rank-delta table.
- **D-16 Phase 3 calibration: STAT-08 sensitivity Spearman ρ = 0.982 — predictability index leaderboard is robust to the wp filter** (Plan 03-03 commit bf2aba0). Top-5 most-predictable defenses are identical across `competitive_plays` (~57k pass plays) vs unfiltered `play_type='pass'` (~80,782 pass plays); max rank delta = 4. This adds a methodology-rigor signal in FINDINGS.md ("the headline isn't an artifact of our filter") that pairs naturally with the D-15 H-vs-KL divergence finding (one definition is robust to filter; the other isn't even consistent with itself). Headline universe stays at `competitive_plays`.
- **D-17 Phase 3 finding: STAT-06 chi-square (S1 PA × blitz) = chi2 3.464, p=0.063 (marginal at α=0.05)** (Plan 03-03 commit bf2aba0). Effect size: OR = 0.648 [0.418, 1.003] (defenses are about 35% LESS likely to blitz against play-action on 3rd-and-long, with the 95% CI grazing the null). Wilson 95% CI on `P(blitz | PA=1, S1)` = 0.248 [0.176, 0.336] (N=109); paired `P(blitz | PA=0, S1)` = 0.337. Observed gap of −8.94pp **exceeds the pre-registered 5pp gate** from `docs/analysis-plan.md` directionally, but the small PA=1 sample (N=109) limits inferential power and the p-value falls just outside the conventional α=0.05. **Headline framing:** suggestive directional evidence that defenses are more conservative against play-action on 3rd-and-long, with sample-size limitations honestly disclosed. Chi-square assumption (expected cell count ≥ 5) is comfortably satisfied — Fisher's exact fallback was not triggered.

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Deferred Items

Items acknowledged and carried forward (v2 backlog from REQUIREMENTS.md):

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Library | V2-LIB-01: migrate from `nfl_data_py` to `nflreadpy` | Deferred to v2 | Roadmap creation |
| Library | V2-LIB-02: re-pin `numpy>=2.0` post-migration | Deferred to v2 | Roadmap creation |
| Analysis | V2-PERS-01: add personnel-grouping context | Deferred to v2 | Roadmap creation |
| Analysis | V2-ML-01: simple defensive-tendency classifier | Deferred to v2 | Roadmap creation |
| Viz | V2-VIZ-01: animated play visualization (if tracking data appears) | Deferred to v2 | Roadmap creation |
| Docs | V2-DOC-01: inter-rater agreement on FTN subjective fields | Deferred to v2 | Roadmap creation |
| Docs | V2-DOC-02: custom hero-chart social preview iteration | Deferred to v2 | Roadmap creation |

## Session Continuity

Last session: 2026-04-30
Stopped at: Phase 3 COMPLETE. All 3 plans executed and verified. 11 execution commits + 1 planning commit landed. 4 substantive findings recorded as D-14..D-17 above (n_blitzers correction, Spearman gate failure, sensitivity robustness, S1 PA×blitz chi-square). The analytical content is fully delivered; Phase 4 is the recruiter-facing surface (FINDINGS.md memo + README hand-rewrite + GitHub MCP ship). Phase 4 has 21 requirements (VIZ-01..05, DOC-01..08, SHIP-01..08).
Resume file: `.planning/phases/03-analytical-layer-sql-python/03-VERIFICATION.md` (verification report). Run `/gsd-discuss-phase 4` to capture Phase 4 design decisions before planning, then `/gsd-plan-phase 4`.
