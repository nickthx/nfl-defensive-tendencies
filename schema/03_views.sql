-- schema/03_views.sql -- project-wide single source of truth for play-type
-- and win-probability filtering across every analytical query (SCHEMA-03).
--
-- Locked predicate set per .planning/phases/02-data-layer-etl-sqlite-schema/02-CONTEXT.md:
--   D-01: Q4 crunch time stays IN (the wp filter already removes blowouts).
--   D-02: 2-minute drill cutoff is END-OF-HALF ONLY (qtr IN (2,4) AND half_seconds_remaining <= 120).
--   D-03: This is a VIEW, not a materialized table -- always reflects underlying plays.
--   D-04: Play classification uses play_type ONLY (sacks count as play_type='pass'
--         and ARE meaningful for blitz analysis; strict attempt-mode classification
--         would silently drop them -- see PITFALLS.md #7).
--
-- Every analytical query in queries/ MUST read from this view, not from plays.
-- See PITFALLS.md #6 (garbage-time) and #7 (no_play contamination).

CREATE VIEW competitive_plays AS
SELECT *
FROM plays
WHERE play_type IN ('pass','run')
  AND wp BETWEEN 0.05 AND 0.95
  AND qtr <= 4                                              -- exclude OT
  AND NOT (qtr IN (2,4) AND half_seconds_remaining <= 120)  -- exclude end-of-half hurry-up
;
