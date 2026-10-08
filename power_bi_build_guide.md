# Power BI Desktop Implementation & Build Guide
## Executive Business Intelligence Dashboard (Portfolio #5)

This guide documents the complete technical setup, data modeling, DAX architecture, and visual design specifications to assemble the 4-page **Executive Business Intelligence Dashboard** in **Power BI Desktop**.

---

## 1. Quick Start Options

### Option A: Open Native Power BI Project (Recommended)
This repository includes a pre-configured Microsoft **Power BI Project (`.pbip`)**:
- Double-click [`Executive_BI_Dashboard.pbip`](file:///D:/DataAnalyst/Data-Analyst-Portfolio-main/05-executive-business-intelligence/Executive_BI_Dashboard.pbip) on a computer with Power BI Desktop installed.
- Power BI Desktop automatically loads the complete **TMSL Tabular Model** (`Executive_BI_Dashboard.SemanticModel/model.bim`), establishes all 4 star-schema relationships, defines all 45 DAX measures in `_Measures`, and initializes the 4-page layout structure.

### Option B: Clean Import via Power Query M
If starting from a blank Power BI Desktop file (`.pbix`):
1. Open Power BI Desktop -> **Home** -> **Transform Data** -> **Advanced Editor**.
2. Copy and paste each query from [`power_query_scripts.m`](file:///D:/DataAnalyst/Data-Analyst-Portfolio-main/05-executive-business-intelligence/power_query_scripts.m) into a new Blank Query:
   - `DimDate` (from `data/dim_date.csv`)
   - `DimCustomer` (from `data/dim_customer.csv`)
   - `DimProduct` (from `data/dim_product.csv`)
   - `FactSales` (from `data/fact_sales.csv`)
   - `CustomerRFM` (from `analytics/outputs/customer_rfm.csv`)
   - `MonthlyForecast` (from `analytics/outputs/monthly_forecast.csv`)
3. Click **Close & Apply**.

---

## 2. Data Model & Relationship Configuration

### Relationship Architecture (Star Schema)
In the **Model View**, verify and configure the following relationships:

| From Table (Many) | Foreign Key | To Table (One) | Primary Key | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `FactSales` | `DateKey` | `DimDate` | `DateKey` | Many to One (`*:1`) | Single (`DimDate` filters `FactSales`) |
| `FactSales` | `CustomerKey` | `DimCustomer` | `CustomerKey` | Many to One (`*:1`) | Single (`DimCustomer` filters `FactSales`) |
| `FactSales` | `ProductKey` | `DimProduct` | `ProductKey` | Many to One (`*:1`) | Single (`DimProduct` filters `FactSales`) |
| `CustomerRFM` | `CustomerKey` | `DimCustomer` | `CustomerKey` | One to One (`1:1`) | Single (`DimCustomer` filters `CustomerRFM`) |

> **IMPORTANT ARCHITECTURAL RULE — Single-Direction Filtering**:
> Do **NOT** enable bidirectional cross-filtering between `CustomerRFM` and `DimCustomer`/`FactSales`. Bidirectional filtering creates ambiguous filter paths, slows query performance, and can produce unpredictable totals.
> Cross-filtering between `CustomerRFM` and `FactSales` is handled cleanly in DAX using explicit `TREATAS` (see Section 3).

### Dimension Configuration
1. **Mark as Date Table**:
   - Right-click `DimDate` in the Fields pane -> **Mark as date table** -> Select Date Column: `Date`.
2. **Sort Month Name Chronologically**:
   - Select column `DimDate[MonthName]`.
   - Go to **Column tools** -> **Sort by column** -> Select `MonthNumber`.

### Disconnected Parameter Table
1. Go to **Modeling** tab -> **New Parameter** -> **Numeric range**:
   - Name: `Discount Parameter`
   - Data type: `Decimal number`
   - Minimum: `-0.10` (-10%)
   - Maximum: `0.10` (+10%)
   - Increment: `0.01` (1%)
   - Default: `0.00` (0%)
2. *(Alternative DAX Calculated Table)*:
   ```dax
   Discount Parameter = GENERATESERIES(-0.10, 0.10, 0.01)
   ```

---

## 3. DAX Measures Library & Display Folders

Create a dedicated table named `_Measures` and add all measures from [`dax_measures.txt`](file:///D:/DataAnalyst/Data-Analyst-Portfolio-main/05-executive-business-intelligence/dax_measures.txt). Organize them into display folders:

### Folder: `01. Financials`
- **Total Revenue**: `SUM(FactSales[Revenue])` (Format: `"Rp"#,##0`)
- **Total Profit**: `SUM(FactSales[Profit])` (Format: `"Rp"#,##0`)
- **Total COGS**: `SUM(FactSales[COGS])` (Format: `"Rp"#,##0`)
- **Profit Margin %**: `DIVIDE([Total Profit], [Total Revenue], 0)` (Format: `0.00%`)
- **Total Orders**: `DISTINCTCOUNT(FactSales[OrderID])` (Format: `#,##0`)
- **Units Sold**: `SUM(FactSales[Quantity])` (Format: `#,##0`)
- **Average Order Value**: `DIVIDE([Total Revenue], [Total Orders], 0)` (Format: `"Rp"#,##0`)
- **Unique Customers**: `DISTINCTCOUNT(FactSales[CustomerKey])` (Format: `#,##0`)
- **Customer Count**: `[Unique Customers]` (Format: `#,##0`)
- **Revenue per Customer**: `DIVIDE([Total Revenue], [Unique Customers], 0)` (Format: `"Rp"#,##0`)
- **Average Customer Revenue**: `[Revenue per Customer]` (Format: `"Rp"#,##0`)
- **Average Orders per Customer**: `DIVIDE([Total Orders], [Unique Customers], 0)` (Format: `#,##0.00`)
- **Repeat Customers**:
  ```dax
  CALCULATE(
      DISTINCTCOUNT(FactSales[CustomerKey]),
      FILTER(VALUES(FactSales[CustomerKey]), CALCULATE(DISTINCTCOUNT(FactSales[OrderID])) > 1)
  )
  ```
- **Repeat Customer Rate**: `DIVIDE([Repeat Customers], [Unique Customers], 0)` (Format: `0.00%`)

### Folder: `02. Time Intelligence`
- **Revenue Previous Month**: `CALCULATE([Total Revenue], DATEADD(DimDate[Date], -1, MONTH))`
- **MoM Revenue Growth %**: `DIVIDE([Total Revenue] - [Revenue Previous Month], [Revenue Previous Month], 0)` (Format: `+0.00%;-0.00%;0.00%`)
- **Revenue Previous Year**: `CALCULATE([Total Revenue], DATEADD(DimDate[Date], -1, YEAR))`
- **YoY Revenue Growth %**: `DIVIDE([Total Revenue] - [Revenue Previous Year], [Revenue Previous Year], 0)` (Format: `+0.00%;-0.00%;0.00%`)
- **Running Revenue**: `CALCULATE([Total Revenue], FILTER(ALLSELECTED(DimDate[Date]), DimDate[Date] <= MAX(DimDate[Date])))`
- **Running Total**: `[Running Revenue]`

### Folder: `03. Rankings & Share`
- **Category Revenue Share %**: `DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(DimProduct[Category])), 0)`
- **Customer Rank by Revenue**: `RANKX(ALL(DimCustomer[CustomerID]), [Total Revenue], , DESC)`
- **Product Rank by Revenue**: `RANKX(ALL(DimProduct[Product]), [Total Revenue], , DESC)`

### Folder: `04. What-If Simulator`
- **Discount Parameter Value**: `SELECTEDVALUE('Discount Parameter'[Discount Parameter], 0)`
- **Selected Discount Adjustment %**:
  ```dax
  VAR RawVal = [Discount Parameter Value]
  RETURN IF(ABS(RawVal) > 1, RawVal / 100, RawVal)
  ```
- **Simulated Revenue**:
  ```dax
  VAR DiscAdj = [Selected Discount Adjustment %]
  RETURN
  SUMX(
      FactSales,
      FactSales[Quantity] * FactSales[UnitPrice] * (1 - MAX(0, MIN(1.0, FactSales[DiscountPct] + DiscAdj)))
  )
  ```
- **Simulated COGS**: `SUM(FactSales[COGS])`
- **Simulated Profit**: `[Simulated Revenue] - [Simulated COGS]`
- **Simulated Profit Margin %**: `DIVIDE([Simulated Profit], [Simulated Revenue], 0)`
- **Revenue Variance**: `[Simulated Revenue] - [Total Revenue]`
- **Revenue Variance %**: `DIVIDE([Revenue Variance], [Total Revenue], 0)`
- **Profit Variance**: `[Simulated Profit] - [Total Profit]`
- **Profit Variance %**: `DIVIDE([Profit Variance], [Total Profit], 0)`
- **Margin Impact pts**: `[Simulated Profit Margin %] - [Profit Margin %]`

### Folder: `05. RFM Segmentation`
- **Segment Customers**: `DISTINCTCOUNT(CustomerRFM[CustomerKey])`
- **Segment Revenue**: `SUM(CustomerRFM[Monetary_Revenue])`
- **Segment Profit**: `SUM(CustomerRFM[Total_Profit])`
- **Segment Revenue Share %**: `DIVIDE([Segment Revenue], CALCULATE([Segment Revenue], ALL(CustomerRFM)), 0)`
- **Segment Profit Margin %**: `DIVIDE([Segment Profit], [Segment Revenue], 0)`
- **Segment Avg Recency Days**: `AVERAGE(CustomerRFM[Recency_Days])`
- **Segment Avg Frequency Orders**: `AVERAGE(CustomerRFM[Frequency_Orders])`
- **Segment Avg Monetary Spend**: `AVERAGE(CustomerRFM[Monetary_Revenue])`
- **Revenue (RFM Cross-Filtered)**:
  ```dax
  CALCULATE([Total Revenue], TREATAS(VALUES(CustomerRFM[CustomerKey]), FactSales[CustomerKey]))
  ```
- **Profit (RFM Cross-Filtered)**:
  ```dax
  CALCULATE([Total Profit], TREATAS(VALUES(CustomerRFM[CustomerKey]), FactSales[CustomerKey]))
  ```
- **Orders (RFM Cross-Filtered)**:
  ```dax
  CALCULATE([Total Orders], TREATAS(VALUES(CustomerRFM[CustomerKey]), FactSales[CustomerKey]))
  ```

### Folder: `06. Forecasting`
- **Forecast Revenue Total**: `CALCULATE(SUM(MonthlyForecast[Revenue]), MonthlyForecast[Period_Type] = "Forecast")`
- **Forecast Profit Total**: `CALCULATE(SUM(MonthlyForecast[Profit]), MonthlyForecast[Period_Type] = "Forecast")`
- **Forecast Margin %**: `DIVIDE([Forecast Profit Total], [Forecast Revenue Total], 0)`

---

## 4. Visual Layout Specifications (4 Pages)

### Page 1 — Executive Overview
*Answers: "What is the overall commercial and financial health of the business?"*

1. **Header Banner**: Textbox: `"Executive Business Intelligence Dashboard | Commercial Overview"`
2. **Top KPI Row** (8 Cards / Multi-row card across top):
   - Card 1: `[Total Revenue]` -> `Rp1,685,022,050`
   - Card 2: `[Total Profit]` -> `Rp573,923,050`
   - Card 3: `[Profit Margin %]` -> `34.06%`
   - Card 4: `[Total Orders]` -> `4,000`
   - Card 5: `[Average Order Value]` -> `Rp421,256`
   - Card 6: `[Units Sold]` -> `6,291`
   - Card 7: `[Repeat Customer Rate]` -> `73.22%`
   - Card 8: `[MoM Revenue Growth %]` -> `+7.02%` (Aug 2026)
3. **Monthly Trend Visual (Line Chart)**:
   - X-Axis: `DimDate[YearMonth]`
   - Y-Axis: `[Total Revenue]`, `[Total Profit]`
   - Secondary Y-Axis: `[Profit Margin %]`
4. **Category Breakdown (Clustered Column Chart)**:
   - X-Axis: `DimProduct[Category]`
   - Y-Axis: `[Total Revenue]`, `[Total Profit]`
5. **Geographic Performance (Clustered Bar Chart)**:
   - Y-Axis: `DimCustomer[City]`
   - X-Axis: `[Total Revenue]`
6. **Payment Mix (Donut Chart)**:
   - Legend: `FactSales[PaymentMethod]`
   - Values: `[Total Revenue]`
7. **Slicers Panel**: `DimDate[Year]`, `DimDate[Quarter]`, `DimProduct[Category]`, `DimCustomer[City]`.

---

### Page 2 — Customer & Product Analytics
*Answers: "Who are our customers, what are their behavioral patterns, and where is churn risk concentrated?"*

1. **Customer KPI Row**:
   - Card 1: `[Customer Count]` -> `1,602`
   - Card 2: `[Average Customer Revenue]` -> `Rp1,051,824`
   - Card 3: `[Average Orders per Customer]` -> `2.50`
   - Card 4: `[Repeat Customer Rate]` -> `73.22%`
2. **RFM Segment Revenue Treemap**:
   - Category: `CustomerRFM[RFM_Segment]`
   - Values: `[Segment Revenue]`
   - Tooltips: `[Segment Customers]`, `[Segment Revenue Share %]`, `[Segment Profit Margin %]`
3. **RFM Recency vs. Spend Scatter Plot**:
   - Legend: `CustomerRFM[RFM_Segment]`
   - X-Axis: `[Segment Avg Recency Days]`
   - Y-Axis: `[Segment Revenue]`
   - Size: `[Segment Customers]`
4. **At-Risk Priority Action Table**:
   - Visual Type: Table
   - Columns: `CustomerRFM[CustomerID]`, `CustomerRFM[City]`, `CustomerRFM[RFM_Segment]`, `CustomerRFM[Recency_Days]`, `CustomerRFM[Monetary_Revenue]`, `CustomerRFM[Recommended_Action]`
   - Filter on Visual: `CustomerRFM[RFM_Segment]` in (`At Risk`, `Cannot Lose Them`)
5. **Product Profitability Hierarchy (Matrix)**:
   - Rows: `DimProduct[Category]` -> `DimProduct[Product]`
   - Values: `[Total Revenue]`, `[Total Profit]`, `[Profit Margin %]`, `[Units Sold]`

---

### Page 3 — Trends & Forecast
*Answers: "Where is commercial performance heading over the next 6 months?"*

1. **Forecast KPI Cards**:
   - Card 1: `[Forecast Revenue Total]` -> `Rp560,594,435`
   - Card 2: `[Forecast Profit Total]` -> `Rp190,575,470`
   - Card 3: `[Forecast Margin %]` -> `34.00%`
   - Card 4 (Model Validation Summary Textbox):
     `Revenue MAPE: 10.07% (Ridge Champion)`
     `Profit MAPE: 11.01% (3M Moving Average)`
2. **Revenue Actuals vs. 6-Month Forecast with 95% CI (Line Chart)**:
   - X-Axis: `MonthlyForecast[YearMonth]`
   - Y-Axis: `MonthlyForecast[Revenue]`, `MonthlyForecast[Revenue_Lower_95]`, `MonthlyForecast[Revenue_Upper_95]`
   - Formatting: Solid line for Revenue, dotted/light shaded bands for lower/upper prediction intervals.
3. **Profit Actuals vs. 6-Month Forecast (Line Chart)**:
   - X-Axis: `MonthlyForecast[YearMonth]`
   - Y-Axis: `MonthlyForecast[Profit]`, `MonthlyForecast[Profit_Lower_95]`, `MonthlyForecast[Profit_Upper_95]`
4. **Monthly Projection Details Table**:
   - Columns: `MonthlyForecast[YearMonth]`, `MonthlyForecast[Period_Type]`, `MonthlyForecast[Revenue]`, `MonthlyForecast[Profit]`, `MonthlyForecast[Profit_Margin_Pct]`, `MonthlyForecast[MoM_Growth_Pct]`

---

### Page 4 — What-If Pricing & Discount Simulator
*Answers: "What happens to revenue and bottom-line margin if we adjust promotional discount depth?"*

1. **Interactive Control**:
   - Slicer: Bound to `'Discount Parameter'[Discount Parameter]`.
   - Visual style: Slider with single-value selector (-10% to +10%).
2. **Simulated Scenario KPI Cards**:
   - Card 1: `[Simulated Revenue]`
   - Card 2: `[Simulated Profit]`
   - Card 3: `[Simulated Profit Margin %]`
   - Card 4: `[Revenue Variance %]`
   - Card 5: `[Profit Variance]` (Format: Green if positive, Red if negative)
   - Card 6: `[Margin Impact pts]`
3. **Commercial Profit Waterfall Visual**:
   - Visual Type: Waterfall Chart
   - Category / Breakdown: `Baseline Profit` -> `Profit Variance` -> `Simulated Profit`
   - Y-Axis: Value
4. **Baseline vs. Simulated Profit by Category (Clustered Column Chart)**:
   - X-Axis: `DimProduct[Category]`
   - Y-Axis: `[Total Profit]`, `[Simulated Profit]`
5. **Category & Product Sensitivity Matrix**:
   - Rows: `DimProduct[Category]` -> `DimProduct[Product]`
   - Values: `[Total Revenue]`, `[Simulated Revenue]`, `[Revenue Variance]`, `[Total Profit]`, `[Simulated Profit]`, `[Profit Variance]`, `[Profit Margin %]`, `[Simulated Profit Margin %]`

---

## 5. Audit & Validation Checklist

Before presenting or publishing, verify these exact numbers:
1. **Total Revenue**: `Rp1,685,022,050`
2. **Total Profit**: `Rp573,923,050`
3. **Profit Margin**: `34.0656%`
4. **Total Orders**: `4,000`
5. **Total Customers**: `1,602`
6. **What-If at 0% Discount Adjustment**:
   - `Simulated Revenue` = `Rp1,685,022,050` (Variance: `Rp0.00`)
   - `Simulated Profit` = `Rp573,923,050` (Variance: `Rp0.00`)
   - `Simulated Profit Margin %` = `34.0656%` (Variance: `0.00% pts`)
7. **RFM Segment Total Revenue**: `Rp1,685,022,050` (across 1,602 customers)
8. **6-Month Forecast Horizon**: `2026-09` through `2027-02` (Projected Revenue: `Rp560,594,435`)
