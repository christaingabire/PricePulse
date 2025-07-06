import pandas as pd
import numpy as np

def clean_nigeria_data(df):
    """Clean and process Nigeria food price data"""
    
    # Convert price_date to datetime
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    # Add derived columns
    df['year_month'] = df['price_date'].dt.to_period('M')
    
    # Nigeria commodities (from your file)
    commodity_cols = ['rice', 'sorghum', 'beans', 'millet', 'yam']
    
    # Filter out rows with no price data
    df_clean = df[df[commodity_cols].notna().any(axis=1)].copy()
    
    # Remove test/aggregated markets
    df_clean = df_clean[df_clean['mkt_name'] != 'Market Average']
    
    print(f"Original rows: {len(df)}")
    print(f"After cleaning: {len(df_clean)}")
    print(f"Markets after cleaning: {df_clean['mkt_name'].nunique()}")
    
    return df_clean

if __name__ == "__main__":
    # Load and clean data
    df = pd.read_csv('../../data_sources/raw/NGA_RTFP_mkt_2007_2025-06-30.csv')
    df_clean = clean_nigeria_data(df)
    
    # Save cleaned data
    df_clean.to_csv('../../data_sources/processed/nigeria_prices_clean.csv', index=False)
    print("Nigeria data cleaned and saved!")