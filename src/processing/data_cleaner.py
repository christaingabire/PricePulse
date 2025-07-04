import pandas as pd
import numpy as np

def clean_kenya_data(df):
    """Clean and process Kenya food price data"""
    
    # Convert price_date to datetime
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    # Add derived columns
    df['year_month'] = df['price_date'].dt.to_period('M')
    
    # Filter out rows with no price data
    commodity_cols = ['maize', 'potatoes', 'sorghum']
    df_clean = df[df[commodity_cols].notna().any(axis=1)].copy()
    
    # Remove test/aggregated markets
    df_clean = df_clean[df_clean['mkt_name'] != 'Market Average']
    
    print(f"Original rows: {len(df)}")
    print(f"After cleaning: {len(df_clean)}")
    print(f"Markets after cleaning: {df_clean['mkt_name'].nunique()}")
    
    return df_clean

def get_market_summary(df):
    """Get summary statistics by market"""
    
    summary = df.groupby('mkt_name').agg({
        'maize': ['count', 'mean', 'std'],
        'potatoes': ['count', 'mean', 'std'],
        'sorghum': ['count', 'mean', 'std'],
        'price_date': ['min', 'max']
    }).round(2)
    
    return summary

if __name__ == "__main__":
    # Load and clean data
    df = pd.read_csv('../../data_sources/raw/KEN_RTFP_mkt_2007_2025-06-30.csv')
    df_clean = clean_kenya_data(df)
    
    # Get summary
    summary = get_market_summary(df_clean)
    print("\nMarket Summary:")
    print(summary.head())
    
    # Save cleaned data
    df_clean.to_csv('../../data_sources/processed/kenya_prices_clean.csv', index=False)