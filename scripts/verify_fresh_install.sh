#!/usr/bin/env bash
# Fresh-venv reproducibility check (SHIP-02).
# Runs the recruiter ritual end-to-end: clean venv -> install -> ETL -> notebook
# execute -> notebook clear-output. Prints elapsed time at the end so the
# <=10-minute reproducibility budget claim in README setup is verifiable.
#
# Usage:
#   bash scripts/verify_fresh_install.sh
#
# Notes:
# - Creates `.venv-fresh/` at repo root; deletes any existing one first so the
#   "fresh" claim holds. Does NOT touch the developer's `.venv/`.
# - Uses the two-step nfl_data_py install pattern (PROJECT.md Key Decisions):
#     pip install -r requirements.txt (excluding nfl_data_py line)
#     pip install nfl_data_py==0.3.3 --no-deps appdirs fastparquet
#   The first pass installs the transitive non-nfl_data_py deps with the
#   strict pandas>=2.1,<2.3 constraint; the second pass installs nfl_data_py
#   itself without re-resolving its declared pandas<2.0 metadata conflict.
# - Requires `python3.11` on PATH (Linux/macOS) -- not the system `python3`.
# - .venv-fresh/ is gitignored; it is left in place after the run for inspection.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR="$REPO_ROOT/.venv-fresh"
START_TS=$(date +%s)

echo "==> Removing any existing fresh-venv at $VENV_DIR"
rm -rf "$VENV_DIR"

echo "==> Creating Python 3.11 venv at $VENV_DIR"
python3.11 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing requirements.txt (excluding nfl_data_py for now)"
grep -v '^nfl_data_py' requirements.txt | pip install -r /dev/stdin

echo "==> Installing nfl_data_py==0.3.3 with --no-deps + companions"
pip install --no-deps nfl_data_py==0.3.3 'appdirs>=1' 'fastparquet>=0.5'

echo "==> Verifying core imports"
python -c "import nfl_data_py; import pandas; import numpy; import scipy; import matplotlib; import seaborn; import jupytext; import nbconvert; print('imports OK')"

echo "==> Running ETL: python -m etl.run"
python -m etl.run

echo "==> Executing notebooks end-to-end"
for nb in analysis/01_exploratory.ipynb \
          analysis/02_predictability_modeling.ipynb \
          analysis/03_visualizations.ipynb; do
    echo "    --> $nb"
    jupyter nbconvert --to notebook --execute --inplace "$nb"
done

echo "==> Clearing notebook outputs"
for nb in analysis/01_exploratory.ipynb \
          analysis/02_predictability_modeling.ipynb \
          analysis/03_visualizations.ipynb; do
    jupyter nbconvert --clear-output --inplace "$nb"
done

END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))
echo "==> Fresh-install reproducibility check PASSED in ${ELAPSED}s"
echo "    Reproducibility budget: 600s (10 min). Observed: ${ELAPSED}s."
if [ "$ELAPSED" -gt 600 ]; then
    echo "WARNING: exceeded 10-minute reproducibility budget"
    exit 1
fi
