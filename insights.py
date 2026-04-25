"""
Nile.ag Supply Chain – Deep Insights Discovery
Helps operations find: declining suppliers, worst region-product pairs, price spike seasons, etc.
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import timedelta

def load_data(filepath="nile_supply_chain.csv"):
    """Load and prepare data"""
    df = pd.read_csv(filepath, parse_dates=["order_date", "expected_delivery_date", "actual_delivery_date"])
    # Ensure numeric columns
    df["delay_days"] = df["actual_delivery_date"] - df["expected_delivery_date"]
    df["delay_days"] = df["delay_days"].dt.days
    df["on_time"] = (df["delay_days"] <= 0).astype(int)
    return df

def find_declining_suppliers(df, min_orders=30):
    """
    Which suppliers are getting WORSE over time?
    Returns suppliers with negative trend slope in on-time percentage.
    """
    # Aggregate monthly on-time rate per supplier
    df["year_month"] = df["order_date"].dt.to_period("M")
    monthly = df.groupby(["supplier", "year_month"])["on_time"].mean().reset_index()
    monthly["month_num"] = monthly.groupby("supplier").cumcount()
    
    results = []
    for supplier in monthly["supplier"].unique():
        sub = monthly[monthly["supplier"] == supplier]
        orders_count = df[df["supplier"] == supplier].shape[0]
        if orders_count >= min_orders and len(sub) >= 3:
            slope, intercept, r_value, p_value, std_err = stats.linregress(sub["month_num"], sub["on_time"])
            results.append({
                "supplier": supplier,
                "trend_slope": round(slope, 4),
                "direction": "🔻 DECLINING" if slope < -0.02 else "📈 IMPROVING" if slope > 0.02 else "➡️ STABLE",
                "current_on_time_pct": round(df[df["supplier"] == supplier]["on_time"].mean() * 100, 1),
                "orders": orders_count,
                "priority": "HIGH" if slope < -0.03 else "MEDIUM" if slope < -0.015 else "LOW"
            })
    
    declining = pd.DataFrame(results).sort_values("trend_slope")
    return declining[declining["trend_slope"] < -0.01]

def worst_region_product_pairs(df, min_orders=10):
    """
    Which (region, product) combinations have the highest average delay?
    This helps logistics focus on specific lanes.
    """
    grouped = df.groupby(["supplier_region", "product"]).agg(
        avg_delay=("delay_days", "mean"),
        orders=("order_id", "count"),
        total_value=("total_value_zar", "sum"),
        high_risk_pct=("delay_days", lambda x: (x > 5).mean() * 100)
    ).reset_index()
    
    grouped = grouped[grouped["orders"] >= min_orders]
    grouped = grouped.sort_values("avg_delay", ascending=False)
    grouped["avg_delay"] = grouped["avg_delay"].round(1)
    grouped["high_risk_pct"] = grouped["high_risk_pct"].round(1)
    return grouped.head(15)

def price_spike_calendar(df, threshold_sigma=2.0):
    """
    Which months have the most price spikes?
    Returns month, spike_count, spike_rate.
    """
    # Calculate per-product mean and std
    price_stats = df.groupby("product")["price_per_kg"].agg(["mean", "std"]).reset_index()
    price_stats.columns = ["product", "price_mean", "price_std"]
    df = df.merge(price_stats, on="product")
    df["is_spike"] = df["price_per_kg"] > (df["price_mean"] + threshold_sigma * df["price_std"])
    
    # Aggregate by month
    df["month"] = df["order_date"].dt.month
    spikes_by_month = df[df["is_spike"]].groupby("month").size().reset_index(name="spike_count")
    total_by_month = df.groupby("month").size().reset_index(name="total_orders")
    
    calendar = spikes_by_month.merge(total_by_month, on="month", how="right").fillna(0)
    calendar["spike_rate"] = (calendar["spike_count"] / calendar["total_orders"] * 100).round(1)
    calendar = calendar.sort_values("spike_rate", ascending=False)
    
    # Add month names
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    calendar["month_name"] = calendar["month"].apply(lambda x: month_names[x-1])
    return calendar[["month_name", "spike_count", "total_orders", "spike_rate"]]

def predict_high_risk_orders(df, declining_suppliers_df):
    """
    Flag orders that are likely to become high risk based on:
    - Supplier is declining
    - Product is perishable
    - Current delay > 0 (already slightly late)
    """
    declining_list = declining_suppliers_df["supplier"].tolist()
    
    # Add prediction flags
    df["predicted_risk"] = "Low"
    df.loc[(df["supplier"].isin(declining_list)) & 
           (df["perishable"] == True) &
           (df["delay_days"] > 0), "predicted_risk"] = "HIGH"
    
    df.loc[(df["supplier"].isin(declining_list)) & 
           (df["perishable"] == True), "predicted_risk"] = "MEDIUM"
    
    # Return high-risk predictions
    high_risk_pred = df[df["predicted_risk"] == "HIGH"].copy()
    high_risk_pred = high_risk_pred[["order_id", "supplier", "product", "order_date", 
                                      "delay_days", "total_value_zar", "predicted_risk"]]
    high_risk_pred["value_at_risk"] = high_risk_pred["total_value_zar"].sum()
    return high_risk_pred.sort_values("order_date", ascending=False)

def supplier_performance_timeline(df, selected_supplier):
    """
    Monthly on-time percentage trend for a specific supplier.
    Used for deep dive.
    """
    sub = df[df["supplier"] == selected_supplier].copy()
    sub["year_month"] = sub["order_date"].dt.to_period("M").astype(str)
    monthly = sub.groupby("year_month")["on_time"].agg(["mean", "count"]).reset_index()
    monthly.columns = ["month", "on_time_pct", "orders"]
    monthly["on_time_pct"] = (monthly["on_time_pct"] * 100).round(1)
    return monthly

def cost_of_delays(df):
    """
    Estimate financial impact of delays:
    - Assume 20% of delayed orders are cancelled
    - Assume 20% discount on delayed perishable orders
    """
    delayed = df[df["delay_days"] > 0].copy()
    critical_delayed = delayed[delayed["delay_days"] > 5].copy()
    
    # Estimate
    cancellation_loss = delayed["total_value_zar"].sum() * 0.15  # 15% cancellation rate
    discount_compensation = delayed[delayed["perishable"] == True]["total_value_zar"].sum() * 0.1
    total_estimated_loss = cancellation_loss + discount_compensation
    
    return {
        "total_orders_delayed": len(delayed),
        "percent_delayed": round(len(delayed) / len(df) * 100, 1),
        "critical_delays": len(critical_delayed),
        "estimated_financial_loss": round(total_estimated_loss, 0),
        "total_revenue": round(df["total_value_zar"].sum(), 0),
        "loss_percent": round(total_estimated_loss / df["total_value_zar"].sum() * 100, 1)
    }

def product_risk_ranking(df):
    """
    Rank products by:
    - Average delay
    - % High/Critical
    - Perishability (inherent risk)
    - Total value at risk
    """
    product_risk = df.groupby("product").agg(
        avg_delay=("delay_days", "mean"),
        high_risk_pct=("delay_days", lambda x: (x > 3).mean() * 100),
        total_orders=("order_id", "count"),
        total_value=("total_value_zar", "sum"),
        perishable=("perishable", "first")
    ).reset_index()
    
    product_risk["avg_delay"] = product_risk["avg_delay"].round(1)
    product_risk["high_risk_pct"] = product_risk["high_risk_pct"].round(1)
    product_risk["risk_score"] = (product_risk["avg_delay"] * 10 + 
                                   product_risk["high_risk_pct"]).round(1)
    product_risk = product_risk.sort_values("risk_score", ascending=False)
    return product_risk.head(10)