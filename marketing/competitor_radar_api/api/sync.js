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

    // 3. Get Ranking (Simple mock based on hero_score)
    // In a real app, you'd query the 'competitive_ranking' view
    const rankResponse = await fetch(`${SUPABASE_URL}/rest/v1/competitive_ranking?domain=eq.${domain}`, {
        headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` }
    });
    const rankData = await rankResponse.json();

    return res.status(200).json({ 
      success: true, 
      ranking: rankData[0] || { rank_percentile: 0.5, category: 'General' } 
    });

  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
