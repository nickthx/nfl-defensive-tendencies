# FTN Schema Audit (Phase 1 Pivot Calibration)

The 29 columns of the public FTN charting subset distributed via nflverse contain
zero coverage labels. The full Cover-0-through-6 / man-zone taxonomy is part of
FTN's paid product (`ftnfantasy.com/data`), not the CC-BY-SA subset. This audit
confirms the project's pivot to broader defensive tendencies (pressure,
play-fakery, and personnel/location) using the columns FTN does include.

I pulled `nfl.import_ftn_data([2022, 2023, 2024, 2025])` against the live
nflverse CDN on 2026-04-29 and joined to `nfl.import_pbp_data` on
`(nflverse_game_id, nflverse_play_id)` with `validate='one_to_one'`. The join
matched 185,215 of 185,215 FTN rows against 197,362 pbp rows. The observed
match rate was 0.9999, well above the 0.95 floor required for the join to be
analytically trustworthy. Per-column NaN rates are in `audit/ftn_null_profile.csv`.

## FTN column inventory (29 columns)

The frame has 29 columns across 2022-2025, one more than the 28-column inventory
documented in the project's pre-audit research notes. The additional column is
`n_defense_box`, a defensive-personnel context column that is NaN-clean
across all play types. The 2025 season pulled clean against the same schema:
no columns added or removed between 2024 and 2025, so the 4-season frame
binds without conditional handling. The full list:

```
ftn_game_id, nflverse_game_id, season, week, ftn_play_id, nflverse_play_id,
starting_hash, qb_location, n_offense_backfield, n_defense_box, is_no_huddle,
is_motion, is_play_action, is_screen_pass, is_rpo, is_trick_play,
is_qb_out_of_pocket, is_interception_worthy, is_throw_away, read_thrown,
is_catchable_ball, is_contested_ball, is_created_reception, is_drop,
is_qb_sneak, n_blitzers, n_pass_rushers, is_qb_fault_sack, date_pulled
```

None of these 29 columns label coverage shell or man-vs-zone.

## Selection rule

Drop any FTN column with >30% NaN on the relevant `play_type`. Among
survivors, curate for cross-category diversity across pressure, play-fakery,
and personnel-location (the story tiebreaker, since the cutoff alone may
leave more than 4 candidates). Use `play_type='pass'` for pressure and
play-fakery columns: `n_blitzers` and `n_pass_rushers` are populated only on
pass plays, so NaN on run plays is by design: FTN doesn't chart pass-rusher
counts on runs. Personnel and location columns are evaluated on competitive
plays (`play_type IN ('pass','run')`), the project-wide filtering convention.

The 30% cutoff is hard. A column at 31% NaN is dropped, full stop.

## NaN rates for the 8 candidate dimensions

| Category | Column | Scope | NaN rate | Survives 30% cutoff? |
|---|---|---|---|---|
| Pressure | n_blitzers | play_type='pass' | 0.000 | yes |
| Pressure | n_pass_rushers | play_type='pass' | 0.000 | yes |
| Play-fakery | is_play_action | play_type='pass' | 0.000 | yes |
| Play-fakery | is_screen_pass | play_type='pass' | 0.000 | yes |
| Play-fakery | is_rpo | play_type='pass' | 0.000 | yes |
| Personnel | qb_location | competitive plays | 0.001 | yes |
| Personnel | n_offense_backfield | competitive plays | 0.009 | yes |
| Personnel | starting_hash | competitive plays | 0.001 | yes |

All 8 candidates survive the 30% cutoff. On run plays, n_blitzers and
n_pass_rushers are 100% NaN by design (FTN doesn't chart pass-rusher counts
on runs). Every blitz-rate calculation in this project filters to pass plays
first; the convention is locked in `docs/analysis-plan.md`.

## Anchor selection

Target 4 anchors with cross-category breadth. All 8 candidates survive the
NaN gate, so the selection is editorial: a story tiebreaker, not a NaN
tiebreaker. The 4 chosen anchors:

1. **n_blitzers** (Pressure / front, on `play_type='pass'`).
   The cleanest, most recruiter-recognizable pressure signal at 0.000 NaN.
   Drives the 3rd-and-long blitz-rate hypothesis and the situation-by-
   situation blitz-rate decomposition. Operational definition for the
   "blitz" boolean is `n_blitzers > 0` (any extra rusher above the base
   4-man defensive front, per FTN column semantics — see calibration note
   below).

### Calibration note (Phase 3 post-execution)

The original operational definition reused the standard nflfastR convention where `n_pass_rushers >= 5` (5 or more total rushers) defines a blitz. That convention applies to nflfastR's `n_pass_rushers` column, which is a total rusher count. FTN's `n_blitzers` is a different column with a different encoding: it counts extra rushers above the base 4-man defensive front (max observed value = 6 across 4 seasons). The nflfastR-style threshold applied to the FTN column returned only 7 blitz plays out of 58,178 competitive pass plays (0.012%) — analytically degenerate. Any `n_blitzers >= 1` means a blitz was sent; the corrected boolean is `n_blitzers > 0`. Under the corrected boolean, the league-wide blitz rate on competitive pass plays is 29.45% (N=17,131 / 58,178), consistent with public sports-analytics benchmarks. See `.planning/STATE.md` D-14 for the full audit trail.

2. **n_pass_rushers** (Pressure / front, on `play_type='pass'`).
   The complementary pass-rush count covers four-down-line vs.
   five-or-more-rusher fronts independent of blitz, at 0.000 NaN. Used in
   the red-zone pressure-rate hypothesis and the 2nd-and-medium variance
   hypothesis. Both pressure anchors ship together because pressure
   decisions are the load-bearing situational tendency the FTN subset
   covers.

3. **is_play_action** (Play-fakery, on `play_type='pass'`). NaN is 0.000
   on pass plays, which makes a play-action vs. straight-dropback split
   feasible inside every pre-registered situation. It functions as a
   cross-cutting stratifier rather than a stand-alone slate item, so each
   situation produces a stratified comparison wherever both strata clear
   N>=30. The analytical convention is locked in `docs/analysis-plan.md`;
   Phase 3 implements it in `analysis/02_predictability_modeling.ipynb`.

4. **n_offense_backfield** (Personnel / location, on competitive plays).
   The cleanest personnel/location dimension at 0.009 NaN. Names the
   number of players in the backfield (single-back vs. two-back vs. empty),
   which is the single most observable pre-snap personnel signal in the
   public FTN subset. Used in the 1st-and-10 distribution baseline and the
   2nd-and-medium variance hypothesis. starting_hash is a weaker signal at
   the same NaN rate; qb_location is included only as a stratifier where
   the play-action split would otherwise overlap (under-center vs. shotgun
   is partially redundant with n_offense_backfield).

The 4-anchor pick spans all three categories (2 pressure, 1 play-fakery,
1 personnel), so the empty-category contingency in the analysis plan does
not apply.

The other 4 candidates (is_screen_pass, is_rpo, qb_location, starting_hash)
remain available as exploratory or stratifier columns in
`analysis/01_exploratory.ipynb`. They are not headline anchors: the
4-situation firewall in `docs/analysis-plan.md` keeps headline insights
inside the pre-registered slate.

## Subsequent finding worth flagging for v2

The pbp frame returned by `nfl.import_pbp_data()` for 2022-2025 on 2026-04-29
contains `defense_man_zone_type` and `defense_coverage_type` columns sourced
from NFL Next Gen Stats data the nflverse community has merged into pbp since
the original research pass. These columns are 0.023 and 0.025 NaN on
`play_type='pass'`, well below the 30% cutoff. They are NOT part of the FTN
charting subset; they're on the pbp side of the join.

The v1 plan stays locked because the pivot is in writing and the analysis
plan is pre-registered around FTN-confirmed columns. Adopting NGS-derived
coverage labels mid-stream would re-open the man-zone framing this project
deliberately stepped away from.

This is a v2 candidate. The columns are publicly available, well-populated,
and would re-enable a portion of the original SPEC's coverage-shell framing.
A v2 audit should re-test the columns' definitions and inter-rater profile
before adopting them as analytical anchors. Logged as a v2 candidate.

## Sample-size health for the 4 pre-registered situations

The four-season pull (2022 through Super Bowl LX in February 2026) has
80,782 pass plays and 59,824 run plays in the joined frame, a raw
play-type-only universe of 140,606 plays.

The analytical universe is smaller. Phase 2's `competitive_plays` view
(`schema/03_views.sql`) further filters to win-probability between 0.05
and 0.95, excludes overtime, and excludes the end-of-half hurry-up
(`NOT (qtr IN (2,4) AND half_seconds_remaining <= 120)`). The full
predicate stack trims roughly 25%, leaving 105,556 competitive plays. This
is the denominator every Phase 3 analytical query reads from. The trim removes
blowout garbage-time, overtime small-sample anomalies, and end-of-half
desperation playcalling, all of which would distort tendency analysis.
Phase 3's predictability scoring and team-by-situation slicing both treat
the post-filter 105,556-row view as the analytical universe; the raw
140,606 figure is referenced only inside STAT-08's "with vs without
filter" sensitivity check.

Against the live `competitive_plays` view, the four pre-registered
situations return 9,925 (3rd-and-long), 15,559 (red zone), 41,901
(1st-and-10), and 10,513 (2nd-and-medium). All four sit well above the
per-team-per-season N>=30 floor for tendency claims and the N>=100 floor
for "extreme" claims at the team-by-situation level. The smallest situation
(3rd-and-long) divided across 32 teams and 4 seasons leaves an average of
~78 team-season plays, comfortable for the locked sample-size discipline.
Phase 3's `min_n_filter()` helper is the enforcement gate.
