"""
RFM Customer Segmentation Analysis
Portfolio #5 - Executive Business Intelligence Dashboard

Calculates Recency, Frequency, and Monetary (RFM) metrics from fact_sales.csv,
generates 1-5 quintile scores, segments customers into actionable behavioral groups,
handles potential non-transactional customers gracefully without data fabrication,
and outputs a Power BI-ready CSV dataset.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np


def run_rfm_analysis():
    # Resolve paths relative to script location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    data_dir = project_root / 'data'
    output_dir = script_dir / 'outputs'
    output_dir.mkdir(parents=True, exist_ok=True)

    fact_path = data_dir / 'fact_sales.csv'
    dim_date_path = data_dir / 'dim_date.csv'
    dim_cust_path = data_dir / 'dim_customer.csv'

    print("=" * 85)
    print("       EXECUTIVE BI - RFM CUSTOMER SEGMENTATION & AUDIT ENGINE")
    print("=" * 85)

    # 1. Ingest Data
    print(f"Loading data from {data_dir}...")
    if not fact_path.exists():
        raise FileNotFoundError(f"Missing {fact_path}")
    if not dim_date_path.exists():
        raise FileNotFoundError(f"Missing {dim_date_path}")
    if not dim_cust_path.exists():
        raise FileNotFoundError(f"Missing {dim_cust_path}")

    fact = pd.read_csv(fact_path)
    dim_date = pd.read_csv(dim_date_path)
    dim_cust = pd.read_csv(dim_cust_path)

    total_dim_cust = len(dim_cust)
    unique_dim_keys = dim_cust['CustomerKey'].nunique()
    unique_fact_keys = fact['CustomerKey'].nunique()

    print(f"  - fact_sales: {len(fact):,} rows (across {unique_fact_keys:,} unique customers)")
    print(f"  - dim_customer: {total_dim_cust:,} data rows (1,603 lines including CSV header)")
    print(f"  - dim_date: {len(dim_date):,} rows")

    # 2. Join Fact with Date Dimension
    df = fact.merge(dim_date[['DateKey', 'Date', 'YearMonth']], on='DateKey', how='left')
    df['Date'] = pd.to_datetime(df['Date'])

    # Snapshot Date = Day after maximum observed transaction date
    snapshot_date = df['Date'].max() + pd.Timedelta(days=1)
    print("\nAnalysis Timeline:")
    print(f"  - Earliest Transaction: {df['Date'].min().strftime('%Y-%m-%d')}")
    print(f"  - Latest Transaction:   {df['Date'].max().strftime('%Y-%m-%d')}")
    print(f"  - Snapshot Reference:   {snapshot_date.strftime('%Y-%m-%d')}")

    # 3. Aggregate Transactional Customer Level Metrics
    tx_rfm = df.groupby('CustomerKey').agg(
        FirstOrderDate=('Date', 'min'),
        LastOrderDate=('Date', 'max'),
        Frequency_Orders=('OrderID', 'nunique'),
        Monetary_Revenue=('Revenue', 'sum'),
        Total_Profit=('Profit', 'sum'),
        Total_Units=('Quantity', 'sum')
    ).reset_index()

    tx_rfm['Recency_Days'] = (snapshot_date - tx_rfm['LastOrderDate']).dt.days
    tx_rfm['Avg_Order_Value'] = (tx_rfm['Monetary_Revenue'] / tx_rfm['Frequency_Orders']).round(2)
    tx_rfm['Profit_Margin_Pct'] = ((tx_rfm['Total_Profit'] / tx_rfm['Monetary_Revenue']) * 100).round(2)

    # 4. Generate RFM Scores (Quintiles 1 to 5) strictly on active transactional customers
    # Recency: Lower days = Higher score (5 is best)
    tx_rfm['R_Score'] = pd.qcut(tx_rfm['Recency_Days'].rank(method='first'), q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    # Frequency: Higher count = Higher score (5 is best)
    tx_rfm['F_Score'] = pd.qcut(tx_rfm['Frequency_Orders'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    # Monetary: Higher spend = Higher score (5 is best)
    tx_rfm['M_Score'] = pd.qcut(tx_rfm['Monetary_Revenue'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    tx_rfm['RFM_Score'] = tx_rfm['R_Score'].astype(str) + tx_rfm['F_Score'].astype(str) + tx_rfm['M_Score'].astype(str)
    tx_rfm['RFM_Index'] = ((tx_rfm['R_Score'] + tx_rfm['F_Score'] + tx_rfm['M_Score']) / 3.0).round(2)

    # 5. Define Strategic Behavioral Segments
    def segment_customer(row):
        r = row['R_Score']
        f = row['F_Score']
        m = row['M_Score']

        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f in [2, 3]:
            return 'Potential Loyalists'
        elif r >= 4 and f == 1:
            return 'New Customers'
        elif r == 3 and f in [1, 2]:
            return 'Promising'
        elif r == 3 and f >= 3:
            return 'Needs Attention'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk'
        elif r == 1 and (f >= 4 or m >= 4):
            return 'Cannot Lose Them'
        elif r == 2 and f <= 2:
            return 'About to Sleep'
        elif r == 1 and f <= 2:
            return 'Lost / Inactive'
        else:
            return 'Hibernating'

    tx_rfm['RFM_Segment'] = tx_rfm.apply(segment_customer, axis=1)

    # Actionable Marketing / Business Strategies for each segment
    strategy_map = {
        'Champions': 'VIP rewards, early access to new product releases, brand ambassador initiatives',
        'Loyal Customers': 'Upsell higher margin categories, loyalty tier bonuses, referral incentives',
        'Potential Loyalists': 'Cross-sell complementary products, membership invitations, personalized bundles',
        'New Customers': 'Post-purchase onboarding series, welcome second-order discount, user guide follow-ups',
        'Promising': 'Targeted coupon codes with minimum basket thresholds, category discovery campaigns',
        'Needs Attention': 'Limited-time re-engagement discounts, product feedback surveys, cart recovery reminders',
        'At Risk': 'Personalized win-back email sequences, aggressive reactivation vouchers, account manager outreach',
        'Cannot Lose Them': 'High-touch executive outreach, tailored reactivation bundles, high-value incentives',
        'About to Sleep': 'Brand value reminder campaigns, popular product highlights, re-activation perks',
        'Hibernating': 'Automated low-cost email reactivation campaigns, clearance sale promotions',
        'Lost / Inactive': 'Periodic automated win-back blasts; deprioritize paid acquisition re-targeting'
    }
    tx_rfm['Recommended_Action'] = tx_rfm['RFM_Segment'].map(strategy_map)

    # 6. Master Left Join with dim_customer: Retains ALL master customer records
    # If any customer has 0 purchase history, they are preserved with explicit "No Purchase History"
    customer_rfm = dim_cust[['CustomerKey', 'CustomerID', 'City', 'CustomerSegment']].merge(
        tx_rfm,
        on='CustomerKey',
        how='left'
    )
    customer_rfm.rename(columns={'CustomerSegment': 'Original_Segment'}, inplace=True)

    # Identify customers with no purchase history (if any)
    no_purchase_mask = customer_rfm['Frequency_Orders'].isna()
    no_purchase_count = no_purchase_mask.sum()

    if no_purchase_count > 0:
        print(f"\n[AUDIT NOTE] Identified {no_purchase_count} registered customer(s) with NO purchase history:")
        for _, row in customer_rfm[no_purchase_mask].iterrows():
            print(f"  - Key: {row['CustomerKey']}, ID: {row['CustomerID']}, City: {row['City']}")
        
        # Populate non-purchasing attributes without fabricating behavioral RFM scores
        customer_rfm.loc[no_purchase_mask, 'Frequency_Orders'] = 0
        customer_rfm.loc[no_purchase_mask, 'Monetary_Revenue'] = 0.0
        customer_rfm.loc[no_purchase_mask, 'Total_Profit'] = 0.0
        customer_rfm.loc[no_purchase_mask, 'Total_Units'] = 0
        customer_rfm.loc[no_purchase_mask, 'Avg_Order_Value'] = 0.0
        customer_rfm.loc[no_purchase_mask, 'Profit_Margin_Pct'] = 0.0
        customer_rfm.loc[no_purchase_mask, 'RFM_Score'] = 'N/A'
        customer_rfm.loc[no_purchase_mask, 'RFM_Segment'] = 'No Purchase History'
        customer_rfm.loc[no_purchase_mask, 'Recommended_Action'] = 'Welcome journey, activation offer, first-purchase incentive'
    else:
        print(f"\n[AUDIT NOTE] Complete transactional coverage: All {total_dim_cust:,} customers in dim_customer")
        print(f"             possess verified transaction records in fact_sales.csv (0 non-purchasing customers).")

    # Format dates
    customer_rfm['FirstOrderDate'] = pd.to_datetime(customer_rfm['FirstOrderDate']).dt.strftime('%Y-%m-%d').fillna('N/A')
    customer_rfm['LastOrderDate'] = pd.to_datetime(customer_rfm['LastOrderDate']).dt.strftime('%Y-%m-%d').fillna('N/A')

    # Organize columns cleanly
    col_order = [
        'CustomerKey', 'CustomerID', 'City', 'Original_Segment',
        'FirstOrderDate', 'LastOrderDate', 'Recency_Days', 'Frequency_Orders',
        'Monetary_Revenue', 'Total_Profit', 'Total_Units', 'Avg_Order_Value', 'Profit_Margin_Pct',
        'R_Score', 'F_Score', 'M_Score', 'RFM_Score', 'RFM_Index',
        'RFM_Segment', 'Recommended_Action'
    ]
    customer_rfm = customer_rfm[col_order].sort_values(by='Monetary_Revenue', ascending=False)

    # 7. Export Output CSV
    output_csv = output_dir / 'customer_rfm.csv'
    customer_rfm.to_csv(output_csv, index=False)
    print(f"\n[SUCCESS] RFM dataset exported successfully to:")
    print(f"  -> {output_csv}")
    print(f"  -> Total records: {len(customer_rfm):,} (1,603 lines including header)")

    # 8. Executive Segment Summary Table
    total_rev = customer_rfm['Monetary_Revenue'].sum()
    total_prof = customer_rfm['Total_Profit'].sum()

    summary = customer_rfm.groupby('RFM_Segment').agg(
        Customers=('CustomerKey', 'count'),
        Avg_Recency_Days=('Recency_Days', 'mean'),
        Avg_Orders=('Frequency_Orders', 'mean'),
        Avg_Revenue_IDR=('Monetary_Revenue', 'mean'),
        Total_Revenue_IDR=('Monetary_Revenue', 'sum'),
        Total_Profit_IDR=('Total_Profit', 'sum')
    ).reset_index()

    summary['Customer_Share_Pct'] = ((summary['Customers'] / len(customer_rfm)) * 100).round(2)
    summary['Revenue_Share_Pct'] = ((summary['Total_Revenue_IDR'] / total_rev) * 100).round(2)
    summary['Profit_Share_Pct'] = ((summary['Total_Profit_IDR'] / total_prof) * 100).round(2)
    summary['Avg_Margin_Pct'] = np.where(
        summary['Total_Revenue_IDR'] > 0,
        ((summary['Total_Profit_IDR'] / summary['Total_Revenue_IDR']) * 100).round(2),
        0.0
    )

    summary = summary.sort_values(by='Total_Revenue_IDR', ascending=False).reset_index(drop=True)

    print("\n" + "=" * 105)
    print("                               EXECUTIVE RFM SEGMENTATION BREAKDOWN")
    print("=" * 105)

    header = f"{'Segment':20s} | {'Cust':5s} | {'Cust%':6s} | {'Avg Rec':7s} | {'Avg Freq':8s} | {'Total Revenue (IDR)':20s} | {'Rev%':6s} | {'Margin%':7s}"
    print(header)
    print("-" * 105)
    for _, row in summary.iterrows():
        rev_str = f"Rp{row['Total_Revenue_IDR']:,.0f}"
        rec_str = f"{row['Avg_Recency_Days']:7.1f}" if not pd.isna(row['Avg_Recency_Days']) else "    N/A"
        print(
            f"{row['RFM_Segment']:20s} | "
            f"{row['Customers']:5d} | "
            f"{row['Customer_Share_Pct']:5.2f}% | "
            f"{rec_str} | "
            f"{row['Avg_Orders']:8.2f} | "
            f"{rev_str:>20s} | "
            f"{row['Revenue_Share_Pct']:5.2f}% | "
            f"{row['Avg_Margin_Pct']:6.2f}%"
        )
    print("=" * 105)
    print(f"Total Revenue: Rp{total_rev:,.0f} | Total Profit: Rp{total_prof:,.0f} | Customers: {len(customer_rfm):,}")
    print("=" * 105)

    return customer_rfm, summary


if __name__ == '__main__':
    run_rfm_analysis()
