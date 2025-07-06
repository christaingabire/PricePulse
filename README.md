# PricePulse

I built this project to analyze food prices across African countries and understand how food markets work differently across the continent. I realized how little cross-country food price data was available in an accessible format.

## What This Project Does

PricePulse takes messy food price data from different African countries and makes it possible to compare prices, identify trends, and spot interesting patterns across regions. The system now covers six countries spanning East Africa to the Sahel, representing over 360 million people and different agricultural systems.

## Current Coverage

The platform monitors food prices across:
- **6 countries**: Kenya, Nigeria, Mali, Mozambique, Senegal, Somalia
- **404 markets**: From rural trading posts to major urban centers
- **36,000+ observations**: Covering 18 years of price data (2007-2025)
- **5 regions**: East Africa, West Africa, Sahel, Southern Africa, Horn of Africa

Key commodities tracked include maize, rice, sorghum, millet, and regional specialties, with some crops available across multiple countries for direct comparison.

## Interesting Discoveries

The most interesting aspect has been seeing how different food systems are across the continent:

- **Regional differences**: East Africa relies heavily on maize, while West Africa centers on rice and other grains
- **Price variations**: Sorghum costs much more in Kenya than Nigeria, which suggests potential trade opportunities
- **Currency zones**: Mali and Senegal share the same currency, making price comparisons easier
- **Crisis patterns**: Somalia's markets show different price patterns that could be useful for monitoring food security

These patterns show not just market differences but also how geography, conflict, and food security connect across Africa.

## How I Built This

### The Data Challenge
Getting clean, comparable data across countries was harder than expected. Each country has different commodity names, market structures, and data quality. Some countries focus on cereals while others emphasize root crops.

I used the World Bank's Real-Time Food Prices database as the main source since it's standardized across countries and updated regularly.

### Technical Approach
The project uses a modular Python structure that can handle new countries:
- Country-specific cleaners handle different data formats
- A unified processor combines everything for cross-country analysis  
- Automatic commodity matching enables price comparisons
- Pandas and matplotlib handle data processing and visualization

The hardest part was building something flexible enough to handle different African food systems while still making meaningful comparisons possible.

## Project Structure

```
PricePulse/
├── data_sources/
│   ├── raw/                    # Downloaded World Bank data
│   └── processed/              # Cleaned, unified datasets
├── src/
│   ├── multi_country/          # Cross-country analysis engine
│   ├── processing/             # Country-specific data cleaners
│   └── analysis/               # Individual country analysis
```

## What I Learned

This project taught me a lot about working with real-world data:
- African food markets are complex and diverse
- Building scalable code from the start saves time later
- Cross-country analysis needs careful handling of currencies and local conditions
- Food security patterns often reflect broader economic and political situations

I also learned that good food price data could help policy makers and humanitarian organizations make better decisions.

## Running the Analysis

To run the analysis:

```bash
# Clone and navigate
git clone https://github.com/christaingabire/PricePulse.git
cd PricePulse

# Run individual country cleaners
python src/processing/clean_mali.py
python src/processing/clean_senegal.py
# ... etc for each country

# Run cross-country analysis
python src/multi_country/multi_country_processor.py
```

Requirements: pandas, numpy, matplotlib, seaborn

## Next Steps

I'm planning to expand to more countries to build better continental coverage. Ethiopia, Democratic Republic of Congo, and South Sudan are on the list due to their importance for food security.

Ideas I'm exploring:
- Crisis alerting for conflict-affected areas
- Seasonal analysis to understand harvest impacts
- Trade flow analysis between neighboring countries
- Web interface for easier exploration

## Potential Applications

With 36,000+ price observations across African markets, this data could support:
- Early warning systems for food crises
- Trade policy analysis
- Agricultural development planning
- Humanitarian response

## Data Sources

- World Bank Real-Time Food Prices database (primary source)
- Country agricultural ministry data for validation
- FAO market monitoring where available

The World Bank data has been comprehensive and well-maintained across countries.

---

I'm a data engineer interested in working in public interest. African food markets tell interesting stories about economics, development, and resilience, and there's more to discover.
