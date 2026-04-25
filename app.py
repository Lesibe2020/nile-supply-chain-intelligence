import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from insights import (
    load_data, find_declining_suppliers, worst_region_product_pairs,
    price_spike_calendar, predict_high_risk_orders, supplier_performance_timeline,
    cost_of_delays, product_risk_ranking
)

st.set_page_config(page_title="Nile.ag Intelligence", layout="wide")
st.title("🌱 Nile.ag – Supply Chain Deep Intelligence")
st.caption("Discover hidden patterns: declining suppliers, risk hotspots, price spike seasons")

uploaded = st.file_uploader("Upload CSV (nile_supply_chain.csv)", type="csv")

if uploaded:
    df = load_data(uploaded)
    
    # CLEAN UP PRODUCT NAMES - Remove duplicates by stripping whitespace
    df['product'] = df['product'].astype(str).str.strip()
    
    # Basic risk classification for display
    def classify_risk(delay, perishable):
        if perishable:
            if delay > 2: return "Critical"
            elif delay > 1: return "High"
            elif delay > 0: return "Medium"
        else:
            if delay > 5: return "Critical"
            elif delay > 3: return "High"
            elif delay > 0: return "Medium"
        return "On Time"
    
    df["risk_level"] = df.apply(lambda row: classify_risk(row["delay_days"], row["perishable"]), axis=1)
    
    # ====== DISCOVERY FUNCTIONS ======
    declining = find_declining_suppliers(df)
    worst_pairs = worst_region_product_pairs(df)
    spike_calendar = price_spike_calendar(df)
    predicted_risk = predict_high_risk_orders(df, declining)
    cost_impact = cost_of_delays(df)
    product_ranking = product_risk_ranking(df)
    
    # TABS for different insights
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Dashboard", 
        "🔻 Declining Suppliers", 
        "🌍 Region-Product Hotspots", 
        "💰 Price Spikes & Loss", 
        "🔮 Predictive Risk"
    ])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Orders", f"{len(df):,}")
        col2.metric("Avg Delay", f"{df['delay_days'].mean():.1f} days")
        col3.metric("On-Time %", f"{df['on_time'].mean()*100:.1f}%")
        total_value = df["total_value_zar"].sum()
        col4.metric("Total Value", f"R{total_value:,.0f}")
        
        st.metric("📉 Estimated Loss from Delays", f"R{cost_impact['estimated_financial_loss']:,.0f}", 
                  delta=f"{cost_impact['loss_percent']}% of revenue")
        
        st.subheader("Top 10 Riskiest Products")
        st.dataframe(product_ranking)
        
        # Pie chart of risk levels
        risk_counts = df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["risk_level", "count"]
        fig = px.pie(risk_counts, values="count", names="risk_level", 
                     title="Order Risk Distribution", color_discrete_sequence=px.colors.sequential.Reds_r)
        st.plotly_chart(fig, use_container_width=True)
        
        # Executive summary
        st.subheader("📋 Executive Summary")
        worst_product_text = worst_pairs.iloc[0]['product'] if not worst_pairs.empty else "N/A"
        worst_region_text = worst_pairs.iloc[0]['supplier_region'] if not worst_pairs.empty else "N/A"
        worst_delay_val = worst_pairs.iloc[0]['avg_delay'] if not worst_pairs.empty else 0
        
        st.info(f"""
        - **{len(declining)} suppliers** are showing declining reliability → {'review contracts' if len(declining) > 0 else 'all suppliers stable ✅'}
        - **{worst_product_text} from {worst_region_text}** has {worst_delay_val} days avg delay
        - **{spike_calendar.iloc[0]['month_name'] if not spike_calendar.empty else 'N/A'}** has highest price spike rate ({spike_calendar.iloc[0]['spike_rate'] if not spike_calendar.empty else 0}%)
        - **R{df[df['risk_level'].isin(['Critical','High'])]['total_value_zar'].sum():,.0f}** value at risk
        """)
    
    with tab2:
        st.subheader("🔻 Suppliers with Declining On-Time Performance")
        if not declining.empty:
            st.dataframe(declining)
            st.warning(f"{len(declining)} suppliers need immediate attention")
            
            # Show timeline for worst declining supplier
            worst_declining = declining.iloc[0]["supplier"]
            st.subheader(f"📉 Timeline for {worst_declining}")
            timeline = supplier_performance_timeline(df, worst_declining)
            fig = px.line(timeline, x="month", y="on_time_pct", title=f"{worst_declining} – Monthly On-Time %")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No suppliers with significant decline detected – all suppliers are stable or improving!")
            st.balloons()
    
    with tab3:
        st.subheader("🌍 Worst Region × Product Combinations")
        st.dataframe(worst_pairs)
        
        # FIXED HEATMAP - Complete rewrite to avoid duplicate columns
        st.subheader("🔥 Delay Heatmap (Region × Product)")
        
        # Create pivot table
        pivot = df.pivot_table(values="delay_days", index="supplier_region", 
                               columns="product", aggfunc="mean", fill_value=0)
        
        # FORCE UNIQUE COLUMN NAMES - Add numbers to duplicates
        cols = pd.Series(pivot.columns)
        for i, col in enumerate(cols):
            if cols[cols == col].count() > 1:
                # Rename duplicate to product_1, product_2, etc.
                duplicate_count = 1
                for j, check_col in enumerate(cols):
                    if check_col == col:
                        pivot.columns.values[j] = f"{col}_{duplicate_count}"
                        duplicate_count += 1
        
        # Also clean index names
        pivot.index = [str(idx).strip() for idx in pivot.index]
        
        # Select top products from worst_pairs
        if not worst_pairs.empty:
            top_products_raw = worst_pairs["product"].head(10).tolist()
        else:
            top_products_raw = pivot.columns[:10].tolist()
        
        # Find which columns exist (with their new names)
        top_products_found = []
        for prod in top_products_raw:
            matching = [col for col in pivot.columns if col.startswith(prod) or col == prod]
            top_products_found.extend(matching[:1])  # Take first match only
        
        pivot_filtered = pivot[top_products_found] if top_products_found else pivot
        
        if not pivot_filtered.empty and pivot_filtered.shape[1] > 1:
            # Create heatmap
            fig = px.imshow(
                pivot_filtered.values, 
                x=pivot_filtered.columns.tolist(),
                y=pivot_filtered.index.tolist(),
                text_auto=".1f", 
                color_continuous_scale="Reds",
                aspect="auto", 
                height=500,
                title="Average Delay (days) by Region and Product"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Dark red = high average delay. Investigate these specific lanes.")
        else:
            st.info("Not enough data to display heatmap. Try generating more orders.")
    
    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📅 Price Spike Calendar")
            st.dataframe(spike_calendar)
        
        with col2:
            st.subheader("Bar Chart – Spike Rate by Month")
            if not spike_calendar.empty:
                fig = px.bar(spike_calendar, x="month_name", y="spike_rate", 
                             title="Price Spike Rate (%)", color="spike_rate",
                             color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No price spike data available")
        
        st.subheader("💰 Financial Impact of Delays")
        col1, col2, col3 = st.columns(3)
        col1.metric("Orders Delayed", f"{cost_impact['total_orders_delayed']:,}")
        col2.metric("Critical Delays (>5 days)", f"{cost_impact['critical_delays']:,}")
        col3.metric("Estimated Loss", f"R{cost_impact['estimated_financial_loss']:,.0f}")
        
        st.caption("Assumptions: 15% cancellation rate on delayed orders, 10% discount compensation on delayed perishable orders.")
    
    with tab5:
        st.subheader("🔮 Predicted High-Risk Orders")
        st.caption("Based on: supplier reliability declining + perishable product + existing delay")
        
        if not predicted_risk.empty:
            st.metric("Value at Risk (predicted)", f"R{predicted_risk['value_at_risk'].iloc[0]:,.0f}")
            st.dataframe(predicted_risk[["order_id", "supplier", "product", "order_date", "delay_days", "total_value_zar"]])
            
            st.subheader("📋 Recommended Actions")
            for supplier in predicted_risk["supplier"].unique()[:3]:
                st.write(f"- **{supplier}**: Review contract, consider alternative supplier for perishable products")
        else:
            st.success("✅ No high-risk predictions at this time – all orders appear normal")
    
    # Download button
    st.divider()
    st.download_button("📥 Download Full Enriched Data", 
                       df.to_csv(index=False).encode(), 
                       "nile_analyzed.csv", "text/csv")

else:
    st.info("👈 Upload your `nile_supply_chain.csv` (generated by generate_data.py) to start discovering insights.")