# FTN Schema Audit (Phase 1 Pivot Calibration)

The 29 columns of the public FTN charting subset distributed via nflverse contain
zero coverage labels. The full Cover-0-through-6 / man-zone taxonomy is part of
FTN's paid product (`ftnfantasy.com/data`), not the CC-BY-SA subset. This audit
confirms the project's pivot to broader defensive tendencies — pressure,
play-fakery, and personnel/location — using the dimensions FTN does expose.

The audit pulled `nfl.import_ftn_data([2022, 2023, 2024])` against the live
nflverse CDN on 2026-04-29 and joined to `nfl.import_pbp_data` on
`(nflverse_game_id, nflverse_play_id)` with `validate='one_to_one'`. The join
matched 137,899 of 137,899 FTN rows against 148,591 pbp rows; observed
match rate was 0.9998 — well above the 0.95 floor specified by Pitfall #3.
Per-column NaN rates are persisted as `audit/ftn_null_profile.csv`.

## FTN column inventory (29 columns)

The live FTN frame returned 29 columns for 2022-2024, one more than the
28-column inventory documented in `.planning/research/PITFALLS.md` Pitfall #2.
The additional column is `n_defense_box` (a defensive-personnel context
column that appears NaN-clean across all play types). The full list:

```
ftn_game_id, nflverse_game_id, season, week, ftn_play_id, nflverse_play_id,
starting_hash, qb_location, n_offense_backfield, n_defense_box, is_no_huddle,
is_motion, is_play_action, is_screen_pass, is_rpo, is_trick_play,
is_qb_out_of_pocket, is_interception_worthy, is_throw_away, read_thrown,
is_catchable_ball, is_contested_ball, is_created_reception, is_drop,
is_qb_sneak, n_blitzers, n_pass_rushers, is_qb_fault_sack, date_pulled
```

None of these 29 columns label coverage shell or man-vs-zone. The pivot is
correct as designed.

## Selection rule (D-02 + D-01)

Drop any FTN column with >30% NaN on the relevant `play_type`. Among
survivors, curate for cross-category diversity across pressure / play-fakery /
personnel-location (the D-01 story tiebreaker). Pressure and play-fakery
columns are evaluated on `play_type='pass'` rows only (Pitfall #4 is explicit:
`n_blitzers` and `n_pass_rushers` are populated only on pass-context plays;
NaN on run plays is definitional, not a data-quality failure). Personnel /
location columns are evaluated on competitive plays
(`play_type IN ('pass','run')`) per the project-wide filtering convention.

The 30% cutoff is the rule, not a guideline (CONTEXT.md Specifics bullet 3).
A column at 31% NaN is dropped even if it would tell a great story.

## NaN rates for the 8 candidate dimensions

| Category | Column | Scope | NaN rate | Survives D-02 (<=30%)? |
|---|---|---|---|---|
| Pressure | n_blitzers | play_type='pass' | 0.000 | yes |
| Pressure | n_pass_rushers | play_type='pass' | 0.000 | yes |
| Play-fakery | is_play_action | play_type='pass' | 0.000 | yes |
| Play-fakery | is_screen_pass | play_type='pass' | 0.000 | yes |
| Play-fakery | is_rpo | play_type='pass' | 0.000 | yes |
| Personnel | qb_location | competitive plays | 0.001 | yes |
| Personnel | n_offense_backfield | competitive plays | 0.009 | yes |
| Personnel | starting_hash | competitive plays | 0.001 | yes |

All 8 candidates survive the 30% cutoff. Pitfall #4 is borne out: n_blitzers
and n_pass_rushers on `play_type='run'` are 100% NaN by design (FTN does not
chart pass-rusher counts on run plays). Filtering to pass plays before any
blitz-rate calculation is mandatory and is documented as the analytical
convention in `docs/analysis-plan.md`.

## Anchor selection (D-03 / D-04)

Per D-03, target 4 anchors with cross-category breadth. Because all 8
candidates survive the NaN gate, the selection is editorial, not mechanical
(D-01 story tiebreaker). The 4 chosen anchors are:

1. **n_blitzers** (Pressure / front, on `play_type='pass'`).
   The cleanest, most recruiter-recognizable pressure signal at 0.000 NaN.
   Drives the 3rd-and-long blitz-rate hypothesis (S1) and the situation-by-
   situation blitz-rate decomposition. Operational definition for the
   "blitz" boolean is `n_blitzers > 4` (5+ rushers on a pass, in standard
   nflfastR convention).

2. **n_pass_rushers** (Pressure / front, on `play_type='pass'`).
   The complementary pass-rush count covers four-down-line vs.
   five-or-more-rusher fronts independent of blitz, at 0.000 NaN. Used in
   the red-zone pressure-rate hypothesis (S2) and the 2nd-and-medium
   variance hypothesis (S4). Both pressure anchors ship together because
   pressure decisions are the load-bearing situational tendency the FTN
   subset exposes.

3. **is_play_action** (Play-fakery, on `play_type='pass'`).
   Per D-07, is_play_action is a cross-cutting modifier rather than a
   stand-alone slate item — every pre-registered situation gets a
   play-action vs. straight-dropback split where N permits. NaN is 0.000
   on pass plays, which makes the split feasible across all 4 situations.
   Including it in the anchor set names it explicitly so that the
   downstream Phase 3 chi-squares know to stratify on it.

4. **n_offense_backfield** (Personnel / location, on competitive plays).
   The cleanest personnel/location dimension at 0.009 NaN. Names the
   number of players in the backfield (single-back vs. two-back vs. empty),
   which is the single most observable pre-snap personnel signal in the
   public FTN subset. Used in the 1st-and-10 distribution baseline (S3)
   and the 2nd-and-medium variance hypothesis (S4). starting_hash is a
   weaker signal at the same NaN rate; qb_location is included only as a
   stratifier where the play-action split would otherwise overlap (under-
   center vs. shotgun is partially redundant with n_offense_backfield).

The other 4 candidates (is_screen_pass, is_rpo, qb_location, starting_hash)
remain available as exploratory or stratifier columns in
`analysis/01_exploratory.ipynb`. They are not headline anchors per the
4-situation firewall (D-05).

## Empty-category contingency (D-04)

All three categories — pressure, play-fakery, personnel/location — have
survivors at the 30% cutoff. D-04 contingency does not apply. The chosen
4-anchor set spans all three categories: 2 pressure + 1 play-fakery +
1 personnel.

## Cross-cutting modifier note (D-07)

Per D-07, is_play_action is a cross-cutting modifier across the 4
pre-registered situations (see `docs/analysis-plan.md`), not a separate
anchor. It is included in the chosen anchors here because it survives the
30% gate AND fits the cross-category breadth curation. Phase 3
implementation (`analysis/02_predictability_modeling.ipynb`) treats it as a
stratifier on `play_type='pass'` rows: each of the 4 situations produces a
play-action vs. straight-dropback split where both stratum sizes meet the
N>=30 baseline (per Pitfall #8 + STAT-07).

## Subsequent finding worth flagging for v2

The pbp frame returned by `nfl.import_pbp_data()` for 2022-2024 in 2026-04-29
contains `defense_man_zone_type` and `defense_coverage_type` columns sourced
from NFL Next Gen Stats data the nflverse community has merged into pbp since
the original research pass. These columns are 0.023 and 0.025 NaN on
`play_type='pass'` respectively — well below the 30% cutoff. They are NOT
part of the FTN charting subset; they live on the pbp side of the join. The
v1 plan stays as locked because: the project pivot decision has been made
in writing (D-09); the analysis plan and SPEC are pre-registered around
FTN-confirmed columns; and using ngs-derived coverage labels would re-open
the man-zone framing the project deliberately stepped away from.

This is a v2 candidate. The columns are publicly available, well-populated,
and would re-enable a portion of the original SPEC's coverage-shell framing.
A v2 audit should re-test the columns' definitions and inter-rater profile
before adopting them as analytical anchors. Tracked as a forward note for
PROJECT.md Evolution.

## Sample-size health for the 4 pre-registered situations

The joined frame has 61,047 pass plays and 44,931 run plays across 2022-2024.
This is well above the per-team-per-season N>=30 floor for tendency claims
and supports the N>=100 floor for "extreme" claims at the team x situation
level for all but the most fine-grained slices. Phase 3's `min_n_filter()`
helper is the enforcement gate; this audit only confirms that the upstream
volume is sufficient.
