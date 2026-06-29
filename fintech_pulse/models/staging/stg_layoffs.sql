-- stg_layoffs.sql
-- Staging model: select and lightly clean the enriched source table.
-- We reference source tables using the source() function so dbt
-- can track lineage (where data comes from).
WITH source AS (
 SELECT * FROM {{ source('fintech_pulse', 'layoffs_enriched') }}
),
cleaned AS (
    SELECT
        company_name,
        industry,
        country,
        funding_stage,
        severity,
        announced_date,
        year,
        quarter,
        -- Cast to correct types (inferSchema sometimes gets these wrong)
        CAST(total_layoffs AS BIGINT) AS total_layoffs,
        CAST(pct_laid_off AS DOUBLE) AS pct_laid_off,
        CAST(funds_raised_m AS DOUBLE) AS funds_raised_m,
        -- Stock price columns
        ticker,
        CAST(price_t0 AS DOUBLE) AS price_t0,
        CAST(price_t30 AS DOUBLE) AS price_t30,
        CAST(pct_change_30d AS DOUBLE) AS pct_change_30d,
        data_quality,
        -- Useful flag: did the stock go up?
        CASE
            WHEN CAST(pct_change_30d AS DOUBLE) > 0 THEN TRUE
            WHEN CAST(pct_change_30d AS DOUBLE) < 0 THEN FALSE
            ELSE NULL
        END AS stock_went_up
    FROM source
    WHERE company_name IS NOT NULL
    AND announced_date IS NOT NULL
)
SELECT * FROM cleaned