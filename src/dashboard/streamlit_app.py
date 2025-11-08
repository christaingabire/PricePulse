
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import os

# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------
st.set_page_config(page_title="PricePulse Dashboard", page_icon="🌍", layout="wide")

# -------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]

    # Rename columns to match dashboard expectations
    rename_map = {
        "country_name": "country",
        "price_date": "date",
        "mkt_name": "market",
    }
    df = df.rename(columns=rename_map)

    # Ensure date column is properly parsed
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])

    # If no USD prices exist, fall back to local
    if "price_usd" not in df.columns and "price_local" in df.columns:
        df["price"] = df["price_local"]

    return df


# Path to your unified dataset
DATA_PATH = "data_sources/processed/unified_multi_country.csv"

if not os.path.exists(DATA_PATH):
    st.error(f" Data file not found at {DATA_PATH}")
    st.stop()

df = load_data(DATA_PATH)

# -------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------
with st.sidebar:
    st.header("Filters")

    # Date range slider
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.slider(
        "Date range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
    )

    # Region (optional)
    regions = sorted(df["region"].dropna().unique().tolist()) if "region" in df.columns else []
    region_sel = st.multiselect("Region", regions, default=regions) if regions else []

    # Country
    countries = sorted(df["country"].dropna().unique().tolist())
    country_sel = st.multiselect("Country", countries, default=countries)

    # Commodity
    commodities = sorted(df["commodity"].dropna().unique().tolist())
    default_commodity = "maize" if "maize" in commodities else (commodities[0] if commodities else None)
    commodity_sel = st.multiselect("Commodity", commodities, default=[default_commodity] if default_commodity else [])

    # Price basis
    price_candidates = [c for c in ["price_usd", "price_local", "price"] if c in df.columns]
    price_col_default = "price_usd" if "price_usd" in price_candidates else price_candidates[0]
    price_basis = st.radio(
        "Price basis",
        options=price_candidates,
        index=price_candidates.index(price_col_default),
        help="Choose USD if available for cross-country comparability.",
    )

# -------------------------------------------------------
# APPLY FILTERS
# -------------------------------------------------------
mask = df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
if "region" in df.columns and region_sel:
    mask &= df["region"].isin(region_sel)
if country_sel:
    mask &= df["country"].isin(country_sel)
if commodity_sel:
    mask &= df["commodity"].isin(commodity_sel)

view = df.loc[mask].copy()

# -------------------------------------------------------
# DASHBOARD HEADER
# -------------------------------------------------------
st.title(" PricePulse: African Food Price Explorer")
st.caption("Compare food prices across countries, markets, and commodities (2007–2025). Source: World Bank Real-Time Food Prices + validation sources.")

# -------------------------------------------------------
# KPIs
# -------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
if len(view):
    latest_date = view["date"].max()
    latest = view[view["date"] == latest_date]
    avg_level = latest[price_basis].mean()

    # Year-over-year change
    one_year_prior = latest_date - pd.Timedelta(days=365)
    past_window = view[view["date"] <= one_year_prior]
    yoy = np.nan
    if len(past_window):
        past_avg = past_window[price_basis].mean()
        if pd.notnull(past_avg) and past_avg != 0:
            yoy = ((avg_level - past_avg) / past_avg) * 100

    col1.metric("Latest date", latest_date.strftime("%Y-%m-%d"))
    col2.metric(f"Avg price ({price_basis})", f"{avg_level:,.2f}" if pd.notnull(avg_level) else "—")
    col3.metric("YoY change", f"{yoy:,.1f}%" if pd.notnull(yoy) else "—")
    col4.metric("Observations", f"{len(view):,}")
else:
    st.info("No data for the current filters. Try broadening your selection.")

# -------------------------------------------------------
# PRICE TREND (LINE CHART)
# -------------------------------------------------------
st.subheader(" Price trends over time")
if len(view):
    ts = (
        view.groupby(["date", "country", "commodity"], as_index=False)[price_basis]
        .mean()
    )
    fig = px.line(ts, x="date", y=price_basis, color="country", hover_data=["commodity"], title=None)
    fig.update_layout(legend_title_text="Country", height=420, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------
# CROSS-COUNTRY COMPARISON (BAR)
# -------------------------------------------------------
st.subheader(" Cross-country comparison by commodity")
if len(view):
    commodity_pick = st.selectbox(
        "Choose commodity for comparison",
        sorted(view["commodity"].unique().tolist()),
        index=sorted(view["commodity"].unique().tolist()).index(default_commodity)
        if default_commodity in view["commodity"].unique()
        else 0,
    )
    cc = (
        view[view["commodity"] == commodity_pick]
        .groupby("country", as_index=False)[price_basis]
        .mean()
        .sort_values(price_basis, ascending=False)
    )
    fig2 = px.bar(cc, x="country", y=price_basis, text=price_basis, title=None)
    fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig2.update_layout(yaxis_title=price_basis, height=440, margin=dict(t=10))
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------
# DISTRIBUTION / VOLATILITY (BOX PLOT)
# -------------------------------------------------------
st.subheader(" Distribution & volatility")
if len(view):
    long = view[["country", "commodity", price_basis]].dropna()
    fig3 = px.box(long, x="country", y=price_basis, color="commodity", points="outliers")
    fig3.update_layout(height=480, margin=dict(t=10))
    st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------------
# RAW DATA TABLE
# -------------------------------------------------------
with st.expander("Show filtered data"):
    st.dataframe(view.sort_values("date", ascending=False), use_container_width=True)

st.caption(" Tip: Use the sidebar to filter by region, country, commodity, and date range.")
