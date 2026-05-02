---
phase: quick/260502-ftr
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - analysis/03_visualizations.py
  - analysis/03_visualizations.ipynb
  - findings/images/01_predictability_ranking.png
  - findings/images/01_predictability_ranking_top12.png
autonomous: true
requirements: [QUICK-260502-ftr]
---

<objective>
Fix header/subhead stacking in `render_leaderboard()` so the large headline sits above the small gray subhead (newspaper convention), then resync the paired notebook and regenerate the two affected PNGs.

Purpose: The hero image `findings/images/01_predictability_ranking.png` currently renders the subtitle ABOVE the headline (subtitle is placed at `y=1.02` axes-fraction with `va="bottom"` while `set_title` sits at default ~y=1.0), which inverts the intended hierarchy and clips the topmost subtitle line under `savefig.bbox="tight"`. The same renderer also produces the social preview (`_top12.png`), so a single edit fixes both.

Output: Updated renderer in `analysis/03_visualizations.py`, paired `.ipynb` resynced, both PNGs regenerated with correct title-on-top / subhead-below order.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@.planning/STATE.md
@CLAUDE.md
@analysis/03_visualizations.py
@analysis/_style.py

# Project realities the executor must honor
- Python 3.11 only; matplotlib + seaborn only (no Plotly/Streamlit).
- `data/raw/` and `*.db` are gitignored — do NOT commit them.
- jupytext .py:percent <-> .ipynb pairing: both files must stay in sync.
- Notebooks: clear outputs before commit (`nbconvert --clear-output --inplace`); figures live ONLY in `findings/images/`.
- ruff is the only linter; this change adds no new imports.
- No tests/ directory — assertions live inside ETL.
- No new dependencies.

# Current broken block (analysis/03_visualizations.py lines 187-192)
```python
ax.set_title(title, fontsize=13, loc="left")
# Subtitle as a text below the title.
ax.text(
    0.0, 1.02, subtitle,
    transform=ax.transAxes, fontsize=10, color="#444444", va="bottom",
)
```

# Target block
```python
# Headline (large) — pad in points keeps spacing stable across both figsizes
ax.set_title(title, fontsize=14, loc="left", pad=22)
# Subhead (small, gray) sits just above the axes top, below the headline
ax.text(
    0.0, 1.0, subtitle,
    transform=ax.transAxes, fontsize=10, color="#444444",
    va="bottom", ha="left",
)
```

`pad=22` is in points (absolute), so spacing stays stable across the 8x11 hero
and 6.4x3.2 social-preview figsizes. No new imports required.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix title/subhead order in render_leaderboard</name>
  <files>analysis/03_visualizations.py</files>
  <action>
In `analysis/03_visualizations.py`, replace the current title+subtitle block (lines 187-192) with the corrected version:

```python
# Headline (large) — pad in points keeps spacing stable across both figsizes
ax.set_title(title, fontsize=14, loc="left", pad=22)
# Subhead (small, gray) sits just above the axes top, below the headline
ax.text(
    0.0, 1.0, subtitle,
    transform=ax.transAxes, fontsize=10, color="#444444",
    va="bottom", ha="left",
)
```

Changes vs. current:
- Headline `fontsize` 13 -> 14 and add `pad=22` (points, absolute spacing).
- Subhead `y` 1.02 -> 1.0 and add explicit `ha="left"`.

Do NOT modify `analysis/_style.py` — the fix is local to `render_leaderboard`. No new imports. Do not touch any other call site or function.
  </action>
  <verify>
    <automated>cd C:/Users/geoca/projects/nfl-coverage-tendencies && python -m ruff check analysis/03_visualizations.py && python -c "import re,sys; s=open('analysis/03_visualizations.py',encoding='utf-8').read(); assert 'pad=22' in s and 'fontsize=14, loc=\"left\", pad=22' in s and '0.0, 1.0, subtitle' in s and 'ha=\"left\"' in s and '1.02, subtitle' not in s, 'renderer edit not applied as specified'; print('OK')"</automated>
  </verify>
  <done>
`analysis/03_visualizations.py` `render_leaderboard()` uses `ax.set_title(title, fontsize=14, loc="left", pad=22)` followed by `ax.text(0.0, 1.0, subtitle, ..., ha="left")`. Ruff passes. The literal string `1.02, subtitle` no longer appears in the file.
  </done>
</task>

<task type="auto">
  <name>Task 2: Resync paired .ipynb via jupytext</name>
  <files>analysis/03_visualizations.ipynb</files>
  <action>
Run jupytext to propagate the .py edit into the paired notebook:

```bash
cd C:/Users/geoca/projects/nfl-coverage-tendencies
jupytext --sync analysis/03_visualizations.py
```

This rewrites `analysis/03_visualizations.ipynb` so its cell mirroring `render_leaderboard` matches the .py source. Per CLAUDE.md, notebook outputs are cleared before commit; if `jupytext --sync` writes any cell outputs, clear them:

```bash
jupyter nbconvert --clear-output --inplace analysis/03_visualizations.ipynb
```

Do not edit the .ipynb by hand. Do not run the notebook in this task — regeneration of PNGs is Task 3.
  </action>
  <verify>
    <automated>cd C:/Users/geoca/projects/nfl-coverage-tendencies && python -c "import json,sys; nb=json.load(open('analysis/03_visualizations.ipynb',encoding='utf-8')); src=''.join(''.join(c.get('source',[])) for c in nb['cells'] if c.get('cell_type')=='code'); assert 'pad=22' in src and 'ha=\"left\"' in src and '1.02, subtitle' not in src, 'ipynb not in sync with .py'; assert all((not c.get('outputs')) and (c.get('execution_count') in (None,0)) for c in nb['cells'] if c.get('cell_type')=='code'), 'notebook outputs must be cleared before commit'; print('OK')"</automated>
  </verify>
  <done>
`analysis/03_visualizations.ipynb` cell mirroring `render_leaderboard` contains the new `pad=22` / `ha="left"` code and no longer contains `1.02, subtitle`. All code-cell outputs are cleared.
  </done>
</task>

<task type="auto">
  <name>Task 3: Regenerate hero + social-preview PNGs</name>
  <files>findings/images/01_predictability_ranking.png, findings/images/01_predictability_ranking_top12.png</files>
  <action>
Regenerate the two affected PNGs by executing the visualizations script end-to-end (it loads from `data/nfl_v1.db`, which already exists locally):

```bash
cd C:/Users/geoca/projects/nfl-coverage-tendencies
python analysis/03_visualizations.py
```

If running the .py directly is not viable (jupytext percent format), execute the paired notebook in place and clear outputs afterward:

```bash
jupyter nbconvert --to notebook --execute --inplace analysis/03_visualizations.ipynb
jupyter nbconvert --clear-output --inplace analysis/03_visualizations.ipynb
```

Use whichever path the existing project tooling supports; the goal is identical — both PNGs in `findings/images/` overwritten via `render_leaderboard()`. Do NOT stage or commit `data/raw/` or `*.db` artifacts.
  </action>
  <verify>
    <automated>cd C:/Users/geoca/projects/nfl-coverage-tendencies && python -c "import os,subprocess,sys; p1='findings/images/01_predictability_ranking.png'; p2='findings/images/01_predictability_ranking_top12.png'; head=subprocess.check_output(['git','log','-1','--format=%ct','HEAD']).decode().strip(); head=int(head); m1=int(os.path.getmtime(p1)); m2=int(os.path.getmtime(p2)); s1=os.path.getsize(p1); s2=os.path.getsize(p2); assert m1>head and m2>head, f'PNGs not regenerated since HEAD ({head}); got {m1},{m2}'; assert 10*1024 <= s1 <= 250*1024, f'hero size out of sane band: {s1} bytes'; assert 10*1024 <= s2 <= 250*1024, f'social size out of sane band: {s2} bytes'; print(f'OK hero={s1}B social={s2}B')"</automated>
  </verify>
  <done>
Both `findings/images/01_predictability_ranking.png` and `findings/images/01_predictability_ranking_top12.png` have mtime newer than HEAD commit, file sizes are within a sane band (not zero, not blown out), and a visual spot-check confirms the headline (large) renders ABOVE the small gray subhead in both images.
  </done>
</task>

</tasks>

<verification>
- `python -m ruff check analysis/03_visualizations.py` passes.
- `analysis/03_visualizations.py` and `analysis/03_visualizations.ipynb` are in sync (both contain `pad=22` / `ha="left"`; neither contains `1.02, subtitle`).
- Both PNGs regenerated (mtime > HEAD commit time) with sane file sizes.
- `git status` shows only the four expected modified files; no `data/raw/` or `*.db` staged.
</verification>

<success_criteria>
- Headline ("Some NFL Defenses Are More Predictable Than Others") renders large and on top.
- Subhead (small, gray, "32 NFL defenses, blitz rate on 4 pre-registered situations, 2022-2025; ...") renders directly below the headline, above the bar plot.
- No clipping of either line under `savefig.bbox="tight"`.
- Same fix observed in both `01_predictability_ranking.png` (8x11 hero) and `01_predictability_ranking_top12.png` (6.4x3.2 social preview, 1280x640 px).
- No changes to `analysis/_style.py`, no new dependencies, no new imports, no tests/ directory added.
</success_criteria>
