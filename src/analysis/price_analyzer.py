import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def load_clean_data():
    """Load the cleaned data"""
    return pd.read_csv('../../data_sources/processed/kenya_prices_clean.csv')

def analyze_price_trends(df):
    """Analyze price trends over time"""
    
    # Convert price_date to datetime
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    # Focus on maize (most data)
    maize_data = df[df['maize'].notna()].copy()
    
    print(f"Maize data: {len(maize_data)} observations across {maize_data['mkt_name'].nunique()} markets")
    print(f"Date range: {maize_data['price_date'].min()} to {maize_data['price_date'].max()}")
    
    return maize_data

def create_price_visualizations(df):
    """Create price visualizations"""
    
    # 1. Price trends by market
    plt.figure(figsize=(15, 8))
    
    # Get top 5 markets with most data
    top_markets = df['mkt_name'].value_counts().head(5).index
    
    for market in top_markets:
        market_data = df[df['mkt_name'] == market]
        plt.plot(market_data['price_date'], market_data['maize'], 
                marker='o', label=market, alpha=0.7)
    
    plt.title('Maize Price Trends by Market (2015-2020)')
    plt.xlabel('Date')
    plt.ylabel('Price (KES per kg)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('../../data_sources/processed/maize_price_trends.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Average prices by market
    plt.figure(figsize=(12, 6))
    
    avg_prices = df.groupby('mkt_name')['maize'].mean().sort_values(ascending=True)
    
    plt.barh(range(len(avg_prices)), avg_prices.values)
    plt.yticks(range(len(avg_prices)), avg_prices.index)
    plt.xlabel('Average Maize Price (KES per kg)')
    plt.title('Average Maize Prices by Market')
    plt.tight_layout()
    
    plt.savefig('../../data_sources/processed/average_prices_by_market.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return avg_prices

def price_insights(df):
    """Generate key insights"""
    
    print("\n" + "="*50)
    print("KEY INSIGHTS FROM KENYA FOOD PRICE DATA")
    print("="*50)
    
    # Overall statistics
    print(f"\nOVERVIEW:")
    print(f"• {len(df)} price observations")
    print(f"• {df['mkt_name'].nunique()} markets analyzed")
    print(f"• Price range: {df['maize'].min():.2f} - {df['maize'].max():.2f} KES/kg")
    print(f"• Average price: {df['maize'].mean():.2f} KES/kg")
    
    # Highest and lowest price markets
    avg_by_market = df.groupby('mkt_name')['maize'].mean()
    
    print(f"\nMOST EXPENSIVE MARKET:")
    expensive = avg_by_market.idxmax()
    print(f"• {expensive}: {avg_by_market[expensive]:.2f} KES/kg")
    
    print(f"\nCHEAPEST MARKET:")
    cheap = avg_by_market.idxmin()
    print(f"• {cheap}: {avg_by_market[cheap]:.2f} KES/kg")
    
    print(f"\nPRICE DIFFERENCE:")
    price_diff = avg_by_market.max() - avg_by_market.min()
    print(f"• {price_diff:.2f} KES/kg difference between markets")
    print(f"• {(price_diff/avg_by_market.min()*100):.1f}% price variation")

def advanced_insights(df):
    """Generate advanced insights"""
    
    print("\n" + "="*60)
    print("ADVANCED MARKET ANALYSIS")
    print("="*60)
    
    # Volatility analysis
    volatility = df.groupby('mkt_name')['maize'].std().sort_values(ascending=False)
    
    print(f"\nPRICE VOLATILITY RANKING:")
    for i, (market, vol) in enumerate(volatility.head().items(), 1):
        print(f"{i}. {market}: {vol:.2f} KES/kg std deviation")
    
    # Seasonal patterns
    df['month'] = pd.to_datetime(df['price_date']).dt.month
    seasonal = df.groupby('month')['maize'].mean()
    
    print(f"\nSEASONAL PATTERNS:")
    print(f"• Highest prices: Month {seasonal.idxmax()} ({seasonal.max():.2f} KES/kg)")
    print(f"• Lowest prices: Month {seasonal.idxmin()} ({seasonal.min():.2f} KES/kg)")
    
    # Market accessibility (price vs distance from Nairobi)
    market_coords = {
        'Kitui': (-1.367, 38.01),
        'Mandera': (3.93, 41.87), 
        'Marsabit': (2.34, 37.99),
        'Lodwar (Turkana)': (3.12, 35.60),
        'Marigat (Baringo)': (0.48, 35.98)
    }
    
    nairobi = (-1.29, 36.82)
    
    print(f"\nDISTANCE IMPACT:")
    avg_prices_by_market = df.groupby('mkt_name')['maize'].mean()
    
    for market in market_coords:
        if market in avg_prices_by_market.index:
            # Calculate rough distance (simplified)
            lat_diff = market_coords[market][0] - nairobi[0]
            lon_diff = market_coords[market][1] - nairobi[1]
            distance = (lat_diff**2 + lon_diff**2)**0.5 * 111  # Rough km conversion
            
            price = avg_prices_by_market[market]
            print(f"• {market}: ~{distance:.0f}km from Nairobi, avg price {price:.2f} KES/kg")

if __name__ == "__main__":
    # Load and analyze data
    df = load_clean_data()
    maize_data = analyze_price_trends(df)
    
    # Create visualizations
    avg_prices = create_price_visualizations(maize_data)
    
    # Generate insights
    price_insights(maize_data)
    
    # Add advanced analysis
    advanced_insights(maize_data)