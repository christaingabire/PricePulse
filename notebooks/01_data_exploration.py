import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data 
df = pd.read_csv('../data_sources/raw/KEN_RTFP_mkt_2007_2025-06-30.csv')
metadata = pd.read_csv('../data_sources/raw/KEN_RTP_details_2007_2025-06-30.csv')

# Basic exploration
print("Dataset shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst few rows:")
print(df.head())

# Check the markets
print(f"\nNumber of unique markets: {df['mkt_name'].nunique()}")
print("Markets:", df['mkt_name'].unique())

# Check time range
print(f"\nDate range: {df['price_date'].min()} to {df['price_date'].max()}")

# Check commodities (non-null values)
commodities = ['maize', 'potatoes', 'sorghum']
for commodity in commodities:
    non_null_count = df[commodity].notna().sum()
    print(f"{commodity}: {non_null_count} observations")