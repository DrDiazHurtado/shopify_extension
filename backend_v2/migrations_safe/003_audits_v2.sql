-- MIGRATION 003 V2: AUDITS
-- Objetivo: Verificaciones de calidad REALES que monitoricen estado y anomalías.

-- 1. Snapshot Distributions (Solo Tiendas Activas)
-- FIX: JOIN stores WHERE status = 'active'
CREATE OR REPLACE VIEW view_audit_snapshot_distributions AS
SELECT 
    percentile_disc(0.5) WITHIN GROUP (ORDER BY snap.total_products) as p50_products,
    percentile_disc(0.9) WITHIN GROUP (ORDER BY snap.total_products) as p90_products,
    percentile_disc(0.99) WITHIN GROUP (ORDER BY snap.total_products) as p99_products,
    percentile_disc(0.5) WITHIN GROUP (ORDER BY snap.avg_price) as p50_price,
    percentile_disc(0.99) WITHIN GROUP (ORDER BY snap.avg_price) as p99_price,
    count(*) as total_active_snapshots
FROM store_snapshots snap
JOIN stores s ON snap.store_id = s.id
WHERE 
    s.status = 'active' AND
    snap.snapshot_at > (NOW() - INTERVAL '1 DAY');


-- 2. Failure Reasons (Analizar estado del Scraper)
-- Agrupa errores para detectar patrones comunes (e.g. 403, Password blocks)
CREATE OR REPLACE VIEW view_audit_failure_reasons AS
SELECT 
    last_error as error_reason,
    count(*) as failed_stores,
    avg(fail_count) as avg_failures
FROM stores
WHERE status IN ('dead', 'blocked', 'password')
GROUP BY last_error
ORDER BY failed_stores DESC;


-- 3. Feature Coverage (Are we scraping correctly?)
-- FIX: Comparar JSONB <> '{}' en lugar de string.
CREATE OR REPLACE VIEW view_audit_coverage_features AS
SELECT 
    count(*) as total_feature_scans,
    sum(case when theme IS NOT NULL then 1 else 0 end) as has_theme,
    sum(case when pixel_meta <> '{}'::jsonb then 1 else 0 end) as has_pixels,
    sum(case when social <> '{}'::jsonb then 1 else 0 end) as has_social
FROM store_feature_snapshots
WHERE snapshot_at > (NOW() - INTERVAL '7 DAYS');


-- 4. Audit Signals & Alerts (Señales frescas de hoy)
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
