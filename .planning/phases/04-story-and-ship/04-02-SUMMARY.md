---
phase: 04-story-and-ship
plan: "02"
subsystem: documentation
tags: [findings-memo, readme, data-readme, reconciliation, n-blitzers, d48, d49]

requires:
  - phase: 04-story-and-ship
    plan: "01"
    provides: "findings/images/01_predictability_ranking.png, S3 chi-square numbers, league avg=14.28"
provides:
  - "findings/FINDINGS.md (DOC-01+DOC-02: memo with 6 insights + methodology + appendix + limitations + attribution)"
  - "README.md (DOC-03+DOC-04+DOC-05+DOC-06+DOC-07: hand-rewrite with hero PNG + Mermaid + setup + glossary + Known Issues)"
  - "data/README.md (DOC-08: gitignored DB regen path + parquet cache layout)"
  - "5-site D-48 cross-doc reconciliation (n_blitzers > 0 consistent across all user-facing surfaces + code)"
affects:
  - "04-03-PLAN (SHIP-08 placeholder regex now passes; D-49 grep verified clean)"

tech-stack:
  added: []
  patterns:
    - "Memo voice: numbers-first, N inline, claim->evidence->implication/caveat 3-sentence structure"
    - "Pre-registered vs exploratory firewall labeling in prose (not just code)"
    - "D-49 scoped grep using explicit file allow-list (immune to .planning/phases/* audit trail)"

key-files:
  created:
    - "findings/FINDINGS.md (178 lines)"
    - "data/README.md (extended to 26 lines with Files/Regeneration/Schema sections)"
  modified:
    - "README.md (74 lines — full hand-rewrite over skeleton)"
    - ".planning/PROJECT.md (Site 1: n_blitzers > 0 at L58)"
    - ".planning/phases/03-analytical-layer-sql-python/03-CONTEXT.md (Site 2: D-02 + D-09 corrected; calibration sentence added)"
    - "docs/ftn-schema-audit.md (Site 3: operational definition + Calibration note section)"
    - "docs/analysis-plan.md (H1 hypothesis threshold corrected)"
    - "analysis/01_exploratory.py (Site 5: SQL n_blitzers >= 1 + comment fixed; re-executed; outputs cleared)"
    - "analysis/01_exploratory.ipynb (cleared outputs, 10.6 KB)"
    - "analysis/02_predictability_modeling.py (D-02 comment + DEVIATION comment updated)"
    - "queries/01_tendency_distribution_by_team.sql (Caveats comment updated)"

key-decisions:
  - "League average cited as 14.3 (rounded from live DB value 14.28 per 04-01-SUMMARY.md)"
  - "TL;DR bullet for leaderboard uses 14.3 (consistent with FINDINGS narrative)"
  - "Methodology Block 1 avoids literal n_blitzers > 4 string by describing as nflfastR-style total-rusher threshold"
  - "Calibration note in ftn-schema-audit.md avoids n_blitzers > 4 literal by using n_pass_rushers >= 5 as the comparator"
  - "D-49 required fixing docs/analysis-plan.md H1, 02_predictability_modeling.py comments, and queries/01 Caveats comment beyond the original 5-site plan — these were in-scope files the pattern scan did not enumerate but the negative grep caught"

metrics:
  duration: 45min
  completed: 2026-04-30
---

# Phase 4 Plan 02: FINDINGS.md + README + Cross-Doc Reconciliation Summary

**Recruiter-facing memo (findings/FINDINGS.md), hand-rewritten README.md (hero PNG above the fold, Mermaid diagram, 6-term glossary, 5-command setup), and 5-site D-48 cross-doc reconciliation — all DOC requirements satisfied, D-49 scoped grep returns zero matches**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-04-30
- **Tasks:** 3 of 3
- **Files modified/created:** 10

## Accomplishments

- Authored `findings/FINDINGS.md` from scratch: 178 lines, 6 named insights in locked sequence, 3 methodology blocks, 4 appendix tables (T1-T4 with S1+S3 contingency cells), 5 limitations (L1/L2/L3/L4/L6), FTN + nflverse CC-BY-SA attribution. All AI-template phrase greps pass (comprehensive, leverage, cutting-edge, welcome to — all absent).
- Hand-rewrote `README.md`: hero PNG above the fold, cross-situation hook framing (4 pre-registered situations named; stale "third-and-long only" phrasing removed), Mermaid flowchart LR diagram, 5-command setup block with reproducibility budget, 6-term glossary with `n_blitzers > 0` blitz definition, Known Issues with `nfl_data_py` archival note. Zero placeholders (`<[A-Z_]{4,}>` returns 0 matches).
- Extended `data/README.md` with Files / Regeneration path / Schema sections and full row counts.
- Executed the 5-site D-48 reconciliation sweep plus 4 additional in-scope file fixes caught by the D-49 negative grep: `docs/analysis-plan.md` H1, `analysis/02_predictability_modeling.py` comments (2 locations), `queries/01_tendency_distribution_by_team.sql` Caveats comment.
- Re-executed `analysis/01_exploratory.ipynb` end-to-end after SQL fix; confirmed blitz_rate values 26-34% (corrected from near-zero); cleared outputs (10.6 KB, well under 50 KB limit).
- D-49 scoped negative grep returns zero `n_blitzers > 4` matches across all user-facing surfaces and code.

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Author findings/FINDINGS.md | `854f9c7` | findings/FINDINGS.md |
| 2 | Hand-rewrite README.md | `ca484a1` | README.md |
| 3 | data/README.md + 5-site D-48 sweep + D-49 verify | `5f1d5e9` | data/README.md, .planning/PROJECT.md, 03-CONTEXT.md, ftn-schema-audit.md, analysis-plan.md, 01_exploratory.py/.ipynb, 02_predictability_modeling.py, queries/01_*.sql |

## D-48 / D-49 Reconciliation Results

### 5-site sweep (D-48)

| Site | File | Before | After |
|------|------|--------|-------|
| 1 | .planning/PROJECT.md L58 | `n_blitzers > 4` | `n_blitzers > 0` |
| 2 | 03-CONTEXT.md D-02 + D-09 | `n_blitzers > 4` | `n_blitzers > 0`; calibration sentence appended |
| 3 | docs/ftn-schema-audit.md operational definition | `n_blitzers > 4` | `n_blitzers > 0`; Calibration note section added |
| 4 | README.md glossary | (new entry) | `n_blitzers > 0` |
| 5 | analysis/01_exploratory.py L163 SQL + L148 comment | `n_blitzers > 4` | `n_blitzers >= 1` |

### Additional in-scope fixes caught by D-49 negative grep

| File | Location | Fix |
|------|----------|-----|
| docs/analysis-plan.md | H1 hypothesis | stale threshold -> `n_blitzers > 0` |
| analysis/02_predictability_modeling.py | D-02 comment (L34) | stale threshold -> `n_blitzers > 0` |
| analysis/02_predictability_modeling.py | DEVIATION comment (L259) | stale threshold -> prose description |
| queries/01_tendency_distribution_by_team.sql | Caveats comment (L6) | stale threshold -> prose description |

### D-49 scoped negative grep result

**Zero matches** for `n_blitzers > 4` across the user-facing-surfaces-plus-code allow-list (README.md, findings/FINDINGS.md, data/README.md, docs/*.md, .planning/PROJECT.md, analysis/*.py, queries/*.sql, etl/*.py, schema/*.sql, scripts/*.py). The `.planning/phases/*` and `.planning/STATE.md` audit-trail references are intentionally out of scope.

### D-49 positive presence checks

| File | Pattern | Count |
|------|---------|------:|
| .planning/PROJECT.md | `n_blitzers > 0` | 1 |
| 03-CONTEXT.md | `n_blitzers > 0` | 4 |
| docs/ftn-schema-audit.md | `n_blitzers > 0` | 2 |
| README.md | `n_blitzers > 0` or `>= 1` | 2 |
| analysis/01_exploratory.py | `n_blitzers > 0` or `>= 1` | 2 |

## FINDINGS.md Word Count and Verification

- **Line count:** 178 lines
- **Placeholder regex `<[A-Z_]{4,}>`:** 0 matches
- **AI-template phrase greps:** 0 matches (comprehensive, leverage/leverages, cutting-edge, "in this article we will", "I am excited", "welcome to")
- **`n_blitzers > 4` in FINDINGS.md:** 0 matches
- **6 numbered insights:** confirmed (## 1. through ## 6.)
- **5 limitations:** L1/L2/L3/L4/L6 present; L5 absent (lives in README Known Issues per D-18)
- **Required strings:** 1.235%, inter-rater reliability, CC-BY-SA, nflverse, nfl_data_py, Exploratory, pre-registered — all present

## README.md Verification

- **Placeholder regex `<[A-Z_]{4,}>`:** 0 matches
- **`n_blitzers > 4`:** 0 matches
- **Hook framing:** cross-situation (names 3rd-and-long, red zone, 1st-and-10, 2nd-and-medium); stale "predictable than others on third-and-long" removed
- **Hero PNG:** `findings/images/01_predictability_ranking.png` embedded above fold
- **Mermaid diagram:** `flowchart LR` present
- **6-term glossary:** Down, Distance, EPA, Blitz (n_blitzers > 0), RPO, Predictability index — all present
- **Known Issues:** nfl_data_py archived 2025-09-25 noted

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] D-49 required fixing 4 additional in-scope files beyond the 5-site plan**

- **Found during:** Task 3, Sub-task C (D-49 negative grep)
- **Issue:** The plan enumerated 5 specific reconciliation sites. The D-49 negative grep over the full allow-list caught 4 additional `n_blitzers > 4` references in in-scope files: `docs/analysis-plan.md` H1, `analysis/02_predictability_modeling.py` (2 comments), `queries/01_tendency_distribution_by_team.sql` Caveats comment. These were in-scope per D-49's explicit file list but not enumerated in the plan's 5-site list.
- **Fix:** Updated all 4 files inline; re-ran D-49 negative grep; confirmed zero matches.
- **Files modified:** docs/analysis-plan.md, analysis/02_predictability_modeling.py, queries/01_tendency_distribution_by_team.sql
- **Committed in:** `5f1d5e9` (Task 3)

**2. [Rule 1 - Bug] ftn-schema-audit.md Calibration note initially contained literal `n_blitzers > 4`**

- **Found during:** Task 3, Sub-task C (D-49 negative grep)
- **Issue:** The calibration note I added to explain the correction used the literal stale predicate as a historical reference, which the D-49 negative grep correctly flagged.
- **Fix:** Rephrased to use `n_pass_rushers >= 5` (the nflfastR convention it was mistakenly borrowing from) and "nflfastR-style total-rusher threshold" rather than the literal FTN column predicate.
- **Committed in:** `5f1d5e9` (Task 3)

**3. [Rule 1 - Deviation] League average cited as 14.3, not 14.28 or ~12.5**

- **Found during:** Task 1 authoring
- **Issue:** The plan's context block estimated league avg ~12.5; 04-01-SUMMARY.md states the live computed value is 14.28. FINDINGS.md and README both cite 14.3 (one decimal, rounded).
- **Resolution:** 14.28 rounded to 14.3 is the correct live value per 04-01-SUMMARY.md. The plan's ~12.5 was a pre-execution estimate. Using 14.3 (not 14.28) keeps prose readable without false precision. Consistent across both files.

## Known Stubs

None. All numbers in FINDINGS.md and README.md are empirical values from the live DB (via 04-01-SUMMARY.md and Phase 3 SUMMARYs). No hardcoded placeholder values flow to any output.

## Threat Flags

None. This plan creates documentation files only (FINDINGS.md, README.md, data/README.md) and fixes prose references in existing source files. No new network endpoints, auth paths, schema changes, or security-relevant surfaces introduced.

## Self-Check

### Created/modified files exist

- `findings/FINDINGS.md` — FOUND (178 lines)
- `README.md` — FOUND (74 lines, hand-rewritten)
- `data/README.md` — FOUND (26 lines, extended)
- `.planning/PROJECT.md` — FOUND (n_blitzers > 0 at L58)
- `docs/ftn-schema-audit.md` — FOUND (Calibration note present)
- `analysis/01_exploratory.py` — FOUND (n_blitzers >= 1 at SQL + comment)
- `analysis/01_exploratory.ipynb` — FOUND (10.6 KB, outputs cleared)

### Commits exist

- `854f9c7` — Task 1 FINDINGS.md
- `ca484a1` — Task 2 README.md
- `5f1d5e9` — Task 3 reconciliation sweep

## Self-Check: PASSED
