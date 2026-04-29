# Stack Research

**Domain:** Python data-analytics portfolio (NFL coverage / defensive tendency analysis with `nfl_data_py` FTN + nflfastR PBP, SQLite, Jupyter)
**Researched:** 2026-04-29
**Confidence:** HIGH on version intel and ecosystem state; MEDIUM on FTN column shape (Phase 1 audit owns final answer)

---

## TL;DR — The One Thing You Need to Know

**`nfl_data_py` was archived on 2025-09-25. The upstream README explicitly says "users are encouraged to switch immediately" to `nflreadpy`.** [VERIFIED: github.com/nflverse/nfl_data_py README, Sep 25 2025]

The SPEC pins `nfl_data_py`, but the SPEC was written before that archival was widely visible in this repo's planning context. This is a stack-risk decision the project owner needs to make explicitly:

| Path | What you get | What it costs |
|------|--------------|---------------|
| **A. Stick with `nfl_data_py==0.3.3`** (SPEC literal) | API matches the SPEC exactly; one package; everything still functions today | Pinning to an archived, unmaintained library; well-known NumPy 2.0 / pandas-version landmines; recruiter can argue "you picked a deprecated dep" |
| **B. Switch to `nflreadpy`** (de-facto current) | Maintained successor, modern Polars-first design, official nflverse blessing | API differs: `load_pbp()` / `load_ftn_charting()` instead of `import_pbp_data()` / `import_ftn_data()`; default return type is Polars; small Python ≥3.10 bump (already satisfied) |

**Recommendation:** Path B (`nflreadpy`). The whole point of the project is recruiter signal, and "library archived 7 months before you cloned the repo" is exactly the kind of detail a sharp reviewer will flag. The API delta is two-line wrapper functions in your ETL layer. This is the highest-leverage decision in the stack and should be raised back to the SPEC owner before Phase 1 begins.

The remainder of this document gives a full version-pinned stack for **both paths**, with Path B as the recommended default.

---

## Architectural Responsibility Map

| Capability | Primary owner | Secondary | Rationale |
|------------|---------------|-----------|-----------|
| Raw data fetch (FTN, PBP) | `nflreadpy` (or `nfl_data_py`) | local parquet cache | Single canonical source; cache makes recruiter clone-and-run reproducible without network on second run |
| Frame manipulation / transforms | `pandas` | `numpy` (vectorized math) | `pandas` is the lingua franca recruiters expect; Polars adds skill-signal cost without project payoff |
| Persistence | `sqlite3` (stdlib) | `pandas.to_sql` for bulk loads | Stdlib for queries (transparent SQL the recruiter can read); `to_sql` only for the bulk PBP-and-FTN dump |
| SQL analyses | raw `.sql` files run via `sqlite3` CLI / Python | — | Analyses are the deliverable — keep them as flat files, not embedded strings |
| Statistical tests | `scipy.stats` | `numpy` | Chi-square + Shannon entropy are both 1-line `scipy` calls |
| Static charts | `matplotlib` + `seaborn` | `plotly` (interactive only) | SPEC pinned; PNG export drives FINDINGS.md |
| Notebook authoring | `jupyterlab` | `jupytext` (paired .py for clean git diffs) | Lab is the modern default; jupytext is the recruiter-signal multiplier |
| Notebook → static export | `nbconvert` | — | Used to render notebook PNGs / HTML at publish time |

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | `>=3.11,<3.13` | Runtime | SPEC-pinned 3.11+. Cap at <3.13 because some scientific stack wheels still flap on 3.13 in mid-2025 (`nfl_data_py` had an open install issue on 3.13 before archival); 3.11 and 3.12 are the safest recruiter-laptop targets. [VERIFIED: github.com/nflverse/nfl_data_py issue #122] |
| **`nflreadpy`** (Path B, recommended) | `==0.1.5` | NFL data loader (FTN + PBP) | Maintained successor to `nfl_data_py`; same nflverse data backbone; released 2025-11-19. Returns Polars DataFrames — call `.to_pandas()` once at the boundary and the rest of the project is pure pandas. [VERIFIED: pypi.org/project/nflreadpy v0.1.5; github.com/nflverse/nflreadpy] |
| **`nfl_data_py`** (Path A, SPEC-literal) | `==0.3.3` | NFL data loader (FTN + PBP) | Archived 2025-09-25 but functional. Use only if the SPEC owner consciously chooses to ignore the deprecation. [VERIFIED: pypi.org/project/nfl-data-py v0.3.3 released 2024-09-20; archive notice in README] |
| **`pandas`** | `>=2.2,<2.4` | Tabular analysis | **Pin away from 3.0.** pandas 3.0.0 shipped 2026-01-21 with breaking string-dtype and copy-on-write behavior changes. The 2.3.x line is the last "safe" major before 3.0. 2.2.x is the most-tested band against `nfl_data_py`/`nflreadpy`. [VERIFIED: pandas.pydata.org/community/blog/pandas-3.0.html; pandas 3.0.2 latest as of 2026-04] |
| **`numpy`** | `>=1.26,<2.3` | Numerics under pandas | NumPy 2.0 broke `np.float_` which `nfl_data_py` 0.3.x depends on (issue #98). `nflreadpy` is fine on 2.x. Cap at <2.3 for cross-OS wheel availability on a recruiter laptop. [VERIFIED: github.com/nflverse/nfl_data_py issue #98] |
| **`pyarrow`** | `>=15,<22` | Parquet I/O backbone | Both nflverse loaders fetch parquet files. pandas 3.0 will eventually require pyarrow as a hard dep; pinning ≥15 satisfies all current loaders. Latest 24.0.0 (Apr 2026). [VERIFIED: pypi.org/project/pyarrow] |
| **`sqlite3`** | stdlib (3.11+) | Persistence + query layer | Stdlib — no install, no version pin. Python 3.11 ships SQLite 3.40+ which is plenty for window functions and CTEs. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **`matplotlib`** | `>=3.8,<3.11` | Static charts | The 3.8/3.9/3.10 line is the seaborn-compatible band. Latest is 3.10.9. Pinning a range gives the recruiter a wheel that exists for their Python. [VERIFIED: pypi.org/project/matplotlib] |
| **`seaborn`** | `==0.13.2` | Statistical plotting | Seaborn 0.13.2 is the only release of the 0.13.x line and has been stable since 2024-01-25. Pin exact — no harm in it, and it removes a class of "why does my chart look different" issues for the recruiter. [VERIFIED: pypi.org/project/seaborn] |
| **`scipy`** | `>=1.13,<1.18` | `chi2_contingency`, `entropy` | scipy.stats provides both required statistical primitives in one import. No need for `statsmodels` — it would be over-tooling. Latest 1.17.1. [VERIFIED: pypi.org/project/scipy] |
| **`jupyterlab`** | `>=4.2,<4.6` | Notebook IDE | The 4.x line; 4.5.7 is current. **Use `jupyterlab`, not bare `notebook` and not `jupyter` meta-package** — Lab is the de-facto default for new projects in 2025+, recruiters know it. [VERIFIED: pypi.org/project/jupyterlab] |
| **`ipykernel`** | `>=6.29,<8` | Kernel for JupyterLab | Required transitively; pinning the line keeps `pip install` quiet. ipykernel 7.x just released; 6.29 is the long-tail stable. [VERIFIED: pypi.org/project/ipykernel] |
| **`jupytext`** | `>=1.16,<2` | Paired-py notebook representation | Stores notebooks as `.ipynb` AND a stripped `.py` for clean git diffs. **This is the single highest recruiter-signal item in the dev stack** — clicking through a clean PR diff of a notebook tells a recruiter you've actually shipped data work before. [VERIFIED: pypi.org/project/jupytext v1.19.1 latest] |
| **`nbconvert`** | `>=7.16,<8` | Notebook → HTML / PNG export | Used at publish time to render the FINDINGS.md image dump. Stdlib-adjacent; usually pulls in via JupyterLab. [VERIFIED: pypi.org/project/nbconvert v7.17.1 latest] |
| **`plotly`** | `>=5.20,<7` *(optional)* | Interactive in-notebook charts | Install only if a chart genuinely needs hover. SPEC says "static charts everywhere except in-notebook interactivity." Plotly 6.x is the current major. [VERIFIED: pypi.org/project/plotly v6.7.0 latest] |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **`ruff`** | Lint + format in one binary | Use it. Even on a "small data project" it costs zero — `ruff check` and `ruff format` are sub-second. The configuration shown below is deliberately minimal so it doesn't become portfolio noise. [VERIFIED: pypi.org/project/ruff v0.15.12 latest] |
| **`pip-tools`** *(optional)* | Compile pinned `requirements.txt` from a hand-edited `requirements.in` | Worth it once for the published `requirements.txt`. Keeps the recruiter-facing pin file fully reproducible while you keep the human-readable `.in` file. |
| **`pre-commit`** *(optional, defer)* | Run ruff on commit | Skip for v1. Adds a clone-time install step that contradicts the "5-command setup" reproducibility budget. |

---

## Detailed Question Answers

### 1. `nfl_data_py` itself — current state

- **Latest version:** `0.3.3`, released `2024-09-20`. [VERIFIED: PyPI]
- **Repo status:** **ARCHIVED 2025-09-25** by nflverse maintainers. README explicitly states "users are encouraged to switch immediately" to `nflreadpy`. [VERIFIED: github.com/nflverse/nfl_data_py]
- **Known landmines:**
  - **NumPy 2.0 incompatibility** — `np.float_` was removed in NumPy 2; `nfl_data_py` 0.3.x still references it. Workaround is `numpy<2`. **Will never be patched** (archived). [VERIFIED: nfl_data_py issue #98]
  - **Python 3.13 install fails** (issue #122 still open at archive time). Cap at 3.12.
  - Older pandas-`.append` deprecation was fixed in 0.2.8, so 0.3.3 is fine on pandas 2.x.
- **`import_ftn_data(years)` actual exposure (2022–2024):** [CITED: nflreadr.nflverse.com/reference/load_ftn_charting.html]
  - Visible columns: `ftn_game_id, nflverse_game_id, season, week, ftn_play_id, nflverse_play_id, starting_hash, qb_location, n_offense_backfield, n_defense_box, is_no_huddle, is_motion, is_play_action, is_screen_pass, is_rpo, is_trick_play, is_qb_out_of_pocket, is_interception_worthy, is_throw_away, read_thrown, is_catchable_ball, is_contested_ball` + 23 more.
  - **The defensive-coverage labels (Cover 0/1/2/3/4/6, man/zone) appear NOT to be in `load_ftn_charting`.** The `defense_man_zone_type` and `defense_coverage_type` fields live in `load_participation()`, which is NFL-NGS data, not FTN. [VERIFIED: nflreadpy docs + multiple search hits]
  - This means **the project's Phase 1 audit will likely confirm the pivot path** (the project becomes "defensive tendencies" — blitz rate, pass-rusher count, defenders in box, play-action response — not "Cover 0–6 distribution"). The pivot is already documented in `.planning/PROJECT.md` as the preferred response.
  - **Do not write the data dictionary into roadmap tasks based on these column lists alone.** Phase 1 must `head()` the actual frame and freeze the schema in `data/raw/`.
- **Pinning recommendation if Path A:** `nfl_data_py==0.3.3` *exact* (no upper bound game — there will never be a 0.3.4). Combine with `numpy>=1.26,<2.0` and `pandas>=2.0,<2.3`. Confidence: HIGH.

### 2. pandas / numpy

- **pandas 3.0 dropped 2026-01-21 with breaking changes:** new default string dtype (was object), Copy-on-Write made permanent, several `to_numpy()` semantic shifts when NA values are present. [VERIFIED: pandas.pydata.org/community/blog/pandas-3.0.html]
- **For a portfolio project that must run on a recruiter laptop today:** pin pandas to the 2.3.x line (`>=2.2,<2.4`). 2.3 emits the deprecation warnings 3.0 turned into errors, which is also a useful skill signal if a recruiter pokes around.
- **NumPy:** `>=1.26,<2.3`. Path A forces `numpy<2.0`; Path B can take `numpy>=2.0` happily.
- **Path B (nflreadpy) note:** nflreadpy is Polars-first. You can either (a) keep Polars internally and pivot the project's pandas signal to Polars (NOT recommended — recruiters skim for `import pandas as pd`), or (b) call `.to_pandas()` once in your loader wrapper and treat nflreadpy as a pure data-source layer. **Recommendation: (b)**. One conversion call at the ETL boundary. The skill signal stays pandas. Confidence: HIGH.

### 3. SQLite tooling in Python

For a portfolio project where readability beats performance:

- **`sqlite3` stdlib for queries** — recruiter opens `etl/load_pbp.py`, sees `conn = sqlite3.connect(...)`, instantly grasps it. No magic.
- **`pandas.to_sql(con=conn, if_exists='replace', method='multi', chunksize=5000)` for bulk inserts** — ~270 games × 32 teams × 3 seasons of plays is ~50k–150k rows; chunked `to_sql` handles it in single-digit seconds and is one line.
- **`sqlalchemy`: skip.** It's not needed and adds ~3 imports of "why is this here" for the recruiter. Pandas itself supports `to_sql` via a raw `sqlite3` connection (with a known FutureWarning on non-SQLAlchemy connections in pandas 2.x — silenceable, harmless, will be a deprecation in pandas 3.0; another reason to pin to 2.3.x). [CITED: pandas docs `to_sql`]
- **One exception:** if you decide to write integration tests that verify schema, `sqlalchemy.inspect()` is genuinely cleaner than raw `PRAGMA table_info`. Decide at Phase 2.

Confidence: HIGH.

### 4. Jupyter

- **Use `jupyterlab` (the IDE), not the meta-package `jupyter`, not the legacy `notebook`.** Lab 4.x is the modern default; classic `notebook` is in maintenance mode behind the `nbclassic` shim. [VERIFIED: jupyter.org docs]
- **`jupytext` is worth installing.** Configure paired notebook ↔ `.py` representations and *commit only the `.py`*; the `.ipynb` regenerates locally. This gives you (a) clean PR diffs in the public repo, (b) the ability to run notebooks via `pytest --nbmake` later if you grow into it, and (c) a strong "this person has shipped data work before" signal in the GitHub diff history. Configure via a top-level `jupytext.toml` or per-notebook frontmatter.
- **`nbconvert` is the export tool** for the FINDINGS.md PNG flow. JupyterLab pulls it in transitively. You'll invoke it as `jupyter nbconvert --to html` or `--execute --to notebook` in CI / a publish script.

Confidence: HIGH.

### 5. Static charts — pairing + portfolio polish

- **`matplotlib>=3.8,<3.11` + `seaborn==0.13.2`.** This is the documented compatibility band; seaborn 0.13.2 was released 2024-01-25 and explicitly supports the matplotlib 3.7–3.10 line. [VERIFIED: pypi.org/project/seaborn]
- **Style configuration for portfolio polish** (drop into a `styles/portfolio.mplstyle` or a notebook setup cell):
  ```python
  import matplotlib.pyplot as plt
  import seaborn as sns
  sns.set_theme(style="whitegrid", context="notebook", palette="muted")
  plt.rcParams.update({
      "figure.dpi": 110,
      "savefig.dpi": 200,           # crisp PNGs in FINDINGS.md
      "figure.figsize": (8, 4.5),
      "axes.titlesize": 13,
      "axes.titleweight": "semibold",
      "axes.spines.top": False,
      "axes.spines.right": False,
      "font.family": "DejaVu Sans", # cross-platform safe; available on a recruiter laptop
  })
  ```
  Save inline charts as `findings/images/<question_id>_<short_slug>.png`. Confidence: HIGH on the version pairing, MEDIUM on the exact rc settings (taste-driven; defensible defaults).

### 6. Statistical — what to import

- **`scipy.stats.chi2_contingency`** — direct chi-square for "is this team's coverage distribution different from league baseline." One-call.
- **`scipy.stats.entropy`** — Shannon entropy for the predictability score. Pass it a probability vector; specify `base=2` for bits or default `base=e` for nats. **Do NOT hand-roll** — `scipy.stats.entropy` handles zero-probability cells correctly (treats `0 log 0` as 0), which a hand-rolled version routinely gets wrong.
- **`statsmodels`: skip.** Nothing in the SPEC requires regression diagnostics, GLM, or time-series modeling. Adding it for v1 is over-tooling. Reach for it only if a stretch goal demands it.

Confidence: HIGH.

### 7. `requirements.txt` vs `pyproject.toml`

For "recruiter clone-and-run experience," **`requirements.txt` wins for v1.** Specifically a `pip-tools`-compiled `requirements.txt` pinned to exact versions. Reasoning:

- Recruiter-laptop muscle memory is `pip install -r requirements.txt`. They've done it 200 times.
- `pyproject.toml` requires the recruiter to know your build backend (`hatch`? `setuptools`? `poetry`?) and know to run `pip install -e .` or equivalent. That's friction.
- `pyproject.toml` *signals more rigor* in a backend / library project. For an analysis project, the convention is `requirements.txt`, and breaking convention costs more than it gains.
- **Compromise (recommended):** ship a `requirements.txt` (the recruiter-facing artifact) AND a tiny `pyproject.toml` that contains only `[tool.ruff]` configuration. This gives you the linter config in its canonical location without making `pyproject.toml` the install manifest.

Confidence: HIGH.

### 8. Linting / formatting — `ruff`?

**Yes, ship with ruff. No, don't make it a portfolio centerpiece.** A minimal `pyproject.toml` block:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]   # pycodestyle, pyflakes, isort, bugbear, pyupgrade
ignore = ["E501"]                      # let line-length do that work; long URL strings are fine
```

Why this rule set:
- `E`/`F` — baseline correctness.
- `I` — import sorting; clean import blocks are a real recruiter signal in notebooks.
- `B` — flags actual bugs, not style.
- `UP` — pyupgrade nudges; keeps Python 3.11+ idioms consistent.

**Skip `ruff format` enforcement in CI** — this is a solo portfolio repo, not a team codebase. Run it locally before commits. Confidence: MEDIUM (taste call; the case for "no linter at all" is real for a solo data project — but ruff is so cheap it's a free skill signal).

---

## Installation — Recommended (Path B)

```bash
python -m pip install -r requirements.txt
```

Where `requirements.txt` is:

```text
# Data sources
nflreadpy==0.1.5

# Numerical / data
pandas>=2.2,<2.4
numpy>=1.26,<2.3
pyarrow>=15,<22
scipy>=1.13,<1.18

# Visualization
matplotlib>=3.8,<3.11
seaborn==0.13.2
plotly>=5.20,<7              # optional; remove if no interactive notebook charts ship

# Notebooks
jupyterlab>=4.2,<4.6
ipykernel>=6.29,<8
jupytext>=1.16,<2
nbconvert>=7.16,<8

# Dev (optional — could move to a separate requirements-dev.txt)
ruff>=0.6,<1.0
```

## Installation — Path A (SPEC-literal, NOT recommended)

```text
nfl_data_py==0.3.3
pandas>=2.0,<2.3
numpy>=1.26,<2.0          # forced — nfl_data_py uses np.float_ which NumPy 2.0 removed
pyarrow>=15,<22
scipy>=1.13,<1.18
matplotlib>=3.8,<3.11
seaborn==0.13.2
jupyterlab>=4.2,<4.6
ipykernel>=6.29,<8
jupytext>=1.16,<2
nbconvert>=7.16,<8
ruff>=0.6,<1.0
```

The Path A pin file requires a `numpy<2.0` cap that will look strange to a recruiter. Be ready to defend it as "data-source library compatibility, archived upstream" or accept Path B.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **`nflreadpy`** | `nfl_data_py` | Only if the SPEC owner explicitly chooses to ignore the upstream archival — then accept the NumPy 2.0 / Python 3.13 baggage and pin tighter |
| **pandas** | **Polars** (nflreadpy native) | If the project rebrands as a "modern Python data stack" piece. Costs the pandas skill signal. Probably the *correct* call for a project starting from scratch in 2026, but works against this SPEC's stated audience expectation. |
| **SQLite** | DuckDB | If the analysis grows into >1M plays and tracking-data joins. SPEC explicitly forbids; do not relitigate. |
| **`pandas.to_sql` + raw sqlite3** | SQLAlchemy Core | If the project grows test infrastructure that needs reflection. v1 doesn't. |
| **matplotlib + seaborn** | Plotly-only | If the deliverable were a hosted dashboard. SPEC forbids. |
| **`requirements.txt`** | `pyproject.toml` + `pip install .` | If shipping a reusable library. This is an analysis repo. |
| **`scipy.stats.entropy`** | hand-rolled `-sum(p * log(p))` | Never. Hand-rolled fails on zero-probability cells unless guarded; scipy already guards. |
| **`ruff`** | `black + flake8 + isort` | Never in 2025+. Three tools for what ruff does in one binary. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Streamlit / Dash / FastAPI / any web layer** | SPEC explicitly forbids; deployment surface area without recruiter signal | Static notebooks + FINDINGS.md PNG export |
| **Docker / docker-compose** | SPEC explicitly forbids; violates the "stock laptop, single `pip install`" reproducibility budget | Plain venv + `requirements.txt` |
| **Postgres / DuckDB / cloud DB** | SPEC explicitly forbids; SQLite is the right answer for this scale | `sqlite3` stdlib |
| **Polars as the primary frame library** (despite nflreadpy native) | Costs the pandas skill signal recruiters expect | `.to_pandas()` at the loader boundary |
| **`statsmodels`** | Over-tooling for chi-square + entropy; adds ~30MB install | `scipy.stats` |
| **`pandas` 3.x** (until project ships) | Released 2026-01-21 with breaking string-dtype + CoW changes; `nfl_data_py`/`nflreadpy` ecosystems haven't fully validated | `pandas>=2.2,<2.4` |
| **`numpy` 2.0+** with Path A | `nfl_data_py` 0.3.x uses removed `np.float_` | `numpy<2.0` if Path A; otherwise `numpy>=1.26,<2.3` |
| **`black` + `flake8` + `isort` separately** | Three tools, three configs, three pre-commit hooks for what `ruff` does alone | `ruff` |
| **`notebook` package (legacy classic)** | In maintenance behind the `nbclassic` shim | `jupyterlab` |
| **`jupyter` meta-package** | Pulls in everything; ambiguous to a recruiter (which Jupyter exactly?) | `jupyterlab` + explicit `ipykernel` + `jupytext` + `nbconvert` |
| **`pre-commit` framework for v1** | Adds a clone-time `pre-commit install` step; violates the 5-command setup budget | Run `ruff check` manually before commits; reconsider for v2 |
| **Kaggle-CLI / Big Data Bowl tracking data** | SPEC explicitly forbids | `nflreadpy` / `nfl_data_py` only |

---

## Stack Patterns by Variant

**If Phase 1 FTN audit confirms Cover 0–6 columns are in `load_ftn_charting()`:**
- Project ships under the working name `nfl-coverage-tendencies`.
- The Cover 0–6 distribution analyses become the centerpiece of FINDINGS.md.
- No stack changes from this document.

**If Phase 1 audit confirms (as evidence currently suggests) FTN charting only exposes blitz/pressure/play-action/box-count, and `load_participation()` would be needed for true coverage labels:**
- Project pivots to "NFL Defensive Tendency Analysis" — same skills, broader scheme dimensions.
- Optionally add `nflreadpy.load_participation()` for the 2016–2024 NGS-era coverage labels (this is NGS, not FTN — different licensing footnote in README, but freely available via nflverse).
- No package additions; same `nflreadpy` call.

**If pandas 3.0 ecosystem stabilizes before ship (unlikely in this window):**
- Bump pin to `pandas>=2.3,<3.1` and re-run the analyses.

**If the recruiter audience pivots toward "modern Python" signal (e.g., applying to a place that explicitly uses Polars):**
- Drop pandas. Use Polars throughout. nflreadpy already returns Polars natively. Document the choice in README.

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `nflreadpy==0.1.5` | `python>=3.10`, `polars>=1.0`, `pandas` (optional extra) | Polars is the native return type; `pandas` extra optional. Works on `numpy>=2.0`. |
| `nfl_data_py==0.3.3` | `python<3.13`, `numpy<2.0`, `pandas<2.3` (untested above) | Archived; will not be patched. |
| `pandas==2.3.x` | `numpy>=1.26`, `pyarrow>=10`, `python>=3.10` | Last 2.x line; emits 3.0 deprecation warnings. |
| `pandas==3.0.x` | `pyarrow` becomes a hard dep; new string dtype default | Avoid for this project until ecosystem validates. |
| `seaborn==0.13.2` | `matplotlib>=3.4,<3.11`, `pandas>=1.2`, `numpy>=1.20`, `python>=3.8` | Stable; no upper bound surprises in this project's pin range. |
| `scipy==1.17.x` | `numpy>=1.25,<2.5`, `python>=3.11` | `chi2_contingency` and `entropy` APIs unchanged since 1.6+. |
| `matplotlib==3.10.x` | `numpy>=1.23`, `python>=3.10` | Pairs cleanly with seaborn 0.13.2. |
| `jupyterlab==4.5.x` | `python>=3.9`, `ipykernel>=6.5` | Lab 4.x line; jupytext 1.16+ has Lab 4 extension. |

---

## Phase 1 Audit Tasks (handed off to roadmap)

The following questions MUST be resolved by Phase 1 before ETL design — this STACK research deliberately did not pretend to know the answers:

1. **Run `nflreadpy.load_ftn_charting(seasons=[2022, 2023, 2024]).columns` — freeze the actual column list.** Specifically confirm whether any field carries Cover 0/1/2/3/4/6 or man/zone classification.
2. If absent, **run `nflreadpy.load_participation(seasons=[2022, 2023, 2024])`** and confirm `defense_man_zone_type` and `defense_coverage_type` exist for those seasons (the data may stop at 2023 — NGS coverage data has had availability gaps).
3. **Validate `nflreadpy` actually fetches in <60s on first call and caches to disk** (confirms the "5 commands, 10 minutes" reproducibility budget).
4. **Run `pip install -r requirements.txt` from a fresh venv on the target Python (3.11.x or 3.12.x)** and confirm zero errors. Both Path A and Path B should be tried before final commit.
5. **Decide Path A vs Path B explicitly, with the SPEC owner.** This stack research does not have authority to make that call unilaterally; it can only flag it.

---

## Sources

### Primary (HIGH confidence)
- **[PyPI: nfl-data-py](https://pypi.org/project/nfl-data-py/)** — version 0.3.3 confirmed, release date 2024-09-20.
- **[GitHub: nflverse/nfl_data_py](https://github.com/nflverse/nfl_data_py)** — archived status confirmed (Sep 25, 2025), README deprecation notice.
- **[PyPI: nflreadpy](https://pypi.org/project/nflreadpy/)** — version 0.1.5 confirmed, released 2025-11-19, Polars default.
- **[GitHub: nflverse/nflreadpy](https://github.com/nflverse/nflreadpy)** — successor package confirmed, function inventory.
- **[nflreadr docs: load_ftn_charting](https://nflreadr.nflverse.com/reference/load_ftn_charting.html)** — partial column list verified; coverage-label absence inferred from visible column set.
- **[nflreadpy docs: Load Functions](https://nflreadpy.nflverse.com/api/load_functions/)** — `load_participation` function existence confirmed.
- **[pandas: 3.0 release blog](https://pandas.pydata.org/community/blog/pandas-3.0.html)** — pandas 3.0.0 release date (2026-01-21) and breaking changes.
- **[pandas: 3.0 whatsnew](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html)** — string dtype + CoW + `to_numpy()` semantic changes.
- **PyPI version queries via `pip index versions`** — exact-version verification for all packages in the recommended stack (run 2026-04-29).

### Secondary (MEDIUM confidence)
- **[GitHub issue: nfl_data_py #98](https://github.com/nflverse/nfl_data_py/issues/98)** — `np.float_` / NumPy 2.0 incompatibility, status confirmed unfixed at archival.
- **[GitHub issue: nfl_data_py #122](https://github.com/nflverse/nfl_data_py/issues/122)** — Python 3.13 install failure.
- **[Substack: Optimizing NFL Predictive Models](https://arielcalista.substack.com/p/optimizing-nfl-predictive-models-b72)** — third-party validation that `defense_man_zone_type` and `defense_coverage_type` live in participation data, not FTN charting.

### Tertiary (LOW confidence — flagged for Phase 1 verification)
- The exact column name list for `load_ftn_charting()` was only partially visible in nflreadr docs ("23 more variables" not enumerated). Phase 1 must `df.columns.tolist()` against a live fetch.
- The exact pandas-3.0 incompatibility surface in `nflreadpy` is currently unverified — nflreadpy released *before* pandas 3.0 GA. Pin to `pandas<2.4` and revisit at v2.

---

*Stack research for: NFL coverage / defensive tendency analysis (Python + SQLite + Jupyter portfolio project)*
*Researched: 2026-04-29*
*Valid until: ~2026-07-29 (90 days, given pandas 3.0 ecosystem still settling and nflreadpy at v0.1.x — re-verify before any Phase 1 ETL work begins)*
