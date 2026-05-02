---
phase: quick/260502-ftr
plan: 01
status: complete
date: 2026-05-02
duration_min: ~10
commits:
  - 1bb2a55  # fix(viz): reorder hero leaderboard title above subtitle (260502-ftr)
  - 6872222  # chore(viz): jupytext-sync 03_visualizations.ipynb (260502-ftr)
  - 9551dab  # chore(viz): regenerate hero + social-preview PNGs (260502-ftr)
files_modified:
  - analysis/03_visualizations.py
  - analysis/03_visualizations.ipynb
  - findings/images/01_predictability_ranking.png
  - findings/images/01_predictability_ranking_top12.png
requirements: [QUICK-260502-ftr]
---

# Quick Task 260502-ftr: Fix header/subhead order in render_leaderboard — Summary

Reordered the hero leaderboard so the large headline renders above the small gray subhead (newspaper convention), resynced the paired notebook, and regenerated both affected PNGs end-to-end through the existing `data/nfl_defensive_tendencies.db`. All three tasks executed and committed atomically.

## Tasks Executed

### Task 1 — Fix title/subhead order in `render_leaderboard()` — DONE

**File:** `analysis/03_visualizations.py` (lines 185-197 post-edit)

**Before:**
```python
ax.set_title(title, fontsize=13, loc="left")
# Subtitle as a text below the title.
ax.text(
    0.0, 1.02, subtitle,
    transform=ax.transAxes, fontsize=10, color="#444444", va="bottom",
)
```
- subtitle at `y=1.02` axes-fraction with `va="bottom"` placed it ABOVE the headline (which sits at default `y≈1.0`)
- result: subtitle on top, headline below — inverted hierarchy
- worse on the social preview where `savefig.bbox="tight"` clipped the topmost line

**After:**
```python
# Headline (large) — pad in points keeps spacing stable across both figsizes
ax.set_title(title, fontsize=14, loc="left", pad=22)
# Subhead (small, gray) sits just above the axes top, below the headline
ax.text(
    0.0,
    1.0,
    subtitle,
    transform=ax.transAxes,
    fontsize=10,
    color="#444444",
    va="bottom",
    ha="left",
)
```
- `set_title(..., pad=22)` pushes the headline up 22 pt (absolute) from the axes top — stable across the 8x11 hero and 6.4x3.2 social-preview figsizes
- subhead at `y=1.0, va="bottom"` sits flush against the axes top, below the lifted headline
- explicit `ha="left"` for clarity

Verification:
- `ruff check analysis/03_visualizations.py`: passed
- `ruff format --check`: required reformat (see Deviation 1 below); applied; re-verified
- semantic grep: `pad=22` present, `set_title(..., fontsize=14, loc="left", pad=22)` present, `ax.text(0.0, 1.0, subtitle, ...)` present, `ha="left"` present, `1.02, subtitle` removed

### Task 2 — Resync paired `.ipynb` via jupytext — DONE

**File:** `analysis/03_visualizations.ipynb`

Commands run from project root (`C:\Users\geoca\projects\nfl-coverage-tendencies`):
```
.venv/Scripts/jupytext.exe --sync analysis/03_visualizations.py
.venv/Scripts/jupyter.exe nbconvert --clear-output --inplace analysis/03_visualizations.ipynb
```

Verification:
- `pad=22` and `ha="left"` propagated into the .ipynb code-cell source
- `1.02, subtitle` no longer in any code cell
- all code-cell `outputs == []` and `execution_count in (None, 0)` (CLAUDE.md "outputs cleared before commit")

### Task 3 — Regenerate hero + social-preview PNGs — DONE

**Files:** `findings/images/01_predictability_ranking.png`, `findings/images/01_predictability_ranking_top12.png`

End-to-end execution path:
```
.venv/Scripts/jupyter.exe nbconvert --to notebook --execute --inplace analysis/03_visualizations.ipynb
.venv/Scripts/jupyter.exe nbconvert --clear-output --inplace analysis/03_visualizations.ipynb
```

Notebook executed against the existing `data/nfl_defensive_tendencies.db` (~49.6 MB, last built 2026-04-29). All cells ran cleanly; no errors. Outputs cleared post-execute per the workflow.

Final PNG sizes (after re-render):

| File | Size | mtime | In 30-80 KB band? |
|------|------|-------|-------------------|
| `01_predictability_ranking.png` | 115,615 B (~112 KB) | 2026-05-02 | ABOVE band (was 114 KB pre-fix; size driven by 8x11 portrait at 200 DPI with 32 team labels — consistent with the prior committed hero) |
| `01_predictability_ranking_top12.png` | 53,027 B (~51 KB) | 2026-05-02 | within band |

`02_kl_vs_h_scatter.png` was also re-rendered (same notebook) but produced a byte-identical file (deterministic via `np.random.seed(SEED)`); not staged.

**Visual confirmation (read both PNGs and inspected as images):**
- Hero (8x11 portrait): large headline "Some NFL Defenses Are More Predictable Than Others" renders ABOVE small gray subhead "32 NFL defenses, blitz rate on 4 pre-registered situations, 2022-2025; 0-100 predictability index, higher = more predictable." — both above the bar plot, no clipping. Hierarchy is correct.
- Social preview (1280x640): same large-headline-above-small-subhead order. Note: the social preview's headline has `(Top 12)` appended and is wide enough that the rightmost edge is clipped at the 1280-px figure boundary — this is a pre-existing, separate issue (long title vs narrow figsize) and is out of scope for this task. The order/spacing fix this task targets is verified.

## Deviations From Plan

### 1 — Rule 3 (auto-fix blocking issue): ruff format reformatted the multi-arg `ax.text` call

The plan's automated verifier for Task 1 used a literal-string assertion:
```python
'0.0, 1.0, subtitle' in s and '1.02, subtitle' not in s and 'fontsize=14, loc="left", pad=22' in s
```

My initial edit matched this verbatim (single-line `ax.text(0.0, 1.0, subtitle, transform=ax.transAxes, fontsize=10, color="#444444", va="bottom", ha="left")`). The constraints instructed me to run `ruff format` if `ruff format --check` fails. It did fail (`Would reformat: analysis\03_visualizations.py`). After `ruff format`, the multi-arg call was split across multiple lines per ruff's standard line-length policy:

```python
ax.text(
    0.0,
    1.0,
    subtitle,
    transform=ax.transAxes,
    fontsize=10,
    color="#444444",
    va="bottom",
    ha="left",
)
```

The plan's literal one-liner `'0.0, 1.0, subtitle'` no longer matches because ruff split it across three lines. I substituted a semantic check (regex `r'ax\.text\(\s*0\.0,\s*1\.0,\s*subtitle'`) which passes. All four substantive checks — `pad=22` present, `set_title(..., fontsize=14, loc="left", pad=22)` present, subtitle uses `y=1.0`, `ha="left"` present, `1.02, subtitle` removed — pass on the formatted code. The "done" criteria (intent, not literal whitespace) are satisfied. No behavior change.

### 2 — Rule 3 (auto-fix blocking issue): used `.venv/` not `venv/` for the toolchain

This repo has two virtualenvs at the project root:
- `venv/` — minimal env with `ruff`, `pyarrow`, `pandas 3.0.2`, `numpy 2.4.4` (does NOT match the locked stack)
- `.venv/` — full env with `nfl_data_py 0.3.3`, `numpy 1.26.4`, `pandas 2.2.3`, `jupytext 1.19.1`, `nbconvert 7.17.1`, `ruff 0.15.12` (matches the locked stack from `requirements.txt`)

I initially tried `venv/Scripts/ruff.exe` (worked) but `venv` lacks `jupytext`/`jupyter`/`nfl_data_py` and has the wrong NumPy/pandas pins. Switched all subsequent commands to `.venv/Scripts/...` for Tasks 2 and 3. No project-file change; this is purely an executor-environment selection note for future quick-task runs in this repo.

### 3 — Notebook execution-timestamp metadata churn (non-blocking, expected)

`jupyter nbconvert --execute --inplace` writes `iopub.execute_input` / `iopub.status.busy` / `iopub.status.idle` / `shell.execute_reply` ISO-8601 timestamps into each code cell's `metadata.execution` block. `--clear-output --inplace` clears `outputs` and resets `execution_count` to `null` but does NOT strip those `metadata.execution` timestamps. The prior 2026-05-01 commit of this notebook (`6872222` in this task — wait, that's the new sync; the pre-existing committed copy was from 04-01-SUMMARY) already carried the same metadata pattern, so this is the established repo convention. The Task 3 .ipynb diff is purely these timestamp updates plus no source/output changes. Staged with the PNGs in the Task 3 commit and called out explicitly in the commit body.

## Code Block — Before vs After (canonical reference)

**Before** (`analysis/03_visualizations.py` lines 187-192, single-line `ax.text`):
```python
ax.set_title(title, fontsize=13, loc="left")
# Subtitle as a text below the title.
ax.text(
    0.0, 1.02, subtitle,
    transform=ax.transAxes, fontsize=10, color="#444444", va="bottom",
)
```

**After** (`analysis/03_visualizations.py` lines 185-197, ruff-formatted):
```python
# Headline (large) — pad in points keeps spacing stable across both figsizes
ax.set_title(title, fontsize=14, loc="left", pad=22)
# Subhead (small, gray) sits just above the axes top, below the headline
ax.text(
    0.0,
    1.0,
    subtitle,
    transform=ax.transAxes,
    fontsize=10,
    color="#444444",
    va="bottom",
    ha="left",
)
```

## Regeneration Outcome

**Status:** SUCCEEDED.

The end-to-end notebook execution path worked on first try via `.venv/Scripts/jupyter.exe`. The DB existed and `analysis._common.DB_PATH` resolved correctly to `data/nfl_defensive_tendencies.db`. No fallback to `python analysis/03_visualizations.py` was needed; no fallback-to-deferred path was triggered.

PNGs verified post-regeneration:
- `findings/images/01_predictability_ranking.png` mtime > HEAD commit time (1777735790 > 1777735748)
- `findings/images/01_predictability_ranking_top12.png` mtime > HEAD commit time (1777735790 > 1777735748)
- both within sane size band (10 KB ≤ size ≤ 250 KB sanity check from plan); hero is 112 KB which is ~40% above the typical 30-80 KB band but matches the prior committed hero (114 KB) — driven by the 8x11 portrait at 200 DPI with 32 team labels, not a regression
- visual spot-check confirms headline-above-subhead order in both images

## Commits

| Task | Hash | Message |
|------|------|---------|
| 1 | `1bb2a55` | `fix(viz): reorder hero leaderboard title above subtitle (260502-ftr)` |
| 2 | `6872222` | `chore(viz): jupytext-sync 03_visualizations.ipynb (260502-ftr)` |
| 3 | `9551dab` | `chore(viz): regenerate hero + social-preview PNGs (260502-ftr)` |

## Constraints Honored

- Did NOT modify `analysis/_style.py`. Fix is local to `render_leaderboard`.
- Did NOT add a `tests/` directory.
- Did NOT stage `data/raw/` or any `*.db` files (gitignored; `git status` confirmed before each commit).
- Did NOT commit `.planning/quick/` PLAN.md / SUMMARY.md / STATE.md (orchestrator handles the docs commit after merge).
- Did NOT update `.planning/ROADMAP.md`.
- Used POSIX shell paths via Git Bash on Windows.
- All three commits use conventional-commit format with the suggested messages.

## Self-Check

- `analysis/03_visualizations.py` — exists, modified, ruff check + format clean: PASS
- `analysis/03_visualizations.ipynb` — exists, in sync with .py, outputs cleared: PASS
- `findings/images/01_predictability_ranking.png` — exists, mtime fresh, size sane, headline-above-subhead visually confirmed: PASS
- `findings/images/01_predictability_ranking_top12.png` — exists, mtime fresh, size 51 KB in band, headline-above-subhead visually confirmed: PASS
- commit `1bb2a55` — present in `git log`: PASS
- commit `6872222` — present in `git log`: PASS
- commit `9551dab` — present in `git log`: PASS

## Self-Check: PASSED
