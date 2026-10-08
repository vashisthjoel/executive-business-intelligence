# Executive Business Intelligence Dashboard

[![Power BI](https://img.shields.io/badge/Power_BI-PBIP_v4.0-F2C811?logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Forecasting-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Analytics-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An enterprise-grade Business Intelligence and Advanced Analytics platform transforming 4,000 multi-category commercial transactions into executive decision-support tools. Built using Microsoft Power BI (Enhanced PBIR Project format), DAX, Python, RFM customer segmentation, and time-series forecasting.

---

## Overview

This project is an end-to-end Business Intelligence and Data Analytics solution engineered to transform raw transactional e-commerce sales records into executive-level insights, commercial diagnosis, and dynamic decision simulation. 

Rather than basic retrospective reporting, the platform bridges historical performance, behavioral customer segmentation (RFM), forward-looking machine learning projections, and real-time What-If promotional pricing analysis within a unified 4-page interactive dashboard.

---

## Business Problem

Executive leadership and commercial managers face critical questions when optimizing commercial trajectory and marketing capital:

- **Performance Tracking**: How are top-line gross revenue, net profit, and gross margins performing over time?
- **Customer Value**: Which customers represent the primary revenue engine, and what is their retention profile?
- **Customer Churn Risk**: Which valuable customers have lapsed, and what commercial intervention is required?
- **Product Profitability**: Which product categories drive true net margin versus those eroding profit through heavy promotions?
- **Forward Visibility**: What is the projected revenue and profit trajectory over the upcoming 6-month horizon?
- **Promotional Risk**: What are the bottom-line financial consequences of deepening or tightening discount policies before campaigns launch?

---

## Dashboard Architecture

The dashboard is structured into four focused analytical pages built in Microsoft Power BI Desktop using the modern Power BI Project (`.pbip`) format:

| Page | Objective | Key Visualizations |
|:---|:---|:---|
| **1. Executive Overview** | High-level commercial health and executive KPI tracking | Monthly revenue & margin trend line chart, category revenue & profit column chart, top market horizontal bar chart, payment method mix donut chart, global slicers. |
| **2. Customer & Product Analytics** | Behavioral customer segmentation and product margin breakdown | RFM segment revenue treemap, recency vs. monetary scatter plot, at-risk customer priority matrix with commercial action guidance, product hierarchy margin matrix. |
| **3. Trends & Forecast** | Historical growth trajectory and 6-month predictive runway | 20-month historical actuals vs. 6-month machine learning forecast with 95% prediction interval band, monthly projection data table, validation accuracy indicators. |
| **4. What-If Pricing & Discount Simulator** | Real-time commercial decision tool modeling discount adjustments | Disconnected What-If parameter slider (-10% to +10%), baseline vs. simulated KPI comparison cards, profit variance waterfall chart, category margin sensitivity matrix. |

---

## Analytics

### 1. RFM Customer Segmentation
- **Dataset**: 1,602 distinct customer entities across 4,000 verified orders.
- **Methodology**: Quintile ranking (1–5) based on **Recency** (days since last purchase relative to snapshot date `2026-09-01`), **Frequency** (total distinct orders), and **Monetary** (total net spend).
- **Behavioral Cohorts**: Customers classified into 11 actionable cohorts (Champions, Loyal Customers, At Risk, Potential Loyalists, Hibernating, etc.).
- **Auditing**: Reconciled master dimensional relationships to preserve 1-to-1 integrity without synthetic data fabrication.

### 2. Time-Series Revenue & Profit Forecasting
- **Historical Scope**: 20 months of monthly transaction data (January 2025 – August 2026).
- **Backtesting Methodology**: Chronological split (16 months training: `2025-01` to `2026-04`; 4 months validation test: `2026-05` to `2026-08`).
- **Models Evaluated**:
  1. 3-Month Moving Average (Baseline)
  2. Linear Trend (Ordinary Least Squares)
  3. Ridge Regularized Regression (Trend + Quarterly Seasonality)
  4. Holt's Linear Exponential Smoothing (L-BFGS-B optimization)
- **Champion Models**:
  - **Revenue Champion**: Ridge Regression with quarterly seasonality (**Validation MAPE: 10.07%**, MAE: Rp8.78M).
  - **Profit Champion**: 3-Month Moving Average (**Validation MAPE: 11.01%**, MAE: Rp3.37M).
- **Confidence Intervals**: 95% prediction intervals calculated via residual standard error.

### 3. What-If Discount & Price Elasticity Simulation
- **Dynamic Modeling**: Evaluates discount shifts ($\Delta_{\text{Discount}} \in [-10\%, +10\%]$) dynamically using high-performance DAX `SUMX` iterators and disconnected parameter tables.
- **Calculations**:
  $$\text{Simulated Revenue} = \sum (\text{Quantity} \times \text{UnitPrice} \times (1 - \text{Adjusted Discount}))$$
  $$\text{Simulated Profit} = \text{Simulated Revenue} - \text{Actual COGS}$$
  $$\text{Profit Variance} = \text{Simulated Profit} - \text{Actual Profit}$$
- **Zero Variance at Baseline**: Guaranteed mathematical consistency (Rp0.00 variance at 0% adjustment).

---

## Key Results

| Metric | Validated Finding |
|:---|:---|
| **Total Customers** | **1,602** unique verified customers |
| **Total Orders** | **4,000** completed transactions |
| **Total Historical Revenue** | **Rp1,685,022,050** |
| **Total Historical Profit** | **Rp573,923,050** |
| **Historical Profit Margin** | **34.06%** |
| **Average Order Value (AOV)** | **Rp421,256** |
| **Repeat Customer Rate** | **73.22%** (1,173 repeat buyers) |
| **Champions + Loyal Customers** | **35.71%** of customer base driving **58.34%** of total revenue (Rp983.0M) |
| **At-Risk Customer Cohort** | **188** customers representing **Rp265.2M** (15.74% of revenue) requiring win-back campaigns |
| **6-Month Forecast Revenue** | **Rp560,594,435** (Sep 2026 – Feb 2027) |
| **6-Month Forecast Profit** | **Rp190,575,470** |
| **Forecast Profit Margin** | **34.00%** (Stable commercial trajectory) |

---

## Technical Stack

- **Python (3.10+)**: Core analytical engine and modeling.
- **Pandas & NumPy**: Data cleaning, transformation, and vector arithmetic.
- **Scikit-learn**: Time-series regression modeling, Ridge regularization, and backtest evaluation metrics.
- **SciPy**: Parameter optimization for exponential smoothing.
- **Microsoft Power BI Desktop**: Report design, semantic modeling, and interactive visualization.
- **DAX (Data Analysis Expressions)**: 45+ measures covering time intelligence, RFM cross-filtering, and What-If simulation iterators.
- **Power Query (M)**: Star schema data extraction, typing, and source transformations.
- **Power BI Project (PBIP / PBIR v4.0)**: Modern developer-friendly text-based report and semantic model source control.

---

## Project Structure

```
executive-business-intelligence/
├── analytics/
│   ├── forecasting.py               # Time-series forecasting & backtesting engine
│   ├── requirements.txt             # Python analytical dependencies
│   ├── rfm_analysis.py              # RFM customer segmentation engine
│   └── outputs/
│       ├── customer_rfm.csv         # Reconciled RFM cohort output (1,602 records)
│       └── monthly_forecast.csv     # 6-month forward projections (26 records)
├── data/
│   ├── dim_customer.csv             # Customer dimension (1,602 entities)
│   ├── dim_date.csv                 # Date calendar dimension (607 days)
│   ├── dim_product.csv              # Product dimension (25 SKUs)
│   └── fact_sales.csv               # Transactional sales facts (4,000 orders)
├── Executive_BI_Dashboard.pbip      # Native Power BI Project file
├── Executive_BI_Dashboard.Report/   # PBIR v4.0 report definition, pages, and visuals
├── Executive_BI_Dashboard.SemanticModel/ # TMDL tabular data model & relationships
├── dashboard_preview.xlsx           # Interactive Excel workbook mirror
├── dashboard_spec.md                # 4-page dashboard UX/UI specification
├── dax_measures.txt                 # Complete DAX measure code repository
├── power_bi_build_guide.md          # Visual binding & configuration guide
├── power_query_scripts.m            # Standalone Power Query M scripts
├── .gitignore                       # Clean repository exclusions
└── README.md                        # Portfolio documentation
```

---

## Reproducibility

### 1. Environment Setup
Install required Python packages in a virtual environment:

```bash
# Clone the repository
git clone https://github.com/vashisthjoel/executive-business-intelligence.git
cd executive-business-intelligence

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r analytics/requirements.txt
```

### 2. Execute Analytics Pipelines
Run the segmentation and forecasting scripts from the project root:

```bash
# 1. Generate RFM segmentation output
python analytics/rfm_analysis.py

# 2. Run time-series benchmark and generate 6-month forecast
python analytics/forecasting.py
```

Outputs are automatically written to `analytics/outputs/customer_rfm.csv` and `analytics/outputs/monthly_forecast.csv`.

---

## Power BI Integration

This project uses the modern **Microsoft Power BI Enhanced Report Format (PBIR / PBIP)**:
1. Open [`Executive_BI_Dashboard.pbip`](Executive_BI_Dashboard.pbip) directly in Power BI Desktop (May 2024 release or newer with PBIP enabled).
2. The report loads the localized tabular model from `Executive_BI_Dashboard.SemanticModel/` and visuals from `Executive_BI_Dashboard.Report/`.
3. If source paths require updating, modify the root path in Power Query (`power_query_scripts.m` or Advanced Editor) and click **Refresh**.

---

## Business Insights

1. **Revenue Concentration in Top Cohorts**: 35.71% of customers (Champions and Loyalists) generate 58.34% of revenue (Rp983.0M). These customers should be excluded from margin-eroding blanket discounts and nurtured through VIP loyalty milestones and early access programs.
2. **Actionable At-Risk Intervention**: 188 previously active customers represent Rp265.2M in cumulative spending but have not transacted in over 300 days. A dedicated win-back campaign with category-specific reactivation incentives offers an estimated 4x return on marketing spend.
3. **Product Margin Optimization**: Gross margins remain healthy at 34.06% overall, with **Home & Living** and **Electronics** demonstrating high volume and price stability.
4. **Discount Elasticity Discipline**: What-If sensitivity indicates that tightening discount rates by 1–2 percentage points on inelastic categories protects bottom-line margins with minimal order volume attrition.
5. **Predictable Growth Runway**: Chronological forecasting projects steady expansion over the next 6 months, reaching Rp95.2M in monthly revenue by February 2027 with a consistent 34.00% gross margin.

---

## Skills Demonstrated

- **Data Cleaning & Engineering**: Ingesting, cleaning, and validating transactional datasets; handling date types, missing customer records, and numeric precision.
- **Dimensional Modeling**: Designing an optimized star schema with 1-to-many single-direction relationships.
- **DAX Engineering**: Developing complex calculated measures, time intelligence, iterators (`SUMX`), and disconnected parameter slicers.
- **Exploratory Data Analysis (EDA)**: Statistical distribution analysis, correlation evaluation, and basket size modeling.
- **Customer Segmentation & RFM**: Quantile scoring and behavioral clustering.
- **Time-Series Forecasting**: Chronological cross-validation, baseline benchmarking, Ridge regularization, and prediction intervals.
- **Executive Business Intelligence**: Designing intuitive, decision-oriented dashboard layouts with strict visual hierarchy.
- **Data Storytelling & Decision Support**: Translating technical analytics into actionable commercial strategies for leadership.

---

## Disclaimer

This project is part of a professional analytics portfolio. The dataset, transactional records, and analytical models are structured for demonstration, analytical rigor, and educational purposes.
