-- ---
-- Question:    How has each defense's blitz rate (n_blitzers > 0 on pass plays) trended across the 4-season scope 2022-2025? Includes a LEAGUE aggregate row per season.
-- Filter:      competitive_plays JOIN ftn_play, play_type='pass'.
-- Result shape: defteam TEXT (32 teams + 'LEAGUE'), season INT, blitz_count INT, no_blitz_count INT, total_pass_plays INT, blitz_rate REAL
-- Hypothesis:  n/a (rollup; supports the 4-season scope narrative D-10 and Phase 4 visualization VIZ-03).
-- Caveats:     Per-team-per-season cells average ~445 pass plays (~57k / 32 / 4); plenty of headroom above N>=30. The 'LEAGUE' aggregate row has the same shape and can be selected via WHERE defteam='LEAGUE'. FTN n_blitzers counts extra rushers beyond the base front; n_blitzers > 0 is the blitz indicator for this dataset.
-- N expected:  32 teams x 4 seasons + 4 league rows = 132 rows.
-- ---

SELECT
    cp.defteam,
    cp.season,
    SUM(CASE WHEN f.n_blitzers > 0 THEN 1 ELSE 0 END)   AS blitz_count,
    SUM(CASE WHEN f.n_blitzers = 0 THEN 1 ELSE 0 END)   AS no_blitz_count,
    COUNT(*)                                            AS total_pass_plays,
    ROUND(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END), 4) AS blitz_rate
FROM competitive_plays cp
JOIN ftn_play f USING (game_id, play_id)
WHERE cp.play_type = 'pass'
GROUP BY cp.defteam, cp.season

UNION ALL

SELECT
    'LEAGUE'                                            AS defteam,
    cp.season,
    SUM(CASE WHEN f.n_blitzers > 0 THEN 1 ELSE 0 END)   AS blitz_count,
    SUM(CASE WHEN f.n_blitzers = 0 THEN 1 ELSE 0 END)   AS no_blitz_count,
    COUNT(*)                                            AS total_pass_plays,
    ROUND(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END), 4) AS blitz_rate
FROM competitive_plays cp
JOIN ftn_play f USING (game_id, play_id)
WHERE cp.play_type = 'pass'
GROUP BY cp.season

ORDER BY defteam, season;
