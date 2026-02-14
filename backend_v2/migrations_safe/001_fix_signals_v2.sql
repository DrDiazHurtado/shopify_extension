-- MIGRATION 001 V2: FIX SIGNALS & QUEUE STABILITY (Robust & Idempotent)
-- Objetivos: Idempotencia diaria real, limpieza segura y prevención de duplicados nulos.

-- -----------------------------------------------------------------------------
-- 1. FIX STORE_SIGNALS (Idempotencia diaria)
-- -----------------------------------------------------------------------------

-- Añadir columna computed_date para agrupar por día natural
ALTER TABLE store_signals ADD COLUMN IF NOT EXISTS computed_date DATE DEFAULT CURRENT_DATE;

-- Rellenar computed_date para filas existentes, protegiendo contra nulos
-- Usamos COALESCE para asegurar que ningún registro quede sin fecha base
UPDATE store_signals 
SET computed_date = COALESCE(date(computed_at), CURRENT_DATE) 
WHERE computed_date IS NULL;

-- Asegurar que sea NOT NULL tras el update
ALTER TABLE store_signals ALTER COLUMN computed_date SET NOT NULL;

-- Eliminar duplicados previos si existen (manteniendo el más reciente por ID)
-- Esto previene fallos al crear el constraint UNIQUE
DELETE FROM store_signals a USING store_signals b
WHERE a.id < b.id 
  AND a.store_id = b.store_id 
  AND a.computed_date = b.computed_date 
  AND a.window_days = b.window_days 
  AND a.signal_key = b.signal_key;

-- Crear constraint única para evitar inflación futura
-- DROP seguro por si ya existe alguna versión anterior
ALTER TABLE store_signals DROP CONSTRAINT IF EXISTS store_signals_store_id_computed_at_window_days_signal_key_key; 
ALTER TABLE store_signals DROP CONSTRAINT IF EXISTS unique_daily_signal;

-- CONSTRAINT DEFINITIVO: Store + Fecha + Ventana + Key = Único
ALTER TABLE store_signals ADD CONSTRAINT unique_daily_signal UNIQUE (store_id, computed_date, window_days, signal_key);

-- Índices optimizados para búsquedas por fecha y tipo de señal
CREATE INDEX IF NOT EXISTS idx_signals_date_key ON store_signals(computed_date DESC, signal_key);


-- -----------------------------------------------------------------------------
-- 2. FIX SCAN_QUEUE (Limpieza Segura)
-- -----------------------------------------------------------------------------

-- Eliminar columnas de estado que pertenecen a 'stores' (si existen)
ALTER TABLE scan_queue DROP COLUMN IF EXISTS fail_count;
ALTER TABLE scan_queue DROP COLUMN IF EXISTS last_error;

-- Asegurar índices para el Scheduler (Priority Queue pattern)
CREATE INDEX IF NOT EXISTS idx_queue_schedule ON scan_queue(next_run_at ASC, priority DESC);


-- -----------------------------------------------------------------------------
-- 3. FIX STORES (Alinear estado & Salud)
-- -----------------------------------------------------------------------------

-- Asegurar columnas de tracking de fallos en la tabla maestra
ALTER TABLE stores ADD COLUMN IF NOT EXISTS fail_count INT DEFAULT 0;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS last_error TEXT;
ALTER TABLE stores ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMPTZ; 

-- Índice para monitorizar salud del sistema (Active vs Dead/Blocked)
CREATE INDEX IF NOT EXISTS idx_stores_health ON stores(status, fail_count);
