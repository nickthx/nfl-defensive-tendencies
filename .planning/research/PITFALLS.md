# Pitfalls Research

**Domain:** Python + SQLite + Jupyter tabular data analytics, `nfl_data_py` (FTN + nflfastR), NFL defensive tendency analysis, public GitHub portfolio piece for entry-level data-analyst applications
**Researched:** 2026-04-29
**Confidence:** HIGH for `nfl_data_py` / FTN schema and ecosystem facts (verified via Context7, nflverse data dictionaries, GitHub issues, PyPI). MEDIUM for FTN per-column NaN rates (rates not published — must be measured in Phase 1 audit). HIGH for portfolio / repo-discipline pitfalls.

---

## Critical Pitfalls

### Pitfall 1: `nfl_data_py` is archived — the project is built on a deprecated package

**What goes wrong:**
The SPEC and PROJECT.md both name `nfl_data_py` as the data layer. The repo was **archived on 2025-09-25** and the README explicitly tells users to switch immediately to `nflreadpy`. A recruiter who clones the repo a year from now will see "this package is deprecated" stamped across the docs, and any unfixed bugs (e.g. open issue #122 — install fails on Python 3.13) stay unfixed forever. [VERIFIED: GitHub nflverse/nfl_data_py archived banner; GitHub issue #122; PyPI last release 0.3.3, 2024-09-20]

**Why it happens:**
Training-era documentation and most NFL-analytics tutorials still reference `nfl_data_py`. The pivot to `nflreadpy` (released 2025) is recent enough that it's easy to miss without checking GitHub directly. [VERIFIED: nflreadpy v0.1.5 released 2025-11-19]

**How to avoid:**
- **Decision required in Phase 1 audit:** stay on `nfl_data_py` (frozen, install-tested, accept deprecation warning) OR migrate to `nflreadpy` (active, polars-native, requires `.to_pandas()` conversion). The SPEC currently mandates the former.
- If staying on `nfl_data_py`: pin exact version `nfl-data-py==0.3.3` in `requirements.txt`, document the deprecation in the README ("This portfolio uses the archived `nfl_data_py` 0.3.3 — equivalent migration to `nflreadpy` is documented in `docs/migration.md` for production use"). This turns a weakness into a signal that the candidate knows the ecosystem.
- If migrating: every notebook / ETL script uses `nflreadpy` and converts polars→pandas at the boundary. SQL/pandas analysis code is unchanged.

**Warning signs:**
- Recruiter (or you) opens the GitHub repo for `nfl_data_py` and sees "This repository is archived" banner.
- `pip install nfl_data_py` emits a deprecation warning at import.
- Issue tracker shows unaddressed bugs from late 2024 / 2025.

**Phase to address:**
Phase 1 (FTN schema audit). The audit phase MUST resolve this decision before any ETL is written.

---

### Pitfall 2: FTN nflverse subset does NOT contain Cover 0/1/2/3/4/6 or man/zone labels

**What goes wrong:**
The SPEC's headline business questions ("Which teams run the most Cover 3 on 3rd-and-long?") are not answerable from the public FTN charting data. The nflverse-distributed FTN subset has **28 columns and zero coverage labels**. The full Cover-0-through-6 / man/zone taxonomy is part of FTN's **paid product** (`ftnfantasy.com/data`), not the CC-BY-SA subset published through nflverse. [VERIFIED: nflreadr FTN data dictionary lists 28 columns: ftn_game_id, nflverse_game_id, season, week, ftn_play_id, nflverse_play_id, starting_hash, qb_location, n_offense_backfield, is_no_huddle, is_motion, is_play_action, is_screen_pass, is_rpo, is_trick_play, is_qb_out_of_pocket, is_interception_worthy, is_throw_away, read_thrown, is_catchable_ball, is_contested_ball, is_created_reception, is_drop, is_qb_sneak, n_blitzers, n_pass_rushers, is_qb_fault_sack, date_pulled. None contain coverage/man/zone information.]

**Why it happens:**
SPEC was written before the schema audit. FTN's marketing copy says "FTN's expert charting team … defensive coverages" which describes the paid product. The free subset was negotiated for nflverse and excludes the labeling that's commercially valuable.

**How to avoid:**
- **This is THE Phase 1 outcome.** Phase 1 must explicitly print `nfl.see_pbp_cols()` and the column list of `nfl.import_ftn_data([2024])` and document the result in `docs/ftn-schema-audit.md` before any analysis is designed.
- Project pivots (per the SPEC's stated pivot path) to the **defensive dimensions FTN actually does provide**: `n_blitzers`, `n_pass_rushers`, `n_offense_backfield` (offensive personnel proxy), `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location` (under-center vs. shotgun pre-snap), `starting_hash`. These still answer the SPEC's underlying business questions ("which teams are most predictable on 3rd-and-long?") — just on different axes (blitz rate, pressure tendency, personnel-vs-formation).
- The repo name (`nfl-coverage-tendencies`) and findings narrative are **calibrated post-audit** per SPEC — do NOT lock the public repo name until Phase 1 completes.

**Warning signs:**
- Drafted SQL queries reference `coverage`, `cover_type`, `man_zone`, `coverage_shell` — none of these columns exist.
- Findings narrative or chart titles use "Cover 3" / "Cover 2" without a defined data source — they're ghost-written from domain knowledge, not data.

**Phase to address:**
Phase 1 (FTN schema audit) — blocking decision. ETL phase is gated on this audit's output.

---

### Pitfall 3: FTN join keys are `nflverse_game_id` / `nflverse_play_id`, NOT `game_id` / `play_id`

**What goes wrong:**
A naïve `pd.merge(ftn_df, pbp_df, on=['game_id', 'play_id'])` returns zero rows or — worse — a silently mis-joined dataframe if column names happen to coincide loosely. FTN exposes both `ftn_game_id` (FTN-internal) and `nflverse_game_id` (the join key). The corresponding play-level keys are `ftn_play_id` and `nflverse_play_id`. nflfastR's pbp uses `game_id` and `play_id`, but `game_id` in pbp matches `nflverse_game_id` in FTN. [VERIFIED: nflreadr FTN data dictionary lists ftn_game_id, nflverse_game_id, ftn_play_id, nflverse_play_id]

**Why it happens:**
The dual-ID design is for traceability — FTN keeps its own IDs while exposing a join key for nflverse. Anyone skimming the FTN dataframe and seeing `ftn_game_id` first will reach for it.

**How to avoid:**
- ETL `join_and_normalize.py` MUST use:
  ```python
  merged = pbp.merge(
      ftn,
      left_on=['game_id', 'play_id'],
      right_on=['nflverse_game_id', 'nflverse_play_id'],
      how='left',  # keep all pbp; FTN may not chart every play
      validate='one_to_one'  # raises if join is wrong
  )
  ```
- Drop `ftn_game_id` and `ftn_play_id` after the join; keep `game_id` / `play_id` as the canonical play key.
- Assert on join match rate: `assert merged['nflverse_play_id'].notna().mean() > 0.95` (FTN should chart >95% of regular-season offensive plays). Below threshold = something's wrong with the join.

**Warning signs:**
- Empty merge result.
- Merged dataframe has fewer rows than `pbp` (suggests inner join applied accidentally).
- Merged dataframe has DOUBLE the rows of `pbp` (key collision — `validate='one_to_one'` would catch this).
- FTN columns are all NaN after merge (keys didn't match — silent failure with `how='left'` and no validation).

**Phase to address:**
Phase 2 (ETL) — encode in `etl/join_and_normalize.py` with explicit `validate=` and a row-count assertion.

---

### Pitfall 4: FTN `n_blitzers` / `n_pass_rushers` are populated only on pass-relevant plays — NaN on runs is expected, not a data quality issue

**What goes wrong:**
A blitz-rate analysis like `df['n_blitzers'].mean()` over all plays underweights blitzing because run plays have NaN for these columns. Worse — a chi-square test of "blitz rate by down" silently drops every run play and reports a misleading sample size.

**Why it happens:**
FTN charts pass-rusher counts on plays where there's a backfield to count rushers against — pass attempts and dropbacks. Run plays don't get a meaningful `n_pass_rushers`. This is a definitional NaN, not a data-quality NaN. [VERIFIED via FTN dictionary semantics: n_blitzers/n_pass_rushers are pass-context fields; INFERRED that NaN rate maps to non-pass plays — Phase 1 audit MUST measure the actual NaN-by-play_type breakdown.]

**How to avoid:**
- Phase 1 audit: produce an `audit/ftn_null_profile.csv` showing `% NaN` for every FTN column, broken down by `play_type` (pass / run / no_play / qb_kneel / qb_spike). Document the expected-vs-suspicious nulls in `docs/ftn-schema-audit.md`.
- All blitz/rush analyses filter to `pbp.play_type == 'pass'` first, THEN compute the rate. Document this filter in every notebook cell that uses these columns.
- For the predictability score: define each "situation" as the filter scope explicitly (e.g. "pass-context predictability" vs. "all-plays predictability"). Don't mix.

**Warning signs:**
- Notebook has `df['n_blitzers'].mean()` with no upstream `play_type == 'pass'` filter.
- Reported sample sizes don't reconcile across cells (chi-square shows N=300 for one team, descriptive stats show N=900 — silent NaN dropping).
- `df['n_blitzers'].isna().sum()` is suspiciously close to the number of rush plays.

**Phase to address:**
Phase 1 (audit produces null profile); Phase 3 (analysis notebooks enforce explicit filtering with documented rationale).

---

### Pitfall 5: FTN has no pre-snap-vs-post-snap distinction except `qb_location`

**What goes wrong:**
SPEC asks "what coverage does the defense show pre-snap vs. play post-snap?" — FTN cannot answer this because (a) no coverage label exists at all, and (b) only `qb_location` is explicitly labeled as pre-snap in the dictionary. Every other field describes the play as it unfolded. [VERIFIED: FTN data dictionary explicitly marks only `qb_location` as pre-snap.]

**Why it happens:**
The pre-snap show / post-snap rotate distinction is a video-charting / tracking-data concept (Big Data Bowl tracking enables it). FTN's tabular nflverse subset doesn't carry that granularity.

**How to avoid:**
- Drop the "pre-snap shown coverage vs. played coverage" angle from the business questions in Phase 1.
- Reframe the analysis as "play-level defensive snapshot" and explicitly disclaim in FINDINGS.md: *"This dataset captures the defensive look as charted post-snap. Pre-snap disguise / rotation is not labeled in the public FTN subset and is not analyzed."*
- The disclaimer is itself a recruiter signal — it shows the candidate knows the limit of their data.

**Warning signs:**
- A query named `pre_snap_vs_post_snap_coverage.sql` in the queries/ directory (impossible to write).
- FINDINGS.md text describing "what the defense disguised" without a column reference.

**Phase to address:**
Phase 1 (scope this out before queries are designed).

---

### Pitfall 6: Garbage time, 2-minute drill, and end-of-half plays distort tendency claims

**What goes wrong:**
A claim like "Team X blitzes on 28% of 3rd-and-long" mixes (a) competitive-game 3rd-and-longs where the defense calls its real package and (b) garbage-time 3rd-and-longs where they're in prevent and the offense is in 4-vertical desperation. The mixed sample tells you nothing about the coordinator's tendency.

**Why it happens:**
nflfastR's pbp includes every play. EPA convention in the analytics community is to filter on `wp BETWEEN 0.05 AND 0.95` (or `0.10–0.90`) to exclude blowouts, but this filter is not applied by default. [VERIFIED: nflfastR EPA analysis convention via Open Source Football, rbsdm.com Baldwin/Carl methodology.]

**How to avoid:**
- Define a project-wide `competitive_play` filter applied in the SQL view layer, not ad-hoc per query:
  ```sql
  CREATE VIEW competitive_plays AS
  SELECT * FROM plays
  WHERE play_type IN ('pass','run')
    AND wp BETWEEN 0.05 AND 0.95
    AND qtr <= 4              -- exclude OT unless explicitly desired
    AND half_seconds_remaining > 120  -- exclude 2-minute drill
    AND NOT (qtr = 4 AND half_seconds_remaining < 300)  -- exclude crunch time if scoping to "normal" tendencies
  ;
  ```
- Document the filter in `queries/00_filters.sql` and reference it from every tendency query. The exact thresholds are a defensible analyst choice — what matters is that they're explicit and consistent.
- Provide one query (or notebook section) that re-runs the headline finding **without** the filter, showing how much the claim depends on the filter. Recruiters read this as statistical maturity.

**Warning signs:**
- Headline tendency in FINDINGS.md changes by >10pp when the garbage-time filter is toggled.
- A per-team blitz-rate ranking that puts a defense with a famously bad pass rush at #1 — they only "blitz" because they're losing every game and forced into desperation.
- No mention of WP / win-probability filtering anywhere in the queries directory.

**Phase to address:**
Phase 2 (ETL produces a `competitive_plays` view); Phase 3 (every analysis query references it).

---

### Pitfall 7: Special teams / no_play / qb_kneel / qb_spike contamination

**What goes wrong:**
`SELECT COUNT(*) FROM plays WHERE down = 4` returns punts, field goals, kneels, spikes, and offensive 4th downs all bundled together. Tendency analysis on this sample is meaningless. Worse — `play_type='no_play'` historically had a documented bug where pass plays with end-of-play penalties were miscoded; some legitimate pass attempts hide there. [VERIFIED: nflfastR issue #46 "Faulty no_play designation"; common analytics convention to filter `play_type IN ('pass','run')`.]

**Why it happens:**
nflfastR's `play_type` field has six+ values: `pass`, `run`, `kickoff`, `punt`, `field_goal`, `extra_point`, `qb_kneel`, `qb_spike`, `no_play`. Defaulting to "all plays" pulls in everything. New analysts also forget that `no_play` includes both dead-ball penalties (false start) and pass plays where the penalty replays the down — these are categorically different.

**How to avoid:**
- The base view (Pitfall 6) already restricts to `play_type IN ('pass','run')`. Hold the line: every tendency query reads from the view, never from raw `plays`.
- For explicitly "what happens after a flag" analyses, treat `no_play` as a separate cohort with its own caveats documented inline.
- Penalty-relevant plays: `pass_attempt = 1` and `rush_attempt = 1` are nflfastR's "the play was actually attempted" flags; prefer those over `play_type` for participation counts.

**Warning signs:**
- A team's reported "1st-and-10 pass rate" includes 4th-and-1 punts.
- Sample sizes ~3,000 plays per team per season (way too many — includes ST and no_plays). Real offensive-play count is ~1,000–1,100/team/season.
- `play_type` value distribution not printed in Phase 1 audit.

**Phase to address:**
Phase 2 (view layer enforces the filter).

---

### Pitfall 8: Sample-size collapse — the "75% on 3rd-and-12 from their own 5" with N=4 problem

**What goes wrong:**
4 seasons × 32 teams × down × distance bucket × field zone × score state collapses cell counts toward zero exponentially fast. An eye-catching "Team X plays Cover 3 87.5% of the time on 3rd-and-12 from inside their own 10" can be N=8 plays. Publishing that as a finding is a recruiter-killer — anyone who has worked with NFL data will spot it instantly.

**Why it happens:**
The **most interesting** tendency claims are exactly the ones with the smallest cells (rare situations are rare). The discovery process pulls the analyst toward extremes that have no statistical support.

**How to avoid:**
- SPEC's `N=15 minimum` is a starting point but **insufficient** for the entropy / chi-square work. Apply a tiered threshold:
  - **N ≥ 30** for any per-team-situation tendency claim in FINDINGS.md (this aligns with chi-square's ≥ 5 expected count per cell rule across a 6-bucket distribution).
  - **N ≥ 100** for any "extreme tendency" claim (e.g. ">75% one look").
  - **N ≥ 15** for descriptive-only chart inclusion with a small-N flag visible on the chart.
- Every tendency claim in FINDINGS.md prints its N in the same sentence: *"Cleveland blitzes on 41% of 3rd-and-long passes (N=78, 2022–2024)."*
- Build a `min_n_filter()` helper used by every notebook — make the threshold a function argument, not a magic number scattered across cells.
- For extreme claims, also report a 95% Wilson confidence interval around the proportion. A tendency that's "73% ± 26pp" is a non-finding and should be cut.

**Warning signs:**
- Any chart in `analysis/` notebooks where a bar's underlying N is < 15 and there's no shaded "low-N" indicator.
- FINDINGS.md text contains "always" or "never" without a sample size disclosed.
- "Top 3 most predictable team-situation combos" where the top entry has N < 30.

**Phase to address:**
Phase 3 (analysis) — N-thresholds are encoded in the helper module; Phase 4 (FINDINGS.md) — each insight reports N inline.

---

### Pitfall 9: Multiple-comparisons trap — "scan 32 teams across 50 situations and report what's extreme"

**What goes wrong:**
Running a per-team tendency test across 32 teams × 8 situational buckets = 256 implicit hypothesis tests. At α=0.05, ~13 will look significant by chance alone. Publishing those as "exploitable matchups" (SPEC business question #8) is data dredging dressed up as analysis.

**Why it happens:**
Chi-square per cell is a tempting reflex. The more teams × situations the analyst slices, the more "findings" pop. None of them generalize.

**How to avoid:**
- Choose **3–5 pre-registered situations** in Phase 1 (before looking at data). Document them in `docs/analysis-plan.md`. Examples: 3rd-and-long pass, red-zone runs, 1st-and-10 in opponent territory, 2nd-and-short. These are the only situations FINDINGS.md gets to claim findings on.
- For exploratory scans across all situations, use a Bonferroni or Benjamini-Hochberg correction and label the section "Exploratory — uncorrected / corrected p-values for context, not conclusions".
- The "exploitable matchups" deliverable becomes: *"Of the 8 pre-registered situations, here are the team-situation cells with extreme tendency, ranked by effect size, each with N and 95% CI."* Effect size + N + CI together — not raw p-values across hundreds of comparisons.

**Warning signs:**
- The "exploitable matchups" notebook contains a loop over all teams × all situations producing a table of "significant" results with no correction.
- FINDINGS.md surfaces a "Cover 3 on 4th-and-2 from midfield" type claim that wasn't in the analysis plan.
- p-values are reported anywhere without sample size and effect size alongside.

**Phase to address:**
Phase 1 (pre-register the situational scope in `docs/analysis-plan.md`); Phase 3 (analysis notebooks honor the plan; exploratory work is segregated and labeled).

---

### Pitfall 10: Entropy-based predictability score is meaningless without baseline normalization

**What goes wrong:**
Raw Shannon entropy `H(p) = -Σ p_i log p_i` over a defensive distribution is bounded by `log(k)` where k = number of categories. A team with 4 observed defensive looks (k=4) has max entropy ≈ 1.39; a team with 6 looks (k=6) has max entropy ≈ 1.79. The score "Cleveland: H=1.42, Pittsburgh: H=1.55" doesn't tell you Pittsburgh is more unpredictable — it might just mean they got charted using more categories. The SPEC's headline "rank all 32 teams by predictability" is broken without normalization.

**Why it happens:**
Information-theoretic measures look quantitative and impressive, so they get plugged in without thinking about whether the underlying random variable has the same support across the things being compared.

**How to avoid:**
- Use **normalized entropy** `H(p) / log(k)` ∈ [0, 1] where k is the **same fixed support** for all teams (e.g. {blitz_low, blitz_med, blitz_high} × {pa_yes, pa_no} = 6 categories). Define the support once, in Phase 3, and apply identically across teams.
- Or use **Kullback-Leibler divergence from league baseline**: `KL(team || league)` measures how much a team's distribution differs from the league's. This is invariant to support choice if the same situational filter is applied.
- For the public-facing single number: convert to a 0–100 "Predictability Index" with the league average normalized to 50, std-dev around it. Recruiters parse a 0–100 score; they do not parse `H=1.42 nats`.
- Document the formula and an worked example in FINDINGS.md.

**Warning signs:**
- Entropy values reported with different k across teams.
- The team that ranks "most unpredictable" is the team with the smallest sample size (more sampling = more observed categories = higher raw entropy).
- The score doesn't pass a sanity check (e.g. a team famous for predictability per public scouting reports ranks as average — the score is measuring noise).

**Phase to address:**
Phase 3 (predictability modeling notebook) — normalization formula is the FIRST cell, applied consistently.

---

### Pitfall 11: Predictability score reflects opponent strength / game script, not defensive coordinator tendency

**What goes wrong:**
A defense that mostly faces backup QBs and runs out the clock with a lead all season looks "predictable" because situational forcing makes them call basic defenses. A defense that plays from behind constantly looks "unpredictable" because they're forced into varied responses to passing offenses. Neither score reflects the coordinator's actual playbook diversity.

**Why it happens:**
Confounding by game script (who's leading, time remaining, opponent pass rate) is severe in NFL data. Without conditioning on situation, the score measures schedule, not scheme.

**How to avoid:**
- Compute predictability **conditional on situation**, not as a marginal: H(defense | down=3 AND distance≥7 AND score_diff∈[-7,+7] AND wp∈[0.2,0.8]). Then aggregate across situations with each situation weighted equally (so a team that plays from behind a lot doesn't dominate the score by sheer count).
- In FINDINGS.md, present the score with a "schedule-adjusted" caveat or, better, show the score broken out by score-state bucket (leading / tied / trailing).
- Consider a **residual** approach: regress defensive choice on situation features, take the team-level residual variance — that's "predictability holding situation constant".

**Warning signs:**
- Top of the predictability ranking correlates suspiciously with team win-loss record or strength of schedule.
- Score is unstable when re-computed on a single half of the season.
- The "most unpredictable" defense is a famously bad one (they're not unpredictable, they're losing).

**Phase to address:**
Phase 3 (predictability notebook conditions on situation); Phase 4 (FINDINGS.md addresses the confound explicitly).

---

### Pitfall 12: Notebook with hidden state / out-of-order cells

**What goes wrong:**
The notebook runs fine in the author's session because cells were re-executed in a custom order. Recruiter clones, hits "Run All", and gets a `NameError` or — worse — silently different chart values than what's checked into the repo's PNG outputs.

**Why it happens:**
Jupyter encourages exploration. Variables get redefined, cells get deleted out of order, the kernel keeps the old objects alive. This is the single most common failure mode for portfolio Jupyter repos.

**How to avoid:**
- **CI gate:** add a `make test-notebooks` (or a simple `nbclient` / `papermill` script) that executes every notebook top-to-bottom on a fresh kernel and fails if any cell errors. Add a one-line GitHub Actions workflow running this on push.
- Pre-commit hook: `jupyter nbconvert --to notebook --execute --inplace --ClearOutputPreprocessor.enabled=False <nb>` — forces a clean run before commit.
- `nbqa` + `ruff` on notebook code cells.
- README's "Setup" section ends with: *"Verify reproducibility: `make test-notebooks` — runs all notebooks end-to-end on a fresh kernel. Should complete in <2 minutes."*

**Warning signs:**
- Notebook cell counts are non-sequential (`In [12]`, `In [3]`, `In [27]`).
- A variable is referenced before its defining cell.
- PNG charts in `findings/images/` show different numbers than the notebook's last-executed-cell output for the same chart.

**Phase to address:**
Phase 5 (ship) — reproducibility gate is a hard ship blocker. Should also be enforced in Phase 3 as the notebooks are written.

---

### Pitfall 13: Jargon overload — recruiters bouncing because they can't parse "Cover 6"

**What goes wrong:**
The audience is non-football data-analyst recruiters. A README that opens "We analyze single-high vs. two-high coverage rotations across 12-personnel sets" loses the reader in 8 seconds. The candidate's data-engineering skills never get evaluated because the recruiter never reaches the methodology section.

**Why it happens:**
NFL analytics has dense in-group vocabulary. Authors steeped in the domain forget that "Cover 3" needs a one-line gloss for a reader whose football knowledge stops at "the offense throws to the receiver".

**How to avoid:**
- README's hook is **one plain-English sentence**: *"Which NFL defenses are predictable in known situations, and which aren't? This project analyzes 4 seasons of charted data to answer that, ranks 32 teams, and highlights 3 exploitable matchups."* No jargon.
- A `## Glossary` section in the README defines every domain term used elsewhere in 1 line each (down & distance, EPA, blitz rate, predictability index).
- FINDINGS.md leads with the takeaway in plain English, then the chart, then the methodology in collapsed/footnoted form.
- Hero chart in the README is **labeled for a non-fan**: y-axis says "Predictability Index (0=random, 100=fully predictable)", not "Normalized situational entropy (nats)".

**Warning signs:**
- README first paragraph contains "Cover", "EPA", "PPF", "DVOA", "personnel grouping" without a gloss.
- A non-football friend reads the README and can't say what the project does.
- FINDINGS.md insights start with the methodology rather than the result.

**Phase to address:**
Phase 4 (FINDINGS.md drafting); Phase 5 (README polish + non-football reader test before ship).

---

### Pitfall 14: Big committed `.db` file blowing up the repo size

**What goes wrong:**
SQLite database with FTN + pbp for 4 seasons is roughly 250–500 MB depending on which columns are kept. GitHub blocks files > 100 MiB outright; files > 50 MiB trigger a warning. `git push` either fails with "this exceeds GitHub's file size limit" or the repo balloons past 1 GB on the first clone, killing the "recruiter clone-and-run in 90 seconds" promise. [VERIFIED: GitHub 100 MiB hard limit; 50 MiB warning per GitHub Docs.]

**Why it happens:**
The SPEC says the .db is "checked in if small". "Small" is undefined. SQLite from 4 seasons of pbp + FTN is not small.

**How to avoid:**
- `.db` is **gitignored by default**. The ETL pipeline generates it from scratch in <2 minutes on a stock laptop.
- README says: *"Run `python -m etl.build_database` — generates `data/nfl_coverage.db` (~250 MB) in 60–90 seconds."*
- Sanity-check ETL output size in the build script; if .db > 100 MB, fail with a message pointing the user to the ETL command.
- `data/raw/` (parquet caches from `nfl_data_py`) is also gitignored — these are 100s of MB and regenerable.
- Optionally: ship a tiny `data/sample.db` (one team, one season — under 5 MB) for quickstart browsing without running ETL. Document in README as "quickstart sample, full data via ETL".

**Warning signs:**
- `git status` shows `data/nfl_coverage.db` as tracked.
- `du -sh .git/` exceeds 200 MB.
- Push to GitHub returns "this exceeds GitHub's file size limit of 100.00 MB".
- `git ls-files | xargs ls -la | sort -k5 -n -r | head` shows .db / .parquet at the top.

**Phase to address:**
Phase 2 (ETL writes to gitignored path; .gitignore committed correctly); Phase 5 (ship — verify clone size on a fresh checkout).

---

### Pitfall 15: PNGs checked in inconsistently — README hero chart is stale

**What goes wrong:**
Notebook generates `findings/images/hero_predictability.png`. Author tweaks the chart, re-runs the notebook, but forgets to commit the new PNG. README still shows the old chart. Or worse — the notebook generates a chart with one set of numbers, the PNG in the repo shows a different set, and the FINDINGS.md text quotes a third.

**Why it happens:**
Three artifacts (notebook code, exported PNG, FINDINGS.md text) carry the same number. Updating one without the others creates silent drift.

**How to avoid:**
- Single source of truth: the notebook generates the PNG via `plt.savefig('findings/images/<name>.png', dpi=150, bbox_inches='tight')` AND prints the underlying number to a logged dict. FINDINGS.md text is generated by string-templating from that dict (or at least sanity-checked against it).
- Pre-ship checklist (run in Phase 5): re-execute every notebook, regenerate every PNG, diff against committed PNGs — any visual diff = stale. Tools: `imagemagick compare`, or a simpler MD5 check. A `make rebuild-images` target makes this one command.
- Commit notebook + PNGs in the same commit. Never one without the other.

**Warning signs:**
- A PNG's git mtime is older than the notebook that generated it.
- README displays a chart with numbers that don't appear anywhere in FINDINGS.md text.
- Re-running a notebook produces a different PNG than what's checked in.

**Phase to address:**
Phase 4 (FINDINGS.md); Phase 5 (ship — pre-commit regen check).

---

### Pitfall 16: `requirements.txt` not pinned tightly enough — recruiter's pandas version breaks the notebook

**What goes wrong:**
`requirements.txt` says `pandas`. On a recruiter's machine with pandas 2.2.x, an `import_pbp_data` call hits `AttributeError: np.float_ was removed in NumPy 2.0`. The recruiter sees a stack trace, closes the tab, and the candidate is filtered out. [VERIFIED: nfl_data_py issue #98 — np.float_ removed in NumPy 2.0; pandas/numpy compatibility issues #59023, #59052.]

**Why it happens:**
NumPy 2.0 removed `np.float_`. `nfl_data_py` 0.3.3 uses it. Without pinning numpy < 2 (or pandas to a version that pulls in numpy < 2), a fresh `pip install` resolves to the latest numpy and breaks.

**How to avoid:**
- Pin everything in `requirements.txt` to known-good exact versions:
  ```
  nfl-data-py==0.3.3
  pandas==2.1.4
  numpy<2
  matplotlib==3.8.2
  seaborn==0.13.0
  jupyter==1.0.0
  notebook==7.0.6
  ```
- Plus a `requirements-dev.txt` with linting/test tools (`ruff`, `nbqa`, `papermill`).
- Test the install path on a fresh venv (Linux/macOS/Windows if possible) before ship. Consider including the test as a GitHub Actions workflow that runs `pip install -r requirements.txt && python -c "import nfl_data_py; nfl_data_py.import_pbp_data([2024], cache=False)"` — turns the install into a recruiter-verifiable green badge.
- Pin Python: README says "Python 3.11.x recommended" (NOT 3.13 — known broken per nfl_data_py issue #122).

**Warning signs:**
- `requirements.txt` has unpinned packages or `>=` ranges.
- No CI workflow that re-installs and runs ETL.
- Issues #98 and #122 in `nfl_data_py` not acknowledged in the README's "Known Issues" section.

**Phase to address:**
Phase 2 (ETL phase locks `requirements.txt` after first successful pull); Phase 5 (CI workflow to verify install + import).

---

### Pitfall 17: `nfl_data_py` data pull failing silently (network / nflverse release moved)

**What goes wrong:**
`nfl.import_ftn_data([2024])` hits a 404 from the nflverse release CDN. Without explicit error handling, the ETL continues with an empty dataframe; downstream queries return zero rows; FINDINGS.md is "blank" but no error raised. [VERIFIED: nfl_data_py issue #145 "import_injuries gives 404 for 2025" — same failure mode applies to FTN.]

**Why it happens:**
nflverse release URLs occasionally move. The package retries silently on some endpoints; on others it returns an empty result. Solo-author projects don't notice until someone else clones and gets confused.

**How to avoid:**
- ETL asserts on row counts post-pull:
  ```python
  ftn = nfl.import_ftn_data([2022, 2023, 2024, 2025])
  assert len(ftn) > 130_000, f"FTN pull returned {len(ftn)} rows — expected >130k for 4 seasons. Check nflverse release status."
  ```
- Cache raw pulls as parquet to `data/raw/` (gitignored). On subsequent ETL runs, prefer cache; on cache miss, re-pull. The cache turns "ephemeral nflverse outage" into "you already have the data".
- README documents: *"If `nfl_data_py.import_ftn_data` fails, check https://github.com/nflverse/nflverse-data/releases — the package follows the latest release."*
- Stretch: archive the parquet caches to a release on the project's own GitHub repo so the project is replayable even if nflverse goes down.

**Warning signs:**
- Database build "succeeds" in <5 seconds (data didn't actually load).
- Row counts in `data/audit/row_counts.csv` don't match expected ~50k/season for FTN, ~45k/season for pbp.
- Notebooks render "no data" charts without errors.

**Phase to address:**
Phase 2 (ETL with row-count assertions and parquet caching).

---

### Pitfall 18: Public-repo discipline — accidentally committing scratch / .env / oversized data

**What goes wrong:**
Author's working directory accumulates `scratch.ipynb`, `experiment-with-2025-data.py`, a copy of a stale `.env` from another project (defensive — the project doesn't use API keys, but the reflex of `git add .` after a long session causes it). Recruiter sees a messy commit history with `WIP` and `delete this later` and a 3MB stray PNG that's not referenced anywhere.

**Why it happens:**
Solo developer + portfolio repo + no PR review. `git add .` is the default reflex. Default tooling doesn't catch any of this.

**How to avoid:**
- `.gitignore` from the start covers: `.env`, `.env.*`, `*.db`, `*.parquet`, `data/raw/`, `data/cache/`, `.ipynb_checkpoints/`, `__pycache__/`, `.DS_Store`, `*.log`, `scratch*`, `tmp_*`.
- Pre-commit hook running `detect-secrets` (or `gitleaks`) — blocks commit on any high-entropy string.
- Commit hygiene: squash messy WIP commits before ship via interactive rebase. Final history shows logical phases, not a stream-of-consciousness.
- Pre-ship audit: `git log --oneline | head -50` is reviewable as a portfolio artifact in itself. Recruiters DO look at commit history.

**Warning signs:**
- `.env` files anywhere in `git ls-files`.
- `git log --all --pretty=format:'%s'` contains "WIP", "fix", "asdf", "test commit", or anything with no semantic content.
- Files in repo not referenced from any other file (orphan PNG, unused .py).
- `git ls-files | wc -l` is suspiciously high (>200) for a portfolio repo.

**Phase to address:**
Phase 0 (initial repo setup with `.gitignore` + pre-commit); Phase 5 (ship — final commit-history audit + squash).

---

### Pitfall 19: FINDINGS.md reads like a CS homework write-up, not an analyst memo

**What goes wrong:**
"Section 1: Introduction. Section 2: Data. Section 3: Methodology. Section 4: Results..." — this is a school assignment format. NFL analytics teams and data-analyst hiring managers read **memos**: takeaway first, evidence second, methodology in an appendix. A homework-format doc signals "junior, hasn't worked in industry".

**Why it happens:**
The author's most recent writing experience is academic. The format gets transferred without thinking about the audience.

**How to avoid:**
- FINDINGS.md format:
  - **Top:** 3–4 bullet-point findings (the headline numbers + one-line interpretation each).
  - **Body:** 5–7 numbered insights, each in this template:
    1. **Headline** (1 sentence, plain English).
    2. **The chart** (one PNG, labeled for a non-fan).
    3. **Why it matters** (1 paragraph, the football/strategic implication).
    4. **Sample size & caveats** (1 sentence: N, season scope, filters applied).
  - **Methodology appendix:** terse — data source, join, filter, score formula. 1–2 pages max.
- Look at FTN's, PFF's, or Football Outsiders' public-facing analyst posts as the structural model. Avoid academic-paper formatting.
- Have a non-technical friend read FINDINGS.md cold; they should be able to summarize the headline findings after one read.

**Warning signs:**
- FINDINGS.md is structured like a paper (Abstract / Introduction / Methods / Results / Discussion).
- The first chart appears > 200 words in.
- Methodology comes before results.
- Findings are framed as "we ran a chi-square test" instead of "Cleveland is the most predictable defense in 2024".

**Phase to address:**
Phase 4 (FINDINGS.md drafting) — use a memo template from the start.

---

### Pitfall 20: README claims that don't match what the code produces

**What goes wrong:**
README says "Analyzes coverage tendencies across Cover 0/1/2/3/4/6". Phase 1 audit revealed FTN has no coverage labels and the project pivoted to blitz/personnel/play-action. Author updates the queries and notebooks but forgets to re-write the README hook. Recruiter reads the README, opens a notebook, sees `n_blitzers` and zero "Cover 3" anywhere, concludes the candidate doesn't proofread.

**Why it happens:**
README is typically written first (when it's aspirational) and last (when it's polished). The middle drift between the aspirational version and what actually shipped doesn't get reconciled.

**How to avoid:**
- Phase 1 outcome MUST trigger an explicit "rewrite README hook + business questions" task — not deferred to ship.
- Pre-ship checklist: every claim in README maps to a query, notebook cell, or FINDINGS.md insight. Any unmappable claim is cut. A `make verify-claims` script that grep-checks key terms (e.g. "Cover 3" should NOT appear if it's not a column we use) is a 30-minute investment.
- Hero charts in README are direct PNG references, not redrawn — same image as in FINDINGS.md.

**Warning signs:**
- README's "What this project does" doesn't match FINDINGS.md's headline findings.
- Repo description on GitHub (a separate string) is stale relative to the README.
- Tech-stack badges or topic tags reference tools/concepts not actually used (e.g. "Cover-3" topic tag with no Cover-3 analysis inside).

**Phase to address:**
Phase 1 (rewrite triggered by audit); Phase 5 (ship — claim/evidence audit).

---

### Pitfall 21: FTN charting field definitions are subjective — `is_play_action` is a charter judgment call

**What goes wrong:**
FTN charts plays manually within 48 hours. `is_play_action` is a binary label assigned by a human watching film. Edge cases (read-option fakes, RPOs that look like PA, mesh-point handoff fakes) are charter judgment calls. Two charters can disagree. "Team X uses play-action 32.4% of the time" carries the precision of FTN's charting consistency, not 4-significant-figure exactness. [VERIFIED via FTN methodology — manual charting; INFERRED that subjectivity exists because no charting protocol guarantees zero inter-rater variance, but FTN does not publish inter-rater agreement metrics for the nflverse subset.] [ASSUMED — not directly verified — that the same play-action threshold applied across seasons.]

**Why it happens:**
Tabular data feels objective. Numbers in a column don't disclose their provenance. A reader of `is_play_action == True` doesn't see "this was a charter's snap judgment".

**How to avoid:**
- README's data-source section explicitly notes: *"FTN charting is manual, expert-charted within 48 hours of each game. Subjective fields like `is_play_action`, `is_rpo`, `is_screen_pass` reflect FTN's charting standards; small biases between charters are possible. We treat these as ground truth for this analysis but report rates to 1 decimal place, not 3."*
- Don't report play-action rates with 4 significant figures (32.4321%) — implies a precision the data doesn't have. Use 1 decimal: "32.4%" or rounded to 0: "32%".
- For sensitivity analysis: report a finding both with and without play-action conditioning. If the headline doesn't survive, the finding is fragile.

**Warning signs:**
- Findings reported to 4 decimal places.
- A single subjective FTN field carries the entire weight of a headline finding.
- No mention anywhere that FTN data is manually charted.

**Phase to address:**
Phase 4 (FINDINGS.md — disclose data provenance and round appropriately).

---

### Pitfall 22: Random seeds / non-deterministic ordering — notebook re-run produces different values

**What goes wrong:**
A `train_test_split` without a seed, a `df.sample(100)` without a seed, or a SQL `SELECT ... LIMIT 10` against an unindexed table all produce different values on each run. The PNG checked in shows N=27 plays in one chart; rerun shows N=24 (because a random sample was taken upstream). Recruiter sees their re-run differs from FINDINGS.md and concludes the analysis isn't reproducible.

**Why it happens:**
Default API behavior in pandas/sklearn is non-deterministic for any sampling/splitting operation unless a `random_state` is passed.

**How to avoid:**
- Project-wide constant `SEED = 42` in `analysis/_constants.py` imported by every notebook. Pass to every `random_state=`.
- Avoid any `df.sample()` in core analysis — use full populations (per Pitfall 8 N-thresholds, that's preferable anyway).
- For SQL: `ORDER BY game_id, play_id` on every query that doesn't already aggregate, so deterministic row ordering.
- A "reproducibility test" cell at the bottom of each notebook prints a hash of the result table — committed in the README. Recruiter can re-run and verify the hash matches.

**Warning signs:**
- `random_state=` not present in any `train_test_split` / `sample` call.
- Two re-runs of the same notebook on the same machine produce different chart values.
- Sample-size in chart legends shifts on re-run.

**Phase to address:**
Phase 3 (notebooks); Phase 5 (reproducibility hash check).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip the Phase 1 FTN schema audit and just write SQL against assumed `coverage` column | Saves 1 day | Project is unshippable — pivot becomes a rewrite, not a recalibration | **Never** — this is the project's foundational unknown |
| Use unpinned `requirements.txt` (`pandas`, `nfl-data-py`) | Saves typing exact versions | Recruiter's `pip install` fails on numpy 2.0 / Python 3.13 — silent project-killer | Only on local dev branch; locked before ship |
| Commit the SQLite .db directly to git "for convenience" | Recruiter doesn't have to run ETL | Repo > 200 MB; clone slow; eventually breaks GitHub limits as data grows; demonstrates poor data hygiene | If the .db is < 25 MB AND ETL takes > 30s — borderline acceptable for a sample slice. Full DB: never |
| Hand-write notebook cells without testing top-to-bottom | Faster exploration | Cells silently depend on hidden state; recruiter clone fails | During exploration; never at ship |
| Report tendency rates without sample size | Cleaner-looking charts | First sharp recruiter spots N=4 and the project is dismissed | Never for portfolio |
| Use raw entropy without normalization for the predictability score | Quick to compute | Score is meaningless; ranking is artifact of category support, not skill | Never — defeats the purpose of the deliverable |
| Skip the "competitive plays" filter and analyze on all plays | More data, simpler queries | Tendency claims are confounded by garbage time, prevent defense, kneels | Only as an explicitly-labeled "no filter" sensitivity check |
| `df.sample(100)` for "quick exploration" charts that ship | Easier to render | Re-run produces different PNG; reproducibility broken | Exploratory only — sampled charts never ship |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `nfl_data_py.import_ftn_data` | Joining on `ftn_game_id` / `ftn_play_id` instead of `nflverse_game_id` / `nflverse_play_id` | Always join FTN to pbp on `nflverse_game_id == game_id` and `nflverse_play_id == play_id`; use `validate='one_to_one'` |
| `nfl_data_py.import_pbp_data` | Using `cache=True` in CI / fresh-clone path (cache bug in 2024 season per issue #136) | Set `cache=False` in CI; cache-via-parquet manually in `data/raw/` for local dev |
| `nfl_data_py` install | Allowing pip to resolve to NumPy 2.0 (breaks `np.float_`) and Python 3.13 (install fails) | Pin `numpy<2` and recommend Python 3.11 in README; CI runs on 3.11 |
| nflverse FTN releases | Assuming the URL/path is stable indefinitely | Snapshot raw pulls as parquet in `data/raw/` (gitignored); document fallback in README |
| SQLite from pandas | Writing without dtypes / indexes — every query is a table scan | Define explicit `dtype` in `to_sql`; create indexes via `schema/02_indexes.sql` on `(game_id, play_id)`, `(team, season)`, `(season, week)` |
| Jupyter + matplotlib | `%matplotlib inline` missing → no charts in the rendered notebook on GitHub | Set `%matplotlib inline` in every notebook's first cell; verify charts render in GitHub's notebook viewer (not just locally) |
| GitHub MCP repo creation (ship phase) | Creating repo with default settings (no description, no topics, not pinned) | Ship plan explicitly sets repo description, topics (`nfl-analytics`, `data-analysis`, `python`, `sqlite`, `jupyter`), and pins as portfolio piece |
| FTN data licensing | Forgetting attribution — CC-BY-SA 4.0 requires it | README's "Data" section reads: *"FTN charting data via nflverse, released under CC-BY-SA 4.0. Attribution: FTN Data via nflverse."* |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| pbp DataFrame in memory unfiltered | Notebook OOM on a 16 GB recruiter laptop; `import_pbp_data([2022,2023,2024])` is ~3M rows × 370 cols | Pass `columns=[...]` to `import_pbp_data` to keep only needed columns; drop pbp before notebook moves to next analysis | 8 GB RAM laptop hits swap during ETL |
| SQLite without indexes | Per-team-per-situation queries take 30s+ | `CREATE INDEX` on `(season, week, posteam)`, `(game_id, play_id)`, `(down, ydstogo)` after load | Once joined dataset has >500k rows |
| Repeated FTN/pbp pulls during dev | Each pull is 30–90s + network | Cache to `data/raw/*.parquet` after first pull; subsequent ETL reads parquet | Becomes annoying after 5–10 ETL re-runs |
| Notebook rendering large dataframes inline | `df` (no `.head()`) prints 50,000 rows in Jupyter; notebook bloats to 100MB; GitHub refuses to render | Always `.head()` or `.describe()` for inline display; configure `pd.set_option('display.max_rows', 50)` | Once a notebook displays a full dataframe |
| Per-row pandas operations (`.apply` over a column) for situational binning | ETL goes from 30s to 5 min | Vectorize with `np.where` / `pd.cut` / `.assign` | Once the binning involves >3 columns |
| Re-rendering all PNGs on every notebook run | "Run all" takes 5 min instead of 30s | Gate PNG saves behind `if SAVE_FIGURES: plt.savefig(...)`, default False; flip to True only for the ship-time render | Becomes painful around 20+ charts |

For this project's scale (4 seasons, ~185k plays, ~30k FTN-charted), most of these are mild — but a recruiter on an old laptop is the explicit performance target, so all of them matter.

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Committing `.env` (reflex bug — even though this project doesn't use one) | Public exposure of any secret you happened to have in any `.env` while working in this directory | `.gitignore` `.env` and `.env.*` from the start; pre-commit `detect-secrets` |
| Redistributing PFF / paid charting data alongside FTN | Copyright violation; takedown notice; portfolio repo gone | Never check in PFF / paid sources; README explicitly states data sources are FTN (CC-BY-SA via nflverse) and nflfastR (MIT) |
| Missing FTN attribution | License violation (CC-BY-SA requires attribution) | README and FINDINGS.md both attribute "FTN Data via nflverse, CC-BY-SA 4.0" |
| Hardcoding any API key (defensive — none should exist) | Public exposure | No external APIs are used; if any third-party tool gets added later, use env vars and document |
| Recruiter clones repo with malicious post-install hook | Supply-chain risk for the recruiter | `requirements.txt` only — no `setup.py` post-install scripts; no Makefile target that runs anything destructive without explicit invocation |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| README requires running ETL before any chart is visible | Recruiter who skims (90% of them) sees no signal in the first 30 seconds | Embed 1–2 hero PNG charts directly in README — visible without cloning |
| FINDINGS.md is one giant markdown file with charts at the bottom | Reader bails before reaching them | Top-3-findings TL;DR at the top, each with its inline chart |
| Notebooks named `01.ipynb`, `02.ipynb`, `final_v3.ipynb` | Recruiter doesn't know which one to open | Notebooks named for what they DO: `01_exploratory.ipynb`, `02_predictability_modeling.ipynb`, `03_visualizations.ipynb` (matches SPEC structure) |
| Setup instructions span 8 commands and a paragraph of caveats | "Recruiter clone-and-run in 90 seconds" promise dies | Setup is exactly 4 commands fenced as one block: `git clone …`, `pip install -r requirements.txt`, `python -m etl.build_database`, `jupyter notebook` |
| Charts use seaborn defaults (small fonts, gray bg) | Look generic, screenshot poorly | Define one project-wide style in `analysis/_style.py` — large fonts, white bg, consistent palette; import in every notebook |
| Glossary buried at the bottom of README | Non-football recruiter hits jargon early, bounces | Glossary is its own collapsible `<details>` block right after the hook OR jargon terms link to it inline |

---

## "Looks Done But Isn't" Checklist

- [ ] **FTN schema audit:** Often missing the **column-list dump** in `docs/ftn-schema-audit.md` — verify the exact 28-column list is recorded and the "no coverage labels" finding is explicit, not implied.
- [ ] **ETL:** Often missing **row-count assertions** post-pull — verify that `len(ftn_df) > 100_000` and `len(pbp_df) > 100_000` checks exist.
- [ ] **ETL join:** Often missing `validate='one_to_one'` in the FTN↔pbp merge — verify it's present and the post-join match rate is logged.
- [ ] **Competitive-plays filter:** Often missing as an explicit view — verify `queries/00_filters.sql` exists and is referenced (not duplicated) by every tendency query.
- [ ] **Sample-size flagging:** Often missing inline N in FINDINGS.md text — every tendency claim should have `(N=X)` in the same sentence.
- [ ] **Predictability score normalization:** Often computed as raw entropy — verify the formula in the notebook divides by `log(k)` or uses KL-from-baseline.
- [ ] **Notebooks reproducible:** Often passes locally but fails on fresh kernel — verify `make test-notebooks` (or equivalent) runs every notebook top-to-bottom green.
- [ ] **PNGs current:** Often stale relative to notebook — verify mtime of PNG ≥ mtime of generating notebook for every chart.
- [ ] **README claims match code:** Often drifts after Phase 1 pivot — verify every domain term in README is grep-able in queries/ or analysis/.
- [ ] **Glossary:** Often missing — verify a glossary section exists and covers every football term used elsewhere.
- [ ] **`requirements.txt` pinned:** Often loose ranges — verify every line is `==` to an exact version, including `numpy<2` and `python_requires` style hint in README.
- [ ] **`.gitignore` complete:** Often missing one of `.env*`, `data/raw/`, `*.db`, `.ipynb_checkpoints/` — verify on a fresh clone via `git status` after running ETL.
- [ ] **FTN attribution:** Often missing CC-BY-SA notice — verify README and FINDINGS.md both attribute FTN Data via nflverse.
- [ ] **Repo size:** Often forgotten until ship — verify `du -sh .git/` is < 50 MB before push.
- [ ] **GitHub MCP ship config:** Often default — verify repo description, 5–8 topic tags, and pinned-repo status are set during the ship phase, not afterthoughts.
- [ ] **Commit history clean:** Often "WIP" / "fix typo" noise — verify squashed to logical commits before public push.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Phase 1 reveals FTN has no coverage labels (post-audit) | LOW | Pivot is built into the SPEC. Rewrite the 8 business questions around blitz / play-action / personnel; rename repo if needed; update README hook. ~1 day. |
| Predictability score correlates suspiciously with team record | MEDIUM | Re-derive as situation-conditional or KL-from-baseline. ~1–2 days; salvageable without rerunning ETL. |
| Notebook execution fails on recruiter's machine | LOW | Pin `requirements.txt` exactly; lock to Python 3.11; add a CI workflow proving install. ~half day. |
| Repo > 100 MB; push rejected | LOW | `git filter-repo` to strip the .db from history; add `.gitignore`; force-push (acceptable only if not yet shared). If shared: BFG repo-cleaner + new repo. ~half day to a day. |
| Headline finding doesn't survive sample-size or filter sensitivity | MEDIUM | Replace with a different finding from the analysis; don't bury the dead finding — the appendix can document "we initially saw X, but it didn't survive Y filter — here's the more robust finding". This is itself a positive recruiter signal. ~half day. |
| Repository name was published, then Phase 1 forces a pivot | MEDIUM | GitHub allows repo rename; old URL redirects. But don't ship until the audit is in — that's the whole point of "name decided after Phase 1" in the constraints. |
| FINDINGS.md jargon confuses non-football reader (caught at ship gate) | LOW | Add glossary; rewrite hook; reorder so plain-English takeaway is first. ~half day. |
| `nflverse` releases moved during analysis; ETL breaks | LOW (if cached) / MEDIUM (if not) | If parquet cache exists in `data/raw/`: re-run ETL from cache. If not: snapshot the cache the moment a new pull succeeds. |
| Multiple-comparisons issue caught late by reviewer | MEDIUM | Re-frame "exploitable matchups" as effect-size + N-ranked, with caveats about exploration vs. confirmation. Keep findings honest, not fewer. ~1 day. |

---

## Pitfall-to-Phase Mapping

Phase numbering corresponds to the SPEC's project structure (Phase 1 audit → 2 ETL → 3 analysis → 4 findings/report → 5 ship). Phase 0 is repo bootstrap.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| 1. `nfl_data_py` archived | Phase 1 | `nfl_data_py` version pinned to 0.3.3 in `requirements.txt`; deprecation noted in README "Known Issues" |
| 2. FTN lacks coverage labels | Phase 1 | `docs/ftn-schema-audit.md` lists actual 28 FTN columns; business questions reframed accordingly |
| 3. FTN join keys | Phase 2 | `etl/join_and_normalize.py` uses `validate='one_to_one'`; post-join match rate logged > 95% |
| 4. NaN on run plays for blitz columns | Phase 1 + 3 | `audit/ftn_null_profile.csv` shows null rates by play_type; analysis cells filter to `play_type='pass'` |
| 5. Pre/post-snap distinction | Phase 1 | Business question list does not include any pre-snap-vs-post-snap claim |
| 6. Garbage time / WP filter | Phase 2 | `competitive_plays` view exists in schema; every query references it |
| 7. ST / no_play contamination | Phase 2 | View filters `play_type IN ('pass','run')` |
| 8. Sample-size collapse | Phase 3 + 4 | `min_n_filter()` helper; FINDINGS.md displays N inline for every claim; N≥30 for tendency, N≥100 for extreme |
| 9. Multiple comparisons | Phase 1 + 3 | `docs/analysis-plan.md` pre-registers 3–5 situations; exploratory work labeled and corrected |
| 10. Entropy normalization | Phase 3 | Predictability notebook's first cell defines fixed support and normalizer; documented in FINDINGS.md |
| 11. Score reflects schedule | Phase 3 + 4 | Score conditioned on situation; FINDINGS.md addresses confound |
| 12. Notebook hidden state | Phase 3 + 5 | `make test-notebooks` runs all notebooks fresh-kernel green; CI workflow enforces |
| 13. Jargon overload | Phase 4 + 5 | Glossary in README; non-football reader test before ship |
| 14. Big .db file | Phase 2 + 5 | `.db` gitignored; ETL builds from scratch in <2 min; `du -sh .git/` < 50 MB at ship |
| 15. Stale PNGs | Phase 4 + 5 | `make rebuild-images` regenerates all PNGs; pre-ship visual diff check |
| 16. Loose `requirements.txt` | Phase 2 + 5 | All packages pinned `==`; CI verifies `pip install` + import |
| 17. Silent data pull failure | Phase 2 | Row-count assertions in ETL; parquet cache fallback |
| 18. Public-repo discipline | Phase 0 + 5 | `.gitignore` + pre-commit `detect-secrets` from day 1; commit history audited at ship |
| 19. Memo vs. homework format | Phase 4 | FINDINGS.md follows memo template; non-technical reader test |
| 20. README↔code drift | Phase 1 + 5 | Phase 1 audit triggers README rewrite task; pre-ship `make verify-claims` script |
| 21. FTN subjectivity | Phase 4 | Data provenance + charting limitations disclosed in README data section; rates rounded to 1 decimal |
| 22. Random seeds / determinism | Phase 3 + 5 | `SEED = 42` constant; reproducibility hash committed; verifier in README |

---

## Sources

### Primary (HIGH confidence)
- [nfl_data_py GitHub repo (archived banner & deprecation notice)](https://github.com/nflverse/nfl_data_py) — verified archive date 2025-09-25, recommended successor `nflreadpy`
- [nfl_data_py PyPI](https://pypi.org/project/nfl-data-py/) — version 0.3.3 (2024-09-20), Python 3.6–3.12
- [Context7: /nflverse/nfl_data_py](https://github.com/nflverse/nfl_data_py) — confirms `import_ftn_data(years, columns=None, downcast=True, thread_requests=False)` signature, FTN from 2022+, CC-BY-SA 4.0
- [nflreadr FTN data dictionary](https://nflreadr.nflverse.com/articles/dictionary_ftn_charting.html) — definitive 28-column list; **no coverage labels present**; `qb_location` is the only field marked pre-snap
- [nflreadr load_ftn_charting reference](https://nflreadr.nflverse.com/reference/load_ftn_charting.html) — license CC-BY-SA 4.0; attribution required
- [nflreadpy GitHub](https://github.com/nflverse/nflreadpy) — successor package, polars-native, `load_ftn_charting()` function
- [nflreadpy PyPI](https://pypi.org/project/nflreadpy/) — v0.1.5 (2025-11-19)
- [nfl_data_py issue #98 — np.float_ NumPy 2.0 break](https://github.com/nflverse/nfl_data_py/issues/98)
- [nfl_data_py issue #122 — Python 3.13 install failure](https://github.com/nflverse/nfl_data_py/issues/122)
- [nfl_data_py issue #136 — caching broken for 2024 season](https://github.com/nflverse/nfl_data_py/issues)
- [nfl_data_py issue #145 — import returns 404](https://github.com/nflverse/nfl_data_py/issues)
- [nflfastR issue #46 — faulty no_play designation](https://github.com/nflverse/nflfastR/issues/46)
- [GitHub Docs: About large files on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) — 100 MiB hard limit, 50 MiB warning

### Secondary (MEDIUM confidence)
- [Open Source Football: nflfastR EP, WP, CP xYAC, and xPass models](https://opensourcefootball.com/posts/2020-09-28-nflfastr-ep-wp-and-cp-models/) — EPA / WP filtering convention
- [How to Analyze NFL Play-by-Play in R with nflfastR (EPA & WP)](https://rprogrammingbooks.com/nfl-analytics-with-r-nflfastr-nflverse/) — confirms `wp` between 0.05 and 0.95 garbage-time filter convention
- [nflfastR docs / pdf](https://cran.r-project.org/web/packages/nflfastR/nflfastR.pdf) — column conventions, `play_type` values
- [FTN Data NFL Catalog](https://ftnfantasy.com/ftn-data-nfl-catalog) — describes paid product including coverage labels; corroborates absence from public subset
- [pandas issue #59023 — NumPy 2.2 support](https://github.com/pandas-dev/pandas/issues/59023) and #59052 — pandas/NumPy version pairing constraints

### Tertiary (LOW confidence — flagged for validation)
- FTN per-column NaN rates beyond the qualitative "expected NaN on non-pass plays for `n_blitzers` / `n_pass_rushers`" — not published; **must be measured in Phase 1 audit and recorded in `audit/ftn_null_profile.csv`**.
- FTN inter-rater agreement metrics on subjective fields (`is_play_action`, `is_rpo`) — not published by FTN for the nflverse subset; treated as ground truth with rounding caveat.
- Exact .db file size from 4 seasons of joined data — estimated 250–500 MB based on column counts and row counts (~185k plays × ~50 retained columns); **must be measured in Phase 2 and reflected in the gitignore decision**.

---

*Pitfalls research for: NFL coverage / defensive-tendency portfolio project on `nfl_data_py` (FTN + nflfastR), Python 3.11 + SQLite + Jupyter, public GitHub repo, entry-level data-analyst portfolio audience.*
*Researched: 2026-04-29*
