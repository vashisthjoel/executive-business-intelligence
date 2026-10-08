# Power BI Dashboard Build Specification

## Executive Summary
This document specifies the architecture, data model, visual layout, and interactivity rules for the **Executive Business Intelligence Dashboard** (Portfolio #5). The dashboard is designed across four executive-facing pages to provide end-to-end commercial clarity: high-level performance tracking, customer behavioral segmentation, time-series forecasting, and an interactive What-If scenario simulator.

---

## Page 1 — Executive Overview
**Objective**: Provide senior leadership with immediate visibility into top-line commercial health, revenue drivers, and profitability breakdown.

### Top KPI Cards (Cards / Multi-row Cards)
- **Total Revenue**: `[Total Revenue]` (formatted as IDR currency, e.g., Rp1.69B)
- **Total Profit**: `[Total Profit]` (formatted as IDR currency, e.g., Rp573.9M)
- **Profit Margin %**: `[Profit Margin %]` (target baseline: 34.06%)
- **Total Orders**: `[Total Orders]` (4,000 distinct orders)
- **Average Order Value (AOV)**: `[Average Order Value]` (Rp421,256)
- **Units Sold**: `[Units Sold]` (6,291 units)

### Core Visualizations
1. **Revenue & Profit Trend (Line & Clustered Column Chart)**:
   - Shared Axis: `DimDate[YearMonth]`
   - Column Values: `[Total Revenue]`
   - Line Values: `[Profit Margin %]` (Secondary axis)
   - Tooltip: `[Total Profit]`, `[MoM Revenue Growth %]`
2. **Category Profitability Matrix (Clustered Column Chart)**:
   - X-Axis: `DimProduct[Category]`
   - Y-Axis: `[Total Revenue]`, `[Total Profit]`
   - Data labels enabled for executive clarity.
3. **Top 10 Products by Revenue (Horizontal Clustered Bar Chart)**:
   - Y-Axis: `DimProduct[Product]`
   - X-Axis: `[Total Revenue]`
   - Tooltip: `[Profit Margin %]`, `[Product Rank by Revenue]`
4. **Geographic Distribution (Bar Chart / Filled Map)**:
   - Category: `DimCustomer[City]`
   - Values: `[Total Revenue]`
   - Highlight: Top tier markets (Jakarta, Surabaya, Medan, Denpasar, Makassar).
5. **Payment Method Mix (Donut Chart)**:
   - Legend: `FactSales[PaymentMethod]`
   - Values: `[Total Revenue]`
   - Detail Labels: Category & Percentage of Total.
6. **Executive Global Slicers**:
   - `DimDate[Year]`, `DimDate[Quarter]`, `DimProduct[Category]`, `DimCustomer[City]`

---

## Page 2 — Customer & Product Performance (Behavioral Segmentation)
**Objective**: Evaluate customer lifetime engagement, identify churn risk using RFM segmentation, and guide retention/cross-sell commercial actions.

### Top KPI Cards
- **Unique Customers**: `[Unique Customers]` (1,602 total)
- **Revenue per Customer**: `[Revenue per Customer]` (Rp1,051,824)
- **Champion Customers**: `CALCULATE([Segment Customers], CustomerRFM[RFM_Segment] = "Champions")` (255 customers)
- **At-Risk Revenue**: `CALCULATE([Segment Revenue], CustomerRFM[RFM_Segment] = "At Risk")` (Rp265.2M / 15.74% of revenue)

### Core Visualizations
1. **RFM Segment Revenue Contribution (Treemap)**:
   - Category: `CustomerRFM[RFM_Segment]`
   - Values: `[Segment Revenue]`
   - Color Saturation: `[Segment Profit Margin %]`
   - Tooltip: `[Segment Customers]`, `[Segment Revenue Share %]`, `[Segment Avg Frequency Orders]`
2. **Customer Value vs. Recency Scatter Plot**:
   - X-Axis: `CustomerRFM[Recency_Days]` (Inverted scale: 0 to 600 days)
   - Y-Axis: `CustomerRFM[Monetary_Revenue]` (IDR)
   - Size: `CustomerRFM[Frequency_Orders]`
   - Legend: `CustomerRFM[RFM_Segment]`
3. **At-Risk Customer Priority Table (Matrix / Table)**:
   - Rows: `CustomerRFM[CustomerID]`, `CustomerRFM[City]`, `CustomerRFM[RFM_Segment]`
   - Values: `CustomerRFM[Monetary_Revenue]`, `CustomerRFM[Recency_Days]`, `CustomerRFM[Frequency_Orders]`, `CustomerRFM[Recommended_Action]`
   - Conditional Formatting: Flag customers with Recency > 180 days and Revenue > Rp1.5M.
4. **Product Hierarchy Performance (Matrix)**:
   - Rows: `DimProduct[Category]` > `DimProduct[Product]`
   - Values: `[Total Revenue]`, `[Category Revenue Share %]`, `[Total Profit]`, `[Profit Margin %]`, `[Units Sold]`
5. **Slicers**:
   - `CustomerRFM[RFM_Segment]`, `DimCustomer[City]`, `DimProduct[Category]`

---

## Page 3 — Trend, Growth & Predictive Projections
**Objective**: Analyze historical performance dynamics (MoM, YoY, Cumulative) and display the 6-month predictive revenue & profit forecasts.

### Top KPI Cards
- **Latest MoM Revenue Growth**: `[MoM Revenue Growth %]` (+7.02% in Aug 2026)
- **Latest YoY Revenue Growth**: `[YoY Revenue Growth %]` (+19.76% in Aug 2026 vs Aug 2025)
- **6-Month Projected Revenue**: `SUM(MonthlyForecast[Revenue])` where `Period_Type = "Forecast"` (Rp560.6M)
- **6-Month Projected Profit**: `SUM(MonthlyForecast[Profit])` where `Period_Type = "Forecast"` (Rp190.6M)

### Core Visualizations
1. **Historical Actuals vs. 6-Month Forecast with 95% Confidence Band (Line Chart)**:
   - X-Axis: `MonthlyForecast[YearMonth]`
   - Line 1: `MonthlyForecast[Revenue]` (Actuals up to Aug 2026, Projections Sep 2026 - Feb 2027)
   - Shaded Band: `MonthlyForecast[Revenue_Lower_95]` and `MonthlyForecast[Revenue_Upper_95]`
   - Legend / Line Style: Solid for Historical, Dashed for Forecast.
2. **Monthly Growth Dynamics (Waterfall / Clustered Bar Chart)**:
   - X-Axis: `DimDate[YearMonth]`
   - Values: `[MoM Revenue Growth %]`
   - Color coding: Positive growth (Green), Negative growth (Red).
3. **Running Cumulative Revenue (Area Chart)**:
   - X-Axis: `DimDate[Date]`
   - Values: `[Running Revenue]`
4. **Profit Margin Trajectory (Line Chart with Reference Line)**:
   - X-Axis: `DimDate[YearMonth]`
   - Line: `[Profit Margin %]`
   - Reference Line: Historical Mean (34.06%).

---

## Page 4 — What-If Discount & Price Simulator (Executive Decision Tool)
**Objective**: Empower commercial leadership to simulate the financial consequences of discount adjustments and price changes on gross revenue, net profit, and profit margin without modifying historical source data.

### Interactive What-If Controls (Disconnected Slicers)
1. **Discount Adjustment Slider**:
   - Bound to: `'Discount Parameter'[Discount Parameter]`
   - Range: `-10%` to `+10%` (Step: `1%`, Default: `0%`)
   - Description: Simulates lowering discounts (tightening promotions) or deepening discounts.
2. **Price Adjustment Slider (Optional Dual-Factor)**:
   - Bound to: `'Price Parameter'[Price Parameter]`
   - Range: `-20%` to `+20%` (Step: `5%`, Default: `0%`)
3. **Scope Slicers**:
   - `DimProduct[Category]`, `DimCustomer[City]`, `DimDate[Year]`

### Dynamic Comparison KPI Cards
- **Simulated Revenue**: `[Simulated Revenue]`
- **Revenue Impact**: `[Revenue Variance]` and `[Revenue Variance %]` (Green if positive, Red if negative)
- **Simulated Profit**: `[Simulated Profit]`
- **Profit Impact**: `[Profit Variance]` and `[Profit Variance %]`
- **Simulated Profit Margin**: `[Simulated Profit Margin %]`
- **Margin Impact**: `[Margin Impact pts]` (e.g., -1.25% pts)

### Core Visualizations
1. **Commercial Impact Waterfall Chart**:
   - Category: Breakdown stages (`Baseline Profit`, `Revenue Change from Discount`, `Simulated Profit`)
   - Visualizes exact IDR dollar-for-dollar profit sensitivity.
2. **Category Margin Sensitivity Matrix (Matrix / Table)**:
   - Rows: `DimProduct[Category]`
   - Columns: Scenario Discount Delta (`-5%`, `-2%`, `0%`, `+2%`, `+5%`)
   - Values: `[Simulated Profit Margin %]` and `[Simulated Profit]`
3. **Product Elasticity Table**:
   - Rows: `DimProduct[Product]`
   - Values: `[Total Revenue]`, `[Simulated Revenue]`, `[Profit Variance]`, `[Simulated Profit Margin %]`
   - Enables category managers to see which products withstand promotional adjustments best.

---

## Data Model & Relationship Architecture
The data model follows an optimized **Star Schema** with dimension tables filtering the central fact table via **single-direction 1-to-many relationships**, extended with the analytical and parameter tables:

```
[DimDate] (1) --------< (*) [FactSales]
                          |
[DimCustomer] (1) -----< (*)   ^
  |                            |
  | (1:1)                      |
  v                            |
[CustomerRFM]                  |
                               |
[DimProduct] (1) ------< (*) --+

[MonthlyForecast] (Independent analytical table for Page 3)
[Discount Parameter] (Disconnected What-If table for Page 4)
[Price Parameter] (Disconnected What-If table for Page 4)
```

### Table Relationships:
1. `DimDate[DateKey]` (1) to `FactSales[DateKey]` (*) — Single direction (`DimDate` filters `FactSales`).
2. `DimCustomer[CustomerKey]` (1) to `FactSales[CustomerKey]` (*) — Single direction (`DimCustomer` filters `FactSales`).
3. `DimProduct[ProductKey]` (1) to `FactSales[ProductKey]` (*) — Single direction (`DimProduct` filters `FactSales`).
4. `CustomerRFM[CustomerKey]` (1) to `DimCustomer[CustomerKey]` (1) — 1-to-1 relationship, or imported as an enriched customer dimension.
5. `Discount Parameter` and `Price Parameter`: Disconnected tables with no physical relationships, evaluated dynamically using `SELECTEDVALUE` within DAX iterator functions (`SUMX`).

---

## Format & Styling Standards
- **Currency Format**: Indonesian Rupiah (`Rp#,##0` or `Rp#,##0.00` for averages).
- **Percentages**: Two decimal places (`0.00%`).
- **Color Palette**:
  - Primary / Neutral: Dark Slate (`#1E293B`)
  - Accent / Revenue: Navy Blue (`#2563EB`)
  - Profit / Positive: Emerald Green (`#10B981`)
  - Cost / Negative: Crimson Red (`#EF4444`)
  - Secondary Accents: Amber (`#F59E0B`), Violet (`#8B5CF6`)
- **Typography**: Segoe UI or Aptos (standard enterprise Power BI clean typography).
