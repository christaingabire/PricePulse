import pandas as pd
import numpy as np

def clean_somalia_data(df):
    """Clean and process Somalia food price data"""
    
    # Convert price_date to datetime
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    # Add derived columns
    df['year_month'] = df['price_date'].dt.to_period('M')
    
    # Somalia commodities (from your data structure)
    commodity_cols = ['maize', 'oil', 'rice', 'sorghum']
    
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

def get_somalia_market_summary(df):
    """Get summary statistics by market for Somalia"""
    
    summary = df.groupby('mkt_name').agg({
        'maize': ['count', 'mean', 'std'],
        'oil': ['count', 'mean', 'std'],
        'rice': ['count', 'mean', 'std'],
        'sorghum': ['count', 'mean', 'std'],
        'price_date': ['min', 'max']
    }).round(2)
    
    return summary

if __name__ == "__main__":
    # Load and clean data
    print("=== PROCESSING SOMALIA DATA ===")
    df = pd.read_csv('../../data_sources/raw/SOM_RTFP_mkt_2007_2025-06-30.csv')
    df_clean = clean_somalia_data(df)
    
    # Get summary
    summary = get_somalia_market_summary(df_clean)
    print("\nMarket Summary (first 5 markets):")
    print(summary.head())
    
    # Additional analysis
    print(f"\nCurrency: {df_clean['currency'].unique()}")
    print(f"Date range: {df_clean['price_date'].min()} to {df_clean['price_date'].max()}")
    print(f"Administrative regions: {df_clean['adm1_name'].nunique()}")
    
    # Commodity availability analysis
    print("\nCommodity Data Availability:")
    for commodity in ['maize', 'oil', 'rice', 'sorghum']:
        non_null_count = df_clean[commodity].notna().sum()
        percentage = (non_null_count / len(df_clean)) * 100
        print(f"{commodity}: {non_null_count:,} observations ({percentage:.1f}%)")
    
    # Cross-country compatibility check
    print("\n Cross-Country Commodity Overlap:")
    shared_commodities = []
    if not df_clean['maize'].isna().all():
        shared_commodities.append("maize (with Kenya)")
    if not df_clean['rice'].isna().all():
        shared_commodities.append("rice (with Nigeria)")
    if not df_clean['sorghum'].isna().all():
        shared_commodities.append("sorghum (with Kenya & Nigeria)")
    
    print(f"Shared commodities: {', '.join(shared_commodities)}")
    print("  CONFLICT ZONE: Somalia data is critical for food security monitoring in crisis areas")
    
    # Save cleaned data
    df_clean.to_csv('../../data_sources/processed/somalia_prices_clean.csv', index=False)
    print("\n Somalia data cleaned and saved!")
    print(f"Final dataset: {len(df_clean):,} rows across {df_clean['mkt_name'].nunique()} markets")