---
phase: 01-foundation-ftn-pivot-calibration
plan: 02
subsystem: audit
tags: [ftn, nfl-data-py, schema-audit, pivot-calibration, pre-registration, analysis-plan]

# Dependency graph
requires:
  - phase: 01-foundation-ftn-pivot-calibration/01
    provides: "Locked Python 3.11 stack (nfl_data_py 0.3.3 + pandas>=2.1,<2.3 + numpy<2.0); two-step install pattern; analysis/, audit/, docs/ directories"
provides:
  - "Calibrated 4-anchor defensive dimension set: n_blitzers, n_pass_rushers (pressure), is_play_action (D-07 cross-cutting modifier), n_offense_backfield (personnel)"
  - "audit/ftn_null_profile.csv: per-column NaN rates for 53 joined-frame columns x 9 play_type values across 137,899 FTN rows for 2022-2024"
  - "FTN<->pbp join pattern: validate='one_to_one' on (nflverse_game_id, nflverse_play_id), match_rate observed 0.9998 (Phase 2 ETL-04 inherits this)"
  - "docs/ftn-schema-audit.md (156 lines): names the 4 chosen anchors; flags ngs defense_coverage_type / defense_man_zone_type as v2 candidate"
  - "docs/analysis-plan.md (167 lines): pre-registers 4 situations (S1 3rd-and-long, S2 red zone, S3 1st-and-10, S4 2nd-and-medium) with H1+H2 falsifiable hypotheses each (9 'Falsified if' clauses total)"
  - "Public GitHub repo name locked: nfl-defensive-tendencies (D-09 in PROJECT.md Key Decisions); working folder stays nfl-coverage-tendencies"
  - "SPEC.md 8 business questions reframed in place around the 4 anchors; no analytical Cover-shell / man-zone references remain in Business Questions section"
  - "README.md Hook filled with 3-paragraph post-pivot framing + 2 placeholder slots for Phase 4"
  - "PROJECT.md pandas pin aligned with requirements.txt: stale >=2.2,<2.4 removed; locked >=2.1,<2.3 confirmed (Pitfall #20 doc-vs-code drift prevention)"
affects: [02-data-layer, 03-analytical-layer, 04-story-and-ship]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "FTN<->pbp join: left_on=['nflverse_game_id','nflverse_play_id'], right_on=['game_id','play_id'], validate='one_to_one'; observed match_rate 0.9998 - threshold 0.95 confirmed safe"
    - "Pitfall #4 borne out empirically: n_blitzers and n_pass_rushers are 0.000 NaN on play_type='pass' AND 1.000 NaN on play_type='run'. Filtering to pass plays before any blitz computation is mandatory."
    - "Audit notebook authored as paired jupytext .py + .ipynb; outputs cleared via nbconvert --clear-output --inplace before commit (VIZ-04 pattern established)"

key-files:
  created:
    - "analysis/00_data_audit.ipynb (paired) and analysis/00_data_audit.py - 7-cell audit notebook"
    - "audit/ftn_null_profile.csv - 53 rows x 9 play_type cols, NaN rates rounded to 3 decimals"
    - "docs/ftn-schema-audit.md - 156-line analytical narrative naming 4 anchors"
    - "docs/analysis-plan.md - 167-line pre-registration with 4 situations + cross-cutting D-07 modifier"
  modified:
    - ".planning/PROJECT.md - appended D-09 row + corrected stale pandas pin (Pitfall #20)"
    - "SPEC.md - in-place rewrite of 8 Business Questions around chosen anchors"
    - "README.md - filled Hook section with 3-paragraph post-pivot framing + 2 placeholder slots"

key-decisions:
  - "Live FTN frame returned 29 columns for 2022-2024 (nfl_data_py 0.3.3 against current nflverse CDN), one more than the 28-column inventory documented in PITFALLS.md #2. Addition is `n_defense_box`, NaN-clean across all play types. Documented in ftn-schema-audit.md."
  - "All 8 candidate FTN columns survived the D-02 30% NaN cutoff. D-04 contingency does not apply. Anchor selection became editorial (D-01 story tiebreaker) rather than mechanical."
  - "Chosen 4 anchors span 3 categories: 2 pressure (n_blitzers + n_pass_rushers), 1 play-fakery (is_play_action, also serving as the D-07 cross-cutting modifier), 1 personnel (n_offense_backfield). qb_location, starting_hash, is_screen_pass, is_rpo remain available as exploratory or stratifier columns in 01_exploratory.ipynb but are NOT headline anchors."
  - "FTN<->pbp match rate observed 0.9998 across 3 seasons (137,899 of 137,899 FTN rows joined). Phase 2 ETL-04 should keep the >0.95 floor; the observed value gives ~5pp of headroom against future nflverse drift."
  - "MAJOR FINDING flagged for v2: nfl.import_pbp_data() now returns defense_coverage_type and defense_man_zone_type columns (sourced from NFL Next Gen Stats since the original research pass) at 0.025 / 0.023 NaN on play_type='pass' - well below the 30% cutoff. These are NOT in FTN; they live on pbp. The v1 plan stays as locked because the pivot decision is in writing (D-09), the analysis plan is pre-registered, and using ngs-derived coverage labels would re-open the man-zone framing the project deliberately stepped away from. Documented in ftn-schema-audit.md under 'Subsequent finding worth flagging for v2'."

patterns-established:
  - "Notebook authoring: jupytext-paired .py for clean diffs + .ipynb executed and cleared. The .py is the editable source; the .ipynb is the runnable artifact. Both committed."
  - "Schema-audit voice: numbers-first memo style with zero exclamation points, modeled on PITFALLS.md Pitfall #2 prose. Every claim states the NaN rate or the row count inline."
  - "4-situation firewall: SQL filters in docs/analysis-plan.md (down=3 AND ydstogo>=7; yardline_100<=20; down=1 AND ydstogo=10; down=2 AND ydstogo BETWEEN 3 AND 6) are the pre-registered slate. FINDINGS.md headline insights MUST come from these. Anything outside stays exploratory. Bonferroni/BH correction not applied because the slate is locked at 4."
  - "PROJECT.md Key Decisions table append (NOT new ADR file) is the canonical pattern for promoting a phase-discovered decision."
  - "README placeholder slots use UPPERCASE_UNDERSCORE convention in angle brackets: <MOST_PREDICTABLE_DEFENSE>. Phase 4 / DOC-03 fills with actual values."

requirements-completed:
  - AUDIT-01
  - AUDIT-02
  - AUDIT-03
  - AUDIT-04
  - AUDIT-05
  - AUDIT-06
  - AUDIT-07

# Metrics
duration: 25m
completed: 2026-04-29
---

# Phase 1 Plan 02: FTN Audit Summary

**FTN pivot calibration complete: 4 anchor dimensions locked (n_blitzers, n_pass_rushers, is_play_action, n_offense_backfield); 4 pre-registered situations locked with falsifiable hypotheses; D-09 public repo name `nfl-defensive-tendencies` locked; PROJECT.md pandas pin aligned with requirements.txt (Pitfall #20 prevention). Live FTN<->pbp match rate observed 0.9998 across 137,899 rows.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3 / 3
- **Files created:** 4 (notebook + .py source + CSV + 2 docs)
- **Files modified:** 3 (PROJECT.md, SPEC.md, README.md)

## Setup Required

The plan's literal text assumes the venv from Plan 01-01 persists, but `.venv-bootcheck/` was intentionally cleaned up at the end of 01-01 per the bootstrap plan's instructions. Plan 01-02 reapplied the documented two-step install workaround at the start of Task 1, creating a fresh `.venv/` (gitignored, distinct from the legacy `venv/` Python 3.13 environment from `/gsd-init`):

1. `py -3.11 -m venv .venv` (Python 3.11.9 confirmed)
2. Step A: `pip install -r <requirements.txt minus nfl_data_py>` (11 packages)
3. Step B: `pip install "appdirs>1" "fastparquet>0.5"` (transitive deps)
4. Step C: `pip install nfl_data_py==0.3.3 --no-deps` (bypass upstream metadata mismatch)

Verified: `import nfl_data_py` exits 0; pandas 2.2.3; numpy 1.26.4. The `.venv/` is left in place after Task 1 completes for Phase 2 / 3 reuse.

## Accomplishments

### Task 1 - FTN audit notebook + null profile + schema-audit narrative (AUDIT-01..03)

- Authored `analysis/00_data_audit.ipynb` as a jupytext-paired notebook with 7 cells (imports, FTN pull, pbp pull, FTN<->pbp join, NaN profile, heatmap, 30% cutoff). Outputs cleared via `nbconvert --clear-output --inplace`.
- Executed end-to-end on the verified Python 3.11 venv. Pulled 137,899 FTN rows x 29 columns and 148,591 pbp rows. Joined with `validate='one_to_one'` on (nflverse_game_id, nflverse_play_id); observed match_rate 0.9998 (well above the 0.95 floor).
- Wrote `audit/ftn_null_profile.csv` with per-column NaN rates rounded to 3 decimals across 9 play_type values: pass (61,047), run (44,931), no_play (11,887), punt (6,765), kickoff (5,790), field_goal (3,378), extra_point (2,540), qb_kneel (1,333), qb_spike (207).
- Wrote `docs/ftn-schema-audit.md` (156 lines): names the 4 chosen anchors with NaN-rate-aware rationale; documents the 30% cutoff applied to all 8 candidates; flags `n_defense_box` as the new 29th FTN column; flags ngs `defense_coverage_type` / `defense_man_zone_type` as v2 candidate.

### Task 2 - Pre-registered analysis plan (AUDIT-04)

- Wrote `docs/analysis-plan.md` (167 lines): pre-registers all 4 D-06 situations with H1+H2 falsifiable hypotheses each (9 "Falsified if" clauses total).
- Each situation gets the verbatim SQL filter from D-06: `down = 3 AND ydstogo >= 7`, `yardline_100 <= 20`, `down = 1 AND ydstogo = 10`, `down = 2 AND ydstogo BETWEEN 3 AND 6`.
- Cross-cutting `is_play_action` modifier (D-07) documented as a stratifier on `play_type='pass'` rows where N permits, NOT a 5th slate item.
- Firewall: FINDINGS.md headline insights MUST come from this 4-situation slate. Sample-size discipline (N>=30 / 100 / 15) referenced; `min_n_filter()` named as the Phase 3 / STAT-01 enforcement gate.
- Includes a "Why these 4 and not 5" paragraph defending the locked slate against the multiple-comparisons family-wise error rate.

### Task 3 - Lock D-09 + fix pandas pin + reframe SPEC + fill README hook (AUDIT-05..07)

- **PROJECT.md:** Appended D-09 row to Key Decisions table locking `nfl-defensive-tendencies` as the public GitHub repo name. Working folder stays `nfl-coverage-tendencies` for git history continuity.
- **PROJECT.md:** Corrected stale `pandas>=2.2,<2.4` -> `pandas>=2.1,<2.3` on the Locked tech stack line. PROJECT.md, requirements.txt, SUMMARY.md Consolidated Stack, and PATTERNS.md now agree on the locked pin (Pitfall #20 doc-vs-code drift prevention).
- **PROJECT.md:** Updated Last-updated footer to "after Phase 1 D-09 lock + pandas pin alignment".
- **SPEC.md:** Rewrote all 8 Business Questions in place around the 4 anchors. Q6 reframed as cross-cutting play-action stratification (D-07). Q8 reframed to honor the 4-situation firewall (D-05). All 8 questions remain; numbering preserved. Zero analytical references to Cover 0-6 / man-zone in the rewritten Business Questions section (the strings remain only in Data Sources / Out of Scope / Risks contexts that explain what FTN does NOT have).
- **README.md:** Filled `## Hook` section with 3-paragraph post-pivot framing (7 body lines between `## Hook` and `## Findings preview`). Two placeholder slots: `<MOST_PREDICTABLE_DEFENSE>` and `<PREDICTABILITY_GAP_VS_LEAGUE_AVG>` for Phase 4 / DOC-03 to fill. Memo voice; zero exclamation-point punctuation in rendered prose. Other 8 H2 sections unchanged from BOOT-06 skeleton.

## Task Commits

1. **Task 1 (AUDIT-01..03):** `ba1f131` - feat(01-02): run FTN audit notebook + null profile + schema-audit narrative
2. **Task 2 (AUDIT-04):** `c8ddff3` - feat(01-02): pre-register 4-situation analysis plan
3. **Task 3 (AUDIT-05..07):** `64219fb` - docs(01-02): lock D-09 + fix pandas pin + reframe SPEC + fill README hook

## Anchor Selection Evidence

All 8 candidate FTN columns survived the D-02 30% NaN cutoff (the result is more permissive than the planning docs anticipated; D-04 contingency did not apply). Selection became editorial (D-01 story tiebreaker) rather than mechanical:

| Category | Column | Scope | NaN rate | Survives | Chosen anchor? |
|---|---|---|---|---|---|
| Pressure | n_blitzers | play_type='pass' | 0.000 | yes | yes (S1 + S4 lead anchor) |
| Pressure | n_pass_rushers | play_type='pass' | 0.000 | yes | yes (S2 lead anchor) |
| Play-fakery | is_play_action | play_type='pass' | 0.000 | yes | yes (D-07 cross-cutting modifier) |
| Play-fakery | is_screen_pass | play_type='pass' | 0.000 | yes | no (exploratory only) |
| Play-fakery | is_rpo | play_type='pass' | 0.000 | yes | no (exploratory only) |
| Personnel | qb_location | competitive plays | 0.001 | yes | no (stratifier only) |
| Personnel | n_offense_backfield | competitive plays | 0.009 | yes | yes (S3 + S4 anchor) |
| Personnel | starting_hash | competitive plays | 0.001 | yes | no (exploratory only) |

## D-09 PROJECT.md Diff

Appended verbatim to the Key Decisions table:

```
| D-09: Public GitHub repo name | Locked to `nfl-defensive-tendencies` after Phase 1 audit confirmed the public-FTN pivot; `coverage` framing in original repo name no longer accurate. Working folder stays `nfl-coverage-tendencies` for git history continuity. | Locked 2026-04-29 |
```

## PROJECT.md pandas pin diff (Pitfall #20)

**Before:**
> - **Locked tech stack**: `nfl-data-py==0.3.3`, `numpy<2.0` (forced by upstream `np.float_` reference), `pandas>=2.2,<2.4`, ...

**After:**
> - **Locked tech stack**: `nfl-data-py==0.3.3`, `numpy<2.0` (forced by upstream `np.float_` reference), `pandas>=2.1,<2.3`, ...

Verification: `! grep -q "pandas>=2.2,<2.4" .planning/PROJECT.md` (passes) and `grep -q "pandas>=2.1,<2.3" .planning/PROJECT.md` (passes). PROJECT.md now agrees with requirements.txt (BOOT-02), .planning/research/SUMMARY.md Consolidated Stack, and PATTERNS.md Shared Pattern 1.

## Phase 1 Closeout: All 5 ROADMAP Success Criteria Met

1. **Fresh Python 3.11 venv installs requirements.txt cleanly and imports nfl_data_py without error.** Met by Plan 01-01 / BOOT-07 (`.venv-bootcheck/`); reapplied in Plan 01-02 / Task 1 (`.venv/`).
2. **`audit/ftn_null_profile.csv` exists and shows per-column NaN rate by `play_type` for FTN columns across 2022-2024.** Met by Task 1, AUDIT-02.
3. **`docs/ftn-schema-audit.md` names the 3-4 chosen anchor defensive dimensions with a defensible, NaN-rate-aware rationale.** Met by Task 1, AUDIT-03 (4 anchors named: n_blitzers, n_pass_rushers, is_play_action, n_offense_backfield).
4. **`docs/analysis-plan.md` pre-registers 3-5 situations the FINDINGS.md memo will claim findings on.** Met by Task 2, AUDIT-04 (4 situations locked with falsifiable hypotheses).
5. **The public repo name is locked in writing and the README hook is rewritten in plain English to match the post-pivot framing.** Met by Task 3, AUDIT-05 + AUDIT-07 (D-09 row in PROJECT.md + Hook fill in README.md).

## Open Questions Handed Off to Phase 2

- **FTN<->pbp match rate observed 0.9998 in this audit (137,899/137,899 rows).** Phase 2 ETL-04 should keep the > 0.95 floor unchanged; the observed value provides ~5 percentage points of headroom against future nflverse drift. If ETL-04 sees a value below 0.95, the audit notebook is the diagnostic baseline.
- **`n_defense_box` is a 29th FTN column not documented in PITFALLS.md #2.** Phase 2 / ETL-03 (column whitelist) should decide whether to ingest it; current recommendation is yes since it is NaN-clean across all play types and may be a useful exploratory column.
- **`defense_coverage_type` and `defense_man_zone_type` (NGS-derived columns now living on pbp) are a v2 candidate.** Phase 2 / ETL-03 may exclude them from the v1 column whitelist to keep the v1 SPEC framing coherent. Documented in `docs/ftn-schema-audit.md`.
- **`competitive_plays` view (Phase 2 / SCHEMA-03) must encode the same play_type and wp filtering this analysis presumes.** The audit notebook used the raw FTN<->pbp join; production analytical queries in Phase 3 will read from `competitive_plays` instead.

## Deviations from Plan

### Setup-procedure deviation (not Rule 1-3)

**Re-applied two-step install workaround.** The plan's literal text assumes the Plan 01-01 venv persists, but `.venv-bootcheck/` was intentionally cleaned up at the end of 01-01 (per the bootstrap plan's own instructions). Plan 01-02 created a fresh `.venv/` at the repo root (gitignored, distinct from the legacy Python 3.13 `venv/`) using the documented two-step install pattern from 01-01-SUMMARY.md. Pin block in `requirements.txt` was not modified. The locked stack is unchanged: nfl_data_py 0.3.3, pandas 2.2.3 (in the 2.1/2.2 band), numpy 1.26.4.

### Auto-fixed Issues (Rule 1-3)

None - no bugs surfaced during execution. The 8-candidate-survives-the-30%-cutoff outcome was more permissive than the planning docs anticipated, but this is a finding (D-04 contingency does not apply, anchor selection becomes editorial) rather than a deviation.

### Documented findings worth flagging

**1. Live FTN frame has 29 columns, not 28 (PITFALLS.md #2 documented 28).**
- **Found during:** Task 1 sub-step A.
- **Detail:** `nfl.import_ftn_data([2022, 2023, 2024])` returned 29 columns. The addition is `n_defense_box`, which is NaN-clean across all play types.
- **Impact:** None on v1 plan. Documented in `docs/ftn-schema-audit.md`. Phase 2 / ETL-03 column whitelist decision is downstream.

**2. pbp now exposes ngs-derived coverage columns at populated rates.**
- **Found during:** Task 1 sub-step A (post-join NaN profile review).
- **Detail:** `nfl.import_pbp_data()` returns `defense_coverage_type` (0.025 NaN on pass) and `defense_man_zone_type` (0.023 NaN on pass) - well below the 30% cutoff. These come from NFL Next Gen Stats merged into pbp since the original research pass.
- **Impact:** None on v1 plan because the pivot decision (D-09) is locked, the analysis plan is pre-registered around FTN-confirmed columns, and re-opening coverage-shell framing would contradict the locked SPEC. Flagged as v2 candidate in `docs/ftn-schema-audit.md` "Subsequent finding worth flagging for v2" section.

**Total deviations:** 0 Rule-1/2/3 fixes. 1 setup-procedure reapplication. 2 documented findings (no plan changes needed).

## Verification Evidence (AUDIT-01..07)

| Req | Evidence |
|-----|----------|
| AUDIT-01 | `analysis/00_data_audit.ipynb` runs end-to-end on Python 3.11.9 venv; contains literal strings `import nfl_data_py`, `import_ftn_data`, `nflverse_game_id`, `nflverse_play_id`, `validate='one_to_one'`, `match_rate > 0.95`, `ftn_null_profile.csv`. Outputs cleared (0 `"output_type"` keys). |
| AUDIT-02 | `audit/ftn_null_profile.csv` exists with header row referencing `play_type` (column names are play_type values: extra_point, field_goal, kickoff, no_play, pass, punt, qb_kneel, qb_spike, run). 53 rows x 9 cols of NaN rates in [0.000, 1.000]. |
| AUDIT-03 | `docs/ftn-schema-audit.md` is 156 lines (>= 60); references `28` (FTN column inventory) and `30%` (cutoff); references all 8 candidate columns; 0 exclamation-point punctuation; no analytical Cover-shell or man-zone claims (the strings appear only in prose explaining what FTN does NOT have). |
| AUDIT-04 | `docs/analysis-plan.md` is 167 lines (>= 40); contains all 4 SQL filters verbatim; 9 "Falsified if" clauses (>= 4); references `is_play_action`, `competitive_plays`, all 3 N-tier thresholds (N>=30/100/15); 0 exclamation points; 0 Cover/man-zone false flags. |
| AUDIT-05 | `.planning/PROJECT.md` Key Decisions table contains `D-09: Public GitHub repo name` with `nfl-defensive-tendencies` and `Locked 2026-04-29`. Stale `pandas>=2.2,<2.4` removed; locked `pandas>=2.1,<2.3` confirmed (Pitfall #20 prevention applied). |
| AUDIT-06 | `SPEC.md` retains heading `## Business Questions to Answer`; section has 8 numbered questions (1-8); references the 4 anchor columns explicitly; 0 Cover/man-zone false flags in the Business Questions section. Other SPEC sections unchanged. |
| AUDIT-07 | `README.md` Hook section has 7 body lines between `## Hook` and `## Findings preview` (>= 4); 2 placeholder slots in angle-bracket form; 0 exclamation-point punctuation in rendered prose; HTML comment delimiters preserved per voice rule exception. Other 8 H2 sections unchanged from BOOT-06 skeleton. |

## Self-Check: PASSED

- All 4 created files exist (`analysis/00_data_audit.ipynb`, `audit/ftn_null_profile.csv`, `docs/ftn-schema-audit.md`, `docs/analysis-plan.md`)
- All 3 modified files contain the required edits (`.planning/PROJECT.md` D-09 row + corrected pandas pin; `SPEC.md` rewritten 8 Business Questions; `README.md` filled Hook with placeholder slots)
- All 3 task commits visible in git log (`ba1f131`, `c8ddff3`, `64219fb`)
- `.venv/` exists at repo root (not staged; gitignored); legacy `venv/` (Python 3.13) untouched
- All 22 plan-level verify-block checks pass
- Working tree clean before SUMMARY commit

## Next Phase Readiness

- **Plan 02-01 (Schema) and Plan 02-02 (ETL) are unblocked.** Both can read the anchor dimension list from `docs/ftn-schema-audit.md` and the column whitelist implications.
- **Phase 2 / ETL-04** inherits the `validate='one_to_one'` + `match_rate > 0.95` join pattern from this audit; the observed 0.9998 match rate is the baseline reference.
- **Phase 2 / SCHEMA-03** (`competitive_plays` view) must encode `play_type IN ('pass','run')` AND `wp BETWEEN 0.05 AND 0.95` filtering; this is presumed by the analytical claims in `docs/analysis-plan.md`.
- **Phase 3** reads `docs/analysis-plan.md` as the locked pre-registration; FINDINGS.md headline insights are firewalled to the 4 situations.
- **Phase 4** reads `README.md` Hook placeholders (`<MOST_PREDICTABLE_DEFENSE>`, `<PREDICTABILITY_GAP_VS_LEAGUE_AVG>`) and DOC-03 fills them with actual values.

---
*Phase: 01-foundation-ftn-pivot-calibration*
*Completed: 2026-04-29*
