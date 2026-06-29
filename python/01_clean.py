import pandas as pd
import numpy as np

#Load the raw file
df = pd.read_csv("data/layoffs_raw.csv", low_memory=False)

#Always look at your data before touching it
print("Shape: ", df.shape)
print("\nColumn names: ", df.columns.to_list())
print("\nNull counts: \n", df.isnull().sum())
print("\nFirst 3 rows:\n", df.head(3))

#make all columns names lowercase with underscores - consistent and easy to type
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(r"[^a-z0-9_]","",regex=True)
)

# Rename specific columns to clearer names
df = df.rename(columns={
 "company": "company_name",
 "laid_off": "total_layoffs",
 "percentage": "pct_laid_off",
 "date_layoffs": "announced_date",
 "stage": "funding_stage",
 "money_raised_in__mil": "funds_raised_m",
})

from datetime import datetime
def parse_date_flexible(val):
    """Try multiple date formats until one works."""
    if pd.isna(val):
        return pd.NaT
    val = str(val).strip()
    formats_to_try = [
        "%Y-%m-%d", # 2022-11-04
        "%m/%d/%Y", # 11/04/2022
        "%d-%b-%Y", # 04-Nov-2022
        "%B %d, %Y", # November 4, 2022
        "%Y/%m/%d", # 2022/11/04
    ]
    for fmt in formats_to_try:
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return pd.NaT # none worked — return empty

df["announced_date"] = df["announced_date"].apply(parse_date_flexible)
df["announced_date"] = pd.to_datetime(df["announced_date"])
# Remove rows we can't place in time — useless for trend analysis
rows_before = len(df)
df = df.dropna(subset=["announced_date"])
print(f"Removed {rows_before - len(df)} rows with unparseable dates.")

def clean_number(val):
    """Handle '1,500', '1.5K', '2M', or plain numbers."""
    if pd.isna(val):
        return np.nan
    val = str(val).strip().replace(",", "").replace(" ", "")
    if val in ("", "-", "N/A", "Unknown", "none"):
        return np.nan
    try:
        if val.upper().endswith("K"):
            return float(val[:-1]) * 1_000
        if val.upper().endswith("M"):
            return float(val[:-1]) * 1_000_000
        return float(val)
    except ValueError:
        return np.nan
    df["total_layoffs"] = df["total_layoffs"].apply(clean_number)
    df["funds_raised_m"] = df["funds_raised_m"].apply(clean_number)


def clean_pct(val):
    if pd.isna(val):
        return np.nan
    val = str(val).strip().replace("%", "")
    try:
        pct = float(val)
        # If stored as a decimal (e.g. 0.15 meaning 15%)
        if pct <= 1.0:
            pct = pct * 100
        # Anything over 100% is a data error
        if pct > 100:
            return np.nan
        return round(pct, 2)
    except ValueError:
        return np.nan
df["pct_laid_off"] = df["pct_laid_off"].apply(clean_pct)

df["year"] = df["announced_date"].dt.year
df["month"] = df["announced_date"].dt.month
df["quarter"] = df["announced_date"].dt.to_period("Q").astype(str)

def layoff_severity(pct):
    if pd.isna(pct): return "Unknown"
    if pct < 5: return "Minor (<5%)"
    if pct < 15: return "Moderate (5-15%)"
    if pct < 30: return "Major (15-30%)"
    return "Severe (30%+)"

df["severity"] = df["pct_laid_off"].apply(layoff_severity)

df.to_csv("data/layoffs_clean.csv", index=False)
print(f"\nSaved {len(df)} clean rows to data/layoffs_clean.csv")
print(df.dtypes)