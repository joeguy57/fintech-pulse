-- industry_summary.sql
-- Aggregated stock performance by industry.
-- Answers: "Which sectors see the biggest post-layoff bounces?"
WITH reactions AS (
    SELECT * FROM {{ ref('layoff_stock_reactions') }}
)

SELECT
    industry,
    COUNT(*) AS total_events,
    SUM(total_layoffs) AS total_jobs_cut,
    ROUND(AVG(pct_change_30d), 2) AS avg_30d_return,
    ROUND(PERCENTILE_APPROX(pct_change_30d, 0.5), 2) AS median_30d_return,
    ROUND(MAX(pct_change_30d), 2) AS best_30d,
    ROUND(MIN(pct_change_30d), 2) AS worst_30d,
    ROUND(
    AVG(CASE WHEN stock_went_up THEN 1.0 ELSE 0.0 END) * 100, 1) 
FROM reactions
GROUP BY industry
HAVING COUNT(*) >= 3 -- only show industries with enough data
ORDER BY avg_30d_return DESC