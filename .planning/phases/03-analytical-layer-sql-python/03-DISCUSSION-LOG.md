# Phase 3: Analytical Layer (SQL + Python) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `03-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-04-30
**Phase:** 03-analytical-layer-sql-python
**Areas selected for discussion:** Predictability Index design, The 8-query slate, Chi-square + sensitivity targets
**Areas explicitly deferred to Claude's Discretion:** `_common.py` helper API

---

## Gray Area Selection

| Area | Description | Selected |
|------|-------------|----------|
| Predictability Index design | H/log(k) vs KL; input dimension; aggregation; 0-100 mapping; weighting; PA treatment (STAT-04, STAT-05) | ✓ |
| The 8-query slate | Filename slate alignment with hypotheses; QUERY-04 dimension; QUERY-08 reframe; header convention (QUERY-01..09) | ✓ |
| Chi-square + sensitivity targets | Hypothesis target; test scope; effect size; sensitivity check target (STAT-06, STAT-08) | ✓ |
| `_common.py` helper API | Connection helper; `min_n_filter` signature; SEED placement (STAT-01) | (deferred to Claude's Discretion) |

---

## Predictability Index design

### Q1: Normalization scheme for cell 1 of `02_predictability_modeling.ipynb`

| Option | Description | Selected |
|--------|-------------|----------|
| H/log(k) over fixed support (Recommended) | Bounded [0,1]; project research SUMMARY.md TL;DR endorses. | |
| KL from league baseline | Stats-rigorous; harder to explain. | |
| Both — H/log(k) headline + KL secondary check | H/log(k) drives leaderboard; KL appears as comparison table. | ✓ |

**User's choice:** Both — H/log(k) headline + KL secondary check.

**Notes (verbatim from user):** H/log(k) and KL measure different things. H/log(k) measures distribution concentration ("how predictable is this team in isolation"). KL measures deviation from the league baseline ("how different is this team from average"). For the headline predictability framing in the README and FINDINGS.md, concentration is the right concept — a team that always does what the league does is predictable, even though their KL would be zero. So H/log(k) leads.

KL earns its place as a secondary view because it answers an adjacent question that adds analytical depth: when a team scores high on H/log(k), KL tells us whether their predictability is the league pattern or a unique pattern. That's substantive.

Lock the validation gate for KL → H/log(k) at Spearman rank correlation ≥ 0.85. If the two rankings agree at that threshold or higher, KL serves as the methodological sensitivity check (STAT-08 contribution). If correlation drops below 0.85, the divergence is treated as a substantive finding and investigated, not papered over.

Notebook structure: cell 1 locks H/log(k) as the primary metric per CONTEXT mandate. KL is computed in a follow-on cell against the same per-team distributions, then surfaced as a comparison table with the Spearman correlation reported alongside.

### Q2: Input dimension feeding the entropy calculation

| Option | Description | Selected |
|--------|-------------|----------|
| Blitz boolean (n_blitzers > 4) (Recommended) | k=2 support; cleanest defensive choice; matches ftn-schema-audit.md operational definition. | ✓ |
| n_pass_rushers binned (k=3 or 4) | Richer pressure signal; harder bin-choice explanation. | |
| Composite blitz_bool + pressure_bool blend | Two-anchor average; risk of correlated double-counting. | |
| Per-anchor parallel indexes | One leaderboard per anchor; biggest narrative load. | |

**User's choice:** Blitz boolean (n_blitzers > 4).

### Q3: Per-team-per-situation matrix vs aggregate scalar

| Option | Description | Selected |
|--------|-------------|----------|
| Aggregate scalar per team (Recommended) | Drives hero chart; methodology appendix carries breakdown. | |
| Per-team-per-situation matrix as the artifact | Heatmap-only; loses the leaderboard narrative. | |
| Both — matrix in FINDINGS, scalar in hero chart | Per-team-per-situation heatmap in FINDINGS.md appendix; aggregate scalar drives hero chart leaderboard. | ✓ |

**User's choice:** Both — matrix in FINDINGS methodology appendix + aggregate scalar in hero chart.

### Q4: 0–100 mapping

| Option | Description | Selected |
|--------|-------------|----------|
| (1 − H/log(k)) × 100 (Recommended) | High score = more predictable; intuitive for non-football recruiter narrative. | ✓ |
| H/log(k) × 100 | High score = more random; counterintuitive for "predictability" framing. | |
| Min-max scaled across the 32 teams | Pure ranking; positional, not theoretical. | |

**User's choice:** (1 − H/log(k)) × 100.

### Q5: Aggregate scalar weighting

| Option | Description | Selected |
|--------|-------------|----------|
| Sample-size weighted (Recommended) | Standard meta-analytic; S3 dominates due to its ~41k league plays. | |
| Equal-weighted across the 4 situations | Each situation 1/4 weight; treats all 4 as equally important. | |
| Sample-size weighted with min-N gate | Weighted, but per-(team × situation) below floor are dropped not down-weighted. | ✓ |

**User's choice:** Sample-size weighted with min-N gate at N≥30 (project-wide baseline tier).

### Q6: is_play_action treatment in the index

| Option | Description | Selected |
|--------|-------------|----------|
| Ignore at the index level (Recommended) | PA stays as Phase 1 D-07 stratifier for chi-square + FINDINGS narrative only. | ✓ |
| Stratify within the index | 4 situations × 2 PA strata = 8 sub-indexes per team; small-N risk. | |
| Stratify but only as a parallel sensitivity index | Headline ignores PA; PA-stratified runs as appendix. | |

**User's choice:** Ignore at the index level.

---

## The 8-query slate

### Q1: Slate structure

| Option | Description | Selected |
|--------|-------------|----------|
| Keep placeholder slate, queries are rollup MATERIALS (Recommended) | Notebooks compute hypothesis tests; queries organized by domain. | |
| Realign 1:1 with hypotheses | Per-situation queries plus 4 supporting; biggest churn. | |
| Hybrid: keep most names, ensure each situation is addressable | Minimal renaming; expand QUERY-02 to all 4 situations; reframe QUERY-08 cross-season. | ✓ |

**User's choice:** Hybrid — keep most placeholder names, ensure each pre-registered situation is addressable.

### Q2: QUERY-04 (EPA allowed by <dim>) dimension target

| Option | Description | Selected |
|--------|-------------|----------|
| Blitz boolean (n_blitzers > 4) (Recommended) | Mirrors predictability index input; cleanest "do these tendencies work?" narrative. | ✓ |
| n_pass_rushers >= 5 heavy-pressure boolean | Wider net than blitz boolean; partly redundant. | |
| n_offense_backfield (single-back vs multi-back) | Personnel anchor; off-mainstream from pressure framing. | |
| Multiple dimensions in one query | Long-form rollup with `dimension` rows. | |

**User's choice:** Blitz boolean (n_blitzers > 4).

### Q3: QUERY-08 reframe

| Option | Description | Selected |
|--------|-------------|----------|
| Cross-season trend across 2022-2025 (Recommended) | D-10 four-season scope narrative; recruiter-friendly; current. | ✓ |
| Keep within-season week-over-week drift | More technical; harder to explain in 1 sentence. | |
| Both — split into QUERY-08 + 9th query | Adds artifact; exceeds 8-query slate. | |

**User's choice:** Cross-season trend across 2022-2025.

### Q4: SQL query header convention

| Option | Description | Selected |
|--------|-------------|----------|
| Structured sections (Recommended) | 6-section comment block: Question / Filter / Result shape / Hypothesis / Caveats / N expected. | ✓ |
| Prose docstring | 1 paragraph; harder to grep. | |
| Hybrid — short prose + result shape table | 2–3 sentence prose + result-shape pipe-list. | |

**User's choice:** Structured 6-section comment block.

---

## Chi-square + sensitivity targets

### Q1: Chi-square headline target

| Option | Description | Selected |
|--------|-------------|----------|
| PA cross-cutting on S1: blitz × is_play_action on 3rd-and-long (Recommended) | Activates D-07 cross-cutting modifier; both anchor categories feature; recruiter-readable. | ✓ |
| S2-H1: pressure × red_zone on competitive pass plays | Big sample on both sides; tests "do defenses pressure more in red zone?". | |
| S1-H1 reframed: blitz × in_S1 across all competitive pass plays | Reframe of >35% league benchmark hypothesis. | |

**User's choice:** PA cross-cutting on S1.

### Q2: Test scope

| Option | Description | Selected |
|--------|-------------|----------|
| League-aggregate 2×2 (Recommended) | Single contingency; matches analysis-plan.md hypothesis phrasing. | ✓ |
| Team-level 32×2 (variance test) | Omnibus team-variance test; different statistical question. | |
| Both — league as headline, team-level as supplemental | Adds 1 cell to the notebook. | |

**User's choice:** League-aggregate 2×2.

### Q3: Effect size measure

| Option | Description | Selected |
|--------|-------------|----------|
| Cramér's V (Recommended) | Standard chi-square effect size; reads as abstract association strength. | |
| Phi coefficient | Equivalent to Cramér's V for 2×2 specifically; signed. | |
| Odds ratio + 95% CI | Football-analytics-native; multiplicative interpretation. | ✓ |

**User's choice:** Odds ratio + 95% CI.

### Q4: STAT-08 sensitivity check target

| Option | Description | Selected |
|--------|-------------|----------|
| Predictability Index leaderboard (Recommended) | Per-team rank delta + Spearman ρ between filtered vs unfiltered universes. | ✓ |
| The chi-square headline test | Re-run 2×2 on both universes; report test stat / p-value / OR / CI delta. | |
| Both — PI leaderboard primary, chi-square as secondary | Methodology rigor maxed; biggest notebook footprint. | |

**User's choice:** Predictability Index leaderboard.

---

## Claude's Discretion (areas user explicitly deferred)

- `_common.py` connection helper API
- `min_n_filter()` signature
- `SEED` placement
- `_style.py` color palette specifics
- `01_exploratory.ipynb` scope beyond the minimum requirement
- QUERY-09 window/CTE/cross-source-join distribution (slate-collective vs per-query)
- QUERY-07 exact result column schema for the predictability raw inputs

Defaults documented in `03-CONTEXT.md` under `Claude's Discretion`.

---

## Deferred Ideas (carried forward to v2 / future phases)

See `03-CONTEXT.md` `<deferred>` section for the full list. Highlights:

- Per-anchor parallel predictability indexes (n_pass_rushers, n_offense_backfield)
- PA-stratified predictability index
- Team-level 32×2 omnibus chi-square
- Cramér's V alongside odds ratio
- Within-season week-over-week drift query (REQUIREMENTS.md placeholder; reframed for v1)
- Per-team color palette in `_style.py` for non-hero charts
