import pandas as pd
import numpy as np
import yfinance as yf
import time
import os
import sys
from datetime import timedelta

TICKER_MAP = {
    "Amazon":     "AMZN",
    "Meta":       "META",
    "Google":     "GOOGL",
    "Alphabet":   "GOOGL",
    "Microsoft":  "MSFT",
    "Salesforce": "CRM",
    "Lyft":       "LYFT",
    "Uber":       "UBER",
    "Snap":       "SNAP",
    "Spotify":    "SPOT",
    "Netflix":    "NFLX",
    "Coinbase":   "COIN",
    "Robinhood":  "HOOD",
    "Peloton":    "PTON",
    "Zoom":       "ZM",
    "Shopify":    "SHOP",
    "Twilio":     "TWLO",
    "Palantir":   "PLTR",
    "Snowflake":  "SNOW",
    "Datadog":    "DDOG",
    "Intel":      "INTC",
    "Cisco":      "CSCO",
    "Oracle":     "ORCL",
    "Stripe":     None,   # private — skip
    "Klarna":     None,   # private — skip
}


def get_ticker(company_name):
    return TICKER_MAP.get(company_name.strip().title(), None)


def get_price_on_date(ticker, target_date, max_offset=5):
    """Fetch closing price on or just after target_date, skipping non-trading days."""
    for offset in range(max_offset):
        check = target_date + timedelta(days=offset)
        start = check.strftime("%Y-%m-%d")
        end   = (check + timedelta(days=1)).strftime("%Y-%m-%d")
        try:
            # Suppress yfinance's noisy "possibly delisted" stderr messages
            devnull    = open(os.devnull, "w")
            old_stderr = sys.stderr
            sys.stderr = devnull

            data = yf.download(ticker, start=start, end=end,
                               progress=False, auto_adjust=True)

            sys.stderr = old_stderr
            devnull.close()

            if data.empty:
                continue

            close = data["Close"]
            # Newer yfinance returns a MultiIndex DataFrame — flatten to a Series
            if hasattr(close, "columns") and isinstance(close.columns, pd.MultiIndex):
                close = close.iloc[:, 0]

            return float(close.iloc[0])

        except Exception:
            sys.stderr = old_stderr  # always restore stderr on error
            continue

    return None


# ── Load data ─────────────────────────────────────────────────
df = pd.read_csv("data/layoffs_clean.csv", parse_dates=["announced_date"])

# Print stage values so you can confirm the filter label matches your data
print("Unique funding_stage values:", df["funding_stage"].unique())

PUBLIC_STAGE_LABEL = "Post-IPO"
public_df = df[df["funding_stage"] == PUBLIC_STAGE_LABEL].copy()
print(f"\nEnriching {len(public_df)} public company events...")

results = []

for _, row in public_df.iterrows():
    company  = row["company_name"]
    ann_date = row["announced_date"]
    ticker   = get_ticker(company)

    # Skip rows where the date didn't parse correctly
    if pd.isnull(ann_date):
        print(f"  ⚠️  Skipping {company} — invalid date")
        continue

    record = {
        "company_name":   company,
        "announced_date": ann_date,
        "ticker":         ticker,
        "price_t0":       None,
        "price_t30":      None,
        "pct_change_30d": None,
        "data_quality":   "no_ticker" if not ticker else "pending",
    }

    if ticker:
        time.sleep(0.5)  # respect Yahoo Finance rate limit

        p0  = get_price_on_date(ticker, ann_date)
        p30 = get_price_on_date(ticker, ann_date + timedelta(days=30))

        # Use "is not None" — "if p0" would wrongly treat 0.0 as missing
        record["price_t0"]  = round(p0,  2) if p0  is not None else None
        record["price_t30"] = round(p30, 2) if p30 is not None else None

        if p0 is not None and p30 is not None:
            record["pct_change_30d"] = round((p30 - p0) / p0 * 100, 2)
            record["data_quality"]   = "complete"
        else:
            record["data_quality"] = "missing_price"

        print(f"  {company} ({ticker}): {record['pct_change_30d']}%")

    results.append(record)

# Merge stock data back onto the full dataset
stock_df = pd.DataFrame(results)

enriched = df.merge(
    stock_df[["company_name", "announced_date", "ticker",
              "price_t0", "price_t30", "pct_change_30d", "data_quality"]],
    on=["company_name", "announced_date"],
    how="left"
)

enriched.to_csv("data/layoffs_enriched.csv", index=False)
print(f"\nSaved enriched data → data/layoffs_enriched.csv")

# ── Summary ───────────────────────────────────────────────────
complete = enriched[enriched["data_quality"] == "complete"]
print(f"\n📊 Summary:")
print(f"  Total rows:          {len(enriched)}")
print(f"  Complete stock data: {len(complete)}")
if len(complete) > 0:
    print(f"  Avg 30d change:      {complete['pct_change_30d'].mean():.2f}%")
    positive = (complete["pct_change_30d"] > 0).sum()
    print(f"  Stock went UP:       {positive}/{len(complete)} events ({positive/len(complete)*100:.1f}%)")