from fastapi import FastAPI, HTTPException
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------
# APP SETUP
# ---------------------------------------------------------

app = FastAPI(
    title="FORESIGHT Demand Forecast & Risk API",
    description="API for SKU-level demand forecast and inventory risk scoring.",
    version="1.0.0"
)

# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

FORECAST_FILE = BASE_DIR / "reports" / "future_6_week_forecast.csv"
RISK_FILE = BASE_DIR / "reports" / "risk_scoring.csv"

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

try:
    forecast_df = pd.read_csv(FORECAST_FILE)
    risk_df = pd.read_csv(RISK_FILE)

except Exception as e:
    forecast_df = pd.DataFrame()
    risk_df = pd.DataFrame()
    print(f"Data loading error: {e}")


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "service": "FORESIGHT Demand Forecast & Risk API",
        "status": "running",
        "version": "1.0"
    }


# ---------------------------------------------------------
# LIST AVAILABLE SKUs
# ---------------------------------------------------------

@app.get("/skus")
def get_skus():

    if forecast_df.empty:
        raise HTTPException(
            status_code=500,
            detail="Forecast data is unavailable."
        )

    skus = sorted(
        forecast_df["SKU"].dropna().unique().tolist()
    )

    return {
        "count": len(skus),
        "SKUs": skus
    }


# ---------------------------------------------------------
# FORECAST + RISK FOR ONE SKU
# ---------------------------------------------------------

@app.get("/forecast/{sku}")
def get_forecast(sku: str):

    sku = sku.upper().strip()

    if forecast_df.empty or risk_df.empty:
        raise HTTPException(
            status_code=500,
            detail="Forecast or risk data is unavailable."
        )

    # Check SKU
    if sku not in forecast_df["SKU"].astype(str).str.upper().values:

        raise HTTPException(
            status_code=404,
            detail=f"SKU '{sku}' was not found."
        )

    # Forecast
    sku_forecast = forecast_df[
        forecast_df["SKU"].astype(str).str.upper() == sku
    ].copy()

    sku_forecast["Date"] = pd.to_datetime(
        sku_forecast["Date"]
    ).dt.strftime("%Y-%m-%d")

    forecast_records = sku_forecast[
        ["Date", "Forecast_Units"]
    ].to_dict(orient="records")

    # Risk
    sku_risk = risk_df[
        risk_df["SKU"].astype(str).str.upper() == sku
    ]

    if sku_risk.empty:

        raise HTTPException(
            status_code=404,
            detail=f"Risk information for SKU '{sku}' was not found."
        )

    risk_row = sku_risk.iloc[0]

    return {
        "SKU": sku,

        "forecast": forecast_records,

        "risk": {
            "stockout_risk": risk_row["Stockout_Risk"],
            "overstock_risk": risk_row["Overstock_Risk"],
            "recommended_action": risk_row["Recommended_Action"],
            "current_stock": float(risk_row["Current_Stock"]),
            "on_order": float(risk_row["On_Order"]),
            "forecast_6_week_units": float(
                risk_row["Forecast_6W_Units"]
            ),
            "projected_stock_6_week": float(
                risk_row["Projected_Stock_6W"]
            ),
            "sales_at_risk_inr": float(
                risk_row["Sales_At_Risk_INR"]
            ),
            "locked_capital_inr": float(
                risk_row["Locked_Capital_INR"]
            ),
            "value_at_stake_inr": float(
                risk_row["Value_At_Stake_INR"]
            )
        }
    }


# ---------------------------------------------------------
# BATCH FORECAST + RISK
# ---------------------------------------------------------

@app.post("/forecast/batch")
def batch_forecast(skus: list[str]):

    if forecast_df.empty or risk_df.empty:
        raise HTTPException(
            status_code=500,
            detail="Forecast or risk data is unavailable."
        )

    if not skus:

        raise HTTPException(
            status_code=400,
            detail="Please provide at least one SKU."
        )

    requested_skus = [
        sku.upper().strip()
        for sku in skus
    ]

    available_skus = set(
        forecast_df["SKU"]
        .astype(str)
        .str.upper()
    )

    invalid_skus = [
        sku for sku in requested_skus
        if sku not in available_skus
    ]

    if invalid_skus:

        raise HTTPException(
            status_code=404,
            detail={
                "message": "Some SKUs were not found.",
                "invalid_skus": invalid_skus
            }
        )

    results = []

    for sku in requested_skus:

        sku_forecast = forecast_df[
            forecast_df["SKU"].astype(str).str.upper() == sku
        ].copy()

        sku_forecast["Date"] = pd.to_datetime(
            sku_forecast["Date"]
        ).dt.strftime("%Y-%m-%d")

        sku_risk = risk_df[
            risk_df["SKU"].astype(str).str.upper() == sku
        ]

        if sku_risk.empty:
            continue

        risk_row = sku_risk.iloc[0]

        results.append({
            "SKU": sku,

            "forecast": sku_forecast[
                ["Date", "Forecast_Units"]
            ].to_dict(orient="records"),

            "recommended_action":
                risk_row["Recommended_Action"],

            "stockout_risk":
                risk_row["Stockout_Risk"],

            "overstock_risk":
                risk_row["Overstock_Risk"],

            "value_at_stake_inr":
                float(risk_row["Value_At_Stake_INR"])
        })

    return {
        "count": len(results),
        "results": results
    }