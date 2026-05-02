---
phase: quick/260502-g4w
plan: 01
status: complete
date: 2026-05-02
duration_min: ~6
commits:
  - 93e6952  # fix(viz): reserve headroom for league-avg label above top bar (260502-g4w)
  - 4eef3ff  # chore(viz): jupytext-sync 03_visualizations.ipynb (260502-g4w)
  - d6c17eb  # chore(viz): regenerate hero + social-preview PNGs (260502-g4w)
files_modified:
  - analysis/03_visualizations.py
  - analysis/03_visualizations.ipynb
  - findings/images/01_predictability_ranking.png
  - findings/images/01_predictability_ranking_top12.png
requirements: [QUICK-260502-g4w]
---

# Quick Task 260502-g4w: Fix league-avg label spacing on findings images — Summary

Reserved a 1-unit headroom band above the top bar in `render_leaderboard()` and re-anchored the "League avg = X.X" label inside that band, so it no longer overlaps the PHI top bar in either the 8x11 hero or the 1280x640 social preview. Synced the paired notebook, regenerated both PNGs end-to-end against the existing local DB, cleared notebook outputs. All three tasks executed and committed atomically.

## Tasks Executed

### Task 1 — Reserve headroom + re-anchor league-avg label — DONE

**File:** `analysis/03_visualizations.py` (lines 199–211 post-format)

**Before** (lines 199–209):
```python
# League-average dashed vertical line + label placed at upper-right corner
# away from top-ranked bars per D-29.
ax.axvline(league_avg, linestyle="--", color="#666666", linewidth=1.0)
ax.text(
    league_avg + 1.5,
    n - 0.5,
    f"League avg = {league_avg:.1f}",
    fontsize=9,
    color="#444444",
    va="top",
)
```
- Bar y-positions are `np.arange(n)[::-1]` so matplotlib auto-ranges to roughly `(-0.5, n - 0.5)`. Label at `y = n - 0.5` with `va="top"` placed it AT the very top of the axes, on top of the PHI top bar — overlapping the bar instead of sitting in clear space as the comment claimed.

**After** (lines 199–211, ruff-formatted):
```python
# League-average dashed vertical line + label.
# Reserve a 1-unit headroom band above the top bar so the label sits in
# clear space adjacent to the line (was overlapping the PHI bar pre-fix).
ax.set_ylim(-0.6, n + 0.5)
ax.axvline(league_avg, linestyle="--", color="#666666", linewidth=1.0)
ax.text(
    league_avg + 1.5,
    n,
    f"League avg = {league_avg:.1f}",
    fontsize=9,
    color="#444444",
    va="center",
)
```
- `ax.set_ylim(-0.6, n + 0.5)` reserves a 1-unit clearance band above the top bar at `y = n - 1`.
- Label `y` value `n - 0.5` → `n` (now centered inside the headroom band).
- Label `va` `"top"` → `"center"`.
- Comment updated to reflect actual placement.

Verification:
- `ruff check analysis/03_visualizations.py` — passed.
- `ruff format --check` — required reformat (see Deviation 1); applied; re-verified.
- Semantic regex checks (per constraints — ruff splits the multi-arg `ax.text` call across multiple lines, so literal one-liner string matches won't work):
  - `ax.set_ylim(-0.6, n + 0.5)` present
  - new `ax.text(... y=n, ..., va="center")` block present (regex over the multi-line form)
  - old `n - 0.5,\n        f"League avg` placement gone
  - old `va="top"` no longer in the league-avg block
  - `ylim` set BEFORE `axvline` (precedence verified by string offsets)

Side-effects (unchanged):
- Top-3 / bottom-3 score annotations at lines 213–224 use `y_positions[i]` in `[0, n - 1]`, well inside the new ylim — untouched.
- Hero path uses `tight_layout()` + global `savefig.bbox="tight"` — handled the slightly taller axes fine.
- Social-preview path uses `exact_pixels=(1280, 640)` with `bbox=None`; ylim is internal to the axes and does NOT change figsize, so 1280x640 still hits exactly (verified post-regen via PIL).

### Task 2 — Resync paired `.ipynb` via jupytext — DONE

**File:** `analysis/03_visualizations.ipynb`

Commands:
```
.venv/Scripts/jupytext.exe --sync analysis/03_visualizations.py
.venv/Scripts/jupyter.exe nbconvert --clear-output --inplace analysis/03_visualizations.ipynb
```

(Toolchain invoked from main-repo `.venv/` via absolute path — see Deviation 2.)

Verification (semantic, JSON walk over `.ipynb`):
- `ax.set_ylim(-0.6, n + 0.5)` propagated into the code-cell source.
- New `ax.text(y=n, va="center")` block present in code-cell source (multi-line regex match).
- Old `n - 0.5, f"League avg` placement absent.
- All code-cell `outputs == []` and `execution_count in (None, 0)` (CLAUDE.md "outputs cleared before commit").

### Task 3 — Regenerate hero + social-preview PNGs — DONE

**Files:** `findings/images/01_predictability_ranking.png`, `findings/images/01_predictability_ranking_top12.png`

End-to-end execution:
```
.venv/Scripts/jupyter.exe nbconvert --to notebook --execute --inplace analysis/03_visualizations.ipynb
.venv/Scripts/jupyter.exe nbconvert --clear-output --inplace analysis/03_visualizations.ipynb
```

Notebook executed against `data/nfl_defensive_tendencies.db` (49.6 MB; copied into the worktree from the main repo before execution — see Deviation 4). All cells ran cleanly. One `RuntimeWarning` from zmq's Proactor event loop (not a failure; pre-existing on this Windows + Python 3.11 + ipykernel 7.2 stack — ignored).

**Final PNG sizes (after re-render):**

| File | Size | mtime | In 30–80 KB band? |
|------|------|-------|-------------------|
| `01_predictability_ranking.png` | 115,211 B (~112 KB) | 2026-05-02 | ABOVE band (matches prior 115,615 B baseline; >80 KB issue OUT OF SCOPE per plan) |
| `01_predictability_ranking_top12.png` | 52,965 B (~52 KB) | 2026-05-02 | within band |

**Dimension verification (PIL):**
- Hero: 1845x2173 px (8x11 portrait at ~230 DPI under tight-bbox crop — consistent with prior committed hero).
- Social preview: exactly **1280x640 px** as required.

**mtime check** (per constraints, against HEAD~1 — Task 1 commit time, since Task 2 commits .ipynb timestamp metadata):
- HEAD~1 (Task 1 `93e6952`) ct = 1777736526
- PNG1 mtime = 1777736580 > 1777736526
- PNG2 mtime = 1777736580 > 1777736526
- Both PNGs regenerated since HEAD~1 — PASS.

## Visual Confirmation (read both PNGs as images)

**Hero `01_predictability_ranking.png`:**
- (a) "League avg = 14.3" label sits in **clear space above the PHI top bar** — no overlap with any bar. Adjacent to and to the right of the dashed vertical line, in the headroom band reserved by the new `ax.set_ylim`. CONFIRMED.
- (b) Headline-above-subhead order from 260502-ftr is preserved: large "Some NFL Defenses Are More Predictable Than Others" headline ABOVE the small gray subhead "32 NFL defenses, blitz rate on 4 pre-registered situations…". CONFIRMED.
- (c) No clipping at edges. All 32 team labels and the x-axis label "Predictability index (0-100; higher = more predictable)" fully visible. Top-3 (PHI 23.5 / SF 23.5 / IND 22.4) shown in blue, bottom-3 (MIA 5.9 / TB 4.1 / MIN 1.5) in orange, all with one-decimal annotations. League-avg dashed line at x=14.3 unchanged.

**Social preview `01_predictability_ranking_top12.png` (1280x640):**
- (a) "League avg = 14.3" label sits cleanly above the PHI top bar; **no overlap**. CONFIRMED.
- (b) Headline-above-subhead order is preserved (large headline on top, smaller gray subhead "Most Predictable Defenses 2022-2025." below). CONFIRMED.
- (c) Two **pre-existing** edge-clipping issues remain (already documented in the prior 260502-ftr SUMMARY as separate, OUT OF SCOPE concerns):
  1. The hero-headline `(Top 12)` suffix is right-clipped at the 1280-px figure boundary — long-title vs. narrow-figsize issue, untouched.
  2. The bottom of the x-axis label "Predictability index (0-100; higher = more predictable)" is slightly cropped at the bottom edge — driven by the 14pt `pad=22` headline pushing content downward in the fixed 640-px figure under `bbox=None`. Pre-existing as of 260502-ftr.

  Neither is the league-avg-spacing target of this task, and neither is a regression — both predate Task 1 of 260502-g4w.

## Deviations From Plan

### 1 — Rule 3 (auto-fix blocking issue): ruff format reformatted the multi-arg `ax.text` call

This is the same pattern documented in the prior 260502-ftr SUMMARY (Deviation 1).

The plan target block was:
```python
ax.text(
    league_avg + 1.5,
    n,
    f"League avg = {league_avg:.1f}",
    fontsize=9, color="#444444", va="center",
)
```
(two-arguments-per-line on the trailing line: `fontsize=9, color="#444444", va="center",`).

After `ruff format`, ruff split each kwarg onto its own line per its default policy:
```python
ax.text(
    league_avg + 1.5,
    n,
    f"League avg = {league_avg:.1f}",
    fontsize=9,
    color="#444444",
    va="center",
)
```

Per the constraints I used **semantic regex checks**, not literal multi-arg one-liner string matches, so this is non-blocking. All semantic invariants hold: `va="center"` present, `va="top"` removed, label `y=n` (not `n - 0.5`), `ax.set_ylim(-0.6, n + 0.5)` present and positioned before `axvline`. No behavior change.

### 2 — Rule 3 (auto-fix blocking issue): main-repo `.venv/` accessed via absolute path from the worktree

Same pattern as the prior 260502-ftr SUMMARY (Deviation 2). I'm executing inside a git worktree at `.claude/worktrees/agent-a5c3ec473a5d7a3df/`. The full pinned `.venv/` (matplotlib + jupytext + jupyter + ruff + the locked NumPy/pandas pins) lives only in the **main repo root** at `C:/Users/geoca/projects/nfl-coverage-tendencies/.venv/`, not in the worktree.

I did NOT repeat the venv-selection loop from the prior task — I went directly to `C:/Users/geoca/projects/nfl-coverage-tendencies/.venv/Scripts/{ruff,jupytext,jupyter,python}.exe` for all toolchain invocations. The toolchain works fine across the worktree filesystem boundary (it operates on file paths, not `cwd` lookups). No project-file change.

### 3 — Notebook execution-timestamp metadata churn (non-blocking, expected)

Same pattern as the prior 260502-ftr SUMMARY (Deviation 3). `jupyter nbconvert --execute --inplace` writes ISO-8601 timestamps into each code cell's `metadata.execution` block (`iopub.execute_input`, `iopub.status.busy`, `iopub.status.idle`, `shell.execute_reply`). `--clear-output --inplace` clears outputs but does NOT strip those metadata timestamps. The Task 3 `.ipynb` diff is purely those updates — no source/output churn. Staged with the PNGs in the Task 3 commit and called out in the commit body.

### 4 — Rule 3 (auto-fix blocking issue): copied DB into the worktree before notebook execution

The worktree was checked out fresh and `data/nfl_defensive_tendencies.db` (gitignored) did not exist in it. The notebook resolves `DB_PATH` via `_common.py` to `<repo_root>/data/nfl_defensive_tendencies.db` and `assert DB_PATH.exists()` is run at notebook startup. Without the DB the execute step would fail.

I copied the existing DB from the main repo (49.6 MB; built 2026-04-29) into the worktree's `data/` folder:
```
cp "C:/Users/geoca/projects/nfl-coverage-tendencies/data/nfl_defensive_tendencies.db" data/nfl_defensive_tendencies.db
```
Verified `git status` showed no `*.db` entry (gitignored). DB was NOT staged; not committed. This is purely an executor-environment setup step — no project-file change.

### 5 — Worktree base hard-reset on entry (per `<worktree_branch_check>`)

The worktree's initial `git merge-base HEAD e3accb6` returned `72b20b14` (a different commit), so I ran `git reset --hard e3accb6b646b684332c895d6b3070e5d8afe3b90` per the worktree-branch-check instructions. Post-reset `git rev-parse HEAD == e3accb6...` confirmed. All three task commits were then made on top of `e3accb6`. No project-file impact; this is an orchestrator-instructed worktree-setup step.

## Code Block — Before vs After (canonical reference)

**Before** (`analysis/03_visualizations.py` lines 199–209):
```python
# League-average dashed vertical line + label placed at upper-right corner
# away from top-ranked bars per D-29.
ax.axvline(league_avg, linestyle="--", color="#666666", linewidth=1.0)
ax.text(
    league_avg + 1.5,
    n - 0.5,
    f"League avg = {league_avg:.1f}",
    fontsize=9,
    color="#444444",
    va="top",
)
```

**After** (`analysis/03_visualizations.py` lines 199–211, ruff-formatted):
```python
# League-average dashed vertical line + label.
# Reserve a 1-unit headroom band above the top bar so the label sits in
# clear space adjacent to the line (was overlapping the PHI bar pre-fix).
ax.set_ylim(-0.6, n + 0.5)
ax.axvline(league_avg, linestyle="--", color="#666666", linewidth=1.0)
ax.text(
    league_avg + 1.5,
    n,
    f"League avg = {league_avg:.1f}",
    fontsize=9,
    color="#444444",
    va="center",
)
```

## Regeneration Outcome

**Status:** SUCCEEDED.

End-to-end notebook execution worked first try via `.venv/Scripts/jupyter.exe`. DB present, `analysis._common.DB_PATH` resolved to `data/nfl_defensive_tendencies.db`, `assert DB_PATH.exists()` passed, all cells ran without error. Outputs cleared post-execute per the workflow.

PNGs verified post-regeneration:
- `findings/images/01_predictability_ranking.png` — mtime 1777736580 > HEAD~1 ct 1777736526; size 115,211 B in [10, 250] KB sanity band; visual: league-avg label in clear headroom band above PHI bar, no overlap.
- `findings/images/01_predictability_ranking_top12.png` — mtime 1777736580 > HEAD~1 ct 1777736526; size 52,965 B in band; **exactly 1280x640 px**; visual: league-avg label cleanly above top bar, no overlap.

Hero is ~112 KB which matches the prior committed hero (115,615 B from 260502-ftr) — same 8x11 portrait at 200 DPI with 32 team labels. The >80 KB band issue is, per the plan and the prior SUMMARY, explicitly OUT OF SCOPE for this task. Not a regression.

## Commits

| Task | Hash | Message |
|------|------|---------|
| 1 | `93e6952` | `fix(viz): reserve headroom for league-avg label above top bar (260502-g4w)` |
| 2 | `4eef3ff` | `chore(viz): jupytext-sync 03_visualizations.ipynb (260502-g4w)` |
| 3 | `d6c17eb` | `chore(viz): regenerate hero + social-preview PNGs (260502-g4w)` |

## Constraints Honored

- Did NOT modify `analysis/_style.py`. Fix is local to `render_leaderboard()`.
- Did NOT add a `tests/` directory.
- Did NOT stage `data/raw/` or any `*.db` files. `git status` confirmed clean of those before each commit; the DB I copied into the worktree (Deviation 4) is gitignored and never appeared in the staging area.
- Did NOT touch `figsize`, `dpi`, or `exact_pixels` arguments — pixel dimensions of the social preview remain exactly 1280x640.
- Did NOT commit `.planning/quick/` PLAN.md / SUMMARY.md / STATE.md (orchestrator handles after merge).
- Did NOT update `.planning/ROADMAP.md`.
- Used POSIX shell paths via Git Bash on Windows; used `.venv/Scripts/...` for all toolchain commands (resolved to main-repo path per Deviation 2).
- All three commits use conventional-commit format with the suggested messages.

## Self-Check

- `analysis/03_visualizations.py` — exists, modified, ruff check + format clean: PASS
- `analysis/03_visualizations.ipynb` — exists, in sync with .py (semantic regex match), all code-cell outputs cleared: PASS
- `findings/images/01_predictability_ranking.png` — exists, mtime fresh (> HEAD~1 ct), size 115,211 B in sane band, league-avg label in clear headroom above PHI bar (visually confirmed), headline-above-subhead order preserved: PASS
- `findings/images/01_predictability_ranking_top12.png` — exists, mtime fresh, size 52,965 B in 30–80 KB band, **exactly 1280x640 px**, league-avg label cleanly above top bar (visually confirmed), headline-above-subhead preserved: PASS
- commit `93e6952` — present in `git log`: PASS
- commit `4eef3ff` — present in `git log`: PASS
- commit `d6c17eb` — present in `git log`: PASS

## Self-Check: PASSED
