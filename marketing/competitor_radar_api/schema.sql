-- RUN THIS IN SUPABASE SQL EDITOR

-- 1. Table for Stores
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain TEXT UNIQUE NOT NULL,
    platform TEXT DEFAULT 'shopify',
    category TEXT,
    country TEXT DEFAULT 'Spain',
    total_products INTEGER DEFAULT 0,
    avg_price FLOAT,
    hero_score FLOAT,
    discount_ratio FLOAT,
    payload JSONB,
    last_scanned TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Table for Products (Optional, for deeper analysis)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    external_id TEXT,
    title TEXT,
    handle TEXT,
    price FLOAT,
    stock_quantity INTEGER,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Table for Events (Audit Log from all extensions)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    extension_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Table for Licenses (Monetization)
CREATE TABLE IF NOT EXISTS licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_key TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    plan_type TEXT DEFAULT 'PRO_LIFETIME',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Simple Ranking Logic (View or Function)
-- This calculates how a store ranks against others in the same category
CREATE OR REPLACE VIEW competitive_ranking AS
SELECT 
    id,
    domain,
    category,
    hero_score,
    PERCENT_RANK() OVER (PARTITION BY category ORDER BY hero_score DESC) as rank_percentile
FROM stores;
