-- MIGRATION 003: AUDITS (QA / DASHBOARD)
-- Auditorías rápidas para verificar integridad de datos.

CREATE OR REPLACE VIEW view_audit_snapshot_distributions AS
-- Distribution of products and prices across active stores
SELECT 
    percentile_disc(0.5) WITHIN GROUP (ORDER BY total_products) as p50_products,
    percentile_disc(0.9) WITHIN GROUP (ORDER BY total_products) as p90_products,
    percentile_disc(0.99) WITHIN GROUP (ORDER BY total_products) as p99_products,
    percentile_disc(0.5) WITHIN GROUP (ORDER BY avg_price) as p50_price,
    percentile_disc(0.99) WITHIN GROUP (ORDER BY avg_price) as p99_price,
    count(*) as total_active_snapshots
FROM (
    SELECT total_products, avg_price 
    FROM store_snapshots 
    WHERE snapshot_at > (NOW() - INTERVAL '1 DAY')
) as recent_snaps;

CREATE OR REPLACE VIEW view_audit_failure_reasons AS
-- Conteo de fallos por tipo
SELECT 
    last_error as error_reason,
    count(*) as failed_stores,
    avg(fail_count) as avg_failures
FROM stores
WHERE status IN ('dead', 'blocked', 'password')
GROUP BY last_error
ORDER BY failed_stores DESC;

CREATE OR REPLACE VIEW view_audit_coverage_features AS
-- Check coverage of features (Are we getting blank data?)
SELECT 
    count(*) as total_feature_scans,
    sum(case when theme IS NOT NULL then 1 else 0 end) as has_theme,
    sum(case when pixel_meta::text != '{}'::text then 1 else 0 end) as has_pixels,
    sum(case when social::text != '{}'::text then 1 else 0 end) as has_social
FROM store_feature_snapshots
WHERE snapshot_at > (NOW() - INTERVAL '7 DAYS');

-- Vista: Listado de Alertas Potenciales (Señales de hoy)
CREATE OR REPLACE VIEW view_signals_alerts_today AS
    SELECT 
        s.domain,
        sig.window_days,
        sig.signal_key,
        sig.signal_value,
        sig.computed_date
    FROM store_signals sig
    JOIN stores s ON sig.store_id = s.id
    WHERE sig.computed_date = CURRENT_DATE
    ORDER BY abs(sig.signal_value) DESC;
