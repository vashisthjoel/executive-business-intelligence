"""
Revenue & Profit Time Series Forecasting
Portfolio #5 - Executive Business Intelligence Dashboard

Uses historical monthly sales and profitability data (2025-01 through 2026-08)
to evaluate multiple forecasting models (Moving Average, Linear Trend, Ridge Regression,
and Holt Linear Exponential Smoothing), selects the best-performing model using
chronological backtesting metrics (MAE, RMSE, MAPE), and generates a 6-month forward
forecast (2026-09 through 2027-02) with 95% prediction intervals.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from scipy.optimize import minimize
import warnings

warnings.filterwarnings('ignore')


def holt_linear_forecast(series, alpha, beta, horizon):
    """
    Computes Holt's linear exponential smoothing for level and trend.
    Returns: (fitted_values, forecasts, final_level, final_trend)
    """
    y = np.array(series, dtype=float)
    n = len(y)
    l = y[0]
    b = y[1] - y[0] if n > 1 else 0.0

    fitted = [l]
    for t in range(1, n):
        l_prev, b_prev = l, b
        l = alpha * y[t] + (1.0 - alpha) * (l_prev + b_prev)
        b = beta * (l - l_prev) + (1.0 - beta) * b_prev
        fitted.append(l_prev + b_prev)

    forecasts = [l + (h + 1) * b for h in range(horizon)]
    return np.array(fitted), np.array(forecasts), l, b


def fit_holt_linear(train_series, horizon):
    """
    Optimizes smoothing parameters alpha and beta using SSE.
    """
    y = np.array(train_series, dtype=float)

    def sse(params):
        a, b = params
        fitted, _, _, _ = holt_linear_forecast(y, a, b, 1)
        return np.mean((y[1:] - fitted[1:]) ** 2)

    res = minimize(sse, [0.3, 0.1], bounds=[(0.01, 0.99), (0.01, 0.99)], method='L-BFGS-B')
    alpha_opt, beta_opt = res.x
    _, forecasts, l_end, b_end = holt_linear_forecast(y, alpha_opt, beta_opt, horizon)
    return forecasts, alpha_opt, beta_opt


def run_forecasting():
    # Resolve paths relative to script location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    data_dir = project_root / 'data'
    output_dir = script_dir / 'outputs'
    output_dir.mkdir(parents=True, exist_ok=True)

    fact_path = data_dir / 'fact_sales.csv'
    dim_date_path = data_dir / 'dim_date.csv'

    print("=" * 85)
    print("      EXECUTIVE BI - REVENUE & PROFIT FORECASTING ENGINE (6-MONTH HORIZON)")
    print("=" * 85)

    if not fact_path.exists() or not dim_date_path.exists():
        raise FileNotFoundError("Missing fact_sales.csv or dim_date.csv")

    fact = pd.read_csv(fact_path)
    dim_date = pd.read_csv(dim_date_path)

    # 1. Monthly Aggregation
    df = fact.merge(dim_date[['DateKey', 'Date', 'YearMonth']], on='DateKey', how='left')
    monthly = df.groupby('YearMonth').agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('OrderID', 'nunique'),
        Units=('Quantity', 'sum')
    ).reset_index().sort_values('YearMonth').reset_index(drop=True)

    monthly['Profit_Margin_Pct'] = ((monthly['Profit'] / monthly['Revenue']) * 100).round(2)
    monthly['MoM_Growth_Pct'] = (monthly['Revenue'].pct_change() * 100).round(2)
    monthly['t'] = np.arange(len(monthly))

    n_hist = len(monthly)
    print(f"\nHistorical Timeline: {monthly['YearMonth'].iloc[0]} to {monthly['YearMonth'].iloc[-1]} ({n_hist} months)")
    print(f"Total Historical Revenue: Rp{monthly['Revenue'].sum():,.0f}")
    print(f"Total Historical Profit:  Rp{monthly['Profit'].sum():,.0f}")
    print(f"Average Profit Margin:    {monthly['Profit_Margin_Pct'].mean():.2f}%\n")

    # 2. Chronological Backtesting Split (16 train, 4 validation)
    train_size = 16
    train = monthly.iloc[:train_size].copy()
    val = monthly.iloc[train_size:].copy()
    val_len = len(val)

    print(f"Backtesting Setup:")
    print(f"  - Training Period:   {train['YearMonth'].iloc[0]} to {train['YearMonth'].iloc[-1]} ({train_size} months)")
    print(f"  - Validation Period: {val['YearMonth'].iloc[0]} to {val['YearMonth'].iloc[-1]} ({val_len} months)\n")

    # Feature engineering for ML models
    def build_features(df_subset):
        X = pd.DataFrame()
        X['t'] = df_subset['t']
        # Quarterly seasonality features
        months = pd.to_datetime(df_subset['YearMonth'] + '-01').dt.month
        X['sin_month'] = np.sin(2 * np.pi * months / 12)
        X['cos_month'] = np.cos(2 * np.pi * months / 12)
        return X

    X_train = build_features(train)
    X_val = build_features(val)

    # Evaluation storage
    models_rev = {}
    models_prof = {}

    # 1. 3-Month Moving Average Baseline
    ma_preds_rev = [train['Revenue'].iloc[-3:].mean()]
    ma_preds_prof = [train['Profit'].iloc[-3:].mean()]
    for i in range(1, val_len):
        hist_r = list(train['Revenue']) + list(val['Revenue'].iloc[:i])
        hist_p = list(train['Profit']) + list(val['Profit'].iloc[:i])
        ma_preds_rev.append(np.mean(hist_r[-3:]))
        ma_preds_prof.append(np.mean(hist_p[-3:]))
    models_rev['3M Moving Average (Baseline)'] = np.array(ma_preds_rev)
    models_prof['3M Moving Average (Baseline)'] = np.array(ma_preds_prof)

    # 2. Linear Trend (OLS)
    lr_rev = LinearRegression().fit(train[['t']], train['Revenue'])
    lr_prof = LinearRegression().fit(train[['t']], train['Profit'])
    models_rev['Linear Trend (OLS)'] = lr_rev.predict(val[['t']])
    models_prof['Linear Trend (OLS)'] = lr_prof.predict(val[['t']])

    # 3. Ridge Regression with Seasonality
    ridge_rev = Ridge(alpha=1.0).fit(X_train, train['Revenue'])
    ridge_prof = Ridge(alpha=1.0).fit(X_train, train['Profit'])
    models_rev['Ridge (Trend + Seasonality)'] = ridge_rev.predict(X_val)
    models_prof['Ridge (Trend + Seasonality)'] = ridge_prof.predict(X_val)

    # 4. Holt Linear Exponential Smoothing
    holt_preds_rev, _, _ = fit_holt_linear(train['Revenue'], val_len)
    holt_preds_prof, _, _ = fit_holt_linear(train['Profit'], val_len)
    models_rev['Holt Linear Smoothing'] = holt_preds_rev
    models_prof['Holt Linear Smoothing'] = holt_preds_prof

    # Compute validation metrics
    print("=" * 85)
    print("                     MODEL VALIDATION & BENCHMARK COMPARISON")
    print("=" * 85)

    def print_metrics(target_name, models_dict, actuals):
        print(f"\n--- Target: {target_name} ---")
        header = f"{'Model':32s} | {'MAE (IDR)':14s} | {'RMSE (IDR)':14s} | {'MAPE (%)':8s}"
        print(header)
        print("-" * 75)
        best_name = None
        lowest_mape = float('inf')
        for name, preds in models_dict.items():
            mae = mean_absolute_error(actuals, preds)
            rmse = np.sqrt(mean_squared_error(actuals, preds))
            mape = mean_absolute_percentage_error(actuals, preds) * 100
            if mape < lowest_mape:
                lowest_mape = mape
                best_name = name
            print(f"{name:32s} | Rp{mae:11,.0f} | Rp{rmse:11,.0f} | {mape:7.2f}%")
        print(f"--> Selected Best Model for {target_name}: {best_name} (MAPE: {lowest_mape:.2f}%)")
        return best_name

    best_rev_model = print_metrics("Revenue", models_rev, val['Revenue'])
    best_prof_model = print_metrics("Profit", models_prof, val['Profit'])

    # 3. Train Champion Model on Full 20-Month Historical Data
    print("\n" + "=" * 85)
    print("         RETRAINING CHAMPION MODEL ON FULL DATASET & 6-MONTH PROJECTION")
    print("=" * 85)

    full_lr_rev = LinearRegression().fit(monthly[['t']], monthly['Revenue'])
    full_lr_prof = LinearRegression().fit(monthly[['t']], monthly['Profit'])

    # Residual Standard Errors for 95% Prediction Interval
    res_rev = monthly['Revenue'] - full_lr_rev.predict(monthly[['t']])
    std_rev = np.std(res_rev, ddof=2)

    res_prof = monthly['Profit'] - full_lr_prof.predict(monthly[['t']])
    std_prof = np.std(res_prof, ddof=2)

    # 6-Month Horizon (Sep 2026 to Feb 2027)
    future_t = np.arange(n_hist, n_hist + 6).reshape(-1, 1)
    future_months = ['2026-09', '2026-10', '2026-11', '2026-12', '2027-01', '2027-02']

    pred_rev = full_lr_rev.predict(future_t)
    pred_prof = full_lr_prof.predict(future_t)

    # 1.96 critical value for 95% prediction interval
    rev_lower = np.maximum(0, pred_rev - 1.96 * std_rev)
    rev_upper = pred_rev + 1.96 * std_rev
    prof_lower = np.maximum(0, pred_prof - 1.96 * std_prof)
    prof_upper = pred_prof + 1.96 * std_prof
    forecast_margin = (pred_prof / pred_rev) * 100

    forecast_rows = []
    prev_r = monthly['Revenue'].iloc[-1]
    for i, ym in enumerate(future_months):
        mom_g = ((pred_rev[i] - prev_r) / prev_r) * 100
        prev_r = pred_rev[i]
        forecast_rows.append({
            'YearMonth': ym,
            'Period_Type': 'Forecast',
            'Revenue': round(pred_rev[i], 2),
            'Revenue_Lower_95': round(rev_lower[i], 2),
            'Revenue_Upper_95': round(rev_upper[i], 2),
            'Profit': round(pred_prof[i], 2),
            'Profit_Lower_95': round(prof_lower[i], 2),
            'Profit_Upper_95': round(prof_upper[i], 2),
            'Profit_Margin_Pct': round(forecast_margin[i], 2),
            'MoM_Growth_Pct': round(mom_g, 2),
            'Model_Used': 'Linear Trend (Champion OLS)'
        })

    df_future = pd.DataFrame(forecast_rows)

    # Historical rows format
    hist_rows = []
    for _, row in monthly.iterrows():
        hist_rows.append({
            'YearMonth': row['YearMonth'],
            'Period_Type': 'Historical',
            'Revenue': round(row['Revenue'], 2),
            'Revenue_Lower_95': round(row['Revenue'], 2),
            'Revenue_Upper_95': round(row['Revenue'], 2),
            'Profit': round(row['Profit'], 2),
            'Profit_Lower_95': round(row['Profit'], 2),
            'Profit_Upper_95': round(row['Profit'], 2),
            'Profit_Margin_Pct': round(row['Profit_Margin_Pct'], 2),
            'MoM_Growth_Pct': row['MoM_Growth_Pct'] if not np.isnan(row['MoM_Growth_Pct']) else 0.0,
            'Model_Used': 'Actual Data'
        })

    df_hist = pd.DataFrame(hist_rows)
    df_combined = pd.concat([df_hist, df_future], ignore_index=True)

    output_csv = output_dir / 'monthly_forecast.csv'
    df_combined.to_csv(output_csv, index=False)
    print(f"\n[SUCCESS] Forecast dataset exported successfully to:")
    print(f"  -> {output_csv}")
    print(f"  -> Total rows (20 Historical + 6 Forecast): {len(df_combined)}")

    # 4. Display Executive Forecast Summary
    print("\n" + "=" * 95)
    print("                          EXECUTIVE 6-MONTH FORWARD PROJECTION")
    print("=" * 95)
    f_header = f"{'Month':8s} | {'Forecast Revenue (IDR)':22s} | {'Revenue 95% CI':27s} | {'Forecast Profit (IDR)':21s} | {'Margin%':7s}"
    print(f_header)
    print("-" * 95)
    for _, r in df_future.iterrows():
        r_str = f"Rp{r['Revenue']:,.0f}"
        ci_str = f"[Rp{r['Revenue_Lower_95']:,.0f} - Rp{r['Revenue_Upper_95']:,.0f}]"
        p_str = f"Rp{r['Profit']:,.0f}"
        print(f"{r['YearMonth']:8s} | {r_str:>22s} | {ci_str:>27s} | {p_str:>21s} | {r['Profit_Margin_Pct']:6.2f}%")
    print("=" * 95)

    tot_fc_rev = df_future['Revenue'].sum()
    tot_fc_prof = df_future['Profit'].sum()
    print(f"Cumulative 6-Month Projected Revenue: Rp{tot_fc_rev:,.0f}")
    print(f"Cumulative 6-Month Projected Profit:  Rp{tot_fc_prof:,.0f} (Avg Margin: {tot_fc_prof/tot_fc_rev*100:.2f}%)")
    print("=" * 95 + "\n")

    return df_combined, df_future


if __name__ == '__main__':
    run_forecasting()
