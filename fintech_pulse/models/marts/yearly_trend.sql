-- yearly_trend.sql
-- Year-over-year summary of layoff activity and stock reactions.
-- Uses LAG() window function to compare each year to the previous one.
WITH yearly AS (
    SELECT
        year,
        COUNT(*) AS events,
        SUM(total_layoffs) AS total_jobs_cut,
        ROUND(AVG(pct_change_30d), 2) AS avg_30d_return,
        ROUND(
        AVG(CASE WHEN stock_went_up THEN 1.0 ELSE 0.0 END) * 100, 1) AS pct_rewarded
    FROM {{ ref('layoff_stock_reactions') }}
    GROUP BY year
)
SELECT
    year,
    events,
    total_jobs_cut,
    avg_30d_return,
    pct_rewarded,
    -- How did this year compare to last year?
    ROUND(
    avg_30d_return - LAG(avg_30d_return) OVER (ORDER BY year), 2) AS yoy_return_delta,
    ROUND(
    pct_rewarded - LAG(pct_rewarded) OVER (ORDER BY year), 1) AS yoy_pct_rewarded_delta
FROM yearly
ORDER BY year