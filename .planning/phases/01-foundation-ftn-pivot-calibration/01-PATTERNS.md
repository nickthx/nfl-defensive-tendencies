# Phase 1: Foundation & FTN Pivot Calibration - Pattern Map

**Mapped:** 2026-04-29
**Files analyzed:** 17 (7 BOOT artifacts + 7 AUDIT artifacts + 3 directory-tree placeholders)
**Analogs found:** 6 / 17 in-repo; 8 / 17 in `.planning/research/` (style/voice analogs); 3 / 17 greenfield (establish pattern)

**Greenfield reality:** The repo currently contains only `.git/`, `.gitignore`, `CLAUDE.md`, `SPEC.md`, `.planning/`, and `venv/`. There are no Python source files, no notebooks, no schema. Phase 1 establishes the patterns that Phases 2–4 will copy. Where in-repo analogs do exist (existing `.gitignore`, `SPEC.md`, `CLAUDE.md`, the `.planning/research/*.md` corpus), they are explicit anchors and excerpts are extracted below. Where no analog exists, the canonical reference is the relevant section of `.planning/research/SUMMARY.md`, `.planning/REQUIREMENTS.md`, `.planning/research/STACK.md`, `.planning/research/ARCHITECTURE.md`, or `.planning/research/PITFALLS.md`.

---

## File Classification

### Plan 01-01: Bootstrap (BOOT-01..07)

| File / Artifact | Role | Data Flow | Closest Analog | Match Quality |
|-----------------|------|-----------|----------------|---------------|
| `requirements.txt` | config (pinned deps) | static manifest | `.planning/research/SUMMARY.md` §Consolidated Stack (canonical pin block) | reference-not-analog |
| `pyproject.toml` | config (lint config only) | static manifest | `.planning/research/STACK.md` §Linting (the `[tool.ruff]` block at lines 165-175) | reference-not-analog |
| `.python-version` | config (single-line) | static manifest | none — establishes pattern (file is literally the string `3.11\n`) | greenfield |
| `.gitignore` (expanded) | config | static manifest | `./.gitignore` (existing 455-byte version at repo root) | exact role-match (expand-in-place) |
| `README.md` (skeleton) | doc | hand-written prose | `CLAUDE.md` §Audience Voice (voice rules) + `.planning/research/SUMMARY.md` §Consolidated Feature Priority (P1 + Anti-Features) | role-match (voice/style) |
| Repo skeleton dirs (`data/`, `data/raw/.gitkeep`, `schema/`, `etl/`, `queries/`, `analysis/`, `findings/`, `findings/images/`, `audit/`, `docs/`) | structure | static | `.planning/research/ARCHITECTURE.md` §Directory Tree (canonical tree at lines 102-153 of ARCHITECTURE.md) | reference-not-analog |
| `data/README.md` (placeholder; full version is Phase 4 DOC-08, but a stub may land in Phase 1) | doc | static | none in-repo; SPEC.md is closest tone analog | role-match (voice/style) |

### Plan 01-02: FTN Audit (AUDIT-01..07)

| File / Artifact | Role | Data Flow | Closest Analog | Match Quality |
|-----------------|------|-----------|----------------|---------------|
| `analysis/00_data_audit.ipynb` | notebook (exploratory) | network pull → DataFrame → CSV export | none in-repo (greenfield); reference `.planning/research/STACK.md` §1 lines 88-93 (column inventory call) and `.planning/research/ARCHITECTURE.md` §Pattern 1 lines 184-201 (loader pattern) | reference-not-analog |
| `audit/ftn_null_profile.csv` | data artifact | DataFrame → CSV | none — establishes pattern | greenfield |
| `docs/ftn-schema-audit.md` | doc (analytical narrative) | static prose | `.planning/research/PITFALLS.md` (Pitfall 2, lines 36-53 — discusses the FTN-no-coverage-labels finding in the exact narrative voice the audit doc must adopt) + `.planning/research/SUMMARY.md` §TL;DR (memo-style framing) | role-match (voice/style) |
| `docs/analysis-plan.md` | doc (pre-registration) | static prose | `.planning/research/PITFALLS.md` (Pitfall 9, lines 217-237 — pre-registration pattern) + CONTEXT.md §D-06/D-08 (the 4 situations + falsifiable-hypothesis format) | role-match (structure/voice) |
| `SPEC.md` (in-place rewrite per AUDIT-06) | doc (rewritten) | static prose | `./SPEC.md` (existing pre-pivot file) | exact (in-place rewrite) |
| `README.md` (hook rewrite per AUDIT-07) | doc (hook section only) | static prose | `CLAUDE.md` §Audience Voice (voice rules at lines 99-107 of CLAUDE.md) + `.planning/research/SUMMARY.md` §TL;DR first bullet (the post-pivot framing already exists in plain English) | role-match (voice/style) |
| `.planning/PROJECT.md` Key Decisions (append D-09 row) | doc (table append) | static prose | `.planning/PROJECT.md` (existing Key Decisions table) | exact (in-place append) |

---

## Pattern Assignments

### `requirements.txt` (config, static manifest)

**Analog:** none in-repo. **Canonical reference:** `.planning/research/SUMMARY.md` §Consolidated Stack lines 66-91.

**Pin block to copy verbatim** (from `.planning/research/SUMMARY.md` lines 67-91):

```text
# requirements.txt — v1 LOCKED
# Data layer (archived upstream; intentional pin — see README "Known Issues")
nfl_data_py==0.3.3

# Numerical / data
pandas>=2.1,<2.3
numpy>=1.26,<2.0          # forced — nfl_data_py 0.3.x uses np.float_, removed in NumPy 2.0
pyarrow>=15,<22           # parquet I/O; required transitively by nfl_data_py

# Statistical
scipy>=1.13,<1.18         # chi2_contingency + entropy

# Visualization
matplotlib>=3.8,<3.11
seaborn==0.13.2           # exact pin — only release in 0.13.x line

# Notebooks
jupyterlab>=4.2,<4.6
ipykernel>=6.29,<8
jupytext>=1.16,<2         # paired .py representation for clean git diffs
nbconvert>=7.16,<8        # for one-time clear-output before commit

# Dev tooling
ruff>=0.6,<1.0
```

**Constraint applies (CLAUDE.md "Locked Stack"):** Path A locked. NO `nflreadpy`. NO upper-bound game on `nfl_data_py` (there will never be a 0.3.4 — package archived). NO `pandas>=2.2` — REQUIREMENTS.md BOOT-02 pins `pandas>=2.1,<2.3` (matches Architecture researcher's tested-against-nfl_data_py band; do not silently drift to STACK.md's `>=2.2,<2.4` recommendation).

**Pitfall #8 governs (PITFALLS.md lines 384-414):** every line MUST be tightly bounded; `numpy<2.0` is non-negotiable.

---

### `pyproject.toml` (config, lint only)

**Analog:** none in-repo. **Canonical reference:** `.planning/research/STACK.md` lines 165-175.

**Block to copy verbatim** (from `.planning/research/STACK.md` lines 166-175):

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]   # pycodestyle, pyflakes, isort, bugbear, pyupgrade
ignore = ["E501"]                      # let line-length do that work; long URL strings are fine
```

**Constraint applies (REQUIREMENTS.md BOOT-04):** `[tool.ruff]` config ONLY. Do NOT add `[project]`, `[build-system]`, or any package-metadata sections — this is an analysis repo, not a library. `requirements.txt` is the install manifest (per STACK.md §7 lines 151-160 and CLAUDE.md "Locked Stack").

---

### `.python-version` (config, single-line)

**Analog:** none — file is the literal string `3.11\n`. Establishes pattern.

**Constraint applies (CLAUDE.md "Locked Stack"):** Python 3.11 only — NOT 3.12, NOT 3.13. `nfl_data_py` 0.3.x install fails on 3.13 (PITFALLS.md Pitfall #1 ref to issue #122).

---

### `.gitignore` (config, expand-in-place)

**Analog (in-repo, exact role-match):** `./.gitignore` — existing 455-byte file. Already covers Python (`venv/`, `__pycache__/`), Jupyter (`.ipynb_checkpoints/`), OS/editor noise (`.DS_Store`, `.vscode/`, `.idea/`), data (`data/raw/`, `data/*.parquet`, `data/*.db-journal`), and secrets (`.env`, `.env.local`, `*.key`, `*.pem`).

**Existing imports/structure** (lines 1-31 of `./.gitignore`):

```gitignore
# Python
venv/
.venv/
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
.pytest_cache/
.ipynb_checkpoints/

# Jupyter
*.ipynb_checkpoints

# OS / editor
.DS_Store
Thumbs.db
.vscode/
.idea/

# Data — large raw pulls, keep out of git
data/raw/
data/*.db-journal
data/*.parquet
# Note: data/nfl_coverage.db tracked decision deferred to ship phase (size-dependent)

# Secrets (defensive, even though this project shouldn't have any)
.env
.env.local
*.key
*.pem
```

**Pattern: what BOOT-03 must add** (per REQUIREMENTS.md BOOT-03 + PITFALLS.md Pitfall #14 lines 336-358 + #18 lines 446-466):

1. `*.db` (BOOT-03 explicitly lists this; the existing file has `data/*.db-journal` but NOT `*.db` — the line `# Note: data/nfl_coverage.db tracked decision deferred...` must be replaced with a hard `*.db` line, since CLAUDE.md and PROJECT.md have now LOCKED `.db` as gitignored).
2. `.env*` glob (existing has `.env` and `.env.local` literals; replace with `.env*` to catch `.env.production`, `.env.foo`, etc.).
3. `scratch/` and `scratch*` (per CLAUDE.md "File-Organization Rules" — "If you need throwaway work, put it in `scratch/` (gitignored)").
4. `tmp_*` and `*.log` (PITFALLS.md Pitfall #18 line 454).
5. Confirm `data/raw/` and `__pycache__/` and `.ipynb_checkpoints/` and `venv/` remain (they are already present).

**Constraint applies (PITFALLS.md Pitfall #14):** `.db` IS gitignored — locked. Replace the deferral comment with a hard exclusion. Do NOT use `git add -f` on any `.db` file.

---

### `README.md` (skeleton, BOOT-06)

**Analog (voice/style — in-repo):** `CLAUDE.md` §Audience Voice lines 99-107 of CLAUDE.md (project-level rules).

**Voice rules to honor (excerpt from CLAUDE.md lines 99-107):**

```markdown
- **Memo style**, not tutorial. The reader is a peer (recruiter, hiring manager, analyst), not a student.
- **No exclamation points, no emoji section headers, no "Welcome to my project!" greetings.**
- **Numbers first.** "The Bills blitz 38% on 3rd-and-long (N=247)." Not: "The Bills are an aggressive blitzing defense."
- **State sample size inline** with every claim.
- **Limitations section** is mandatory in `FINDINGS.md`. Name what the data CAN'T tell you.
```

**Anti-features list to honor (excerpt from `.planning/research/SUMMARY.md` lines 142-156, P3 list):**

```markdown
- AI-generated README boilerplate (emoji-section-header + "Welcome to my project!" — biggest negative signal)
- Streamlit / web dashboard
- Excessive shields.io badge soup (>5)
- Tutorial-style writeup ("First we import pandas…")
- Academic structure (Abstract / Methods / Results / Discussion)
- Custom logo / branded header image
- Self-deprecating language ("This is just a small project…")
- Betting / DFS / wagering framing
- "Future work" laundry list
```

**Skeleton section list (per CONTEXT.md §Claude's Discretion bullet 1 — defaulted to standard portfolio README structure):**

```markdown
# NFL Defensive Tendencies

## Hook
<!-- 2-3 sentences, plain English, names the public-FTN pivot. Filled in AUDIT-07. -->

## Findings preview
<!-- 3-4 stat-first bullets with N inline. Placeholders in Phase 1; numbers fill in Phase 4. -->

## Architecture
<!-- Mermaid diagram (data flow, not file tree). Built in Phase 4 / DOC-04. -->

## Setup
<!-- 5-command block: clone, venv, pip install, python -m etl.run, jupyter. Built in Phase 4 / DOC-05. -->

## Glossary
<!-- 6 football terms (down, distance, EPA, blitz, RPO, predictability index). Built in Phase 4 / DOC-06. -->

## Methodology
<!-- Brief — link to FINDINGS.md for the full version. -->

## Limitations
<!-- What public FTN can't tell us (no Cover 0-6, charter subjectivity, etc.). -->

## Attribution
<!-- FTN Data via nflverse, CC-BY-SA 4.0; nflfastR. Per DOC-07. -->

## Known Issues
<!-- nfl_data_py archived 2025-09-25; v2 migration path. Per DOC-07. -->
```

**Constraint applies (PITFALLS.md Pitfall #20 lines 502-521):** every claim in README must map to a real query / notebook cell / FINDINGS.md insight. In Phase 1, the README is a SKELETON with empty bodies — no claims yet. AUDIT-07 fills only the Hook with a 2-3 sentence post-pivot framing, with placeholder slots (e.g., `<HEADLINE_NUMBER_1>`) for headline numbers Phase 4 will fill.

---

### Repo skeleton directories (BOOT-01)

**Analog:** none in-repo. **Canonical reference:** `.planning/research/ARCHITECTURE.md` §Directory Tree lines 102-153 + `.planning/research/SUMMARY.md` §Consolidated Architecture Sketch lines 165-220 + CLAUDE.md §Project Structure lines 36-58.

**Directories to create** (per REQUIREMENTS.md BOOT-01 + ARCHITECTURE.md tree):

- `data/` (Phase 4 / DOC-08 will put a real README here; Phase 1 may add a stub)
- `data/raw/` with `.gitkeep` (so the gitignored directory exists for ETL to write into)
- `schema/` (empty in Phase 1; Phase 2 fills with `01_create_tables.sql`, `02_indexes.sql`, `03_views.sql`)
- `etl/` (empty in Phase 1; Phase 2 fills)
- `queries/` (empty in Phase 1; Phase 3 fills with `01_*.sql`..`08_*.sql`)
- `analysis/` (Phase 1 lands `00_data_audit.ipynb` here; Phase 3 adds `_common.py`, `_style.py`, `01_exploratory.ipynb`, `02_predictability_modeling.ipynb`, `03_visualizations.ipynb`)
- `findings/` and `findings/images/` (Phase 4 fills)
- `audit/` (Phase 1 lands `ftn_null_profile.csv` here)
- `docs/` (Phase 1 lands `ftn-schema-audit.md` and `analysis-plan.md` here)

**Constraint applies (CLAUDE.md §File-Organization Rules):** never save scratch / WIP files to repo root. `tests/` directory is NOT created (CLAUDE.md: "there is no `tests/` directory by default. Assertions live inside the ETL... Do not add a cargo-cult `tests/` directory with trivial asserts.").

---

### `analysis/00_data_audit.ipynb` (notebook, exploratory)

**Analog:** none in-repo (greenfield). **Canonical references:**

1. `.planning/research/STACK.md` §1 lines 88-93 — column inventory expectations and the Phase 1 audit task list.
2. `.planning/research/ARCHITECTURE.md` §Pattern 1 lines 184-201 — loader pattern (Phase 2 will reuse this; Phase 1's audit notebook does an in-notebook simplified version).
3. `.planning/research/PITFALLS.md` Pitfall #4 lines 89-110 — the NaN-by-`play_type` breakdown.

**Pattern: notebook structure to establish** (synthesized from REQUIREMENTS.md AUDIT-01..02 + PITFALLS.md Pitfall #4 + CONTEXT.md §D-01/D-02):

```python
# Cell 1 — Imports + setup
import nfl_data_py as nfl
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

SEASONS = [2022, 2023, 2024]
AUDIT_DIR = Path("../audit")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# Cell 2 — Pull FTN charting (~30-90s on cold cache)
ftn = nfl.import_ftn_data(SEASONS)
print(f"FTN frame: {len(ftn):,} rows × {len(ftn.columns)} columns")
print(ftn.columns.tolist())

# Cell 3 — Pull pbp (for play_type join)
pbp = nfl.import_pbp_data(SEASONS, columns=['game_id', 'play_id', 'play_type', 'season'])
# Note: FTN keys are nflverse_game_id / nflverse_play_id; pbp keys are game_id / play_id.
# These match. See PITFALLS.md Pitfall #3.

# Cell 4 — Join FTN ↔ pbp on the canonical play key for play_type lookup
joined = ftn.merge(
    pbp,
    left_on=['nflverse_game_id', 'nflverse_play_id'],
    right_on=['game_id', 'play_id'],
    how='left',
    validate='one_to_one',  # PITFALLS.md Pitfall #3
)
match_rate = joined['play_type'].notna().mean()
assert match_rate > 0.95, f"FTN↔pbp match rate {match_rate:.3f} below 0.95 threshold"

# Cell 5 — Per-column NaN rate by play_type (the AUDIT-02 deliverable)
null_profile = (
    joined.groupby('play_type')
    .apply(lambda g: g.isna().mean())
    .T  # rows = columns, cols = play_type
    .round(3)
)
null_profile.to_csv(AUDIT_DIR / "ftn_null_profile.csv")

# Cell 6 — Visualize NaN rate (for recruiter-presentable polish)
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(null_profile, annot=True, cmap='Reds', vmin=0, vmax=1, ax=ax)
ax.set_title("FTN per-column NaN rate by play_type, 2022–2024")
fig.tight_layout()
# Note: figure is for in-notebook display only; no savefig in Phase 1.

# Cell 7 — Apply the 30% NaN cutoff (D-01, D-02)
# For pressure columns: NaN rate on play_type='pass' must be ≤ 0.30
# For personnel/location columns: NaN rate on competitive plays must be ≤ 0.30
candidate_cols = ['n_blitzers', 'n_pass_rushers', 'is_play_action', 'is_screen_pass',
                  'is_rpo', 'qb_location', 'n_offense_backfield', 'starting_hash']
# ... (compute per-column survival, group by category, document survivors)
```

**Constraint applies (PITFALLS.md Pitfall #3 lines 56-86):** the FTN↔pbp join uses `left_on=['nflverse_game_id', 'nflverse_play_id']` and `right_on=['game_id', 'play_id']` with `validate='one_to_one'`. Wrong keys silently mis-join. This pattern propagates to Phase 2 ETL.

**Constraint applies (PITFALLS.md Pitfall #4 lines 89-110):** `n_blitzers` and `n_pass_rushers` are populated only on pass-context plays. The NaN rate for these columns on `play_type='run'` will be ~100% — that is expected, not a data-quality issue. Document this expectation in the notebook prose.

**Constraint applies (PITFALLS.md Pitfall #17 lines 419-441):** assert on row counts post-pull (`assert len(ftn) > 100_000` for 3 seasons) to catch silent CDN failures.

**Constraint applies (CLAUDE.md "File-Organization Rules"):** notebook lives at `analysis/00_data_audit.ipynb`. Outputs cleared before commit (`jupyter nbconvert --clear-output --inplace`). Notebook stays in repo as recruiter-visible artifact (FEATURES.md P2: "shows pivot reasoning visibly").

---

### `audit/ftn_null_profile.csv` (data artifact, AUDIT-02)

**Analog:** none — establishes pattern.

**Schema (per REQUIREMENTS.md AUDIT-02 + CONTEXT.md §D-01..D-02):**

- Rows: every column in the FTN frame (28 columns).
- Columns: one per `play_type` value (`pass`, `run`, `qb_kneel`, `qb_spike`, `no_play`).
- Cells: NaN rate, rounded to 3 decimal places, range [0.000, 1.000].

**Constraint applies (CONTEXT.md §Claude's Discretion bullet 4):** `play_type` axis is mandatory. Adding a season axis (2022 / 2023 / 2024 separately) is optional polish — do only if Phase 1 execution has slack. If included, document any seasonal differences in `docs/ftn-schema-audit.md`.

---

### `docs/ftn-schema-audit.md` (doc, analytical narrative)

**Analog (voice/style):** `.planning/research/PITFALLS.md` Pitfall 2 lines 36-53 (already names the FTN-no-coverage-labels finding in the exact prose voice the audit doc must adopt).

**Excerpt to model voice from (PITFALLS.md lines 36-37, the headline framing):**

```markdown
**What goes wrong:**
The SPEC's headline business questions ("Which teams run the most Cover 3 on 3rd-and-long?") are not answerable from the public FTN charting data. The nflverse-distributed FTN subset has **28 columns and zero coverage labels**. The full Cover-0-through-6 / man/zone taxonomy is part of FTN's **paid product** (`ftnfantasy.com/data`), not the CC-BY-SA subset published through nflverse.
```

**Required content (per REQUIREMENTS.md AUDIT-03 + CONTEXT.md §D-01..D-04):**

1. The 28-column FTN inventory (printed verbatim from `df.columns.tolist()` in `00_data_audit.ipynb`).
2. The per-column NaN rate by `play_type` (referenced from `audit/ftn_null_profile.csv`; can include a small markdown table excerpt of the 8 candidate columns).
3. The 30% NaN cutoff rule (D-02), applied to:
   - **Pressure / front:** `n_blitzers`, `n_pass_rushers` — measured on `play_type='pass'`.
   - **Play-fakery:** `is_play_action`, `is_screen_pass`, `is_rpo` — measured on `play_type='pass'`.
   - **Personnel / location:** `qb_location`, `n_offense_backfield`, `starting_hash` — measured on competitive plays (`play_type IN ('pass','run')`).
4. The cross-category curation choice (D-01 — mechanical cutoff is rule, story tiebreaker resolves ties for cross-category breadth).
5. The 3 or 4 chosen anchor dimensions (D-03 — aim 4, accept 3 if NaN cuts one).
6. Empty-category contingency narrative if a category has zero survivors (D-04 — document the gap, don't relax the ceiling; fill 4th from surplus).

**Constraint applies (CLAUDE.md §Audience Voice):** memo style. No exclamation points. No emoji section headers. Numbers first.

**Constraint applies (PITFALLS.md Pitfall #1 lines 11-31, Pitfall #2 lines 34-53):** the doc is the explicit, recruiter-readable artifact that proves the candidate looked at the data before writing SQL. Don't bury the FTN-no-coverage-labels finding — name it in the first paragraph.

---

### `docs/analysis-plan.md` (doc, pre-registration)

**Analog (structure/voice):** `.planning/research/PITFALLS.md` Pitfall 9 lines 217-237 (multiple-comparisons trap pattern); CONTEXT.md §D-06 (the 4 situations) and §D-08 (falsifiable-hypothesis format).

**Pre-registration pattern excerpt (PITFALLS.md lines 226-228):**

```markdown
- Choose **3–5 pre-registered situations** in Phase 1 (before looking at data). Document them in `docs/analysis-plan.md`. Examples: 3rd-and-long pass, red-zone runs, 1st-and-10 in opponent territory, 2nd-and-short. These are the only situations FINDINGS.md gets to claim findings on.
```

**Required content (per REQUIREMENTS.md AUDIT-04 + CONTEXT.md §D-05..D-08):**

1. The 4 pre-registered situations (D-06):
   - **3rd-and-long** — `down = 3 AND ydstogo >= 7`.
   - **Red zone** — `yardline_100 <= 20`.
   - **1st-and-10** — `down = 1 AND ydstogo = 10`.
   - **2nd-and-medium** — `down = 2 AND ydstogo BETWEEN 3 AND 6`.
2. The cross-cutting `is_play_action` modifier treatment (D-07 — applied per-situation as a stratifying variable on `play_type='pass'` rows where N permits; NOT a 5th situation).
3. Falsifiable-hypothesis format for each situation (D-08): 1–2 hypotheses each, worded as a prediction. Example template:

```markdown
### Situation 1: 3rd-and-long
**Filter:** `down = 3 AND ydstogo >= 7` on `competitive_plays`.

**Hypotheses (falsifiable):**
- H1: League-wide blitz rate (`n_blitzers > 4`) on 3rd-and-long exceeds 35%. **Falsified if** observed league rate ≤ 35% over 2022–2024.
- H2: At least 3 teams have a blitz rate >50% on 3rd-and-long with N ≥ 100. **Falsified if** fewer than 3 teams meet both thresholds.
```

4. The strict firewall: anything outside these 4 situations stays in `01_exploratory.ipynb` and never appears as a headline insight in `FINDINGS.md`.

**Constraint applies (PITFALLS.md Pitfall #9 lines 217-237):** the slate is locked at 4 situations precisely to avoid the multiple-comparisons trap. Bonferroni / BH correction is NOT needed because the slate is locked at 4 with one chi-square per situation (per CONTEXT.md §Deferred Ideas).

**Constraint applies (CONTEXT.md §Specifics):** "Hypothesis wording must be falsifiable. Per D-08, write 'Defenses blitz at >35% league-wide on 3rd-and-long' — not 'We will look at blitz rates on 3rd-and-long'. The hypothesis names what would falsify it."

---

### `SPEC.md` (in-place rewrite per AUDIT-06)

**Analog (in-repo, exact role-match):** `./SPEC.md` — existing pre-pivot file with the 8 business questions framed around Cover 0–6 / man-zone. AUDIT-06 rewrites these in-place once anchor dimensions are locked from `docs/ftn-schema-audit.md`.

**Existing structure to preserve (from `./SPEC.md` lines 84-94):**

```markdown
## Business Questions to Answer
Each becomes a SQL query, Python analysis, or both. Final wording will be calibrated to whichever defensive dimensions are picked in Phase 1.

1. **Distribution baseline:** What's the league-wide defensive tendency mix on the chosen dimensions? How does each team deviate from baseline?
2. **Down & distance:** Which teams are most predictable on 3rd-and-long? 1st down? Goal-to-go?
3. **Field zone:** How do tendencies change in the red zone vs between the 20s? Backed-up vs midfield?
4. **EPA allowed:** Which defensive looks give up the most EPA per play? Per team?
5. **Predictability score:** Build a single metric per team measuring how predictable their defense is given situation. Rank all 32 teams.
6. **Play-action vulnerability:** Which defensive looks are most exploited by play-action? Which teams stay disciplined?
7. **Drift over time:** Do coordinators adapt week-over-week, or do tendencies stay sticky?
8. **Exploitable matchups:** Identify 2–3 specific team-situation combos with extreme tendencies (>75% one look)
```

**Pattern: how AUDIT-06 rewrites these 8 questions:**

- Replace "defensive tendency mix" / "tendencies" / "looks" with the specific anchor dimensions chosen in `docs/ftn-schema-audit.md` (e.g., "blitz rate (`n_blitzers > 4`)", "pass-rusher count distribution", "play-action rate", "personnel mix").
- Question 6 (Play-action vulnerability) keeps its top-line framing but is reframed per D-07 as a cross-cutting modifier across the other 4 situations rather than its own slate item.
- Question 8 (Exploitable matchups) is reframed to honor the 4-situation pre-registration firewall (per D-05): extreme-tendency claims only come from the 4 pre-registered situations.
- Other CLAUDE.md realities to preserve: no `coverage` column references; FTN↔pbp join keys are `nflverse_game_id`/`nflverse_play_id`.

**Constraint applies (PITFALLS.md Pitfall #20 lines 502-521):** the SPEC rewrite is the README-code-drift prevention step. Every business question after rewrite must map to a real anchor dimension from the audit.

**Constraint applies (REQUIREMENTS.md AUDIT-06):** in-place rewrite. The file path stays `./SPEC.md`. Rewrite the questions, not the project framing — the rest of the SPEC (Audience, Tech Stack, Repo Structure, Out of Scope) is already post-pivot accurate.

---

### `README.md` hook rewrite (AUDIT-07)

**Analog (voice/style — in-repo):** `CLAUDE.md` §Audience Voice + `.planning/research/SUMMARY.md` §TL;DR first bullet (which already names the public-FTN pivot in plain English).

**Excerpt to model voice from (`.planning/research/SUMMARY.md` line 12):**

```markdown
The SPEC's headline framing — "Cover 0/1/2/3/4/6 + man/zone tendencies" — is unanswerable from public data. The nflverse-distributed FTN subset is 28 columns and contains zero coverage labels. The full Cover-0–6 / man-zone taxonomy is part of FTN's paid product. The project pivots to broader **defensive tendencies** using the available FTN dimensions: `n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`.
```

**Pattern: 2-3 sentence Hook (per CONTEXT.md §Claude's Discretion bullet 3):**

A plain-English Hook that:
1. Names what the project does in numbers-first memo style (e.g., "Three seasons (2022–2024) of NFL play-by-play and FTN charting, asking which defenses are predictable in known situations.").
2. Names the public-FTN pivot honestly — public FTN data exposes broader defensive tendencies (blitz / pressure / play-action / personnel), NOT coverage shells (Cover 0–6, man / zone).
3. Includes 1–2 placeholder slots for headline numbers Phase 4 fills (e.g., `<MOST_PREDICTABLE_DEFENSE>` and `<LEAGUE_BLITZ_RATE_3RD_LONG>`).

**Constraint applies (CLAUDE.md "Locked Stack" + PITFALLS.md Pitfall #13 lines 313-332):** the Hook does NOT use jargon — no "Cover 3", no "shell", no "DVOA" without a glossary gloss. The non-football recruiter must parse it cold.

**Constraint applies (PITFALLS.md Pitfall #20):** the Hook must match the post-AUDIT-06 SPEC rewrite. README and SPEC are reconciled at end of Phase 1, not deferred to ship.

---

### `.planning/PROJECT.md` Key Decisions table (append D-09)

**Analog (in-repo, exact role-match):** `.planning/PROJECT.md` — existing Key Decisions table.

**Pattern (read existing table format at `.planning/PROJECT.md` lines 78-80, then append):**

```markdown
| D-09: Public GitHub repo name | Locked to `nfl-defensive-tendencies` after Phase 1 audit confirmed the public-FTN pivot; `coverage` framing in original repo name no longer accurate. Working folder stays `nfl-coverage-tendencies` for git history continuity. | Locked 2026-04-29 |
```

**Constraint applies (REQUIREMENTS.md AUDIT-05 + CONTEXT.md §D-09):** working folder stays `nfl-coverage-tendencies`. Public GitHub repo name `nfl-defensive-tendencies` is used in Phase 4 / SHIP-03 (GitHub MCP repo creation); it is NOT renamed in Phase 1.

**Constraint applies (CONTEXT.md §canonical_refs):** "If Phase 1 surfaces a decision worth promoting, add it to PROJECT.md Key Decisions, not a new ADR." D-09 is added to the existing table; no new ADR file is created.

---

## Shared Patterns

These cross-cutting patterns apply to multiple Phase 1 files. The planner should reference these from each plan's `read_first` block.

### Shared Pattern 1: Audience voice (every prose file)

**Source:** `CLAUDE.md` §Audience Voice (lines 99-107) and `.planning/research/SUMMARY.md` §Consolidated Feature Priority §P3 Anti-Features (lines 142-156).

**Apply to:** `README.md` (skeleton + AUDIT-07 hook), `docs/ftn-schema-audit.md`, `docs/analysis-plan.md`, `SPEC.md` rewrite, `data/README.md` (if Phase 1 stubs it).

**Voice rules:**

- Memo style, not tutorial style. Reader is a peer.
- No exclamation points. No emoji section headers. No "Welcome to my project!".
- Numbers first inline ("38% on 3rd-and-long, N=247", not "an aggressive blitzing defense").
- State sample size inline with every claim.
- No academic structure (Abstract / Methods / Results / Discussion).
- No "Future work" laundry list.
- No self-deprecating language ("This is just a small project...").
- No betting / DFS framing.

### Shared Pattern 2: Sample-size discipline (every doc that names a number)

**Source:** `CLAUDE.md` §Project Realities to Remember + REQUIREMENTS.md STAT-07 + PITFALLS.md Pitfall #8.

**Apply to:** `docs/analysis-plan.md` hypothesis thresholds, `docs/ftn-schema-audit.md` if any rates are quoted, FINDINGS.md (Phase 4), README findings preview placeholder structure.

**Tiers:**

- **N ≥ 30** for any tendency claim.
- **N ≥ 100** for any "extreme" claim (>75%).
- **N ≥ 15** allowed only with explicit narrative low-N flag.

In Phase 1, this pattern is mostly establishing the documentation convention — the actual `min_n_filter()` helper lives in `analysis/_common.py` (Phase 3 / STAT-01).

### Shared Pattern 3: Public-FTN reality (every doc that names data)

**Source:** `CLAUDE.md` §Project Realities + PITFALLS.md Pitfall #2 + ARCHITECTURE.md Critical Up-Front Findings #2.

**Apply to:** `docs/ftn-schema-audit.md`, `SPEC.md` rewrite, `README.md` Hook rewrite, `docs/analysis-plan.md`.

**Rules:**

- The 28 public FTN columns do NOT include Cover 0–6 / man-zone labels. Never write `WHERE coverage = 'Cover 3'` — the column does not exist.
- The 8 candidate defensive dimensions are: `n_blitzers`, `n_pass_rushers`, `is_play_action`, `is_screen_pass`, `is_rpo`, `qb_location`, `n_offense_backfield`, `starting_hash`.
- FTN↔pbp join keys are `nflverse_game_id` and `nflverse_play_id` — NOT `ftn_game_id` / `game_id` / `play_id`.

### Shared Pattern 4: File-organization discipline

**Source:** `CLAUDE.md` §File-Organization Rules + §Project Structure.

**Apply to:** every file Phase 1 creates.

**Rules:**

- Source code lives in `etl/`, `analysis/`, `schema/`, `queries/`. Never in repo root.
- Notebooks live in `analysis/`. Outputs cleared before commit (`jupyter nbconvert --clear-output --inplace`).
- Documentation lives in `findings/` (Phase 4), `data/` (Phase 4), `docs/` (Phase 1: `ftn-schema-audit.md`, `analysis-plan.md`), and the project root (top-level `README.md`).
- Planning lives in `.planning/`. Do NOT write planning docs anywhere else.
- No `tests/` directory by default. Assertions live inside the ETL.
- Never save scratch / WIP files to repo root. If needed, put in `scratch/` (gitignored).

### Shared Pattern 5: Greenfield reality

**Source:** CONTEXT.md §code_context lines 87-110.

**Apply to:** every Phase 1 file, especially the Bootstrap plan (01-01).

The repo is greenfield except for `.git/`, `.gitignore`, `CLAUDE.md`, `SPEC.md`, `.planning/`, and `venv/`. There are no existing Python coding patterns to mirror — Phase 1 establishes them. The `venv/` exists at repo root; BOOT-07 verifies a fresh-venv install passes (planner should specify whether to reuse the existing venv after confirming Python 3.11 cleanliness, or create `.venv/` fresh).

---

## No Analog Found (greenfield — establishes pattern)

Files with no in-repo analog. Planner should reference the canonical research docs listed below instead of looking for code analogs.

| File | Role | Data Flow | Canonical Reference |
|------|------|-----------|---------------------|
| `requirements.txt` | config | static manifest | `.planning/research/SUMMARY.md` §Consolidated Stack lines 66-91 (verbatim block above) |
| `pyproject.toml` | config | static manifest | `.planning/research/STACK.md` lines 165-175 (verbatim block above) |
| `.python-version` | config | static manifest | literal `3.11\n` — no analog needed |
| `analysis/00_data_audit.ipynb` | notebook | network → DataFrame → CSV | REQUIREMENTS.md AUDIT-01..02 + STACK.md §1 + ARCHITECTURE.md §Pattern 1 + PITFALLS.md #3, #4, #17 |
| `audit/ftn_null_profile.csv` | data artifact | DataFrame → CSV | REQUIREMENTS.md AUDIT-02 + CONTEXT.md §D-01..D-02 |
| `data/raw/.gitkeep` | placeholder | static | none — empty file in a gitignored directory |
| `findings/images/` (empty in Phase 1) | placeholder | static | ARCHITECTURE.md tree lines 147-153; populated in Phase 4 |

**Reason for greenfield:** This is the first phase of a portfolio piece initialized from `/gsd-init`. The repo's Python coding patterns — loader functions, schema files, notebook structure, statistical helpers — are all established in Phases 1–3. Phase 1's audit notebook is the FIRST notebook; the loader pattern it establishes is the analog Phase 2 ETL will copy from.

---

## Metadata

**Analog search scope:**
- `./` (repo root: `.gitignore`, `CLAUDE.md`, `SPEC.md`)
- `.planning/` (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md)
- `.planning/research/` (STACK.md, SUMMARY.md, ARCHITECTURE.md, PITFALLS.md, FEATURES.md)
- `.planning/phases/01-foundation-ftn-pivot-calibration/` (CONTEXT.md, RESEARCH.md if present)

**Files scanned:** 11 (all in `.planning/` + 3 root files).
**In-repo code analogs found:** 0 Python files (greenfield).
**In-repo style/voice analogs found:** 4 (existing `.gitignore`, `SPEC.md`, `CLAUDE.md`, `.planning/PROJECT.md` Key Decisions table).
**Reference-not-analog (canonical research docs):** 5 (`SUMMARY.md` Consolidated Stack, `STACK.md` ruff block, `ARCHITECTURE.md` directory tree, `PITFALLS.md` 22-pitfall register, `REQUIREMENTS.md` BOOT/AUDIT acceptance criteria).

**Pattern extraction date:** 2026-04-29.

---

## PATTERN MAPPING COMPLETE
