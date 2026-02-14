-- MIGRATION 001: FIX SIGNALS & QUEUE STABILITY
-- Mantiene compatibilidad, añade constraints idempotentes y limpieza.

-- 1. FIX STORE_SIGNALS (Idempotencia diaria)
-- Añadir columna computed_date para agrupar por día natural
ALTER TABLE store_signals ADD COLUMN IF NOT EXISTS computed_date DATE DEFAULT CURRENT_DATE;

-- Rellenar computed_date para filas existentes
UPDATE store_signals SET computed_date = date(computed_at) WHERE computed_date IS NULL;

-- Asegurar que sea NOT NULL tras el update
ALTER TABLE store_signals ALTER COLUMN computed_date SET NOT NULL;

-- Eliminar duplicados previos si existen (manteniendo el más reciente)
DELETE FROM store_signals a USING store_signals b
WHERE a.id < b.id 
  AND a.store_id = b.store_id 
  AND a.computed_date = b.computed_date 
  AND a.window_days = b.window_days 
  AND a.signal_key = b.signal_key;

-- Crear constraint única para evitar inflación futura
ALTER TABLE store_signals DROP CONSTRAINT IF EXISTS store_signals_store_id_computed_at_window_days_signal_key_key; -- Drop old unique
ALTER TABLE store_signals ADD CONSTRAINT unique_daily_signal UNIQUE (store_id, computed_date, window_days, signal_key);

-- Índices optimizados
CREATE INDEX IF NOT EXISTS idx_signals_date_key ON store_signals(computed_date DESC, signal_key);


-- 2. FIX SCAN_QUEUE (Limpieza y Separación de Responsabilidades)
-- Eliminar columnas de estado que pertenecen a 'stores' (si existen)
-- Nota: En Postgres DROP COLUMN IF EXISTS es seguro.
ALTER TABLE scan_queue DROP COLUMN IF EXISTS fail_count;
ALTER TABLE scan_queue DROP COLUMN IF EXISTS last_error;

-- Asegurar índices para el Scheduler
CREATE INDEX IF NOT EXISTS idx_queue_schedule ON scan_queue(next_run_at ASC, priority DESC);


-- 3. FIX STORES (Alinear estado)
-- Asegurar columnas de tracking de fallos
ALTER TABLE stores ADD COLUMN IF NOT EXISTS fail_count INT DEFAULT 0;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS last_error TEXT;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMPTZ; -- Diferente de last_seen (que puede ser intento fallido)

-- Índice para ver salud del sistema
CREATE INDEX IF NOT EXISTS idx_stores_health ON stores(status, fail_count);
