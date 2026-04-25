# generate_images.py
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import seaborn as sns
import matplotlib.gridspec as gridspec
import os

# Set style - use available matplotlib styles instead of seaborn
try:
    # Try to use seaborn style if available
    import seaborn as sns
    sns.set_style("darkgrid")
    sns.set_palette("husl")
except:
    # Fall back to matplotlib default styles
    plt.style.use('default')
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3

# Create output directory
os.makedirs("images", exist_ok=True)

print("=" * 60)
print("Generating Nile.ag Control Tower Images")
print("=" * 60)

# ============================================================================
# IMAGE 1: System Architecture Diagram
# ============================================================================
print("Generating Image 1: System Architecture...")
fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')

# Title
ax.text(5, 7.5, 'Nile.ag Supply Chain Intelligence Platform', 
        fontsize=20, fontweight='bold', ha='center', color='#2c3e50')

# Data Layer
data_rect = FancyBboxPatch((0.5, 5.5), 9, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#e8f4f8', edgecolor='#2980b9', linewidth=2)
ax.add_patch(data_rect)
ax.text(5, 6.5, 'DATA LAYER', fontsize=14, fontweight='bold', ha='center', color='#2980b9')
ax.text(5, 5.9, 'Orders | Suppliers | Products | Pricing | Delivery Records', 
        fontsize=11, ha='center', color='#34495e')

# Intelligence Layer
intel_rect = FancyBboxPatch((0.5, 3.5), 9, 1.8, boxstyle="round,pad=0.1",
                             facecolor='#fef9e7', edgecolor='#f39c12', linewidth=2)
ax.add_patch(intel_rect)
ax.text(5, 4.7, 'INTELLIGENCE ENGINE', fontsize=14, fontweight='bold', ha='center', color='#e67e22')
ax.text(5, 4.2, 'ML Predictions | Risk Scoring | Trend Analysis | Anomaly Detection', 
        fontsize=11, ha='center', color='#34495e')
ax.text(5, 3.8, 'Supplier Intelligence | Price Optimization | Logistics Analytics', 
        fontsize=11, ha='center', color='#34495e')

# Decision Layer
decision_rect = FancyBboxPatch((0.5, 1.2), 9, 1.8, boxstyle="round,pad=0.1",
                                facecolor='#e8f8f5', edgecolor='#27ae60', linewidth=2)
ax.add_patch(decision_rect)
ax.text(5, 2.4, 'DECISION ENGINE', fontsize=14, fontweight='bold', ha='center', color='#27ae60')
ax.text(5, 1.9, 'Smart Routing | Procurement Timing | Supplier Selection | Scenario Simulation', 
        fontsize=11, ha='center', color='#34495e')
ax.text(5, 1.5, 'Profit Protection | Risk Mitigation | Cost Optimization', 
        fontsize=11, ha='center', color='#34495e')

# Arrows
arrow1 = FancyArrowPatch((5, 5.5), (5, 5.3), arrowstyle='->', mutation_scale=20, linewidth=2, color='#2980b9')
arrow2 = FancyArrowPatch((5, 3.5), (5, 3.3), arrowstyle='->', mutation_scale=20, linewidth=2, color='#f39c12')
ax.add_patch(arrow1)
ax.add_patch(arrow2)

plt.tight_layout()
plt.savefig('images/01_system_architecture.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/01_system_architecture.png")

# ============================================================================
# IMAGE 2: Risk Assessment Dashboard
# ============================================================================
print("Generating Image 2: Risk Assessment...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Risk Assessment Dashboard', fontsize=18, fontweight='bold', y=0.98)

# Subplot 1: Risk Levels Distribution
ax1 = axes[0, 0]
risk_levels = ['HIGH', 'MEDIUM', 'LOW']
risk_counts = [15, 35, 50]
colors = ['#e74c3c', '#f39c12', '#27ae60']
bars = ax1.bar(risk_levels, risk_counts, color=colors, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Percentage (%)', fontsize=12)
ax1.set_title('Order Risk Distribution', fontsize=14, fontweight='bold')
for bar, count in zip(bars, risk_counts):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{count}%', ha='center', fontsize=11, fontweight='bold')

# Subplot 2: Supplier Risk Score
ax2 = axes[0, 1]
suppliers = ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E']
risk_scores = [85, 72, 68, 45, 32]
colors2 = ['#e74c3c' if x > 70 else '#f39c12' if x > 50 else '#27ae60' for x in risk_scores]
bars2 = ax2.barh(suppliers, risk_scores, color=colors2, edgecolor='black', linewidth=1)
ax2.set_xlabel('Risk Score', fontsize=12)
ax2.set_title('Supplier Risk Ranking', fontsize=14, fontweight='bold')
ax2.axvline(x=70, color='red', linestyle='--', linewidth=2, label='Critical')
ax2.axvline(x=50, color='orange', linestyle='--', linewidth=2, label='Warning')
ax2.legend()

# Subplot 3: Product Risk Heatmap
ax3 = axes[1, 0]
products = ['Tomatoes', 'Lettuce', 'Avocados', 'Berries', 'Herbs']
metrics = ['Delay Risk', 'Price Risk', 'Quality Risk', 'Supply Risk']
np.random.seed(42)
data = np.random.rand(len(products), len(metrics)) * 100
im = ax3.imshow(data, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
ax3.set_xticks(range(len(metrics)))
ax3.set_yticks(range(len(products)))
ax3.set_xticklabels(metrics, fontsize=10, rotation=45, ha='right')
ax3.set_yticklabels(products, fontsize=10)
ax3.set_title('Product Risk Matrix', fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax3, label='Risk Score')

# Subplot 4: Risk Trend
ax4 = axes[1, 1]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
high_risk = [12, 15, 18, 14, 10, 8]
medium_risk = [25, 28, 30, 26, 22, 20]
low_risk = [63, 57, 52, 60, 68, 72]

ax4.stackplot(months, high_risk, medium_risk, low_risk, 
              labels=['HIGH', 'MEDIUM', 'LOW'],
              colors=['#e74c3c', '#f39c12', '#27ae60'], alpha=0.8)
ax4.set_xlabel('Month', fontsize=12)
ax4.set_ylabel('Percentage (%)', fontsize=12)
ax4.set_title('Risk Trend Analysis', fontsize=14, fontweight='bold')
ax4.legend(loc='upper right')
ax4.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('images/02_risk_assessment.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/02_risk_assessment.png")

# ============================================================================
# IMAGE 3: Supplier Performance Dashboard
# ============================================================================
print("Generating Image 3: Supplier Performance...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Supplier Performance Dashboard', fontsize=18, fontweight='bold', y=0.98)

# Subplot 1: On-Time Delivery
ax1 = axes[0, 0]
suppliers = ['Cape Fresh', 'Stellenbosch', 'Limpopo', 'KZN Hub', 'Gauteng']
otd_rates = [94, 88, 76, 82, 91]
colors_otd = ['green' if x >= 90 else 'orange' if x >= 80 else 'red' for x in otd_rates]
bars = ax1.bar(suppliers, otd_rates, color=colors_otd, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('On-Time Delivery (%)', fontsize=12)
ax1.set_title('Supplier Reliability Score', fontsize=14, fontweight='bold')
ax1.axhline(y=90, color='green', linestyle='--', linewidth=2, label='Target (90%)')
ax1.axhline(y=80, color='orange', linestyle='--', linewidth=2, label='Minimum (80%)')
ax1.legend()
for bar, rate in zip(bars, otd_rates):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{rate}%', ha='center', fontsize=10, fontweight='bold')

# Subplot 2: Trend Analysis
ax2 = axes[0, 1]
months = np.arange(1, 13)
np.random.seed(42)
supplier_declining = 88 - np.cumsum(np.random.randn(12) * 1.5)
supplier_stable = 85 + np.cumsum(np.random.randn(12) * 0.5)
supplier_improving = 78 + np.cumsum(np.random.randn(12) * 2)

# Ensure values stay within 0-100
supplier_declining = np.clip(supplier_declining, 60, 95)
supplier_stable = np.clip(supplier_stable, 75, 95)
supplier_improving = np.clip(supplier_improving, 70, 98)

ax2.plot(months, supplier_declining, marker='o', linewidth=2, label='Declining Supplier', color='red')
ax2.plot(months, supplier_stable, marker='s', linewidth=2, label='Stable Supplier', color='blue')
ax2.plot(months, supplier_improving, marker='^', linewidth=2, label='Improving Supplier', color='green')
ax2.set_xlabel('Month', fontsize=12)
ax2.set_ylabel('On-Time Rate (%)', fontsize=12)
ax2.set_title('Supplier Trend Analysis', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(60, 100)

# Subplot 3: Supplier Scorecard
ax3 = axes[1, 0]
categories = ['Quality', 'Delivery', 'Price', 'Service']
supplier1_scores = [92, 94, 85, 90]
supplier2_scores = [85, 88, 90, 82]
supplier3_scores = [78, 76, 88, 75]

x = np.arange(len(categories))
width = 0.25
ax3.bar(x - width, supplier1_scores, width, label='Cape Fresh', color='#3498db')
ax3.bar(x, supplier2_scores, width, label='Stellenbosch', color='#2ecc71')
ax3.bar(x + width, supplier3_scores, width, label='Limpopo', color='#e74c3c')
ax3.set_ylabel('Score (0-100)', fontsize=12)
ax3.set_title('Supplier Scorecard Comparison', fontsize=14, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(categories)
ax3.legend()
ax3.set_ylim(0, 100)

# Subplot 4: Value Contribution
ax4 = axes[1, 1]
values = [28, 22, 18, 17, 15]
supplier_labels = ['Cape Fresh', 'Stellenbosch', 'Limpopo', 'KZN Hub', 'Gauteng']
explode = (0.05, 0, 0, 0, 0)
wedges, texts, autotexts = ax4.pie(values, explode=explode, labels=supplier_labels, autopct='%1.0f%%',
                                    colors=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'])
ax4.set_title('Supplier Value Contribution', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('images/03_supplier_performance.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/03_supplier_performance.png")

# ============================================================================
# IMAGE 4: Logistics Operations Heatmap
# ============================================================================
print("Generating Image 4: Logistics Operations...")
fig, axes = plt.subplots(1, 2, figsize=(15, 7))
fig.suptitle('Logistics & Operations Analytics', fontsize=18, fontweight='bold', y=0.98)

# Subplot 1: Delay Heatmap
ax1 = axes[0]
regions = ['Western Cape', 'Gauteng', 'KZN', 'Eastern Cape', 'Limpopo', 'Mpumalanga']
products = ['Tomatoes', 'Lettuce', 'Avocados', 'Potatoes', 'Apples', 'Herbs']
np.random.seed(42)
delay_data = np.random.uniform(0, 10, (len(regions), len(products)))
delay_data[0, :] = [1, 2, 3, 2, 1, 4]  # Western Cape - good
delay_data[4, :] = [8, 9, 7, 6, 8, 10]  # Limpopo - bad
delay_data[5, :] = [7, 6, 5, 8, 4, 6]   # Mpumalanga - medium

im = ax1.imshow(delay_data, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=10)
ax1.set_xticks(range(len(products)))
ax1.set_yticks(range(len(regions)))
ax1.set_xticklabels(products, rotation=45, ha='right', fontsize=10)
ax1.set_yticklabels(regions, fontsize=10)
ax1.set_xlabel('Product', fontsize=12)
ax1.set_ylabel('Region', fontsize=12)
ax1.set_title('Average Delay Heatmap (days)', fontsize=14, fontweight='bold')

# Add text annotations
for i in range(len(regions)):
    for j in range(len(products)):
        color = "white" if delay_data[i, j] > 5 else "black"
        ax1.text(j, i, f'{delay_data[i, j]:.1f}', ha="center", va="center", color=color, fontsize=9)

plt.colorbar(im, ax=ax1, label='Delay (days)')

# Subplot 2: Hotspots
ax2 = axes[1]
hotspots = ['Limpopo - Avocados', 'Mpumalanga - Tomatoes', 'Eastern Cape - Herbs', 
            'KZN - Lettuce', 'Limpopo - Potatoes']
severity = [9.2, 8.5, 7.8, 7.2, 6.9]
colors_sev = ['darkred', 'red', 'orange', 'orange', 'orange']
bars = ax2.barh(hotspots, severity, color=colors_sev, edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Severity Score (0-10)', fontsize=12)
ax2.set_title('Critical Logistics Hotspots', fontsize=14, fontweight='bold')
for bar, sev in zip(bars, severity):
    ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
             f'{sev}/10', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('images/04_logistics_operations.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/04_logistics_operations.png")

# ============================================================================
# IMAGE 5: Price Intelligence Dashboard
# ============================================================================
print("Generating Image 5: Price Intelligence...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Price Intelligence & Market Analytics', fontsize=18, fontweight='bold', y=0.98)

# Subplot 1: Price Volatility
ax1 = axes[0, 0]
products_vol = ['Tomatoes', 'Herbs', 'Avocados', 'Peppers', 'Grapes', 'Lettuce']
volatility = [24, 22, 19, 17, 15, 13]
colors_vol = plt.cm.RdYlGn_r(np.array(volatility) / max(volatility))
bars = ax1.barh(products_vol, volatility, color=colors_vol, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Volatility Index (%)', fontsize=12)
ax1.set_title('Product Price Volatility', fontsize=14, fontweight='bold')
for bar, vol in zip(bars, volatility):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
             f'{vol}%', va='center', fontsize=11, fontweight='bold')

# Subplot 2: Seasonal Patterns
ax2 = axes[0, 1]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
tomatoes = [12, 11, 10, 13, 16, 18, 20, 19, 17, 15, 13, 12]
avocados = [35, 32, 30, 28, 32, 38, 42, 45, 43, 40, 37, 36]
herbs = [42, 40, 38, 35, 38, 42, 45, 44, 42, 40, 41, 43]

ax2.plot(months, tomatoes, marker='o', linewidth=2, label='Tomatoes', color='red')
ax2.plot(months, avocados, marker='s', linewidth=2, label='Avocados', color='green')
ax2.plot(months, herbs, marker='^', linewidth=2, label='Herbs', color='blue')
ax2.set_xlabel('Month', fontsize=12)
ax2.set_ylabel('Price (R/kg)', fontsize=12)
ax2.set_title('Seasonal Price Patterns', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xticks(range(len(months)))
ax2.set_xticklabels(months, rotation=45)

# Subplot 3: Spike Calendar
ax3 = axes[1, 0]
spike_data = np.random.uniform(0, 1, (12, 7))
for i in range(12):
    for j in range(7):
        if np.random.random() > 0.7:
            spike_data[i, j] = np.random.uniform(0.5, 1)
        else:
            spike_data[i, j] = np.random.uniform(0, 0.3)

im = ax3.imshow(spike_data, cmap='Reds', aspect='auto', vmin=0, vmax=1)
ax3.set_xticks(range(7))
ax3.set_yticks(range(12))
ax3.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], fontsize=9)
ax3.set_yticklabels(months, fontsize=9)
ax3.set_title('Price Spike Probability Calendar', fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax3, label='Spike Probability')

# Subplot 4: Procurement Strategy
ax4 = axes[1, 1]
products_proc = ['Avocados', 'Herbs', 'Tomatoes', 'Peppers', 'Grapes']
savings = [45, 35, 28, 22, 18]
colors_sav = ['green', 'lightgreen', 'orange', 'orange', 'red']
bars = ax4.bar(products_proc, savings, color=colors_sav, edgecolor='black', linewidth=1.5)
ax4.set_ylabel('Potential Savings (%)', fontsize=12)
ax4.set_title('Procurement Optimization', fontsize=14, fontweight='bold')
for bar, save in zip(bars, savings):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{save}%', ha='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('images/05_price_intelligence.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/05_price_intelligence.png")

# ============================================================================
# IMAGE 6: Financial Impact Dashboard
# ============================================================================
print("Generating Image 6: Financial Impact...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Financial Impact & Profit Protection', fontsize=18, fontweight='bold', y=0.98)

# Subplot 1: Loss by Region
ax1 = axes[0, 0]
regions_loss = ['Limpopo', 'Mpumalanga', 'Eastern Cape', 'KZN', 'Gauteng', 'Western Cape']
loss_amounts = [1250000, 850000, 620000, 480000, 320000, 180000]
colors_loss = ['darkred', 'red', 'orange', 'orange', 'green', 'lightgreen']
bars = ax1.bar(regions_loss, loss_amounts, color=colors_loss, edgecolor='black', linewidth=1.5)
ax1.set_ylabel('Loss Amount (ZAR)', fontsize=12)
ax1.set_title('Profit Leakage by Region', fontsize=14, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)
for bar, loss in zip(bars, loss_amounts):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20000, 
             f'R{loss/1000:.0f}K', ha='center', fontsize=10, fontweight='bold')

# Subplot 2: Loss Categories
ax2 = axes[0, 1]
categories = ['Supplier Delays', 'Perishable Waste', 'Logistics', 'Quality', 'Price Volatility']
loss_percent = [45, 25, 15, 10, 5]
colors_cat = ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#2ecc71']
wedges, texts, autotexts = ax2.pie(loss_percent, labels=categories, autopct='%1.0f%%',
                                    colors=colors_cat, explode=(0.05, 0, 0, 0, 0))
ax2.set_title('Loss Distribution by Cause', fontsize=14, fontweight='bold')

# Subplot 3: Scenario Simulation
ax3 = axes[1, 0]
scenarios = ['Base', '+10% Price', '+20% Price', '+5 Days', '+10 Days']
impacts = [4.5, 7.2, 9.8, 11.5, 18.2]
colors_imp = ['blue', 'orange', 'orange', 'red', 'darkred']
bars = ax3.bar(scenarios, impacts, color=colors_imp, edgecolor='black', linewidth=1.5)
ax3.set_ylabel('Revenue Impact (%)', fontsize=12)
ax3.set_title('Scenario Simulation Results', fontsize=14, fontweight='bold')
ax3.axhline(y=10, color='red', linestyle='--', linewidth=2, label='Warning Threshold (10%)')
ax3.legend()
for bar, impact in zip(bars, impacts):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
             f'{impact}%', ha='center', fontsize=11, fontweight='bold')

# Subplot 4: ROI Analysis
ax4 = axes[1, 1]
interventions = ['Supplier Switch', 'Route Optimization', 'Inventory Buffer', 'Price Hedging', 'Quality Control']
roi = [245, 189, 156, 98, 76]
colors_roi = ['green', 'lightgreen', 'orange', 'orange', 'red']
bars = ax4.barh(interventions, roi, color=colors_roi, edgecolor='black', linewidth=1.5)
ax4.set_xlabel('ROI (%)', fontsize=12)
ax4.set_title('Intervention ROI Analysis', fontsize=14, fontweight='bold')
for bar, r in zip(bars, roi):
    ax4.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, 
             f'{r}%', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('images/06_financial_impact.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/06_financial_impact.png")

# ============================================================================
# IMAGE 7: ML Performance
# ============================================================================
print("Generating Image 7: ML Performance...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Machine Learning Model Performance', fontsize=18, fontweight='bold', y=0.98)

# Subplot 1: Actual vs Predicted
ax1 = axes[0]
np.random.seed(42)
actual = np.random.exponential(4, 200)
predicted = actual + np.random.normal(0, 1, 200)
predicted = np.clip(predicted, 0, 20)
actual = np.clip(actual, 0, 20)

ax1.scatter(actual, predicted, alpha=0.6, c='blue', edgecolors='black', linewidth=0.5)
ax1.plot([0, 20], [0, 20], 'r--', linewidth=2, label='Perfect Prediction')
ax1.set_xlabel('Actual Delay (days)', fontsize=12)
ax1.set_ylabel('Predicted Delay (days)', fontsize=12)
ax1.set_title('Actual vs Predicted Delay', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Calculate and display metrics
from sklearn.metrics import r2_score, mean_absolute_error
r2 = r2_score(actual, predicted)
mae = mean_absolute_error(actual, predicted)
ax1.text(0.05, 0.95, f'R2 Score: {r2:.3f}\nMAE: {mae:.2f} days', 
         transform=ax1.transAxes, fontsize=12, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Subplot 2: Feature Importance
ax2 = axes[1]
features = ['Quantity (kg)', 'Price (R/kg)', 'Perishable', 'Supplier Region', 'Product Category', 'Season']
importance = [0.35, 0.25, 0.22, 0.10, 0.05, 0.03]
colors_imp = plt.cm.Blues(np.linspace(0.4, 0.9, len(features)))
bars = ax2.barh(features, importance, color=colors_imp, edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Feature Importance', fontsize=12)
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
# IMAGE 8: Executive Dashboard
# ============================================================================
print("Generating Image 8: Executive Dashboard...")
fig = plt.figure(figsize=(16, 10))
fig.suptitle('Executive Control Tower Dashboard', fontsize=20, fontweight='bold', y=0.98)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

# KPI Cards
ax1 = fig.add_subplot(gs[0, 0])
ax1.axis('off')
kpi_data = [('Total Orders', '18,247', '+12%'), ('On-Time Rate', '86.3%', '-2.1%'),
            ('Avg Delay', '3.2d', '+0.8d'), ('Health Score', '72.5', '-5.2')]
y_pos = 0.8
for title, value, delta in kpi_data:
    ax1.text(0.1, y_pos, title, fontsize=12, fontweight='bold', va='center')
    ax1.text(0.6, y_pos, value, fontsize=14, fontweight='bold', va='center', color='#2c3e50')
    color = '#e74c3c' if '-' in delta else '#27ae60'
    ax1.text(0.85, y_pos, delta, fontsize=11, va='center', color=color)
    y_pos -= 0.2
ax1.set_title('Key Performance Indicators', fontsize=14, fontweight='bold', y=0.98)

# Health Gauge
ax2 = fig.add_subplot(gs[0, 1])
health_score = 72
gauge_data = [health_score, 100-health_score]
wedges, texts = ax2.pie(gauge_data, startangle=90, colors=['#27ae60', '#ecf0f1'],
                         wedgeprops={'width': 0.3}, autopct=None)
ax2.text(0, 0, f'{health_score}\n/100', ha='center', va='center', fontsize=20, fontweight='bold')
ax2.set_title('System Health Score', fontsize=14, fontweight='bold')

# Priority Actions
ax3 = fig.add_subplot(gs[0, 2])
ax3.axis('off')
actions = ['Replace Limpopo suppliers', 'Renegotiate herb contracts', 
           'Optimize KZN logistics', 'Scale Western Cape partners']
for i, action in enumerate(actions):
    ax3.text(0.1, 0.8 - i*0.15, f'• {action}', fontsize=11, va='center')
ax3.set_title('Priority Actions', fontsize=14, fontweight='bold', y=0.98)

# Weekly Trend
ax4 = fig.add_subplot(gs[1, 0:2])
weeks = list(range(1, 13))
on_time_trend = [88, 87, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76]
ax4.plot(weeks, on_time_trend, marker='o', linewidth=2, color='red')
ax4.fill_between(weeks, on_time_trend, 70, alpha=0.3, color='red')
ax4.set_xlabel('Week', fontsize=11)
ax4.set_ylabel('On-Time Rate (%)', fontsize=11)
ax4.set_title('Weekly Performance Trend', fontsize=14, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.axhline(y=80, color='orange', linestyle='--', linewidth=2, label='Target (80%)')
ax4.legend()

# Top Risks
ax5 = fig.add_subplot(gs[1, 2])
risks = ['Supplier Dependency', 'Price Volatility', 'Logistics Delays', 'Quality Issues']
risk_scores = [85, 78, 72, 65]
colors_risk = ['red', 'orange', 'orange', 'green']
bars = ax5.barh(risks, risk_scores, color=colors_risk)
ax5.set_xlabel('Risk Score', fontsize=11)
ax5.set_title('Top Risks', fontsize=14, fontweight='bold')

# Recommendations
ax6 = fig.add_subplot(gs[2, :])
ax6.axis('off')
recommendations = """RECOMMENDATIONS:
1. IMMEDIATE: Terminate contract with Limpopo Agro Farms (32% decline in reliability)
2. SHORT-TERM: Implement hedging strategy for herb prices (45% volatility)
3. MEDIUM-TERM: Diversify avocado suppliers to reduce dependency (single supplier at 38%)
4. LONG-TERM: Build inventory buffer for high-risk products during peak season"""
ax6.text(0.05, 0.5, recommendations, fontsize=12, va='center',
         bbox=dict(boxstyle='round', facecolor='#fff3cd', edgecolor='#ffc107', linewidth=2))
ax6.set_title('Strategic Recommendations', fontsize=14, fontweight='bold', y=0.98)

plt.savefig('images/08_executive_dashboard.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("  ✓ Saved: images/08_executive_dashboard.png")

print("=" * 60)
print("✅ All 8 images generated successfully!")
print("📁 Images saved to 'images/' directory")
print("=" * 60)

# Verify all images were created
print("\nVerifying images:")
import glob
for i in range(1, 9):
    files = glob.glob(f"images/{i:02d}_*.png")
    if files:
        size = os.path.getsize(files[0]) / 1024
        print(f"  ✓ Image {i}: {os.path.basename(files[0])} ({size:.1f} KB)")
    else:
        print(f"  ✗ Image {i}: Not found")

print("\n🎉 All images ready for use in your documentation!")