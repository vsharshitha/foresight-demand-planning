import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="FORESIGHT - Demand Planning Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

FORECAST_FILE = BASE_DIR / "reports" / "future_6_week_forecast.csv"
RISK_FILE = BASE_DIR / "reports" / "risk_scoring.csv"
SALES_FILE = BASE_DIR / "data" / "processed" / "sales_daily_clean.csv"
SKU_FILE = BASE_DIR / "data" / "processed" / "sku_master_clean.csv"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():

    forecast = pd.read_csv(FORECAST_FILE)
    risk = pd.read_csv(RISK_FILE)
    sales = pd.read_csv(SALES_FILE)
    sku = pd.read_csv(SKU_FILE)

    forecast["Date"] = pd.to_datetime(forecast["Date"])
    sales["Date"] = pd.to_datetime(sales["Date"])

    return forecast, risk, sales, sku


try:
    forecast, risk, sales, sku = load_data()

except Exception as e:
    st.error("Unable to load dashboard data.")
    st.write("Please check that the required files exist in the project folders.")
    st.exception(e)
    st.stop()


# ---------------------------------------------------------
# PREPARE DATA
# ---------------------------------------------------------

# Weekly actual sales
weekly_actual = (
    sales
    .set_index("Date")
    .groupby("SKU")["Units_Sold"]
    .resample("W-MON")
    .sum()
    .reset_index()
)

# Add product information
forecast = forecast.merge(
    sku[["SKU", "Product_Name", "Category", "Subcategory"]],
    on="SKU",
    how="left"
)

weekly_actual = weekly_actual.merge(
    sku[["SKU", "Product_Name", "Category"]],
    on="SKU",
    how="left"
)

risk = risk.merge(
    sku[["SKU", "Product_Name", "Category", "Subcategory"]],
    on="SKU",
    how="left",
    suffixes=("", "_master")
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("🔎 Filters")

categories = ["All"] + sorted(
    forecast["Category"].dropna().unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "Category",
    categories
)

if selected_category == "All":
    available_skus = sorted(forecast["SKU"].unique())
else:
    available_skus = sorted(
        forecast.loc[
            forecast["Category"] == selected_category,
            "SKU"
        ].unique()
    )

selected_sku = st.sidebar.selectbox(
    "SKU",
    ["All"] + available_skus
)


# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------

filtered_forecast = forecast.copy()
filtered_risk = risk.copy()
filtered_actual = weekly_actual.copy()

if selected_category != "All":

    filtered_forecast = filtered_forecast[
        filtered_forecast["Category"] == selected_category
    ]

    filtered_risk = filtered_risk[
        filtered_risk["Category"] == selected_category
    ]

    filtered_actual = filtered_actual[
        filtered_actual["Category"] == selected_category
    ]

if selected_sku != "All":

    filtered_forecast = filtered_forecast[
        filtered_forecast["SKU"] == selected_sku
    ]

    filtered_risk = filtered_risk[
        filtered_risk["SKU"] == selected_sku
    ]

    filtered_actual = filtered_actual[
        filtered_actual["SKU"] == selected_sku
    ]


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("📊 FORESIGHT — Demand Planning Dashboard")

st.markdown(
    "Weekly demand forecasts, inventory risk and recommended planning actions."
)

st.divider()


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

total_skus = filtered_risk["SKU"].nunique()

reorder_count = (
    filtered_risk["Recommended_Action"]
    .eq("Reorder now")
    .sum()
)

markdown_count = (
    filtered_risk["Recommended_Action"]
    .eq("Markdown / clear")
    .sum()
)

value_at_stake = filtered_risk["Value_At_Stake_INR"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "SKUs",
    total_skus
)

col2.metric(
    "Reorder Now",
    reorder_count
)

col3.metric(
    "Markdown / Clear",
    markdown_count
)

col4.metric(
    "Value at Stake",
    f"₹{value_at_stake:,.0f}"
)

st.divider()


# ---------------------------------------------------------
# FORECAST VS ACTUAL
# ---------------------------------------------------------

st.subheader("📈 Forecast vs Actual Demand")

# Show current selection clearly
if selected_sku == "All":
    st.write(f"**Current selection:** {selected_category} — All SKUs")
else:
    st.write(f"**Current selection:** {selected_category} — {selected_sku}")

# Prepare actual data
actual_data = filtered_actual[
    ["Date", "Units_Sold"]
].copy()

# Prepare forecast data
forecast_data = filtered_forecast[
    ["Date", "Forecast_Units"]
].copy()

# Aggregate according to selected filter
actual_data = (
    actual_data
    .groupby("Date", as_index=False)["Units_Sold"]
    .sum()
)

forecast_data = (
    forecast_data
    .groupby("Date", as_index=False)["Forecast_Units"]
    .sum()
)

# Rename columns
actual_data = actual_data.rename(
    columns={"Units_Sold": "Actual Demand"}
)

forecast_data = forecast_data.rename(
    columns={"Forecast_Units": "Forecast Demand"}
)

# Combine
chart_data = pd.merge(
    actual_data,
    forecast_data,
    on="Date",
    how="outer"
).sort_values("Date")

# Use Date as index
chart_data = chart_data.set_index("Date")

# Display chart
st.line_chart(
    chart_data,
    use_container_width=True
)

# Show forecast values underneath
if not forecast_data.empty:

    st.write("### 🔮 Future Forecast")

    display_forecast = forecast_data.copy()

    display_forecast["Date"] = display_forecast.index if False else pd.to_datetime(
        display_forecast.index
    )

    display_forecast["Forecast Demand"] = (
        display_forecast["Forecast Demand"].round(2)
    )

    st.dataframe(
        display_forecast,
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("No forecast data available for this selection.")
    
    
# ---------------------------------------------------------
# RISK SUMMARY
# ---------------------------------------------------------

st.subheader("⚠️ Inventory Risk Summary")

risk_counts = (
    filtered_risk["Recommended_Action"]
    .value_counts()
    .rename_axis("Recommended Action")
    .reset_index(name="SKU Count")
)

if len(risk_counts) > 0:
    st.bar_chart(
        risk_counts.set_index("Recommended Action")
    )
else:
    st.info("No risk records available for the selected filters.")


# ---------------------------------------------------------
# PRIORITIZED ACTION LIST
# ---------------------------------------------------------

st.subheader("🚨 Prioritized Planning Actions")

priority_actions = filtered_risk[
    [
        "SKU",
        "Product_Name",
        "Category",
        "Stockout_Risk",
        "Overstock_Risk",
        "Recommended_Action",
        "Forecast_6W_Units",
        "Current_Stock",
        "On_Order",
        "Value_At_Stake_INR"
    ]
].copy()

priority_actions = priority_actions.sort_values(
    "Value_At_Stake_INR",
    ascending=False
)

priority_actions["Value_At_Stake_INR"] = (
    priority_actions["Value_At_Stake_INR"]
    .round(0)
)

priority_actions = priority_actions.rename(
    columns={
        "Forecast_6W_Units": "6W Forecast",
        "Current_Stock": "Current Stock",
        "On_Order": "On Order",
        "Value_At_Stake_INR": "Value at Stake (₹)"
    }
)

if len(priority_actions) > 0:

    st.dataframe(
        priority_actions,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No planning actions are available for the selected filters."
    )


# ---------------------------------------------------------
# DETAILED SKU FORECAST
# ---------------------------------------------------------

if selected_sku != "All":

    st.subheader(f"🔮 6-Week Forecast — {selected_sku}")

    sku_forecast = filtered_forecast[
        [
            "SKU",
            "Product_Name",
            "Date",
            "Forecast_Units"
        ]
    ].copy()

    sku_forecast["Forecast_Units"] = (
        sku_forecast["Forecast_Units"].round(2)
    )

    st.dataframe(
        sku_forecast,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------------------------
# RISK DETAILS
# ---------------------------------------------------------

st.subheader("📋 Risk Details")

risk_display = filtered_risk[
    [
        "SKU",
        "Product_Name",
        "Category",
        "Current_Stock",
        "On_Order",
        "Forecast_6W_Units",
        "Projected_Stock_6W",
        "Stockout_Risk",
        "Overstock_Risk",
        "Recommended_Action",
        "Sales_At_Risk_INR",
        "Locked_Capital_INR",
        "Value_At_Stake_INR"
    ]
].copy()

st.dataframe(
    risk_display,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "FORESIGHT | Demand Forecasting & Inventory Risk Planning"
)