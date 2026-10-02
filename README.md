# FORESIGHT — Demand Forecasting & Inventory Risk Analytics

## 1. Project Overview

**FORESIGHT** is a data science and analytics project designed to help operations teams make better inventory planning decisions.

The project uses historical SKU-level sales, product, calendar, and inventory data to:

* Forecast future weekly demand for each SKU
* Compare the forecast against a seasonal-naive baseline
* Identify stockout and overstock risk
* Quantify the financial value at risk
* Provide an interactive planning dashboard
* Expose forecast and risk results through a FastAPI scoring service
* Present business findings through an executive readout

The project follows a reproducible pipeline from raw data to forecasting, risk scoring, dashboard, API, and executive reporting.

---

## 2. Business Problem

Inventory teams need to answer two important questions:

1. **What should we expect to sell in the coming weeks?**
2. **Which products require action now?**

Poor demand forecasts can result in:

* Stockouts and lost sales
* Excess inventory
* Capital being locked in slow-moving products
* Inefficient replenishment decisions

FORESIGHT converts historical demand and inventory information into forecasts and actionable risk classifications.

---

## 3. Project Objectives

The main objectives are:

* Build a reproducible data-cleaning and preparation pipeline
* Perform exploratory data analysis and identify demand patterns
* Establish a seasonal-naive forecasting baseline
* Train and evaluate a machine-learning forecasting model
* Use rolling-origin backtesting for time-series evaluation
* Calculate stockout and overstock risk
* Quantify sales at risk and locked capital
* Build a non-technical planning dashboard
* Deploy a scoring API
* Communicate the results through an executive readout

---

## 4. Dataset

The project uses four main data sources provided for the engagement:

### Sales Data

Daily SKU-level sales information including demand and sales-related variables.

### SKU Master

Product-level information such as:

* SKU
* Category
* Subcategory
* Launch information
* Unit cost
* List price

### Calendar

Date-related information including:

* Week
* Month
* Season
* Holiday indicators
* Promotion events

### Inventory Snapshots

Inventory information including:

* On-hand quantity
* On-order quantity
* Lead time
* Reorder point

The data was cleaned and transformed into analysis-ready datasets before modelling.

---

## 5. Project Structure

```text
foresight/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_baseline.ipynb
│   └── 03_model.ipynb
│
├── src/
│   ├── pipeline.py
│   ├── forecast.py
│   └── risk.py
│
├── app/
│   └── Streamlit dashboard files
│
├── service/
│   └── FastAPI scoring service
│
├── reports/
│   ├── EDA_Memo
│   ├── Executive_Readout.pptx
│   └── model and risk output files
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 6. Methodology

The project follows a structured forecasting workflow:

```text
Raw Data
   ↓
Data Cleaning & Validation
   ↓
Exploratory Data Analysis
   ↓
Feature Engineering
   ↓
Seasonal-Naive Baseline
   ↓
Forecasting Model
   ↓
Rolling-Origin Backtesting
   ↓
Risk Scoring
   ↓
Dashboard + API
   ↓
Executive Readout
```

### Forecasting

A seasonal-naive model was established as the baseline.

A Random Forest forecasting model was then trained using engineered historical and calendar features.

The models were evaluated using **WAPE (Weighted Absolute Percentage Error)**.

Rolling-origin backtesting was used to evaluate model performance while respecting the time-series structure of the data.

---

## 7. Model Results

### Forecast Accuracy

| Model                   |       WAPE |
| ----------------------- | ---------: |
| Seasonal Naive Baseline | **11.97%** |
| Random Forest           | **10.99%** |

The Random Forest model reduced WAPE from 11.97% to 10.99%, representing an **8.23% improvement versus the seasonal-naive baseline**.

Rolling-origin backtesting produced an average WAPE of approximately **2.14%** for the evaluated backtest setup.

These results should be interpreted in the context of the evaluation period and available historical data.

---

## 8. Risk Scoring Results

The forecast was combined with inventory information to classify SKU-level inventory risk.

### Current Decision Categories

| Action           | SKU Count |
| ---------------- | --------: |
| Reorder Now      |    **30** |
| Markdown / Clear |     **8** |
| Healthy          |    **12** |

### Financial Impact

| Metric               |           Value |
| -------------------- | --------------: |
| Sales at Risk        | **₹5.25 crore** |
| Locked Capital       | **₹0.91 crore** |
| Total Value at Stake | **₹6.16 crore** |

These values translate model outputs into business-oriented inventory decisions.

---

## 9. Dashboard

A Streamlit planning dashboard was developed to allow users to explore:

* Forecast versus actual demand
* SKU-level forecasts
* Inventory risk
* Reorder recommendations
* Markdown / clearance recommendations
* Category-level information
* SKU-level filtering

The dashboard is publicly deployed.

**Dashboard URL:**
`https://foresight-demand-planning-7nfktzkgjsh786u7evj5ig.streamlit.app/`

---

## 10. Scoring API

A FastAPI service was deployed to provide forecast and risk information for individual SKUs.

Example endpoint:

```text
GET /forecast/{sku}
```

Example:

```text
GET /forecast/SKU001
```

The API returns forecast and associated risk information for the requested SKU.

The service also provides a root endpoint:

```text
GET /
```

which confirms that the service is running.

**API URL:**
`https://foresight-demand-planning.onrender.com/`

**Swagger documentation:**
Add the public `https://foresight-demand-planning.onrender.com/docs` URL here.

---

## 11. Reproducibility

### 1. Clone the repository

```bash
git clone https://github.com/vsharshitha
cd foresight
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the data pipeline

```bash
python src/pipeline.py
```

### 6. Run the forecasting workflow

```bash
python src/forecast.py
```

### 7. Run the risk scoring workflow

```bash
python src/risk.py
```

### 8. Run the Streamlit dashboard

```bash
streamlit run app/app.py
```

### 9. Run the FastAPI service

```bash
uvicorn service.api:app --reload
```

The exact filenames or commands should be adjusted if the implementation in the repository uses different entry points.

---

## 12. Key Assumptions

* Historical demand is used as the primary basis for forecasting.
* Forecast evaluation respects chronological ordering.
* Seasonal-naive forecasting is used as the baseline.
* Rolling-origin validation is used instead of a random train/test split for time-series evaluation.
* Future information is not intentionally used when generating historical model features.
* Risk classifications are based on forecast demand and available inventory information.
* Financial impact estimates depend on the assumptions and data supplied in the project dataset.

---

## 13. Limitations

The results should be interpreted with the following limitations:

* The dataset represents the provided engagement data and may not capture every real-world demand driver.
* Forecast accuracy can change when market conditions or customer behaviour change.
* Risk classifications depend on inventory assumptions and available inventory snapshots.
* The model does not perform automated purchase-order placement.
* The project does not include live integration with external client systems.
* Forecast performance should be monitored and recalibrated when new data becomes available.

---

## 14. Deliverables

| Deliverable | Description                     | Status   |
| ----------- | ------------------------------- | -------- |
| D1          | Reproducible data pipeline      | Complete |
| D2          | Data-quality & EDA insight memo | Complete |
| D3          | Demand forecast model           | Complete |
| D4          | Risk scoring                    | Complete |
| D5          | Planning dashboard              | Complete |
| D6          | Deployed scoring service        | Complete |
| D7          | Executive readout               | Complete |

---

## 15. Business Outcome

FORESIGHT converts demand forecasting into actionable inventory decisions.

The current analysis identifies:

* **30 SKUs** requiring reorder action
* **8 SKUs** requiring markdown / clearance attention
* **12 SKUs** classified as healthy
* **₹5.25 crore** in sales at risk
* **₹0.91 crore** in locked capital
* **₹6.16 crore** total value at stake

The project demonstrates an end-to-end data science workflow from raw data preparation through forecasting, risk scoring, deployment, and executive communication.

---

## 16. Technologies Used

* Python
* Pandas
* NumPy
* Scikit-learn
* Matplotlib
* Jupyter Notebook
* Streamlit
* FastAPI
* Uvicorn
* Git / GitHub

---

## 17. Author

**FORESIGHT — Data Science Project**

Developed as part of the Zidio Development project-based engagement.
