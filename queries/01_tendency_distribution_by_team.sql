-- ---
-- Question:    What is each defense's blitz rate (n_blitzers > 0 on pass plays) versus the league baseline, 2022-2025?
-- Filter:      competitive_plays JOIN ftn_play, play_type='pass'.
-- Result shape: defteam TEXT, n_pass_plays INT, blitz_count INT, blitz_rate REAL, league_blitz_rate REAL, deviation_pp REAL
-- Hypothesis:  n/a (rollup material; KL-from-league input for STAT-04 predictability index)
-- Caveats:     n_blitzers is NaN on run plays - filter to play_type='pass' BEFORE applying the > 0 predicate. FTN n_blitzers counts EXTRA rushers beyond the base front (0=standard rush, 1+=blitz). A nflfastR-style total-rusher threshold applied to this FTN column was calibrated for a different encoding; n_blitzers > 0 is the correct blitz indicator for this dataset. Teams with N<100 are still emitted here; the notebook applies min_n_filter for claim-level use.
-- N expected:  ~32 rows (one per defteam) over a ~57k pass-play universe. League blitz rate ~30%.
-- ---

SELECT
    cp.defteam,
    COUNT(*)                                            AS n_pass_plays,
    SUM(CASE WHEN f.n_blitzers > 0 THEN 1 ELSE 0 END)   AS blitz_count,
    ROUND(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END), 4) AS blitz_rate,
    ROUND(AVG(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END))
              OVER (), 4)                               AS league_blitz_rate,
    ROUND(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END)
            - AVG(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END)) OVER (), 4)
                                                        AS deviation_pp
FROM competitive_plays cp
JOIN ftn_play f USING (game_id, play_id)
WHERE cp.play_type = 'pass'
GROUP BY cp.defteam
ORDER BY blitz_rate DESC;
