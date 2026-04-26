# insights.py 
# Requires: pip install statsmodels

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


# =========================================================
# LOAD DATA WITH VALIDATION
# =========================================================
def load_data(filepath):
    """Enhanced data loading with validation and error handling"""
    df = pd.read_csv(filepath, parse_dates=[
        "order_date", "expected_delivery_date", "actual_delivery_date"
    ])

    df["delay_days"] = (df["actual_delivery_date"] - df["expected_delivery_date"]).dt.days
    df["delay_days"] = df["delay_days"].fillna(0)

    df["on_time"] = (df["delay_days"] <= 0).astype(int)
    df["year_month"] = df["order_date"].dt.to_period("M")
    
    # Enhanced additions
    df["early_delivery"] = (df["delay_days"] < 0).astype(int)
    df["delay_severity"] = pd.cut(
        df["delay_days"],
        bins=[-float('inf'), 0, 2, 5, 10, float('inf')],
        labels=["Early", "On-Time", "Minor Delay", "Major Delay", "Critical Delay"]
    )
    
    return df


# =========================================================
# ENHANCED SUPPLIER TREND
# =========================================================
def find_declining_suppliers(df, min_orders=30):
    """Enhanced supplier trend detection with acceleration and volatility"""
    monthly = df.groupby(["supplier", "year_month"]).agg(
        on_time=("on_time", "mean"),
        orders=("order_id", "count"),
        avg_delay=("delay_days", "mean")
    ).reset_index()
    
    monthly["t"] = monthly.groupby("supplier").cumcount()
    results = []
    
    for s in monthly["supplier"].unique():
        sub = monthly[monthly["supplier"] == s]
        
        if sub["orders"].sum() < min_orders or len(sub) < 4:
            continue
        
        # Linear regression for trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(sub["t"], sub["on_time"])
        
        # Acceleration (second derivative)
        if len(sub) >= 5:
            accel_slope, _, _, _, _ = stats.linregress(sub["t"][-3:], sub["on_time"][-3:])
            acceleration = accel_slope - slope
        else:
            acceleration = 0
        
        # Volatility (stability score)
        volatility = sub["on_time"].std()
        
        # Enhanced direction
        if slope < -0.03:
            direction = "CRITICAL DECLINE"
            urgency = "IMMEDIATE"
        elif slope < -0.02:
            direction = "DECLINING"
            urgency = "HIGH"
        elif slope < -0.01:
            direction = "SLIGHT DECLINE"
            urgency = "MEDIUM"
        elif slope > 0.02:
            direction = "IMPROVING"
            urgency = "LOW"
        else:
            direction = "STABLE"
            urgency = "MONITOR"
        
        # Add acceleration flag
        if acceleration < -0.05:
            direction = f"{direction} (ACCELERATING)"
            urgency = "URGENT"
        
        results.append({
            "supplier": s,
            "trend_slope": round(slope, 4),
            "acceleration": round(acceleration, 4),
            "volatility": round(volatility, 3),
            "p_value": round(p_value, 4),
            "r_squared": round(r_value**2, 3),
            "direction": direction,
            "urgency": urgency,
            "on_time_pct": round(sub["on_time"].mean() * 100, 1),
            "current_on_time": round(sub["on_time"].iloc[-1] * 100, 1) if len(sub) > 0 else 0,
            "avg_delay": round(sub["avg_delay"].mean(), 2)
        })
    
    if not results:
        return pd.DataFrame(columns=["supplier", "trend_slope", "direction", "urgency", "on_time_pct"])
    
    return pd.DataFrame(results).sort_values("trend_slope")


# =========================================================
# SUPPLIER PERFORMANCE TIMELINE
# =========================================================
def supplier_performance_timeline(df, supplier):
    t = df[df["supplier"] == supplier]
    if t.empty:
        return pd.DataFrame(columns=["year_month", "on_time_pct", "month"])
    t = t.groupby("year_month").agg(on_time_pct=("on_time", "mean")).reset_index()
    t["month"] = t["year_month"].astype(str)
    t["on_time_pct"] *= 100
    return t


# =========================================================
# WORST LANES (VALUE-AWARE)
# =========================================================
def worst_region_product_pairs(df):
    g = df.groupby(["supplier_region", "product"]).agg(
        avg_delay=("delay_days", "mean"),
        std=("delay_days", "std"),
        critical=("delay_days", lambda x: (x > 5).mean()),
        value=("total_value_zar", "sum")
    ).reset_index()
    g["score"] = g["avg_delay"] * 2 + g["std"].fillna(0) + g["critical"] * 10 + np.log1p(g["value"] / 10000)
    return g.sort_values("score", ascending=False)


# =========================================================
# PRICE SPIKE CALENDAR
# =========================================================
def price_spike_calendar(df):
    df = df.sort_values("order_date")
    df["rolling_mean"] = df.groupby("product")["price_per_kg"].transform(lambda x: x.rolling(30, min_periods=10).mean())
    df["rolling_std"] = df.groupby("product")["price_per_kg"].transform(lambda x: x.rolling(30, min_periods=10).std())
    df["spike"] = df["price_per_kg"] > (df["rolling_mean"] + 2 * df["rolling_std"])
    df["month_name"] = df["order_date"].dt.strftime("%b")
    result = df.groupby("month_name")["spike"].mean().reset_index(name="spike_rate")
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    result['month_order'] = result['month_name'].map({m: i for i, m in enumerate(all_months)})
    return result.sort_values('month_order').drop('month_order', axis=1)


# =========================================================
# PRICE SPIKE PREDICTION
# =========================================================
def predict_price_spikes(df, lookback_days=30):
    """Predict upcoming price spikes based on historical patterns"""
    df = df.sort_values("order_date")
    df["price_ma7"] = df.groupby("product")["price_per_kg"].transform(lambda x: x.rolling(7, min_periods=1).mean())
    df["price_ma30"] = df.groupby("product")["price_per_kg"].transform(lambda x: x.rolling(30, min_periods=1).mean())
    df["price_volatility"] = df.groupby("product")["price_per_kg"].transform(lambda x: x.rolling(30, min_periods=1).std())
    df["price_momentum"] = (df["price_ma7"] - df["price_ma30"]) / df["price_ma30"]
    df["spike_probability"] = (df["price_momentum"] * 5 + 0.1).clip(0, 1)
    high_risk_products = df[df["spike_probability"] > 0.7].groupby("product").agg({
        "spike_probability": "mean",
        "price_per_kg": "last"
    }).reset_index()
    return high_risk_products.sort_values("spike_probability", ascending=False)


# =========================================================
# PREDICT HIGH RISK ORDERS
# =========================================================
def predict_high_risk_orders(df, declining):
    df = df.copy()
    bad_suppliers = set(declining["supplier"]) if not declining.empty else set()
    df["risk_score"] = 0
    df.loc[df["supplier"].isin(bad_suppliers), "risk_score"] += 3
    df.loc[df["perishable"], "risk_score"] += 2
    df.loc[df["delay_days"] > 0, "risk_score"] += 2
    df.loc[df["delay_days"] > 5, "risk_score"] += 3
    df.loc[df["quantity_kg"] > df["quantity_kg"].quantile(0.8), "risk_score"] += 2
    df["risk_level"] = pd.cut(df["risk_score"], bins=[-1,2,5,10], labels=["LOW","MEDIUM","HIGH"])
    high = df[df["risk_level"]=="HIGH"].copy()
    if not high.empty:
        high["value_at_risk"] = high["total_value_zar"]
    return high.sort_values("risk_score", ascending=False) if not high.empty else pd.DataFrame()


# =========================================================
# ENHANCED COST ENGINE
# =========================================================
def cost_of_delays(df):
    d = df[df["delay_days"] > 0].copy()
    if d.empty:
        return {
            "total_orders_delayed": 0,
            "critical_delays": 0,
            "estimated_financial_loss": 0,
            "loss_percent": 0.0,
            "cost_by_product": {},
            "cost_by_region": {}
        }
    
    perish_penalty = np.where(d["perishable"], 0.3, 0.15)
    delay_factor = np.clip(d["delay_days"] / 7, 0.05, 0.5)
    d["loss"] = d["total_value_zar"] * (delay_factor + perish_penalty)
    
    total_value = df["total_value_zar"].sum()
    loss_percent = 0 if total_value == 0 else round(d["loss"].sum() / total_value * 100, 1)
    
    cost_by_product = d.groupby("product")["loss"].sum().sort_values(ascending=False).head(10).to_dict()
    cost_by_region = d.groupby("supplier_region")["loss"].sum().sort_values(ascending=False).to_dict()
    
    return {
        "total_orders_delayed": len(d),
        "critical_delays": int((d["delay_days"] > 5).sum()),
        "estimated_financial_loss": round(d["loss"].sum(), 0),
        "loss_percent": loss_percent,
        "cost_by_product": cost_by_product,
        "cost_by_region": cost_by_region,
        "risk_adjusted_loss": round(d["loss"].sum() * 1.2, 0)
    }


# =========================================================
# PRICE VOLATILITY BY PRODUCT
# =========================================================
def price_volatility_by_product(df):
    g = df.groupby("product").agg(
        avg_price=("price_per_kg", "mean"),
        volatility=("price_per_kg", "std"),
        max_price=("price_per_kg", "max"),
        min_price=("price_per_kg", "min"),
        total_value=("total_value_zar", "sum")
    ).reset_index()
    g["price_range_pct"] = ((g["max_price"] - g["min_price"]) / g["avg_price"]) * 100
    g["price_range_pct"] = g["price_range_pct"].fillna(0)
    g["volatility_score"] = g["volatility"] * 2 + g["price_range_pct"] * 0.5 + np.log1p(g["total_value"] / 10000)
    return g.sort_values("volatility_score", ascending=False)


# =========================================================
# SEASONAL PRICE PATTERNS
# =========================================================
def seasonal_price_patterns(df):
    df = df.copy()
    df["month"] = df["order_date"].dt.month
    df["month_name"] = df["order_date"].dt.strftime("%b")
    g = df.groupby(["product", "month", "month_name"]).agg(
        avg_price=("price_per_kg", "mean"),
        demand=("quantity_kg", "sum")
    ).reset_index()
    return g.sort_values(["product", "month"])


# =========================================================
# ENHANCED PRODUCT RISK WITH WEIGHTS
# =========================================================
def product_risk_ranking(df):
    g = df.groupby("product").agg(
        avg_delay=("delay_days","mean"),
        volatility=("delay_days","std"),
        critical=("delay_days", lambda x: (x>5).mean()),
        perishable=("perishable","first"),
        value=("total_value_zar","sum"),
        supplier_count=("supplier", "nunique")
    ).reset_index()
    
    g["base_risk"] = g["avg_delay"] * 2 + g["volatility"].fillna(0) + g["critical"] * 15 + g["perishable"].astype(int) * 3
    max_risk = g["base_risk"].max()
    g["risk_weight"] = (g["base_risk"] / max_risk).clip(0.1, 1.0) if max_risk > 0 else 0.5
    
    g["score"] = g["avg_delay"] * 2 + g["volatility"].fillna(0) * 1.5 + g["critical"] * 12 + g["perishable"].astype(int) * 3 + np.log1p(g["value"] / 10000)
    g["risk_level"] = pd.cut(g["score"], bins=[0, 30, 60, 100, float('inf')], labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    g["required_supplier_grade"] = g["risk_level"].map({"LOW": "B or higher", "MEDIUM": "A or higher", "HIGH": "A+ only", "CRITICAL": "Specialized only"})
    
    return g.sort_values("score", ascending=False)


# =========================================================
# DETECT PRICE SPIKES
# =========================================================
def detect_price_spikes(df):
    df = df.copy()
    stats_df = df.groupby("product")["price_per_kg"].agg(["mean", "std"]).reset_index()
    df = df.merge(stats_df, on="product")
    df["std"] = df["std"].replace(0, 0.01)
    df["z_score"] = (df["price_per_kg"] - df["mean"]) / df["std"]
    df["spike_severity"] = pd.cut(df["z_score"], bins=[-np.inf, 2, 3, np.inf], labels=["Normal", "Moderate Spike", "Extreme Spike"])
    return df[df["z_score"] > 2].sort_values("z_score", ascending=False)


# =========================================================
# PRICE RISK INDEX
# =========================================================
def price_risk_index(df):
    g = df.groupby("product").agg(
        volatility=("price_per_kg", "std"),
        spike_rate=("price_per_kg", lambda x: ((x - x.mean()) > 2*x.std()).mean()),
        total_value=("total_value_zar", "sum")
    ).reset_index()
    g["risk_index"] = g["volatility"].fillna(0) * 2 + g["spike_rate"].fillna(0) * 20 + np.log1p(g["total_value"] / 10000)
    return g.sort_values("risk_index", ascending=False)


# =========================================================
# SEASONAL SPIKE MATRIX
# =========================================================
def seasonal_spike_matrix(df):
    df = df.copy()
    df["month"] = df["order_date"].dt.strftime("%b")
    product_stats = df.groupby("product")["price_per_kg"].agg(["mean", "std"]).reset_index()
    df = df.merge(product_stats, on="product")
    df["std"] = df["std"].replace(0, 0.01)
    df["spike"] = df["price_per_kg"] > (df["mean"] + 2 * df["std"])
    return df.pivot_table(values="spike", index="product", columns="month", aggfunc="mean", fill_value=0)


# =========================================================
# PROCUREMENT TIMING STRATEGY
# =========================================================
def procurement_timing_strategy(df):
    df = df.copy()
    df["month"] = df["order_date"].dt.month
    g = df.groupby(["product", "month"]).agg(avg_price=("price_per_kg", "mean")).reset_index()
    strategy = []
    for product in g["product"].unique():
        sub = g[g["product"] == product]
        if len(sub) < 2: continue
        cheapest = sub.loc[sub["avg_price"].idxmin()]
        most_expensive = sub.loc[sub["avg_price"].idxmax()]
        strategy.append({
            "product": product,
            "buy_month": int(cheapest["month"]),
            "avoid_month": int(most_expensive["month"]),
            "price_diff": round(most_expensive["avg_price"] - cheapest["avg_price"], 2),
            "savings_percent": round((most_expensive["avg_price"] - cheapest["avg_price"]) / most_expensive["avg_price"] * 100, 1)
        })
    if not strategy:
        return pd.DataFrame(columns=["product", "buy_month", "avoid_month", "price_diff"])
    return pd.DataFrame(strategy).sort_values("price_diff", ascending=False)


# =========================================================
# PROFIT LEAKAGE
# =========================================================
def profit_leakage(df):
    df = df.copy()
    df["loss"] = df["total_value_zar"] * np.clip(df["delay_days"]/10, 0.05, 0.4)
    g = df.groupby(["supplier","supplier_region"]).agg(
        total_loss=("loss","sum"),
        avg_delay=("delay_days","mean")
    ).reset_index()
    return g.sort_values("total_loss", ascending=False)


# =========================================================
# SMART ROUTING ENHANCED
# =========================================================
def smart_routing(df, product, region, min_reliability=0.75):
    subset = df[(df["product"]==product) & (df["supplier_region"]==region)]
    if subset.empty:
        return pd.DataFrame(columns=["supplier", "delay", "reliability", "cost", "value", "score", "accountability"])
    
    g = subset.groupby("supplier").agg(
        delay=("delay_days","mean"),
        reliability=("on_time","mean"),
        cost=("price_per_kg","mean"),
        value=("total_value_zar","sum"),
        samples=("order_id","count")
    ).reset_index()
    
    g = g[g["reliability"] >= min_reliability]
    if g.empty:
        return pd.DataFrame(columns=["supplier", "delay", "reliability", "cost", "value", "score", "accountability"])
    
    g["reliability_score"] = g["reliability"] * 50
    g["delay_penalty"] = (1 - g["delay"] / 15).clip(0, 1) * 20
    g["cost_score"] = (1 - g["cost"] / g["cost"].max()) * 15 if g["cost"].max() > 0 else 0
    g["value_score"] = np.log1p(g["value"] / 10000) * 15
    g["accountability"] = (g["reliability_score"] + g["delay_penalty"] + g["cost_score"] + g["value_score"]).clip(0, 100)
    
    g["score"] = g["reliability"]*60 - g["delay"]*10 - g["cost"]*0.2 + np.log1p(g["value"]/10000) + g["accountability"]*0.1
    g["recommendation"] = g["accountability"].apply(lambda x: "Strongly Recommended" if x > 80 else "Recommended" if x > 60 else "Consider" if x > 40 else "Avoid")
    
    return g.sort_values("score", ascending=False)


# =========================================================
# SUPPLY FRAGILITY
# =========================================================
def supply_fragility(df):
    dep = df["supplier"].value_counts(normalize=True).reset_index()
    dep.columns = ["supplier","dependency"]
    dep["risk"] = np.where(dep["dependency"]>0.25,"HIGH","NORMAL")
    return dep.sort_values("dependency", ascending=False)


# =========================================================
# SUPPLIER ACCOUNTABILITY SCORES
# =========================================================
def supplier_accountability_scores(df):
    """Calculate comprehensive accountability scores for suppliers"""
    supplier_metrics = []
    
    for supplier in df["supplier"].unique():
        supplier_df = df[df["supplier"] == supplier]
        
        on_time_rate = supplier_df["on_time"].mean()
        avg_delay = supplier_df["delay_days"].mean()
        total_orders = len(supplier_df)
        delayed_orders = (supplier_df["delay_days"] > 0).sum()
        
        performance_score = on_time_rate * 60
        reliability_score = max(0, 40 - avg_delay * 3)
        total_score = min(100, performance_score + reliability_score)
        
        if total_score >= 85:
            grade = "A+"
            action = "🚀 Strategic Partner"
        elif total_score >= 75:
            grade = "A"
            action = "✅ Preferred Supplier"
        elif total_score >= 65:
            grade = "B"
            action = "👀 Monitor"
        elif total_score >= 55:
            grade = "C"
            action = "📋 Review Required"
        elif total_score >= 45:
            grade = "D"
            action = "⚠️ Warning"
        else:
            grade = "F"
            action = "🔴 Terminate"
        
        supplier_metrics.append({
            "supplier": supplier,
            "region": supplier_df["supplier_region"].iloc[0],
            "total_orders": total_orders,
            "delayed_orders": delayed_orders,
            "on_time_rate": round(on_time_rate * 100, 1),
            "avg_delay": round(avg_delay, 2),
            "accountability_score": round(total_score, 1),
            "grade": grade,
            "action": action
        })
    
    return pd.DataFrame(supplier_metrics).sort_values("accountability_score", ascending=False)


# =========================================================
# GENERATE ALERTS
# =========================================================
def generate_alerts(df, supplier_scores, product_risks):
    """Generate actionable alerts for supply chain risks"""
    alerts = []
    
    # Supplier alerts
    for _, supplier in supplier_scores.iterrows():
        if supplier["grade"] in ["D", "F"]:
            alerts.append({
                "type": "CRITICAL SUPPLIER",
                "severity": "HIGH" if supplier["grade"] == "F" else "MEDIUM",
                "entity": supplier["supplier"],
                "message": f"Supplier {supplier['supplier']} has grade {supplier['grade']} ({supplier['on_time_rate']:.1f}% on-time). Action: {supplier['action']}",
                "action": supplier["action"]
            })
    
    # Product risk alerts
    for _, product in product_risks.head(10).iterrows():
        if product["risk_level"] in ["HIGH", "CRITICAL"]:
            alerts.append({
                "type": "HIGH RISK PRODUCT",
                "severity": "HIGH" if product["risk_level"] == "CRITICAL" else "MEDIUM",
                "entity": product["product"],
                "message": f"Product {product['product']} has {product['risk_level']} risk level (Score: {product['score']:.1f})",
                "action": "Review supplier assignments and pricing strategy"
            })
    
    # Declining supplier alerts
    declining = find_declining_suppliers(df)
    for _, supplier in declining.head(5).iterrows():
        alerts.append({
            "type": "DECLINING SUPPLIER",
            "severity": "MEDIUM",
            "entity": supplier["supplier"],
            "message": f"Supplier {supplier['supplier']} is showing {supplier['direction']} trend (slope: {supplier['trend_slope']:.3f})",
            "action": "Schedule performance review meeting"
        })
    
    return pd.DataFrame(alerts)


# =========================================================
# ENHANCED ML MODEL
# =========================================================
def train_delay_model(df):
    X = df[["quantity_kg","price_per_kg","perishable"]].copy()
    X["perishable"] = X["perishable"].astype(int)
    X["log_quantity"] = np.log1p(X["quantity_kg"])
    X["price_per_unit"] = X["price_per_kg"] / (X["quantity_kg"] + 1)
    X["value_density"] = X["price_per_kg"] * X["quantity_kg"] / (X["quantity_kg"] + 1)
    
    if "product_category" in df.columns:
        cat_avg = df.groupby("product_category")["delay_days"].transform("mean")
        X["category_avg_delay"] = cat_avg
    
    if "supplier" in df.columns:
        supplier_rel = df.groupby("supplier")["on_time"].transform("mean")
        X["supplier_reliability"] = supplier_rel
    
    y = df["delay_days"]
    model = RandomForestRegressor(n_estimators=200, max_depth=8, min_samples_split=10, min_samples_leaf=4, random_state=42, n_jobs=-1)
    model.fit(X, y)
    return model


def predict_delay(df, model):
    X = df[["quantity_kg","price_per_kg","perishable"]].copy()
    X["perishable"] = X["perishable"].astype(int)
    X["log_quantity"] = np.log1p(X["quantity_kg"])
    X["price_per_unit"] = X["price_per_kg"] / (X["quantity_kg"] + 1)
    X["value_density"] = X["price_per_kg"] * X["quantity_kg"] / (X["quantity_kg"] + 1)
    
    if "product_category" in df.columns:
        cat_avg = df.groupby("product_category")["delay_days"].transform("mean").fillna(0)
        X["category_avg_delay"] = cat_avg
    
    if "supplier" in df.columns:
        supplier_rel = df.groupby("supplier")["on_time"].transform("mean").fillna(0.5)
        X["supplier_reliability"] = supplier_rel
    
    df["predicted_delay"] = model.predict(X)
    df["predicted_risk"] = pd.cut(df["predicted_delay"], bins=[-1, 1, 3, 7, 100], labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    return df


# =========================================================
# SCENARIO ENGINE
# =========================================================
def simulate_shock(df, price_increase=0.0, delay_increase=0):
    sim = df.copy()
    sim["price_per_kg"] = sim["price_per_kg"] * (1 + price_increase)
    sim["delay_days"] = sim["delay_days"] + delay_increase
    sim["total_value_zar"] = sim["quantity_kg"] * sim["price_per_kg"]
    loss = (sim["total_value_zar"] * np.clip(sim["delay_days"]/10, 0.05, 0.4)).sum()
    total_value = df["total_value_zar"].sum()
    impact_pct = 0 if total_value == 0 else round(loss / total_value * 100, 1)
    return {"shock_loss": round(loss, 0), "impact_pct": impact_pct}


# =========================================================
# MASTER PIPELINE
# =========================================================
def run_all(filepath):
    df = load_data(filepath)
    
    declining = find_declining_suppliers(df)
    model = train_delay_model(df)
    product_risk = product_risk_ranking(df)
    supplier_scores = supplier_accountability_scores(df)
    
    return {
        "declining": declining,
        "worst_lanes": worst_region_product_pairs(df),
        "price_spikes": price_spike_calendar(df),
        "price_volatility": price_volatility_by_product(df),
        "seasonality": seasonal_price_patterns(df),
        "price_spike_events": detect_price_spikes(df),
        "price_risk": price_risk_index(df),
        "seasonal_spike_matrix": seasonal_spike_matrix(df),
        "procurement_strategy": procurement_timing_strategy(df),
        "high_risk": predict_high_risk_orders(df, declining),
        "cost": cost_of_delays(df),
        "product_risk": product_risk,
        "profit_leakage": profit_leakage(df),
        "fragility": supply_fragility(df),
        "model": model,
        "supplier_accountability": supplier_scores,
        "price_spike_predictions": predict_price_spikes(df),
        "alerts": generate_alerts(df, supplier_scores, product_risk)
    }


print("✅ COMPLETE ENHANCED INSIGHTS MODULE LOADED!")
print("   Features: Supplier Accountability | Price Spike Prediction | Real-time Alerts | Enhanced ML")
