-- MIGRATION 002: STORE FEATURE SNAPSHOTS (Features Vendibles)
-- Separa las características de la tienda (Features HTML) del snapshot de ventas numérico.

CREATE TABLE IF NOT EXISTS store_feature_snapshots (
    id BIGSERIAL PRIMARY KEY,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    snapshot_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    snapshot_date DATE DEFAULT CURRENT_DATE, -- Para asegurar solo 1 al día
    theme TEXT NULL,
    pixel_meta JSONB DEFAULT '{}'::JSONB,  -- {meta:true, tiktok:false, ga:true}
    social JSONB DEFAULT '{}'::JSONB,      -- {instagram:..., tiktok:...}
    flags JSONB DEFAULT '{}'::JSONB,       -- {urgency:true, bundles:true, subscriptions:false}
    inventory_recency_days INT NULL,       -- Calculado si available en Python
    country_hint TEXT,                     -- Detectado por moneda/dominio
    currency TEXT,
    
    UNIQUE(store_id, snapshot_date) -- Idempotencia Diaria: solo 1 Feature Scan al día por tienda
);

CREATE INDEX IF NOT EXISTS idx_features_store_date ON store_feature_snapshots(store_id, snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_features_theme ON store_feature_snapshots(theme);
CREATE INDEX IF NOT EXISTS idx_features_pixel_meta ON store_feature_snapshots USING gin (pixel_meta); -- Necesita extensión pg_trgm o btree_gin a veces, JSONB ops default OK

-- Vista Combinada Features + Metrics (Super útil)
CREATE OR REPLACE VIEW view_store_intelligence AS
SELECT 
    s.domain,
    snap.total_products,
    snap.avg_price,
    snap.hero_score,
    feat.theme,
    feat.pixel_meta->>'tiktok' as has_tiktok_pixel,
    feat.pixel_meta->>'meta' as has_meta_pixel,
    feat.social->>'instagram' as instagram_url,
    snap.snapshot_at as last_updated
FROM stores s
LEFT JOIN LATERAL (
    SELECT * FROM store_snapshots 
    WHERE store_id = s.id 
    ORDER BY snapshot_at DESC LIMIT 1
) snap ON true
LEFT JOIN LATERAL (
    SELECT * FROM store_feature_snapshots 
    WHERE store_id = s.id 
    ORDER BY snapshot_at DESC LIMIT 1
) feat ON true;

