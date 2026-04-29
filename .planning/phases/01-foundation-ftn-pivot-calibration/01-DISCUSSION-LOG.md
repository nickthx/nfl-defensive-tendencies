# Phase 1: Foundation & FTN Pivot Calibration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `01-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 01-foundation-ftn-pivot-calibration
**Areas discussed:** Anchor dimension selection rule, Pre-registered situations, Public repo name
**Areas deferred to Claude's Discretion:** Audit notebook polish + README hook timing

---

## Gray-Area Selection

| Option | Description | Selected |
|--------|-------------|----------|
| Anchor dimension selection rule | How to pick 3–4 anchors from 8 FTN candidates | ✓ |
| Pre-registered situations | Which 3–5 situations FINDINGS.md commits to | ✓ |
| Public repo name | Confirm `nfl-defensive-tendencies` or alternative | ✓ |
| Audit notebook polish + README hook timing | Skeleton sections, hook rewrite timing, audit notebook polish | (deferred) |

**User's choice:** "1, 2, and 3. not 4"

---

## Area 1: Anchor Dimension Selection Rule

### Q1.1 — Selection rule

| Option | Description | Selected |
|--------|-------------|----------|
| NaN-cutoff + story tiebreaker | Drop columns >30% NaN on relevant play_type; among survivors curate for cross-category diversity | ✓ |
| Pure NaN-rate ranking | Rank all 8 by lowest population-weighted NaN rate; pick top 3–4 mechanically | |
| Story-first, NaN-as-veto | Pre-pick most analytically interesting; veto only if NaN >50% on relevant play_type | |

**User's choice:** NaN-cutoff + story tiebreaker (recommended)
**Notes:** Documents both the rule AND the editorial choice in `docs/ftn-schema-audit.md`.

### Q1.2 — NaN-rate ceiling

| Option | Description | Selected |
|--------|-------------|----------|
| 30% on the relevant play_type | Strict; protects N≥30/100/15 sample-size discipline | ✓ |
| 50% on the relevant play_type | Permissive; risks unstable chi-square cells | |
| No fixed ceiling — judgment call | Document the rate, explain in prose | |

**User's choice:** 30% on the relevant play_type (recommended)

### Q1.3 — Anchor count target

| Option | Description | Selected |
|--------|-------------|----------|
| Aim for 4, accept 3 if NaN cuts one | Max breadth across categories; 30% NaN gate is only valid drop reason | ✓ |
| Target 3, treat 4 as stretch | Tighter focus, fewer chi-squares | |
| Let the NaN data decide | Whatever passes 30% with story-diversity weighting | |

**User's choice:** Aim for 4, accept 3 if NaN cuts one (recommended)

### Q1.4 — Empty-category contingency

| Option | Description | Selected |
|--------|-------------|----------|
| Document gap, fill 4th from surplus | Name empty category as known limitation in audit doc | ✓ |
| Drop to 3 anchors, two-category coverage | Keep one anchor per surviving category | |
| Relax NaN ceiling for that category | Allow >30% NaN for one column with explicit narrative flag | |

**User's choice:** Document gap, fill 4th from surplus (recommended)
**Notes:** Honest about what the data can't answer; do NOT relax the NaN ceiling silently.

---

## Area 2: Pre-registered Situations

### Q2.1 — Slate approach

| Option | Description | Selected |
|--------|-------------|----------|
| Pick 4 now, lock in analysis-plan.md | Strict multiple-comparisons firewall | ✓ |
| Pick 3 now, leave 1 slot for post-audit | 4th slot filled in Phase 1 closeout | |
| Pick 5, accept multiple-comparisons cost | Bonferroni / BH correction in chi-square reporting | |

**User's choice:** Pick 4 now, lock in analysis-plan.md (recommended)

### Q2.2 — Situation selection (multi-select)

| Option | Description | Selected |
|--------|-------------|----------|
| 3rd-and-long (≥7 yards) | Pressure / blitz showcase, high recruiter recognition | ✓ |
| Red zone (yardline_100 ≤ 20) | Tendency contraction, easy to interpret | ✓ |
| 1st-and-10 (neutral baseline) | Highest sample size; anchors league-deviation comparators | ✓ |
| 2nd-and-medium (3–6 yards) | Strongest team-by-team variance; richest predictability signal | ✓ |

**User's choice:** All four recommended situations selected.

### Q2.3 — Play-action handling

| Option | Description | Selected |
|--------|-------------|----------|
| Cross-cutting modifier across all 4 | is_play_action becomes analytical lens, not 5th situation | ✓ |
| 5th pre-registered situation | Adds play-action as independent slate entry; needs MC correction | |
| Exploratory only — keep slate at 4 | Play-action analysis stays in 01_exploratory.ipynb | |

**User's choice:** Cross-cutting modifier across all 4 (recommended)

### Q2.4 — Plan format

| Option | Description | Selected |
|--------|-------------|----------|
| Falsifiable hypotheses per situation | 1–2 hypotheses worded as predictions per situation | ✓ |
| Open questions per situation | 1–2 analytical questions per situation | |
| Mixed (hypothesis where confident, question where exploring) | Per-situation tone | |

**User's choice:** Falsifiable hypotheses per situation (recommended)

---

## Area 3: Public Repo Name

### Q3.1 — Repo name

| Option | Description | Selected |
|--------|-------------|----------|
| nfl-defensive-tendencies | PROJECT.md default; matches post-pivot framing exactly | ✓ |
| nfl-defense-tendencies-2024 | Adds season anchor; reads more academic | |
| nfl-blitz-and-pressure | Narrower hook; risky if anchors aren't pressure-heavy | |
| nfl-defensive-scheme-analytics | Broader but may overpromise (no Cover 0–6) | |

**User's choice:** nfl-defensive-tendencies (recommended)

### Q3.2 — GitHub topics slate

| Option | Description | Selected |
|--------|-------------|----------|
| Default 7 from REQUIREMENTS.md | 7-topic slate verified for recruiter discovery surfaces | |
| Add 'portfolio' as 8th | Explicit portfolio framing | |
| Decide at ship time | Defer to Phase 4 / SHIP-03 | ✓ |

**User's choice:** Decide at ship time
**Notes:** Topics are not in the README; only used in GitHub MCP repo config. The 7-topic working default in REQUIREMENTS.md remains in place but is not locked in Phase 1.

---

## Claude's Discretion

User explicitly skipped Area 4 (audit notebook polish + README skeleton sections + hook-rewrite timing). Captured under `01-CONTEXT.md` §Claude's Discretion with default approach for each:

- README skeleton: standard portfolio sections (Hook → Findings preview → Architecture → Setup → Glossary → Methodology → Limitations → Attribution → Known Issues), empty bodies.
- Audit notebook: presentable level (kept in repo per FEATURES.md P2).
- README hook (AUDIT-07): write 2–3 sentence plain-English hook in Phase 1 with placeholder slots for Phase 4 to fill in headline numbers.
- NaN profile granularity: by `play_type` is required; per-season breakdown is optional polish.

## Deferred Ideas

- GitHub topics slate (locked in PROJECT.md working default; revisit at SHIP-03).
- Per-season FTN NaN breakdown (optional polish on `audit/ftn_null_profile.csv`).
- Bonferroni / BH correction (not needed unless analysis exceeds the locked 4-situation slate).
- `nflreadpy` migration (already deferred to V2-LIB-01 in REQUIREMENTS.md).
