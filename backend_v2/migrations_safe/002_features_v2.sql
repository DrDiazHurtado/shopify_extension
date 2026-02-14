-- MIGRATION 002 V2: STORE FEATURE SNAPSHOTS (Features Vendibles)
-- Objetivo: Almacenar características (features) separadas de métricas, con tipos correctos (bool).

-- -----------------------------------------------------------------------------
-- 1. Create Feature Snapshots Table
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS store_feature_snapshots (
    id BIGSERIAL PRIMARY KEY,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    snapshot_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    snapshot_date DATE DEFAULT CURRENT_DATE, -- Para asegurar solo 1 al día
    theme TEXT NULL,
    pixel_meta JSONB DEFAULT '{}'::JSONB,  -- {meta:true, tiktok:false, ga:true}
    social JSONB DEFAULT '{}'::JSONB,      -- {instagram:..., tiktok:...}
    flags JSONB DEFAULT '{}'::JSONB,       -- {urgency:true, bundles:true, subscriptions:false}
    inventory_recency_days INT NULL,       -- Calculado si available
    country_hint TEXT,                     -- Detectado por moneda/dominio
    currency TEXT,
    
    -- Idempotencia Diaria: solo 1 Feature Scan al día por tienda. 
    -- Permite re-runs seguros que simplemente fallan (o podríamos usar ON CONFLICT DO UPDATE en código).
    UNIQUE(store_id, snapshot_date) 
);

-- Índices clave para búsquedas de Features
CREATE INDEX IF NOT EXISTS idx_features_store_date ON store_feature_snapshots(store_id, snapshot_date DESC);
CREATE INDEX IF NOT EXISTS idx_features_theme ON store_feature_snapshots(theme);
CREATE INDEX IF NOT EXISTS idx_features_pixel_meta ON store_feature_snapshots USING gin (pixel_meta); -- Necesario para búsquedas eficientes en JSONB

-- -----------------------------------------------------------------------------
-- 2. CREATE INTELLIGENCE VIEW (Typed Correctly)
-- -----------------------------------------------------------------------------

-- Vista Combinada Features + Metrics (Super útil para exportación y API)
-- FIX V2: COALESCE(val::boolean, false) para devolver tipos estrictos.
CREATE OR REPLACE VIEW view_store_intelligence AS
SELECT 
    s.domain,
    s.status,
    snap.total_products,
    snap.avg_price,
    snap.hero_score,
    feat.theme,
    -- Typing robusto para booleanos desde JSONB
    COALESCE((feat.pixel_meta->>'tiktok')::boolean, FALSE) as has_tiktok_pixel,
    COALESCE((feat.pixel_meta->>'meta')::boolean, FALSE) as has_meta_pixel,
    COALESCE((feat.pixel_meta->>'ga')::boolean, FALSE) as has_ga_pixel,
    
    -- Social links como texto o null
    feat.social->>'instagram' as instagram_url,
    feat.social->>'tiktok' as tiktok_url,
    
    snap.snapshot_at as last_ updated_at
FROM stores s
-- Usamos LATERAL JOIN para obtener el snapshot MÁS RECIENTE de métricas
LEFT JOIN LATERAL (
    SELECT * FROM store_snapshots 
    WHERE store_id = s.id 
    ORDER BY snapshot_at DESC LIMIT 1
) snap ON true
-- Y el snapshot MÁS RECIENTE de features
LEFT JOIN LATERAL (
    SELECT * FROM store_feature_snapshots 
    WHERE store_id = s.id 
    ORDER BY snapshot_at DESC LIMIT 1
) feat ON true;

