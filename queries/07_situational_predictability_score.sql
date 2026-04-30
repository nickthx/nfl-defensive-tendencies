-- ---
-- Question:    Per (defteam x season x situation), how many pass plays were blitzes vs not? Raw inputs for the predictability index (STAT-04, STAT-05).
-- Filter:      competitive_plays JOIN ftn_play, play_type='pass', situation_id IN (S1,S2,S3,S4).
-- Result shape: defteam TEXT, season INT, situation_id TEXT, blitz_count INT, no_blitz_count INT, total_pass_plays INT
-- Hypothesis:  n/a (rollup; feeds the H/log(k) headline + KL secondary in 02_predictability_modeling.ipynb cell 1).
-- Caveats:     The notebook computes entropy here, NOT the SQL - keeps the .sql portable and lets recruiters re-run with a different normalization scheme. FTN n_blitzers counts extra rushers beyond the base front; n_blitzers > 0 is the blitz indicator for this dataset. Sample-size discipline (min_n_filter at N>=30) is applied AFTER this rollup, in the notebook.
-- N expected:  ~32 teams x 4 seasons x 4 situations = up to 512 rows.
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
    COUNT(*)                                            AS total_pass_plays
FROM situations s
JOIN ftn_play f USING (game_id, play_id)
WHERE s.situation_id IS NOT NULL
  AND s.play_type = 'pass'
GROUP BY s.defteam, s.season, s.situation_id
ORDER BY s.defteam, s.season, s.situation_id;
