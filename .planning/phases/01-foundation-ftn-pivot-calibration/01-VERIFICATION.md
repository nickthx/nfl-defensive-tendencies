---
status: passed
phase: 01-foundation-ftn-pivot-calibration
date: 2026-04-29
must_haves_total: 14
must_haves_verified: 14
gaps: 0
prior_warnings_resolved:
  W1_spec_pandas_pin: yes
  W2_ruff_clean: yes
re_verification:
  previous_status: human_needed
  previous_score: 14/14
  gaps_closed:
    - "W1: SPEC.md pandas pin alignment to >=2.1,<2.3 (Pitfall #20 prevention)"
    - "W2: ruff check . exits clean (4 prior errors auto-fixed)"
  gaps_remaining: []
  regressions: []
  notes:
    - "Scope expanded from 3 seasons (2022-2024) to 4 seasons (2022-2025) under D-10. Audit notebook re-run, CSV regenerated, schema-audit narrative refreshed with new totals (185,215 FTN rows / 197,362 pbp / 0.9999 match rate / 80,782 pass / 59,824 run / 140,606 competitive)."
    - "Voice cleanup applied to README Hook + docs/ftn-schema-audit.md per user-supervised cleanup pass. Both files now contain zero em dashes, zero internal-jargon codes (D-XX / Pitfall #N / STAT-XX / S1-S4), zero exclamation-point punctuation in rendered prose."
    - "SHIP-08 filed in REQUIREMENTS.md (placeholder-guard requirement); Phase 4 count 21 / total 56."
    - "PROJECT.md FTN column count corrected from 28 to 29 (n_defense_box surfaced during audit)."
minor_drift_observations:
  - file: "SPEC.md"
    line: 4
    finding: "Objective opening still references '2022–2024 seasons' (en-dash form). Lines 27 and 94 use 2022-2025 correctly. Not a Phase 1 acceptance failure (AUDIT-06 requires the Business Questions section to be reframed, which it is — Q8 references 2022-2025), but worth noting for the Phase 4 docs polish pass."
    severity: info
    blocks_ship: false
    suggested_phase_to_fix: "Phase 4 (DOC-03 README polish bundles SPEC.md normalization)"
  - file: ".planning/ROADMAP.md"
    line: "7, 104, 146-147"
    finding: "ROADMAP.md still reports Phase 4 as 20 requirements (SHIP-01..07) totaling 55, but REQUIREMENTS.md was correctly updated to Phase 4 = 21 (SHIP-01..08), total = 56. This is doc-vs-doc drift relative to SHIP-08 having been filed. Not a Phase 1 must-have (SHIP-08 itself is filed correctly in REQUIREMENTS.md per the verification checklist), but the ROADMAP coverage table will fail Pitfall #20 on a future audit if not synced."
    severity: info
    blocks_ship: false
    suggested_phase_to_fix: "Phase 4 ship-readiness check, or a post-Phase-1 housekeeping commit"
---

# Phase 1: Foundation & FTN Pivot Calibration — Verification Report (Pass 2)

**Phase Goal (from ROADMAP.md):** Bootstrap a reproducible Python 3.11 / nfl_data_py portfolio repo skeleton AND calibrate the FTN public-data pivot — measure NaN rates, lock 3-4 anchor defensive dimensions, pre-register 4 analytical situations with falsifiable hypotheses, lock the public repo name (D-09), align all docs on the locked stack pins, and rewrite SPEC + README in place.

**Verified:** 2026-04-29
**Status:** passed (14/14 must-haves verified)
**Re-verification:** Yes — second pass after voice cleanup commit `182ff15` and D-10 scope expansion to 2022-2025. The first verification (status `human_needed`, 14/14, two non-blocking warnings) is now obsolete.

## 1. Goal Achievement Summary

Phase 1 delivers its ROADMAP goal in full. The locked Python 3.11 stack installs cleanly into a fresh venv (`numpy 1.26.4`, `pandas 2.2.3`, `nfl_data_py` imports OK; `ruff check .` exits 0 with "All checks passed"). The FTN audit ran end-to-end against 4 seasons (2022-2025), produced the per-column NaN profile in `audit/ftn_null_profile.csv` with a 0.9999 FTN↔pbp match rate, and surfaced an unexpected 29th column (`n_defense_box`). The 4 anchor defensive dimensions (`n_blitzers`, `n_pass_rushers`, `is_play_action`, `n_offense_backfield`) are documented with NaN-rate-aware rationale in `docs/ftn-schema-audit.md` (143 lines, post-cleanup, post-scope-expansion). The 4 pre-registered situations (3rd-and-long, red zone, 1st-and-10, 2nd-and-medium) are locked in `docs/analysis-plan.md` with 9 explicit "falsified if" disconfirmation clauses. The public repo name `nfl-defensive-tendencies` is locked under D-09. SPEC.md's 8 business questions are reframed in place around the chosen anchors with no Cover-shell jargon. README.md Hook contains a 3-sentence post-pivot framing with three uppercase placeholder slots (`<MOST_PREDICTABLE_DEFENSE_2025>`, `<SCORE>`, `<DELTA>`) for Phase 4 to fill. Both prior verification warnings (W1: SPEC.md pandas pin; W2: ruff cleanliness) are resolved. Two minor doc-vs-doc drift observations (SPEC.md Objective season span, ROADMAP.md SHIP-08 count) are recorded as info-level — neither is a Phase 1 acceptance failure and both have a clear Phase 4 home.

## 2. Requirement Verification Table

| ID | Description | Evidence | Status |
|----|-------------|----------|--------|
| BOOT-01 | Skeleton repo with directory tree per ARCHITECTURE.md | All 8 .gitkeep markers present (`analysis/.gitkeep`, `audit/.gitkeep`, `docs/.gitkeep`, `etl/.gitkeep`, `findings/.gitkeep`, `findings/images/.gitkeep`, `queries/.gitkeep`, `schema/.gitkeep`); `data/`, `data/raw/` exist; no `tests/` directory | ✓ verified |
| BOOT-02 | requirements.txt pins Consolidated Stack (12 packages) | `requirements.txt:3` `nfl_data_py==0.3.3`; `:6` `pandas>=2.1,<2.3`; `:7` `numpy>=1.26,<2.0`; `:8` `pyarrow>=15,<22`; `:11` `scipy>=1.13,<1.18`; `:14` `matplotlib>=3.8,<3.11`; `:15` `seaborn==0.13.2`; `:18-21` jupyterlab/ipykernel/jupytext/nbconvert; `:24` `ruff>=0.6,<1.0` | ✓ verified |
| BOOT-03 | .gitignore excludes data/raw/, *.db, .env*, __pycache__/, .ipynb_checkpoints/, scratch, venv/ | `.gitignore:23` `data/raw/`; `:26` `*.db`; `:29` `.env*`; `:4` `__pycache__/`; `:9` `.ipynb_checkpoints/`; `:34` `scratch/`; `:2-3` `venv/`, `.venv/` — no bare `.env` line | ✓ verified |
| BOOT-04 | pyproject.toml is [tool.ruff] config only | `pyproject.toml:1` `[tool.ruff]`; `:2` `line-length = 100`; `:3` `target-version = "py311"`; `:5` `[tool.ruff.lint]`; `:6` `select = ["E", "F", "I", "B", "UP"]`; `:7` `ignore = ["E501"]`; no `[project]` or `[build-system]` sections | ✓ verified |
| BOOT-05 | .python-version pinned to 3.11 | `.python-version:1` `3.11` (single line, trimmed) | ✓ verified |
| BOOT-06 | README skeleton has 9 voice-compliant H2 headers | All 9 H2s present: Hook, Findings preview, Architecture, Setup, Glossary, Methodology, Limitations, Attribution, Known Issues. Zero `!` in rendered prose (`sed 's/<!--[^>]*-->//g' README.md \| grep -c '!'` = 0). No "Welcome to". No emoji headers. No `img.shields.io`. | ✓ verified |
| BOOT-07 | Fresh-venv install verified | `01-01-SUMMARY.md` documents Python 3.11.9 venv install with two-step nfl_data_py workaround. Live re-test: `.venv/Scripts/python.exe -c "import nfl_data_py"` exits 0; numpy 1.26.4 (<2 holds); pandas 2.2.3 (within 2.1-2.3 band); `ruff check .` returns "All checks passed" | ✓ verified |
| AUDIT-01 | analysis/00_data_audit.ipynb runs FTN pull + pbp join + NaN profile | All 7 required strings present: `import nfl_data_py`, `import_ftn_data`, `nflverse_game_id`, `nflverse_play_id`, `validate='one_to_one'`, `match_rate > 0.95`, `ftn_null_profile.csv`. `SEASONS = [2022, 2023, 2024, 2025]` (4-season scope). Assertion `> 130_000`. Outputs cleared (0 `output_type` keys, 0 execution_count). | ✓ verified |
| AUDIT-02 | audit/ftn_null_profile.csv has NaN rates per column × play_type | File exists, 60 rows, header row references play_type values: `,extra_point,field_goal,kickoff,no_play,pass,punt,qb_kneel,qb_spike,run,`. Data values numeric in [0.0, 1.0]. Regenerated 2026-04-29 21:35 against the 4-season join (185,215 FTN rows). | ✓ verified |
| AUDIT-03 | docs/ftn-schema-audit.md names 3-4 anchors with NaN-rate rationale | 143 lines (substantive, well above the 60-line floor). Mentions `29` (FTN col count, corrected from 28) and `30%` cutoff. References all 8 candidate columns. 4 anchors named: n_blitzers, n_pass_rushers, is_play_action, n_offense_backfield. ZERO `!`, ZERO em dashes, ZERO internal-jargon codes (D-XX, Pitfall #N, STAT-XX, S1-S4). 4-season totals quoted: 185,215 / 197,362 / 0.9999 / 80,782 / 59,824 / 140,606. | ✓ verified |
| AUDIT-04 | docs/analysis-plan.md pre-registers 4 situations with falsifiable hypotheses | 167 lines. All 4 D-06 SQL filter predicates verbatim. 9 occurrences of "falsified if" (>4 floor). References `is_play_action` (D-07 cross-cutting modifier) and `competitive_plays`. N≥30 / N≥100 / N≥15 tiers all present. Zero `!`. All season refs are 2022-2025 (no stale 2022-2024 remnants). | ✓ verified |
| AUDIT-05 | PROJECT.md has D-09 (repo name) + pandas pin aligned | `.planning/PROJECT.md:96` D-09 row present locking `nfl-defensive-tendencies`, `Locked 2026-04-29`. `:97` D-10 row also present (scope expansion to 2022-2025). `:70` pandas pin reads `pandas>=2.1,<2.3` (stale `>=2.2,<2.4` removed; Pitfall #20 prevention applied). FTN col count says 29 (line 54, with `n_defense_box` rationale). | ✓ verified |
| AUDIT-06 | SPEC.md 8 business questions reframed around chosen anchors | `SPEC.md:84` `## Business Questions to Answer` retained. 8 numbered questions present (1.–8., the `grep -cE "^[0-9]+\. "` returns 16 because of double-counted SPEC numbering — manual inspection confirms exactly 8 BQs). Anchor preamble at line 85 names all 4 chosen anchors. No `Cover [0-6]` / `man-zone` references in the BQ section (verified via awk between Business Questions and Technical Requirements). Zero `!` in BQ section. | ✓ verified |
| AUDIT-07 | README.md Hook has post-pivot framing + Phase 4 placeholder slots | `README.md:3-7` Hook body is 4 lines of substantive content. Three placeholder slots present in uppercase angle-bracket form: `<MOST_PREDICTABLE_DEFENSE_2025>`, `<SCORE>`, `<DELTA>`. References "four seasons (2022-2025, through Super Bowl LX)". Zero `!` in rendered prose. No `Cover 3` / `Cover 0` / `man-zone` jargon (only an HTML comment in the Limitations section mentions "no Cover 0-6 labels", which is a future-Phase-4 placeholder note). Other 8 H2 sections unchanged from BOOT-06 skeleton. | ✓ verified |

## 3. Voice & Public-Repo Discipline

The voice cleanup applied in commit `182ff15` is fully effective on the in-scope files:

| Check | Target file | Result |
|-------|-------------|--------|
| Em-dash count | `docs/ftn-schema-audit.md` | 0 (was material before cleanup) |
| Em-dash count | `docs/analysis-plan.md` | 0 |
| Em-dash count | `README.md` | 0 |
| Internal codes (D-XX, Pitfall #N, STAT-XX, S1-S4) | `docs/ftn-schema-audit.md` | 0 (cleanup target — clean) |
| Internal codes | `README.md` (rendered prose) | 0 |
| Exclamation-point punctuation | `docs/ftn-schema-audit.md` | 0 |
| Exclamation-point punctuation | `docs/analysis-plan.md` | 0 |
| Exclamation-point punctuation | `README.md` (rendered prose, HTML comments stripped) | 0 |
| `Cover 0-6` / `man-zone` analytical references | `SPEC.md` Business Questions, `docs/ftn-schema-audit.md`, `docs/analysis-plan.md`, `README.md` | 0 (only the existing "Out of Scope" / Limitations explanatory mentions remain — these explain what we do NOT have, never as analytical anchors) |
| Schema-audit length | `docs/ftn-schema-audit.md` | 143 lines (after cleanup-then-scope-expansion-rebuild; comfortable above the 60-line floor; cleanup pass took it from 156 → 138 → 143 as scope-expansion edits added the 4-season rebuild numbers) |

`docs/analysis-plan.md` and `SPEC.md` retain D-XX / S1-S4 references intentionally — these are pre-registration documents whose decision-ID and situation-ID references are part of the analytical contract, not boilerplate jargon. They are NOT in the cleanup scope per the user's commit message.

Public-repo discipline:
- `git status` returns clean working tree
- `git ls-files | grep -E "\.db$|data/raw/"` returns empty (no .db or raw/ contents tracked)
- `.venv-bootcheck` does not exist
- No `tests/` directory
- All 8 directories (data, data/raw, schema, etl, queries, analysis, findings, findings/images, audit, docs) exist with .gitkeep markers as expected

## 4. Prior Warnings Disposition

| Warning | Origin | Resolution Evidence | Status |
|---------|--------|---------------------|--------|
| W1: SPEC.md pandas pin reads `pandas>=2.2,<2.4` (drift from locked `>=2.1,<2.3`) | First verification pass | `SPEC.md:31` now reads `\`pandas>=2.1,<2.3\``. `grep "pandas>=2.2,<2.4" SPEC.md` returns nothing. PROJECT.md / requirements.txt / SUMMARY.md / SPEC.md all aligned on the same single-source-of-truth pin. Pitfall #20 prevention complete. | ✓ resolved |
| W2: `ruff check .` reports 4 errors (unused/duplicate imports) in 00_data_audit.{ipynb,py} | First verification pass | Re-run via `.venv/Scripts/python.exe -m ruff check .` returns "All checks passed!" with exit code 0. The 4 prior errors were auto-fixed via `ruff --fix`. | ✓ resolved |

Both prior warnings are closed. No regressions detected.

## 5. Pitfall Mitigations Confirmed

| Pitfall | What it prevents | Evidence in current state |
|---------|-----------------|---------------------------|
| #14 | Committing the .db file (200-400 MB > 100 MiB GitHub limit) | `.gitignore:26` `*.db` (hard rule, no deferral comment); `git ls-files \| grep "\.db$"` returns empty |
| #16 | numpy 2.x being resolved despite the np.float_ landmine in nfl_data_py 0.3.x | `.venv/Scripts/python.exe -c "import numpy; print(numpy.__version__)"` returns `1.26.4`. Pin `numpy>=1.26,<2.0` in requirements.txt holds. |
| #18 | .env / .env.local / .env.production credential leak | `.gitignore:29` `.env*` glob (replaced bare `.env`); covers all `.env.*` variants |
| #20 | Doc-vs-code pandas-pin drift | All four artifacts agree on `pandas>=2.1,<2.3`: `requirements.txt:6`, `.planning/PROJECT.md:70`, `.planning/research/SUMMARY.md` (Consolidated Stack), `SPEC.md:31`. Two minor outstanding drifts (SPEC.md line 4 season span; ROADMAP.md SHIP-08 count) recorded in `minor_drift_observations` but NOT pin-related. |

## 6. Scope Expansion Validation (D-10)

The 4-season expansion (2022-2024 → 2022-2025) executed end-to-end:

| Check | Evidence |
|-------|----------|
| Audit notebook SEASONS literal | `analysis/00_data_audit.py:40` `SEASONS = [2022, 2023, 2024, 2025]`; `analysis/00_data_audit.ipynb` contains `"SEASONS = [2022, 2023, 2024, 2025]\n"` |
| Row-count assertion threshold | `analysis/00_data_audit.py:55` `assert len(ftn) > 130_000, f"...expected >130k for 4 seasons"` |
| FTN total rows (audit) | 185,215 (quoted in schema-audit.md:13) |
| pbp total rows (audit) | 197,362 (quoted in schema-audit.md:14) |
| Match rate | 0.9999 (above 0.95 floor; quoted in schema-audit.md:13) |
| Pass / run / competitive splits | 80,782 pass / 59,824 run / 140,606 competitive (schema-audit.md:137-138) |
| Heatmap title in notebook | `analysis/00_data_audit.py:117` `"FTN per-column NaN rate by play_type, 2022-2025"` |
| README Hook season span | `README.md:5` "four seasons (2022-2025, through Super Bowl LX)" |
| docs/analysis-plan.md hypothesis span | All H1/H2 references say `2022-2025` (6 occurrences); zero `2022-2024` |
| docs/ftn-schema-audit.md narrative spans | All 4-season; zero `2022-2024` |
| PROJECT.md D-10 row | `.planning/PROJECT.md:97` lock-recorded with full rationale and the data-quality-check evidence |
| Historical 3-season records | `01-01-SUMMARY.md`, `01-02-SUMMARY.md`, `01-CONTEXT.md`, `01-DISCUSSION-LOG.md` retain their original 3-season references (intentional preservation per cleanup commit message) |
| CSV regeneration | `audit/ftn_null_profile.csv` mtime `Apr 29 21:35` (post-commit-`182ff15` regeneration) |

D-10 scope expansion is verified end-to-end. The audit notebook re-ran against the 4-season frame and the CSV reflects the new data shape.

## 7. Phase 1 → Phase 2 Handoff Readiness

| Handoff requirement | Status |
|---------------------|--------|
| 4 anchor dimensions documented with rationale | ✓ `docs/ftn-schema-audit.md` §"Anchor selection" |
| 4 pre-registered situations locked with SQL filters | ✓ `docs/analysis-plan.md` §1-4 (3rd-and-long, red zone, 1st-and-10, 2nd-and-medium) |
| Cross-cutting modifier (`is_play_action`) treatment locked | ✓ `docs/analysis-plan.md` §"Cross-cutting Modifier" |
| Sample-size discipline (N≥30 / 100 / 15) referenced | ✓ Both `analysis-plan.md` and `ftn-schema-audit.md`; `min_n_filter()` Phase 3 deliverable named |
| `.venv/` reusable | ✓ `.venv/Scripts/python.exe` imports `nfl_data_py` cleanly; numpy 1.26.4; pandas 2.2.3; ruff clean |
| Public repo name (D-09) and FTN reality (D-10) documented in PROJECT.md | ✓ Lines 96-97 |
| ETL-04 join-keys pattern proven | ✓ Audit notebook used `validate='one_to_one'` on `(nflverse_game_id, nflverse_play_id)`, post-join match-rate 0.9999. Phase 2 ETL-04 inherits this exact pattern. |
| Match rate observed for ETL-04 threshold reference | 0.9999 (well above the 0.95 ETL-04 acceptance) |

Phase 2 can begin without remediation work.

## 8. Gaps

No blocking gaps. Two info-level doc-vs-doc drift observations are recorded in `minor_drift_observations` (frontmatter):

1. **SPEC.md line 4 — Objective opening still says "2022–2024 seasons"** while line 27 (Seasons in scope) and line 94 (Q8) correctly say 2022-2025. This is NOT an AUDIT-06 acceptance failure (AUDIT-06 only governs the Business Questions section, which is correctly reframed). Suggested fix during Phase 4 DOC-03 (README polish bundles SPEC.md normalization). Severity: info. Does not block ship.

2. **ROADMAP.md still reports Phase 4 = 20 (SHIP-01..07), total = 55** while REQUIREMENTS.md was correctly updated to Phase 4 = 21 (SHIP-01..08), total = 56 when SHIP-08 was filed. SHIP-08 itself is correctly defined in REQUIREMENTS.md per the verification checklist. The drift is between two planning docs, not between a planning doc and code. Suggested fix during Phase 4 ship-readiness check or a post-Phase-1 housekeeping commit. Severity: info. Does not block Phase 2.

Neither observation is a Phase 1 BOOT-* / AUDIT-* acceptance failure. Both are surfaced in case the user wants to fold them into a quick housekeeping commit before Phase 2 begins; neither requires a closure plan.

## 9. Human Verification Items

None. The README Hook prose and `docs/ftn-schema-audit.md` voice were eyeballed and approved by the user during the cleanup pass that produced commit `182ff15`. The voice rules (no exclamation-point punctuation, no em dashes, no internal jargon codes, no Cover-shell jargon as analytical claims, no emoji headers, no "Welcome to") are all programmatically verified above. No new prose surfaces require human review in this verification pass.

---

_Verified: 2026-04-29_
_Verifier: Claude (gsd-verifier, second pass post-cleanup)_
_Prior verification (now obsolete): pre-cleanup 3-season state, status `human_needed`, 14/14 with W1+W2 warnings_
