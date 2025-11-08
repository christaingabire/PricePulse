# src/multi_country/build_unified.py

from pathlib import Path
import pandas as pd
import numpy as np

# ---------- Step 1: locate processed CSVs ----------
PROC = Path("data_sources/processed")
files = list(PROC.glob("*_prices_clean.csv"))

dfs = []
for f in files:
    df = pd.read_csv(f)
    df.columns = [c.strip().lower() for c in df.columns]

    # rename common columns for consistency
    possible_commodity_cols = [
        "commodity", "item", "item_name", "product", "product_name", "crop"
    ]
    for col in possible_commodity_cols:
        if col in df.columns:
            df = df.rename(columns={col: "commodity"})
            break

    possible_price_cols = ["price_local", "price", "value"]
    for col in possible_price_cols:
        if col in df.columns:
            df = df.rename(columns={col: "price_local"})
            break

    if "country" not in df.columns:
        country = f.stem.replace("_prices_clean", "").capitalize()
        df["country"] = country

    dfs.append(df)
    print(f" Processed {f.name} ({len(df):,} rows)")

# ---------- Step 2: merge all countries ----------
if not dfs:
    print(" No *_prices_clean.csv files found.")
    raise SystemExit

merged = pd.concat(dfs, ignore_index=True)

# ---------- Step 3: reshape from wide to long ----------

# Try to detect which column is the date column (different countries label it differently)
possible_date_cols = ["date", "price_date", "recorded_date", "observation_date", "year_month"]
date_col = None
for c in possible_date_cols:
    if c in merged.columns:
        date_col = c
        break

if date_col is None:
    raise KeyError("No date column found in merged data. Expected one of: " + ", ".join(possible_date_cols))

print(f" Using '{date_col}' as date column")

id_vars = ["country", date_col]
if "mkt_name" in merged.columns:
    id_vars.append("mkt_name")

# Pick numeric columns to melt (exclude id_vars)
value_vars = [c for c in merged.columns if c not in id_vars and merged[c].dtype != "O"]

melted = merged.melt(
    id_vars=id_vars,
    value_vars=value_vars,
    var_name="commodity",
    value_name="price_local"
)

# rename the detected date column to 'date' for consistency
melted = melted.rename(columns={date_col: "date"})


# ---------- Step 4: add 2019=100 index ----------
melted["date"] = pd.to_datetime(melted["date"], errors="coerce")
melted = melted.dropna(subset=["date"])
melted["year"] = melted["date"].dt.year

base_year = 2019
base = (
    melted[melted["year"] == base_year]
    .groupby(["country", "commodity"], as_index=False)["price_local"]
    .mean()
    .rename(columns={"price_local": "base_price"})
)

melted = melted.merge(base, on=["country", "commodity"], how="left")
melted["price_index"] = np.where(
    (melted["base_price"].notna()) & (melted["base_price"] > 0),
    (melted["price_local"] / melted["base_price"]) * 100,
    np.nan
)

# ---------- Step 5: save ----------
out_path = PROC / "unified_multi_country.csv"
melted.to_csv(out_path, index=False)
print(f"\n Unified dataset saved to {out_path}")
print(f" Columns: {melted.columns.tolist()}")
print(f" Rows: {len(melted):,}")
