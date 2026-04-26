
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import seaborn as sns
import matplotlib.gridspec as gridspec
import os
import pandas as pd

# Set style
plt.style.use('seaborn-v0-8-darkgrid')
sns.set_palette("husl")

# Create output directory
os.makedirs("images", exist_ok=True)

print("=" * 60)
print("Generating Nile.ag App-Aligned Images")
print("=" * 60)

# ============================================================================
# Helper function to create realistic delay data
# ============================================================================
def create_delay_data():
    regions = ['Western Cape', 'Gauteng', 'KZN', 'Eastern Cape', 'Limpopo', 'Mpumalanga']
    products = ['Tomatoes', 'Lettuce', 'Avocados', 'Potatoes', 'Apples', 'Herbs']
    data = np.array([
        [1.2, 2.1, 3.0, 2.5, 1.8, 4.2],  # Western Cape
        [2.5, 3.2, 4.1, 3.5, 2.8, 5.2],  # Gauteng
        [3.5, 4.2, 5.0, 4.2, 3.5, 6.0],  # KZN
        [4.2, 5.1, 6.0, 5.0, 4.2, 7.0],  # Eastern Cape
        [8.5, 9.0, 7.5, 8.0, 7.2, 10.0], # Limpopo
        [6.0, 7.0, 5.5, 7.5, 5.0, 8.0],  # Mpumalanga
    ])
    return regions, products, data

# ============================================================================
# IMAGE 1: App Overview / Dashboard Screenshot Mockup
# ============================================================================
print("Generating Image 1: App Dashboard Overview...")
fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')

# Main header
ax.add_patch(FancyBboxPatch((0.5, 6.5), 9, 1.2, boxstyle="round,pad=0.1",
                            facecolor='#0F2027', edgecolor='#2C5364', linewidth=2))
ax.text(5, 7.1, '🌱 Nile.ag - Operations Decision Engine', fontsize=18, fontweight='bold', 
        ha='center', color='white')
ax.text(5, 6.7, 'Predictive Analytics | Real-time Risk Assessment | Actionable Insights', 
        fontsize=11, ha='center', color='#a0c4c4')

# KPI Cards
kpi_positions = [(1, 5.5), (3.5, 5.5), (6, 5.5), (8.5, 5.5)]
kpi_labels = ['Total Orders', 'On-Time %', 'Financial Loss', 'High Risk']
kpi_values = ['124,567', '86.3%', 'R1.2M', '47']

for (x, y), label, value in zip(kpi_positions, kpi_labels, kpi_values):
    ax.add_patch(FancyBboxPatch((x-0.8, y-0.5), 1.6, 0.9, boxstyle="round,pad=0.05",
                                facecolor='#667eea', edgecolor='#764ba2', linewidth=1.5))
    ax.text(x, y+0.1, label, fontsize=10, ha='center', color='white', alpha=0.8)
    ax.text(x, y-0.2, value, fontsize=16, fontweight='bold', ha='center', color='white')

# Prediction Banner
ax.add_patch(FancyBboxPatch((0.5, 4.2), 9, 0.9, boxstyle="round,pad=0.1",
                            facecolor='#667eea20', edgecolor='#667eea', linewidth=2))
ax.text(5, 4.65, '🔮 PREDICTION: 47 orders may be delayed in the next 7 days', 
        fontsize=12, fontweight='bold', ha='center', color='#2c3e50')
ax.text(5, 4.35, '⚡ 23 high confidence predictions | 💡 Estimated loss: R342,000', 
        fontsize=10, ha='center', color='#555')

# Main tabs visualization
tabs = ['🚨 Priority', '🏭 Suppliers', '📦 Products', '🗺️ Regions', '📈 Trends']
tab_x = [1.2, 2.8, 4.4, 6.0, 7.6]
for i, (tab, x) in enumerate(zip(tabs, tab_x)):
    color = '#667eea' if i == 0 else '#ccc'
    ax.text(x, 3.5, tab, fontsize=11, fontweight='bold', ha='center', color=color)
    if i == 0:
        ax.plot([x-0.5, x+0.5], [3.4, 3.4], color='#667eea', linewidth=2)

# Priority list simulation
ax.text(1, 3.1, '🚨 TODAY\'S PRIORITY LIST', fontsize=11, fontweight='bold', color='#e74c3c')

priority_items = [
    ('ORD-100564', 'Organic Avocados', '25 days', 'R62,500'),
    ('ORD-187807', 'Organic Avocados', '25 days', 'R62,500'),
    ('ORD-112760', 'Passion Fruit', '25 days', 'R62,500'),
]
for i, (order, product, delay, loss) in enumerate(priority_items):
    y = 2.7 - i * 0.4
    ax.add_patch(FancyBboxPatch((1, y-0.15), 8, 0.35, boxstyle="round,pad=0.05",
                                facecolor='#f8d7da', edgecolor='#e74c3c', linewidth=1))
    ax.text(1.2, y, f'{order} | {product} | Delay: {delay} | Loss: {loss}', 
            fontsize=9, va='center', color='#333')

ax.text(9, 2.5, '...and 17 more', fontsize=9, ha='right', color='#666', style='italic')

# Footer
ax.text(5, 0.5, 'Nile.ag v3.0 | Powered by Machine Learning | Real-time Analytics', 
        fontsize=9, ha='center', color='#999')

plt.tight_layout()
plt.savefig('images/01_app_dashboard_overview.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/01_app_dashboard_overview.png")

# ============================================================================
# IMAGE 2: Delay Heatmap (Matches app's Operations tab)
# ============================================================================
print("Generating Image 2: Delay Heatmap...")
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
regions, products, delay_data = create_delay_data()

im = ax.imshow(delay_data, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=10)
ax.set_xticks(range(len(products)))
ax.set_yticks(range(len(regions)))
ax.set_xticklabels(products, rotation=45, ha='right', fontsize=11)
ax.set_yticklabels(regions, fontsize=11)
ax.set_xlabel('Product', fontsize=12, fontweight='bold')
ax.set_ylabel('Region', fontsize=12, fontweight='bold')
ax.set_title('Delay Heatmap by Region & Product (days)', fontsize=16, fontweight='bold', pad=20)

# Add text annotations
for i in range(len(regions)):
    for j in range(len(products)):
        color = "white" if delay_data[i, j] > 5 else "black"
        ax.text(j, i, f'{delay_data[i, j]:.1f}', ha="center", va="center", color=color, fontsize=10, fontweight='bold')

plt.colorbar(im, ax=ax, label='Average Delay (days)', fraction=0.046, pad=0.04)
plt.tight_layout()
plt.savefig('images/02_delay_heatmap.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/02_delay_heatmap.png")

# ============================================================================
# IMAGE 3: Price Spike Heatmap (Matches app's Price Spikes tab)
# ============================================================================
print("Generating Image 3: Price Spike Heatmap...")
fig, ax = plt.subplots(1, 1, figsize=(14, 8))

products_spike = ['Avocados', 'Herbs', 'Tomatoes', 'Peppers', 'Grapes', 'Lettuce', 'Strawberries']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

np.random.seed(42)
spike_data = np.random.beta(2, 5, size=(len(products_spike), len(months)))
spike_data[0, 1:4] = [0.85, 0.78, 0.82]  # Avocados spike in Feb-Apr
spike_data[1, 0:4] = [0.72, 0.68, 0.75, 0.70]  # Herbs spike early year
spike_data[2, 8:11] = [0.65, 0.72, 0.68]  # Tomatoes spike in Sep-Nov

im = ax.imshow(spike_data * 100, cmap='Reds', aspect='auto', vmin=0, vmax=100)
ax.set_xticks(range(len(months)))
ax.set_yticks(range(len(products_spike)))
ax.set_xticklabels(months, fontsize=10)
ax.set_yticklabels(products_spike, fontsize=11)
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Product', fontsize=12, fontweight='bold')
ax.set_title('Price Spike Probability by Product and Month (%)', fontsize=16, fontweight='bold', pad=20)

# Add text annotations
for i in range(len(products_spike)):
    for j in range(len(months)):
        val = spike_data[i, j] * 100
        if val > 10:
            ax.text(j, i, f'{val:.0f}%', ha="center", va="center", color="white" if val > 50 else "black", fontsize=8)

plt.colorbar(im, ax=ax, label='Spike Probability (%)', fraction=0.046, pad=0.04)
plt.tight_layout()
plt.savefig('images/03_price_spike_heatmap.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/03_price_spike_heatmap.png")

# ============================================================================
# IMAGE 4: Supplier Performance Dashboard
# ============================================================================
print("Generating Image 4: Supplier Performance...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Supplier accountability scores
suppliers = ['Cape Fresh', 'Stellenbosch', 'KZN Hub', 'Gauteng Hub', 'Limpopo Agro']
scores = [94, 87, 76, 82, 45]
grades = ['A+', 'A', 'B', 'B+', 'D']
colors = ['#27ae60', '#2ecc71', '#f39c12', '#f1c40f', '#e74c3c']

ax1 = axes[0]
bars = ax1.barh(suppliers, scores, color=colors, edgecolor='black', linewidth=1)
ax1.set_xlabel('Accountability Score', fontsize=12, fontweight='bold')
ax1.set_title('Supplier Accountability Ranking', fontsize=14, fontweight='bold')
ax1.set_xlim(0, 100)

for bar, score, grade in zip(bars, scores, grades):
    ax1.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, 
             f'{score} ({grade})', va='center', fontsize=11, fontweight='bold')

# Supplier performance over time
ax2 = axes[1]
months = np.arange(1, 13)
cape_fresh = [92, 93, 94, 94, 95, 94, 93, 94, 95, 96, 95, 94]
stellenbosch = [88, 87, 88, 87, 86, 85, 84, 83, 82, 81, 80, 79]
limpopo = [75, 74, 73, 72, 70, 68, 65, 62, 60, 58, 55, 52]

ax2.plot(months, cape_fresh, marker='o', linewidth=2, label='Cape Fresh', color='#27ae60')
ax2.plot(months, stellenbosch, marker='s', linewidth=2, label='Stellenbosch', color='#3498db')
ax2.plot(months, limpopo, marker='^', linewidth=2, label='Limpopo Agro', color='#e74c3c')
ax2.axhline(y=80, color='orange', linestyle='--', linewidth=2, label='Target (80%)')
ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax2.set_ylabel('On-Time Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Supplier Performance Trends', fontsize=14, fontweight='bold')
ax2.legend(loc='lower left')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(50, 100)

plt.tight_layout()
plt.savefig('images/04_supplier_performance.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/04_supplier_performance.png")

# ============================================================================
# IMAGE 5: Risk Distribution
# ============================================================================
print("Generating Image 5: Risk Distribution...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Pie chart
ax1 = axes[0]
risk_labels = ['HIGH RISK', 'MEDIUM RISK', 'LOW RISK']
risk_counts = [47, 156, 12364]
risk_colors = ['#e74c3c', '#f39c12', '#27ae60']
wedges, texts, autotexts = ax1.pie(risk_counts, labels=risk_labels, autopct='%1.1f%%',
                                    colors=risk_colors, explode=(0.05, 0, 0), startangle=90)
ax1.set_title('Order Risk Distribution', fontsize=14, fontweight='bold')

# Risk matrix
ax2 = axes[1]
risk_categories = ['Supplier', 'Price', 'Logistics', 'Quality']
high_risk = [85, 78, 72, 65]
medium_risk = [12, 15, 18, 20]
low_risk = [3, 7, 10, 15]

x = np.arange(len(risk_categories))
width = 0.25
ax2.bar(x - width, high_risk, width, label='HIGH', color='#e74c3c')
ax2.bar(x, medium_risk, width, label='MEDIUM', color='#f39c12')
ax2.bar(x + width, low_risk, width, label='LOW', color='#27ae60')
ax2.set_xlabel('Risk Category', fontsize=12, fontweight='bold')
ax2.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax2.set_title('Risk Breakdown by Category', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(risk_categories)
ax2.legend()

plt.tight_layout()
plt.savefig('images/05_risk_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/05_risk_distribution.png")

# ============================================================================
# IMAGE 6: Financial Impact Dashboard
# ============================================================================
print("Generating Image 6: Financial Impact...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Loss by supplier
ax1 = axes[0]
suppliers_loss = ['China Large\nImports', 'Limpopo Agro', 'KZN Hub', 'Eastern Cape\nCo-op', 'Mpumalanga\nFresh']
losses = [25657000, 12450000, 8750000, 6230000, 4120000]
colors_loss = ['#c0392b', '#e74c3c', '#e67e22', '#f39c12', '#f1c40f']
bars = ax1.barh(suppliers_loss, losses, color=colors_loss, edgecolor='black', linewidth=1)
ax1.set_xlabel('Financial Loss (R)', fontsize=12, fontweight='bold')
ax1.set_title('Top Loss-Making Suppliers', fontsize=14, fontweight='bold')

for bar, loss in zip(bars, losses):
    ax1.text(bar.get_width() + 200000, bar.get_y() + bar.get_height()/2, 
             f'R{loss/1000000:.1f}M', va='center', fontsize=10, fontweight='bold')

# Loss by region
ax2 = axes[1]
regions_loss = ['Limpopo', 'Mpumalanga', 'Eastern Cape', 'KZN', 'Gauteng', 'Western Cape']
losses_region = [1250000, 850000, 620000, 480000, 320000, 180000]
colors_region = ['#c0392b', '#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#2ecc71']
bars = ax2.bar(regions_loss, losses_region, color=colors_region, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Loss Amount (R)', fontsize=12, fontweight='bold')
ax2.set_title('Profit Leakage by Region', fontsize=14, fontweight='bold')
ax2.tick_params(axis='x', rotation=45)

for bar, loss in zip(bars, losses_region):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20000, 
             f'R{loss/1000:.0f}K', ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('images/06_financial_impact.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/06_financial_impact.png")

# ============================================================================
# IMAGE 7: ML Performance (Actual vs Predicted)
# ============================================================================
print("Generating Image 7: ML Performance...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Actual vs Predicted Scatter
ax1 = axes[0]
np.random.seed(42)
actual = np.random.exponential(3.5, 300)
predicted = actual + np.random.normal(0, 1.2, 300)
predicted = np.clip(predicted, 0, 18)
actual = np.clip(actual, 0, 18)

ax1.scatter(actual, predicted, alpha=0.5, c='#3498db', edgecolors='black', linewidth=0.5, s=50)
ax1.plot([0, 18], [0, 18], 'r--', linewidth=2, label='Perfect Prediction')
ax1.set_xlabel('Actual Delay (days)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Predicted Delay (days)', fontsize=12, fontweight='bold')
ax1.set_title('ML Model: Actual vs Predicted Delay', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Add metrics box
from sklearn.metrics import r2_score, mean_absolute_error
r2 = r2_score(actual, predicted)
mae = mean_absolute_error(actual, predicted)
ax1.text(0.05, 0.95, f'R² Score: {r2:.3f}\nMAE: {mae:.2f} days', 
         transform=ax1.transAxes, fontsize=12, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

# Feature Importance
ax2 = axes[1]
features = ['Quantity (kg)', 'Price (R/kg)', 'Perishable', 'Supplier\nReliability', 'Product\nCategory']
importance = [0.32, 0.28, 0.22, 0.12, 0.06]
colors_imp = plt.cm.Blues(np.linspace(0.4, 0.9, len(features)))
bars = ax2.barh(features, importance, color=colors_imp, edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Feature Importance', fontsize=12, fontweight='bold')
ax2.set_title('Model Feature Importance', fontsize=14, fontweight='bold')
for bar, imp in zip(bars, importance):
    ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
             f'{imp:.0%}', va='center', fontsize=11, fontweight='bold')
ax2.set_xlim(0, 0.4)

plt.tight_layout()
plt.savefig('images/07_ml_performance.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/07_ml_performance.png")

# ============================================================================
# IMAGE 8: Decision Engine - Priority Actions
# ============================================================================
print("Generating Image 8: Decision Engine...")
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')

# Title
ax.text(5, 7.5, '🎯 DECISION ENGINE - ACTIONABLE INSIGHTS', fontsize=16, fontweight='bold', 
        ha='center', color='#2c3e50')
ax.text(5, 7.1, 'What YOU need to do RIGHT NOW', fontsize=12, ha='center', color='#666')

# Decision cards
decisions = [
    ('🔴 URGENT', 'Expedite shipment OR switch supplier for Order ORD-100564', 
     '25 days delayed, value R62,500', 'Operations Manager', 'Immediate'),
    ('🔴 URGENT', 'Expedite shipment OR switch supplier for Order ORD-187807', 
     '25 days delayed, value R62,500', 'Operations Manager', 'Immediate'),
    ('🟡 MEDIUM', 'Schedule performance review with Limpopo Agro Farms', 
     'On-time rate: 45%, Trend: DECLINING', 'Procurement Team', 'This week'),
    ('🟡 MEDIUM', 'Buy Avocados NOW before prices increase further', 
     'Price spike detected (Z-score: 2.8)', 'Procurement Team', '48 hours'),
]

colors = ['#e74c3c', '#e74c3c', '#f39c12', '#f39c12']
bg_colors = ['#f8d7da', '#f8d7da', '#fff3cd', '#fff3cd']

for i, (priority, action, reason, owner, deadline) in enumerate(decisions):
    y = 6.2 - i * 1.2
    ax.add_patch(FancyBboxPatch((1, y-0.6), 8, 1.0, boxstyle="round,pad=0.1",
                                facecolor=bg_colors[i], edgecolor=colors[i], linewidth=2))
    ax.text(1.2, y+0.2, priority, fontsize=12, fontweight='bold', color=colors[i])
    ax.text(1.2, y-0.1, f'Action: {action}', fontsize=11, color='#333')
    ax.text(1.2, y-0.4, f'Why: {reason}', fontsize=10, color='#555')
    ax.text(7.5, y+0.2, f'Owner: {owner}', fontsize=10, color='#555', ha='right')
    ax.text(7.5, y-0.1, f'Deadline: {deadline}', fontsize=10, fontweight='bold', color=colors[i], ha='right')

# Simulation box
ax.add_patch(FancyBboxPatch((1, 0.8), 8, 0.8, boxstyle="round,pad=0.1",
                            facecolor='#e8f4f8', edgecolor='#3498db', linewidth=2))
ax.text(5, 1.3, '🔮 What-If Simulation: Current Loss R1,245,000 → After Action R892,000', 
        fontsize=12, fontweight='bold', ha='center', color='#2c3e50')
ax.text(5, 1.05, '💰 Potential Savings: R353,000 (28% improvement)', 
        fontsize=11, ha='center', color='#27ae60', fontweight='bold')

# Footer
ax.text(5, 0.3, 'Nile.ag Decision Engine | Real-time | Actionable | Production-Ready', 
        fontsize=9, ha='center', color='#999')

plt.tight_layout()
plt.savefig('images/08_decision_engine.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/08_decision_engine.png")

print("=" * 60)
print("✅ All 8 app-aligned images generated successfully!")
print("📁 Images saved to 'images/' directory")
print("=" * 60)

# Verify all images were created
print("\n📋 Generated Images:")
image_files = [
    "01_app_dashboard_overview.png",
    "02_delay_heatmap.png", 
    "03_price_spike_heatmap.png",
    "04_supplier_performance.png",
    "05_risk_distribution.png",
    "06_financial_impact.png",
    "07_ml_performance.png",
    "08_decision_engine.png"
]

for img in image_files:
    if os.path.exists(f"images/{img}"):
        size = os.path.getsize(f"images/{img}") / 1024
        print(f"  ✓ {img} ({size:.1f} KB)")
    else:
        print(f"  ✗ {img} - Not found")

print("\n🎉 All images ready")
