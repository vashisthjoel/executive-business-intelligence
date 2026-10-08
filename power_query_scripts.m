// ==============================================================================
// Power Query M Ingestion Scripts
// Portfolio #5 — Executive Business Intelligence Dashboard
// ==============================================================================
// Instructions:
// In Power BI Desktop: Home > Transform Data > Advanced Editor
// Paste each query into a new Blank Query or update source paths.
//
// Root Project Folder Parameter:
// Change DataFolder to your local path if needed:
// Default: "D:\DataAnalyst\Data-Analyst-Portfolio-main\05-executive-business-intelligence"
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. DataFolder Parameter (Optional Helper)
// ------------------------------------------------------------------------------
let
    DataFolder = "D:\DataAnalyst\Data-Analyst-Portfolio-main\05-executive-business-intelligence"
in
    DataFolder

// ------------------------------------------------------------------------------
// 2. DimDate Query
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\DataAnalyst\Data-Analyst-Portfolio-main\05-executive-business-intelligence\data\dim_date.csv"), [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"DateKey", Int64.Type},
        {"Date", type date},
        {"Year", Int64.Type},
        {"Quarter", type text},
        {"MonthNumber", Int64.Type},
        {"MonthName", type text},
        {"YearMonth", type text}
    })
in
    ChangeTypes

// ------------------------------------------------------------------------------
// 3. DimCustomer Query
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\DataAnalyst\Data-Analyst-Portfolio-main\05-executive-business-intelligence\data\dim_customer.csv"), [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"CustomerKey", Int64.Type},
        {"CustomerID", type text},
        {"City", type text},
        {"CustomerSegment", type text}
    })
in
    ChangeTypes

// ------------------------------------------------------------------------------
// 4. DimProduct Query
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\DataAnalyst\Data-Analyst-Portfolio-main\05-executive-business-intelligence\data\dim_product.csv"), [Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"ProductKey", Int64.Type},
        {"Product", type text},
        {"Category", type text}
    })
in
    ChangeTypes

// ------------------------------------------------------------------------------
// 5. FactSales Query
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\DataAnalyst\Data-Analyst-Portfolio-main\05-executive-business-intelligence\data\fact_sales.csv"), [Delimiter=",", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"OrderID", type text},
        {"DateKey", Int64.Type},
        {"CustomerKey", Int64.Type},
        {"ProductKey", Int64.Type},
        {"PaymentMethod", type text},
        {"Quantity", Int64.Type},
        {"UnitPrice", type number},
        {"UnitCost", type number},
        {"DiscountPct", type number},
        {"Revenue", type number},
        {"COGS", type number},
        {"Profit", type number}
    })
in
    ChangeTypes

// ------------------------------------------------------------------------------
// 6. CustomerRFM Query
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\DataAnalyst\Data-Analyst-Portfolio-main\05-executive-business-intelligence\analytics\outputs\customer_rfm.csv"), [Delimiter=",", Columns=20, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"CustomerKey", Int64.Type},
        {"CustomerID", type text},
        {"City", type text},
        {"Original_Segment", type text},
        {"FirstOrderDate", type text},
        {"LastOrderDate", type text},
        {"Recency_Days", Int64.Type},
        {"Frequency_Orders", Int64.Type},
        {"Monetary_Revenue", type number},
        {"Total_Profit", type number},
        {"Total_Units", Int64.Type},
        {"Avg_Order_Value", type number},
        {"Profit_Margin_Pct", type number},
        {"R_Score", Int64.Type},
        {"F_Score", Int64.Type},
        {"M_Score", Int64.Type},
        {"RFM_Score", Int64.Type},
        {"RFM_Index", type number},
        {"RFM_Segment", type text},
        {"Recommended_Action", type text}
    })
in
    ChangeTypes

// ------------------------------------------------------------------------------
// 7. MonthlyForecast Query
// ------------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\DataAnalyst\Data-Analyst-Portfolio-main\05-executive-business-intelligence\analytics\outputs\monthly_forecast.csv"), [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"YearMonth", type text},
        {"Period_Type", type text},
        {"Revenue", type number},
        {"Revenue_Lower_95", type number},
        {"Revenue_Upper_95", type number},
        {"Profit", type number},
        {"Profit_Lower_95", type number},
        {"Profit_Upper_95", type number},
        {"Profit_Margin_Pct", type number},
        {"MoM_Growth_Pct", type number},
        {"Model_Used", type text}
    })
in
    ChangeTypes
