-- ---
-- Question:    For each (defteam x season x situation), what is the blitz rate (n_blitzers > 0) on pass plays?
-- Filter:      competitive_plays JOIN ftn_play, play_type='pass', situation_id IN (S1,S2,S3,S4) per docs/analysis-plan.md.
-- Result shape: defteam TEXT, season INT, situation_id TEXT, blitz_count INT, no_blitz_count INT, total_pass_plays INT, blitz_rate REAL
-- Hypothesis:  S1-H1 (league blitz rate on 3rd-and-long > 35%); S1-H2 (>=3 teams blitz > 50% on S1); supports STAT-04 predictability index input alongside QUERY-07.
-- Caveats:     n_blitzers is NaN on run plays - the play_type='pass' filter is applied BEFORE counting. FTN n_blitzers counts extra rushers beyond the base front; n_blitzers > 0 is the blitz indicator for this dataset. Cells with N<30 will appear here; min_n_filter enforces the floor at claim time.
-- N expected:  ~32 teams x 4 seasons x 4 situations = ~512 rows (some cells may be missing if a team had zero plays in a situation in a season).
-- ---

WITH situations AS (
    SELECT cp.defteam, cp.season, cp.game_id, cp.play_id, cp.play_type,
           CASE
               WHEN cp.down = 3 AND cp.ydstogo >= 7              THEN 'S1_3rd_and_long'
               WHEN cp.yardline_100 <= 20                        THEN 'S2_red_zone'
               WHEN cp.down = 1 AND cp.ydstogo = 10              THEN 'S3_1st_and_10'
               WHEN cp.down = 2 AND cp.ydstogo BETWEEN 3 AND 6   THEN 'S4_2nd_and_medium'
               ELSE NULL
           END AS situation_id
    FROM competitive_plays cp
)
SELECT
    s.defteam,
    s.season,
    s.situation_id,
    SUM(CASE WHEN f.n_blitzers > 0 THEN 1 ELSE 0 END)   AS blitz_count,
    SUM(CASE WHEN f.n_blitzers = 0 THEN 1 ELSE 0 END)   AS no_blitz_count,
    COUNT(*)                                            AS total_pass_plays,
    ROUND(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END), 4) AS blitz_rate
FROM situations s
JOIN ftn_play f USING (game_id, play_id)
WHERE s.situation_id IS NOT NULL
  AND s.play_type = 'pass'
GROUP BY s.defteam, s.season, s.situation_id
ORDER BY s.defteam, s.season, s.situation_id;
