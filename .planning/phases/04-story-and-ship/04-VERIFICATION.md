---
status: passed
phase: 04-story-and-ship
verified: 2026-05-01T00:00:00Z
must_haves_score: 16/16
req_ids_score: 21/21
roadmap_criteria_score: 6/6
re_verification: true
re_verification_note: "Initial pass scored gaps_found (14/16 must-haves) — see preserved 'gaps' block below for the original finding and audit trail. Both gaps closed in commit 7c3a0f1: SPEC.md L87 corrected to 'n_blitzers > 0' with D-14 calibration note; analysis/02_predictability_modeling.ipynb re-synced from the corrected .py via jupytext --sync + nbconvert --clear-output (cells 0 + 11 markdown text now reads '> 0'). Final D-49 grep extended to include SPEC.md returns zero matches across all 11 file patterns: PROJECT.md, README.md, FINDINGS.md, data/README.md, docs/*.md, analysis/*.py, queries/*.sql, etl/*.py, schema/*.sql, scripts/*.py, SPEC.md."
gaps:
  - truth: "Cross-doc reconciliation sweep complete (D-48): all user-facing surfaces + code carry n_blitzers > 0 / n_blitzers >= 1; zero stale n_blitzers > 4 matches across user-facing surfaces"
    status: resolved
    reason: "D-49 strict allow-list grep (per 04-02-PLAN) is clean — README.md, findings/FINDINGS.md, data/README.md, .planning/PROJECT.md, docs/*.md, analysis/*.py, queries/*.sql, etl/*.py, schema/*.sql, scripts/*.py all return zero. However, two user-facing surfaces tracked in git but NOT enumerated in the D-49 allow-list still carry the stale predicate."
    artifacts:
      - path: "SPEC.md"
        issue: "L87 — operational definition still reads `league-wide blitz rate (\\`n_blitzers > 4\\`)` in the Distribution baseline business question. SPEC.md is git-tracked at repo root and rendered on the public GitHub repo browse view; recruiters can land here from the Code tab."
      - path: "analysis/02_predictability_modeling.ipynb"
        issue: "Cell 0 (markdown: methodology lock D-02) at .ipynb-line 25 and cell 11 (markdown: STAT-06 chi-square headline DEVIATION note) at .ipynb-line 359 both still read `n_blitzers > 4`. The paired .py source IS corrected (analysis/02_predictability_modeling.py L34 reads `n_blitzers > 0`); the .ipynb has not been re-synced from the corrected .py. The .ipynb is the surface GitHub renders for a notebook click-through."
    missing:
      - "SPEC.md L87: change `n_blitzers > 4` to `n_blitzers > 0` (or rephrase to `extra rushers above the 4-man front`); this is the same prose-reconciliation pattern the 5-site sweep used"
      - "analysis/02_predictability_modeling.ipynb: run `jupytext --sync analysis/02_predictability_modeling.py` to regenerate the .ipynb from the corrected .py (or `jupyter nbconvert --clear-output --inplace` after re-execution); confirm `grep -F 'n_blitzers > 4' analysis/02_predictability_modeling.ipynb` returns zero"
      - "Optional: add SPEC.md and `analysis/*.ipynb` to the D-49 allow-list in any future reconciliation runbook so this class of drift is caught the next time"
human_verification:
  - test: "Public repo surface inspection (incognito non-author)"
    expected: "All 7 desktop checks PASS + 3/3 mobile DOM/CSS checks PASS — already attested by orchestrator Task 6 incognito report on commit a119289 (per 04-03-SUMMARY.md). Verifier accepts this attestation as the system-of-record because the GitHub MCP token in this session has no admin scope and cannot read public OR private repos via API. No re-verification needed unless any of the four GitHub-side items below change after this report is filed."
    why_human: "Orchestrator already executed in Task 6; verifier cannot independently re-confirm GitHub-side state without admin token scope. Listed here for traceability only — NOT a blocker."
  - test: "SHIP-04 social preview slot still serves custom 1280x640 og:image"
    expected: "https://github.com/nickthx/nfl-defensive-tendencies meta og:image points to repository-images.githubusercontent.com (verified by Task 6); image is the RGB-only top-12 leaderboard variant, not the GitHub default repo cover."
    why_human: "Verifier can't fetch the og:image without browser/curl; orchestrator already attested. Listed for traceability."
  - test: "SHIP-05 profile pin still visible on https://github.com/nickthx"
    expected: "Repo card visible in pinned section of nickthx profile (verified by Task 6 incognito check #5)."
    why_human: "Same as above — admin-scope-free verifier cannot independently confirm; relies on orchestrator attestation."
  - test: "SHIP-03 visibility flag still Public + branch-protection ruleset still Active"
    expected: "Header reads Public; Settings -> Rules shows main-protection Active with 3 rules (restrict deletions, block force pushes, require lint-and-import-smoke). Validated end-to-end by the rejection of direct push 720ab51 (per 04-03-SUMMARY.md)."
    why_human: "Repo-state read requires admin scope; orchestrator attestation accepted."
---

# Phase 4: Story & Ship (Viz + Docs + Public GitHub) — Verification Report

**Phase Goal (ROADMAP §Phase 4):** The recruiter signal is delivered — a hand-written README with hero chart above the fold, a memo-style FINDINGS.md, and a public GitHub repo configured via the GitHub MCP (description, topics, social preview, pinned).

**Verified:** 2026-05-01
**Status:** gaps_found
**Re-verification:** No — initial verification

---

## Phase Goal Verification (ROADMAP Success Criteria 1–6)

### Criterion 1: Public repo URL in non-author browser shows hero chart above fold + 3–4 stat-first bullet findings + Mermaid diagram + 5-command setup + 6-term glossary, all hand-written (DOC-03..06, VIZ-02)

**Status:** PASS (orchestrator-attested for GitHub-rendered surface; local-codebase preconditions all verified)

Evidence (local codebase, verifier-confirmed):
- Hero PNG embedded above the fold: `README.md:9` — `![Predictability leaderboard, 32 NFL defenses, 2022-2025](findings/images/01_predictability_ranking.png)`
- 4 stat-first bullet findings present at `README.md:13-16` (PHI/SF/IND vs MIA/TB/MIN with N=128, the S1 PA chi-square with N(PA=1)=109, RZ pressure differential with N=7,553/50,625, DET 52.3%)
- Mermaid block at `README.md:20-29` — `flowchart LR` with 7 nodes from `nfl_data_py` through `findings/images/*.png` to README+FINDINGS
- 5-command setup block at `README.md:35-41` (clone, cd, venv+activate, pip install, etl.run)
- 6-term glossary at `README.md:49-54`: Down, Distance, EPA, Blitz (`n_blitzers > 0`), RPO, Predictability index — all present
- No emoji section headers; no AI-template tone (verified by reading lines 1-75 end-to-end)
- `! grep -qE '<[A-Z_]{4,}>' README.md` exits 0 (zero placeholder matches)

Evidence (GitHub-rendered surface, orchestrator-attested per 04-03-SUMMARY.md Task 6):
- 7/7 desktop incognito checks PASS on commit a119289
- 3/3 mobile DOM/CSS checks PASS

### Criterion 2: `findings/FINDINGS.md` renders as a memo (TL;DR → 5–7 named insights with N inline → methodology appendix → limitations → FTN+nflverse attribution); tiered N≥30/100/15-flag discipline visible (DOC-01, DOC-02, DOC-07)

**Status:** PASS

Evidence:
- File exists at `findings/FINDINGS.md` (178 lines)
- TL;DR at `findings/FINDINGS.md:3-12` — 4 highlight bullets, names all 4 pre-registered situations, previews D-15 divergence, top-3+bottom-3+league-avg
- 6 numbered insights in locked sequence at `findings/FINDINGS.md:16,24,32,38,44,50` — leaderboard headline → D-15 divergence → S1 pre-registered chi-square → S3 exploratory chi-square → red-zone pressure differential → DET pressure beat
- 3 thematic methodology blocks at `findings/FINDINGS.md:58,66,72` — Block 1 (Metric Choice and Calibration), Block 2 (Sensitivity and Robustness), Block 3 (Sample-Size Discipline and the Pre-registered Firewall)
- 4 appendix tables at `findings/FINDINGS.md:82,101,115,130` — T1 (per-team-per-situation cells), T2 (KL leaderboard with rank-delta), T3 (STAT-08 sensitivity rank-delta), T4 (S1+S3 contingency tables paired)
- 5-item Limitations at `findings/FINDINGS.md:160,162,164,166,168` — L1, L2, L3, L4, L6 (L5 intentionally skipped per 04-CONTEXT D-18 — `nfl_data_py` archival belongs in README Known Issues, not FINDINGS analytical limitations)
- L3 prose constraint (D-19) verified at `findings/FINDINGS.md:164` — explicit "play-action requires a credible run threat to freeze linebackers... 3rd-and-7+, the run is no longer a credible play call" sentence
- L4 prose constraint (D-20) verified at `findings/FINDINGS.md:166` — explicit "FTN does not publish inter-rater reliability statistics for these fields, so the impact of charter subjectivity on the chi-square findings cannot be bounded quantitatively"
- FTN + nflverse + CC-BY-SA attribution at `findings/FINDINGS.md:172-178`
- DOC-02 (N inline): 25 N-citations counted in the file via `grep -cE 'N[ =]|N\)'`; spot-checks confirm every insight (#1: N=128; #3: N(PA=1)=109; #5: N=7,553 / N=50,625; #6: query reference) carries N inline

### Criterion 3: Fresh clone runs `pip install -r requirements.txt` + `python -m etl.run` + Restart-and-Run-All on every notebook with no errors; all PNGs regenerate; notebook outputs cleared on disk (VIZ-01, VIZ-04, VIZ-05, SHIP-02)

**Status:** PASS

Evidence:
- VIZ-01: `analysis/03_visualizations.py` exists with paired `.ipynb` (21,831 bytes); imports `apply_style` from `analysis._style`; assertion `assert DB_PATH.exists()`; reads SQL via `pd.read_sql_query` (2 occurrences) referencing `queries/07_*.sql` and `queries/01_*.sql`
- VIZ-02: `findings/images/01_predictability_ranking.png` exists at 1845×2178 (portrait, height > width), 114 KB
- VIZ-03: `findings/images/02_kl_vs_h_scatter.png` exists at 1600×1600 (square), 139 KB
- VIZ-04: `analysis/02_predictability_modeling.ipynb` size 32,268 bytes (< 60 KB limit) and `analysis/03_visualizations.ipynb` size 21,831 bytes (< 50 KB limit) — both committed with cleared outputs (no embedded base64 PNGs)
- VIZ-05: 04-01-SUMMARY.md attests both notebooks executed end-to-end via `jupyter nbconvert --to notebook --execute --inplace` against the live DB before output-clear
- SHIP-02 POSIX: `scripts/verify_fresh_install.sh` (75 lines) documents 5-command path: venv → pip install (excluding nfl_data_py) → pip install --no-deps nfl_data_py + companions → `python -m etl.run` → nbconvert --execute on each notebook → nbconvert --clear-output; budget gate at 600s
- SHIP-02 Windows: `scripts/verify_fresh_install.ps1` (82 lines) mirrors the POSIX contract using `py -3.11` and PowerShell idioms

### Criterion 4: Single GitHub Actions workflow runs `ruff check` + ETL-module import smoke on push (no notebook execution) and is green on first push to `main` (SHIP-01)

**Status:** PASS

Evidence:
- `.github/workflows/ci.yml` exists (47 lines)
- Triggers: `push` on `main` + `pull_request` on `main` (lines 3-7)
- Concurrency cancel-in-progress block on `${{ github.workflow }}-${{ github.ref }}` (lines 9-11)
- Single job `lint-and-import-smoke` on ubuntu-latest, Python 3.11 (lines 14-24)
- Two-step nfl_data_py install (the Rule-1 fix forward documented in 04-03-SUMMARY.md): filter `nfl_data_py` out of requirements.txt, install rest under strict pandas pin, then `pip install --no-deps nfl_data_py==0.3.3 'appdirs>=1' 'fastparquet>=0.5'` (lines 26-34)
- `ruff check .` step (line 37)
- Import smoke step (lines 39-42): `python -c "import etl"` + `python -c "from analysis import _common, _style"`
- SHIP-08 placeholder regex check (lines 44-47): `! grep -qE '<[A-Z_]{4,}>' README.md` and same for `findings/FINDINGS.md`
- `analysis/__init__.py` (empty package marker, 0 bytes) exists so the `from analysis import _common, _style` import smoke resolves
- `etl/__init__.py` exists (Phase 2 ETL-05 deliverable) so `import etl` resolves
- CI green on commit `a119289` per 04-03-SUMMARY.md (CI #2; CI #1 on `d2ee16d` failed at install step on the pandas pin conflict, fixed forward to a119289)

### Criterion 5: Public repo created via GitHub MCP with description (~70 chars), 5–8 topics, social preview image (1280×640), pinned to Nick's profile, verified in non-author browser (SHIP-03, SHIP-04, SHIP-05, SHIP-07)

**Status:** PASS (orchestrator-attested per 04-03-SUMMARY.md; D-43 fallback policy used UI for all GitHub state changes because token had no admin scope)

Evidence (local codebase preconditions, verifier-confirmed):
- `LICENSE` exists (21 lines, MIT) at repo root with `Copyright (c) 2026 nickthx` (no personal email per D-37) and standard MIT license body
- `findings/images/01_predictability_ranking_top12.png` is the social-preview source PNG at exactly 1280×640 (55,604 bytes) — input to SHIP-04. Note: the GitHub-side variant is the RGB-only resave (the rolled-back 720ab51 commit per Deviations) since matplotlib's RGBA + ICC-profile output was rejected by GitHub's social-preview processor.

Evidence (GitHub-rendered surface, orchestrator-attested per 04-03-SUMMARY.md "Public repo metadata (final state)" + Task 6 incognito report):
- URL: https://github.com/nickthx/nfl-defensive-tendencies
- Description: "Defensive blitz-rate predictability across 32 NFL defenses, 2022-2025" (69 chars, regular hyphens per D-35)
- 8 topics alphabetized: data-analysis, jupyter, nfl-analytics, nfl-data-py, nflverse, python, sports-analytics, sqlite
- License: MIT (visible in repo header)
- Visibility: Public (header badge per Task 6 check #1)
- Branch protection ruleset `main-protection` Active with 3 rules: restrict deletions, block force pushes, require `lint-and-import-smoke` status check (validated by REJECTING direct push 720ab51 per Deviations)
- Social preview: custom 1280×640 RGB-only leaderboard PNG live as og:image at `repository-images.githubusercontent.com/...` (Task 6 check #2)
- Profile pin: visible on https://github.com/nickthx (Task 6 check #5)
- CI: lint-and-import-smoke passing on a119289

### Criterion 6: `du -sh .git/` < 50 MB and commit history contains no `WIP`/`asdf`/scratch messages (SHIP-06)

**Status:** PASS

Evidence:
- `du -sh .git/` reports 2.7 MB (well under 50 MB limit)
- `git log --oneline | grep -iE 'wip|asdf|scratch'` returns zero matches; full history is conventional-commit style (feat/docs/fix/chore prefixes per phase)

---

## Must-Haves Coverage (per-plan)

### Plan 04-01 (Visualizations + S3 chi-square) — 6/6 PASS

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | hero PNG portrait 8x11 | PASS | 1845×2178, height > width, 114 KB |
| 2 | scatter PNG 8x8 with adjustText callouts | PASS | 1600×1600 (square, w-h diff < 50px), `adjust_text(...)` invocation at `analysis/03_visualizations.py`, 8-team callout list verified |
| 3 | top-12 social preview at 1280x640 | PASS | exactly 1280×640, 55 KB |
| 4 | 03_visualizations.ipynb runs end-to-end + cleared outputs | PASS | 21,831 bytes (< 50 KB threshold), 04-01-SUMMARY.md attestation |
| 5 | S3 exploratory cells appended after S1, before STAT-08, with EXPLORATORY label + OR-delta first-class print | PASS | `analysis/02_predictability_modeling.py:333` (EXPLORATORY header), `:349` (S3_PA_BLITZ_SQL), `:363` (read_sql_query), `:411` (or_delta), correct ordering verified |
| 6 | requirements.txt pins adjustText | PASS | `adjustText>=1.0,<2` at requirements.txt with Visualization-block comment |

### Plan 04-02 (FINDINGS + README + cross-doc reconciliation) — 5/6 PASS, 1 PARTIAL

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | FINDINGS.md memo with TL;DR + 6 insights + 3 methodology blocks + 4 appendix tables + 5-item Limitations + FTN/nflverse/CC-BY-SA | PASS | All structure elements grep-confirmed; line 178 |
| 2 | Every claim states N inline (DOC-02); claim→evidence→implication 3-sentence template with mandatory 3rd-sentence caveat | PASS | 25 N-citations counted; spot-check: insight #1 has N=128 cells inline; insight #3 has N(PA=1)=109 inline; insight #5 has N=7,553/N=50,625 inline; 3rd-sentence caveats present (e.g., #1 closes with "Per-team rates vary across situations; appendix T1...") |
| 3 | README hand-rewritten + zero placeholders + hero PNG above fold + 4 stat-first bullets + Mermaid + 5-command setup + 6-term glossary + attribution + Known Issues | PASS | All elements grep-confirmed at README.md:9, 13-16, 20-29, 35-41, 49-54, 65-70, 72-74. SHIP-08 regex returns 0. |
| 4 | data/README.md documents gitignored .db + regen path + parquet cache layout | PASS | 26 lines; Files / Regeneration path / Schema sections present; row counts 1,139 / 197,362 / 185,215 / 105,556 / 58,178 documented |
| 5 | D-48 5-site reconciliation + D-49 SCOPED grep returns zero `n_blitzers > 4` matches | **PARTIAL** | D-49 strict allow-list grep clean (10 file patterns × all clean). However, two user-facing surfaces tracked in git but NOT in the allow-list still carry the stale predicate: SPEC.md L87 + analysis/02_predictability_modeling.ipynb cells 0 and 11 (markdown). See Gaps section. |
| 6 | README hook reconciled to cross-situation framing per D-48 | PASS | README.md:5 reads "across four pre-registered situations (3rd-and-long, red zone, 1st-and-10, 2nd-and-medium)"; the stale "third-and-long only" phrasing is removed |

### Plan 04-03 (CI + LICENSE + ship sequence) — 4/4 PASS for code-side artifacts; 4 GitHub-side truths accept SUMMARY attestation

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | .github/workflows/ci.yml with single job + push/PR triggers + concurrency block + ruff + import smoke + SHIP-08 regex + two-step nfl_data_py install | PASS | All 7 elements verified at .github/workflows/ci.yml lines 1-47; CI #2 green on a119289 |
| 2 | scripts/verify_fresh_install.{sh,ps1} with 5-command path + nbconvert sequence + 600s budget | PASS | sh: 75 lines; ps1: 82 lines; both implement the documented contract |
| 3 | LICENSE = MIT + copyright nickthx no personal email | PASS | 21 lines, `Copyright (c) 2026 nickthx`, standard MIT body |
| 4 | Public repo at github.com/nickthx/nfl-defensive-tendencies with locked metadata | PASS (orchestrator-attested) | 04-03-SUMMARY.md "Public repo metadata (final state)" table |
| 5 | Social preview live (1280×640 RGB resave from top-12 PNG) | PASS (orchestrator-attested) | Task 6 incognito check #2: og:image at repository-images.githubusercontent.com |
| 6 | Repo pinned to nickthx profile | PASS (orchestrator-attested) | Task 6 incognito check #5 |
| 7 | Commit history audit: zero WIP/asdf/scratch + .git/ < 50 MB | PASS | git log greps clean; .git/ = 2.7 MB |
| 8 | Non-author incognito desktop + mobile both render hero PNG above fold + Mermaid + glossary + attribution links | PASS (orchestrator-attested) | Task 6: 7/7 desktop + 3/3 mobile checks PASS |

**Score:** 14/16 must-haves PASS (one partial — the user-facing-surface scope of D-49 is broader than the strict allow-list the plan ran).

---

## REQ-ID Coverage (21/21 SATISFIED)

| REQ-ID | Description | Status | Evidence path |
|--------|-------------|--------|---------------|
| VIZ-01 | 03_visualizations.ipynb exports all PNGs to findings/images/ via _style.py rcParams | SATISFIED | analysis/03_visualizations.py imports apply_style from analysis._style; produces 3 PNGs in findings/images/ |
| VIZ-02 | Hero chart at findings/images/01_predictability_ranking.png embedded in README first scroll | SATISFIED | PNG: 1845×2178 portrait; README.md:9 image embed |
| VIZ-03 | At least one non-bar-chart visualization | SATISFIED | findings/images/02_kl_vs_h_scatter.png — rank-rank scatter (1600×1600), 8 callouts via adjust_text |
| VIZ-04 | Notebooks have outputs cleared via nbconvert --clear-output | SATISFIED | 02_predictability_modeling.ipynb=32 KB, 03_visualizations.ipynb=21.8 KB; no embedded base64 PNGs |
| VIZ-05 | Notebooks run end-to-end on fresh kernel | SATISFIED | 04-01-SUMMARY.md attestation; both executed via nbconvert --execute against live DB |
| DOC-01 | findings/FINDINGS.md memo TL;DR → 5-7 insights → methodology → limitations → attribution | SATISFIED | FINDINGS.md 178 lines; 6 numbered insights; 3 methodology blocks; 4 appendix tables; 5 limitations; CC-BY-SA attribution |
| DOC-02 | Every FINDINGS claim states N inline; tiered N discipline visible | SATISFIED | 25 N-citations grep-counted; methodology Block 3 documents N≥30 / N≥100 / N≥15-with-flag |
| DOC-03 | README hand-written + hero PNG above fold + 3-4 stat-first bullets | SATISFIED | README.md:9 hero embed; :13-16 four stat-first bullets (PHI/SF/IND, S1 chi-square, RZ pressure, DET 52.3%); no AI-template tone |
| DOC-04 | README has Mermaid architecture diagram | SATISFIED | README.md:20-29 `flowchart LR` data-flow diagram |
| DOC-05 | README 5-command setup + reproducibility budget callout | SATISFIED | README.md:35-41 (5 commands); :43 ("under 10 minutes on a stock laptop") |
| DOC-06 | README 6-term glossary | SATISFIED | README.md:49-54 — Down, Distance, EPA, Blitz (n_blitzers > 0), RPO, Predictability index |
| DOC-07 | README CC-BY-SA attribution + Known Issues for nfl_data_py archival | SATISFIED | README.md:65-70 attribution; :72-74 Known Issues |
| DOC-08 | data/README.md documents gitignored .db + regen path + parquet cache | SATISFIED | data/README.md 26 lines; all three sections present |
| SHIP-01 | GitHub Actions workflow with ruff + ETL import smoke | SATISFIED | .github/workflows/ci.yml; CI green on a119289 |
| SHIP-02 | Fresh-venv reproducibility verified | SATISFIED | scripts/verify_fresh_install.{sh,ps1}; 04-03-SUMMARY.md notes 257s install on Win11 (Rule-2 calibration; budget achievable on stock macOS/Linux) |
| SHIP-03 | Public repo with description + 5-8 topics | SATISFIED (orchestrator-attested) | 04-03-SUMMARY.md "Public repo metadata"; 8 topics alphabetized; 69-char description |
| SHIP-04 | Social preview image 1280×640 from hero | SATISFIED (orchestrator-attested) | Task 6 check #2: og:image custom; RGB-only resave landed via Settings UI per D-43 fallback |
| SHIP-05 | Repo pinned to Nick's profile | SATISFIED (orchestrator-attested) | Task 6 check #5 |
| SHIP-06 | Commit history clean + .git/ < 50 MB | SATISFIED | grep -iE 'wip\|asdf\|scratch' returns 0; .git/ = 2.7 MB |
| SHIP-07 | Final push verified on non-author browser | SATISFIED (orchestrator-attested) | Task 6 incognito: 7/7 desktop + 3/3 mobile PASS |
| SHIP-08 | Zero `<UPPERCASE_PLACEHOLDER>` slots in README/FINDINGS; enforced as CI step | SATISFIED | `! grep -qE '<[A-Z_]{4,}>'` exits 0 on both files; .github/workflows/ci.yml:44-47 enforces in CI |

**Score:** 21/21 REQ-IDs SATISFIED.

Note: REQUIREMENTS.md traceability table (lines 191-211) still marks Phase 4 REQs as `Pending`. This is a documentation lag — the requirements ARE implemented, but the table hasn't been bumped to Complete. Phase 3 has the same lag (its REQs are also marked Pending despite Phase 3 being verified-passed). Not a real gap; flagged here for future-state housekeeping.

---

## ROADMAP Success Criteria — 6/6 PASS

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Hero chart above fold + 4 bullets + Mermaid + 5-command setup + 6-term glossary, hand-written | PASS (local + orchestrator-attested) |
| 2 | FINDINGS.md memo with TL;DR + insights with N inline + methodology + limitations + attribution | PASS |
| 3 | Fresh clone runs install + ETL + Restart-and-Run-All; PNGs regenerate; outputs cleared | PASS |
| 4 | GitHub Actions runs ruff + ETL import smoke; green on first push | PASS |
| 5 | Repo created via MCP (or UI fallback per D-43) with description + topics + social preview + profile pin | PASS (D-43 fallback used UI; logged in 04-03-SUMMARY.md) |
| 6 | .git/ < 50 MB + clean commit history | PASS |

---

## Cross-phase Regression Check

| Surface | Status | Detail |
|---------|--------|--------|
| schema/*.sql | unchanged from Phase 2 baseline | 3 files (01_create_tables, 02_indexes, 03_views) — clean |
| etl/*.py | unchanged from Phase 2 baseline | 6 files (run, build_db, columns, load_pbp, load_ftn, __init__) — `import etl` resolves |
| queries/*.sql | reconciled (D-48/D-49) | All 8 SQL files clean of stale `n_blitzers > 4`; queries/01_*.sql Caveats comment was a Phase-4 in-scope fix per 04-02-SUMMARY |
| analysis/_common.py + _style.py | unchanged from Phase 3 | Imports resolve; SEED, DB_PATH, get_conn, min_n_filter, apply_style all exposed |
| analysis/01_exploratory.py + .ipynb | reconciled (D-48 Site 5) | SQL string + comment now use `n_blitzers >= 1`; .ipynb cleared (10.6 KB) |
| analysis/02_predictability_modeling.py | reconciled (D-48 + D-49 in-scope fixes) + Phase-4 S3 cells appended | Source clean; S3 cells at L333+ produce OR-delta first-class output |
| analysis/02_predictability_modeling.ipynb | **DRIFT** | Outputs cleared (32 KB), but markdown cells 0 and 11 still carry stale `n_blitzers > 4` from pre-D-48 source. See Gaps. |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| SPEC.md | 87 | Stale `n_blitzers > 4` in operational definition | Warning | User-facing on GitHub Code tab; not in D-49 strict allow-list, but inconsistent with the corrected definition documented everywhere else |
| analysis/02_predictability_modeling.ipynb | cell 0 (md), cell 11 (md) | Stale `n_blitzers > 4` in two markdown cells | Warning | Out of sync with corrected paired .py source; .ipynb is the GitHub-rendered notebook surface |

No blockers. Both items are user-facing-surface drift from the D-48 reconciliation sweep, captured in the Gaps section below.

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Hero PNG renders + dimensions | `python -c "from PIL import Image; print(Image.open('findings/images/01_predictability_ranking.png').size)"` | (1845, 2178) | PASS (portrait) |
| Social-preview PNG exact 1280×640 | same | (1280, 640) | PASS |
| Scatter PNG square 8x8 inches | same | (1600, 1600) | PASS |
| SHIP-08 regex on README | `! grep -qE '<[A-Z_]{4,}>' README.md` | exit 0 | PASS |
| SHIP-08 regex on FINDINGS | `! grep -qE '<[A-Z_]{4,}>' findings/FINDINGS.md` | exit 0 | PASS |
| Commit-history WIP/asdf/scratch | `git log --oneline \| grep -iE 'wip\|asdf\|scratch'` | empty | PASS |
| .git/ size | `du -sh .git/` | 2.7 MB | PASS (< 50 MB) |
| D-49 strict allow-list grep | scoped `n_blitzers > 4` across plan-defined allow-list | 0 matches across 10 file patterns | PASS |
| `import etl` resolves | `python -c "import etl"` | exit 0 | PASS (CI green attests pandas-loaded equivalent) |
| `from analysis import _common, _style` | same | structural OK; pandas import requires venv | DEFERRED — verifier env lacks pandas; CI green on a119289 attests this works |
| ruff check . | `ruff check .` | not installable in verifier env | DEFERRED — CI #2 attests ruff clean on a119289 |

---

## Gaps

### Gap 1 (PARTIAL): D-49 user-facing-surface coverage incomplete

**Truth:** "Cross-doc reconciliation sweep complete (D-48): all user-facing surfaces + code carry n_blitzers > 0 / n_blitzers >= 1; zero stale n_blitzers > 4 matches across user-facing surfaces."

**Reason:** The plan-defined D-49 allow-list (README.md, findings/FINDINGS.md, data/README.md, .planning/PROJECT.md, docs/*.md, analysis/*.py, queries/*.sql, etl/*.py, schema/*.sql, scripts/*.py) is clean with zero matches. However, two user-facing surfaces tracked in git but NOT enumerated in the allow-list still carry the stale predicate.

**Artifacts with issues:**

- `SPEC.md:87` — operational definition reads ``the league-wide blitz rate (`n_blitzers > 4`) and pass-rusher count`` in the Distribution baseline business question. SPEC.md is git-tracked at repo root and renders on the public GitHub Code tab; recruiters can land here.
- `analysis/02_predictability_modeling.ipynb` cells 0 (line 25, methodology-lock D-02 markdown) and 11 (line 359, STAT-06 chi-square headline DEVIATION-note markdown). The paired .py source at `analysis/02_predictability_modeling.py:34` IS corrected to `n_blitzers > 0`; the .ipynb has not been re-synced from the corrected .py.

**Missing (remediation):**

1. `SPEC.md:87` — change ``(`n_blitzers > 4`)`` to ``(`n_blitzers > 0`)``, OR rephrase to ``(extra rushers above the base 4-man front)`` to match the calibration sentence pattern used in `docs/ftn-schema-audit.md`.
2. `analysis/02_predictability_modeling.ipynb` — run `jupytext --sync analysis/02_predictability_modeling.py` to regenerate the .ipynb markdown cells from the corrected .py source. Confirm with `python -c "import json; nb = json.load(open('analysis/02_predictability_modeling.ipynb', encoding='utf-8')); print(sum(1 for c in nb['cells'] if 'n_blitzers > 4' in ''.join(c.get('source', []))))"` returns 0. Then `jupyter nbconvert --clear-output --inplace` to keep the cleared-outputs invariant.
3. (Optional, future-proofing) Add SPEC.md and `analysis/*.ipynb` to the D-49 allow-list in any future reconciliation runbook so this class of drift is caught next time. Note that D-49 in 04-CONTEXT.md actually says "repo-wide grep" — the strict allow-list lives only in 04-02-PLAN.md frontmatter, which is the source of the drift.

**This looks like a lateral oversight, not a structural failure.** The D-48 5-site sweep was internally consistent and the plan-checker approved the strict allow-list at planning time. The .ipynb is a generated artifact that drifted because cell-source resync wasn't part of the sweep procedure. SPEC.md is a Phase 1 artifact that the D-48 site enumeration didn't catch.

**Override option:** If the user judges these two surfaces out-of-scope per the plan-locked D-49 definition (the strict allow-list explicitly EXCLUDED `.planning/phases/*` and `.planning/STATE.md` as audit trail; `.ipynb` carrying the stale phrase in a methodology-lock D-02 cell could be argued as similar audit-trail context, and SPEC.md could be argued as Phase-1-locked), add this to the VERIFICATION.md frontmatter:

```yaml
overrides:
  - must_have: "Cross-doc reconciliation sweep complete (D-48): all user-facing surfaces + code carry n_blitzers > 0 / n_blitzers >= 1; zero stale n_blitzers > 4 matches across user-facing surfaces"
    reason: "D-49 strict allow-list (per 04-02-PLAN frontmatter) returns zero matches and was the plan-locked verification scope; SPEC.md is Phase-1 locked and analysis/*.ipynb cell-source carries the stale predicate as audit-trail context next to the corrected definition. Both surfaces are out-of-scope of the plan-locked D-49 definition."
    accepted_by: "<your-name>"
    accepted_at: "2026-05-01T00:00:00Z"
```

---

## Verdict

**Status: gaps_found** (with low-severity remediation; passing alternative via override is reasonable)

- All 21 REQ-IDs are SATISFIED.
- All 6 ROADMAP success criteria PASS.
- 14 of 16 must-haves PASS; 1 PARTIAL (D-49 allow-list scope vs. broader user-facing-surface coverage); 1 covered by orchestrator attestation (counted in PASS).
- The two surface-drift items (SPEC.md L87, 02_predictability_modeling.ipynb cells 0+11) are genuine user-facing surfaces but were OUT of the plan-locked D-49 strict allow-list. They cost ~5 minutes to fix, OR can be accepted via override with the rationale above.
- Public repo state, social preview, profile pin, and non-author browser verification all rely on orchestrator Task 6 incognito attestation (verifier cannot re-confirm without admin token scope; this is documented and accepted per the verification context provided).

The phase delivered the recruiter-facing surface end-to-end. The gap is housekeeping on two surfaces not enumerated in the plan-locked D-48 site list; the recruiter signal (hero PNG above the fold, hand-written README, FINDINGS memo, public repo with branch protection + social preview + profile pin, green CI) is intact.

---

*Verified: 2026-05-01*
*Verifier: Claude (gsd-verifier)*
