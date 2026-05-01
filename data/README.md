# Data

This directory holds the project's data layer. The SQLite database is the analytical source of truth and is regenerated from a fresh clone via the ETL pipeline.

## Files

- `data/nfl_defensive_tendencies.db` — **gitignored** (200-400 MB exceeds GitHub's 100 MiB hard limit). Regenerate via `python -m etl.run`. Contains 1,139 games / 197,362 plays / 185,215 ftn_play rows / 105,556 competitive_plays / 58,178 competitive pass plays joined to FTN, 2022-2025.
- `data/raw/*.parquet` — **gitignored**. The ETL caches `nfl_data_py` pulls here on first run; subsequent runs are idempotent. Layout: `pbp_<year>.parquet` + `ftn_<year>.parquet` per year (8 files, ~80 MB combined).
- `data/README.md` — this file.

## Regeneration path

```bash
python -m etl.run
```

Cold cache: ~2-5 minutes. Warm cache (parquet files already populated): under 60 seconds.

## Schema

DDL lives in `schema/`:
- `schema/01_create_tables.sql` — `games`, `plays`, `ftn_play` tables with `(game_id, play_id)` PKs.
- `schema/02_indexes.sql` — composite indexes on `(down, ydstogo, yardline_100)` and `(defteam, season)`.
- `schema/03_views.sql` — `competitive_plays` view (the project-wide analytical universe; `play_type IN ('pass','run')` AND `wp BETWEEN 0.05 AND 0.95` AND not 2-minute drill / OT).

Every analytical query in `queries/*.sql` reads from `competitive_plays`, never from `plays` directly.
