# Phase 4: Story & Ship — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `04-CONTEXT.md` — this log preserves the alternatives considered and the user's reasoning where it deviated from defaults.

**Date:** 2026-04-30
**Phase:** 04-story-and-ship
**Areas drilled (in order):** FINDINGS narrative architecture (#1) → second viz KL-vs-H scatter (#3) → hero chart + social preview (#2) → public repo surface (#4) → CI workflow scope (#5).

**Pre-discuss artifact:** `04-PRE-DISCUSS-BRIEF.md` — factual record on D-14..D-17 + n_blitzers correction. Written by the assistant at the user's request before discuss-phase opened, to establish the analytical record. The user confirmed D-15 as a methodology signal, redirected D-17 framing toward "directional, not headline," and introduced the S3 exploratory chi-square as a substantive Phase 4 addition.

---

## Area #1 — FINDINGS.md narrative architecture

### Q1: Insight count + structural shape + headline

| Option | Description | Selected |
|---|---|---|
| A — Disciplined (5 insights) | Leaderboard, D-15, S1+S3 paired, RZ pressure, situational variation. D-14+D-16 in methodology. Tight read. | |
| B — Standard (6 insights) | Adds team-level pressure beat (DET 52.3% candidate). | ✓ |
| C — Reflective (7 insights) | Adds D-14 itself as a named insight. | |

**Headline sub-question:** Leaderboard leads / D-15 divergence leads / other.
**User's choice:** Leaderboard leads.
**Notes:** "5 leaves real material on the floor (no team-level texture for a 32-team ranking project), 7 promotes D-14 alongside analytical findings which inflates a process-story finding into a peer with the actual results. 6 with D-14 and D-16 in methodology is the right balance." Headline reasoning: "The README sells the leaderboard, the hero chart is the leaderboard — leading FINDINGS with D-15 creates a structural mismatch where the README and memo point different directions. D-15 is a negation finding which makes a worse opener than a positive headline; it lands better as insight #2 where it functions as methodological confirmation." Sub-decision: S1 and S3 stay separate insights (don't merge — labeling is what carries the rigor signal).

---

### Q2: S3 exploratory chi-square — spec + framing protocol

**Part A (spec):**

| Component | Default | Selected | Notes |
|---|---|---|---|
| Universe | `competitive_plays JOIN ftn_play` on `down=1 AND ydstogo=10 AND play_type='pass'`; N=18,609; N(PA=1)=8,652 | ✓ confirmed | |
| 2×2 structure | `is_play_action × (n_blitzers > 0)` | ✓ confirmed | |
| Reporting | chi² + p-value, expected min cell, OR + 95% CI, Wilson CI on P(blitz \| PA=1, S3), paired P(blitz \| PA=0, S3), pp gap | ✓ confirmed | |
| Labeling | "EXPLORATORY — NOT pre-registered" cell comment + insight-header tag | ✓ confirmed | |
| Notebook location | append to `02_predictability_modeling.ipynb` (default) vs new `03_followups.ipynb` | ✓ append | "Cell-level labeling carries the rigor signal; physical separation adds bureaucratic distance without analytical value." |
| **OR delta S1↔S3 as first-class output** | not in default | ✓ **added by user** | "The narrative depends on direction agreement; make the comparison visible rather than leaving it for the reader to extract from two separate test reports." |

**Part B (framing protocol):**

| Option | Description | Selected |
|---|---|---|
| Pre-lock all 4 scenarios' prose in the plan | Reproducibility, deterministic | |
| Author at execution time | Most readable | |
| Hybrid: pre-lock decision rule + structural shape; author prose at execution | Best of both | ✓ |

**5-scenario decision rule (user-specified, more granular than my 4-scenario default):**
1. `p < 0.05 AND OR < 1` — confirms with significance
2. `0.05 ≤ p < 0.10 AND OR < 1` — confirms at marginal significance
3. `OR > 1` (regardless of p; surface p separately) — contradicts
4. `p ≥ 0.10 AND 0.85 ≤ OR ≤ 1.18` — null (within ~15% of OR=1)
5. `p ≥ 0.10 AND OR < 0.85` — directional but inconclusive *(user-added 5th scenario)*

**3-sentence structural shape per scenario:**
- Sentence 1: state S3 result with numbers
- Sentence 2: explicit cross-situation comparison with S1 (using OR delta from D-11)
- Sentence 3: implication

**Notes:** "Pre-locked prose can't engage with specific values; author-time prose can. The pre-locked rule + structure protects against post-hoc rationalization without forcing stiff phrasing."

---

### Q3: Methodology section + appendix + limitations

**Q3a — Methodology section shape:**

| Option | Description | Selected |
|---|---|---|
| α — Prose narrative | One voice, ~600–800 words, no subheadings | |
| β — Five named subsections | Most scannable | |
| γ — Three thematic prose blocks | Middle ground; combines D-14+H/log(k) + D-16 + sample-size-firewall | ✓ |

**Q3b — Methodology appendix tables:**

| Option | Description | Selected |
|---|---|---|
| T1–T4 only | Rigor backbone | ✓ |
| T1–T5 | Adds per-team blitz rate × situation table | |
| T1–T6 | Adds stack/version + SQL slate index | |

**Spec added by user:** Rename T1 from "predictability matrix" to "per-team-per-situation predictability cells (with blitz rate, N, predictability scalar)" — multi-value cell table, not single-value heatmap.

**Q3c — Limitations section content:**

| Option | Description | Selected |
|---|---|---|
| L1+L2+L3+L4+L6 (5 items, skip L5) | L5 belongs in README's Known Issues per DOC-07 | ✓ |
| All 6 items (incl. L5) | | |
| Other | | |

**Two prose constraints added by user:**
- L3 must explain WHY PA collapses on 3rd-and-long (credible run threat → strategic abandonment, not data-quality). One concrete sentence beats a vague hedge.
- L4 must acknowledge the limitation's own boundary: FTN doesn't publish inter-rater reliability for `is_play_action`, so we can't bound the impact quantitatively.

---

### Q4: TL;DR shape + leaderboard depth

**Q4a — TL;DR shape:**

| Option | Description | Selected |
|---|---|---|
| α — Numbers-first bullets | ~150 words; max scan | |
| β — Single prose paragraph | ~200 words | |
| γ — Hybrid (prose + 4 bullets) | ~250–300 words | ✓ |

**User refinement:** "Bias toward the lower end of the word range (~250 words, not 300). Every word past ~270 starts working against the 'first 30 seconds' purpose."

**Q4b — Leaderboard depth:**

| Option | Description | Selected |
|---|---|---|
| Top-1 + bottom-1 | Mirror README hook | |
| Top-3 + bottom-3 | Adds texture; six teams, scannable | ✓ |

**Format spec (user):** "One scannable line — 'Top 3 (most predictable): TEAM_A (X.X), TEAM_B (Y.Y), TEAM_C (Z.Z). Bottom 3: TEAM_X (A.A), TEAM_Y (B.B), TEAM_Z (C.C). League average: M.M.'"

**Two TL;DR prose constraints added by user:**
- The framing paragraph names the four pre-registered situations explicitly (plants the rigor flag before the numbers land).
- The TL;DR previews D-15 in one sentence (prevents recruiter-reading-only-the-TL;DR from walking away thinking the project is one-dimensional). Does NOT bury the leaderboard headline — leaderboard still leads, divergence is a one-line preview pointing at insight #2.

---

### Q5 (gap fix): Insight-internal structure

| Option | Description | Selected |
|---|---|---|
| α — Fixed template, fixed length | All 6 in 3 sentences ~75–100 words. Compresses leaderboard. | |
| β — Variable length, no shape rule | Editorial judgment. Risk: drift across 6 authoring passes. | |
| γ — Fixed template + length tiers | Same 3-sentence shape (claim → evidence → implication/caveat); evidence sentence allowed to expand into mini-table when warranted. | ✓ |

**User addition (locked):** "The third sentence (implication/caveat) is mandatory for every insight, not optional. If a finding feels 'clean' to the executor at authoring time, the caveat sentence still ships — framed as scope or generality rather than as a weakness. Don't let the executor skip the third sentence on grounds of a finding being 'solid.'"

---

## Area #3 — Second viz (KL-vs-H rank-rank scatter)

### Q1: VIZ-03 reading + scatter scaffold

**Q1a — VIZ-03 wording threshold:**

| Option | Description | Selected |
|---|---|---|
| Illustrative | Scatter satisfies on its own | ✓ |
| Restrictive | Add heatmap or small-multiples grid | |

**User addition:** Add a one-line note in the plan documenting how the requirement was met: "VIZ-03 satisfied via the KL-vs-H rank-rank scatter."

**Q1b — Scaffold:**

| Option | Description | Selected |
|---|---|---|
| A — Value-value scatter | Preserves magnitude; no natural reference line | |
| B — Rank-rank scatter | Spearman-native; y=x diagonal as agreement reference | ✓ |

**User addition:** "The y=x diagonal must be drawn as a reference line in light gray (not implied), with a label like 'perfect agreement (ρ = 1.0)' or similar. A scatter without the diagonal forces the recruiter to mentally construct where agreement would sit — the line does that work for them."

---

### Q2: Annotation specifics

**Q2a — Callout list:**

| Option | Description | Selected |
|---|---|---|
| (i) Top-5 disagreers only | 5 labels | |
| (ii) Top-5 disagreers + 3 leaderboard anchors | 8 labels (MIN, TB, PIT, MIA, DET + PHI, SF, IND); double-duty MIN/TB | ✓ |
| (iii) Top-5 disagreers + top-2 agreers | 7 labels (anonymous middle teams) | |
| (iv) All 32 | Busy | |

**User spec:** Lock matplotlib `adjustText` (or equivalent) for label placement so the executor doesn't hand-place and end up with overlap.

**Q2b — Axis convention:**

| Option | Description | Selected |
|---|---|---|
| (i) Natural — rank 1 at bottom-left | Stats convention | |
| (ii) Inverted — rank 1 at top-left | Rankings convention | ✓ **(user pushback against assistant's default)** |

**User reasoning:** "The chart is a rankings visualization first, a stats plot second — every reader's intuition for ranks is '1st at the top' (NBA standings, tennis rankings, sports leaderboards everywhere). Forcing rank 1 to the bottom-left because scatter-plot convention puts low values near the origin is making the reader fight their intuition. The y=x diagonal runs through the chart either way; the 'natural orientation reads cleanest' argument is purely cosmetic. Inverted axes match the implicit mental model the labels invite. Lock it."

**Q2c — Title:**

| Option | Description | Selected |
|---|---|---|
| (i) Finding-as-title | "Two Definitions of Predictable Disagree on This League" | ✓ (with user trim) |
| (ii) Neutral-as-title | Generic | |
| (iii) Question-as-title | "Do Two Definitions of 'Predictable' Agree?" | |

**User trim:** Drop "on This League" — the subtitle's "32 NFL defenses, 2022-2025" carries the scope. Final title: "Two Definitions of Predictable Disagree." "Every word in a chart title earns its place."

---

## Area #2 — Hero chart + social preview

### Q1: Chart design

**Q1a — Chart type:**

| Option | Description | Selected |
|---|---|---|
| (i) Horizontal bar | Most legible; bar-length-as-score reading | ✓ |
| (ii) Lollipop | Stats-savvy, lower visual weight | |
| (iii) Dot plot | Minimal | |
| (iv) Annotated leaderboard | Spreadsheet-like | |

**User spec:** Plain text team codes (PHI, SF, IND), not logos. "Logos add trademark concerns to a public portfolio repo and fragment the visual rhythm."

**Q1b — Color encoding:**

| Option | Description | Selected |
|---|---|---|
| (i) Single color | Cleanest | |
| (ii) Highlight extremes | Top-3 accent + bottom-3 distinct + middle-26 neutral gray | ✓ |
| (iii) Rank gradient | Continuous colormap | |
| (iv) Conference (AFC/NFC) | Football-only signal | |

**User spec:** Pick the bottom-3 color deliberately from `_style.py`'s palette rather than defaulting to red. "Red signals 'these teams are failing,' which isn't the finding — least predictable doesn't mean worst defense. Muted orange, dark teal, or a similar neutral-but-distinct color is preferable."

**Q1c — League-average reference line:**

| Option | Description | Selected |
|---|---|---|
| (i) Line + label | Most explicit | ✓ |
| (ii) Line, no label | | |
| (iii) No line | | |

**User spec:** Place the "League avg = 12.5" label where it doesn't collide with the top-ranked bar. Bottom of chart or upper-right corner away from bars.

**Q1d — Axis scale:**

| Option | Description | Selected |
|---|---|---|
| (i) Fixed 0–100 | Truthful to metric range; informative empty space | ✓ **(user pushback against assistant's default)** |
| (ii) Data-driven 0–25 | Tight; visually exaggerates | |
| (iii) Data-driven 0–30 | Compromise | |

**User reasoning:** "The predictability index runs 0–100; truncating to 0–30 makes PHI's 23.5 look near-maximum when it's actually below a quarter of the metric's theoretical range. The 'empty space' past the top bar isn't wasted — it's informative. It shows that NFL defenses cluster in the low end of the metric, that no team approaches perfect predictability, and that team-to-team spread is small relative to the metric's range. Truncated axes are a known visual rhetoric tell; recruiters with statistical training notice and discount the chart. Full 0–100 reads as honest at a glance, which is the signal we want. If short-bar readability is genuinely a problem at 0–100, add a secondary text annotation near PHI's bar showing the actual score (e.g., '23.5') so the number is readable directly. Better than truncating."

---

### Q2: Social preview + title + score annotations

**Q2a — Social preview generation:**

| Option | Description | Selected |
|---|---|---|
| (i) Same chart re-rendered with all 32 teams | Honest to "derived from"; tight at thumbnail | |
| (ii) Top-12 only at 1280×640 | Roomier; thumbnail-readable | ✓ **(user pushback against assistant's default; locked, not fallback)** |
| (iii) Side-by-side top-5 / bottom-5 | Narrative balance; more design work | |
| (iv) Standalone designed image | Marketing-feel | |

**User reasoning:** "The readability math doesn't work at 32 bars. After accounting for title, subtitle, axis labels, and padding, you get ~12-13 px per bar at 640px height — technically valid, practically unreadable on the platforms social previews actually appear on (LinkedIn, Slack, Twitter cards crop and compress further). Locking top-12 with the title parenthetical 'Most Predictable Defenses 2022-2025 (Top 12)' satisfies SHIP-04's 'derived from' cleanly: same data source, same metric, same color scheme, same style.py pipeline, just thumbnail-appropriate density. Recruiters clicking through get the full leaderboard. Treating top-12 as a fallback rather than the lock puts the executor in a position to subjectively assess 'is 32-bar readable enough?' at execution time — and they'll converge on 'yes, just barely' because nobody wants to invoke a fallback. Skip the ambiguity."

**Q2b — Hero chart title:**

| Option | Description | Selected |
|---|---|---|
| (i) Specific finding ("PHI Is the NFL's Most Predictable Defense") | Brittle if data changes | |
| (ii) Generic descriptive | Neutral; loses the finding | |
| (iii) Finding-framed and data-stable ("Some NFL Defenses Are More Predictable Than Others") | Matches README hook | ✓ (with user trim) |

**User trim:** Trim "on third-and-long" from the README hook for the chart title — the chart aggregates across all four situations. Final title: "Some NFL Defenses Are More Predictable Than Others." Subtitle carries scope and methodology. "Situation qualifier doesn't appear on the cross-situation chart."

**Q2c — Score annotations:**

| Option | Description | Selected |
|---|---|---|
| (i) PHI only | Anchor only top-1 | |
| (ii) Top-3 + bottom-3 | Six teams; symmetric with color scheme | ✓ |
| (iii) All 32 | Cluttered on short bars | |

**User spec:** One decimal place (e.g., "23.5"). "One decimal balances precision with readability — two decimals reads as false precision on a 0-100 scale; integer rounding loses signal between adjacent teams whose decimal differences are real."

---

## Area #4 — Public repo surface

### Q1: Description, topics, license, branch protection

**Q1a — Repo description:**

| Option | Description | Selected |
|---|---|---|
| (i) "Defensive blitz-rate predictability across 32 NFL defenses, 2022-2025" (69 chars) | | ✓ |
| (ii) "Situational blitz-tendency analysis of NFL defenses, 2022-2025" (62 chars) | | |
| (iii) "32-team NFL defensive predictability index — Python + SQLite, 2022-2025" (74 chars) | Over | |

**User spec:** Use a regular hyphen ("2022-2025"), not an en-dash. "GitHub's Unicode handling in repo descriptions is inconsistent across rendering contexts."

**Q1b — Topic list:**

| Option | Description | Selected |
|---|---|---|
| (i) REQUIREMENTS' 7 verbatim | | |
| (ii) REQUIREMENTS' 7 + nflverse | All 8 slots filled | ✓ |
| (iii) Trim to 5–6 | Tighter | |

**User reasoning:** "nflverse is the ecosystem-level discoverability hook the broader football-analytics community searches; nfl-data-py is the package. Both serve different audiences."

**Q1c — License:**

| Option | Description | Selected |
|---|---|---|
| (i) MIT | Convention | ✓ |
| (ii) Apache-2.0 | Adds patent grant | |
| (iii) BSD-3-Clause | Less common | |
| (iv) None | Discourages use | |

**User reasoning:** "The CC-BY-SA data licensing lives separately in the README's Attribution section, since no data ships in the repo."

**Q1d — Auxiliary files + branch protection:**

| Component | Default | Selected |
|---|---|---|
| CONTRIBUTING.md | Skip | ✓ skip |
| CODE_OF_CONDUCT.md | Skip | ✓ skip |
| Branch protection requiring SHIP-01 | Enable | ✓ enable |
| Sub-question: minimal CONTRIBUTING.md as recruiter signal? | (default: no opinion) | ✗ **no (user pushback)** |

**User reasoning on CONTRIBUTING.md skip:** "A solo portfolio repo doesn't earn a CONTRIBUTING.md. On a project with zero open issues, zero stars, no community, the file reads as either (a) template paste without thinking about whether it applies, or (b) theatrical process-awareness. Both signals hurt. Recruiters who want to see professional process applied to real work get it from .planning/, the atomic commit history, the SPEC/REQUIREMENTS/ROADMAP flow, the verifier reports — those are actual process artifacts. CONTRIBUTING.md on a solo repo is process cosplay; the contrast against the real artifacts hurts you. Branch protection + CI + clean commits do the legitimate version of the same signal without the cosplay tax."

---

### Q2: Ship sequence — visibility, verification, MCP fallbacks

**Q2a — Visibility flow:**

| Option | Description | Selected |
|---|---|---|
| (i) Direct public creation | Cleanest | |
| (ii) Private-then-flip | Adds verification beat on actual GitHub-rendered surface | ✓ |
| (iii) Local-staging-then-create | Overkill | |

**User spec:** "The verification beat must specifically check the GitHub-rendered Mermaid diagram, not just that the README displays. GitHub's Mermaid renderer sometimes diverges from local previews on edge cases (Unicode, certain edge label patterns); eyeball the diagram against intent."

**Q2b — Non-author verification:**

| Option | Description | Selected |
|---|---|---|
| (i) Incognito tab on same browser | Verifies public visibility only | |
| (ii) Different browser entirely | + browser quirks | |
| (iii) Incognito desktop + mobile | + mobile viewport + social-preview crops | ✓ |

**User spec:** Check the social preview rendering on mobile too. "GitHub's mobile app/web crops the 1280×640 image differently than desktop and platform cards (LinkedIn, Slack); 30-second mobile check catches edge-cropping issues."

**Q2c — MCP capability + fallback policy:**

| Option | Description | Selected |
|---|---|---|
| (i) Pre-flight capability probe | Front-loads investigation | |
| (ii) Document both paths up front | Plan codifies MCP-or-UI contingency | ✓ |
| (iii) Manual UI by default | Abandons SHIP-04/SHIP-05 spec | |

**User spec:** "Log the path actually used (MCP or UI) for SHIP-04 and SHIP-05 in the verification report. Future-you or a recruiter inspecting the planning artifacts sees a real engineering record, and the next person running this knows what path to expect."

---

## Area #5 — CI workflow scope

### Q1: Scope, triggers, job structure

**Q1a — Workflow scope:**

| Option | Description | Selected |
|---|---|---|
| α — Locked 3 only | ruff + ETL import smoke + SHIP-08 | |
| β — Locked 3 + analysis-module import smoke | Includes `_common.py`, `_style.py` | ✓ |
| γ — Locked 3 + B + SQL static checks | Adds header parse + schema syntax | |

**User reasoning:** "The locked spec's 'ETL-module import smoke' should naturally extend to the analysis layer since both ship in the repo's Python surface; the gap is free to close. SQL static checks (γ) duplicate what `scripts/_verify_queries_run.py` catches locally before push, so CI's marginal value over manual pre-push is small."

**Q1b — Triggers:**

| Option | Description | Selected |
|---|---|---|
| (i) Push to main only | | |
| (ii) Push + PRs targeting main | | ✓ |
| (iii) (ii) + scheduled weekly | Adds notification surface | |

**User reasoning on skipping scheduled:** "Scheduled (iii) creates notification surface for a risk that's unactionable on archived nfl_data_py until the v2 effort — anxiety without action."

**Q1c — Job structure:**

| Option | Description | Selected |
|---|---|---|
| (i) Single job, sequential | Simplest | ✓ |
| (ii) Multiple jobs parallelized | ~30 sec faster wall-clock; triple compute | |

**User reasoning:** "Multi-job parallelization triples compute spend (each job pays its own setup-python + install) for a wall-clock saving of ~30 seconds, with no user or developer benefiting from the speedup. 3-5 min CI on a portfolio repo is invisible."

**User addition (locked):** Concurrency control YAML stanza:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
"Cleaner CI history, faster feedback on the latest commit, no wasted compute on superseded commits during rapid Phase 4 polish iterations."

---

## Discussion close-out: D-14 cross-doc reconciliation timing

**Gap flagged by assistant before close:** When does the D-14 prose reconciliation (PROJECT.md L58, 03-CONTEXT.md D-02, ftn-schema-audit.md, README glossary → `n_blitzers > 0`) actually happen?

| Option | Description | Selected |
|---|---|---|
| (i) Pre-Phase-4 housekeeping commit | Coherent docs before any Phase 4 plan starts | |
| (ii) Folded into Plan 04-02 README hand-rewrite | Single editorial sweep with FINDINGS context fresh | ✓ |
| (iii) Folded into FINDINGS methodology section authoring | Buries plan-mechanical work in content | |

**User spec:** "After updating the four known prose locations, run a final repo-wide grep for `n_blitzers > 4` and variants (e.g., '> 4 rushers'). The brief identified the four known locations; a repo-wide grep is a one-second confidence check that nothing was missed. Surfacing the grep results in the verification log."

---

## Claude's Discretion

The user explicitly delegated to executor judgment with documented defaults:

- Memo length budget (working target ~3000 words; trim aggressively).
- Plan structure (3 vs 4 plans) — planner-phase decision; ROADMAP suggests 3 (04-01 Viz, 04-02 Docs, 04-03 Ship); the planner can split 04-02 if FINDINGS detail warrants.
- Specific prose voice for each insight, methodology block, limitation, transition.
- Mermaid diagram exact node labels and orientation.
- Specific axis labels, tick formatting, color hex values on viz (per `_style.py`).
- CI workflow exact filename (`.github/workflows/ci.yml` is the default).
- DET-as-team-level-beat empirical verification (executor verifies league-leader status during execution).

---

## Deferred Ideas (carried in CONTEXT.md `<deferred>` section)

- Per-team color palette in `_style.py`.
- PA × blitz chi-square on S2 and S4.
- Cramér's V supplemental effect-size measure.
- Within-season week-over-week drift.
- `nflreadpy` migration + `numpy>=2.0`.
- ngs-derived `defense_coverage_type` / `defense_man_zone_type`.
- Inter-rater reliability disclosure for FTN subjective fields.
- Custom hero-chart social preview iteration based on first-month repo analytics.
- Animated play visualization.
- Defensive-tendency classifier (ML).
- Scheduled weekly CI runs.
- SQL static checks in CI.
- Multi-Python-version CI matrix.
- Plan structure split (3 vs 4 plans).

---

*Discussion closed: 2026-04-30. Five areas drilled in user-specified order. ~50 numbered decisions captured in `04-CONTEXT.md`. Three notable user pushbacks against assistant defaults: inverted axes on the scatter (Q2b Area #3), fixed 0–100 axis on the hero (Q1d Area #2), top-12 social preview locked (not fallback) (Q2a Area #2). One assistant-flagged gap closed (insight-internal structure, Area #1 Q5). One user-flagged gap closed (D-14 reconciliation timing).*
