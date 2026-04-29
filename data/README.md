# Data

The SQLite database `data/nfl_*.db` is gitignored (200–400 MB exceeds GitHub's 100 MiB hard limit).

To regenerate from a fresh clone: `python -m etl.run` (Phase 2 deliverable; ~2–5 min on first run).

Raw `nfl_data_py` parquet caches land in `data/raw/` (also gitignored). The ETL creates this directory at runtime.
