import { createClient } from '@supabase/supabase-js';

// --- CONFIGURATION ---
const SUPABASE_URL = process.env.SUPABASE_URL || '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

interface StoreSignal {
  store_id: string;
  signal_key: string;
  value: number;
  window_days: number;
}

// --- MAIN SIGNAL COMPUTE JOB ---
export async function computeSignalsJob() {
  console.log("🧠 Starting Signal Computation Engine...");
  
  // 1. Fetch stores active in last 24h
  const { data: stores, error } = await supabase
    .from('stores')
    .select('id, domain')
    .eq('status', 'active'); // Or check last_seen_at > 24h ago

  if (error) {
    console.error("Error fetching stores:", error);
    return;
  }

  // 2. Process store by store (or batch for performance)
  for (const store of stores || []) {
    await computeStoreSignals(store.id);
  }
  
  console.log("✅ Signal Computation Complete.");
}

async function computeStoreSignals(storeId: string) {
  // A. Fetch Snapshots (Current vs 7d ago vs 30d ago)
  const now = new Date();
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 3600 * 1000);
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 3600 * 1000);

  const { data: snapshots } = await supabase
    .from('store_snapshots')
    .select('*')
    .eq('store_id', storeId)
    .order('snapshot_at', { ascending: false })
    .limit(30); // Get enough history

  if (!snapshots || snapshots.length < 2) return; // Need at least 2 points

  const latest = snapshots[0];
  const prev7d = snapshots.find(s => new Date(s.snapshot_at) <= sevenDaysAgo);
  const prev30d = snapshots.find(s => new Date(s.snapshot_at) <= thirtyDaysAgo);

  // --- SIGNAL 1: CATALOG GROWTH (7d) ---
  if (prev7d) {
    const growth = (latest.total_products - prev7d.total_products) / (prev7d.total_products || 1);
    await saveSignal({
      store_id: storeId,
      signal_key: 'catalog_growth',
      window_days: 7,
      value: parseFloat(growth.toFixed(4))
    });
  }

  // --- SIGNAL 2: PROMO INTENSITY (Current) ---
  // Using snapshot.discount_ratio directly or recomputing from variants
  if (latest.discount_ratio !== undefined) {
    await saveSignal({
      store_id: storeId,
      signal_key: 'promo_intensity',
      window_days: 1, // "Current" state
      value: latest.discount_ratio
    });
  }

  // --- SIGNAL 3: RESTOCK BURST (Requires Variant Snapshots) ---
  // If we have granular variant history, we query:
  // SELECT count(*) FROM variant_snapshots WHERE available was false AND became true in window
  // For MVP/Light scans, we might infer from 'total_products' jumps or specialized logic
  
  // (Pseudocode for granular check)
  // const restocks = await getRestockCount(storeId, 7);
  // await saveSignal({ ... 'restock_burst', value: restocks });

  // --- SIGNAL 4: PRICE SHIFT (30d Median) ---
  if (prev30d) {
    const shift = (latest.avg_price - prev30d.avg_price);
    await saveSignal({
      store_id: storeId,
      signal_key: 'price_shift_avg',
      window_days: 30,
      value: parseFloat(shift.toFixed(2))
    });
  }
}

async function saveSignal(signal: StoreSignal) {
  const { error } = await supabase
    .from('store_signals')
    .upsert({
      store_id: signal.store_id,
      computed_at: new Date().toISOString(),
      window_days: signal.window_days,
      signal_key: signal.signal_key,
      signal_value: signal.value
    }, { onConflict: 'store_id, computed_at, window_days, signal_key' }); // Ensure unique constraint matches schema

  if (error) console.error(`Failed to save signal ${signal.signal_key} for ${signal.store_id}:`, error);
}

// Start
if (require.main === module) {
  computeSignalsJob();
}
