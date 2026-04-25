-- ============================================================================
-- NILE CONTROL TOWER – FINAL INTELLIGENCE LAYER
-- Purpose: Decision-making, prioritization, and operational control
-- Compatible: PostgreSQL (adapt DATE_TRUNC if using MySQL/SQLite)
-- ============================================================================

-- ============================================================================
-- 0. BASE VIEW (STANDARDIZED FOUNDATION)
-- ============================================================================
CREATE OR REPLACE VIEW v_base AS
SELECT
    order_id,
    order_date,
    supplier,
    supplier_region,
    product,
    product_category,
    perishable,
    quantity_kg,
    price_per_kg,
    total_value_zar,
    expected_delivery_date,
    actual_delivery_date,

    -- Core metrics
    (actual_delivery_date - expected_delivery_date) AS delay_days,
    CASE WHEN actual_delivery_date <= expected_delivery_date THEN 1 ELSE 0 END AS on_time,

    DATE_TRUNC('month', order_date) AS month
FROM supply_chain_data;

-- ============================================================================
-- 1. SYSTEM HEALTH SCORE (EXECUTIVE KPI)
-- ============================================================================
CREATE OR REPLACE VIEW v_system_score AS
SELECT
    COUNT(*) AS total_orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(on_time) / COUNT(*), 1) AS on_time_pct,

    ROUND(
        (AVG(on_time) * 100)
        - (AVG(delay_days) * 5)
        - (SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) * 100)
    ,1) AS system_health_score,

    CASE
        WHEN AVG(on_time) < 0.7 THEN '🔴 CRITICAL'
        WHEN AVG(delay_days) > 3 THEN '🟠 UNSTABLE'
        ELSE '🟢 STABLE'
    END AS system_status
FROM v_base;

-- ============================================================================
-- 2. SUPPLIER DECISION ENGINE
-- ============================================================================
CREATE OR REPLACE VIEW v_supplier_decision AS
SELECT
    supplier,
    supplier_region,
    COUNT(*) AS orders,
    ROUND(AVG(delay_days),2) AS avg_delay,
    ROUND(STDDEV(delay_days),2) AS volatility,
    ROUND(100.0 * SUM(on_time)/COUNT(*),1) AS on_time_pct,
    ROUND(SUM(total_value_zar),0) AS total_value,

    -- Risk score
    ROUND(
        AVG(delay_days)*2 +
        STDDEV(delay_days) +
        (1 - SUM(on_time)*1.0/COUNT(*))*50
    ,2) AS risk_score,

    -- Decision output
    CASE
        WHEN AVG(delay_days) > 5 AND COUNT(*) > 30 THEN '❌ TERMINATE'
        WHEN AVG(delay_days) > 3 THEN '⚠️ REVIEW CONTRACT'
        WHEN SUM(on_time)*1.0/COUNT(*) > 0.9 THEN '🚀 SCALE SUPPLIER'
        ELSE '👀 MONITOR'
    END AS decision
FROM v_base
GROUP BY supplier, supplier_region;

-- ============================================================================
-- 3. DECLINING SUPPLIERS (TREND ENGINE)
-- ============================================================================
CREATE OR REPLACE VIEW v_supplier_trends AS
WITH monthly AS (
    SELECT
        supplier,
        month,
        AVG(on_time) AS on_time_rate
    FROM v_base
    GROUP BY supplier, month
),
compare AS (
    SELECT
        supplier,
        AVG(on_time_rate) FILTER (WHERE month >= CURRENT_DATE - INTERVAL '3 months') AS recent,
        AVG(on_time_rate) FILTER (WHERE month < CURRENT_DATE - INTERVAL '3 months') AS past
    FROM monthly
    GROUP BY supplier
)
SELECT
    supplier,
    ROUND((COALESCE(recent, 0) - COALESCE(past, 0))*100, 2) AS change_pct,
    CASE
        WHEN COALESCE(recent, 0) < COALESCE(past, 0) * 0.85 THEN '🔻 SHARP DECLINE'
        WHEN COALESCE(recent, 0) < COALESCE(past, 0) THEN '📉 DECLINING'
        WHEN COALESCE(recent, 0) > COALESCE(past, 0) THEN '📈 IMPROVING'
        ELSE '➡️ STABLE'
    END AS trend_signal,
    CASE
        WHEN COALESCE(recent, 0) < COALESCE(past, 0) * 0.85 THEN 'ACTION_NEEDED'
        ELSE 'MONITOR'
    END AS action_priority
FROM compare
WHERE recent IS NOT NULL AND past IS NOT NULL
ORDER BY change_pct;

-- ============================================================================
-- 4. LOGISTICS HOTSPOTS (LANE ANALYSIS)
-- ============================================================================
CREATE OR REPLACE VIEW v_hotspots AS
SELECT
    supplier_region,
    product,
    product_category,
    COUNT(*) AS orders,
    ROUND(AVG(delay_days),2) AS avg_delay,
    ROUND(STDDEV(delay_days),2) AS volatility,
    ROUND(100.0 * SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END)/COUNT(*), 1) AS critical_rate,

    ROUND(
        AVG(delay_days)*2 +
        COALESCE(STDDEV(delay_days), 0) +
        (SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END)*1.0/COUNT(*)*10)
    ,2) AS severity_score,

    CASE
        WHEN AVG(delay_days) > 5 THEN '🔥 FIX IMMEDIATELY'
        WHEN AVG(delay_days) > 3 THEN '⚠️ OPTIMIZE'
        ELSE '✅ OK'
    END AS action,
    
    ROUND(SUM(total_value_zar), 0) AS financial_impact
FROM v_base
GROUP BY supplier_region, product, product_category
HAVING COUNT(*) > 10
ORDER BY severity_score DESC;

-- ============================================================================
-- 5. PROFIT LEAKAGE (FINANCIAL IMPACT)
-- ============================================================================
CREATE OR REPLACE VIEW v_profit_leakage AS
SELECT
    product,
    supplier,
    supplier_region,
    COUNT(*) AS delayed_orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(SUM(
        total_value_zar *
        CASE 
            WHEN delay_days > 7 THEN 0.30
            WHEN delay_days > 5 THEN 0.20
            WHEN delay_days > 3 THEN 0.10
            ELSE 0.05
        END
    ), 0) AS estimated_loss,
    
    ROUND(SUM(total_value_zar), 0) AS total_value_at_risk
FROM v_base
WHERE delay_days > 0
GROUP BY product, supplier, supplier_region
ORDER BY estimated_loss DESC;

-- ============================================================================
-- 6. ROOT CAUSE ENGINE
-- ============================================================================
CREATE OR REPLACE VIEW v_root_causes AS
SELECT
    supplier_region,
    product_category,
    COUNT(*) AS sample_size,
    ROUND(AVG(delay_days),2) AS avg_delay,
    ROUND(STDDEV(delay_days),2) AS volatility,
    ROUND(AVG(quantity_kg),0) AS avg_volume,
    ROUND(100.0 * SUM(CASE WHEN perishable THEN 1 ELSE 0 END)/COUNT(*), 1) AS perishable_pct,

    CASE
        WHEN AVG(quantity_kg) > 1000 AND AVG(delay_days) > 3 THEN 'Volume Overload'
        WHEN STDDEV(delay_days) > 5 THEN 'Operational Instability'
        WHEN AVG(delay_days) > 4 THEN 'Chronic Delay'
        WHEN AVG(quantity_kg) < 100 AND AVG(delay_days) > 3 THEN 'Small Batch Inefficiency'
        ELSE 'Normal Operations'
    END AS root_cause,
    
    -- Recommended action per root cause
    CASE
        WHEN AVG(quantity_kg) > 1000 AND AVG(delay_days) > 3 THEN 'Split large orders into smaller batches'
        WHEN STDDEV(delay_days) > 5 THEN 'Audit supplier operational processes'
        WHEN AVG(delay_days) > 4 THEN 'Renegotiate SLAs or find alternative suppliers'
        WHEN AVG(quantity_kg) < 100 AND AVG(delay_days) > 3 THEN 'Consolidate small orders'
        ELSE 'Continue monitoring'
    END AS recommendation
FROM v_base
GROUP BY supplier_region, product_category
HAVING COUNT(*) > 20
ORDER BY avg_delay DESC;

-- ============================================================================
-- 7. PRIORITY ACTION QUEUE (REAL-TIME OPERATIONS)
-- ============================================================================
CREATE OR REPLACE VIEW v_priority_queue AS
SELECT
    order_id,
    order_date,
    supplier,
    supplier_region,
    product,
    perishable,
    delay_days,
    total_value_zar,
    (delay_days * total_value_zar / 1000) AS urgency_score,

    CASE
        WHEN perishable AND delay_days > 2 THEN '🚨 SAVE NOW - Perishable'
        WHEN delay_days > 7 THEN '🚨 ESCALATE - Critical Delay'
        WHEN delay_days > 5 THEN '⚠️ PRIORITY - Severe Delay'
        WHEN delay_days > 3 THEN '📞 CONTACT - Moderate Delay'
        ELSE 'Monitor'
    END AS action,
    
    CASE
        WHEN perishable AND delay_days > 2 THEN 'HIGHEST'
        WHEN delay_days > 7 THEN 'HIGH'
        WHEN delay_days > 5 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS priority_level
FROM v_base
WHERE delay_days > 0
ORDER BY urgency_score DESC
LIMIT 50;

-- ============================================================================
-- 8. SUPPLY STRESS INDEX (MONTHLY)
-- ============================================================================
CREATE OR REPLACE VIEW v_supply_stress AS
SELECT
    product,
    product_category,
    TO_CHAR(month, 'YYYY-MM') AS year_month,
    SUM(quantity_kg) AS total_demand,
    COUNT(*) AS order_count,
    ROUND(AVG(delay_days),2) AS avg_delay,
    ROUND(100.0 * SUM(CASE WHEN delay_days > 0 THEN 1 ELSE 0 END)/COUNT(*), 1) AS delay_rate,

    -- Stress index: higher demand + higher delay = higher stress
    ROUND(
        (SUM(quantity_kg) / NULLIF(AVG(delay_days + 0.01), 0)) / 100
    , 2) AS stress_index,
    
    CASE
        WHEN SUM(quantity_kg) > 50000 AND AVG(delay_days) > 3 THEN 'CRITICAL STRESS'
        WHEN SUM(quantity_kg) > 30000 AND AVG(delay_days) > 2 THEN 'HIGH STRESS'
        WHEN AVG(delay_days) > 3 THEN 'MODERATE STRESS'
        ELSE 'NORMAL'
    END AS stress_level
FROM v_base
GROUP BY product, product_category, month
HAVING COUNT(*) > 5
ORDER BY stress_index DESC;

-- ============================================================================
-- 9. PRICE ANOMALY DETECTION
-- ============================================================================
CREATE OR REPLACE VIEW v_price_anomalies AS
WITH stats AS (
    SELECT
        product,
        AVG(price_per_kg) AS mean_price,
        STDDEV(price_per_kg) AS std_price,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY price_per_kg) AS p95_price
    FROM v_base
    GROUP BY product
)
SELECT
    b.order_id,
    b.order_date,
    b.product,
    b.supplier,
    b.supplier_region,
    b.price_per_kg,
    ROUND(s.mean_price, 2) AS avg_price,
    ROUND(s.p95_price, 2) AS benchmark_price,
    ROUND((b.price_per_kg - s.mean_price)/s.mean_price * 100, 1) AS deviation_pct,

    CASE
        WHEN b.price_per_kg > s.mean_price + 3 * s.std_price THEN 'Extreme Spike'
        WHEN b.price_per_kg > s.mean_price + 2 * s.std_price THEN 'Moderate Spike'
        WHEN b.price_per_kg < s.mean_price - 2 * s.std_price THEN 'Price Drop'
        ELSE 'Normal'
    END AS anomaly_type,
    
    ROUND(b.price_per_kg - s.mean_price, 2) AS price_difference
FROM v_base b
JOIN stats s ON b.product = s.product
WHERE b.price_per_kg > s.mean_price + 2 * s.std_price
   OR b.price_per_kg < s.mean_price - 2 * s.std_price
ORDER BY deviation_pct DESC;

-- ============================================================================
-- 10. EARLY WARNING SYSTEM (TRENDING)
-- ============================================================================
CREATE OR REPLACE VIEW v_early_warning AS
WITH recent AS (
    SELECT 
        AVG(delay_days) AS recent_delay,
        AVG(on_time) AS recent_on_time,
        COUNT(*) AS recent_orders
    FROM v_base
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
),
past AS (
    SELECT 
        AVG(delay_days) AS past_delay,
        AVG(on_time) AS past_on_time,
        COUNT(*) AS past_orders
    FROM v_base
    WHERE order_date < CURRENT_DATE - INTERVAL '30 days'
      AND order_date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT
    ROUND(recent_delay, 2) AS current_avg_delay,
    ROUND(past_delay, 2) AS previous_avg_delay,
    ROUND(recent_on_time * 100, 1) AS current_on_time_pct,
    ROUND(past_on_time * 100, 1) AS previous_on_time_pct,
    ROUND(recent_delay - past_delay, 2) AS delay_change,
    ROUND((recent_on_time - past_on_time) * 100, 1) AS on_time_change_pct,

    CASE
        WHEN recent_delay > past_delay * 1.3 THEN '🚨 CRITICAL DETERIORATION'
        WHEN recent_delay > past_delay * 1.15 THEN '⚠️ WARNING - Deteriorating'
        WHEN recent_on_time < past_on_time * 0.85 THEN '⚠️ WARNING - Quality Drop'
        WHEN recent_delay < past_delay * 0.85 THEN '✅ IMPROVING'
        ELSE '➡️ STABLE'
    END AS system_alert,
    
    CASE
        WHEN recent_delay > past_delay * 1.3 THEN 'IMMEDIATE_INTERVENTION'
        WHEN recent_delay > past_delay * 1.15 THEN 'REVIEW_PROCESSES'
        ELSE 'ROUTINE_MONITORING'
    END AS required_action
FROM recent, past;

-- ============================================================================
-- 11. SUPPLIER DEPENDENCY RISK
-- ============================================================================
CREATE OR REPLACE VIEW v_supplier_dependency AS
WITH totals AS (
    SELECT 
        SUM(quantity_kg) AS total_volume,
        SUM(total_value_zar) AS total_value
    FROM v_base
)
SELECT
    s.supplier,
    s.supplier_region,
    COUNT(*) AS order_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS order_share_pct,
    ROUND(100.0 * SUM(s.quantity_kg) / t.total_volume, 2) AS volume_share_pct,
    ROUND(100.0 * SUM(s.total_value_zar) / t.total_value, 2) AS value_share_pct,
    ROUND(AVG(s.delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(s.on_time)/COUNT(*), 1) AS reliability_pct,

    CASE
        WHEN COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () > 0.30 THEN '⚠️ CRITICAL DEPENDENCY'
        WHEN COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () > 0.20 THEN '⚠️ HIGH DEPENDENCY'
        WHEN COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () > 0.10 THEN 'Moderate Dependency'
        ELSE 'Diversified'
    END AS dependency_risk,
    
    CASE
        WHEN COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () > 0.30 AND AVG(delay_days) > 2 THEN 'URGENT: Diversify Required'
        WHEN COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () > 0.20 AND AVG(delay_days) > 3 THEN 'Plan Backup Suppliers'
        ELSE 'Monitor'
    END AS risk_mitigation_action
FROM v_base s
CROSS JOIN totals t
GROUP BY s.supplier, s.supplier_region, t.total_volume, t.total_value
ORDER BY value_share_pct DESC;

-- ============================================================================
-- 12. DAILY PERFORMANCE DASHBOARD (OPERATIONS)
-- ============================================================================
CREATE OR REPLACE VIEW v_daily_performance AS
SELECT
    order_date::DATE AS date,
    COUNT(*) AS orders,
    ROUND(100.0 * SUM(on_time)/COUNT(*), 1) AS on_time_rate,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    COUNT(CASE WHEN delay_days > 5 THEN 1 END) AS critical_delays,
    ROUND(SUM(total_value_zar), 0) AS daily_value,
    ROUND(SUM(CASE WHEN delay_days > 0 THEN total_value_zar ELSE 0 END), 0) AS value_at_risk
FROM v_base
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY order_date
ORDER BY order_date DESC;

-- ============================================================================
-- 13. PRODUCT RISK RANKING
-- ============================================================================
CREATE OR REPLACE VIEW v_product_risk AS
SELECT
    product,
    product_category,
    perishable,
    COUNT(*) AS orders,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END)/COUNT(*), 1) AS critical_rate,
    ROUND(STDDEV(delay_days), 2) AS delay_volatility,
    ROUND(SUM(total_value_zar), 0) AS total_value,

    -- Combined risk score
    ROUND(
        (AVG(delay_days) * 3) +
        (STDDEV(delay_days) * 2) +
        (SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END) * 10.0 / COUNT(*)) +
        (CASE WHEN perishable THEN 5 ELSE 0 END)
    , 2) AS risk_score,

    CASE
        WHEN AVG(delay_days) > 5 OR SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END)*1.0/COUNT(*) > 0.3 THEN '🔴 HIGH RISK'
        WHEN AVG(delay_days) > 3 OR SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END)*1.0/COUNT(*) > 0.15 THEN '🟡 MEDIUM RISK'
        ELSE '🟢 LOW RISK'
    END AS risk_level
FROM v_base
GROUP BY product, product_category, perishable
HAVING COUNT(*) > 10
ORDER BY risk_score DESC;

-- ============================================================================
-- 14. SEASONAL INSIGHTS
-- ============================================================================
CREATE OR REPLACE VIEW v_seasonal_insights AS
SELECT
    EXTRACT(MONTH FROM order_date) AS month_num,
    TO_CHAR(order_date, 'Month') AS month_name,
    product_category,
    COUNT(*) AS orders,
    ROUND(AVG(price_per_kg), 2) AS avg_price,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    ROUND(100.0 * SUM(on_time)/COUNT(*), 1) AS on_time_rate,
    ROUND(AVG(quantity_kg), 0) AS avg_order_size
FROM v_base
GROUP BY month_num, month_name, product_category
ORDER BY product_category, month_num;

-- ============================================================================
-- 15. EXECUTIVE SUMMARY (ALL KEY METRICS)
-- ============================================================================
CREATE OR REPLACE VIEW v_executive_summary AS
SELECT
    (SELECT COUNT(*) FROM v_base) AS total_orders,
    (SELECT ROUND(100.0 * SUM(on_time)/COUNT(*), 1) FROM v_base) AS overall_on_time_rate,
    (SELECT ROUND(AVG(delay_days), 2) FROM v_base) AS overall_avg_delay,
    (SELECT ROUND(SUM(total_value_zar), 0) FROM v_base) AS total_revenue,
    (SELECT COUNT(DISTINCT supplier) FROM v_base) AS active_suppliers,
    (SELECT COUNT(DISTINCT product) FROM v_base) AS active_products,
    (SELECT COUNT(*) FROM v_priority_queue WHERE priority_level IN ('HIGHEST', 'HIGH')) AS urgent_actions,
    (SELECT ROUND(SUM(estimated_loss), 0) FROM v_profit_leakage) AS total_profit_leakage,
    (SELECT COUNT(*) FROM v_supplier_dependency WHERE dependency_risk LIKE '%CRITICAL%') AS critical_dependencies,
    (SELECT COUNT(*) FROM v_price_anomalies WHERE anomaly_type LIKE '%Spike%') AS price_spikes,
    CURRENT_TIMESTAMP AS report_generated_at;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================

-- Optional: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_order_date ON supply_chain_data(order_date);
CREATE INDEX IF NOT EXISTS idx_supplier ON supply_chain_data(supplier);
CREATE INDEX IF NOT EXISTS idx_product ON supply_chain_data(product);
CREATE INDEX IF NOT EXISTS idx_region ON supply_chain_data(supplier_region);