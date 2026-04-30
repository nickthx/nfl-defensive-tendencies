-- schema/02_indexes.sql -- composite indexes for situational queries (SCHEMA-02).
-- Note: PRIMARY KEY (game_id, play_id) on plays and ftn_play is implicit; not re-declared here.
-- Index list capped at five per ARCHITECTURE.md indexing strategy (don't over-index at this scale).

-- Dominant Phase 3 query shape: filter on situation, group by team
CREATE INDEX idx_plays_situation
    ON plays (down, ydstogo, yardline_100);

-- Team-by-season slicing (depends on D-05 denormalization of season onto plays)
CREATE INDEX idx_plays_defteam_season
    ON plays (defteam, season);

-- Play-type prefix filter (used by competitive_plays view)
CREATE INDEX idx_plays_play_type
    ON plays (play_type);

-- FTN charting columns used in tendency aggregations
CREATE INDEX idx_ftn_n_pass_rushers
    ON ftn_play (n_pass_rushers);

CREATE INDEX idx_ftn_n_blitzers
    ON ftn_play (n_blitzers);
