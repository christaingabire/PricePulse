import pandas as pd
import numpy as np

def clean_mozambique_data(df):
    """Clean and process Mozambique food price data"""
    
    # Convert price_date to datetime
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    # Add derived columns
    df['year_month'] = df['price_date'].dt.to_period('M')
    
    # Mozambique commodities (from your data structure)
    commodity_cols = ['cowpeas', 'groundnuts', 'maize', 'maize_meal', 'oil', 'rice', 'sugar', 'wheat_flour']
    
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

def get_mozambique_market_summary(df):
    """Get summary statistics by market for Mozambique"""
    
    summary = df.groupby('mkt_name').agg({
        'cowpeas': ['count', 'mean', 'std'],
        'groundnuts': ['count', 'mean', 'std'], 
        'maize': ['count', 'mean', 'std'],
        'maize_meal': ['count', 'mean', 'std'],
        'oil': ['count', 'mean', 'std'],
        'rice': ['count', 'mean', 'std'],
        'sugar': ['count', 'mean', 'std'],
        'wheat_flour': ['count', 'mean', 'std'],
        'price_date': ['min', 'max']
    }).round(2)
    
    return summary

if __name__ == "__main__":
    # Load and clean data
    print("=== PROCESSING MOZAMBIQUE DATA ===")
    df = pd.read_csv('../../data_sources/raw/MOZ_RTFP_mkt_2007_2025-06-30.csv')
    df_clean = clean_mozambique_data(df)
    
    # Get summary
    summary = get_mozambique_market_summary(df_clean)
    print("\nMarket Summary (first 5 markets):")
    print(summary.head())
    
    # Additional analysis
    print(f"\nCurrency: {df_clean['currency'].unique()}")
    print(f"Date range: {df_clean['price_date'].min()} to {df_clean['price_date'].max()}")
    print(f"Administrative regions: {df_clean['adm1_name'].nunique()}")
    
    # Commodity availability analysis
    print("\nCommodity Data Availability:")
    commodities = ['cowpeas', 'groundnuts', 'maize', 'maize_meal', 'oil', 'rice', 'sugar', 'wheat_flour']
    for commodity in commodities:
        non_null_count = df_clean[commodity].notna().sum()
        percentage = (non_null_count / len(df_clean)) * 100
        print(f"{commodity}: {non_null_count:,} observations ({percentage:.1f}%)")
    
    # Cross-country compatibility check
    print("\n🔗 Cross-Country Commodity Overlap:")
    shared_commodities = []
    if not df_clean['maize'].isna().all():
        shared_commodities.append("maize (with Kenya)")
    if not df_clean['rice'].isna().all():
        shared_commodities.append("rice (with Nigeria)")
    
    print(f"Shared commodities: {', '.join(shared_commodities)}")
    
    # Save cleaned data
    df_clean.to_csv('../../data_sources/processed/mozambique_prices_clean.csv', index=False)
    print("\n Mozambique data cleaned and saved!")
    print(f"Final dataset: {len(df_clean):,} rows across {df_clean['mkt_name'].nunique()} markets")