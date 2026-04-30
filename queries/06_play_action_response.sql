-- ---
-- Question:    Per situation, how does the league blitz rate change against play-action vs straight dropback?
-- Filter:      competitive_plays JOIN ftn_play, play_type='pass', situation_id IN (S1,S2,S3,S4).
-- Result shape: situation_id TEXT, is_play_action INT (0|1), n_pass_plays INT, blitz_count INT, blitz_rate REAL
-- Hypothesis:  S1 cross-cutting PA modifier (gap >= 5pp on PA vs straight dropback); supports STAT-06 chi-square headline (D-09).
-- Caveats:     is_play_action is FTN-charted (subjective); cells stratified to PA=1 in S1/S4 may fall below N>=30 at the per-team level - kept league-aggregate here, the notebook breaks per-team. FTN n_blitzers counts extra rushers beyond the base front; n_blitzers > 0 is the blitz indicator for this dataset.
-- N expected:  4 situations x 2 PA flags = 8 rows.
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
    s.situation_id,
    f.is_play_action,
    COUNT(*)                                            AS n_pass_plays,
    SUM(CASE WHEN f.n_blitzers > 0 THEN 1 ELSE 0 END)   AS blitz_count,
    ROUND(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END), 4) AS blitz_rate
FROM situations s
JOIN ftn_play f USING (game_id, play_id)
WHERE s.situation_id IS NOT NULL
  AND s.play_type = 'pass'
  AND f.is_play_action IS NOT NULL
GROUP BY s.situation_id, f.is_play_action
ORDER BY s.situation_id, f.is_play_action;
