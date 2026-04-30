-- ---
-- Question:    Does league pressure rate (n_pass_rushers >= 5) inside the 20 differ from pressure rate outside the 20?
-- Filter:      competitive_plays JOIN ftn_play, play_type='pass'. Field zone = red zone (yardline_100 <= 20) vs midfield (yardline_100 > 20).
-- Result shape: zone TEXT ('red_zone'|'midfield'), n_pass_plays INT, pressure_count INT, pressure_rate REAL
-- Hypothesis:  S2-H1 (league pressure rate inside the 20 differs from elsewhere by >= 5pp).
-- Caveats:     n_pass_rushers is NaN on run plays - filter to play_type='pass' first. Operational threshold n_pass_rushers >= 5 per docs/ftn-schema-audit.md.
-- N expected:  2 rows; with a ~57k pass-play universe, red zone has ~9k pass plays and midfield has ~48k.
-- ---

SELECT
    CASE WHEN cp.yardline_100 <= 20 THEN 'red_zone' ELSE 'midfield' END AS zone,
    COUNT(*)                                                AS n_pass_plays,
    SUM(CASE WHEN f.n_pass_rushers >= 5 THEN 1 ELSE 0 END)  AS pressure_count,
    ROUND(AVG(CASE WHEN f.n_pass_rushers >= 5 THEN 1.0 ELSE 0.0 END), 4) AS pressure_rate
FROM competitive_plays cp
JOIN ftn_play f USING (game_id, play_id)
WHERE cp.play_type = 'pass'
GROUP BY zone
ORDER BY zone;
