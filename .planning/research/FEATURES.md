# Feature Research — Portfolio Repo Signals

**Domain:** Public GitHub portfolio repo for entry-level data-analyst job applications (NFL defensive coverage tendencies analysis)
**Researched:** 2026-04-29
**Confidence:** HIGH for general data-analyst portfolio signals; MEDIUM for sports-analytics-specific signals (smaller sample of public guidance from teams/outlets)

> **Reframing for this project:** The "users" of this repo are recruiters and analytics-team hiring managers, not end users of a product. The "features" are README/repo elements that produce a positive signal in a 30-to-90-second skim. CONTENT (the NFL coverage analysis) is fixed by SPEC.md — this research only addresses the META-features that wrap that content.

## Executive Summary

The dominant failure mode for technically-skilled entry-level candidates is **good work, terrible presentation** [VERIFIED: KDnuggets, phData, Dataquest 2025 guidance]. Recruiters spend ≤90 seconds on a repo before deciding to dig in. The "30-second test" is satisfied by a clear one-line problem statement, a hero chart visible without scrolling, and a 3-bullet "key findings" block. The "90-second test" is satisfied by a runnable setup block, a visible architecture diagram, and a single link to a memo-style FINDINGS.md.

Sports-analytics audiences (NFL teams, PFF, betting outlets) value the same general signals as data-analyst recruiters, with one addition: **demonstrated football literacy** in the writeup (correctly used scheme terminology, sample-size discipline, EPA/situation framing) [VERIFIED: PFF careers page, Open Source Football style review]. They are skeptical of glossy infrastructure that buries the analysis.

**Recommended narrative style: analyst memo** — modeled on Open Source Football posts. Not tutorial (audience is not learning to code), not academic (audience does not want abstracts and methodology sections), not pure dashboard (audience wants reasoning, not just charts). [VERIFIED: opensourcefootball.com style review]

## Feature Landscape

### Table Stakes (Recruiter Bounces If Missing)

These are non-negotiable. None of them differentiate — but each missing one is a fail.

| # | Feature | Why It Matters (Recruiter Mental Model) | Implementation In This Project | Complexity |
|---|---------|-----------------------------------------|--------------------------------|------------|
| TS-01 | **One-paragraph problem statement at top of README** (above any badges) | "Can this person describe a problem in plain English?" — a portfolio without a clear sentence saying *what* and *why* gets bounced in 10 seconds | Two sentences: what NFL question is answered, why it's interesting. No football jargon in the first sentence. | Trivial |
| TS-02 | **Runnable setup block: clone → `pip install -r requirements.txt` → one command → output** | "Will this run on my laptop without 30 minutes of Slack DMs?" — non-runnable repos are the #1 bounce reason cited by hiring managers | Already in SPEC ("≤5 commands, ≤10 min"). Pin `nfl_data_py`. Test on a fresh clone before shipping. | Moderate |
| TS-03 | **Pinned `requirements.txt` with versions** | Reproducibility signal. 29% of notebook executions fail due to ImportError [CITED: ReviewNB study] — a frozen requirements file proves the candidate knows this | `pip freeze > requirements.txt` after a clean install. Pin Python version too (`.python-version` or note in README). | Trivial |
| TS-04 | **README hero chart visible in the first scroll** | The 30-second test. Recruiter sees ONE chart and asks "is this work I'd want to read more of?" | The single most striking finding (e.g., "team X plays Cover-3 80% of the time on 3rd-and-long") rendered as a clean PNG, embedded near the top. NOT a generic methodology diagram. | Moderate |
| TS-05 | **Key findings as 3-4 bulleted statements with numbers** | Recruiters want signal, not vibes. "Stat-first" bullets ("Team X is 73% Cover-3 on 3rd-and-long, league avg 41%") prove insights exist before they read the memo | Calibrate after Phase 1 audit. Each bullet ≤2 lines, each contains a number, each links to the full FINDINGS.md section | Trivial (once analysis exists) |
| TS-06 | **Clear repo description (the GitHub one-liner under the name)** | Appears in search results and LinkedIn previews. Empty description = unsignalled / abandoned repo | One sentence, ~70 chars: "Situational analysis of NFL defensive tendencies, 2022-2025 (FTN + nflfastR)" | Trivial |
| TS-07 | **Logical folder structure with READMEs in subfolders** | Professionalism signal. Flat repos with 30 files in root scream "junior" | SPEC already has this (`etl/`, `queries/`, `analysis/`, `findings/`). Add a one-line README in `data/` explaining how to fetch data. | Trivial |
| TS-08 | **Notebooks run end-to-end on a fresh clone** | Hidden state and out-of-order cells = "this person doesn't understand reproducibility." Recruiters who try to run notebooks and hit errors stop trying | Restart kernel & run-all before every commit. Add a CI check or pre-commit hook if possible. | Moderate |
| TS-09 | **Static charts saved as PNGs in the repo** (not just live notebook outputs) | GitHub renders PNGs in markdown previews, recruiters scrolling on mobile see them. Live notebook charts require clicking through | Already in SPEC (`findings/images/`). Export from notebooks at end of run. | Trivial |
| TS-10 | **Glossary or domain primer for non-football readers** | The audience may not know what "Cover 3" means. PROJECT.md already flags this. Skipping it loses non-football recruiters in 5 seconds | Short glossary section in README OR top of FINDINGS.md, ~6 terms with one-line definitions | Trivial |
| TS-11 | **Sample-size discipline visible in the writeup** | Junior-analyst-tell #1: "Team X is 100% Cover-3" with N=4 plays. Showing the N alongside every claim signals statistical maturity | SPEC already mandates N≥15. Display N in every chart caption and table. | Trivial |
| TS-12 | **No "WIP" / "in progress" / "TODO" markers in shipped repo** | Public WIP markers make recruiters assume the work is incomplete or abandoned | Strip all WIP comments before ship phase. Move incomplete work to a private branch or out of repo. | Trivial |
| TS-13 | **Setup instructions tested on a clean machine** | The most embarrassing portfolio failure: recruiter clones, hits a missing-dep error, closes tab. Untested setup = "candidate ships untested code" | Use a fresh venv or container before final commit; document any system deps (Python 3.11+, sqlite3) | Moderate |
| TS-14 | **Public, not private repo, with at least one substantive commit history** | Recruiters check commit graph. Single "initial commit" with everything = either copy-paste from elsewhere or AI-generated dump | Natural commit history from the GSD workflow already provides this. Don't squash to one commit at ship. | Trivial |

### Differentiators (Move From "Fine" to "Memorable")

These are where this repo competes. Each one adds a memorable hook beyond table stakes.

| # | Feature | Value Proposition (90th-Percentile Signal) | Implementation In This Project | Complexity |
|---|---------|-------------------------------------------|--------------------------------|------------|
| DIFF-01 | **Memo-style FINDINGS.md with 5-7 named insights** (not a tutorial, not a dashboard) | "This person can write." Hiring managers across data and sports-analytics consistently cite communication as the differentiating skill at the entry level [VERIFIED: phData, Dataquest, PFF job descriptions]. A memo with named, quotable insights ("The Patriots' Cover-2 Tell") is shareable internally — that's the signal | Each finding gets a short title, a 1-line summary stat, a chart, ~150 words of analysis, and a sample-size note. Modeled on Open Source Football post structure. | Moderate |
| DIFF-02 | **A single proprietary metric** (the entropy-based predictability score) | Junior portfolios all have descriptive stats. Building one custom metric from a real concept (Shannon entropy) puts the repo above 90% of submissions and gives the candidate something to walk through in interview | Already in SPEC. The "wow piece." Document the metric definition in README and FINDINGS.md, show the leaderboard chart, walk through one team's score | Heavy (but already planned) |
| DIFF-03 | **Architecture diagram in README** (data flow, not file listing) | Shows the candidate thinks in systems, not scripts. A 5-box flowchart (`nfl_data_py` → ETL → SQLite → notebooks → FINDINGS.md) takes 30 seconds to make and signals seniority | Mermaid diagram embedded in README (renders natively on GitHub). Show data sources, transformation, output. NOT a file tree. | Trivial |
| DIFF-04 | **Reproducibility budget stated explicitly** ("Clone-to-first-chart in 5 commands, 10 min") | Most candidates do not advertise this. Stating it as a contract signals the candidate understands recruiters will try to run it, and forces the candidate to actually test the path | One-line callout in README. Write a quickstart that delivers a chart, not just an installed package. | Trivial |
| DIFF-05 | **Visible commit-process discipline** (atomic commits, conventional commits, branching) | Hiring managers DO read commit history when assessing a candidate's "engineering sense." A clean log with `feat(etl): ...`, `docs(findings): ...` style messages is rare among entry-level portfolios and immediately distinguishing | The GSD workflow naturally produces this. Don't squash. Don't force-push. Optionally add a CONTRIBUTING.md or commit-style note in README. | Trivial |
| DIFF-06 | **GitHub repo metadata fully configured** (description, 5-8 topics, social preview image, pinned to profile) | Topics like `nfl-analytics`, `sql`, `python`, `data-analysis`, `nfl-data-py` make the repo discoverable in GitHub topic search. Social preview image (1280×640) makes it preview attractively on LinkedIn shares. ~80% of portfolio repos skip this | Configure during Ship phase (already planned via GitHub MCP). Generate social preview from a hero chart. | Trivial |
| DIFF-07 | **One sample-size-discipline callout in the README** ("Why we required N≥15") | Most junior portfolios over-claim. Explicitly stating the threshold and why is a maturity flex sports analytics audiences will notice | Two sentences in README, plus footnote in every FINDINGS.md insight | Trivial |
| DIFF-08 | **Visible footballSchemaAuditNotebook** (the Phase 1 FTN audit kept as `00_data_audit.ipynb`) | Most portfolios hide the messy exploration. Showing the audit — "we expected Cover 0-6 columns, found these instead, here's how the project pivoted" — is a unique signal that the candidate handles ambiguity, validates assumptions, and documents pivots | Keep the Phase 1 audit notebook in `analysis/` as the first numbered notebook with a short prose intro framing the question | Trivial (as a side effect of doing the audit anyway) |
| DIFF-09 | **One non-obvious chart that's NOT a bar chart** | Junior portfolios are 90% bar charts. One thoughtful viz (e.g., a heatmap of team × situation tendencies, or a small-multiples grid of team coverage profiles) signals visualization literacy | One heatmap or small-multiples chart in FINDINGS.md, exported as PNG | Moderate |
| DIFF-10 | **Tone-matched to the audience** (analytical, slightly wry, no exclamation points or emoji-heavy copy) | NFL analytics culture (Open Source Football, nflverse) writes in a specific register: confident, lightly skeptical, numbers-forward. Matching it signals "I read this stuff" — a real cultural-fit signal for sports analytics teams | Apply during writeup. No emojis in README/FINDINGS.md. No "Welcome to my project!" copy. Open with the question, not the candidate | Trivial |
| DIFF-11 | **Limitations section in FINDINGS.md** | "What this analysis can't tell you" — the single most senior signal in any analytical writeup. Junior analysts oversell findings. Senior analysts pre-empt the skeptical reader | 3-4 bullets at the end of FINDINGS.md: pre-snap labels only, no situational context like O-line health, single-charter subjectivity in FTN tagging, etc. | Trivial |
| DIFF-12 | **`.planning/` committed to repo** | SPEC.md already plans this. Visible engineering process — research, plans, decisions — is itself a recruiter signal that the candidate works systematically | Already planned. Just keep it. | Trivial |

### Anti-Features (Things That LOOK Impressive But Hurt The Signal)

For technically-skilled candidates, these are the common traps. Each one feels productive while building it but produces a *negative* signal at review time.

| # | Anti-Feature | Why It Looks Tempting | Why It Hurts | Alternative |
|---|--------------|-----------------------|--------------|-------------|
| ANTI-01 | **Streamlit / web dashboard** | "Interactive dashboards look impressive" | Adds deployment surface area without improving analytical signal. Recruiters can't reproduce a deployed app — they can reproduce a notebook. Already correctly out-of-scope in SPEC | Static charts in FINDINGS.md, optionally a Plotly chart inside one notebook |
| ANTI-02 | **Docker / docker-compose** | "Containerization signals devops skills" | For a clone-and-run portfolio, Docker is friction. A recruiter on a stock laptop should not need to install Docker to see your work. Signals over-engineering for a tabular Python project | Plain `pip install -r requirements.txt`. Already correctly excluded in SPEC |
| ANTI-03 | **Postgres / DuckDB / cloud DB** | "Real DBs signal real engineering" | Adds setup steps. SQLite is the *correct* choice for portable single-author analytical work. Switching to Postgres just to look serious is over-engineering | SQLite, single file, gitignored if too large. Already correctly chosen in SPEC |
| ANTI-04 | **A `tests/` directory with a few `assert` statements** | "Tests signal engineering rigor" | Trivial test scaffolding (assert column exists) is worse than no tests — it signals cargo-cult engineering. Real test coverage for an analytical project is unusual and not expected | If testing the ETL is valuable, do it as schema-validation in the ETL itself, or as a small "data quality checks" notebook section |
| ANTI-05 | **CI/CD pipeline (GitHub Actions running on every push)** | "I have a green checkmark, look at me" | A green checkmark on a project that just runs a notebook reads as performative. Worse: red checkmarks on broken CI that wasn't maintained = abandoned project | Skip CI. Manually run notebooks pre-ship. If you must, one workflow: "lint and notebook-run on PR" |
| ANTI-06 | **Excessive shields.io badge banner** ("badge soup": Python, build passing, license, code style, version, contributors, last commit, code quality, hits-counter…) | "Badges look professional" | More than ~5 badges starts to look like cargo-cult. Worse: stale badges (broken build, outdated last-commit) actively damage the signal | 3-5 max: language version, key library, license. No "build passing" badge unless CI is genuinely meaningful |
| ANTI-07 | **AI-generated boilerplate README** (the verbose, identical-template, "Welcome to my project!" / "🚀 Features ✨ / 📋 Table of Contents 🛠 / 💻 Tech Stack 🎯 / 🤝 Contributing" template) | "It looks polished" | Recruiters can spot ChatGPT-template READMEs in 3 seconds [VERIFIED: 2025–2026 hiring-manager guidance on AI fakers]. Identical layout, emoji-section-headers, and excessively confident bullet lists with no specific numbers = "this person used AI to fake substance." Massive negative signal | Hand-write the README in the candidate's voice. Open with the question, not a hero greeting. No section emojis. Specific numbers in every bullet. Use AI for spell-check and tone, not generation |
| ANTI-08 | **Tutorial-style writeup** ("First we import pandas… as you can see, the dataframe has 5 columns…") | "I'm explaining my work clearly" | Recruiters and analytics hiring managers are NOT learning from your project. Tutorial style signals "I think the audience doesn't know pandas," which is condescending to the actual audience | Memo style: lead with the finding, support with code only when the *technique* is interesting (e.g., the entropy score), assume the reader is a peer |
| ANTI-09 | **Academic-paper style** (Abstract / Methodology / Results / Discussion / References) | "It looks rigorous" | Wrong audience. NFL/data-analyst recruiters do not read academic papers, they read memos. The structure feels stiff and over-formal | Memo: punchy headline, summary, 5-7 named findings, limitations. Modeled on Open Source Football posts |
| ANTI-10 | **A "machine learning model" as the centerpiece** | "Models signal advanced skills" | A predictive model layered on top of tendency analysis is exactly the scope creep that kills portfolio projects. Models without rigor (no cross-val, no leakage check) actively *damage* the signal — recruiters see junior modeling errors instantly | Already correctly out-of-scope in SPEC. The entropy score is the "wow." |
| ANTI-11 | **"Future work" laundry list at the end of FINDINGS.md** | "Showing ambition" | Reads as "this is unfinished." Recruiters interpret long future-work sections as the candidate admitting the current work is incomplete | One short paragraph. "v2 might add personnel groupings and play-action vulnerability per team." That's it |
| ANTI-12 | **Unfinished branches, draft PRs, or dangling issues visible on the public repo** | "Shows active engineering" | Junior portfolios with 12 open issues and 3 stale branches signal abandonment. Hiring managers prefer a single clean main branch | Ship clean. Close issues before going public. Delete merged branches |
| ANTI-13 | **Heavy use of jargon-only or in-group football terms with no glossary** | "I sound like an insider" | Half the recruiters reviewing this won't be football people. Talking only about "Quarters," "Tampa-2," "MOFO/MOFC" without definitions loses non-football reviewers — which is the majority of entry-level data-analyst recruiters | Use the terms (cultural fit signal), but define on first use, and provide a 6-term glossary |
| ANTI-14 | **Speculation framed as conclusion** ("Team X is bad in the red zone because their coordinator can't adjust") | "Strong takes are memorable" | Causal claims from observational data are an instant red flag for any analytics hiring manager. They signal "this candidate doesn't understand correlation vs. causation" | Frame all causal language as descriptive: "Team X's red-zone Cover-3 rate dropped 18 pts week 8-12 — without coordinator-level data we can't attribute the change" |
| ANTI-15 | **Betting / DFS / wagering framing** | "Sports analytics = money = interesting" | NFL teams, league-side analytics, and most respected outlets explicitly avoid betting framing. PFF and the Athletic position themselves as analytical, not predictive-for-profit. Betting framing narrows the recruiter audience | Already correctly out-of-scope in SPEC. Frame as "exploitable matchups for offensive coordinators," not "edges for bettors" |
| ANTI-16 | **Excessive `print()` debug output left in notebooks** | (Side effect of normal dev) | Cluttered notebook output makes recruiters bounce. Outputs like `df.head()` 14 times in one notebook = "didn't clean up before shipping" | Restart kernel, run-all, review every cell's output before commit. Each output should be intentional |
| ANTI-17 | **A `data/raw/` folder with 200MB of CSVs checked into git** | "I bundled the data so it's reproducible" | Bloats clone times. GitHub may reject. Signals lack of git literacy | `.gitignore` raw data. Document the `nfl_data_py` fetch command. Optionally check in a small SQLite if <50MB |
| ANTI-18 | **Comparison to PFF or other paid sources you don't have access to** | "Showing depth of football knowledge" | Already correctly excluded in SPEC. Public portfolio projects can't redistribute paid data, and comparisons made *without* paid data are speculation | Stick to FTN + nflfastR. Note the PFF gap as a limitation, not a comparison |
| ANTI-19 | **Self-deprecating language in the README** ("This is just a small project I made to learn…") | "Modesty is good" | Hiring managers read this as a candidate signaling low confidence in their own work. Worse than no statement | Confident, factual: "This project examines [X] using [Y] across [Z] seasons." Let the work speak |
| ANTI-20 | **A custom logo / branded header image at the top of README** | "Visual polish" | For a personal portfolio analysis project, branded headers signal "trying too hard." Energy spent on a logo is energy not spent on the analysis | Skip the logo. The hero CHART is the visual hook |

## Sports-Analytics-Specific Signal Notes

Beyond the generic data-analyst signals, sports-analytics audiences (NFL teams, PFF, ESPN, the Athletic, betting markets) value a few additional signals that are worth calling out separately. Confidence MEDIUM — based on Open Source Football style review, PFF careers page, nflverse community norms, and SumerSports public writeups.

| Signal | Why Sports Analytics Audiences Care | How To Implement Cheaply |
|--------|-------------------------------------|--------------------------|
| **Correct use of EPA framing** | EPA is the lingua franca of NFL analytics. Treating it correctly (per-play, situation-adjusted, with sample-size respect) signals "I read the literature" | Already mandated in SPEC. Use EPA as the value metric, not raw yards or success rate alone |
| **nflverse / nfl_data_py credit in README and writeup** | The community is small and notices when work builds on their tools. A one-line credit ("Built on nflverse / `nfl_data_py` — Carl, Baldwin, et al.") is good etiquette and signals cultural awareness | Single line in README acknowledgments + one in FINDINGS.md |
| **Charting source acknowledgment (FTN)** | Sports analytics audiences are sensitive to data-source provenance. Crediting FTN's chart-by-hand work signals respect for data labor | "Coverage labels via FTN charting (`nfl_data_py.import_ftn_data`)" — one line |
| **Realistic football register** (no "the offense REKT the defense" copy) | Sports analytics culture is dry-witty, not bro-y. Open Source Football, nflverse blogs, and Athletic analytics pieces all share this register | Match the tone. Confident, slightly skeptical, numbers-forward. No exclamation points |
| **Acknowledging the things you can't see** (post-snap rotation, disguise, MOFO/MOFC pre-snap vs post-snap) | Real coverage analysis is hard because pre-snap labels lie. Naming this in the limitations section signals football literacy | One bullet in the limitations section: "FTN labels are post-snap; pre-snap disguises that match the eventual look will read as honest tendencies in this data" |

## The 30-Second Test (First Scroll, No Clicks)

What a recruiter sees in the first viewport on desktop:

1. **Repo name + description** — clear, NFL-specific, includes the data sources
2. **One-paragraph problem statement** — what question, why it matters
3. **One hero chart** — the most striking finding, as PNG, no scrolling required
4. **3-4 key-finding bullets** — stat-first, each with a number

If any of those four fail, the recruiter bounces. Everything else (architecture diagram, setup, notebooks) is the 90-second test.

## The 90-Second Test (One Scroll, Maybe One Click)

What a recruiter sees if the 30-second test passes:

5. **Setup block** — clone, pip, run, see chart. ≤5 commands.
6. **Architecture diagram** — Mermaid, data flow, 5 boxes.
7. **Folder structure walkthrough** — 6 lines, what's in each folder.
8. **Link to FINDINGS.md** — the deeper memo.
9. **Tech stack badges (≤5)** — language, key library, license.
10. **Acknowledgments** — nflverse, FTN.

If they click through to FINDINGS.md, they're now a 5-minute reader. The conversion rate from 90-second skim to FINDINGS.md click is the single best predictor of interview conversion for portfolio-driven recruitment.

## Feature Dependencies

```
TS-04 (hero chart) ──requires──> DIFF-01 (FINDINGS.md memo with named insights)
                                           └──requires──> DIFF-02 (entropy score, the headline finding)

TS-05 (key findings bullets) ──requires──> DIFF-01 (memo to link bullets into)

TS-08 (notebooks run end-to-end) ──requires──> TS-02 (working setup) ──requires──> TS-03 (pinned requirements)

DIFF-08 (visible audit notebook) ──requires──> Phase 1 FTN schema audit (already in plan)

DIFF-06 (GitHub metadata) ──requires──> Ship phase (already planned via GitHub MCP)

ANTI-07 (no AI-template README) ──conflicts──> using AI to draft the README from a generic prompt
   └─ alternative: hand-write README, use AI only for tone/spell-check passes
```

### Dependency Notes

- **TS-04 (hero chart) requires DIFF-01 (memo) requires DIFF-02 (entropy score):** the hero chart is most likely the predictability-score leaderboard, which only exists once the entropy work is done. Hero chart selection is a Phase-late decision, not a Phase-1 one.
- **TS-08 (notebook reproducibility) requires TS-02 + TS-03:** all three are about clone-and-run discipline; they ship together or not at all.
- **DIFF-08 (audit notebook) is a side effect** of doing Phase 1 well — keep the artifact, don't delete it.
- **ANTI-07 conflicts with AI-first README drafting:** the README must be written in the candidate's voice. Generic-template AI output is worse than no README. AI is fine for proofreading, NOT for first drafts.

## MVP Definition (Ship Cut)

### Launch With (v1, ship-blocking)

All Table Stakes (TS-01 through TS-14) plus the highest-leverage Differentiators:

- [ ] TS-01 to TS-14 (every table stake — these are bounce reasons)
- [ ] DIFF-01: Memo-style FINDINGS.md with 5-7 named insights
- [ ] DIFF-02: Entropy-based predictability score (the "wow")
- [ ] DIFF-03: Architecture diagram (Mermaid in README)
- [ ] DIFF-04: Reproducibility-budget callout
- [ ] DIFF-06: GitHub metadata fully configured (description, topics, social preview, pin)
- [ ] DIFF-07: Sample-size discipline callout
- [ ] DIFF-10: Tone-matched copy (analytical, no emojis, no greetings)
- [ ] DIFF-11: Limitations section
- [ ] DIFF-12: `.planning/` committed

### Add If Time Permits (still v1, nice-to-have)

- [ ] DIFF-05: Visible commit-process discipline (mostly a side effect of GSD workflow, but verify before ship)
- [ ] DIFF-08: Audit notebook kept and framed
- [ ] DIFF-09: One non-bar-chart visualization in FINDINGS.md

### Out of Scope (v2+, do not pursue in v1)

- Web dashboard / Streamlit (ANTI-01)
- Docker (ANTI-02)
- ML model on top of tendency analysis (ANTI-10)
- CI/CD beyond hand-running notebooks (ANTI-05)
- Personnel grouping / play-action depth (already in SPEC stretch goals)

## Feature Prioritization Matrix

Compressed view of the highest-priority items. Priority key:
- **P1**: Bounce-reason if missing (table stakes) OR top-2 differentiator. Ship-blocking.
- **P2**: Strong differentiator. Add if time, do not block ship.
- **P3**: Polish. Nice to have, low risk if skipped.

| ID | Feature | Recruiter Value | Implementation Cost | Priority |
|----|---------|-----------------|---------------------|----------|
| TS-01 | One-paragraph problem statement | HIGH | LOW | P1 |
| TS-02 | Runnable setup block | HIGH | MEDIUM | P1 |
| TS-03 | Pinned requirements.txt | HIGH | LOW | P1 |
| TS-04 | README hero chart | HIGH | MEDIUM | P1 |
| TS-05 | Key findings bullets with numbers | HIGH | LOW | P1 |
| TS-06 | Repo description | HIGH | LOW | P1 |
| TS-07 | Logical folder structure | HIGH | LOW | P1 |
| TS-08 | Notebooks run end-to-end | HIGH | MEDIUM | P1 |
| TS-09 | Static charts as PNGs | HIGH | LOW | P1 |
| TS-10 | Glossary | HIGH | LOW | P1 |
| TS-11 | Sample-size discipline | HIGH | LOW | P1 |
| TS-12 | No WIP markers | HIGH | LOW | P1 |
| TS-13 | Setup tested on clean machine | HIGH | MEDIUM | P1 |
| TS-14 | Substantive commit history | HIGH | LOW | P1 |
| DIFF-01 | Memo-style FINDINGS.md | HIGH | MEDIUM | P1 |
| DIFF-02 | Entropy predictability score | HIGH | HIGH | P1 |
| DIFF-03 | Architecture diagram | HIGH | LOW | P1 |
| DIFF-04 | Reproducibility-budget callout | MEDIUM | LOW | P1 |
| DIFF-06 | GitHub repo metadata | HIGH | LOW | P1 |
| DIFF-07 | Sample-size callout | MEDIUM | LOW | P1 |
| DIFF-10 | Tone-matched copy | HIGH | LOW | P1 |
| DIFF-11 | Limitations section | HIGH | LOW | P1 |
| DIFF-12 | `.planning/` committed | MEDIUM | LOW | P1 |
| DIFF-05 | Clean commit log | MEDIUM | LOW | P2 |
| DIFF-08 | Audit notebook visible | MEDIUM | LOW | P2 |
| DIFF-09 | One non-bar-chart viz | MEDIUM | MEDIUM | P2 |

## Reference Portfolios Reviewed

Strong examples consulted for structural patterns (cited as comparison points, NOT as direct templates to copy):

- **Open Source Football** ([opensourcefootball.com](https://opensourcefootball.com/)) — the gold standard for NFL analytics writeups; memo style, EPA-fluent, tone-confident. The FINDINGS.md should pattern-match to this register.
- **nflverse** ([nflverse.nflverse.com](https://nflverse.nflverse.com/)) — the package ecosystem this project sits inside; their README discipline (clear scope, credits, version pinning) is the reference for cross-language equivalent.
- **nktnlx/data_analysis_portfolio** — entry-level data-analyst portfolio with consistent project documentation pattern (description, skills, stack, results); good template for ordering within FINDINGS.md.
- **tiannaparris/Data-Analysis-Portfolio** — frequently cited as a "looks professional" entry-level analyst portfolio.

These are reference points, not copy targets. The candidate's voice and the NFL-specific register matter more than mimicking any single repo.

## Sources

### Primary (HIGH confidence)
- [Dataquest: How to create a data science portfolio for job applications](https://www.dataquest.io/blog/career-guide-data-science-projects-portfolio/) — recruiter scanning, anti-patterns, narrative style
- [phData: Why Your GitHub May Matter More Than Your Degree](https://www.phdata.io/blog/why-your-github-may-matter-more-than-your-degree/) — explicit hiring-manager red flags including "over-polished code that seems inauthentic" (the AI-generated tell)
- [KDnuggets: Develop a Stand-out Data Science Portfolio with GitHub](https://www.kdnuggets.com/develop-stand-out-data-science-portfolio-github) — README structure, profile README, pinning
- [Open Source Football](https://opensourcefootball.com/) — NFL analytics writeup register and structure
- [365 Data Science: How to Build a Data Analyst Portfolio (2025)](https://365datascience.com/career-advice/how-to-build-a-data-analyst-portfolio/) — current 2025 portfolio guidance
- [ReviewNB: Production Jupyter Notebook Reproducibility](https://blog.reviewnb.com/jupyter-notebook-reproducibility-managing-dependencies-data-secrets/) — the 29% ImportError stat, requirements.txt discipline
- [Coursera: How to Build a Data Analyst Portfolio](https://www.coursera.org/articles/how-to-build-a-data-analyst-portfolio) — entry-level expectations
- [Careery (2026): Data Analyst Portfolio Projects That Actually Get You Hired](https://careery.pro/blog/data-analyst-careers/data-analyst-portfolio-projects) — 3-5 project sweet spot, project tier mix

### Secondary (MEDIUM confidence)
- [Medium / Write_or_Wrong: Documenting Your Data Analyst Projects on GitHub](https://medium.com/@sarisaldi365/how-and-what-to-put-in-documenting-your-data-analyst-projects-on-github-de9ee5f2bcc1) — README sectioning conventions
- [Refonte Learning: How to Build a Data Science Portfolio That Gets You Hired](https://www.refontelearning.com/blog/how-to-build-a-data-science-portfolio-that-gets-you-hired) — 2024-25 guidance, project quality vs quantity
- [JobsInSports: NFL Data Analytics Jobs (2025)](https://blog.jobsinsports.com/2025/10/06/nfl-data-analytics-jobs/) — sports analytics hiring landscape
- [PFF Careers / Pro Football Focus](https://www.pff.com/jobs) — sports analytics employer expectations
- [interviewquery: How to Create a Stand Out Data Analyst Portfolio (Updated for 2025)](https://www.interviewquery.com/p/how-to-create-a-data-analyst-portfolio) — 2025 update on what's changed
- [Pragmatic Engineer: AI Fakers Exposed in Tech Dev Recruitment](https://newsletter.pragmaticengineer.com/p/ai-fakers) — how recruiters detect AI-generated content (informs ANTI-07)

### Tertiary (LOW confidence — cited but not load-bearing)
- [nktnlx/data_analysis_portfolio](https://github.com/nktnlx/data_analysis_portfolio) — example portfolio structure
- [tiannaparris/Data-Analysis-Portfolio](https://github.com/tiannaparris/Data-Analysis-Portfolio) — example portfolio structure
- [pkukkapalli/nfldata](https://github.com/pkukkapalli/nfldata) — NFL+SQLite reference pattern
- [Reddit data career discussion recap](https://www.datanomadslab.com/p/data-careers-skills-and-tools-reddit) — community sentiment, secondhand

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | NFL/sports-analytics audiences specifically value "memo style" over tutorial style | DIFF-01, ANTI-08, ANTI-09 | Medium — based on Open Source Football and PFF style review, but no NFL-team hiring-manager interviews directly cited. If wrong, the writeup is still strong, just not optimally tone-matched |
| A2 | Recruiters can reliably spot AI-generated README boilerplate | ANTI-07 | Low — multiple 2025-2026 hiring sources cite this, but specific data-analyst-portfolio AI-detection rates are not published |
| A3 | A 30-second / 90-second skim is the realistic recruiter behavior | TS-04, TS-05, "30/90 second test" sections | Low — widely repeated in 2025 portfolio guidance, though specific time figures vary (some cite 6 seconds, some cite 2 minutes) |
| A4 | Sports analytics teams (NFL clubs, PFF, ESPN, the Athletic) value the same general portfolio signals as data-analyst hiring managers | "Sports-Analytics-Specific Signal Notes" | Medium — based on PFF careers page and nflverse community norms; teams' actual portfolio review processes are not public |
| A5 | The entropy / predictability score is genuinely a 90th-percentile differentiator | DIFF-02 | Low — building a custom metric from a real concept is consistently cited as a strong signal. The risk is that entropy specifically might be underwhelming if poorly explained, but the SPEC already plans the writeup |
| A6 | GitHub repo metadata (topics, social preview) measurably affects perception | DIFF-06 | Low — visible-but-low-impact. Worst case: ignored. Cost is trivial, so include regardless |

**If a downstream consumer wants to lock any of these:** A1 and A4 are the highest-leverage to confirm with Nick — the writeup-style decision (memo vs tutorial vs academic) is upstream of how FINDINGS.md is structured. A2-A3-A5-A6 are robust enough to proceed without further validation.

## Open Questions

1. **Does Nick want a profile-level README on his GitHub username repo?**
   - What we know: Profile READMEs are a known portfolio multiplier when there are multiple pinned repos
   - What's unclear: Whether this is the only portfolio repo or one of several
   - Recommendation: Out of scope for this project; flag for Nick separately. If this is one of 3-5 portfolio pieces, a profile README is worth a few hours of work as a meta-project

2. **Should the FINDINGS.md be split or single-file?**
   - What we know: Memo style favors a single readable document
   - What's unclear: Whether 5-7 insights fit in one document without becoming long; long memos lose recruiters past insight 3
   - Recommendation: Single file, ~1500-2500 words total, headed by an executive summary. Each insight ~200-400 words. If it grows past 3000 words, split off the entropy methodology into a separate doc

3. **Should the repo include a small "exploratory results" appendix showing the dead-ends?**
   - What we know: Showing pivots is a strong DIFF-08 signal
   - What's unclear: Whether exposing every dead-end clutters the repo
   - Recommendation: One audit notebook (DIFF-08) is enough. Don't expand into a full "things we tried" document — that becomes ANTI-11 (laundry-list)

4. **What's the right length for the README itself?**
   - What we know: 90-second test = ~400-600 words readable in that time
   - What's unclear: How much to include before linking to FINDINGS.md
   - Recommendation: README ~500 words / one screen scroll. Key findings teaser, hero chart, setup, architecture, link to FINDINGS.md. Push depth into FINDINGS.md

## Metadata

**Confidence breakdown:**
- Table stakes: HIGH — consistent across 8+ 2025 sources, hiring-manager guidance largely converges
- Differentiators: HIGH for general DA signals, MEDIUM for sports-analytics-specific signals (smaller public sample)
- Anti-features: HIGH — the AI-template trap (ANTI-07) and over-engineering traps (ANTI-01, ANTI-02, ANTI-04, ANTI-05) are explicitly cited in 2025-2026 hiring sources
- Sports analytics signals: MEDIUM — derived from public community norms (Open Source Football, nflverse) and PFF careers page; NFL-team hiring managers don't publish portfolio-review rubrics

**Research date:** 2026-04-29
**Valid until:** ~2026-07-29 (3 months — portfolio conventions move slowly, AI-detection signals move faster)

---
*Feature research for: NFL coverage tendencies portfolio repo*
*Researched: 2026-04-29*
