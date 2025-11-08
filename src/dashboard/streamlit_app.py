import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import os

# ----------------------------------------------------
# Page setup
# ----------------------------------------------------
st.set_page_config(page_title="PricePulse Dashboard", page_icon="🌍", layout="wide")

# ----------------------------------------------------
# Load data
# ----------------------------------------------------
DATA_PATH = "data_sources/processed/unified_multi_country.csv"

if not os.path.exists(DATA_PATH):
    st.error(f" Data file not found at {DATA_PATH}")
    st.stop()

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    return df

df = load_data(DATA_PATH)

# ----------------------------------------------------
# Sidebar filters
# ----------------------------------------------------
with st.sidebar:
    st.header("Filters")

    # View mode toggle
    view_mode = st.radio(
        "View mode",
        ["Index (2019=100)", "Local (per kg)"],
        index=0,
        help="Index is the default mode and makes countries comparable."
)

    # Date range
    min_date, max_date = df["date"].min(), df["date"].max()
    date_range = st.slider(
        "Date range",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
    )

    # Country and commodity filters
    countries = sorted(df["country"].dropna().unique().tolist())
    country_sel = st.multiselect("Country", countries, default=countries)

    commodities = sorted(df["commodity"].dropna().unique().tolist())
    default_commodity = "maize" if "maize" in commodities else commodities[0]
    commodity_sel = st.multiselect(
        "Commodity", commodities, default=[default_commodity]
    )

# ----------------------------------------------------
# Apply filters
# ----------------------------------------------------
mask = df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
if country_sel:
    mask &= df["country"].isin(country_sel)
if commodity_sel:
    mask &= df["commodity"].isin(commodity_sel)
view = df.loc[mask].copy()


# Select column to plot
plot_local = "price_local"
plot_col = plot_local if view_mode.startswith("Local") else "price_index"

# ----------------------------------------------------
# Header and context note
# ----------------------------------------------------
st.title(" PricePulse: African Food Price Explorer")

    
if plot_col == plot_local:
    st.info("Viewing prices in local currency per kg. Values are not comparable across countries")
else:
    st.success("Viewing prices as an Index (2019=100). A value of 150 means prices are 50% higher than in 2019")


st.caption("Data: World Bank Real-Time Food Prices (2007–2025).")

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------
view["year_month"] = view["date"].dt.to_period("M")
monthly = (
    view.groupby("year_month", as_index=True)[plot_col]
        .median()
        .sort_index()
)

col1, col2, col3, col4 = st.columns(4)
if len(monthly) >= 13:
    latest_month = monthly.index[-1]
    current_val = monthly.iloc[-1]
    year_ago_val = monthly.iloc[-13]

    yoy_change = ((current_val - year_ago_val) / year_ago_val * 100) if year_ago_val != 0 else np.nan
    # Volatility = standard deviation of last 12 months
    volatility = monthly.iloc[-12:].std()

    col1.metric("Latest month", str(latest_month))
    col2.metric("Median Index (2019=100)", f"{current_val:,.0f}")
    col3.metric("12-mo Change", f"{yoy_change:+.1f}%" if pd.notnull(yoy_change) else "—")
    col4.metric("12-mo Volatility (σ)", f"{volatility:,.1f}")
else:
    col1.metric("Latest month", "—")
    col2.metric("Median Index", "—")
    col3.metric("12-mo Change", "—")
    col4.metric("12-mo Volatility", "—")

# ----------------------------------------------------
# Charts
# ----------------------------------------------------
if len(view):

    st.subheader(" Price trends over time")
    ts = (
        view.groupby(["date", "country"], as_index=False)[plot_col]
        .mean()
    )
    fig = px.line(ts, x="date", y=plot_col, color="country")
    fig.update_layout(legend_title_text="Country", height=400, margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(" Cross-country comparison by commodity")
    commodity_pick = st.selectbox("Choose commodity for comparison", sorted(view["commodity"].unique()))
    cc = (
        view[view["commodity"] == commodity_pick]
        .groupby("country", as_index=False)[plot_col]
        .mean()
        .sort_values(plot_col, ascending=False)
    )
    fig2 = px.bar(cc, x="country", y=plot_col, text=plot_col)
    fig2.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig2.update_layout(yaxis_title=plot_col, height=400, margin=dict(t=10))
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader(" Distribution & volatility")
    long = view[["country", "commodity", plot_col]].dropna()
    fig3 = px.box(long, x="country", y=plot_col, color="commodity", points="outliers")
    fig3.update_layout(height=450, margin=dict(t=10))
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("Show filtered data"):
        st.dataframe(view.sort_values("date", ascending=False), use_container_width=True)

else:
    st.warning("No records match your current filters")

st.caption(" Tip: Adjust filters or switch to Index view to explore regional differences")
