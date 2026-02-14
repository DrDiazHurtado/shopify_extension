-- -----------------------------------------------------------------------------
-- TAREA 1: DISEÑO DB (Incrementally Friendly)
-- -----------------------------------------------------------------------------

-- 1. Tabla Stores (Master de Identidad)
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'blocked', 'password', 'dead', 'unknown')),
    country_hint TEXT NULL,
    notes JSONB DEFAULT '{}'::JSONB
);

-- 2. Tabla Store Snapshots (Histórico de Métricas - El Activo Vendible)
CREATE TABLE IF NOT EXISTS store_snapshots (
    id BIGSERIAL PRIMARY KEY,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    snapshot_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_products INT,
    avg_price NUMERIC,
    hero_score NUMERIC,
    vendor_count INT,
    discount_ratio NUMERIC,
    currency TEXT,
    scan_meta JSONB DEFAULT '{}'::JSONB, -- timings, pagination success, errors
    UNIQUE(store_id, snapshot_at)
);
CREATE INDEX IF NOT EXISTS idx_store_snapshots_lookup ON store_snapshots(store_id, snapshot_at DESC);

-- 3. Tabla Products (Entidades Mínimas)
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    shopify_product_id BIGINT,
    handle TEXT,
    title TEXT,
    vendor TEXT,
    product_type TEXT,
    status TEXT, -- active|draft|archived
    published_at TIMESTAMPTZ,
    created_at_shopify TIMESTAMPTZ,
    updated_at_shopify TIMESTAMPTZ,
    tags TEXT,
    raw JSONB, -- Payload original (optimizado)
    UNIQUE(store_id, shopify_product_id)
);
CREATE INDEX IF NOT EXISTS idx_products_store ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_updated ON products(store_id, updated_at_shopify DESC);
CREATE INDEX IF NOT EXISTS idx_products_vendor ON products(vendor);

-- 4. Tabla Variants (Entidades Mínimas)
CREATE TABLE IF NOT EXISTS variants (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(id) ON DELETE CASCADE,
    shopify_variant_id BIGINT,
    sku TEXT,
    price NUMERIC,
    compare_at_price NUMERIC,
    available BOOLEAN,
    inventory_quantity INT, -- No siempre fiable
    updated_at_shopify TIMESTAMPTZ,
    raw JSONB,
    UNIQUE(product_id, shopify_variant_id)
);
CREATE INDEX IF NOT EXISTS idx_variants_product ON variants(product_id);
CREATE INDEX IF NOT EXISTS idx_variants_price ON variants(price);

-- 5. Tabla Variant Snapshots (Para detectar Price Moves y Restocks)
CREATE TABLE IF NOT EXISTS variant_snapshots (
    id BIGSERIAL PRIMARY KEY,
    variant_id BIGINT REFERENCES variants(id) ON DELETE CASCADE,
    snapshot_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    price NUMERIC,
    compare_at_price NUMERIC,
    available BOOLEAN,
    inventory_quantity INT,
    UNIQUE(variant_id, snapshot_at)
);
CREATE INDEX IF NOT EXISTS idx_variant_snapshots_lookup ON variant_snapshots(variant_id, snapshot_at DESC);

-- 6. Tabla Store Signals (Inteligencia Derivada)
CREATE TABLE IF NOT EXISTS store_signals (
    id BIGSERIAL PRIMARY KEY,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    window_days INT NOT NULL, -- 7, 30, 90
    signal_key TEXT NOT NULL, -- 'catalog_growth', 'restock_burst', 'price_shift', 'promo_intensity'
    signal_value NUMERIC,
    signal_payload JSONB DEFAULT '{}'::JSONB,
    UNIQUE(store_id, computed_at, window_days, signal_key)
);
CREATE INDEX IF NOT EXISTS idx_signals_key ON store_signals(signal_key);
CREATE INDEX IF NOT EXISTS idx_signals_computed ON store_signals(computed_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_store ON store_signals(store_id);

-- 7. Tabla Scan Queue (Scheduler)
CREATE TABLE IF NOT EXISTS scan_queue (
    id BIGSERIAL PRIMARY KEY,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    priority INT DEFAULT 0, -- Mayor es más urgente
    next_run_at TIMESTAMPTZ DEFAULT NOW(),
    last_run_at TIMESTAMPTZ,
    fail_count INT DEFAULT 0,
    last_error TEXT,
    mode TEXT DEFAULT 'light' CHECK (mode IN ('light', 'full'))
);
CREATE INDEX IF NOT EXISTS idx_queue_next_run ON scan_queue(next_run_at);
CREATE INDEX IF NOT EXISTS idx_queue_priority ON scan_queue(priority DESC);

-- -----------------------------------------------------------------------------
-- TAREA 4: VISTAS MATERIALIZADAS (Para Vender Datos)
-- -----------------------------------------------------------------------------

-- Vista: Top Movers 7d (Tiendas creciendo en catálogo o stock)
CREATE OR REPLACE VIEW view_top_movers_7d AS
SELECT 
    s.domain,
    sig_growth.signal_value as growth_pct,
    sig_restock.signal_value as restock_intensity
FROM stores s
LEFT JOIN store_signals sig_growth ON s.id = sig_growth.store_id 
    AND sig_growth.signal_key = 'catalog_growth' 
    AND sig_growth.window_days = 7
    AND sig_growth.computed_at > NOW() - INTERVAL '24 hours'
LEFT JOIN store_signals sig_restock ON s.id = sig_restock.store_id 
    AND sig_restock.signal_key = 'restock_burst' 
    AND sig_restock.window_days = 7
    AND sig_restock.computed_at > NOW() - INTERVAL '24 hours'
WHERE (sig_growth.signal_value > 0.05 OR sig_restock.signal_value > 0.1)
ORDER BY sig_growth.signal_value DESC NULLS LAST;

-- Vista: High Ticket Promising (Precio alto, pocas promos)
CREATE OR REPLACE VIEW view_high_ticket_opportunities AS
SELECT 
    s.domain,
    snap.avg_price,
    snap.hero_score,
    sig_promo.signal_value as promo_intensity
FROM stores s
JOIN store_snapshots snap ON s.id = snap.store_id
LEFT JOIN store_signals sig_promo ON s.id = sig_promo.store_id 
    AND sig_promo.signal_key = 'promo_intensity'
    AND sig_promo.computed_at > NOW() - INTERVAL '24 hours'
WHERE snap.snapshot_at > NOW() - INTERVAL '7 days'
  AND snap.avg_price > 100 -- Umbral High Ticket configurable
  AND (sig_promo.signal_value IS NULL OR sig_promo.signal_value < 0.2) -- Menos del 20% en oferta
ORDER BY snap.avg_price DESC;
