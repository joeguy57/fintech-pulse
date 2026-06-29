# FintechPulse: Do Tech Layoffs Reward or Punish Companies on the Stock Market?

An end-to-end data pipeline that answers a genuinely interesting question using real public data: **when a tech company announces mass layoffs, does its stock price go up or down in the 30 days that follow?**

---

## What I Found

After enriching thousands of real layoff events with Yahoo Finance stock data and running them through a dbt pipeline on Databricks, the results were clear: **the market more often rewards layoffs than punishes them** — but the severity and industry both matter significantly.

Key findings from the SQL analysis:
- The majority of layoff announcements were followed by a stock price increase within 30 days
- Larger workforce cuts (Severe 30%+) tended to produce stronger market reactions — both positive and negative
- Fintech and cloud-infrastructure companies saw the most consistent positive reactions
- The trend shifted notably year-over-year, with 2022–2023 being the peak of both layoffs and market reward

---

## Stack

| Layer | Tool | Why |
|---|---|---|
| Data cleaning | Python (pandas, numpy) | Handles messy real-world CSVs |
| Stock prices | yfinance | Free Yahoo Finance API, no key needed |
| Cloud platform | Databricks Community Edition | Free Delta Lake + SQL Warehouse |
| Transformations | dbt (dbt-databricks) | Modular, tested, documented SQL |
| Analysis | Spark SQL | Window functions, aggregations |
| Visualizations | matplotlib | Charts produced in Databricks notebook |

---

## Project Structure

```
fintech-pulse/
├── data/
│   ├── layoffs_raw.csv          # Downloaded from Kaggle
│   ├── layoffs_clean.csv        # After 01_clean.py
│   └── layoffs_enriched.csv     # After 02_enrich.py (stock prices added)
├── python/
│   ├── 01_clean.py              # Cleans raw layoffs data
│   └── 02_enrich.py             # Adds 30-day stock price data
├── fintech_pulse/               # dbt project
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/
│       │   ├── stg_layoffs.sql
│       │   └── stg_layoffs.yml
│       └── marts/
│           ├── layoff_stock_reactions.sql
│           ├── industry_summary.sql
│           ├── yearly_trend.sql
│           └── marts.yml
├── sql/
│   └── analysis/
│       ├── headline_answer.sql
│       ├── severity_breakdown.sql
│       ├── industry_breakdown.sql
│       ├── yearly_trend.sql
│       ├── top10_gainers.sql
│       └── rolling_3m_avg.sql
├── notebooks/
│   └── layoff_stock_analysis.ipynb   # Databricks notebook with charts
└── README.md
```

---

## How to Run It

### 1. Prerequisites

- Python 3.11+
- A free [Databricks Community Edition](https://community.cloud.databricks.com) account
- A free [Kaggle](https://www.kaggle.com) account

### 2. Set up your environment

```bash
git clone https://github.com/YOUR_USERNAME/fintech-pulse.git
cd fintech-pulse
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install pandas numpy yfinance dbt-databricks
```

### 3. Get the data

Download `tech_layoffs.csv` from [Kaggle](https://www.kaggle.com/datasets/ulrikeherold/tech-layoffs-2020-2024), rename it to `layoffs_raw.csv`, and place it in the `data/` folder.

### 4. Clean and enrich

```bash
python python/01_clean.py       # produces data/layoffs_clean.csv
python python/02_enrich.py      # produces data/layoffs_enriched.csv (takes a few minutes)
```

### 5. Load into Databricks

Upload both CSVs via the Databricks SQL Editor → Create Table:

- Catalog: `hive_metastore`
- Database: `fintech_pulse`
- Tables: `layoffs_clean`, `layoffs_enriched`

### 6. Run dbt

```bash
cd fintech_pulse
dbt debug       # confirm connection is green
dbt run         # builds all 4 models
dbt test        # runs data quality checks
```

### 7. Explore in the notebook

Import `notebooks/layoff_stock_analysis.ipynb` into your Databricks workspace to run all 6 analysis queries and view the charts.

---

## dbt Models

```
stg_layoffs              (view)   — cleans & casts types from raw source
    └── layoff_stock_reactions   (table)  — one row per event, market reaction labels
            ├── industry_summary (table)  — aggregated returns by sector
            └── yearly_trend     (table)  — YoY deltas using LAG() window function
```

---

## Data Sources

- **Layoffs data:** [Tech layoffs 2020–2025 by Ulrike Herold](https://www.kaggle.com/datasets/ulrikeherold/tech-layoffs-2020-2024) — licensed under ODbL
- **Stock prices:** Yahoo Finance via `yfinance` (free, no API key required)