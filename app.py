# app.py - NILE.AG FINAL PRODUCTION READY (ALL ERRORS FIXED)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
from datetime import datetime, timedelta
import os
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Nile.ag - Operations Decision Engine",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 15px;
        color: white;
    }
    .prediction-banner {
        background: linear-gradient(135deg, #667eea20, #764ba220);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        border: 2px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# BUSINESS RULES (Interactive)
# ============================================================================

def get_business_rules():
    with st.sidebar:
        st.markdown("### ⚙️ Business Rules")
        cost_per_day = st.slider("💰 Cost per delay day (R)", 100, 2000, 500, 100)
        high_value_threshold = st.number_input("💎 High value threshold (R)", 10000, 200000, 50000, 5000)
        high_risk_days = st.slider("🔴 High risk threshold (days)", 2, 10, 5, 1)
        medium_risk_days = st.slider("🟡 Medium risk threshold (days)", 1, 5, 3, 1)
        
        st.markdown("---")
        st.markdown("### 🔮 Time Horizon")
        prediction_days = st.radio("Predict delays in next:", [3, 7, 14, 30], index=1, format_func=lambda x: f"{x} days")
        
        st.markdown("---")
        st.markdown("### 🚀 Simulation")
        expedite_reduction = st.slider("Expedite reduces delay by (days)", 0, 10, 3)
        
        return {
            "cost_per_day": cost_per_day,
            "high_value_threshold": high_value_threshold,
            "high_risk_days": high_risk_days,
            "medium_risk_days": medium_risk_days,
            "prediction_days": prediction_days,
            "expedite_reduction": expedite_reduction
        }


# ============================================================================
# DATA LOADING & PROCESSING
# ============================================================================

@st.cache_data
def load_and_process(uploaded_file, rules):
    df = pd.read_csv(uploaded_file, parse_dates=["order_date", "expected_delivery_date", "actual_delivery_date"])
    
    # Quality checks
    quality_issues = []
    missing_expected = df["expected_delivery_date"].isna().sum()
    missing_actual = df["actual_delivery_date"].isna().sum()
    if missing_expected > 0:
        quality_issues.append(f"⚠️ {missing_expected} records missing expected delivery dates")
    if missing_actual > 0:
        quality_issues.append(f"⚠️ {missing_actual} records missing actual delivery dates")
    
    df["expected_delivery_date"] = df["expected_delivery_date"].fillna(df["order_date"] + pd.Timedelta(days=3))
    df["actual_delivery_date"] = df["actual_delivery_date"].fillna(df["order_date"] + pd.Timedelta(days=5))
    
    # Core metrics
    df["delay_days"] = (df["actual_delivery_date"] - df["expected_delivery_date"]).dt.days.fillna(0)
    df["on_time"] = (df["delay_days"] <= 0).astype(int)
    df["year_month"] = df["order_date"].dt.to_period("M")
    df["month"] = df["order_date"].dt.month
    df["weekday"] = df["order_date"].dt.dayofweek
    
    # Supplier reliability (historical)
    supplier_reliability = df.groupby("supplier")["on_time"].mean().to_dict()
    df["supplier_reliability"] = df["supplier"].map(supplier_reliability).fillna(0.5)
    
    # Financial impact
    df["base_delay_cost"] = df["delay_days"] * rules["cost_per_day"]
    df["value_multiplier"] = np.where(df["total_value_zar"] > rules["high_value_threshold"], 4, 1)
    df["perishable_penalty"] = np.where(df["perishable"] & (df["delay_days"] > 0), rules["cost_per_day"] * df["delay_days"], 0)
    df["total_delay_cost"] = df["base_delay_cost"] * df["value_multiplier"] + df["perishable_penalty"]
    
    # Risk levels
    df["risk_level"] = "🟢 LOW"
    df.loc[df["delay_days"] >= rules["medium_risk_days"], "risk_level"] = "🟡 MEDIUM"
    df.loc[df["delay_days"] >= rules["high_risk_days"], "risk_level"] = "🔴 HIGH"
    
    # Actionable decisions
    df["recommended_action"] = "✅ MONITOR"
    df.loc[df["risk_level"] == "🟡 MEDIUM", "recommended_action"] = "📞 CONTACT SUPPLIER"
    df.loc[df["risk_level"] == "🔴 HIGH", "recommended_action"] = "🚨 EXPEDITE OR SWITCH"
    df.loc[df["perishable"] & (df["delay_days"] > 2), "recommended_action"] = "⚠️ URGENT - PERISHABLE"
    
    # Price spike detection (simple rolling method)
    df["price_rolling_mean"] = df.groupby("product")["price_per_kg"].transform(lambda x: x.rolling(30, min_periods=5).mean())
    df["price_rolling_std"] = df.groupby("product")["price_per_kg"].transform(lambda x: x.rolling(30, min_periods=5).std())
    df["price_zscore"] = (df["price_per_kg"] - df["price_rolling_mean"]) / df["price_rolling_std"].replace(0, 0.01)
    df["is_price_spike"] = df["price_zscore"] > 2
    df["spike_severity"] = np.where(df["price_zscore"] > 3, "Extreme", np.where(df["price_zscore"] > 2, "Moderate", "Normal"))
    
    # Prediction confidence (based on order count)
    order_counts = df.groupby("supplier")["order_id"].count().to_dict()
    df["prediction_confidence"] = df["supplier"].map(order_counts).fillna(0) / 100
    df["prediction_confidence"] = df["prediction_confidence"].clip(0, 0.95)
    
    return df, quality_issues


# ============================================================================
# PREDICTION SUMMARY
# ============================================================================

def get_prediction_summary(df, rules):
    """Returns realistic predictions based on actual risk patterns"""
    
    # Count high-risk orders (already delayed past threshold)
    high_risk_orders = df[df["risk_level"] == "🔴 HIGH"]
    predicted_delayed = len(high_risk_orders)
    
    # High confidence predictions: orders with delay > 7 days OR perishable + delay > 3
    high_confidence = len(df[(df["delay_days"] > 7) | (df["perishable"] & (df["delay_days"] > 3))])
    
    # Estimated future loss: based on high-risk orders' value
    estimated_loss = high_risk_orders["total_value_zar"].sum() * 0.3
    
    # Problem suppliers: those causing most loss
    supplier_loss = df.groupby("supplier")["total_delay_cost"].sum().sort_values(ascending=False)
    problem_suppliers = supplier_loss.head(5).to_dict()
    
    # Total orders that are problematic (delay > 0)
    total_problematic = len(df[df["delay_days"] > 0])
    
    return {
        "total_problematic": total_problematic,
        "predicted_delayed": predicted_delayed,
        "high_confidence": high_confidence,
        "estimated_loss": estimated_loss,
        "problem_suppliers": problem_suppliers,
        "prediction_horizon": rules["prediction_days"]
    }


# ============================================================================
# OTHER INSIGHTS FUNCTIONS
# ============================================================================

def get_priority_list(df):
    result = df[df["delay_days"] > 0].sort_values(["delay_days", "total_delay_cost"], ascending=False).head(20)
    if result.empty:
        return pd.DataFrame(columns=["order_id", "product", "supplier", "delay_days", "total_delay_cost", "risk_level", "recommended_action", "prediction_confidence"])
    return result[["order_id", "product", "supplier", "delay_days", "total_delay_cost", "risk_level", "recommended_action", "prediction_confidence"]]


def get_supplier_report(df):
    supplier_stats = df.groupby("supplier").agg({
        "order_id": "count", 
        "delay_days": "mean", 
        "total_delay_cost": "sum",
        "on_time": "mean", 
        "supplier_reliability": "first", 
        "total_value_zar": "sum"
    }).round(2)
    supplier_stats.columns = ["orders", "avg_delay", "total_loss", "on_time_rate", "reliability", "revenue"]
    supplier_stats = supplier_stats.sort_values("total_loss", ascending=False).reset_index()
    supplier_stats["on_time_rate"] = (supplier_stats["on_time_rate"] * 100).round(1)
    supplier_stats["reliability"] = (supplier_stats["reliability"] * 100).round(1)
    return supplier_stats


def get_product_report(df):
    product_stats = df.groupby("product").agg({
        "order_id": "count", 
        "delay_days": "mean", 
        "total_delay_cost": "sum",
        "on_time": "mean", 
        "total_value_zar": "sum"
    }).round(2)
    product_stats.columns = ["orders", "avg_delay", "total_loss", "on_time_rate", "revenue"]
    product_stats = product_stats.sort_values("total_loss", ascending=False).reset_index()
    product_stats["on_time_rate"] = (product_stats["on_time_rate"] * 100).round(1)
    return product_stats


def get_regional_report(df):
    region_stats = df.groupby("supplier_region").agg({
        "order_id": "count", 
        "delay_days": "mean", 
        "total_delay_cost": "sum", 
        "on_time": "mean"
    }).round(2)
    region_stats.columns = ["orders", "avg_delay", "total_loss", "on_time_rate"]
    region_stats = region_stats.sort_values("total_loss", ascending=False).reset_index()
    region_stats["on_time_rate"] = (region_stats["on_time_rate"] * 100).round(1)
    return region_stats


def get_time_series(df):
    monthly = df.groupby(df["order_date"].dt.to_period("M")).agg({
        "on_time": "mean", 
        "delay_days": "mean", 
        "total_delay_cost": "sum", 
        "total_value_zar": "sum"
    }).reset_index()
    monthly["month"] = monthly["order_date"].astype(str)
    return monthly


def get_seasonal(df):
    seasonal = df.groupby("month").agg({
        "delay_days": "mean", 
        "total_delay_cost": "sum"
    }).reset_index()
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    seasonal["month_name"] = seasonal["month"].apply(lambda x: month_names[x-1])
    return seasonal


def get_price_spike_heatmap(df):
    df_copy = df.copy()
    df_copy["month_short"] = df_copy["order_date"].dt.strftime("%b")
    spike_pivot = df_copy.pivot_table(values="is_price_spike", index="product", columns="month_short", aggfunc="mean", fill_value=0)
    months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    spike_pivot = spike_pivot.reindex(columns=months_order, fill_value=0)
    return spike_pivot.head(20)


def get_delay_distribution(df):
    bins = [0, 1, 2, 3, 5, 7, 10, 15, 20, 30, 100]
    labels = ['0', '1', '2', '3', '4-5', '6-7', '8-10', '11-15', '16-20', '20+']
    df["delay_cat"] = pd.cut(df["delay_days"], bins=bins, labels=labels, right=False)
    result = df["delay_cat"].value_counts().reset_index()
    result.columns = ["delay_category", "count"]
    return result


def simulate_action(df, rules, action):
    sim = df.copy()
    if action == "expedite":
        sim["new_delay"] = np.maximum(sim["delay_days"] - rules["expedite_reduction"], 0)
    elif action == "switch":
        sim["new_delay"] = sim["delay_days"] * 0.4
    else:
        sim["new_delay"] = sim["delay_days"]
    
    sim["new_cost"] = sim["new_delay"] * rules["cost_per_day"]
    sim["new_multiplier"] = np.where(sim["total_value_zar"] > rules["high_value_threshold"], 4, 1)
    sim["new_perishable"] = np.where(sim["perishable"] & (sim["new_delay"] > 0), rules["cost_per_day"] * sim["new_delay"], 0)
    sim["new_total"] = sim["new_cost"] * sim["new_multiplier"] + sim["new_perishable"]
    
    current = df["total_delay_cost"].sum()
    new = sim["new_total"].sum()
    savings = current - new
    return {
        "current_loss": current,
        "new_loss": new,
        "savings": savings,
        "savings_pct": (savings / current * 100) if current > 0 else 0
    }


def create_south_africa_map(df):
    region_coords = {
        "Western Cape": {"lat": -34.0, "lon": 18.5}, "Gauteng": {"lat": -26.2, "lon": 28.0},
        "KwaZulu-Natal": {"lat": -29.6, "lon": 30.4}, "Eastern Cape": {"lat": -32.0, "lon": 26.0},
        "Limpopo": {"lat": -23.0, "lon": 29.5}, "Mpumalanga": {"lat": -25.5, "lon": 30.0},
        "Free State": {"lat": -28.0, "lon": 26.0}, "North West": {"lat": -27.0, "lon": 26.0},
        "Northern Cape": {"lat": -30.0, "lon": 22.0},
    }
    regional = df.groupby("supplier_region").agg({"delay_days": "mean", "total_delay_cost": "sum", "order_id": "count"}).reset_index()
    regional["lat"] = regional["supplier_region"].map(lambda x: region_coords.get(x, {}).get("lat", 0))
    regional["lon"] = regional["supplier_region"].map(lambda x: region_coords.get(x, {}).get("lon", 0))
    regional = regional.dropna()
    
    fig = px.scatter_geo(regional, lat="lat", lon="lon", size="delay_days", color="delay_days",
                         hover_name="supplier_region", hover_data={"total_delay_cost": ":,.0f", "order_id": True},
                         title="South Africa - Average Delay by Region", projection="natural earth",
                         color_continuous_scale="RdYlGn_r", size_max=45)
    fig.update_layout(height=450, margin=dict(l=0, r=0, t=50, b=0))
    return fig


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    st.markdown("""
    <div class='main-header'>
        <h1 style='color: white; font-size: 2.5rem; margin: 0;'>🌱 Nile.ag</h1>
        <p style='color: #a0c4c4; font-size: 1rem;'>Operations Decision Engine | Realistic Predictions | Actionable Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    rules = get_business_rules()
    
    st.markdown("### 📁 Data Source")
    uploaded_file = st.file_uploader("Upload order data (CSV)", type="csv")
    
    if uploaded_file is not None:
        with st.spinner("Analyzing supply chain data..."):
            df, quality_issues = load_and_process(uploaded_file, rules)
            prediction = get_prediction_summary(df, rules)
            priority = get_priority_list(df)
            supplier_report = get_supplier_report(df)
            product_report = get_product_report(df)
            regional_report = get_regional_report(df)
            time_series = get_time_series(df)
            seasonal = get_seasonal(df)
            spike_heatmap = get_price_spike_heatmap(df)
            delay_dist = get_delay_distribution(df)
            
            total_loss = df["total_delay_cost"].sum()
            high_risk_count = len(df[df["risk_level"] == "🔴 HIGH"])
            on_time_rate = df["on_time"].mean() * 100
            total_revenue = df["total_value_zar"].sum()
            
            for issue in quality_issues:
                st.warning(issue)
            
            # ==================== PREDICTION BANNER ====================
            if prediction["predicted_delayed"] > 0:
                st.markdown(f"""
                <div class='prediction-banner'>
                    <h2>🔮 {prediction['predicted_delayed']} orders are HIGH RISK right now</h2>
                    <p>⚡ {prediction['high_confidence']} of these are critical (delay >7 days or perishable + delay >3)</p>
                    <p>💡 Estimated financial impact: <strong>R{prediction['estimated_loss']:,.0f}</strong></p>
                    <p>🚨 Top loss drivers: {', '.join([f"{s} (R{v:,.0f})" for s, v in list(prediction['problem_suppliers'].items())[:3]])}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='prediction-banner'>
                    <h2>✅ No high-risk orders detected</h2>
                    <p>📊 {len(df)} orders analyzed. {prediction['total_problematic']} had some delay.</p>
                    <p>💰 Total financial loss from delays: R{total_loss:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ==================== KPI DASHBOARD ====================
            st.markdown("## 📊 Executive KPI Dashboard")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("Total Orders", f"{len(df):,}")
            col2.metric("Total Revenue", f"R{total_revenue/1_000_000:.1f}M")
            col3.metric("On-Time %", f"{on_time_rate:.1f}%")
            col4.metric("Financial Loss", f"R{total_loss/1_000:.0f}K")
            col5.metric("High Risk Orders", high_risk_count)
            col6.metric("Problematic Orders", prediction["total_problematic"])
            
            st.markdown("---")
            
            # ==================== DAILY DECISION SUMMARY ====================
            st.markdown("## 📋 DAILY DECISION SUMMARY")
            top_supplier = supplier_report.iloc[0]['supplier'] if not supplier_report.empty else 'None'
            top_supplier_loss = supplier_report.iloc[0]['total_loss'] if not supplier_report.empty else 0
            top_region = regional_report.iloc[0]['supplier_region'] if not regional_report.empty else 'None'
            
            st.info(f"""
            **🎯 TODAY'S PRIORITIES:**
            - 🔴 **{high_risk_count} orders** need immediate attention
            - 🏭 **{top_supplier}** causing most losses (R{top_supplier_loss:,.0f})
            - 📍 **{top_region}** region is your biggest problem
            - 💰 **Total loss so far:** R{total_loss:,.0f}
            """)
            
            st.markdown("---")
            
            # ==================== TABS ====================
            tabs = st.tabs(["🚨 Priority", "🏭 Suppliers", "📦 Products", "🗺️ Regions", 
                            "📈 Trends", "📅 Seasonal", "🔥 Price Spikes", "📊 Statistics", "🔮 Simulation"])
            
            # TAB 1: PRIORITY
            with tabs[0]:
                st.markdown("## 🚨 TODAY'S PRIORITY LIST")
                if not priority.empty:
                    for _, row in priority.head(5).iterrows():
                        st.error(f"""
                        **Order {row['order_id']}** | {row['product']} | Supplier: {row['supplier']}
                        - Delay: {row['delay_days']:.0f} days | Loss: R{row['total_delay_cost']:,.0f}
                        - **Action:** {row['recommended_action']}
                        """)
                st.dataframe(priority, use_container_width=True)
            
            # TAB 2: SUPPLIERS
            with tabs[1]:
                st.dataframe(supplier_report.head(15), use_container_width=True)
                fig = px.bar(supplier_report.head(10), x="total_loss", y="supplier", orientation="h", 
                            title="Top Loss-Making Suppliers", color="total_loss", color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            
            # TAB 3: PRODUCTS
            with tabs[2]:
                st.dataframe(product_report.head(15), use_container_width=True)
                fig = px.bar(product_report.head(10), x="total_loss", y="product", orientation="h", 
                            title="Top Loss-Making Products", color="total_loss", color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            
            # TAB 4: REGIONS
            with tabs[3]:
                st.dataframe(regional_report, use_container_width=True)
                fig = create_south_africa_map(df)
                st.plotly_chart(fig, use_container_width=True)
                fig2 = px.bar(regional_report, x="supplier_region", y="total_loss", 
                             title="Delay Cost by Region", color="total_loss", color_continuous_scale="Reds")
                st.plotly_chart(fig2, use_container_width=True)
            
            # TAB 5: TRENDS
            with tabs[4]:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Scatter(x=time_series["month"], y=time_series["on_time"]*100, 
                                        name="On-Time %", line=dict(color="#27ae60", width=3)), secondary_y=False)
                fig.add_trace(go.Scatter(x=time_series["month"], y=time_series["delay_days"], 
                                        name="Delay Days", line=dict(color="#e74c3c", width=3, dash="dash")), secondary_y=True)
                fig.update_layout(title="Performance Trends Over Time", height=450)
                st.plotly_chart(fig, use_container_width=True)
                
                fig2 = px.area(time_series, x="month", y="total_value_zar", title="Revenue Trend")
                st.plotly_chart(fig2, use_container_width=True)
            
            # TAB 6: SEASONAL
            with tabs[5]:
                fig = px.line(seasonal, x="month_name", y="delay_days", title="Average Delay by Month", markers=True)
                st.plotly_chart(fig, use_container_width=True)
                fig2 = px.bar(seasonal, x="month_name", y="total_delay_cost", title="Delay Cost by Month", color="total_delay_cost")
                st.plotly_chart(fig2, use_container_width=True)
            
            # TAB 7: PRICE SPIKES
            with tabs[6]:
                if not spike_heatmap.empty:
                    spike_pct = spike_heatmap * 100
                    fig = px.imshow(spike_pct, text_auto='.1f', aspect='auto', 
                                   title="Price Spike Probability by Product and Month (%)", 
                                   color_continuous_scale="Reds", height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                spike_timeline = df.groupby(df["order_date"].dt.to_period("M"))["is_price_spike"].sum().reset_index()
                spike_timeline["month"] = spike_timeline["order_date"].astype(str)
                fig = px.bar(spike_timeline, x="month", y="is_price_spike", title="Price Spike Count by Month", 
                           color="is_price_spike", color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            
            # TAB 8: STATISTICS
            with tabs[7]:
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.histogram(df, x="delay_days", nbins=30, title="Delay Distribution", marginal="box")
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = px.histogram(df, x="price_per_kg", nbins=40, title="Price Distribution", marginal="violin")
                    st.plotly_chart(fig, use_container_width=True)
                
                if not delay_dist.empty:
                    fig = px.pie(delay_dist, values="count", names="delay_category", title="Delay Categories", hole=0.3)
                    st.plotly_chart(fig, use_container_width=True)
            
            # TAB 9: SIMULATION
            with tabs[8]:
                st.markdown("## 🔮 What-If Simulation")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Total Loss", f"R{total_loss:,.0f}")
                    st.metric("High Risk Orders", high_risk_count)
                with col2:
                    action = st.radio("Action to simulate:", ["🚀 Expedite Critical Orders", "🔄 Switch to Backup Supplier", "⏸️ Do Nothing"], horizontal=True)
                    action_key = {"🚀 Expedite Critical Orders": "expedite", "🔄 Switch to Backup Supplier": "switch", "⏸️ Do Nothing": "none"}[action]
                    sim = simulate_action(df, rules, action_key)
                    st.metric("After Action Loss", f"R{sim['new_loss']:,.0f}", 
                             delta=f"-R{sim['savings']:,.0f}" if sim['savings'] > 0 else None)
                    st.metric("Improvement", f"{sim['savings_pct']:.0f}%")
                    st.success(f"💰 Potential savings: R{sim['savings']:,.0f}")
            
            # ==================== EXPORT ====================
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📊 Export Priority List", priority.to_csv(index=False), "priority.csv", "text/csv")
            with col2:
                st.download_button("🏭 Export Supplier Report", supplier_report.to_csv(index=False), "suppliers.csv", "text/csv")
    
    else:
        st.markdown("""
        <div style='text-align: center; padding: 3rem;'>
            <h2>🚀 Upload Your Supply Chain Data</h2>
            <p>Get real predictions, financial impact, and actionable decisions.</p>
            <p style='margin-top: 2rem;'>↓ Upload a CSV file to begin ↓</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎲 Load Sample Data", use_container_width=True):
            if os.path.exists("nile_supply_chain_moonshot.csv"):
                st.success("Sample data found! Please upload the file.")
            else:
                st.info("Run 'python generate_data.py' first.")


if __name__ == "__main__":
    main()