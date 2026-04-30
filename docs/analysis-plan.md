# Pre-registered Analysis Plan

This document locks the situational slate before any Phase 3 query runs.
Anything outside the 4 situations below stays in
`analysis/01_exploratory.ipynb` and never appears as a headline insight in
`findings/FINDINGS.md`. The strict firewall prevents the multiple-comparisons
trap (PITFALLS.md Pitfall #9): scanning 32 teams x N situations and
reporting "extreme" cells without correction is data dredging, not analysis.

The 4-situation slate, the cross-cutting modifier, and every hypothesis
threshold are locked here on 2026-04-29. Phase 3 chi-squares may be
re-stated in clearer language but their predictions are not movable
post-hoc.

## Anchor Dimensions

Each hypothesis claims findings on one of the anchor defensive dimensions
named in `docs/ftn-schema-audit.md`: `n_blitzers` and `n_pass_rushers`
(pressure, evaluated on `play_type='pass'`), `is_play_action` (play-fakery,
cross-cutting), and `n_offense_backfield` (personnel, evaluated on
competitive plays). The cross-cutting `is_play_action` modifier (D-07) is
applied as a stratifier within each situation on `play_type='pass'` rows
when N permits.

## Situation 1: 3rd-and-long

**Filter:** `down = 3 AND ydstogo >= 7` on `competitive_plays` (Phase 2 view).

**Rationale:** Pressure / blitz showcase, high recruiter recognition (D-06).
The 3rd-and-long down-set is the most legible defensive-tendency situation
to a non-football reader and is the canonical pressure showcase in the
public sports-analytics literature.

**Hypotheses (falsifiable):**

- H1: League-wide blitz rate (`n_blitzers > 4`) on 3rd-and-long exceeds 35%
  over 2022-2025. **Falsified if** observed league-wide rate <= 35% with
  N >= 1,000 (the threshold is met across 4 seasons of every team's
  3rd-and-long pass plays; sample size is not the gate).

- H2: At least 3 teams have a blitz rate > 50% on 3rd-and-long with N >= 100
  per team across 2022-2025. **Falsified if** fewer than 3 teams meet both
  thresholds.

## Situation 2: Red zone

**Filter:** `yardline_100 <= 20` on `competitive_plays`.

**Rationale:** Tendency contraction, easy to interpret (D-06). Red-zone
playcalling compresses the field and forces defenses into more discrete
choices, a high-information situation for tendency analysis.

**Hypotheses (falsifiable):**

- H1: League-wide pressure rate (`n_pass_rushers >= 5`) inside the 20
  differs from the league-wide pressure rate elsewhere by at least 5
  percentage points (in either direction) over 2022-2025 with N >= 1,000
  on each side of the comparison. **Falsified if** the absolute gap is
  < 5pp.

- H2: At least 1 team's red-zone pressure rate is "extreme" (> 75% one
  look) with N >= 100 across 2022-2025. **Falsified if** no team meets
  both thresholds.

## Situation 3: 1st-and-10

**Filter:** `down = 1 AND ydstogo = 10` on `competitive_plays`.

**Rationale:** Neutral baseline, highest sample size, anchors league-
deviation comparators (D-06). 1st-and-10 is the most-played situation in
football and the natural denominator against which other situations are
compared.

**Hypotheses (falsifiable):**

- H1: League-wide pass rate on 1st-and-10 is between 50% and 60% over
  2022-2025 (consistent with the public nflfastR EPA literature's
  reported range with N >= 10,000). **Falsified if** observed rate is
  outside [50%, 60%].

- H2: 1st-and-10 has the highest sample size of the 4 pre-registered
  situations: N(S3) > max(N(S1), N(S2), N(S4)). **Falsified if** any
  other situation has more competitive plays.

## Situation 4: 2nd-and-medium

**Filter:** `down = 2 AND ydstogo BETWEEN 3 AND 6` on `competitive_plays`.

**Rationale:** Strongest team-by-team variance, richest signal for the
predictability index (D-06). The 2nd-and-medium down-set has the most
between-team dispersion of run-vs-pass rate in the nflfastR EPA literature,
making it the highest-signal situation for the predictability index.

**Hypotheses (falsifiable):**

- H1: Team-level standard deviation of the chosen pressure-anchor rate
  on 2nd-and-medium exceeds the team-level standard deviation on
  1st-and-10. Operationally: stddev across 32 teams of
  team-blitz-rate(S4) > stddev across 32 teams of team-blitz-rate(S3).
  **Falsified if** sigma(S4) <= sigma(S3).

- H2: At least 5 teams have N >= 100 plays on 2nd-and-medium across
  2022-2025 with `n_offense_backfield` populated. **Falsified if** fewer
  than 5 teams meet both thresholds.

## Cross-cutting Modifier: is_play_action

Per D-07, `is_play_action` is applied as a stratifier within each situation
on `play_type='pass'` rows where N permits. For each of the 4 situations,
the Phase 3 analysis produces a play-action vs. straight-dropback split;
the split is reported only when both stratum sizes meet the N >= 30
baseline (PITFALLS.md Pitfall #8 + STAT-07). This integrates play-fakery
analysis into every claim without inflating the slate from 4 to 5
pre-registered situations.

The play-action stratification answers an additional set of falsifiable
sub-hypotheses without redefining the slate. Example: within S1
(3rd-and-long), Phase 3 reports league blitz rate against play-action
versus league blitz rate against straight dropback. The pre-registered
prediction is that the gap is at least 5 percentage points; **Falsified if**
the absolute gap is below 5pp with N >= 100 on each side.

## Firewall

FINDINGS.md headline insights MUST come from this 4-situation slate.
Exploratory work, including any scan across additional situations, stays
in `analysis/01_exploratory.ipynb` and is labeled "Exploratory; not a
headline finding." Bonferroni / BH correction is not applied because the
slate is locked at 4 with one chi-square per situation; correction becomes
mandatory only if the slate expands beyond pre-registered situations
(which the firewall prevents). If a Phase 3 exploratory pass surfaces a
candidate insight outside this slate, the path is to document it as
exploratory in `01_exploratory.ipynb` and defer to v2, NOT to retroactively
add it to FINDINGS.md.

## Sample-size discipline

Every claim in FINDINGS.md states N inline. Tiered thresholds (per
CLAUDE.md "Project Realities to Remember"):

- **N >= 30** for any tendency claim.
- **N >= 100** for any "extreme" claim (> 75% one look).
- **N >= 15** allowed only with explicit narrative low-N flag.

Implementation: `analysis/_common.py:min_n_filter()` (Phase 3 / STAT-01)
is applied to every analytical claim. The helper raises if a claim is
emitted on a sample below its tier; the narrative flag for the N >= 15
exception lives in the FINDINGS.md cell that emits the claim, not in the
helper.

## Why these 4 and not 5

The slate sits at 4 because (a) one chi-square per situation times one
Wilson CI per claim across 32 teams compounds the family-wise error rate
quickly even at 4, and the locked slate is the substitute for Bonferroni
correction; (b) the cross-cutting `is_play_action` modifier turns each
of the 4 into 2 sub-claims (play-action vs. dropback), which already
yields 8 stratified comparisons per anchor; (c) adding a 5th situation
would require a recomputed correction or a documented justification for
why the family-wise rate is acceptable, neither of which is in scope
for v1.

## Pre-registered: 2026-04-29

This plan is locked at the start of Phase 3 / STAT-04. Any change after
this date requires a documented decision in PROJECT.md Key Decisions and
a SUMMARY.md note in the affected plan.
