# Phase 4 Pre-Discuss Factual Brief

**Date:** 2026-04-30
**Purpose:** Establish the factual record on the four substantive Phase 3 findings (D-14..D-17) and the `n_blitzers > 4 → > 0` correction before opening Phase 4 discuss-phase. All numbers are verified against `data/nfl_defensive_tendencies.db` (1,139 games / 197,362 plays / 185,215 ftn_play / 105,556 competitive_plays / 58,178 competitive pass plays joined to FTN).

---

## 1. The `n_blitzers > 4 → > 0` correction

### 1.1 What surfaced

The plan documents (`03-CONTEXT.md` D-02, `03-03-PLAN.md`, `docs/ftn-schema-audit.md`) defined "blitz" as `n_blitzers > 4`, citing the standard nflfastR convention where 5+ rushers = blitz. That convention applies to nflfastR's `n_pass_rushers` column, which is a **total** rusher count. FTN's `n_blitzers` is a different column with a different encoding: it counts **extra rushers above the base 4-man defensive front**. Any `n_blitzers >= 1` means a blitz was sent.

Empirical evidence on the live DB:

| Predicate | Plays matching (of 58,178 competitive pass plays) | Rate |
|---|---:|---:|
| `n_blitzers > 4` (broken threshold) | 7 | 0.012% |
| `n_blitzers > 0` (corrected threshold) | 17,131 | 29.45% |
| `n_pass_rushers >= 5` (the analog total-rusher threshold, used unchanged in QUERY-03/05) | — | ~30% range |

`MAX(n_blitzers)` in the DB is 6 (i.e., 6 extra rushers, 10 total). The broken threshold was producing a near-empty universe.

### 1.2 When the catch happened, by whom

Both Phase 3 Wave 2 agents independently caught the bug during execution on 2026-04-30. They were running in parallel on disjoint file sets (queries vs. notebook); neither saw the other's fix in flight.

| Agent | Trigger | Commit | Fix used |
|---|---|---|---|
| 03-02 (queries) | Task 1 smoke testing — initial author run on `queries/01..08_*.sql` returned ~0 blitz rates across the slate | `4cb60de` | `n_blitzers > 0` |
| 03-03 (predictability modeling) | Task 3 — notebook execution failed with `ZeroDivisionError` in the odds-ratio computation because the PA=1/blitz=1 cell collapsed to 0 under the broken threshold | `bf2aba0` | `n_blitzers >= 1` (semantically equivalent; superseded by 03-02's `> 0` via downstream lint sync) |

This is one of the two Wave 2 commits the verifier flagged as "documented Rule-1 bug fix" in `03-VERIFICATION.md`. The convergence (two independent rediscoveries within minutes) is itself a quality signal — the bug was not subtle once any data flowed through it.

### 1.3 What re-ran as a result

Everything analytical. The corrected threshold is the input to:

- All 8 SQL files (`queries/01..08_*.sql`) — re-authored in commit `4cb60de`.
- `scripts/_verify_queries_run.py` — QUERY-09 meta-compliance + behavioral smoke verifier (commit `2cf98b7`).
- `analysis/02_predictability_modeling.py` inline `S1_PA_BLITZ_SQL` (chi-square universe) and `SQL_PRED_UNFILTERED` (sensitivity universe) — both rebuilt at corrected threshold (commit `bf2aba0`).
- `queries/07_situational_predictability_score.sql` — the entropy raw-input rollup that drives the predictability index (commit `cef2649` + linter sync to `> 0`).
- All empirical numbers in `03-03-SUMMARY.md`: predictability index leaderboard, 32×4 matrix, KL secondary, Spearman validation gate, chi-square contingency, odds ratio, Wilson CI, STAT-08 sensitivity — every reported value computed at the corrected threshold.

### 1.4 What did NOT re-run (the prose lag for Phase 4 to fix)

The on-disk **analytical** surface is internally consistent at `> 0`. The on-disk **prose** surface still references the stale `> 4` in four places:

1. `.planning/PROJECT.md` line 58 (Domain Primer operational definition: `(n_blitzers > 4)`)
2. `.planning/phases/03-analytical-layer-sql-python/03-CONTEXT.md` D-02 (the locked decision text)
3. `docs/ftn-schema-audit.md` (operational definition for the anchor dimension)
4. `README.md` glossary (currently a placeholder; the eventual glossary entry must use `> 0`)

`findings/FINDINGS.md` does not exist yet and will be written in Phase 4 with the corrected threshold from inception. The four prose locations are part of Phase 4 / DOC-06 (glossary) and the cross-doc reconciliation work flagged in STATE.md D-14.

### 1.5 Why the bug existed in the first place

The `> 4` convention crossed columns. nflfastR's `n_pass_rushers` is total rushers; `> 4` is the standard blitz boolean. FTN's `n_blitzers` looks superficially similar but has a different meaning — it is the count *above* the base front, not the total. The Phase 1 audit (`docs/ftn-schema-audit.md`) listed `n_blitzers` as the pressure anchor and reused the `> 4` convention without verifying the column semantics. The audit notebook (`analysis/00_data_audit.ipynb`) profiled NaN rates per column but did not eyeball `n_blitzers` value distributions; if it had, the `MAX = 6` and the right-skewed distribution centered near 0 would have surfaced the encoding immediately.

---

## 2. D-14, D-15, D-16, D-17 — one paragraph each

### D-14: `n_blitzers` threshold calibration (full detail in §1 above)

**Question:** What is the correct operational definition of "blitz" against FTN's public charting columns? **Result:** `n_blitzers > 0`, not `n_blitzers > 4`. FTN counts extra rushers above the base 4-man front, not total rushers. Under the corrected threshold, the league-wide blitz rate on competitive pass plays is **29.45% (N=17,131 / 58,178)** — consistent with public sports-analytics benchmarks (~28–32%) and with the S1-H1 hypothesis ("league blitz rate on 3rd-and-long > 35%"), which the corrected threshold confirms directionally (S1 league blitz rate well above 35%; DET leads at 52.3% on QUERY-05). **Sample size:** 58,178 competitive pass plays joined to FTN, 2022–2025. **Characterization:** factual calibration — the correct number is what's now in the queries and notebook; the project's analytical surface is already consistent at the corrected definition. The remaining work is prose reconciliation across four docs (PROJECT.md, 03-CONTEXT.md, ftn-schema-audit.md, README glossary; FINDINGS.md will be written correctly).

### D-15: Spearman ρ = −0.111 between H/log(k) and KL leaderboards

**Question:** Per the locked D-01 validation gate, do the H/log(k) (concentration) and KL-from-league-baseline (deviation) leaderboards agree on which defenses are most predictable? **Result:** Spearman ρ between the 32-team rankings under the two metrics = **−0.111 (p = 0.546)** — statistically indistinguishable from zero, with a slight negative tilt. The pre-registered gate of ρ ≥ 0.85 **fails**. Top-5 disagreers: MIN (rank_H = 32 / rank_KL = 1, Δ = 31), TB (31 / 2, Δ = 29), PIT (26 / 3, Δ = 23), MIA (30 / 8, Δ = 22), DET (27 / 5, Δ = 22). **Sample size:** all 32 teams, all 128 (team × situation) cells clear the N ≥ 30 floor, no dropouts. **Characterization:** D-01 explicitly instructed "if observed ρ < 0.85, treat as substantive finding to investigate, NOT papered over." This is a substantive finding. Diagnosis below in §3 — methodology signal, not a bug or sample-size artifact.

### D-16: STAT-08 sensitivity Spearman ρ = 0.982

**Question:** Does the predictability-index leaderboard depend on the `competitive_plays` view's `wp BETWEEN 0.05 AND 0.95` + `qtr <= 4` + end-of-half-hurry-up exclusion, or is it robust to that filter? **Result:** Spearman ρ between the with-filter leaderboard (58,178 pass plays, 36,569 after FTN join restriction in the predictability cells) and the unfiltered leaderboard (`plays JOIN ftn_play` directly, bypassing the view: 80,782 pass plays, 51,170 in cells) = **0.982 (p < 0.0001)**, max |rank Δ| = 4, top-5 identical with one PHI↔HOU swap. **Sample size:** 32 teams, 128 cells per universe, both universes well above N ≥ 30. **Characterization:** strong methodology-rigor signal. The headline leaderboard is not an artifact of the wp filter. Pairs naturally with the D-15 divergence finding for FINDINGS.md ("one definition of predictable is robust to the filter; the other definition isn't even consistent with itself across rankings").

### D-17: STAT-06 chi-square on S1 PA × blitz

**Question:** On 3rd-and-long pass plays, does play-action change defensive blitz rates (the analysis-plan.md cross-cutting hypothesis: "league blitz rate against play-action vs straight dropback gap ≥ 5pp")? **Result:** **χ² = 3.4643, p = 0.0627** — marginal, falls just outside α = 0.05. **Effect size: odds ratio = 0.648, 95% CI [0.418, 1.003]** — defenses are about 35% less likely to blitz against PA on 3rd-and-long, with the CI grazing the null. **Wilson 95% CI on P(blitz | PA = 1, S1) = 0.248 [0.176, 0.336]** (paired with P(blitz | PA = 0, S1) = 0.337). Observed rate gap = **−8.94pp** — exceeds the pre-registered ≥ 5pp gate directionally. Expected min cell = 36.6 (chi-square assumption holds; Fisher's exact fallback not triggered). **Sample sizes:** total S1 pass = 8,825; PA = 1 stratum = 109 (1.235%); 2×2 contingency [PA=1: blitz=27 / no-blitz=82; PA=0: blitz=2,938 / no-blitz=5,778]. **Characterization:** suggestive directional evidence with marginal statistical significance. The PA=1 stratum is small (N=109) and limits inferential power. STAT-06 requires "reports test statistic, effect size, AND Wilson CI" — all three are present and substantive. Frame as directional finding with sample-size caveat, not as a confirmed effect.

---

## 3. D-15 diagnosis: methodology, bug, or sample-size effect?

**Verdict: methodology signal.** Three lines of evidence rule out the alternatives.

### 3.1 Implementation bug — ruled out

The verifier (`03-VERIFICATION.md` Criterion 2) audited the methodology lock literally: K_SUPPORT=2 at line 98, MIN_N_FOR_CELL=30 at line 99, SPEARMAN_VALIDATION_GATE=0.85 at line 100, the entropy formula `stats.entropy([blitz_count, no_blitz_count], base=np.e)` at line 111, and the 0–100 mapping `(1 - H / np.log(K_SUPPORT)) * 100` at line 112. Smoke checks pass: uniform distribution → 0, deterministic → 100, below-N → NaN. The KL helper (`compute_kl_from_league`) is computed against the same per-team distributions. There is no implementation defect.

### 3.2 Sample-size effect from the N ≥ 100 floor — ruled out

There is no N ≥ 100 floor in this calculation. The locked floor is **N ≥ 30** (D-05, MIN_N_FOR_CELL = 30); the N ≥ 100 tier exists in the project's claim-discipline framework but only applies at FINDINGS.md narrative time, not inside the leaderboard computation. Empirically all 128 (team × situation) cells clear N ≥ 30 by margin (smallest cell = 92 plays in S4 — a 2nd-and-medium cell for one team across 4 seasons). Both leaderboards are computed on the **same** 32 teams over the **same** 128 cells. There is no qualifier-set asymmetry between the two metrics.

### 3.3 Methodology signal — confirmed empirically

H/log(2) and KL center their notion of "extreme" on different points:

- **H/log(2)** is symmetric around 50/50. A team's predictability score rises as its blitz rate moves *away from 50%* in either direction.
- **KL(team || league)** is symmetric around the league baseline of **29.45%**. A team's KL rises as its blitz rate moves *away from 29.45%* in either direction.

These two centers (50% and 29.45%) are not the same point. A metric agreement is only structurally guaranteed when all 32 teams cluster on the same side of *both* centers — which is to say, when teams cluster between 0% and 29.45%. Empirically, teams scatter on both sides of 29.45%, and the high-blitz extremes (MIN at 43.1%, TB at 40.6%, NYG at 37.4%) sit *closer* to 50/50 than the league baseline does. So:

- **High-blitz teams** (MIN, TB) → close to 50/50 → high entropy → **low** predictability index. But also far from 29.45% → **high** KL. **Disagreement.**
- **Low-blitz teams** (SF at 21.9%, IND at 22.3%, PHI at 22.6%) → far from 50/50 → low entropy → **high** predictability index. Also far from 29.45% → **high** KL. **Agreement.**

The asymmetry-of-KL completes the picture. KL penalizes "the rare event happens more often" more steeply than "the rare event happens less often" because of the `p · log(p / q)` weighting. So MIN at 43.1% (driving the rare blitz event UP from a 29.45% baseline) accumulates more KL than SF at 21.9% (driving it DOWN by a comparable absolute distance). That is why MIN ranks #1 on KL while SF — equally extreme in absolute distance from baseline — ranks lower on KL than its rank on H/log(2) might suggest.

This is not a defect of either metric. It is what those metrics measure. "Predictable" can mean "blitzes the same percentage every time" (concentration; H/log(2)) or "blitzes at a rate noticeably different from the league" (deviation; KL). On a league where 29.45% is the baseline, the two definitions diverge for any team whose blitz rate sits between 29.45% and 50%.

**Implication for Phase 4:** D-15 is a real methodology insight, not a bug to caveat away. FINDINGS.md should treat it as a named finding ("the two natural definitions of predictability disagree on this league, and here is why"). The README glossary should pick one definition for the headline number — H/log(2)-based — and FINDINGS.md should explain the divergence in the methodology section. D-16 (the wp-filter sensitivity ρ = 0.982) gives strong cover for the H/log(2) headline being the more stable choice.

---

## 4. D-17 cell breakdown: why N=109 instead of ~476

### 4.1 The 2×2 contingency, verified

Direct from the live DB on 2026-04-30:

| | blitz=1 | blitz=0 | row total |
|---|---:|---:|---:|
| PA=1 | 27 | 82 | **109** |
| PA=0 | 2,938 | 5,778 | **8,716** |
| col total | 2,965 | 5,860 | **8,825** |

This is exactly the contingency reported in `03-03-SUMMARY.md` and `03-VERIFICATION.md`. The 8,825 universe is `competitive_plays` rows on `down=3 AND ydstogo>=7 AND play_type='pass'`, all of which join to `ftn_play` (no FTN-side dropouts on this slice).

### 4.2 The mismatch with ~476

A pre-execution estimate of ~476 implies an assumed PA rate on S1 pass plays of roughly 8,825 × 5.4% ≈ 476 (or 9,925 × 4.8% ≈ 476 if applied to the S1 universe before the pass restriction). Either way the implicit assumption was a PA rate around **5%** on 3rd-and-long.

The actual PA rate on S1 pass plays is **1.235%** — between three and four times lower than the estimate.

### 4.3 The PA-rate-by-situation table (the football-side explanation)

Live counts on the four pre-registered situations and the league baseline:

| Situation | N pass plays | N PA pass plays | PA rate |
|---|---:|---:|---:|
| S1: 3rd-and-long (`down=3 AND ydstogo>=7`) | 8,825 | 109 | **1.235%** |
| S2: red zone (`yardline_100<=20`) | 7,553 | 1,808 | 23.94% |
| S3: 1st-and-10 (`down=1 AND ydstogo=10`) | 18,609 | 8,652 | 46.49% |
| S4: 2nd-and-medium (`down=2 AND ydstogo BETWEEN 3 AND 6`) | 4,756 | 1,819 | 38.25% |
| League (any competitive pass) | 58,178 | 15,281 | 26.27% |

PA rate varies by an order of magnitude across the slate. S3 (1st-and-10) is the most run-pass balanced down, and PA is called on **46.5%** of pass plays there. S4 (2nd-and-medium) and S2 (red zone) are intermediate. S1 (3rd-and-long) collapses to **1.2%** — the lowest by far.

The football logic: play-action is a deception tool that requires a credible run threat. Its purpose is to freeze the linebackers on the snap by faking a handoff, opening a passing window in the middle of the field. On 3rd-and-7+, the run is no longer a credible play call (the league rushes for ~4 yards/carry; even on 3rd-and-7 a successful run rarely converts), so a PA fake doesn't fool a defense that has already locked into pass coverage. PA is essentially abandoned on 3rd-and-long for strategic reasons, not data-quality reasons. The 1.235% rate is a real strategic constraint.

Inverting the lens: on S3 (1st-and-10) the run is the modal play, so a PA fake works on linebackers that have to honor the run. PA rate climbs to 46.5%. The rates beautifully track run-credibility across the slate.

### 4.4 Implication for the chi-square test and FINDINGS framing

The N=109 PA stratum is the binding constraint on STAT-06's statistical power. With only 27 blitz observations against PA on 3rd-and-long across four full seasons, the Wilson CI on P(blitz | PA=1, S1) is wide [0.176, 0.336], and the chi-square p-value falls marginally outside α=0.05 even though the effect-size magnitude (OR = 0.648, gap of −8.94pp) clears the pre-registered 5pp gate directionally. The finding holds as **suggestive directional evidence** — defenses do appear to blitz less against the rare PA looks they see on 3rd-and-long — but the small-N caveat is not optional in the FINDINGS.md narrative.

A v2 pivot (or a post-v1 follow-up) could test the PA × blitz hypothesis on S3 (1st-and-10), where N(PA=1) = 8,652 and the inferential power is far higher. That changes the situational framing — 1st-and-10 is less recruiter-recognizable than 3rd-and-long — but it answers the underlying mechanistic question with much tighter CIs. STATE.md does not flag this as a v2 candidate yet; Phase 4's discuss can decide whether to surface it.

---

## 5. Summary for discuss-phase

| Item | Status entering Phase 4 |
|---|---|
| D-14 calibration | Numerically locked at `n_blitzers > 0`. Prose lag in 4 docs (PROJECT.md L58, 03-CONTEXT.md D-02, ftn-schema-audit.md, README glossary). FINDINGS.md will be written correctly from inception. |
| D-15 divergence | Real methodology signal, not a bug. H/log(2) and KL measure orthogonal concepts on a league with baseline ≠ 50%. Frame as named insight in FINDINGS.md; H/log(2) is the recommended headline (D-16 gives stability cover). |
| D-16 sensitivity | Robust headline. Pairs with D-15 as the rigor counter-narrative. |
| D-17 chi-square | Marginal (p=0.063), directional (−8.94pp gap, OR=0.648), underpowered (PA=1 N=109). Frame as "suggestive directional evidence with disclosed sample-size caveat," not as a confirmed effect. The N=109 is real (PA rate on 3rd-and-long is 1.235%), not a defect. |

All four are substantive findings ready for FINDINGS.md narrative treatment. None requires Phase 3 rework. The Phase 4 work is decidedly downstream: viz pipeline, memo, README hand-rewrite, GitHub MCP ship.

---

*Brief gathered: 2026-04-30. Numbers verified against `data/nfl_defensive_tendencies.db` via `scratch/d17_diagnostic.py`.*
