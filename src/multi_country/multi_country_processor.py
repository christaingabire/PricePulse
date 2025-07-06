import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import os

class MultiCountryFoodPriceAnalyzer:
    """Unified processor for multiple African countries food price data"""
    
    def __init__(self, base_path=None):
        # Find the project root directory (where data_sources folder is)
        if base_path is None:
            current_file = Path(__file__).resolve()
            # Go up directories until we find data_sources folder
            project_root = current_file.parent
            while not (project_root / 'data_sources').exists() and project_root.parent != project_root:
                project_root = project_root.parent
            self.base_path = project_root / 'data_sources'
        else:
            self.base_path = Path(base_path)
            
        self.countries = {}
        self.unified_data = None
        
        # Create output directories
        self.processed_dir = self.base_path / 'processed'
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
    def add_country_data(self, country_code, file_path, country_name):
        """Add a new country's data to the analysis"""
        print(f"Loading {country_name} data from {file_path}...")
        
        # Handle relative paths from project root
        if not Path(file_path).is_absolute():
            # If it's a relative path, make it relative to project root
            project_root = self.base_path.parent
            full_path = project_root / file_path
        else:
            full_path = Path(file_path)
        
        try:
            df = pd.read_csv(full_path)
            df['country_code'] = country_code
            df['country_name'] = country_name
            df['price_date'] = pd.to_datetime(df['price_date'])
            
            # Standardize commodity columns (World Bank RTFP format)
            commodity_cols = ['maize', 'rice', 'sorghum', 'wheat', 'potatoes', 'beans']
            available_commodities = [col for col in commodity_cols if col in df.columns]
            
            print(f"   Available commodities: {available_commodities}")
            
            # Filter to rows with price data
            if available_commodities:
                price_filter = df[available_commodities].notna().any(axis=1)
                df_clean = df[price_filter].copy()
            else:
                print(f"   No standard commodity columns found in {country_name} data")
                return None
            
            # Store country info
            self.countries[country_code] = {
                'data': df_clean,
                'name': country_name,
                'markets': df_clean['mkt_name'].nunique(),
                'commodities': available_commodities,
                'date_range': (df_clean['price_date'].min(), df_clean['price_date'].max()),
                'observations': len(df_clean)
            }
            
            print(f"   {country_name}: {len(df_clean)} observations, {df_clean['mkt_name'].nunique()} markets")
            print(f"   Date range: {df_clean['price_date'].min().strftime('%Y-%m')} to {df_clean['price_date'].max().strftime('%Y-%m')}")
            
            return df_clean
            
        except FileNotFoundError:
            print(f"   Error: File not found: {full_path}")
            return None
        except Exception as e:
            print(f"   Error loading {country_name} data: {str(e)}")
            return None
    
    def create_unified_dataset(self):
        """Combine all country data into unified format"""
        if not self.countries:
            print("No country data loaded. Add countries first!")
            return None
            
        print(f"\nCreating unified dataset from {len(self.countries)} countries...")
        all_data = []
        
        for country_code, country_info in self.countries.items():
            df = country_info['data'].copy()
            
            # Melt commodity columns to long format for easier analysis
            commodity_cols = country_info['commodities']
            
            # Select essential columns that should exist
            id_vars = ['country_code', 'country_name', 'mkt_name', 'price_date']
            
            # Add geographic columns if they exist
            if 'lat' in df.columns:
                id_vars.append('lat')
            if 'lon' in df.columns:
                id_vars.append('lon')
            
            df_melted = pd.melt(
                df, 
                id_vars=id_vars,
                value_vars=commodity_cols,
                var_name='commodity',
                value_name='price_local'
            )
            
            # Remove null prices
            df_melted = df_melted[df_melted['price_local'].notna()]
            all_data.append(df_melted)
        
        self.unified_data = pd.concat(all_data, ignore_index=True)
        
        print(f"Unified dataset created:")
        print(f"   {len(self.unified_data)} total price observations")
        print(f"   {self.unified_data['country_name'].nunique()} countries")
        print(f"   {self.unified_data['commodity'].nunique()} commodities")
        print(f"   {self.unified_data['mkt_name'].nunique()} unique markets")
        
        # Save unified dataset
        unified_path = self.processed_dir / 'unified_multi_country.csv'
        self.unified_data.to_csv(unified_path, index=False)
        print(f"   Saved to: {unified_path}")
        
        return self.unified_data
    
    def cross_country_analysis(self):
        """Perform cross-country price analysis"""
        if self.unified_data is None:
            print("Creating unified dataset first...")
            self.create_unified_dataset()
        
        print(f"\n{'='*60}")
        print("CROSS-COUNTRY FOOD PRICE ANALYSIS")
        print(f"{'='*60}")
        
        # Average prices by country and commodity
        avg_prices = self.unified_data.groupby(['country_name', 'commodity'])['price_local'].agg([
            'mean', 'std', 'count'
        ]).round(2)
        
        print(f"\nAVERAGE PRICES BY COUNTRY:")
        print(avg_prices)
        
        # Price volatility comparison
        volatility = self.unified_data.groupby(['country_name', 'commodity'])['price_local'].std().reset_index()
        volatility_pivot = volatility.pivot(index='commodity', columns='country_name', values='price_local')
        
        print(f"\nPRICE VOLATILITY COMPARISON (Standard Deviation):")
        print(volatility_pivot.round(2))
        
        return avg_prices, volatility_pivot
    
    def create_comparison_charts(self):
        """Generate cross-country comparison visualizations"""
        if self.unified_data is None:
            self.create_unified_dataset()
        
        # Filter to maize (most common commodity)
        maize_data = self.unified_data[self.unified_data['commodity'] == 'maize'].copy()
        
        if len(maize_data) == 0:
            print("No maize data available for comparison")
            # Try other commodities
            available_commodities = self.unified_data['commodity'].unique()
            if len(available_commodities) > 0:
                commodity = available_commodities[0]
                print(f"   Using {commodity} instead...")
                maize_data = self.unified_data[self.unified_data['commodity'] == commodity].copy()
            else:
                print("No commodity data available for visualization")
                return
        else:
            commodity = 'maize'
        
        print(f"\nCreating visualizations for {commodity}...")
        
        # Create comparison charts
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Average prices by country
        avg_prices = maize_data.groupby('country_name')['price_local'].mean().sort_values()
        avg_prices.plot(kind='barh', ax=ax1, color='skyblue')
        ax1.set_title(f'Average {commodity.title()} Prices by Country')
        ax1.set_xlabel('Average Price (Local Currency)')
        
        # 2. Price trends over time
        monthly_avg = maize_data.groupby(['country_name', 'price_date'])['price_local'].mean().reset_index()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        for i, country in enumerate(monthly_avg['country_name'].unique()):
            country_data = monthly_avg[monthly_avg['country_name'] == country]
            color = colors[i % len(colors)]
            ax2.plot(country_data['price_date'], country_data['price_local'], 
                    label=country, marker='o', alpha=0.7, color=color)
        
        ax2.set_title(f'{commodity.title()} Price Trends Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Price (Local Currency)')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        chart_path = self.processed_dir / 'cross_country_comparison.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"   Chart saved to: {chart_path}")
        plt.show()
    
    def generate_summary_report(self):
        """Generate comprehensive analysis report"""
        print(f"\n{'='*60}")
        print("GENERATING SUMMARY REPORT")
        print(f"{'='*60}")
        
        report_path = self.processed_dir / 'multi_country_summary.txt'
        
        with open(report_path, 'w') as f:
            f.write("PRICEPULSE: MULTI-COUNTRY FOOD PRICE ANALYSIS\n")
            f.write("="*50 + "\n\n")
            
            f.write("DATASET OVERVIEW:\n")
            f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Countries Analyzed: {len(self.countries)}\n\n")
            
            for code, info in self.countries.items():
                f.write(f"{info['name']} ({code}):\n")
                f.write(f"   • {info['observations']:,} price observations\n")
                f.write(f"   • {info['markets']} unique markets\n")
                f.write(f"   • {len(info['commodities'])} commodities: {', '.join(info['commodities'])}\n")
                f.write(f"   • Date range: {info['date_range'][0].strftime('%Y-%m')} to {info['date_range'][1].strftime('%Y-%m')}\n\n")
            
            if self.unified_data is not None:
                f.write("UNIFIED DATASET SUMMARY:\n")
                f.write(f"   • Total observations: {len(self.unified_data):,}\n")
                f.write(f"   • Countries: {self.unified_data['country_name'].nunique()}\n")
                f.write(f"   • Commodities: {list(self.unified_data['commodity'].unique())}\n")
                f.write(f"   • Markets: {self.unified_data['mkt_name'].nunique()}\n")
                f.write(f"   • Date range: {self.unified_data['price_date'].min().strftime('%Y-%m')} to {self.unified_data['price_date'].max().strftime('%Y-%m')}\n")
        
        print(f"Summary report saved to: {report_path}")
        
        # Print portfolio highlights
        print(f"\nPORTFOLIO HIGHLIGHTS:")
        print(f"   Multi-country data processing framework operational")
        print(f"   {len(self.countries)} African countries integrated")
        if self.unified_data is not None:
            print(f"   {len(self.unified_data):,} price observations processed")
            print(f"   {self.unified_data['mkt_name'].nunique()} markets monitored")
        print(f"   Cross-country price analysis and visualization capabilities")
        print(f"   Scalable architecture ready for additional countries")

def main():
    """Main execution function"""
    print("PRICEPULSE: MULTI-COUNTRY FOOD PRICE ANALYZER")
    print("="*50)
    
    # Initialize analyzer
    analyzer = MultiCountryFoodPriceAnalyzer()
    
    # Debug: Print the paths being checked
    print(f"Base path found: {analyzer.base_path}")
    print(f"Looking for Kenya file at: {analyzer.base_path.parent / 'data_sources/processed/kenya_prices_clean.csv'}")
    
    # Load Kenya data (using your existing cleaned data)
    kenya_file = 'data_sources/processed/kenya_prices_clean.csv'
    
    # Check if file exists
    full_kenya_path = analyzer.base_path.parent / kenya_file
    print(f"Full path to check: {full_kenya_path}")
    print(f"File exists: {full_kenya_path.exists()}")
    
    if full_kenya_path.exists():
        kenya_data = analyzer.add_country_data('KEN', kenya_file, 'Kenya')
        
        if kenya_data is not None:
            # Perform analysis with available data
            analyzer.create_unified_dataset()
            analyzer.cross_country_analysis()
            analyzer.create_comparison_charts()
            analyzer.generate_summary_report()
            
            print(f"\nSUCCESS! Multi-country framework tested with Kenya data.")
            print(f"\nNEXT STEPS:")
            print(f"   1. Download Nigeria data from World Bank")
            print(f"   2. Save as: data_sources/raw/NGA_RTFP_mkt_2007_2025.csv")
            print(f"   3. Add Nigeria to the analysis")
            print(f"   4. Repeat for Rwanda, Ghana, etc.")
        else:
            print("Failed to load Kenya data. Check file path and format.")
    else:
        print(f"Kenya data file not found at: {full_kenya_path}")
        print(f"Current working directory: {Path.cwd()}")
        print(f"Script location: {Path(__file__).resolve()}")
        
        # Try to find the file manually
        possible_paths = [
            Path.cwd() / "../../data_sources/processed/kenya_prices_clean.csv",
            Path(__file__).parent.parent.parent / "data_sources/processed/kenya_prices_clean.csv",
            Path("/Users/christaingabire/Documents/PricePulse/data_sources/processed/kenya_prices_clean.csv")
        ]
        
        print("Checking possible paths:")
        for path in possible_paths:
            print(f"   {path}: {path.exists()}")
            if path.exists():
                print(f"   FOUND IT! Using: {path}")
                kenya_data = analyzer.add_country_data('KEN', str(path), 'Kenya')
                if kenya_data is not None:
                    analyzer.create_unified_dataset()
                    analyzer.cross_country_analysis()
                    analyzer.create_comparison_charts()
                    analyzer.generate_summary_report()
                    print(f"\nSUCCESS! Multi-country framework tested with Kenya data.")
                break

if __name__ == "__main__":
    main()