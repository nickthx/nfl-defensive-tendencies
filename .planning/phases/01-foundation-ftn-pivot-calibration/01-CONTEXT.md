# Phase 1: Foundation & FTN Pivot Calibration - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Bootstrap a clean Python 3.11 repo skeleton (BOOT-01..07) and complete the FTN pivot calibration (AUDIT-01..07) — measure per-column NaN rates by `play_type` for 2022–2024, pick the 3–4 anchor defensive dimensions, pre-register the 4 analytical situations, and lock the public GitHub repo name. Every downstream phase builds on the calibrated dimension set and pre-registered situation slate produced here.

ETL pipeline construction (Phase 2), SQL/notebook analysis (Phase 3), and visualization/docs/ship (Phase 4) are out of scope for this phase.

</domain>

<decisions>
## Implementation Decisions

### Anchor dimension selection rule (AUDIT-03)

- **D-01:** Selection rule = **NaN-cutoff + story tiebreaker**. Drop any FTN column with >30% NaN on the relevant `play_type` (pass plays for `n_blitzers` / `n_pass_rushers`, all competitive plays for personnel/location columns). Among the survivors, curate for **cross-category diversity** across the three categories (pressure / play-fakery / personnel). Document both the mechanical rule AND the editorial cross-category choice in `docs/ftn-schema-audit.md`.
- **D-02:** NaN-rate ceiling = **30% on the relevant `play_type`**. A column with >30% NaN where it should be populated is dropped from anchor consideration. Conservative; protects sample size for the tiered N≥30/100/15 discipline downstream.
- **D-03:** Anchor count target = **aim for 4, accept 3 if NaN cuts one**. Maximum breadth across categories; the 30% gate is the only valid reason to drop to 3.
- **D-04:** Empty-category contingency = **document the gap, fill 4th from surplus**. If a category (pressure / play-fakery / personnel) has zero survivors after the 30% cut, `docs/ftn-schema-audit.md` names the empty category as a known limitation; the 4th anchor comes from whichever category has surplus survivors. Honest about what the data can't answer; do NOT relax the NaN ceiling.

The 8 candidate columns split into:
- **Pressure / front:** `n_blitzers`, `n_pass_rushers`
- **Play-fakery:** `is_play_action`, `is_screen_pass`, `is_rpo`
- **Personnel / location:** `qb_location`, `n_offense_backfield`, `starting_hash`

### Pre-registered analytical situations (AUDIT-04)

- **D-05:** Approach = **pick 4 situations now, lock in `docs/analysis-plan.md` before any Phase 3 query runs**. Strict multiple-comparisons firewall — anything outside the 4 stays in `01_exploratory.ipynb` and never appears as a headline insight in `FINDINGS.md`.
- **D-06:** The 4 pre-registered situations:
  1. **3rd-and-long** (`down = 3 AND ydstogo >= 7`) — pressure / blitz showcase, high recruiter recognition.
  2. **Red zone** (`yardline_100 <= 20`) — tendency contraction, easy to interpret.
  3. **1st-and-10** (`down = 1 AND ydstogo = 10`) — neutral baseline, highest sample size, anchors league-deviation comparators.
  4. **2nd-and-medium** (`down = 2 AND ydstogo BETWEEN 3 AND 6`) — strongest team-by-team variance, richest signal for the predictability index.
- **D-07:** Play-action treatment = **cross-cutting modifier across all 4 situations**, not a 5th slate entry. `is_play_action` becomes an analytical lens (each situation gets a play-action vs. straight-dropback split where N permits) rather than a separate pre-registered situation. Keeps the slate at 4; integrates play-fakery analysis into every claim.
- **D-08:** Plan format = **falsifiable hypotheses per situation**. Each of the 4 situations gets 1–2 hypotheses worded as predictions (e.g., "Defenses blitz at >35% league-wide on 3rd-and-long"). Each hypothesis names what would falsify it. Strongest stats discipline; reads as rigorous analyst.

### Public repo + ship config (AUDIT-05)

- **D-09:** Public GitHub repo name = **`nfl-defensive-tendencies`** (locked at end of Phase 1). Working folder stays `nfl-coverage-tendencies` for git history continuity per CLAUDE.md. The Phase 4 GitHub MCP repo creation step (SHIP-03) uses this name.
- **D-10:** GitHub topics slate = **defer to Phase 4 / SHIP-03**. Topics are not in the README and are only used during GitHub MCP repo configuration. The default 7-topic slate from REQUIREMENTS.md (`nfl-analytics`, `data-analysis`, `python`, `sqlite`, `jupyter`, `nfl-data-py`, `sports-analytics`) remains the working default but is not locked in Phase 1.

### Claude's Discretion

The user explicitly skipped these areas — Claude has flexibility during planning/execution:

- **README skeleton section list (BOOT-06):** which empty-header sections appear in the Phase 1 skeleton. Apply standard portfolio README structure (Hook → Findings preview → Architecture → Setup → Glossary → Methodology → Limitations → Attribution → Known Issues), with empty bodies. Match the structure FINDINGS.md will reference.
- **Audit notebook polish level (`00_data_audit.ipynb`):** internal-functional vs. recruiter-presentable. Default to "presentable" since FEATURES.md P2 keeps it in the repo as "shows pivot reasoning visibly". Use `_style.py` rcParams once they exist (Phase 3); for Phase 1, plain `df.describe()` + `seaborn.heatmap()` for the NaN profile is sufficient.
- **README hook rewrite timing (AUDIT-07):** the requirement says rewrite in Phase 1 to match the post-pivot framing. Default to writing a 2–3 sentence plain-English hook in Phase 1 that names the pivot ("public FTN exposes broader defensive tendencies — not coverage shells — and here's what 3 seasons reveal") with placeholder slots for headline numbers. Phase 4 fills the placeholders once findings exist.
- **NaN profile granularity (AUDIT-02):** by `play_type` is required (per ROADMAP success criterion 2). Adding a season-axis breakdown is optional polish; do it only if Phase 1 execution has slack.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (gsd-phase-researcher, gsd-planner) MUST read these before planning or implementing.**

### Project-level constraints (read first)

- `CLAUDE.md` — Locked stack, file-organization rules, audience voice, public-repo discipline. Non-negotiables.
- `.planning/PROJECT.md` — Vision, Out of Scope, Key Decisions table.
- `.planning/REQUIREMENTS.md` — BOOT-01..07 + AUDIT-01..07 acceptance criteria with exact pin versions and file paths.
- `.planning/ROADMAP.md` §Phase 1 — Phase boundary, success criteria, plan ordering (01-01 Bootstrap → 01-02 Audit, in-phase parallelism rules).

### Pivot rationale + research (read for context, not re-litigation)

- `.planning/research/SUMMARY.md` — Consolidated stack, "Open Questions Phase 1 Must Answer" §, pitfalls register, suggested phase structure. **Most important single doc for Phase 1 planning.**
- `.planning/research/STACK.md` — Full stack-pinning rationale, `numpy<2` constraint, `nfl_data_py` archival decision.
- `.planning/research/ARCHITECTURE.md` — Directory tree (defines BOOT-01 skeleton).
- `.planning/research/FEATURES.md` — P1/P2/P3 priorities, anti-features list (informs README skeleton tone).
- `.planning/research/PITFALLS.md` — 22 pitfalls; pitfalls #1, #3, #5, #6, #8, #9 directly govern Phase 1 deliverables.

### Original spec (rewritten in Phase 1 per AUDIT-06)

- `SPEC.md` — Original 8 business questions framed around Cover 0–6 / man-zone (which the public FTN data does NOT contain). AUDIT-06 rewrites these in-place to the post-pivot anchor dimensions chosen via D-01..D-04. Read before starting AUDIT-06; don't write to until anchor dimensions are locked from the audit notebook output.

### No external ADRs

The project does not use a `docs/decisions/adr-*.md` system. All decisions live in PROJECT.md (Key Decisions table) and these CONTEXT.md files. If Phase 1 surfaces a decision worth promoting, add it to PROJECT.md Key Decisions, not a new ADR.

</canonical_refs>

<code_context>
## Existing Code Insights

### Greenfield phase

The repo currently contains only `.git/`, `.gitignore`, `CLAUDE.md`, `SPEC.md`, `.planning/`, and `venv/`. There are no Python source files, no schema, no notebooks. Phase 1 lays the entire skeleton.

### Reusable assets

- **`venv/`** exists at repo root (Python 3.11, per CLAUDE.md `.python-version` requirement). BOOT-07 verifies a fresh-venv install passes; reuse the existing venv only if it's confirmed to be Python 3.11 and clean.
- **`.gitignore`** at repo root — small (455 bytes); BOOT-03 expands it to the full required entries (`data/raw/`, `*.db`, `.env*`, `__pycache__/`, `.ipynb_checkpoints/`, scratch files, `venv/`).
- **`CLAUDE.md`** — already documents the locked stack, file org, and audience voice. BOOT/AUDIT planning agents should treat this as a constraint document, not a starting point.
- **`SPEC.md`** — pre-pivot framing in plain markdown. AUDIT-06 rewrites the 8 business questions in place (or appends an addendum) once anchor dimensions are locked.

### Established patterns

There are no Python coding patterns yet — this phase establishes them. The `.planning/` workflow is established and committed; do not invent a parallel workflow system.

### Integration points

- **`.planning/phases/01-foundation-ftn-pivot-calibration/`** is where Phase 1's PLAN.md and execution artifacts land.
- **`SPEC.md`** is the integration point for AUDIT-06 (in-place rewrite of business questions to post-pivot anchor dimensions).
- **`README.md`** does not yet exist; BOOT-06 creates the skeleton, AUDIT-07 writes the hook.

</code_context>

<specifics>
## Specific Ideas

- **Hypothesis wording must be falsifiable.** Per D-08, write "Defenses blitz at >35% league-wide on 3rd-and-long" — not "We will look at blitz rates on 3rd-and-long". The hypothesis names what would falsify it.
- **The audit notebook is a recruiter-visible artifact.** It stays in the repo (per FEATURES.md P2) as proof of analytical rigor — "this candidate looked at the data before writing SQL". Don't treat it as scratch.
- **The 30% NaN cutoff is the rule, not a guideline.** If the audit shows `is_screen_pass` at 32% NaN on pass plays, it's out, even if it would make a great anchor. Do not relax silently — relaxation has its own decision (D-04: don't, document the gap instead).
- **`is_play_action` as a cross-cutting modifier means every claim in FINDINGS.md gets the option of a play-action split.** Implementation in Phase 3: each pre-registered situation's chi-square gets `is_play_action` as a stratifying variable when `play_type='pass'` and N permits.

</specifics>

<deferred>
## Deferred Ideas

- **README skeleton section ordering, audit notebook polish level, README hook rewrite timing** — user explicitly deferred area 4 to Claude's Discretion (see Decisions §Claude's Discretion). Captured there with default approach.
- **GitHub topics slate** (D-10) — deferred to Phase 4 / SHIP-03 with the working default (7-topic slate from REQUIREMENTS.md).
- **Bonferroni / BH correction** — not needed since slate is locked at 4 with one chi-square per situation. Surfaces only if Phase 3 expands beyond pre-registered situations (which the firewall prevents).
- **Per-season FTN NaN breakdown** — single-axis NaN profile (by `play_type`) is mandatory; per-season breakdown is optional polish. Note in `docs/ftn-schema-audit.md` if discovered seasonal differences materially affect the anchor choice.
- **`nflreadpy` migration** — already deferred to V2-LIB-01 in REQUIREMENTS.md.

</deferred>

---

*Phase: 01-foundation-ftn-pivot-calibration*
*Context gathered: 2026-04-29*
