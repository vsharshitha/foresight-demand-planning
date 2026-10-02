# FORESIGHT — EDA & Data Quality Memo

## 1. Executive Summary

The exploratory analysis was performed to understand historical SKU-level demand, identify demand patterns, evaluate seasonality, and identify potential inventory risks.

The analysis confirmed that demand varies substantially across SKUs and time periods. Seasonal and calendar-related patterns were observed, supporting the use of time-based features in the forecasting model.

The cleaned dataset was subsequently used for baseline forecasting, model development, backtesting, and inventory risk scoring.

---

## 2. Data Quality Assessment

The project data was profiled before modelling to identify missing values, duplicates, inconsistent formats, and invalid observations.

The cleaning process included:

* Checking missing values
* Checking duplicate records
* Standardising column names and data types
* Validating date fields
* Checking numerical ranges
* Validating SKU-level records
* Checking categorical values
* Preparing analysis-ready datasets

The cleaned datasets were stored separately from the raw input data to preserve reproducibility.

---

## 3. Exploratory Findings

### 3.1 Demand Distribution

Demand was examined at the SKU and time level to identify differences between high-volume and low-volume products.

The analysis showed that demand is not evenly distributed across SKUs. A relatively small group of products contributes a substantial share of total demand, while lower-volume products require different inventory considerations.

This variation supports SKU-level forecasting rather than applying a single demand assumption to every product.

---

### 3.2 Top Demand Periods

The highest-demand months identified during EDA were:

| Rank | Month      | Units Sold |
| ---: | ---------- | ---------: |
|    1 | March 2024 |     26,791 |
|    2 | March 2025 |     26,757 |
|    3 | May 2025   |     24,636 |
|    4 | June 2024  |     24,506 |
|    5 | May 2024   |     24,402 |

These periods demonstrate that demand changes materially over time and provide evidence for incorporating calendar and seasonal information into the forecasting process.

---

### 3.3 Seasonality

Demand was analysed across months and calendar periods to identify recurring patterns.

The presence of recurring demand behaviour supports the use of a seasonal-naive baseline as the first forecasting benchmark.

The forecasting workflow therefore compares the machine-learning model against a simple seasonal baseline rather than evaluating the model in isolation.

---

### 3.4 SKU Movement

SKU-level analysis was used to identify products with different demand profiles.

High-demand products require attention to potential stockout risk, while low-demand or slow-moving products may create excess inventory and locked capital.

This distinction is incorporated into the subsequent risk-scoring stage.

---

## 4. Feature Engineering

The modelling workflow uses historical and calendar information to create predictive features.

The feature-engineering process includes:

* Lagged demand
* Rolling demand statistics
* Calendar variables
* Seasonal information
* Promotion-related information where available
* SKU/product characteristics
* Inventory-related variables for risk scoring

Features were constructed using historical information so that future demand information was not intentionally introduced into model inputs.

---

## 5. Baseline Analysis

A seasonal-naive model was established as the baseline.

### Baseline WAPE

**11.97%**

The baseline provides a simple benchmark representing expected demand based on historical seasonal behaviour.

Any more complex forecasting model therefore needs to demonstrate improvement against this benchmark.

---

## 6. Forecasting Model Results

The Random Forest forecasting model achieved:

**WAPE: 10.99%**

Compared with the seasonal-naive baseline:

**Improvement: 8.23%**

Rolling-origin backtesting produced an average WAPE of approximately:

**2.14%**

The rolling-origin approach was used because demand forecasting is a time-series problem and chronological ordering must be preserved during evaluation.

---

## 7. Risk & Business Insights

The forecast results were combined with inventory information to identify potential stockout and overstock situations.

### Risk Decision Summary

| Recommended Action | SKU Count |
| ------------------ | --------: |
| Reorder Now        |        30 |
| Markdown / Clear   |         8 |
| Healthy            |        12 |

### Financial Exposure

| Metric               |       Value |
| -------------------- | ----------: |
| Sales at Risk        | ₹5.25 crore |
| Locked Capital       | ₹0.91 crore |
| Total Value at Stake | ₹6.16 crore |

These figures translate the analytical results into business-impact measures that can be used by operations and finance stakeholders.

---

## 8. Key Business Insights

### Insight 1 — Demand is uneven across products

Different SKUs show substantially different demand levels. Forecasting at SKU level is therefore more appropriate than using a single aggregate demand estimate.

### Insight 2 — Time-based patterns matter

The observed monthly demand variation supports the inclusion of calendar and seasonal features in the forecasting workflow.

### Insight 3 — Baseline comparison is important

The Random Forest model was evaluated against the seasonal-naive baseline rather than being judged using model performance alone.

### Insight 4 — Forecasting can support inventory decisions

The forecast becomes more useful when combined with inventory position. This enables the project to move from prediction to actionable risk categories.

### Insight 5 — Financial impact makes the analysis actionable

Expressing risk in rupee terms helps connect technical model output with operational and financial decision-making.

---

## 9. Limitations

The analysis has several limitations:

* The dataset represents the provided project data and may not include every real-world demand driver.
* Historical patterns may not continue unchanged in future periods.
* Forecast accuracy may vary across individual SKUs.
* Risk classifications depend on the quality and timing of inventory snapshots.
* Financial impact estimates depend on the assumptions used in the supplied data.
* Further monitoring would be required when new operational data becomes available.

---

## 10. Conclusion

The EDA established the main demand patterns and data-quality considerations required for forecasting.

The analysis supported:

1. A seasonal-naive forecasting baseline.
2. Time-based and historical feature engineering.
3. Machine-learning demand forecasting.
4. Rolling-origin backtesting.
5. SKU-level inventory risk scoring.
6. Financial impact quantification.

The resulting workflow provides a reproducible foundation for the FORESIGHT planning dashboard and deployed scoring service.
