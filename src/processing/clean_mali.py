import pandas as pd
import numpy as np

def clean_mali_data(df):
    """Clean and process Mali food price data"""
    
    # Convert price_date to datetime
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    # Add derived columns
    df['year_month'] = df['price_date'].dt.to_period('M')
    
    # Mali commodities (from your data structure)
    commodity_cols = ['beans', 'groundnuts', 'maize', 'millet', 'rice', 'sorghum']
    
    # Filter out rows with no price data
    df_clean = df[df[commodity_cols].notna().any(axis=1)].copy()
    
    # Remove test/aggregated markets
    df_clean = df_clean[df_clean['mkt_name'] != 'Market Average']
    
    print(f"Original rows: {len(df)}")
    print(f"After cleaning: {len(df_clean)}")
    print(f"Markets after cleaning: {df_clean['mkt_name'].nunique()}")
    print(f"Commodities available: {[col for col in commodity_cols if not df_clean[col].isna().all()]}")
    
    # Display sample of market names
    print(f"Sample markets: {df_clean['mkt_name'].unique()[:5].tolist()}")
    
    return df_clean

def get_mali_market_summary(df):
    """Get summary statistics by market for Mali"""
    
    summary = df.groupby('mkt_name').agg({
        'beans': ['count', 'mean', 'std'],
        'groundnuts': ['count', 'mean', 'std'], 
        'maize': ['count', 'mean', 'std'],
        'millet': ['count', 'mean', 'std'],
        'rice': ['count', 'mean', 'std'],
        'sorghum': ['count', 'mean', 'std'],
        'price_date': ['min', 'max']
    }).round(2)
    
    return summary

if __name__ == "__main__":
    # Load and clean data
    print("=== PROCESSING MALI DATA ===")
    df = pd.read_csv('../../data_sources/raw/MLI_RTFP_mkt_2007_2025-06-30.csv')
    df_clean = clean_mali_data(df)
    
    # Get summary
    summary = get_mali_market_summary(df_clean)
    print("\nMarket Summary (first 5 markets):")
    print(summary.head())
    
    # Additional analysis
    print(f"\nCurrency: {df_clean['currency'].unique()}")
    print(f"Date range: {df_clean['price_date'].min()} to {df_clean['price_date'].max()}")
    print(f"Administrative regions: {df_clean['adm1_name'].nunique()}")
    
    # Commodity availability analysis
    print("\nCommodity Data Availability:")
    for commodity in ['beans', 'groundnuts', 'maize', 'millet', 'rice', 'sorghum']:
        non_null_count = df_clean[commodity].notna().sum()
        percentage = (non_null_count / len(df_clean)) * 100
        print(f"{commodity}: {non_null_count:,} observations ({percentage:.1f}%)")
    
    # Save cleaned data
    df_clean.to_csv('../../data_sources/processed/mali_prices_clean.csv', index=False)
    print("\n Mali data cleaned and saved!")
    print(f"Final dataset: {len(df_clean):,} rows across {df_clean['mkt_name'].nunique()} markets")