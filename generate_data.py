# generate_data.py - MOON SHOT EDITION
# Complete supply chain data generator with product risk weights

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import json

np.random.seed(42)
random.seed(42)

# =========================
# CONFIGURATION
# =========================
N_ORDERS = 100000
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)
DAYS_RANGE = (END_DATE - START_DATE).days

# =========================
# ALL 9 SOUTH AFRICAN PROVINCES
# =========================
PROVINCES = {
    "Western Cape": {"base_reliability": 0.94, "penalty": 0, "risk": 0.05, "specialty": "Premium Fruits, Vegetables, Wine Grapes"},
    "Gauteng": {"base_reliability": 0.90, "penalty": 0, "risk": 0.08, "specialty": "Distribution Hub, Grains"},
    "KwaZulu-Natal": {"base_reliability": 0.85, "penalty": 1, "risk": 0.12, "specialty": "Subtropical Fruits, Vegetables"},
    "Eastern Cape": {"base_reliability": 0.80, "penalty": 2, "risk": 0.15, "specialty": "Citrus, Livestock"},
    "Mpumalanga": {"base_reliability": 0.78, "penalty": 2, "risk": 0.14, "specialty": "Tropical Fruits, Vegetables"},
    "Free State": {"base_reliability": 0.76, "penalty": 1, "risk": 0.10, "specialty": "Grains, Potatoes"},
    "North West": {"base_reliability": 0.74, "penalty": 1, "risk": 0.11, "specialty": "Maize, Sunflowers"},
    "Limpopo": {"base_reliability": 0.70, "penalty": 3, "risk": 0.18, "specialty": "Subtropical Fruits, Avocados"},
    "Northern Cape": {"base_reliability": 0.68, "penalty": 2, "risk": 0.16, "specialty": "Grapes, Dates"},
}

# =========================
# INTERNATIONAL REGIONS
# =========================
INTERNATIONAL_REGIONS = {
    "Spain": {"base_reliability": 0.88, "lead_time": 7, "premium": 1.15},
    "Netherlands": {"base_reliability": 0.92, "lead_time": 5, "premium": 1.20},
    "USA": {"base_reliability": 0.90, "lead_time": 10, "premium": 1.18},
    "Italy": {"base_reliability": 0.87, "lead_time": 8, "premium": 1.16},
    "Chile": {"base_reliability": 0.85, "lead_time": 12, "premium": 1.12},
    "Peru": {"base_reliability": 0.82, "lead_time": 10, "premium": 1.10},
    "Thailand": {"base_reliability": 0.75, "lead_time": 14, "premium": 1.08},
    "China": {"base_reliability": 0.78, "lead_time": 15, "premium": 1.05},
    "India": {"base_reliability": 0.72, "lead_time": 12, "premium": 1.03},
    "Kenya": {"base_reliability": 0.70, "lead_time": 8, "premium": 1.02},
}

# =========================
# COMPLETE PRODUCTS WITH RISK WEIGHTS
# =========================
PRODUCTS = {
    # ===== PREMIUM VEGETABLES (High Risk - Perishable) =====
    "Heirloom Tomatoes": {"cat": "Premium Vegetables", "perish": True, "base": 28, "season_peak": [1,2,3], "volatility": 1.4, "shelf_life": 5, "risk_weight": 0.95},
    "Organic Butter Lettuce": {"cat": "Premium Vegetables", "perish": True, "base": 24, "season_peak": [1,2,11,12], "volatility": 1.3, "shelf_life": 3, "risk_weight": 0.98},
    "Baby Kale": {"cat": "Premium Vegetables", "perish": True, "base": 35, "season_peak": [4,5,6], "volatility": 1.5, "shelf_life": 4, "risk_weight": 0.96},
    "Microgreens Mix": {"cat": "Premium Vegetables", "perish": True, "base": 48, "season_peak": [3,4,5], "volatility": 1.7, "shelf_life": 2, "risk_weight": 1.00},
    "Rainbow Chard": {"cat": "Premium Vegetables", "perish": True, "base": 32, "season_peak": [5,6,7], "volatility": 1.4, "shelf_life": 5, "risk_weight": 0.94},
    "Asparagus": {"cat": "Premium Vegetables", "perish": True, "base": 42, "season_peak": [4,5,6], "volatility": 1.5, "shelf_life": 7, "risk_weight": 0.92},
    "Artichokes": {"cat": "Premium Vegetables", "perish": True, "base": 38, "season_peak": [3,4,5], "volatility": 1.3, "shelf_life": 7, "risk_weight": 0.90},
    
    # ===== STANDARD VEGETABLES (Medium-High Risk) =====
    "Tomatoes": {"cat": "Vegetables", "perish": True, "base": 12, "season_peak": [1,2,3], "volatility": 1.2, "shelf_life": 7, "risk_weight": 0.85},
    "Lettuce Iceberg": {"cat": "Vegetables", "perish": True, "base": 9, "season_peak": [1,2,11,12], "volatility": 1.1, "shelf_life": 7, "risk_weight": 0.88},
    "Lettuce Romaine": {"cat": "Vegetables", "perish": True, "base": 11, "season_peak": [1,2,11,12], "volatility": 1.1, "shelf_life": 7, "risk_weight": 0.88},
    "Spinach": {"cat": "Vegetables", "perish": True, "base": 15, "season_peak": [4,5,6], "volatility": 1.3, "shelf_life": 5, "risk_weight": 0.92},
    "Cabbage": {"cat": "Vegetables", "perish": False, "base": 8, "season_peak": [5,6,7], "volatility": 0.8, "shelf_life": 21, "risk_weight": 0.45},
    "Broccoli": {"cat": "Vegetables", "perish": True, "base": 16, "season_peak": [4,5,6], "volatility": 1.2, "shelf_life": 7, "risk_weight": 0.82},
    "Cauliflower": {"cat": "Vegetables", "perish": True, "base": 15, "season_peak": [7,8,9], "volatility": 1.1, "shelf_life": 7, "risk_weight": 0.80},
    "Bell Peppers Red": {"cat": "Vegetables", "perish": True, "base": 22, "season_peak": [8,9,10], "volatility": 1.4, "shelf_life": 10, "risk_weight": 0.86},
    "Bell Peppers Green": {"cat": "Vegetables", "perish": True, "base": 18, "season_peak": [8,9,10], "volatility": 1.3, "shelf_life": 10, "risk_weight": 0.84},
    "Cucumbers": {"cat": "Vegetables", "perish": True, "base": 14, "season_peak": [10,11,12], "volatility": 1.1, "shelf_life": 8, "risk_weight": 0.83},
    "Zucchini": {"cat": "Vegetables", "perish": True, "base": 13, "season_peak": [6,7,8], "volatility": 1.2, "shelf_life": 7, "risk_weight": 0.85},
    "Eggplant": {"cat": "Vegetables", "perish": True, "base": 17, "season_peak": [7,8,9], "volatility": 1.2, "shelf_life": 10, "risk_weight": 0.82},
    "Celery": {"cat": "Vegetables", "perish": True, "base": 11, "season_peak": [9,10,11], "volatility": 1.0, "shelf_life": 14, "risk_weight": 0.78},
    "Green Beans": {"cat": "Vegetables", "perish": True, "base": 19, "season_peak": [5,6,7], "volatility": 1.2, "shelf_life": 7, "risk_weight": 0.86},
    "Brussels Sprouts": {"cat": "Vegetables", "perish": True, "base": 21, "season_peak": [9,10,11], "volatility": 1.2, "shelf_life": 10, "risk_weight": 0.84},
    "Butternut Squash": {"cat": "Vegetables", "perish": False, "base": 14, "season_peak": [3,4,5], "volatility": 0.9, "shelf_life": 60, "risk_weight": 0.40},
    
    # ===== ROOT VEGETABLES (Low Risk - Long Shelf Life) =====
    "Potatoes White": {"cat": "Roots", "perish": False, "base": 7, "season_peak": [5,6,7], "volatility": 0.7, "shelf_life": 60, "risk_weight": 0.35},
    "Potatoes Sweet": {"cat": "Roots", "perish": False, "base": 13, "season_peak": [4,5,6], "volatility": 0.8, "shelf_life": 45, "risk_weight": 0.38},
    "Onions Red": {"cat": "Roots", "perish": False, "base": 9, "season_peak": [8,9,10], "volatility": 0.8, "shelf_life": 90, "risk_weight": 0.30},
    "Onions Brown": {"cat": "Roots", "perish": False, "base": 8, "season_peak": [8,9,10], "volatility": 0.7, "shelf_life": 90, "risk_weight": 0.28},
    "Carrots": {"cat": "Roots", "perish": False, "base": 9, "season_peak": [6,7,8], "volatility": 0.8, "shelf_life": 30, "risk_weight": 0.35},
    "Beetroot": {"cat": "Roots", "perish": False, "base": 11, "season_peak": [5,6,7], "volatility": 0.8, "shelf_life": 30, "risk_weight": 0.35},
    "Radishes": {"cat": "Roots", "perish": True, "base": 8, "season_peak": [3,4,5], "volatility": 1.0, "shelf_life": 10, "risk_weight": 0.70},
    "Garlic": {"cat": "Roots", "perish": False, "base": 50, "season_peak": [10,11,12], "volatility": 1.4, "shelf_life": 180, "risk_weight": 0.50},
    "Ginger": {"cat": "Roots", "perish": False, "base": 45, "season_peak": [11,12,1], "volatility": 1.3, "shelf_life": 60, "risk_weight": 0.48},
    
    # ===== PREMIUM FRUITS (Very High Risk) =====
    "Organic Avocados": {"cat": "Premium Fruits", "perish": True, "base": 65, "season_peak": [2,3,4], "volatility": 1.8, "shelf_life": 5, "risk_weight": 0.98},
    "Organic Berries Mix": {"cat": "Premium Fruits", "perish": True, "base": 75, "season_peak": [8,9,10], "volatility": 1.9, "shelf_life": 3, "risk_weight": 1.00},
    "Dragon Fruit": {"cat": "Premium Fruits", "perish": True, "base": 58, "season_peak": [6,7,8], "volatility": 1.6, "shelf_life": 7, "risk_weight": 0.92},
    "Passion Fruit": {"cat": "Premium Fruits", "perish": True, "base": 52, "season_peak": [1,2,12], "volatility": 1.5, "shelf_life": 7, "risk_weight": 0.90},
    
    # ===== STANDARD FRUITS (Medium Risk) =====
    "Apples Red": {"cat": "Fruits", "perish": False, "base": 20, "season_peak": [3,4,5], "volatility": 0.8, "shelf_life": 90, "risk_weight": 0.40},
    "Apples Green": {"cat": "Fruits", "perish": False, "base": 22, "season_peak": [3,4,5], "volatility": 0.8, "shelf_life": 90, "risk_weight": 0.40},
    "Bananas": {"cat": "Fruits", "perish": True, "base": 10, "season_peak": [1,2,3,4,5], "volatility": 1.1, "shelf_life": 10, "risk_weight": 0.75},
    "Oranges Navel": {"cat": "Fruits", "perish": False, "base": 18, "season_peak": [6,7,8], "volatility": 0.7, "shelf_life": 45, "risk_weight": 0.38},
    "Oranges Valencia": {"cat": "Fruits", "perish": False, "base": 16, "season_peak": [9,10,11], "volatility": 0.7, "shelf_life": 45, "risk_weight": 0.38},
    "Lemons": {"cat": "Fruits", "perish": False, "base": 15, "season_peak": [4,5,6], "volatility": 0.7, "shelf_life": 60, "risk_weight": 0.35},
    "Avocados Hass": {"cat": "Fruits", "perish": True, "base": 35, "season_peak": [2,3,4], "volatility": 1.5, "shelf_life": 7, "risk_weight": 0.88},
    "Mangoes": {"cat": "Fruits", "perish": True, "base": 22, "season_peak": [11,12,1], "volatility": 1.3, "shelf_life": 10, "risk_weight": 0.85},
    "Pineapples": {"cat": "Fruits", "perish": False, "base": 28, "season_peak": [1,2,12], "volatility": 1.0, "shelf_life": 21, "risk_weight": 0.55},
    "Grapes Red": {"cat": "Fruits", "perish": True, "base": 35, "season_peak": [1,2,3], "volatility": 1.3, "shelf_life": 14, "risk_weight": 0.80},
    "Strawberries": {"cat": "Fruits", "perish": True, "base": 38, "season_peak": [8,9,10], "volatility": 1.6, "shelf_life": 5, "risk_weight": 0.94},
    "Blueberries": {"cat": "Fruits", "perish": True, "base": 58, "season_peak": [11,12,1], "volatility": 1.7, "shelf_life": 7, "risk_weight": 0.96},
    "Watermelon": {"cat": "Fruits", "perish": False, "base": 15, "season_peak": [12,1,2], "volatility": 0.9, "shelf_life": 21, "risk_weight": 0.50},
    
    # ===== HERBS (Very High Risk - Extremely Perishable) =====
    "Fresh Basil": {"cat": "Herbs", "perish": True, "base": 48, "season_peak": [2,3,4], "volatility": 1.6, "shelf_life": 5, "risk_weight": 0.96},
    "Fresh Cilantro": {"cat": "Herbs", "perish": True, "base": 42, "season_peak": [3,4,5], "volatility": 1.5, "shelf_life": 5, "risk_weight": 0.95},
    "Fresh Parsley": {"cat": "Herbs", "perish": True, "base": 38, "season_peak": [3,4,5], "volatility": 1.5, "shelf_life": 7, "risk_weight": 0.93},
    "Rosemary": {"cat": "Herbs", "perish": True, "base": 35, "season_peak": [4,5,6], "volatility": 1.4, "shelf_life": 10, "risk_weight": 0.90},
    "Mint": {"cat": "Herbs", "perish": True, "base": 32, "season_peak": [5,6,7], "volatility": 1.3, "shelf_life": 7, "risk_weight": 0.92},
    
    # ===== GRAINS (Lowest Risk) =====
    "Organic Quinoa": {"cat": "Grains", "perish": False, "base": 55, "season_peak": [4,5,6], "volatility": 1.1, "shelf_life": 365, "risk_weight": 0.25},
    "Brown Rice": {"cat": "Grains", "perish": False, "base": 15, "season_peak": [4,5,6], "volatility": 0.7, "shelf_life": 365, "risk_weight": 0.20},
    "White Rice": {"cat": "Grains", "perish": False, "base": 12, "season_peak": [4,5,6], "volatility": 0.6, "shelf_life": 365, "risk_weight": 0.18},
    "Lentils": {"cat": "Grains", "perish": False, "base": 18, "season_peak": [6,7,8], "volatility": 0.8, "shelf_life": 365, "risk_weight": 0.22},
    "Chickpeas": {"cat": "Grains", "perish": False, "base": 16, "season_peak": [6,7,8], "volatility": 0.8, "shelf_life": 365, "risk_weight": 0.22},
}

product_names = list(PRODUCTS.keys())

# =========================
# SUPPLIER POOL WITH SPECIALIZATION
# =========================
SUPPLIER_POOL = []
supplier_id = 1

# Create local suppliers for each province
for province, data in PROVINCES.items():
    for size in ["Small", "Medium", "Large"]:
        for specialty in data["specialty"].split(", ")[:2]:
            SUPPLIER_POOL.append({
                "id": supplier_id,
                "name": f"{province} {size} {specialty.split()[0] if specialty else 'Produce'}",
                "region": province,
                "type": "Local",
                "scale": size,
                "reliability": data["base_reliability"] * random.uniform(0.95, 1.05),
                "penalty": data["penalty"],
                "specialty": specialty,
                "organic": random.random() < 0.3,
            })
            supplier_id += 1

# Create international suppliers
for country, data in INTERNATIONAL_REGIONS.items():
    for size in ["Medium", "Large"]:
        SUPPLIER_POOL.append({
            "id": supplier_id,
            "name": f"{country} {size} Imports",
            "region": country,
            "type": "International",
            "scale": size,
            "reliability": data["base_reliability"] * random.uniform(0.95, 1.05),
            "lead_time": data["lead_time"],
            "premium": data["premium"],
            "organic": random.random() < 0.2,
        })
        supplier_id += 1

# =========================
# HELPER FUNCTIONS
# =========================
def format_currency(value):
    if value >= 1_000_000:
        return f"R{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"R{value/1_000:.1f}K"
    return f"R{value:.0f}"

def calculate_supplier_risk_score(supplier, product, qty):
    """Calculate supplier accountability score based on product risk weight"""
    product_data = PRODUCTS[product]
    
    # Base score from reliability
    score = supplier["reliability"] * 100
    
    # Adjust for product risk weight (higher risk products need higher reliability)
    risk_adjustment = product_data["risk_weight"] * 20
    score -= risk_adjustment
    
    # Volume penalty for small suppliers with large orders
    if supplier["scale"] == "Small" and qty > 1000:
        score -= 10
    
    # Organic handling premium
    if supplier.get("organic", False) and product_data["perish"]:
        score -= 5
    
    # International shipping adds risk
    if supplier["type"] == "International" and product_data["perish"]:
        score -= 15
    
    return max(0, min(100, score))

def seasonal_price_factor(date, product):
    product_data = PRODUCTS[product]
    if date.month in product_data["season_peak"]:
        return 0.85
    else:
        return 1.25

def calculate_delay(supplier, product, qty, date):
    product_data = PRODUCTS[product]
    
    # Start with supplier reliability
    if np.random.random() > supplier["reliability"]:
        delay = int(np.random.exponential(4))
    else:
        delay = 0
    
    # Regional penalty for local suppliers
    if supplier["type"] == "Local":
        delay += supplier.get("penalty", 1)
    else:
        # International shipping time
        delay += supplier.get("lead_time", 7)
    
    # Volume penalty
    if qty > 2000:
        delay += 3
    elif qty > 1000:
        delay += 2
    elif qty > 500:
        delay += 1
    
    # Product risk weight affects delay (higher risk = more delay when things go wrong)
    if delay > 0:
        delay = int(delay * (1 + product_data["risk_weight"] * 0.5))
    
    # Weekend effect
    if date.weekday() >= 5:
        delay += 1
    
    # Holiday season
    if date.month in [11, 12]:
        delay += 2
    
    return min(delay, 25)

def calculate_price(product, supplier, qty, date):
    product_data = PRODUCTS[product]
    base = product_data["base"]
    
    # Seasonal adjustment
    price = base * seasonal_price_factor(date, product)
    
    # Supplier premium
    if supplier["type"] == "International":
        price *= supplier.get("premium", 1.1)
    
    # Organic premium
    if supplier.get("organic", False):
        price *= 1.12
    
    # Volume discount
    if qty > 2000:
        price *= 0.85
    elif qty > 1000:
        price *= 0.90
    elif qty > 500:
        price *= 0.95
    
    # Volatility and spikes
    price *= np.random.normal(1, 0.08 * product_data["volatility"])
    
    # Price spike probability based on product risk
    if np.random.random() < (0.03 * product_data["risk_weight"]):
        price *= np.random.uniform(1.4, 2.2)
    
    return round(price, 2)

def calculate_quantity(product, date):
    product_data = PRODUCTS[product]
    base_qty = int(np.random.gamma(2, 150)) + 30
    
    if date.month in product_data["season_peak"]:
        base_qty = int(base_qty * random.uniform(1.2, 1.6))
    
    return min(base_qty, 3000)

# =========================
# MAIN GENERATION
# =========================
def main():
    print("=" * 80)
    print("🌟 MOON SHOT EDITION - SUPPLY CHAIN DATA GENERATOR")
    print("=" * 80)
    print(f"\n📊 Configuration:")
    print(f"   Orders: {N_ORDERS:,}")
    print(f"   Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"   Products: {len(PRODUCTS)}")
    print(f"   Suppliers: {len(SUPPLIER_POOL)}")
    print(f"   Local Suppliers: {len([s for s in SUPPLIER_POOL if s['type'] == 'Local'])}")
    print(f"   International Suppliers: {len([s for s in SUPPLIER_POOL if s['type'] == 'International'])}")
    print()
    
    # Generate dates
    all_dates = [START_DATE + timedelta(days=i) for i in range(DAYS_RANGE)]
    order_dates = np.random.choice(all_dates, N_ORDERS, replace=True)
    
    orders = []
    progress_step = max(1, N_ORDERS // 10)
    
    # Track supplier performance for accountability
    supplier_performance = {s["id"]: {"delivered": 0, "delayed": 0, "total_value": 0, "risk_scores": []} for s in SUPPLIER_POOL}
    
    for i in range(N_ORDERS):
        if i % progress_step == 0:
            print(f"   Generating: {i/N_ORDERS*100:.0f}% complete ({i:,}/{N_ORDERS:,} orders)")
        
        date = order_dates[i]
        product = random.choice(product_names)
        supplier = random.choice(SUPPLIER_POOL)
        product_data = PRODUCTS[product]
        
        qty = calculate_quantity(product, date)
        price = calculate_price(product, supplier, qty, date)
        delay = calculate_delay(supplier, product, qty, date)
        supplier_risk_score = calculate_supplier_risk_score(supplier, product, qty)
        
        promised = random.randint(2, 5)
        if supplier["type"] == "International":
            promised += supplier.get("lead_time", 7)
        actual = max(1, promised + delay)
        
        # Track supplier performance
        supplier_performance[supplier["id"]]["delivered"] += 1
        supplier_performance[supplier["id"]]["total_value"] += round(price * qty, 2)
        supplier_performance[supplier["id"]]["risk_scores"].append(supplier_risk_score)
        if delay > 0:
            supplier_performance[supplier["id"]]["delayed"] += 1
        
        orders.append({
            "order_id": f"ORD-{100000 + i}",
            "order_date": date,
            "product": product,
            "product_category": product_data["cat"],
            "perishable": product_data["perish"],
            "product_risk_weight": product_data["risk_weight"],
            "shelf_life_days": product_data["shelf_life"],
            "supplier": supplier["name"],
            "supplier_id": supplier["id"],
            "supplier_region": supplier["region"],
            "supplier_type": supplier["type"],
            "supplier_scale": supplier["scale"],
            "supplier_reliability": round(supplier["reliability"], 3),
            "supplier_risk_score": round(supplier_risk_score, 1),
            "quantity_kg": qty,
            "price_per_kg": price,
            "total_value_zar": round(price * qty, 2),
            "promised_days": promised,
            "actual_days": actual,
            "delay_days": delay,
        })
    
    print(f"   Generating: 100% complete")
    print()
    
    # Create DataFrame
    print("📊 Processing data...")
    df = pd.DataFrame(orders)
    
    # Calculate delivery dates
    df["expected_delivery_date"] = df["order_date"] + pd.to_timedelta(df["promised_days"], unit="D")
    df["actual_delivery_date"] = df["order_date"] + pd.to_timedelta(df["actual_days"], unit="D")
    df["on_time"] = (df["delay_days"] <= 0).astype(int)
    
    # Add derived columns
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["quarter"] = df["order_date"].dt.quarter
    df["weekday"] = df["order_date"].dt.dayofweek
    
    # Price spike detection
    df["price_zscore"] = df.groupby("product")["price_per_kg"].transform(lambda x: (x - x.mean()) / x.std())
    df["is_spike"] = df["price_zscore"] > 2
    
    # Sort by date
    df = df.sort_values("order_date").reset_index(drop=True)
    
    # Save main file
    output_file = "nile_supply_chain_moonshot.csv"
    df.to_csv(output_file, index=False)
    
    # Create supplier accountability report
    supplier_report = []
    for s_id, perf in supplier_performance.items():
        supplier = next((s for s in SUPPLIER_POOL if s["id"] == s_id), None)
        if supplier:
            delayed_rate = (perf["delayed"] / perf["delivered"] * 100) if perf["delivered"] > 0 else 0
            avg_risk_score = np.mean(perf["risk_scores"]) if perf["risk_scores"] else 0
            
            # Determine accountability grade
            if delayed_rate < 10 and avg_risk_score > 70:
                grade = "A (Excellent)"
            elif delayed_rate < 20 and avg_risk_score > 60:
                grade = "B (Good)"
            elif delayed_rate < 35 and avg_risk_score > 50:
                grade = "C (Average)"
            elif delayed_rate < 50:
                grade = "D (Poor)"
            else:
                grade = "F (Critical - Review Required)"
            
            supplier_report.append({
                "Supplier": supplier["name"],
                "Region": supplier["region"],
                "Type": supplier["type"],
                "Scale": supplier["scale"],
                "Total Orders": perf["delivered"],
                "Delayed Orders": perf["delayed"],
                "Delay Rate %": round(delayed_rate, 1),
                "Avg Risk Score": round(avg_risk_score, 1),
                "Accountability Grade": grade,
                "Total Value": perf["total_value"],
                "Recommendation": "Scale Up" if grade in ["A", "B"] else "Monitor" if grade == "C" else "Review Contract" if grade == "D" else "Terminate"
            })
    
    supplier_df = pd.DataFrame(supplier_report)
    supplier_df = supplier_df.sort_values("Delay Rate %", ascending=False)
    supplier_df.to_csv("supplier_accountability_report.csv", index=False)
    
    # Product risk analysis
    product_risk_df = df.groupby("product").agg({
        "delay_days": ["mean", "std", "max"],
        "product_risk_weight": "first",
        "price_per_kg": "std",
        "is_spike": "sum",
        "total_value_zar": "sum"
    }).round(2)
    product_risk_df.columns = ["avg_delay", "delay_std", "max_delay", "risk_weight", "price_volatility", "spike_count", "total_value"]
    product_risk_df["risk_score"] = (product_risk_df["avg_delay"] * 3 + 
                                      product_risk_df["delay_std"] * 2 + 
                                      product_risk_df["price_volatility"] * 10 +
                                      product_risk_df["spike_count"] * 5)
    product_risk_df = product_risk_df.sort_values("risk_score", ascending=False)
    product_risk_df.to_csv("product_risk_analysis.csv")
    
    # =========================
    # STATISTICS
    # =========================
    print("\n" + "=" * 80)
    print("✅ GENERATION COMPLETE! - MOON SHOT EDITION")
    print("=" * 80)
    
    print(f"\n📁 Main File: {output_file}")
    print(f"   Size: {len(df):,} rows, {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    print(f"\n📦 Product Statistics:")
    print(f"   Total products: {df['product'].nunique()}")
    print(f"   Categories: {df['product_category'].nunique()}")
    print(f"   Top 10 by revenue:")
    top_products = df.groupby('product')['total_value_zar'].sum().sort_values(ascending=False).head(10)
    for idx, (prod, revenue) in enumerate(top_products.items(), 1):
        print(f"      {idx}. {prod}: {format_currency(revenue)}")
    
    print(f"\n🏭 Supplier Statistics:")
    print(f"   Total suppliers: {df['supplier'].nunique()}")
    print(f"   Local suppliers: {df[df['supplier_type']=='Local']['supplier'].nunique()}")
    print(f"   International: {df[df['supplier_type']=='International']['supplier'].nunique()}")
    print(f"\n   Supplier Accountability Summary:")
    for grade in ["A (Excellent)", "B (Good)", "C (Average)", "D (Poor)", "F (Critical - Review Required)"]:
        count = len(supplier_df[supplier_df["Accountability Grade"] == grade])
        print(f"      {grade}: {count} suppliers")
    
    print(f"\n💰 Financial Statistics:")
    print(f"   Total revenue: R{df['total_value_zar'].sum():,.2f}")
    print(f"   Average order value: R{df['total_value_zar'].mean():,.2f}")
    print(f"   Average price/kg: R{df['price_per_kg'].mean():.2f}")
    
    print(f"\n📈 Performance Statistics:")
    print(f"   On-time delivery rate: {df['on_time'].mean()*100:.1f}%")
    print(f"   Average delay: {df['delay_days'].mean():.1f} days")
    print(f"   Orders with delay: {(df['delay_days']>0).sum():,} ({(df['delay_days']>0).mean()*100:.1f}%)")
    
    print(f"\n💥 Price Spike Statistics:")
    print(f"   Total spikes detected: {df['is_spike'].sum():,}")
    print(f"   Spike rate: {df['is_spike'].mean()*100:.2f}%")
    
    print(f"\n⚠️ Top 10 Highest Risk Products:")
    for idx, (product, row) in enumerate(product_risk_df.head(10).iterrows(), 1):
        risk_level = "🔴 EXTREME" if row['risk_score'] > 150 else "🔴 HIGH" if row['risk_score'] > 100 else "🟡 MEDIUM" if row['risk_score'] > 50 else "🟢 LOW"
        print(f"      {idx}. {product}: {risk_level} (Score: {row['risk_score']:.1f}) - Risk Weight: {row['risk_weight']:.2f}")
    
    print("\n" + "=" * 80)
    print("🎯 OUTPUT FILES GENERATED:")
    print("   1. nile_supply_chain_moonshot.csv - Full dataset (100,000 orders)")
    print("   2. supplier_accountability_report.csv - Supplier performance with grades")
    print("   3. product_risk_analysis.csv - Product risk scores")
    print("=" * 80)
    print("\n🎯 NEXT STEPS:")
    print("   1. Run: streamlit run app.py")
    print("   2. Upload 'nile_supply_chain_moonshot.csv' to the Control Tower")
    print("   3. Review supplier accountability report to identify underperformers")
    print("   4. Use product risk analysis for procurement strategy")
    print("=" * 80)
    
    # Create sample files
    for name, size in [("tiny", 100), ("small", 1000), ("medium", 5000)]:
        if size < len(df):
            df.head(size).to_csv(f"nile_sample_{name}.csv", index=False)
            print(f"\n💡 {name.capitalize()} sample: nile_sample_{name}.csv ({size:,} rows)")

if __name__ == "__main__":
    main()