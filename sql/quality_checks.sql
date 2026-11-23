-- Illustrative relational quality checks for a future SQL/dbt-compatible metric layer.
-- This is NOT connected to Pew systems and does not require dbt to run the app.
-- Grant only read access to approved aggregated communications metrics.
-- This file expresses invariants; adjust table names to your authorized warehouse.

-- 1. Source + metric + period + platform must uniquely identify a row.
SELECT portfolio_id, platform, source, metric, period_start, period_end, COUNT(*) AS repeated
FROM communications_aggregate_metrics
GROUP BY portfolio_id, platform, source, metric, period_start, period_end
HAVING COUNT(*) > 1;

-- 2. Aggregate counts cannot be negative.
SELECT * FROM communications_aggregate_metrics WHERE value < 0;

-- 3. Required provenance must not be empty.
SELECT * FROM communications_aggregate_metrics
WHERE source IS NULL OR TRIM(source) = ''
   OR metric IS NULL OR TRIM(metric) = ''
   OR period_start IS NULL OR period_end IS NULL;

-- 4. Never sum sessions, impressions and post engagements into one measure:
--    group by source + metric + period before aggregation.
SELECT portfolio_id, platform, source, metric, period_start, period_end,
       SUM(value) AS metric_total
FROM communications_aggregate_metrics
GROUP BY portfolio_id, platform, source, metric, period_start, period_end;
