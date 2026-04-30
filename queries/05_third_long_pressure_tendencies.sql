-- ---
-- Question:    On 3rd-and-long pass plays, what is each team's blitz rate (n_blitzers > 0) AND extra-rusher rate (n_pass_rushers >= 5)?
-- Filter:      competitive_plays JOIN ftn_play; down=3 AND ydstogo>=7 AND play_type='pass' (S1 deep-dive).
-- Result shape: defteam TEXT, n_pass_plays INT, blitz_count INT, blitz_rate REAL, extra_rusher_count INT, extra_rusher_rate REAL
-- Hypothesis:  S1-H1 (league blitz rate on 3rd-and-long > 35%); S1-H2 (>=3 teams blitz > 50%).
-- Caveats:     S1 universe is ~9.9k competitive plays (Phase 2 verified). FTN n_blitzers counts extra rushers beyond the base front; n_blitzers > 0 is the blitz indicator for this dataset. Per-team N averages ~78 plays/team/season - some teams may fall below N>=100 for the "extreme" claim threshold; min_n_filter applies in the notebook.
-- N expected:  ~32 rows.
-- ---

SELECT
    cp.defteam,
    COUNT(*)                                                AS n_pass_plays,
    SUM(CASE WHEN f.n_blitzers > 0 THEN 1 ELSE 0 END)       AS blitz_count,
    ROUND(AVG(CASE WHEN f.n_blitzers > 0 THEN 1.0 ELSE 0.0 END), 4)       AS blitz_rate,
    SUM(CASE WHEN f.n_pass_rushers >= 5 THEN 1 ELSE 0 END)  AS extra_rusher_count,
    ROUND(AVG(CASE WHEN f.n_pass_rushers >= 5 THEN 1.0 ELSE 0.0 END), 4)  AS extra_rusher_rate
FROM competitive_plays cp
JOIN ftn_play f USING (game_id, play_id)
WHERE cp.down = 3 AND cp.ydstogo >= 7
  AND cp.play_type = 'pass'
GROUP BY cp.defteam
ORDER BY blitz_rate DESC;
