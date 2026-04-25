import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# Config
N_ORDERS = 120000
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2024, 6, 30)
DAYS_RANGE = (END_DATE - START_DATE).days

# 20 products with realistic attributes
PRODUCTS = {
    "Tomatoes":     {"cat": "Veg",  "perish": True,  "base": 12.5, "weight": 0.5, "season_peak": [1, 2, 3]},
    "Lettuce":      {"cat": "Veg",  "perish": True,  "base": 10.0, "weight": 0.3, "season_peak": [1, 2, 11, 12]},
    "Spinach":      {"cat": "Veg",  "perish": True,  "base": 15.0, "weight": 0.3, "season_peak": [4, 5, 6]},
    "Avocados":     {"cat": "Fruit","perish": True,  "base": 35.0, "weight": 0.9, "season_peak": [2, 3, 4]},
    "Mangoes":      {"cat": "Fruit","perish": False, "base": 22.0, "weight": 0.8, "season_peak": [11, 12, 1]},
    "Bananas":      {"cat": "Fruit","perish": True,  "base": 10.0, "weight": 0.6, "season_peak": [1, 2, 3, 4, 5]},
    "Oranges":      {"cat": "Fruit","perish": False, "base": 18.0, "weight": 0.7, "season_peak": [6, 7, 8]},
    "Apples":       {"cat": "Fruit","perish": False, "base": 20.0, "weight": 0.75,"season_peak": [3, 4, 5]},
    "Onions":       {"cat": "Root", "perish": False, "base": 8.0,  "weight": 1.2, "season_peak": [8, 9, 10]},
    "Potatoes":     {"cat": "Root", "perish": False, "base": 7.0,  "weight": 1.5, "season_peak": [5, 6, 7]},
    "Carrots":      {"cat": "Root", "perish": False, "base": 9.0,  "weight": 0.7, "season_peak": [6, 7, 8]},
    "Beetroot":     {"cat": "Root", "perish": False, "base": 11.0, "weight": 0.9, "season_peak": [5, 6, 7]},
    "Peppers":      {"cat": "Veg",  "perish": True,  "base": 18.0, "weight": 0.4, "season_peak": [8, 9, 10]},
    "Cucumbers":    {"cat": "Veg",  "perish": True,  "base": 14.0, "weight": 0.4, "season_peak": [10, 11, 12]},
    "Broccoli":     {"cat": "Veg",  "perish": True,  "base": 16.0, "weight": 0.5, "season_peak": [4, 5, 6]},
    "Cauliflower":  {"cat": "Veg",  "perish": True,  "base": 15.0, "weight": 0.6, "season_peak": [7, 8, 9]},
    "Pineapples":   {"cat": "Fruit","perish": False, "base": 28.0, "weight": 1.2, "season_peak": [1, 2, 12]},
    "Papayas":      {"cat": "Fruit","perish": True,  "base": 30.0, "weight": 0.9, "season_peak": [9, 10, 11]},
    "Herbs":        {"cat": "Herb", "perish": True,  "base": 40.0, "weight": 0.2, "season_peak": [1, 2, 3, 4]},
    "Ginger":       {"cat": "Root", "perish": False, "base": 45.0, "weight": 0.6, "season_peak": [11, 12, 1]},
}
product_names = list(PRODUCTS.keys())

regions = ["Western Cape", "Eastern Cape", "KwaZulu-Natal", "Limpopo", "Mpumalanga", "Gauteng"]
supplier_names = [f"Supplier_{chr(65+i)}" for i in range(15)]  # A to O

suppliers = []
for i, name in enumerate(supplier_names):
    region = random.choice(regions)
    reliability_base = np.random.beta(7, 3)
    expertise_cats = random.sample(list(set(p["cat"] for p in PRODUCTS.values())), k=random.randint(1, 2))
    suppliers.append({
        "name": name,
        "region": region,
        "reliability_base": reliability_base,
        "expertise_cats": expertise_cats,
        "organic": random.random() < 0.3,
    })


def seasonal_price_factor(date, product):
    month = date.month
    peak_months = PRODUCTS[product]["season_peak"]
    return 0.85 if month in peak_months else 1.20


def calculate_delay(supplier, product, qty, date):
    s = supplier
    p = PRODUCTS[product]
    year_effect = max(0, (date.year - 2022) * 0.05)
    reliability = max(0.5, min(0.98, s["reliability_base"] - year_effect))

    if np.random.random() > reliability:
        delay = int(np.random.exponential(scale=5))
    else:
        delay = 0

    region_delay = {
        "Western Cape": 2, "Eastern Cape": 2, "KwaZulu-Natal": 1,
        "Limpopo": 3, "Mpumalanga": 2, "Gauteng": 1
    }.get(s["region"], 1)
    delay += region_delay
    delay += int(qty / 400)

    if date.weekday() >= 5:
        delay += 1

    if p["perish"] and delay > 0:
        delay += int(delay * 0.6)

    delay += int(p["weight"])

    if p["cat"] in s["expertise_cats"]:
        delay -= 1

    if np.random.random() < 0.06:
        delay -= np.random.randint(1, 4)

    if (date.month == 12 and date.day >= 15) or (date.month == 1 and date.day <= 10):
        delay += 3

    return max(-2, min(21, delay))


dates = [START_DATE + timedelta(days=i) for i in range(DAYS_RANGE)]
order_dates = np.random.choice(dates, N_ORDERS)

orders = []
for i in range(N_ORDERS):
    date = order_dates[i]
    product = random.choice(product_names)
    supplier = random.choice(suppliers)
    qty = int(np.random.gamma(2, 150)) + 10
    qty = min(qty, 3000)

    base = PRODUCTS[product]["base"]
    seasonal = seasonal_price_factor(date, product)
    markup = 1.05 if supplier["organic"] else 0.98
    discount = min(qty / 2500, 0.18)
    noise = np.random.normal(1, 0.07)
    spike = np.random.uniform(1.4, 2.2) if np.random.random() < 0.06 else 1.0
    price = base * seasonal * markup * (1 - discount) * noise * spike
    price = round(price, 2)

    delay = calculate_delay(supplier, product, qty, date)
    promised = np.random.randint(2, 7)
    actual = max(promised + delay, 1)
    total = round(price * qty, 2)

    orders.append({
        "order_id": f"ORD-{10000+i}",
        "order_date": date,
        "product": product,
        "product_category": PRODUCTS[product]["cat"],
        "perishable": PRODUCTS[product]["perish"],
        "supplier": supplier["name"],
        "supplier_region": supplier["region"],
        "quantity_kg": qty,
        "price_per_kg": price,
        "total_value_zar": total,
        "promised_days": promised,
        "actual_days": actual,
        "delay_days": delay,
    })

df = pd.DataFrame(orders)
df["expected_delivery_date"] = df["order_date"] + pd.to_timedelta(df["promised_days"], unit="D")
df["actual_delivery_date"] = df["order_date"] + pd.to_timedelta(df["actual_days"], unit="D")
df["on_time"] = (df["delay_days"] <= 0).astype(int)

df.to_csv("nile_supply_chain.csv", index=False)
print(f"✅ Generated {len(df):,} orders | Date range: {df['order_date'].min().date()} to {df['order_date'].max().date()}")
print(f"   Products: {df['product'].nunique()} | Suppliers: {df['supplier'].nunique()}")