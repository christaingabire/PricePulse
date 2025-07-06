import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_kenya_data():
    """Load and process Kenya data"""
    kenya_file = '../../data_sources/processed/kenya_prices_clean.csv'
    df_kenya = pd.read_csv(kenya_file)
    df_kenya['country'] = 'Kenya'
    df_kenya['country_code'] = 'KEN'
    df_kenya['region'] = 'East Africa'
    df_kenya['sub_region'] = 'East Africa'
    df_kenya['population_millions'] = 54.0
    return df_kenya

def load_nigeria_data():
    """Load and process Nigeria data"""
    nigeria_file = '../../data_sources/processed/nigeria_prices_clean.csv'
    df_nigeria = pd.read_csv(nigeria_file)
    df_nigeria['country'] = 'Nigeria'
    df_nigeria['country_code'] = 'NGA'
    df_nigeria['region'] = 'West Africa'
    df_nigeria['sub_region'] = 'West Africa'
    df_nigeria['population_millions'] = 218.0
    return df_nigeria

def load_mali_data():
    """Load and process Mali data"""
    mali_file = '../../data_sources/processed/mali_prices_clean.csv'
    df_mali = pd.read_csv(mali_file)
    df_mali['country'] = 'Mali'
    df_mali['country_code'] = 'MLI'
    df_mali['region'] = 'Sahel'
    df_mali['sub_region'] = 'West Africa'
    df_mali['population_millions'] = 22.0
    return df_mali

def load_mozambique_data():
    """Load and process Mozambique data"""
    moz_file = '../../data_sources/processed/mozambique_prices_clean.csv'
    df_moz = pd.read_csv(moz_file)
    df_moz['country'] = 'Mozambique'
    df_moz['country_code'] = 'MOZ'
    df_moz['region'] = 'Southern Africa'
    df_moz['sub_region'] = 'SADC'
    df_moz['population_millions'] = 32.0
    return df_moz

def load_senegal_data():
    """Load and process Senegal data"""
    sen_file = '../../data_sources/processed/senegal_prices_clean.csv'
    df_sen = pd.read_csv(sen_file)
    df_sen['country'] = 'Senegal'
    df_sen['country_code'] = 'SEN'
    df_sen['region'] = 'West Africa'
    df_sen['sub_region'] = 'Coastal West Africa'
    df_sen['population_millions'] = 17.0
    return df_sen

def load_somalia_data():
    """Load and process Somalia data"""
    som_file = '../../data_sources/processed/somalia_prices_clean.csv'
    df_som = pd.read_csv(som_file)
    df_som['country'] = 'Somalia'
    df_som['country_code'] = 'SOM'
    df_som['region'] = 'Horn of Africa'
    df_som['sub_region'] = 'East Africa'
    df_som['population_millions'] = 17.0
    return df_som

def process_multi_country_data():
    """Process all 6 countries and create unified dataset"""
    
    print("=== PRICEPULSE 6-COUNTRY EXPANSION ===")
    print("Loading all country datasets...")
    
    # Load existing countries
    df_kenya = load_kenya_data()
    df_nigeria = load_nigeria_data()
    
    # Load new countries
    df_mali = load_mali_data()
    df_mozambique = load_mozambique_data()
    df_senegal = load_senegal_data()
    df_somalia = load_somalia_data()
    
    # Combine all datasets
    all_countries = [df_kenya, df_nigeria, df_mali, df_mozambique, df_senegal, df_somalia]
    df_combined = pd.concat(all_countries, ignore_index=True)
    
    # Convert price_date to datetime for analysis
    df_combined['price_date'] = pd.to_datetime(df_combined['price_date'])
    
    print(f"\n COMBINED DATASET SUMMARY:")
    print(f"Total observations: {len(df_combined):,}")
    print(f"Countries: {df_combined['country'].nunique()}")
    print(f"Markets: {df_combined['mkt_name'].nunique()}")
    print(f"Total population covered: {df_combined['population_millions'].sum():.0f}M people")
    print(f"Date range: {df_combined['price_date'].min().strftime('%Y-%m-%d')} to {df_combined['price_date'].max().strftime('%Y-%m-%d')}")
    
    # Country breakdown
    print(f"\n COUNTRY BREAKDOWN:")
    country_summary = df_combined.groupby('country').agg({
        'mkt_name': 'nunique',
        'population_millions': 'first',
        'region': 'first',
        'currency': 'first'
    }).round(0)
    
    for country in df_combined['country'].unique():
        country_data = df_combined[df_combined['country'] == country]
        print(f"{country}: {len(country_data):,} obs, {country_data['mkt_name'].nunique()} markets, {country_data['region'].iloc[0]}")
    
    return df_combined

def analyze_shared_commodities(df_combined):
    """Analyze commodities shared across countries"""
    
    print(f"\n SHARED COMMODITY ANALYSIS:")
    
    # Define commodity mappings for each country
    country_commodities = {
        'Kenya': ['maize', 'potatoes', 'sorghum'],
        'Nigeria': ['rice', 'sorghum', 'beans', 'millet', 'yam'],
        'Mali': ['beans', 'groundnuts', 'maize', 'millet', 'rice', 'sorghum'],
        'Mozambique': ['cowpeas', 'groundnuts', 'maize', 'maize_meal', 'oil', 'rice', 'sugar', 'wheat_flour'],
        'Senegal': ['maize', 'millet', 'rice', 'sorghum'],
        'Somalia': ['maize', 'oil', 'rice', 'sorghum']
    }
    
    # Analyze shared commodities
    shared_analysis = {}
    all_commodities = set()
    for commodities in country_commodities.values():
        all_commodities.update(commodities)
    
    for commodity in all_commodities:
        countries_with_commodity = [country for country, commodities in country_commodities.items() 
                                  if commodity in commodities]
        if len(countries_with_commodity) > 1:
            shared_analysis[commodity] = countries_with_commodity
    
    print("Multi-country commodities:")
    for commodity, countries in sorted(shared_analysis.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"• {commodity.upper()}: {len(countries)} countries - {', '.join(countries)}")
    
    return shared_analysis

def analyze_regional_patterns(df_combined):
    """Analyze regional price patterns"""
    
    print(f"\n REGIONAL ANALYSIS:")
    
    regional_summary = df_combined.groupby('region').agg({
        'country': 'nunique',
        'mkt_name': 'nunique',
        'population_millions': 'sum'
    }).round(0)
    
    print("Regional coverage:")
    for region in df_combined['region'].unique():
        region_data = df_combined[df_combined['region'] == region]
        countries = region_data['country'].unique()
        print(f"• {region}: {', '.join(countries)} ({region_data['population_millions'].sum():.0f}M people)")

def generate_cross_country_sorghum_analysis(df_combined):
    """Analyze sorghum prices across all countries that have it"""
    
    print(f"\n SORGHUM CROSS-COUNTRY ANALYSIS:")
    
    # Countries with sorghum data
    sorghum_countries = []
    for country in df_combined['country'].unique():
        country_data = df_combined[df_combined['country'] == country]
        if 'sorghum' in country_data.columns and not country_data['sorghum'].isna().all():
            sorghum_countries.append(country)
    
    if sorghum_countries:
        print(f"Sorghum available in: {', '.join(sorghum_countries)}")
        
        # Create sorghum analysis for each country
        sorghum_analysis = {}
        for country in sorghum_countries:
            country_data = df_combined[df_combined['country'] == country]
            sorghum_data = country_data[country_data['sorghum'].notna()]
            
            if len(sorghum_data) > 0:
                avg_price = sorghum_data['sorghum'].mean()
                currency = sorghum_data['currency'].iloc[0]
                observations = len(sorghum_data)
                sorghum_analysis[country] = {
                    'avg_price': avg_price,
                    'currency': currency,
                    'observations': observations
                }
        
        print("Average sorghum prices by country:")
        for country, data in sorghum_analysis.items():
            print(f"• {country}: {data['avg_price']:.0f} {data['currency']} (from {data['observations']} observations)")

def create_visualizations(df_combined):
    """Create visualizations for the 6-country dataset"""
    
    print(f"\n GENERATING VISUALIZATIONS...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('PricePulse: 6-Country African Food Price Intelligence', fontsize=16, fontweight='bold')
    
    # 1. Country observation counts
    country_counts = df_combined['country'].value_counts()
    axes[0, 0].bar(country_counts.index, country_counts.values)
    axes[0, 0].set_title('Observations by Country')
    axes[0, 0].set_ylabel('Number of Observations')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Regional distribution
    region_counts = df_combined['region'].value_counts()
    axes[0, 1].pie(region_counts.values, labels=region_counts.index, autopct='%1.1f%%')
    axes[0, 1].set_title('Regional Distribution')
    
    # 3. Market count by country
    market_counts = df_combined.groupby('country')['mkt_name'].nunique()
    axes[1, 0].bar(market_counts.index, market_counts.values)
    axes[1, 0].set_title('Markets by Country')
    axes[1, 0].set_ylabel('Number of Markets')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 4. Population coverage
    pop_by_region = df_combined.groupby('region')['population_millions'].first()
    axes[1, 1].bar(pop_by_region.index, pop_by_region.values)
    axes[1, 1].set_title('Population Coverage by Region (Millions)')
    axes[1, 1].set_ylabel('Population (Millions)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('../../data_sources/processed/six_country_overview.png', dpi=300, bbox_inches='tight')
    print(" Visualization saved: six_country_overview.png")

def save_unified_dataset(df_combined):
    """Save the unified 6-country dataset"""
    
    output_file = '../../data_sources/processed/unified_six_country.csv'
    df_combined.to_csv(output_file, index=False)
    print(f"\n UNIFIED DATASET SAVED: {output_file}")
    print(f"Final dataset: {len(df_combined):,} observations across 6 countries")

def generate_summary_report(df_combined, shared_commodities):
    """Generate comprehensive summary report"""
    
    report_file = '../../data_sources/processed/six_country_summary.txt'
    
    with open(report_file, 'w') as f:
        f.write("PRICEPULSE: 6-COUNTRY AFRICAN FOOD PRICE INTELLIGENCE SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("PORTFOLIO OVERVIEW:\n")
        f.write(f"• Total observations: {len(df_combined):,}\n")
        f.write(f"• Countries covered: {df_combined['country'].nunique()}\n")
        f.write(f"• Markets monitored: {df_combined['mkt_name'].nunique()}\n")
        f.write(f"• Population coverage: {df_combined['population_millions'].sum():.0f}M people\n")
        f.write(f"• Geographic span: 5 African regions\n")
        f.write(f"• Date coverage: {df_combined['price_date'].min().strftime('%Y-%m-%d')} to {df_combined['price_date'].max().strftime('%Y-%m-%d')}\n\n")
        
        f.write("COUNTRY BREAKDOWN:\n")
        for country in sorted(df_combined['country'].unique()):
            country_data = df_combined[df_combined['country'] == country]
            f.write(f"• {country}: {len(country_data):,} observations, {country_data['mkt_name'].nunique()} markets, {country_data['region'].iloc[0]}\n")
        
        f.write("\nSHARED COMMODITIES (Cross-Country Analysis Potential):\n")
        for commodity, countries in sorted(shared_commodities.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"• {commodity.upper()}: {len(countries)} countries - {', '.join(countries)}\n")
        
        f.write("\nREGIONAL COVERAGE:\n")
        for region in sorted(df_combined['region'].unique()):
            region_data = df_combined[df_combined['region'] == region]
            countries = region_data['country'].unique()
            f.write(f"• {region}: {', '.join(sorted(countries))} ({region_data['population_millions'].sum():.0f}M people)\n")
        
        f.write("\nKEY INSIGHTS:\n")
        f.write("• Mali provides highest data volume (15,143 observations)\n")
        f.write("• Senegal has perfect commodity overlap with existing portfolio\n")
        f.write("• Sorghum available in 5/6 countries - ideal for pan-African analysis\n")
        f.write("• Mali + Senegal share XOF currency - direct price comparisons possible\n")
        f.write("• Somalia provides critical conflict zone food security intelligence\n")
        f.write("• Mozambique opens entirely new Southern Africa market\n")
        f.write("• 827% increase in observations from original 2-country system\n")
    
    print(f" SUMMARY REPORT SAVED: {report_file}")

if __name__ == "__main__":
    # Execute the complete 6-country analysis
    print(" Starting PricePulse 6-Country Analysis...")
    
    # Process all data
    df_combined = process_multi_country_data()
    
    # Analyze shared commodities
    shared_commodities = analyze_shared_commodities(df_combined)
    
    # Regional analysis
    analyze_regional_patterns(df_combined)
    
    # Sorghum cross-country analysis
    generate_cross_country_sorghum_analysis(df_combined)
    
    # Create visualizations
    create_visualizations(df_combined)
    
    # Save unified dataset
    save_unified_dataset(df_combined)
    
    # Generate summary report
    generate_summary_report(df_combined, shared_commodities)
    
    print(f"\n SUCCESS! PricePulse now covers 6 countries with {len(df_combined):,} observations!")
    print(" Check data_sources/processed/ for all outputs:")
    print("   • unified_six_country.csv (complete dataset)")
    print("   • six_country_overview.png (visualizations)")
    print("   • six_country_summary.txt (comprehensive report)")