 🌱 Nile.ag Supply Chain Intelligence System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)
[![Made with Pandas](https://img.shields.io/badge/Made%20with-Pandas-150458.svg)](https://pandas.pydata.org/)

> **A production-ready decision intelligence tool for fresh produce supply chains.**  
> Monitor delays, detect price anomalies, rank suppliers fairly, and discover hidden operational risks.

---

## 📸 Dashboard Preview

| Executive Dashboard | Supplier Performance |
|--------------------|----------------------|
| *Run locally to see interactive dashboard* | *Run locally to see interactive dashboard* |

> 🔗 **Live Demo:** *[Deploy to Streamlit Cloud for public URL]*

---

## 🎯 The Problem

Nile.ag operates a fresh produce e‑commerce platform across South Africa. They face three chronic challenges:

| Challenge | Impact |
|-----------|--------|
| **Delivery delays** | Spoilage, customer churn, lost revenue |
| **Price volatility** | Margin erosion, unpredictable costs |
| **Inconsistent supplier performance** | No fair way to compare suppliers handling different products (heavy vs light, perishable vs non‑perishable) |

**Existing dashboards show WHAT happened. This system tells you WHAT TO DO.**

---

## ✨ What This System Does

| Feature | How It Works |
|---------|---------------|
| **📊 Realistic Data Generator** | Creates 12,000+ synthetic orders (20 products, 15 suppliers, 2+ years) with exponential delays, seasonality, price spikes, and supplier reliability decay |
| **🔍 Risk Classification** | Perishable‑aware thresholds (tomatoes: 2 days = Critical; onions: 5 days = Critical) |
| **💰 Price Anomaly Detection** | Flags orders priced >2 standard deviations above product average |
| **🏆 Fair Supplier Score** | `On-Time% – (Avg Delay × 5)` – simple but interpretable |
| **📉 Declining Supplier Detection** | Linear regression trend analysis to find suppliers getting worse over time |
| **🌍 Regional Hotspots** | Identifies worst (region × product) delay combinations |
| **🔮 Predictive Risk** | Flags orders likely to become critical based on supplier decline + perishability |
| **💸 Financial Impact** | Estimates revenue loss from delays (cancellations + discounts) |
| **📊 Interactive Dashboard** | 5‑tab Streamlit dashboard with heatmaps, rankings, and auto‑executive summary |

---

## 🏗️ System Architecture
┌─────────────────────────────────────────────────────────────┐
│ USER INTERFACE LAYER │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Streamlit │ │ Power BI │ │ Terminal │ │
│ │ Dashboard │ │ (SQL) │ │ (CLI) │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ ANALYSIS LAYER │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Risk Engine │ │ Anomaly │ │ Supplier │ │
│ │ │ │ Detection │ │ Scoring │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ DATA LAYER │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ CSV / │ │ Parquet │ │ SQLite / │ │
│ │ Generator │ │ (Archive) │ │ PostgreSQL │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘

text

---

## 📁 Project Structure
nile_insight/
│
├── generate_data.py # 12,000‑order synthetic data generator
├── insights.py # 7 discovery functions (declining suppliers, hotspots, etc.)
├── streamlit_app.py # Interactive dashboard (5 tabs)
├── queries.sql # 10 production SQL queries for Power BI
├── requirements.txt # Python dependencies
├── README.md # This file
│
└── data/ (auto‑created)
├── nile_supply_chain.csv # Generated dataset
└── nile_analyzed.csv # Exported enriched data

text

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone & Install

```bash
git clone https://github.com/Lesibe2020/nile-supply-chain-intelligence.git
cd nile-supply-chain-intelligence
pip install -r requirements.txt
2. Generate Synthetic Data
bash
python generate_data.py
Output:

text
✅ Generated 120,000 orders | Date range: 2022-01-01 to 2024-06-30
   Products: 20 | Suppliers: 15
3. Launch the Dashboard
bash
streamlit run streamlit_app.py
Your browser opens to http://localhost:8501. Upload the generated CSV and explore.

4. Run SQL Queries (Optional)
Load nile_supply_chain.csv into any SQL database and run queries.sql for Power BI / Tableau.

🌐 Deployment to Streamlit Cloud (Free)
Push your code to GitHub

bash
git add .
git commit -m "Initial commit"
git push origin main
Go to share.streamlit.io

Click "New app" and connect your GitHub repository

Configure:

Repository: Lesibe2020/nile-supply-chain-intelligence

Branch: main

Main file: streamlit_app.py

Click Deploy – your app will be live at:
https://lesibe2020-nile-supply-chain-intelligence.streamlit.app

⚠️ Note: You'll need to upload the CSV file manually in the dashboard. The sample data is generated locally with generate_data.py.

📊 Dashboard Tabs Explained
Tab	What You'll Discover
📊 Executive Dashboard	Total orders, avg delay, on‑time %, revenue, value at risk, top riskiest products
🔻 Declining Suppliers	Which suppliers are getting worse over time (trend analysis + timeline charts)
🌍 Region-Product Hotspots	Worst (region × product) delay combinations + interactive heatmap
💰 Price Spikes & Loss	Monthly price spike calendar + estimated financial impact of delays
🔮 Predictive Risk	Orders flagged as high‑risk before they become critical
📋 Data Schema
Original Generated CSV (nile_supply_chain.csv)
Column Name	Data Type	Description	Example
order_id	string	Unique order identifier	ORD-10000
order_date	datetime	Date order was placed	2023-06-15
product	string	Product name	Avocados, Spinach
product_category	string	Category of product	Veg, Fruit, Root
perishable	boolean	Whether product spoils quickly	True, False
supplier	string	Supplier name	Supplier_A
supplier_region	string	Region where supplier is based	Western Cape
quantity_kg	integer	Order quantity in kilograms	150
price_per_kg	float	Price per kilogram in ZAR	35.50
total_value_zar	float	Total order value	5325.00
promised_days	integer	Days promised for delivery	3
actual_days	integer	Actual days to deliver	4
delay_days	integer	Actual - promised	2
expected_delivery_date	datetime	Promised delivery date	2023-06-18
actual_delivery_date	datetime	Actual delivery date	2023-06-20
on_time	boolean	1 if delay_days <= 0	1
Enriched DataFrame (After Processing)
Column Name	Data Type	Description	Calculation
risk_level	string	Risk classification	Perishable: >2d=Critical; Non-perishable: >5d=Critical
price_mean	float	Average price for product	groupby('product')['price_per_kg'].mean()
price_anomaly	boolean	Price spike flag	price > mean + 2×std
reliability_score	float	Supplier score	on_time% - (avg_delay × 5)
action_required	string	Contract action	⚠️ Review Contract if score <60 and orders >30
trend_slope	float	Performance trend	Linear regression of on‑time % over time
🔍 Key Insights You'll Uncover
Discovery	Business Action
Supplier reliability declining over time	Review contract, renegotiate SLAs
Spinach from Western Cape has 5.2 days avg delay	Investigate logistics, add cold chain
Price spikes peak in March (8.5% of orders)	Procurement buys earlier, hedge prices
15 orders predicted as high‑risk	Proactive customer communication
R247k estimated loss from delays	Business case for logistics investment
📈 Sample Outputs
Supplier Performance Ranking
Supplier	On-Time %	Avg Delay	Reliability Score	Action
Supplier_A	92.3%	0.8 days	88.3	✅ Monitor
Supplier_B	78.1%	2.1 days	67.6	✅ Monitor
Supplier_C	61.2%	3.5 days	43.7	⚠️ Review Contract
Risk Distribution
text
Critical:   8.2%
High:      12.4%
Medium:    18.7%
On Time:   60.7%
Price Spike Calendar
Month	Spike Rate
March	8.5%
September	7.2%
December	6.8%
🛠️ Technology Stack
Category	Technologies
Languages	Python 3.10+
Data Processing	Pandas, NumPy, SciPy
Visualization	Plotly, Streamlit
Dashboard	Streamlit (5‑tab interactive UI)
SQL	PostgreSQL/MySQL/SQLite compatible
Statistics	Linear regression (trend analysis), standard deviation (anomaly detection)
📝 SQL Queries for Power BI
The queries.sql file contains 10 production queries:

Executive Dashboard – Overall KPIs

Supplier Performance Ranking

Declining Suppliers – Monthly Trend Analysis

Worst Region–Product Hotspots

Price Spike Calendar

Product Risk Ranking

Customer Impact Analysis

Monthly Trend Analysis

Price Anomaly Details

Operational Alerts – Immediate Action

To use in Power BI:

Get Data → PostgreSQL/MySQL → Advanced options → Paste query

🧪 Running Tests
bash
# Verify data integrity
python -c "import pandas as pd; df = pd.read_csv('nile_supply_chain.csv'); print(f'✅ {len(df):,} orders loaded')"

# Check column data types
python -c "import pandas as pd; df = pd.read_csv('nile_supply_chain.csv'); print(df.dtypes)"
Sample output:

text
order_id                 object
order_date       datetime64[ns]
product                  object
product_category         object
perishable                 bool
supplier                 object
supplier_region          object
quantity_kg               int64
price_per_kg            float64
total_value_zar         float64
delay_days                int64
on_time                   int64
dtype: object
🤝 Contributing
This is a portfolio project. Suggestions welcome via GitHub Issues.

📄 License
MIT License – free for academic and commercial use.

👤 Author
Lesibe Dikgale

📧 Email: bpldikgale75@gmail.com

🔗 LinkedIn: www.linkedin.com/in/lesibe-dikgale-49240b228

💻 GitHub: https://github.com/Lesibe2020

🙏 Acknowledgments
Built as a demonstration for Nile.ag internship application

Data generation inspired by real fresh produce supply chains in South Africa

Thanks to the Streamlit and Plotly communities

⭐ Support This Project
If you find this useful, please star the repository on GitHub!

Built with ❤️ for fresh produce supply chains in Africa.





