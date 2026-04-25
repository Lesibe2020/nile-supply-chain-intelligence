-- ============================================================================
-- NILE.AG SUPPLY CHAIN INTELLIGENCE – COMPLETE SQL QUERIES
-- Compatible with: PostgreSQL, MySQL, SQLite (with minor syntax adjustments)
-- Purpose: Power BI / Tableau dashboards, ad-hoc analysis, operational reporting
-- ============================================================================

-- ============================================================================
-- 1. EXECUTIVE DASHBOARD – Overall KPIs
-- ============================================================================
-- Question: What is our current supply chain health?
SELECT 
    COUNT(*) AS total_orders,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    ROUND(100.0 * SUM(on_time) / COUNT(*), 1) AS on_time_percentage,
    ROUND(MIN(delay_days), 0) AS min_delay,
    ROUND(MAX(delay_days), 0) AS max_delay,
    ROUND(SUM(total_value_zar), 0) AS total_revenue,
    ROUND(SUM(CASE WHEN risk_level IN ('Critical', 'High') THEN total_value_zar ELSE 0 END), 0) AS value_at_risk,
    ROUND(100.0 * SUM(CASE WHEN risk_level IN ('Critical', 'High') THEN total_value_zar ELSE 0 END) / SUM(total_value_zar), 1) AS risk_percentage
FROM supply_chain_data;


-- ============================================================================
-- 2. SUPPLIER PERFORMANCE RANKING (Fair Score)
-- ============================================================================
-- Question: Which suppliers are performing best/worst?
-- Score = On-Time% - (Avg Delay × 5)
SELECT 
    supplier,
    supplier_region,
    COUNT(*) AS total_orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(on_time) / COUNT(*), 1) AS on_time_percentage,
    ROUND(SUM(total_value_zar), 0) AS total_value,
    ROUND(SUM(CASE WHEN risk_level IN ('Critical', 'High') THEN total_value_zar ELSE 0 END), 0) AS value_at_risk,
    ROUND(100.0 * SUM(on_time) / COUNT(*) - AVG(delay_days) * 5, 1) AS reliability_score,
    CASE 
        WHEN ROUND(100.0 * SUM(on_time) / COUNT(*) - AVG(delay_days) * 5, 1) < 60 AND COUNT(*) > 30 THEN '⚠️ Review Contract'
        WHEN ROUND(100.0 * SUM(on_time) / COUNT(*) - AVG(delay_days) * 5, 1) < 40 THEN '⚠️ Urgent Action'
        ELSE '✅ Monitor'
    END AS action_required
FROM supply_chain_data
GROUP BY supplier, supplier_region
ORDER BY reliability_score DESC;


-- ============================================================================
-- 3. DECLINING SUPPLIERS – Monthly Trend Analysis
-- ============================================================================
-- Question: Which suppliers are getting worse over time?
WITH monthly_supplier AS (
    SELECT 
        supplier,
        DATE_TRUNC('month', order_date) AS month,
        AVG(on_time) AS on_time_rate,
        COUNT(*) AS orders
    FROM supply_chain_data
    GROUP BY supplier, DATE_TRUNC('month', order_date)
),
trend_calc AS (
    SELECT 
        supplier,
        MIN(on_time_rate) AS min_rate,
        MAX(on_time_rate) AS max_rate,
        -- Simple trend: compare first 3 months vs last 3 months
        (AVG(CASE WHEN month >= (SELECT MAX(month) FROM monthly_supplier m2 WHERE m2.supplier = m1.supplier) - INTERVAL '3 months' THEN on_time_rate ELSE NULL END) -
         AVG(CASE WHEN month <= (SELECT MIN(month) FROM monthly_supplier m2 WHERE m2.supplier = m1.supplier) + INTERVAL '3 months' THEN on_time_rate ELSE NULL END)) AS trend_change
    FROM monthly_supplier m1
    GROUP BY supplier
)
SELECT 
    supplier,
    ROUND(trend_change * 100, 1) AS percentage_change,
    ROUND(min_rate * 100, 1) AS lowest_rate,
    ROUND(max_rate * 100, 1) AS highest_rate,
    CASE 
        WHEN trend_change < -0.05 THEN '🔻 CRITICAL DECLINE'
        WHEN trend_change < -0.02 THEN '📉 Declining'
        WHEN trend_change > 0.05 THEN '📈 Improving'
        ELSE '➡️ Stable'
    END AS trend_status
FROM trend_calc
WHERE trend_change IS NOT NULL
ORDER BY trend_change;


-- ============================================================================
-- 4. WORST REGION–PRODUCT HOTSPOTS (Logistics Focus)
-- ============================================================================
-- Question: Which specific lanes (region + product) have the worst delays?
SELECT 
    supplier_region,
    product,
    product_category,
    perishable,
    COUNT(*) AS orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(MAX(delay_days), 0) AS max_delay,
    ROUND(100.0 * SUM(CASE WHEN delay_days > 3 THEN 1 ELSE 0 END) / COUNT(*), 1) AS severe_delay_percentage,
    ROUND(SUM(total_value_zar), 0) AS total_value,
    CASE 
        WHEN AVG(delay_days) > 5 THEN '🔥 CRITICAL'
        WHEN AVG(delay_days) > 3 THEN '⚠️ High'
        WHEN AVG(delay_days) > 1 THEN '📌 Medium'
        ELSE '✅ Good'
    END AS hotspot_severity
FROM supply_chain_data
WHERE delay_days > 0
GROUP BY supplier_region, product, product_category, perishable
HAVING COUNT(*) >= 5
ORDER BY avg_delay DESC
LIMIT 20;


-- ============================================================================
-- 5. PRICE SPIKE CALENDAR – Seasonal Anomalies
-- ============================================================================
-- Question: When do price spikes happen most frequently?
WITH price_stats AS (
    SELECT 
        product,
        AVG(price_per_kg) AS mean_price,
        STDDEV(price_per_kg) AS std_price
    FROM supply_chain_data
    GROUP BY product
),
spike_data AS (
    SELECT 
        s.product,
        EXTRACT(MONTH FROM s.order_date) AS month_num,
        CASE WHEN s.price_per_kg > p.mean_price + 2 * p.std_price THEN 1 ELSE 0 END AS is_spike
    FROM supply_chain_data s
    JOIN price_stats p ON s.product = p.product
)
SELECT 
    CASE month_num
        WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March'
        WHEN 4 THEN 'April' WHEN 5 THEN 'May' WHEN 6 THEN 'June'
        WHEN 7 THEN 'July' WHEN 8 THEN 'August' WHEN 9 THEN 'September'
        WHEN 10 THEN 'October' WHEN 11 THEN 'November' WHEN 12 THEN 'December'
    END AS month,
    COUNT(*) AS total_orders,
    SUM(is_spike) AS spike_count,
    ROUND(100.0 * SUM(is_spike) / COUNT(*), 1) AS spike_rate_percentage
FROM spike_data
GROUP BY month_num
ORDER BY spike_rate_percentage DESC;


-- ============================================================================
-- 6. PRODUCT RISK RANKING
-- ============================================================================
-- Question: Which products cause the most operational headache?
SELECT 
    product,
    product_category,
    perishable,
    COUNT(*) AS total_orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(CASE WHEN delay_days > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS delay_frequency,
    ROUND(100.0 * SUM(CASE WHEN delay_days > 3 THEN 1 ELSE 0 END) / COUNT(*), 1) AS severe_delay_frequency,
    ROUND(AVG(price_per_kg), 2) AS avg_price,
    ROUND(SUM(total_value_zar), 0) AS total_value,
    ROUND(SUM(CASE WHEN delay_days > 0 THEN total_value_zar ELSE 0 END) / NULLIF(SUM(total_value_zar), 0) * 100, 1) AS value_at_risk_percentage
FROM supply_chain_data
GROUP BY product, product_category, perishable
ORDER BY avg_delay DESC;


-- ============================================================================
-- 7. CUSTOMER IMPACT ANALYSIS (If customer_id exists)
-- ============================================================================
-- Question: Which customers are most affected by delays?
-- Note: Only runs if customer_id column exists
SELECT 
    'customer_id' AS column_check,
    CASE WHEN COUNT(*) > 0 THEN 'Available' ELSE 'Missing' END AS status
FROM information_schema.columns 
WHERE table_name = 'supply_chain_data' AND column_name = 'customer_id';

-- Uncomment below when customer_id exists:
/*
SELECT 
    customer_id,
    COUNT(*) AS orders_placed,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(on_time) / COUNT(*), 1) AS on_time_percentage,
    ROUND(SUM(total_value_zar), 0) AS total_spent,
    ROUND(SUM(CASE WHEN delay_days > 5 THEN total_value_zar ELSE 0 END), 0) AS high_risk_exposure
FROM supply_chain_data
GROUP BY customer_id
ORDER BY avg_delay DESC
LIMIT 20;
*/


-- ============================================================================
-- 8. MONTHLY TREND ANALYSIS (Time Series)
-- ============================================================================
-- Question: How is supply chain health changing month over month?
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    COUNT(*) AS orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(on_time) / COUNT(*), 1) AS on_time_percentage,
    ROUND(SUM(total_value_zar), 0) AS revenue,
    ROUND(SUM(CASE WHEN delay_days > 3 THEN total_value_zar ELSE 0 END) / NULLIF(SUM(total_value_zar), 0) * 100, 1) AS value_at_risk_percentage,
    COUNT(DISTINCT supplier) AS active_suppliers
FROM supply_chain_data
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month DESC;


-- ============================================================================
-- 9. PRICE ANOMALY DETAILS (For Investigation)
-- ============================================================================
-- Question: List all price anomalies for procurement team to investigate
WITH price_stats AS (
    SELECT 
        product,
        AVG(price_per_kg) AS mean_price,
        STDDEV(price_per_kg) AS std_price
    FROM supply_chain_data
    GROUP BY product
)
SELECT 
    s.order_id,
    s.order_date,
    s.product,
    s.supplier,
    s.price_per_kg,
    ROUND(p.mean_price, 2) AS product_avg_price,
    ROUND(p.std_price, 2) AS product_std_price,
    ROUND((s.price_per_kg - p.mean_price) / p.mean_price * 100, 1) AS spike_percentage,
    s.quantity_kg,
    s.total_value_zar,
    CASE 
        WHEN s.price_per_kg > p.mean_price + 3 * p.std_price THEN 'Extreme Spike'
        WHEN s.price_per_kg > p.mean_price + 2 * p.std_price THEN 'Moderate Spike'
        ELSE 'Normal'
    END AS anomaly_severity
FROM supply_chain_data s
JOIN price_stats p ON s.product = p.product
WHERE s.price_per_kg > p.mean_price + 2 * p.std_price
ORDER BY spike_percentage DESC
LIMIT 100;


-- ============================================================================
-- 10. OPERATIONAL ALERTS – Orders Requiring Immediate Action
-- ============================================================================
-- Question: Which orders need immediate attention right now?
SELECT 
    order_id,
    order_date,
    product,
    supplier,
    supplier_region,
    delay_days,
    total_value_zar,
    CASE 
        WHEN perishable = TRUE AND delay_days > 2 THEN '🚨 URGENT: Perishable order critically delayed'
        WHEN delay_days > 7 THEN '🚨 URGENT: Severe delay (>7 days)'
        WHEN delay_days > 5 THEN '⚠️ High priority: Significant delay'
        WHEN perishable = TRUE AND delay_days > 1 THEN '⚠️ Perishable order delayed'
        ELSE 'Monitor'
    END AS alert_reason,
    CURRENT_DATE - order_date AS days_since_order
FROM supply_chain_data
WHERE delay_days > 0  -- Currently delayed
    AND actual_delivery_date > CURRENT_DATE  -- Not yet delivered (in real-time)
ORDER BY 
    CASE WHEN perishable = TRUE THEN 1 ELSE 2 END,
    delay_days DESC
LIMIT 50;


-- ============================================================================
-- ADDITIONAL: VIEWS FOR POWER BI (Create once, query repeatedly)
-- ============================================================================

-- Create view: Supplier performance summary
CREATE VIEW IF NOT EXISTS v_supplier_performance AS
SELECT 
    supplier,
    supplier_region,
    COUNT(*) AS total_orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(on_time) / COUNT(*), 1) AS on_time_pct,
    ROUND(100.0 * SUM(on_time) / COUNT(*) - AVG(delay_days) * 5, 1) AS reliability_score
FROM supply_chain_data
GROUP BY supplier, supplier_region;

-- Create view: Daily operational metrics
CREATE VIEW IF NOT EXISTS v_daily_metrics AS
SELECT 
    DATE(order_date) AS date,
    COUNT(*) AS orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(on_time) / COUNT(*), 1) AS on_time_pct,
    ROUND(SUM(total_value_zar), 0) AS revenue
FROM supply_chain_data
GROUP BY DATE(order_date)
ORDER BY date DESC;

-- ============================================================================
-- NOTES FOR POWER BI / TABLEAU INTEGRATION:
-- 1. For Power BI: Use "Import" mode for these queries
-- 2. For Tableau: Use "Custom SQL" in data source
-- 3. For real-time: Wrap in a stored procedure and refresh every hour
-- 4. Date functions vary by database:
--    - PostgreSQL: DATE_TRUNC('month', date)
--    - MySQL: DATE_FORMAT(date, '%Y-%m-01')
--    - SQLite: STRFTIME('%Y-%m', date)
-- ============================================================================