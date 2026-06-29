-- layoff_stock_reactions.sql
-- One row per layoff event for public companies with complete stock data.
-- Adds market reaction labels for easy analysis.
WITH base AS (
    SELECT * FROM {{ ref('stg_layoffs') }}
    WHERE data_quality = 'complete'
)

SELECT
    company_name,
    ticker,
    industry,
    country,
    funding_stage,
    severity,
    announced_date,
    year,
    quarter,
    total_layoffs,
    pct_laid_off,
    price_t0,
    price_t30,
    pct_change_30d,
    stock_went_up,
    -- Human-readable label for what the market did
    CASE
        WHEN pct_change_30d > 5 THEN 'Strong Reward (>+5%)'
        WHEN pct_change_30d > 0 THEN 'Mild Reward (0-5%)'
        WHEN pct_change_30d > -5 THEN 'Mild Punishment (0-5%)'
        ELSE 'Strong Punishment (<-5%)'
    END AS market_reaction,
    -- Alpha: return above the typical market baseline of ~0.5%/month
    ROUND(pct_change_30d - 0.5, 2) AS alpha_vs_market
FROM base