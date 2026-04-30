# Phase 4: Story & Ship (Viz + Docs + Public GitHub) — Context

**Gathered:** 2026-04-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 delivers the recruiter-facing surface — the visualization pipeline, the FINDINGS.md memo, the hand-written README, the GitHub Actions lint workflow, and the public GitHub repo created via the GitHub MCP. The 21 requirements (VIZ-01..05, DOC-01..08, SHIP-01..08) collapse to four artifact streams:

1. **Viz pipeline.** `analysis/03_visualizations.ipynb` exports through `_style.py` rcParams, producing `findings/images/01_predictability_ranking.png` (hero leaderboard, VIZ-02), `findings/images/02_kl_vs_h_scatter.png` (second viz, VIZ-03), and a 1280×640 social-preview PNG derived from the hero leaderboard at top-12 density.
2. **FINDINGS.md memo.** Six named insights with a locked sequence (leaderboard → D-15 divergence → S1 chi-square pre-registered → S3 chi-square exploratory → red-zone pressure → team-level beat); three-thematic-block methodology section; four appendix tables; five-item limitations section; FTN + nflverse CC-BY-SA attribution.
3. **README hand-rewrite + cross-doc prose reconciliation sweep.** Fills the placeholder skeleton (hero PNG above the fold, 5-command setup, 6-term glossary, Mermaid data-flow diagram, attribution, Known Issues). Carries the **D-14 cross-doc reconciliation sweep** (PROJECT.md L58, 03-CONTEXT.md D-02, docs/ftn-schema-audit.md operational definition, README glossary) plus the **README-hook S1-vs-cross-situation reconciliation** (current "on third-and-long" wording is inconsistent with the cross-situation leaderboard).
4. **Ship sequence via GitHub MCP.** Single GitHub Actions workflow (`ruff` + import smoke + SHIP-08 placeholder regex); private-then-flip repo creation; description + 8 topics + MIT license + branch protection requiring SHIP-01 to pass; social preview + profile pin via MCP-or-UI fallback; non-author browser verification on incognito desktop + mobile.

The S3 exploratory chi-square is a new analytical deliverable that did not exist in Phase 3. It is appended to `analysis/02_predictability_modeling.ipynb` during Phase 4 execution and feeds insight #4.

**Out of scope (carried by Phase 3 or v2):** any Phase 3 analytical rework, any v2 enrichments (per-anchor parallel indexes, PA-stratified index, Cramér's V, week-over-week drift, `nflreadpy` migration, ngs-derived coverage labels), any new statistical tests beyond S3, any tracking/film data.

</domain>

<decisions>
## Implementation Decisions

### A. FINDINGS.md narrative architecture (insights spine)

- **D-01 Six named insights, locked count.** Five leaves real material on the floor (no team-level texture for a 32-team ranking project); seven promotes the D-14 calibration alongside analytical findings (inflates a process story into a peer with the actual results). Six with D-14 + D-16 in methodology section is the right balance.

- **D-02 Locked insight sequence.** Insight #1: predictability leaderboard (headline). Insight #2: D-15 H/log(2) vs KL divergence (Spearman ρ = −0.111; named methodology finding). Insight #3: S1 PA × blitz chi-square (pre-registered; directional, marginal). Insight #4: S3 PA × blitz chi-square (exploratory follow-up; new Phase 4 deliverable). Insight #5: red-zone pressure differential (QUERY-03; +9.5pp gap). Insight #6: team-level pressure beat (DET 52.3% blitz on S1 candidate from QUERY-05; verify "DET is the league leader" empirically during execution before committing the team to the prose). The leaderboard leads, not D-15 — README sells the leaderboard, the hero chart IS the leaderboard, and leading FINDINGS with D-15 creates a structural mismatch where README and memo point in different directions. D-15 lands at #2 as methodological confirmation that the leaderboard's metric choice (H/log(2)) was deliberate.

- **D-03 D-14 + D-16 land in the methodology section, NOT as named insights.** D-14 (n_blitzers calibration) is a process story; promoting it to a named insight inflates rigor framing into a peer with the analytical findings. D-16 (sensitivity ρ = 0.982) is the rigor counterweight to D-15; it pairs naturally with the metric-choice rationale in the methodology section.

- **D-04 S1 + S3 stay separate insights, not merged.** Same mechanism, different samples, different methodological status (pre-registered vs exploratory). The labeling — explicit "pre-registered" tag on S1 and explicit "Exploratory; not pre-registered in `docs/analysis-plan.md`" tag on S3 — IS what carries the rigor signal. Merging them into one insight collapses the labeling.

- **D-05 Insight-internal γ shape: fixed 3-sentence template + length tiers.** Every insight follows claim → evidence → implication/caveat. The evidence sentence is allowed to expand (leaderboard's evidence becomes a top-3+bottom-3+league-mean line; D-15's evidence becomes a 2-row rank-delta example pair; the rest stay one sentence). The third sentence (implication/caveat) is **mandatory for every insight, not optional**. If a finding feels "clean" at authoring time, the caveat sentence still ships — framed as scope ("This pattern holds across all four seasons in the dataset; pre-2022 trend not assessed") or generality ("Per-team rates vary; see appendix T1 for full distribution") rather than as a weakness. The methodological-honesty beat is what gives the memo consistent rigor signal across all six insights.

### B. TL;DR (memo opener)

- **D-06 Shape: γ hybrid — short framing paragraph + 4 highlight bullets.** ~250 words target, not 300. Every word past ~270 starts working against the "first 30 seconds" purpose.

- **D-07 Framing paragraph names the four pre-registered situations explicitly.** Plants the rigor flag (pre-registered slate) before the numbers land.

- **D-08 D-15 divergence previewed in one sentence in the TL;DR.** Prevents a recruiter who reads only the TL;DR from walking away thinking the project is one-dimensional. Does NOT bury the leaderboard headline — leaderboard still leads, divergence is a one-line preview pointing at insight #2.

- **D-09 Leaderboard depth: top-3 + bottom-3 in a single scannable line + league average.** Format: "Top 3 (most predictable): TEAM_A (X.X), TEAM_B (Y.Y), TEAM_C (Z.Z). Bottom 3: TEAM_X (A.A), TEAM_Y (B.B), TEAM_Z (C.C). League average: M.M." One bullet, six teams, scannable. README sells the headline pair; FINDINGS earns its slot in the recruiter's read by giving texture they didn't see on the README.

### C. S3 exploratory chi-square (new Phase 4 analytical deliverable)

- **D-10 Universe and 2×2 spec.** `competitive_plays JOIN ftn_play USING (game_id, play_id)` on `down=1 AND ydstogo=10 AND play_type='pass'`. Verified count: N = 18,609 pass plays; N(PA=1) = 8,652 (46.49%); N(PA=0) = 9,957. 2×2 contingency: `is_play_action × (n_blitzers > 0)`. Reporting: chi² + p-value, expected min cell, odds ratio + 95% CI, Wilson 95% CI on `P(blitz | PA=1, S3)`, paired `P(blitz | PA=0, S3)`, observed pp gap. Identical reporting structure to the S1 cells in `02_predictability_modeling.ipynb`.

- **D-11 OR delta between S1 and S3 reported as first-class output.** The narrative depends on direction agreement; make the comparison visible rather than leaving it for the reader to extract from two separate test reports. Compute and print the OR delta (and a CI for the delta if implementable closed-form; otherwise just the point estimate) in the same cell that produces the S3 result.

- **D-12 Append to `02_predictability_modeling.ipynb`, not a separate notebook.** Cell-level `# EXPLORATORY — NOT pre-registered in docs/analysis-plan.md` comment carries the rigor signal; physical separation into a standalone notebook adds bureaucratic distance without analytical value, and the methodology appendix's "all chi-squares run" enumeration reads more cleanly when both tests live in one place.

- **D-13 Five-scenario decision rule for the S3 result, pre-locked.** Decisions:
  - Scenario 1 — confirms with significance: `p < 0.05 AND OR < 1`.
  - Scenario 2 — confirms at marginal significance: `0.05 ≤ p < 0.10 AND OR < 1`.
  - Scenario 3 — contradicts: `OR > 1`, regardless of p (and surface the p separately).
  - Scenario 4 — null: `p ≥ 0.10 AND 0.85 ≤ OR ≤ 1.18` (within ~15% of OR=1).
  - Scenario 5 — directional but inconclusive: `p ≥ 0.10 AND OR < 0.85`.

- **D-14 Three-sentence structural shape per scenario, pre-locked.** Sentence 1 states the S3 result with numbers. Sentence 2 makes the explicit cross-situation comparison with S1, using the OR delta from D-11. Sentence 3 is the implication (what this tells us about defensive behavior or the limits of the pre-registered analysis).

- **D-15 Author the prose at execution time, not in the plan.** Pre-locked rule + structure protects against post-hoc rationalization without forcing stiff phrasing. Author-time prose can engage with the actual numbers; pre-locked prose can't.

### D. Methodology section + appendix + limitations

- **D-16 Methodology section: γ shape, three thematic prose blocks.**
  1. **Metric choice & calibration** — combines D-14 (`n_blitzers > 0` calibration story; the FTN-vs-nflfastR column-encoding catch) with the H/log(2) formula derivation + 0–100 inverted mapping rationale.
  2. **Sensitivity & robustness** — D-16 sensitivity ρ = 0.982 (leaderboard robust to the `competitive_plays` wp/qtr filter); pairs with the D-15 framing in insight #2 to do the rigor counterweight.
  3. **Sample-size discipline & pre-registered firewall** — combines the tiered N≥30/100/15-flag framework + `min_n_filter` behavior + all-128-cells-clear stat with the S1/S3 firewall + pre-registered/exploratory protocol.

- **D-17 Methodology appendix tables: T1–T4 ship; T5 + T6 skip.**
  - **T1: Per-team-per-situation predictability cells** — multi-value cell table with blitz rate, N, and predictability scalar per (team × situation). NOT a single-value heatmap; the executor builds it as a multi-column table so a skeptical reader can replicate cell values directly. Supports insights #1 + #2.
  - **T2: KL leaderboard with rank-delta vs H/log(k).** Evidences D-15 directly (full 32-team rank disagreement table).
  - **T3: STAT-08 sensitivity rank-delta table** — with-filter (`competitive_plays`) vs without-filter leaderboards; max |delta|; Spearman ρ. Evidences D-16.
  - **T4: S1 + S3 contingency tables paired** — the actual 2×2 cells behind insights #3 + #4. Lets a skeptical reader compute the chi-square + OR + Wilson CI by hand.
  - T5 (per-team blitz rate + N + SD across situations) skipped — redundant with T1.
  - T6 (stack/version + SQL slate index) skipped — README territory, not FINDINGS appendix.

- **D-18 Limitations section: 5 named items.** L1 (no paid FTN coverage labels — Cover 0–6, man/zone), L2 (4-season scope 2022–2025; no pre-2022 longitudinal trend), L3 (PA rate on 3rd-and-long is 1.235% in this dataset → S1 chi-square underpowered → S3 exists as exploratory follow-up), L4 (FTN charter subjectivity on `is_play_action` / `is_rpo`), L6 (tabular-only data; no player-tracking or film coverage). **L5 (`nfl_data_py` archival) skipped from FINDINGS limitations** — that is a reproducibility note for future maintainers, not an analytical limitation; it lives in the README's `## Known Issues` section per DOC-07.

- **D-19 L3 prose constraint.** L3 must explain WHY PA collapses on 3rd-and-long: play-action requires a credible run threat to freeze linebackers; on `down=3 AND ydstogo>=7`, the run is no longer a credible play call, so the PA fake doesn't fool a defense already locked into pass coverage; PA is therefore strategically abandoned. The 1.235% PA rate is a real strategic constraint, not a data-quality issue. One concrete sentence beats a vague hedge.

- **D-20 L4 prose constraint.** L4 must acknowledge the limitation's own boundary: FTN does not publish inter-rater reliability statistics for `is_play_action`, so we cannot bound the impact of charter subjectivity quantitatively. Frame as honest about what isn't known rather than papering over the limitation.

### E. VIZ-03 — second visualization (KL-vs-H rank-rank scatter)

- **D-21 VIZ-03 satisfaction.** Read the requirement's parenthetical "(heatmap or small-multiples grid)" as illustrative, not restrictive. The KL-vs-H rank-rank scatter is non-bar-chart and adds analytical depth → VIZ-03 satisfied on its own. The plan documents the rationale in a one-line note: "VIZ-03 satisfied via the KL-vs-H rank-rank scatter." Adding a third chart for completeness dilutes the recruiter's read.

- **D-22 Rank-rank scaffold (B), inverted axes.** Both axes show rank 1 at top-left (rankings convention: 1st place at the visual top, matching every reader's mental model from sports leaderboards). The y=x diagonal still serves as the agreement reference; the "natural-axes" stats convention argument is purely cosmetic and pulls against rankings intuition. Axis labels make direction unambiguous: "Rank 1 = most predictable" / "Rank 1 = most extreme deviation from league baseline."

- **D-23 y=x diagonal drawn as a light-gray reference line, labeled.** Label reads "perfect agreement (ρ = 1.0)" or equivalent. Drawing the line explicitly does the explaining work — a scatter without the diagonal forces the recruiter to mentally construct where agreement would sit. The contrast between the dashed reference and the actual scatter cloud IS the finding made visible.

- **D-24 Eight callouts via `adjustText` (or equivalent label-placement library).** Top-5 disagreers (MIN, TB, PIT, MIA, DET — rank Δ ≥ 22) plus the three leaderboard anchors from the FINDINGS TL;DR (PHI, SF, IND). Eight unique labels (MIN and TB are double-duty: top-5 disagreers AND bottom-3 of the leaderboard). Label placement via `adjustText` (or matplotlib equivalent) so the executor doesn't hand-place and end up with overlap on a 200 DPI export. The eight teams carry both insights (divergence + headline anchors) in one chart, which is what makes D-15 feel structural rather than anecdotal.

- **D-25 Title + subtitle.** Title: "Two Definitions of Predictable Disagree" (the finding made standalone-readable; "on This League" trimmed — the subtitle's "32 NFL defenses, 2022–2025" carries scope). Subtitle: "Spearman ρ = −0.111 between H/log(2) and KL-from-league-baseline rankings; 32 NFL defenses, 2022–2025."

- **D-26 File spec.** `findings/images/02_kl_vs_h_scatter.png`, 8×8" square @ 200 DPI, color/style from `_style.py` (`apply_style()`, `'colorblind'` palette).

### F. VIZ-02 — hero leaderboard chart + SHIP-04 social preview

- **D-27 Chart type: horizontal bar chart, 32 plain-text team codes (PHI, SF, IND, ...).** Logos add trademark concerns to a public portfolio repo and fragment the visual rhythm. Plain-text codes match the audience (data-analyst recruiters; non-football fluency assumed) and keep the chart visually quiet.

- **D-28 Color encoding: highlight extremes.** Top-3 in one accent color, bottom-3 in a deliberately-non-red palette color (muted orange, dark teal, or similar — picked from `_style.py`'s colorblind palette). Red signals "these teams are failing," which isn't the finding — least predictable does not mean worst defense; it means "blitzes at a rate close to 50/50, hardest to anticipate." Middle 26 in neutral gray. Reinforces the FINDINGS TL;DR top-3+bottom-3 rollup with a parallel visual cue.

- **D-29 League-average reference line + label, placed away from bars.** Vertical dashed line at the league mean (computed empirically; ~12.5 given league blitz rate of 29.45%). Label "League avg = 12.5" placed at bottom of chart or upper-right corner away from the top-ranked bars to avoid collision.

- **D-30 Axis scale: fixed 0–100 (the metric's theoretical range).** Truncating to 0–30 makes PHI's ~23.5 score look near-maximum when it is actually below a quarter of the metric's range. The "empty space" past the top bar isn't wasted — it shows that NFL defenses cluster at the low end of the metric, that no team approaches perfect predictability, and that team-to-team spread is small relative to the metric's range. Truncated axes are a known visual rhetoric tell; recruiters with statistical training notice and discount the chart. Full 0–100 reads as honest at a glance.

- **D-31 Score annotations on top-3 + bottom-3 only at one decimal precision** (e.g., "23.5"). Same six teams highlighted by D-28; pairing color + score-annotation creates one coherent emphasis pattern. Two decimals reads as false precision on a 0–100 scale; integer rounding loses signal between adjacent teams whose decimal differences are real. Middle 26 teams readable via bar length and X-axis ticks.

- **D-32 Title + subtitle.** Title: "Some NFL Defenses Are More Predictable Than Others" — finding-framed, data-stable, matches the README hook so a recruiter who lands on the social preview gets the same opener as the README. **"on third-and-long" is trimmed** because the chart aggregates across all four pre-registered situations, not S1 specifically. Subtitle carries scope and methodology: "32 NFL defenses, blitz rate on 4 pre-registered situations, 2022–2025; 0–100 predictability index, higher = more predictable."

- **D-33 Hero file spec.** `findings/images/01_predictability_ranking.png`, portrait ~8×11" @ 200 DPI, colors/fonts from `_style.py`.

- **D-34 Social preview LOCKED at top-12 only at 1280×640 (NOT a fallback).** Readability math at 32 bars in 640 px height (after title + subtitle + axis labels + padding) yields ~12–13 px per bar — technically valid, practically unreadable on the platforms social previews actually appear on (LinkedIn, Slack, Twitter cards crop and compress further). Top-12 at 1280×640 yields ~40 px per bar, comfortable. Title parenthetical "(Top 12)" carries the scope honestly; subtitle adds "Most Predictable Defenses 2022–2025." Same data source, same metric, same color scheme, same `_style.py` pipeline as the hero — just thumbnail-appropriate density. Recruiters clicking through get the full leaderboard. The "top-12 as fallback" framing creates execution-time ambiguity (executor would converge on "32 bars at 13 px is just barely readable enough"); locking top-12 as the design eliminates that drift.

### G. Public repo surface (SHIP-03..05 — repo creation, topics, license, branch protection)

- **D-35 Description.** "Defensive blitz-rate predictability across 32 NFL defenses, 2022-2025" (69 chars). Use a regular hyphen ("2022-2025"), not an en-dash — GitHub's Unicode handling in repo descriptions is inconsistent across rendering contexts.

- **D-36 Topic list (8, max ceiling).** `nfl-analytics`, `data-analysis`, `python`, `sqlite`, `jupyter`, `nfl-data-py`, `sports-analytics`, `nflverse`. The `nflverse` umbrella is the discoverability hook for the broader football-analytics community; `nfl-data-py` is the package name for users searching the specific dependency. Both serve different audiences.

- **D-37 License: MIT.** Convention for analytical/portfolio Python projects. The data-license note (FTN + nflverse under CC-BY-SA 4.0) lives in the README's Attribution section per DOC-07 — no data ships in the repo (`.db` gitignored, parquet cache gitignored, only `data/README.md` is tracked), so the LICENSE file applies only to the user's code.

- **D-38 No CONTRIBUTING.md, no CODE_OF_CONDUCT.md.** A solo portfolio repo with zero issues, zero stars, no community does not earn either file. The signal a recruiter wants — process applied to real work — comes from `.planning/` artifacts, atomic commit history, the SPEC/REQUIREMENTS/ROADMAP flow, and the verifier reports. CONTRIBUTING.md on a solo repo is process cosplay; the contrast against the real artifacts hurts recruiter signal. Branch protection + CI + clean commits do the legitimate version of the same signal without the cosplay tax.

- **D-39 Branch protection on `main`: single rule "require status checks to pass before merging," gated on the SHIP-01 GitHub Actions workflow.** Forces self-merges through PRs that pass CI; signals professionalism with light overhead.

### H. Ship execution sequence (Plan 04-03 mechanics for SHIP-03..07)

- **D-40 Visibility flow: private-then-flip.** MCP `create_repository` with `private: true`. Push code. Verify on the actual GitHub-rendered surface. Then flip to public via separate MCP call. SHIP-08 placeholder regex catches placeholder text; private staging adds an eyeball pass on the actual GitHub rendering (Mermaid diagram, hero PNG embedded, attribution links resolve, mobile viewport works) before the repo becomes recruiter-visible.

- **D-41 Verification spec — Mermaid diagram specifically eyeballed.** GitHub's Mermaid renderer sometimes diverges from local previews on edge cases (Unicode, certain edge label patterns); eyeball the rendered Mermaid against intent. "README displays" is not a sufficient check.

- **D-42 Non-author verification (SHIP-07): incognito desktop + mobile.** Incognito desktop verifies repo is actually public and accessible to anonymous visitors. Mobile verifies the recruiter-glance experience (30–50% of recruiter views happen on phone) AND the social-preview crop rendering on platform cards (LinkedIn, Slack, GitHub mobile crop the 1280×640 image differently than desktop). 30-second mobile check catches edge-cropping issues.

- **D-43 GitHub MCP capability + fallback policy: both paths documented up front.** Plan 04-03 specifies "via MCP if supported, manual UI step if not" for SHIP-04 (social preview upload) and SHIP-05 (profile pin). These MCP capabilities are not standard across all GitHub MCP implementations. The chosen path (MCP or UI) is logged in the verification report so future-self or a recruiter inspecting the planning artifacts sees a real engineering record, and the next person running this knows what path to expect.

### I. CI workflow scope (SHIP-01 + SHIP-08 enforcement)

- **D-44 Single workflow file, single job, sequential steps.** `.github/workflows/ci.yml` (or equivalent) with one job containing: checkout → setup-python 3.11 → `pip install -r requirements.txt` → `ruff check` → import smoke (`python -c "import etl, analysis"` or equivalent loading both `etl/*.py` and `analysis/_common.py` + `analysis/_style.py`) → SHIP-08 placeholder regex grep on `README.md` and `findings/FINDINGS.md` (`! grep -qE '<[A-Z_]{4,}>' <file>`). Multi-job parallelization triples compute spend (each job pays its own setup-python + install) for ~30 sec wall-clock saving; on a portfolio repo the simplicity wins.

- **D-45 Triggers: push to `main` + PRs targeting `main`.** Branch protection (D-39) requires status checks on PRs to gate merges; push-only would break that flow. Scheduled weekly runs skipped — they create notification surface for a risk (dep drift on archived `nfl_data_py`) that's unactionable until the v2 effort. Anxiety without action.

- **D-46 Concurrency control.**
  ```yaml
  concurrency:
    group: ${{ github.workflow }}-${{ github.ref }}
    cancel-in-progress: true
  ```
  Cancels in-flight runs when a new push to the same branch arrives. Cleaner CI history, faster feedback on the latest commit, no wasted compute on superseded commits during rapid Phase 4 polish iterations.

- **D-47 SQL static checks (option γ) skipped.** Parsing `queries/*.sql` headers and validating QUERY-09 meta-compliance in CI duplicates what `scripts/_verify_queries_run.py` catches locally before push. CI's marginal value over the manual pre-push step is small.

### J. D-14 cross-doc reconciliation (sweep timing + extent)

- **D-48 D-14 reconciliation folds into Plan 04-02 README hand-rewrite, alongside README-hook reconciliation.** Single editorial sweep, one mind on prose coherence across all four files, with the FINDINGS-narrative context fresh. Files updated to `n_blitzers > 0`: PROJECT.md L58 (Domain Primer operational definition), 03-CONTEXT.md D-02 (the locked decision text), `docs/ftn-schema-audit.md` (operational definition for the anchor dimension), README glossary entry. README hook ("predictable than others on third-and-long") reconciled in the same sweep — generalize to cross-situation framing or commit to S1 as the prose anchor (planner's call given the FINDINGS structure).

- **D-49 Post-sweep repo-wide grep confidence check.** After updating the four known prose locations, run a repo-wide grep for `n_blitzers > 4` and variants (e.g., `> 4 rushers`, "n_blitzers > 4"). One-second confidence check that nothing was missed. Surface the grep results (zero matches expected) in the verification log.

### Claude's Discretion

The user explicitly delegated these to executor judgment with documented defaults:

- **Memo length budget.** Implied by the locked structure (TL;DR ~250 words + 6 insights × 3-sentence template with evidence-tier expansion + 3 thematic methodology blocks + 4 appendix tables + 5-item limitations + attribution). Working target ~3000 words; trim aggressively — a recruiter-friendly memo respects 30-second skim + 5-minute read modes.
- **Plan structure (3 vs 4 plans).** Planner-phase decision. ROADMAP suggests 3 (04-01 Visualizations, 04-02 Documentation, 04-03 Ship). The planner can split docs into 04-02a (FINDINGS) + 04-02b (README + cross-doc sweep) if the FINDINGS detail warrants, but this discuss locks the WHAT, not the HOW-many-plans.
- **Specific prose voice for each insight, methodology block, limitation, transition.** Author at execution time per the structural locks. Pre-locked rule + structure (D-05, D-13, D-14) protects against post-hoc rationalization without forcing stiff phrasing.
- **Mermaid diagram exact node labels and orientation.** Executor authors per data flow at execution time. Suggested flow: `nfl_data_py` → parquet cache → SQLite → `competitive_plays` view → SQL queries → notebooks → PNG → README.
- **Specific axis labels, tick formatting, and color hex values on viz.** Per `_style.py` defaults. Executor picks specific top-3/bottom-3/league-avg accents from the colorblind palette per D-28 (no red).
- **CI workflow exact filename.** `.github/workflows/ci.yml` is the convention default; executor may use a different name if there's a reason.
- **Insight-to-insight transition prose.** No pre-locked transitions. Executor authors at execution time so prose can engage with the actual numbers.
- **DET-as-team-level-beat empirical verification.** Insight #6 names DET at 52.3% as the candidate from QUERY-05; executor verifies at execution time that DET is still the league leader on S1 (and updates the prose if a different team emerges).

### Folded Todos

None — STATE.md "Pending Todos" was empty going into this phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents (gsd-phase-researcher, gsd-planner, gsd-executor) MUST read these before planning or implementing.**

### Project-level constraints (read first)

- `CLAUDE.md` — Locked stack; file-organization rules (`/analysis`, `/queries`, `/findings`, `/docs`; never repo root); audience voice (memo not tutorial; numbers first; no AI emoji headers; FTN+nflverse attribution mandatory; limitations section mandatory). The "When in Doubt" pointer to PROJECT.md + research/SUMMARY.md applies here.
- `.planning/PROJECT.md` — Vision, Out of Scope, Key Decisions table. **D-09 (repo name `nfl-defensive-tendencies`)** governs Plan 04-03 SHIP-03 repo creation. **D-10 (4-season scope 2022–2025)** is the dataset framing for FINDINGS.md TL;DR + methodology. **PROJECT.md L58 carries a stale `n_blitzers > 4`** — Plan 04-02 reconciles to `> 0` per D-48.
- `.planning/REQUIREMENTS.md` — VIZ-01..05, DOC-01..08, SHIP-01..08 acceptance criteria. SHIP-08 regex spec (`! grep -qE '<[A-Z_]{4,}>' <file>`) is enforced by the SHIP-01 workflow per D-44.
- `.planning/STATE.md` — Substantive findings D-14..D-17 (n_blitzers calibration, Spearman gate failure, sensitivity robustness, S1 PA×blitz chi-square). These are the analytical inputs Phase 4 narrates.
- `.planning/ROADMAP.md` §Phase 4 — Phase boundary, 21 reqs, success criteria 1–6, in-phase parallelism ("04-01 Viz is the serial prerequisite; 04-02 docs and 04-03 ship-skeleton parallelize after; SHIP-03..05 are strictly serial after 04-02 completes").

### Phase 4 internal references

- `.planning/phases/04-story-and-ship/04-PRE-DISCUSS-BRIEF.md` — **The factual record on D-14..D-17 + n_blitzers correction.** Phase 4 narrative authoring reads numbers and rationale from here, not from STATE.md (which is more compressed). The brief's §3 (D-15 diagnosis: methodology signal) and §4 (D-17 cell breakdown: PA rate by situation table) are direct inputs to FINDINGS.md insights #2 + #3 + #4 + L3.

### Pre-registered analytical scope (the firewall)

- `docs/analysis-plan.md` — **THE locked situational slate.** S1/S2/S3/S4 filters, falsifiable hypotheses, cross-cutting PA modifier, sample-size discipline tiers, live N counts. Phase 4's S3 exploratory chi-square does NOT amend this doc — the slate stays at 4 pre-registered + 1 cross-cutting modifier; S3 ships explicitly outside the pre-registered firewall as exploratory. The methodology section explains the firewall and the labeling protocol per D-16 block 3.
- `docs/ftn-schema-audit.md` — Anchor dimension narrative; **operational definition `blitz = n_blitzers > 4` is stale**. Plan 04-02 reconciles to `> 0` per D-48.

### Phase 3 outputs (Phase 4 reads from these)

- `.planning/phases/03-analytical-layer-sql-python/03-CONTEXT.md` — Phase 3 D-01..D-13 (predictability index design, 8-query slate, chi-square + Wilson CI + sensitivity). **D-02 contains stale `n_blitzers > 4`** — Plan 04-02 reconciles per D-48.
- `.planning/phases/03-analytical-layer-sql-python/03-VERIFICATION.md` — Verifier report; documents D-14..D-17 as substantive findings, not gaps. Confirms all 17 REQ-IDs satisfied + all 5 ROADMAP success criteria PASS.
- `.planning/phases/03-analytical-layer-sql-python/03-02-SUMMARY.md` — Empirical row counts from QUERY-01..08: league blitz rate 29.4%, DET 52.3% S1 (insight #6 candidate), RZ pressure 36.2% vs midfield 26.7% (insight #5).
- `.planning/phases/03-analytical-layer-sql-python/03-03-SUMMARY.md` — Predictability scalar leaderboard (top-5: PHI 23.53, SF 23.48, IND 22.37, HOU 22.01, TEN 21.61; bottom-5: NE 6.54, KC 6.21, MIA 5.91, TB 4.07, MIN 1.53), KL gate failure (ρ = -0.111), chi-square (χ² 3.4643, p 0.0627, OR 0.648 [0.418, 1.003], Wilson [0.176, 0.336], N=109), STAT-08 sensitivity (ρ = 0.982, max |delta|=4).

### Code Phase 4 imports / extends

- `analysis/_common.py` — `SEED=42`, `DB_PATH`, `get_conn()`, `min_n_filter()`. The viz notebook imports the lot.
- `analysis/_style.py` — `apply_style()` with savefig.dpi=200, `'colorblind'` palette. Both VIZ-02 hero + VIZ-03 scatter use.
- `analysis/02_predictability_modeling.py` (and paired `.ipynb`) — **Where the S3 exploratory chi-square cells are appended per D-12.**
- `queries/01..08_*.sql` — Numerical inputs to FINDINGS narrative (insights #5 and #6 cite QUERY-03 and QUERY-05 directly).
- `data/nfl_defensive_tendencies.db` — Phase 4 reads only (no writes); recruiter regenerates via `python -m etl.run`. **Gitignored** — never `git add -f`.
- `README.md` — Existing skeleton with placeholder slots (`<MOST_PREDICTABLE_DEFENSE_2025>`, `<SCORE>`, `<DELTA>`); Plan 04-02 hand-rewrites + reconciles per D-48.
- `requirements.txt`, `pyproject.toml`, `.python-version` — Locked stack; Plan 04-03 SHIP-02 fresh-venv reproducibility script verifies these install cleanly.

### Research backbone (read for narrative authoring)

- `.planning/research/SUMMARY.md` — TL;DR + Resolved Disagreements; signals which methodology choices the project pre-committed to (entropy normalization, sample-size discipline, SQLite ETL).
- `.planning/research/PITFALLS.md` — **#18 placeholder ship-guard** (SHIP-08 regex enforcement); **#11 entropy normalization** (D-01 closes); **#9 multiple-comparisons trap** (the 4-situation firewall + S3 explicit exploratory labeling per D-04 + the methodology section block 3 per D-16); **#20 pandas pin alignment** (verified clean in Phase 1 D-09 era).
- `.planning/research/FEATURES.md` — Anti-features list (no Streamlit, no excessive viz; FINDINGS.md is memo not tutorial). Applies directly to FINDINGS authoring voice.
- `.planning/research/STACK.md` — `seaborn==0.13.2` for the scatter; `matplotlib` for both viz; `numpy<2.0` constraint; `scipy.stats.spearmanr` for the existing D-15 / D-16 computations Phase 4 reads.
- `.planning/research/ARCHITECTURE.md` — `findings/` directory layout; notebook output discipline (clear-output before commit; figures live only in `findings/images/`).

### No external ADRs

This project doesn't use a `docs/decisions/adr-*.md` system. Decisions live in PROJECT.md Key Decisions and these CONTEXT.md files.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`analysis/_common.py`** — `SEED=42`, `DB_PATH`, `get_conn() -> sqlite3.Connection`, `min_n_filter()`. Phase 4 viz notebook imports all four.
- **`analysis/_style.py`** — `apply_style()` setting `savefig.dpi=200` + colorblind palette + font sizes. Both `findings/images/01_predictability_ranking.png` (hero) and `findings/images/02_kl_vs_h_scatter.png` (scatter) use this. The bottom-3 hero color (D-28) is selected from this palette to avoid red.
- **`analysis/02_predictability_modeling.py`** — Where the S3 exploratory chi-square cells are appended (per D-12). The S1 chi-square block (cell 13) is the structural template the S3 cells mirror per D-10.
- **`queries/01_tendency_distribution_by_team.sql`** — Per-team blitz rate (input to KL leaderboard for the scatter and to the per-team beat for insight #6).
- **`queries/03_red_zone_vs_midfield.sql`** — Insight #5 numerical source.
- **`queries/05_third_long_pressure_tendencies.sql`** — Insight #6 candidate (DET 52.3% league leader on S1).
- **`queries/07_situational_predictability_score.sql`** — Predictability index raw inputs (used by `02_predictability_modeling.py`'s leaderboard cells).
- **`data/nfl_defensive_tendencies.db`** — The Phase 2 build (1,139 games / 197,362 plays / 185,215 ftn_play / 105,556 competitive_plays / 58,178 competitive pass plays). Read-only for Phase 4. Gitignored.
- **`README.md`** — Skeleton with placeholder slots; Plan 04-02 hand-rewrites.
- **`scripts/_verify_queries_run.py`** — QUERY-09 meta-compliance + execution smoke. Local pre-push step (not in CI per D-47).

### Established patterns

- **jupytext .ipynb + .py pairing.** All `analysis/*.ipynb` files have a paired `.py` per `formats: ipynb,py:percent` header. Phase 4 `03_visualizations.ipynb` follows the same pattern. Outputs cleared before commit via `nbconvert --clear-output --inplace` (VIZ-04).
- **Static-figure pipeline.** matplotlib + seaborn only; no Plotly, Bokeh, Streamlit. Figures saved as PNG via `savefig(path)` with `_style.py` rcParams already applied. Figures live in `findings/images/` only — never embedded in committed `.ipynb` outputs.
- **Path management.** `pathlib.Path` throughout. `_common.py:DB_PATH` is a `Path`. SQL loading idiom: `sql = (Path("queries") / "07_situational_predictability_score.sql").read_text(); df = pd.read_sql_query(sql, conn)`.
- **SQL on `competitive_plays`.** All analytical queries reference the `competitive_plays` view (Phase 2 D-04) via `JOIN ftn_play USING (game_id, play_id)`. The S3 exploratory chi-square in `02_predictability_modeling.py` follows the same join pattern.
- **Assertion style.** Plain `assert` with f-string error messages (Phase 1+2 ETL pattern). `min_n_filter` does NOT raise — returns filtered DataFrame and logs WARNINGs.
- **Audience voice.** Memo not tutorial; numbers first; N inline with every claim; tiered N≥30/100/15-flag visible. No emoji headers; no "Welcome to my project!" greetings.

### Integration points

- **`analysis/03_visualizations.ipynb` ↔ `_common.py` + `_style.py` + `queries/*.sql` + DB.** Greenfield notebook (does not exist). Reads numbers via `_common.get_conn()` + SQL files; styles via `_style.apply_style()`; exports two PNGs to `findings/images/`. Outputs cleared before commit.
- **`findings/images/01_predictability_ranking.png` ↔ social preview PNG.** Same parameterized leaderboard function renders the hero (32 bars, portrait, fixed 0–100) and the social preview (top-12 only, 1280×640 landscape). Both files committed to `findings/images/`.
- **`findings/images/02_kl_vs_h_scatter.png` ↔ rank computation in `02_predictability_modeling.py`.** The scatter notebook reads the 32-team predictability scalar + KL leaderboard from the existing modeling notebook's outputs (or recomputes them from QUERY-07 + QUERY-01). Eight callouts placed via `adjustText`.
- **`findings/FINDINGS.md` ↔ all the above + appendix tables T1..T4.** Greenfield. Authors prose against the locked structure (TL;DR γ + 6 insights + 3 thematic methodology blocks + T1..T4 + 5 limitations + attribution). Reads empirical numbers from `02_predictability_modeling.py`'s leaderboard, the chi-square cells, and the SQL query result rows.
- **`README.md` ↔ `findings/images/01_predictability_ranking.png` + Mermaid diagram + glossary.** Plan 04-02 hand-rewrite fills placeholders, reconciles the D-14 cross-doc threshold and the README-hook S1-vs-cross-situation framing per D-48.
- **`.github/workflows/ci.yml` ↔ `etl/`, `analysis/`, README.md, FINDINGS.md.** Greenfield. Single workflow file per D-44; runs on push to main + PRs per D-45; concurrency cancel-in-progress per D-46.

### Greenfield within Phase 4

- `analysis/03_visualizations.ipynb` (+ paired `.py`) — VIZ-01..05.
- `findings/images/01_predictability_ranking.png` — VIZ-02 hero.
- `findings/images/02_kl_vs_h_scatter.png` — VIZ-03 second viz.
- Social-preview PNG (filename per executor's choice; same code path as the hero) — SHIP-04.
- `findings/FINDINGS.md` — DOC-01, DOC-02.
- `data/README.md` — DOC-08 (small file documenting the gitignored DB regen path).
- `.github/workflows/ci.yml` — SHIP-01.
- New cells in `analysis/02_predictability_modeling.py` — S3 exploratory chi-square per D-10..D-15.

### Phase 3 patterns this phase extends

- The 3-sentence S3 protocol shape (D-13 + D-14 in this CONTEXT) extends the S1 chi-square reporting structure already in `02_predictability_modeling.py` cell 13. No new statistical methodology — just a new universe + the OR-delta first-class output (D-11).
- The chart export pipeline extends the existing `_style.py` + matplotlib pattern from Phase 3's `01_exploratory.ipynb` (which also outputs to `findings/images/` even though Phase 3 didn't ship images publicly — the directory infrastructure is established).

</code_context>

<specifics>
## Specific Ideas

These are particular references, examples, or "I want it like X" moments from the discussion that should survive into research/planning verbatim.

- **Top-12 social preview is the locked design, not a fallback.** Treating top-12 as a fallback puts the executor in a position to subjectively assess "is 32-bar readable enough?" at execution time — and they'll converge on "yes, just barely" because nobody wants to invoke a fallback. Skip the ambiguity. Lock top-12 with the title parenthetical "(Top 12)."
- **Inverted axes on the KL-vs-H scatter (rank 1 at top-left) is a deliberate pushback against stats-plot convention.** The chart is a rankings visualization first, a stats plot second. Every reader's intuition for ranks is "1st at the top" (NBA standings, tennis, sports leaderboards). Forcing rank 1 to the bottom-left because scatter convention puts low values near the origin is making the reader fight their intuition. The y=x diagonal runs through the chart either way; "natural orientation reads cleanest" is purely cosmetic.
- **Fixed 0–100 hero axis is a deliberate pushback against truncated-axis convention.** Truncating to 0–30 makes PHI's ~23.5 look near-maximum when it's below a quarter of the metric's range. The "empty space" past the top bar isn't wasted — it shows defenses cluster at the low end of the metric, no team approaches perfect predictability, and team-to-team spread is small relative to the metric's range. Truncated axes are a known visual rhetoric tell; recruiters with statistical training notice and discount the chart. Score annotations on top-3 + bottom-3 mitigate short-bar readability without truncating.
- **D-15 (H-vs-KL divergence) ships as named insight #2, not buried in methodology.** A negation finding ("two definitions disagree") is a worse opener than a positive headline, but it lands powerfully at #2 where it functions as methodological confirmation that the leaderboard's metric choice was deliberate.
- **S1 + S3 stay separate insights (not merged).** The methodological-status labels (pre-registered vs exploratory) are what carry the rigor signal. Merging collapses the labeling.
- **Mandatory third-sentence caveat on every insight.** Even findings the executor judges "clean" at authoring time still get the third sentence — framed as scope ("This pattern holds across all four seasons; pre-2022 trend not assessed") or generality ("Per-team rates vary; see appendix T1") rather than as weakness. The methodological-honesty beat is what gives consistent rigor signal across all six insights.
- **CONTRIBUTING.md skip is a recruiter-signal optimization, not laziness.** A solo portfolio repo with zero issues, zero stars, no community doesn't earn it. The file would read as either template paste or theatrical process-awareness — both signals hurt. The real process artifacts (`.planning/`, atomic commits, SPEC/REQUIREMENTS/ROADMAP flow, verifier reports) do the legitimate version of the same signal. Process cosplay tax avoided.
- **Concurrency control on the CI workflow.** Standard pattern (`group: ${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: true`). Cleaner CI history, faster feedback on the latest commit, no wasted compute on superseded commits during rapid Phase 4 polish iterations.
- **Mermaid render verification is its own beat, not subsumed by "README displays."** GitHub's Mermaid renderer diverges from local previews on edge cases (Unicode, certain edge-label patterns). Eyeball the GitHub-rendered diagram against intent during the private-staging verification window per D-40 + D-41.
- **Mobile social-preview crop check is its own beat.** GitHub mobile / LinkedIn / Slack crop the 1280×640 image differently than desktop. 30-second mobile check during the SHIP-07 non-author verification.
- **Repo-wide grep after the four known D-14 reconciliation locations.** The brief identified four prose files; a `grep -rn "n_blitzers > 4"` (and variants like `> 4 rushers`) is a one-second confidence check that nothing was missed. Surface zero-results in the verification log per D-49.
- **MCP/UI path actually used for SHIP-04 + SHIP-05 logged in verification report.** Future-self or a recruiter inspecting the planning artifacts sees a real engineering record, and the next person running this knows what path to expect.
- **L3 prose (PA-on-S1 strategic abandonment) is a one-concrete-sentence beat, not a vague hedge.** The sentence makes the football logic explicit: PA requires a credible run threat; 3rd-and-7+ removes the threat; PA is strategically abandoned; the 1.235% rate is real strategic constraint, not data quality.
- **L4 prose (FTN charter subjectivity) acknowledges the limitation's own boundary.** FTN doesn't publish inter-rater reliability for `is_play_action`; we can't bound the impact quantitatively. Frame as honest about what isn't known rather than papering over.
- **One-decimal score precision on hero annotations.** Two decimals reads as false precision on a 0–100 scale; integer rounding loses signal between adjacent teams whose decimal differences are real. One decimal is the balanced choice.
- **Bottom-3 hero color is deliberately non-red.** Red signals "these teams are failing." The finding isn't that; least predictable doesn't mean worst defense — it means "blitzes at a rate close to 50/50, hardest to anticipate." Muted orange / dark teal / similar from `_style.py`'s palette.

</specifics>

<deferred>
## Deferred Ideas

These came up during discussion (or are implied by the locked decisions) but are out of Phase 4 scope. Capture so future phases / v2 don't re-discover.

- **Per-team color palette in `_style.py`.** Defaulted to the colorblind palette (Phase 3 deferral). v2 if the analytical narrative ever needs per-team identity in non-hero charts.
- **PA × blitz chi-square on S2 (red zone) and S4 (2nd-and-medium).** Phase 4 ships S1 (pre-registered) + S3 (exploratory) only. S2 has N(PA=1) = 1,808 and S4 has N(PA=1) = 1,819 — both well above S1's N=109 and meaningful for inferential power. Would expand the slate from 2 chi-squares to 4. Deferred to v2 to keep the FINDINGS slot count at 6 and respect the analysis-plan.md firewall (S2/S4 PA chi-squares would also need explicit "exploratory" labeling).
- **Cramér's V as supplemental effect-size measure.** Phase 3 D-11 locked odds-ratio + Wilson CI. v2 if a non-2×2 generalization is ever added.
- **Within-season week-over-week drift.** The original REQUIREMENTS.md placeholder for QUERY-08 (renamed in Phase 3 D-07 to cross-season trend). v2 if "in-season tendency stability" earns a FINDINGS slot.
- **`nflreadpy` migration + numpy>=2.0 re-pin.** PROJECT.md v2 deferral; Phase 4's `Known Issues` README section (DOC-07) names the path.
- **`defense_coverage_type` and `defense_man_zone_type` from nflfastR ngs.** Phase 1 v2 candidate; flagged in `docs/ftn-schema-audit.md`. Would re-open the man-zone framing the project deliberately stepped away from. Documented but not actioned in v1.
- **Inter-rater reliability disclosure for FTN subjective fields.** PROJECT.md v2 deferral (V2-DOC-01). L4 in this phase acknowledges the limitation's own boundary; v2 would commission empirical IRR measurement.
- **Custom hero-chart social preview iteration based on first-month repo analytics.** PROJECT.md v2 deferral (V2-DOC-02). v1 ships with the top-12-rendered preview locked in D-34.
- **Animated play visualization.** PROJECT.md v2 deferral (V2-VIZ-01). Requires tracking data not present in the public FTN dataset; not addressable without source-data expansion.
- **Simple defensive-tendency classifier (ML).** PROJECT.md v2 deferral (V2-ML-01). v1 holds at tendency analysis, not prediction.
- **Scheduled weekly CI runs.** Skipped per D-45 (notification surface for unactionable risk on archived `nfl_data_py`). v2 if a maintained-package post-migration warrants drift detection.
- **SQL static checks in CI** (option γ from Q1a of Area #5). Skipped per D-47 — duplicates `scripts/_verify_queries_run.py` local pre-push step. v2 if the local pre-push step is ever automated away.
- **Multi-Python-version CI matrix.** Skipped — the locked stack pins 3.11 only (`nfl_data_py==0.3.3` install fails on 3.13). Single 3.11 is the right CI target.
- **Plan structure split (3 vs 4 plans).** Planner-phase decision; not locked here. ROADMAP suggests 3.

### Reviewed Todos (not folded)

None — STATE.md "Pending Todos" was empty going into this phase.

</deferred>

---

*Phase: 04-story-and-ship*
*Context gathered: 2026-04-30*
*Areas drilled: FINDINGS narrative architecture (#1) → second viz KL-vs-H scatter (#3) → hero chart + social preview (#2) → public repo surface (#4) → CI workflow scope (#5).*
