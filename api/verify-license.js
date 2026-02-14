// /api/verify-license.js
// Vercel Serverless Function to verify a license key against Supabase

export default async function handler(req, res) {
  // Configurar CORS para permitir que la extensión haga peticiones
  res.setHeader('Access-Control-Allow-Origin', '*'); 
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { key } = req.query;

  if (!key) {
    return res.status(400).json({ valid: false, message: "No key provided" });
  }

  const SUPABASE_URL = process.env.SUPABASE_URL || "https://cbffcvgecksspyhnqpqd.supabase.co";
  const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!SUPABASE_KEY) {
    return res.status(500).json({ valid: false, error: "Critical configuration missing: SUPABASE_SERVICE_ROLE_KEY is not defined in Vercel settings." });
  }

  try {
    const response = await fetch(`${SUPABASE_URL}/rest/v1/licenses?license_key=eq.${key}&is_active=eq.true`, {
      method: 'GET',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (data && data.length > 0) {
      return res.status(200).json({ 
        valid: true, 
        plan: data[0].plan_type,
        message: "License active" 
      });
    } else {
      return res.status(200).json({ 
        valid: false, 
        message: "Invalid or inactive license key" 
      });
    }

  } catch (error) {
    return res.status(500).json({ valid: false, error: error.message });
  }
}
