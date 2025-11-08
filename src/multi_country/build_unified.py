# src/multi_country/build_unified.py
from pathlib import Path
import pandas as pd

PROC = Path("data_sources/processed")
files = list(PROC.glob("*_prices_clean.csv"))

dfs = []
for f in files:
    df = pd.read_csv(f)
    df.columns = [c.strip().lower() for c in df.columns]

    #  Fix commodity naming 
    # Try to detect commodity-like columns and rename to "commodity"
    possible_commodity_cols = [
        "commodity", "item", "item_name", "product", "product_name", "crop", "food"
    ]
    for col in possible_commodity_cols:
        if col in df.columns:
            df = df.rename(columns={col: "commodity"})
            break
    if "commodity" not in df.columns:
        df["commodity"] = "Unknown"

    # --- Fix price naming ---
    possible_price_cols = ["price_local", "price", "value", "price_usd", "average_price"]
    for col in possible_price_cols:
        if col in df.columns:
            df = df.rename(columns={col: "price_local"})
            break

    # --- Fix date naming ---
    possible_date_cols = ["price_date", "date", "recorded_date", "observation_date"]
    for col in possible_date_cols:
        if col in df.columns:
            df = df.rename(columns={col: "date"})
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            break

    # --- Add country column if missing ---
    if "country" not in df.columns:
        country = f.stem.replace("_prices_clean", "").capitalize()
        df["country"] = country

    dfs.append(df)
    print(f" Processed {f.name} ({len(df):,} rows)")

# --- Combine all ---
if dfs:
    out = pd.concat(dfs, ignore_index=True)

    # -----------------------------------------------
    # Melt wide commodity columns (e.g., maize, millet, rice...) into long format
    # -----------------------------------------------
    # Identify all possible commodity columns (numerical price columns)
    id_vars = ["country", "date", "mkt_name"] if "mkt_name" in out.columns else ["country", "date"]
    value_vars = [c for c in out.columns if c not in id_vars and out[c].dtype != 'O']  # all numeric columns

    # Melt wide -> long
    melted = out.melt(
        id_vars=id_vars,
        value_vars=value_vars,
        var_name="commodity",
        value_name="price_local"
    )

    # Drop missing values
    melted = melted.dropna(subset=["price_local"])
    melted = melted[melted["price_local"] > 0]

    # Save reshaped data
    melted.to_csv(PROC / "unified_multi_country.csv", index=False)
    print(f"\n Unified dataset reshaped to long format with {len(melted):,} rows.")
    print(" Columns:", melted.columns.tolist())
else:
    print(" No country files found in processed/ folder.")

