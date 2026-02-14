import { createClient } from '@supabase/supabase-js';
import axios from 'axios';
import { sleep } from './utils'; // Assumed utility

// --- CONFIGURATION ---
const SUPABASE_URL = process.env.SUPABASE_URL || '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || ''; // Must be service role for backend
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const RATE_LIMIT_DELAY = 1000; // 1 second between requests per domain
const MAX_CONCURRENT_SCANS = 5;

// --- TYPES ---
interface ScanJob {
  id: number;
  store_id: string;
  domain: string;
  mode: 'light' | 'full';
}

// --- MAIN LOOP ---
async function startScanner() {
  console.log("🚀 Starting Shopify Intelligent Scanner...");

  while (true) {
    // 1. Fetch Job from Queue
    const { data: jobs, error } = await supabase
      .from('scan_queue')
      .select('*, stores(domain)')
      .lte('next_run_at', new Date().toISOString())
      .order('priority', { ascending: false })
      .limit(MAX_CONCURRENT_SCANS);

    if (error) {
      console.error("Queue Fetch Error:", error);
      await sleep(5000);
      continue;
    }

    if (!jobs || jobs.length === 0) {
      console.log("💤 No jobs due. Waiting...");
      await sleep(10000);
      continue;
    }

    // 2. Process Jobs Concurrently
    await Promise.all(jobs.map(job => processJob({
      id: job.id,
      store_id: job.store_id,
      domain: job.stores.domain, // Supabase join syntax might vary, pseudocode
      mode: job.mode
    })));
  }
}

// --- JOB PROCESSOR ---
async function processJob(job: ScanJob) {
  const startTime = Date.now();
  console.log(`🔍 Scanning ${job.domain} [${job.mode}]`);

  try {
    // A. FETCH PRODUCTS
    let products = [];
    if (job.mode === 'light') {
      // Light Scan: Page 1 Only (250 items)
      products = await fetchShopifyProducts(job.domain, 1, 250);
      
      // Check heuristics to upgrade to full scan?
      // implementation derived from TAREA 2 logic
    } else {
      // Full Scan: Pagination Loop
      products = await fetchAllProducts(job.domain);
    }

    // B. COMPUTE METRICS
    const snapshot = computeSnapshot(products);
    
    // C. UPSERT DATA
    await saveSnapshot(job.store_id, snapshot);
    if (job.mode === 'full') {
      await saveProductsAndVariants(job.store_id, products);
    }

    // D. UPDATE QUEUE
    await supabase.from('scan_queue').update({
      last_run_at: new Date().toISOString(),
      next_run_at: calculateNextRun(job.mode, snapshot), // e.g. 24h or 7d
      last_error: null,
      fail_count: 0
    }).eq('id', job.id);

    console.log(`✅ Finished ${job.domain} in ${(Date.now() - startTime) / 1000}s`);

  } catch (err: any) {
    console.error(`❌ Failed ${job.domain}: ${err.message}`);
    
    // Backoff Logic
    await supabase.from('scan_queue').update({
      last_error: err.message,
      fail_count: 1, // increment in real DB
      next_run_at: new Date(Date.now() + 3600 * 1000).toISOString() // Retry in 1h
    }).eq('id', job.id);
  }
}

// --- FETCHING LOGIC ---
async function fetchShopifyProducts(domain: string, page: number, limit: number) {
  const url = `https://${domain}/products.json?limit=${limit}&page=${page}`;
  try {
    const res = await axios.get(url, {
      headers: { 'User-Agent': 'ShopifyRadar/1.0 (Research)' },
      timeout: 10000
    });
    return res.data.products || [];
  } catch (err: any) {
    if (err.response?.status === 429) throw new Error("RateLimit");
    if (err.response?.status === 404) throw new Error("NotFound");
    throw err;
  }
}

async function fetchAllProducts(domain: string) {
  let allProducts = [];
  let page = 1;
  const limit = 250;

  while (true) {
    const pageProducts = await fetchShopifyProducts(domain, page, limit);
    if (pageProducts.length === 0) break;
    
    allProducts.push(...pageProducts);
    if (pageProducts.length < limit) break; // End of list
    
    page++;
    await sleep(RATE_LIMIT_DELAY); // Be polite
  }
  return allProducts;
}

// --- STORAGE LOGIC ---
async function saveSnapshot(storeId: string, snapshot: any) {
  const { error } = await supabase.from('store_snapshots').insert({
    store_id: storeId,
    snapshot_at: new Date().toISOString(),
    ...snapshot
  });
  if (error) throw error;
}

async function saveProductsAndVariants(storeId: string, products: any[]) {
  // Batch insert implementation (simplified)
  // Real implementation would map products -> Supabase structure
  // and use .upsert() bulk
}

// --- METRICS LOGIC ---
function computeSnapshot(products: any[]) {
  if (!products.length) return {};
  
  let totalPrice = 0;
  let vendorCounts = new Set();
  let discountCount = 0;
  let totalVariants = 0;

  products.forEach(p => {
    vendorCounts.add(p.vendor);
    p.variants.forEach((v: any) => {
      totalVariants++;
      totalPrice += parseFloat(v.price || 0);
      if (v.compare_at_price && parseFloat(v.compare_at_price) > parseFloat(v.price)) {
        discountCount++;
      }
    });
  });

  return {
    total_products: products.length,
    avg_price: totalVariants ? (totalPrice / totalVariants).toFixed(2) : 0,
    vendor_count: vendorCounts.size,
    discount_ratio: totalVariants ? (discountCount / totalVariants).toFixed(2) : 0,
    // hero_score logic...
  };
}

function calculateNextRun(mode: string, snapshot: any) {
    // Dynamic Scheduling Policy
    // If 'hot' store (high changes), scan sooner
    return new Date(Date.now() + 24 * 3600 * 1000).toISOString(); // Default 24h
}

// Start
if (require.main === module) {
  startScanner();
}
