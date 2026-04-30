"""Project matplotlib rcParams + seaborn palette for portfolio-friendly figures.

Per STAT-02 and .planning/phases/03-analytical-layer-sql-python/03-CONTEXT.md
Claude's Discretion: neutral seaborn 'colorblind'-derived palette; per-team
32-color palette is a Phase 4 / VIZ-01 decision and is not implemented here.

Notebook usage (top of every notebook, after imports):

    from analysis._style import apply_style
    apply_style()
"""

from __future__ import annotations

import matplotlib as mpl
import seaborn as sns

# Single named palette for v1 — keeps non-hero charts visually consistent.
PALETTE: str = "colorblind"

# rcParams chosen to satisfy:
#  - savefig.dpi 200 so Phase 4 PNGs land in the 30-80 KB band per CLAUDE.md
#  - figure font sizes legible above the README fold on a typical 1080p display
#  - tight axes spines (no top/right) for an analyst-memo aesthetic
RCPARAMS: dict[str, object] = {
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "figure.dpi": 100,
    "figure.figsize": (8.0, 5.0),
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "legend.frameon": False,
}


def apply_style() -> None:
    """Apply project rcParams and the seaborn 'colorblind' palette in-place."""
    mpl.rcParams.update(RCPARAMS)
    sns.set_palette(PALETTE)
