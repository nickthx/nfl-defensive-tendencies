-- ---
-- Question:    What is the average EPA allowed when the defense blitzes (n_blitzers > 0) vs does not, sliced by pre-registered situation?
-- Filter:      competitive_plays JOIN ftn_play, play_type='pass', situation_id IN (S1,S2,S3,S4); excludes plays with NULL epa.
-- Result shape: situation_id TEXT, blitz_flag INT (0|1), n_pass_plays INT, mean_epa REAL, stddev_epa REAL
-- Hypothesis:  n/a (rollup; supports the FINDINGS narrative on blitz cost/benefit).
-- Caveats:     EPA is computed by nflfastR's WP/EP model and may be NULL on no-play snaps even after the competitive_plays filter; rows with NULL epa are dropped via WHERE epa IS NOT NULL. FTN n_blitzers counts extra rushers beyond the base front; n_blitzers > 0 is the blitz indicator for this dataset. Within-situation N can fall below 100 in S1 and S4; min_n_filter applies in the notebook.
-- N expected:  4 situations x 2 blitz flags = 8 rows; total denominator ~57k pass plays minus NULL-epa snaps.
-- ---

WITH situations AS (
    SELECT cp.defteam, cp.season, cp.game_id, cp.play_id, cp.play_type, cp.epa,
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
    s.situation_id,
    CASE WHEN f.n_blitzers > 0 THEN 1 ELSE 0 END  AS blitz_flag,
    COUNT(*)                                       AS n_pass_plays,
    ROUND(AVG(s.epa), 4)                           AS mean_epa,
    ROUND(
        SQRT(AVG(s.epa * s.epa) - AVG(s.epa) * AVG(s.epa)), 4
    )                                              AS stddev_epa
FROM situations s
JOIN ftn_play f USING (game_id, play_id)
WHERE s.situation_id IS NOT NULL
  AND s.play_type = 'pass'
  AND s.epa IS NOT NULL
GROUP BY s.situation_id, blitz_flag
ORDER BY s.situation_id, blitz_flag;
