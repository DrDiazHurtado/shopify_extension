// /api/sync.js
// Vercel Serverless Function to receive data from any extension

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method Not Allowed' });

  const { extension_id, domain, data, metrics } = req.body;
  const SUPABASE_URL = process.env.SUPABASE_URL;
  const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

  try {
    // 1. Upsert Store Data
    const storeResponse = await fetch(`${SUPABASE_URL}/rest/v1/stores`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation,resolution=merge-duplicates'
      },
      body: JSON.stringify({
        domain: domain,
        total_products: data.length,
        avg_price: metrics.avg_price,
        hero_score: metrics.hero_score,
        discount_ratio: metrics.discount_ratio,
        last_scanned: new Date().toISOString()
      })
    });

    const storeData = await storeResponse.json();
    const storeId = storeData[0]?.id;

    // 2. Log Event
    await fetch(`${SUPABASE_URL}/rest/v1/events`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        store_id: storeId,
        extension_id: extension_id,
        event_type: 'sync_data',
        payload: { products_count: data.length, metrics }
      })
    });

    // 3. Get Ranking and Ecosystem (Winner Radar)
    const rankResponse = await fetch(`${SUPABASE_URL}/rest/v1/stores?domain=neq.${domain}&order=hero_score.desc&limit=5`, {
        headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` }
    });
    const competitors = await rankResponse.json();

    // 4. Get Current Store Rank Percentile
    const allStoresCountRes = await fetch(`${SUPABASE_URL}/rest/v1/stores?select=count`, {
        headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}`, 'Prefer': 'count=exact' }
    });
    const totalStores = parseInt(allStoresCountRes.headers.get('content-range')?.split('/')[1] || "1");
    
    // Simplified rank calculation for the demo
    const rankData = await fetch(`${SUPABASE_URL}/rest/v1/stores?domain=eq.${domain}`, {
        headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` }
    });
    const currentStore = await rankData.json();

    return res.status(200).json({ 
      success: true, 
      ranking: {
          rank_percentile: currentStore[0]?.hero_score > 0.8 ? 0.05 : 0.5,
          category: 'E-commerce Standard'
      },
      ecosystem: competitors.map(c => ({
          domain: c.domain,
          score: c.hero_score,
          strength: c.hero_score > 1.5 ? 'Elite' : 'High Performance'
      })) 
    });

  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
