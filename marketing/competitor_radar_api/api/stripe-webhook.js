// /api/stripe-webhook.js
// Vercel Serverless Function to handle Stripe payments and create licenses

import crypto from 'crypto';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method Not Allowed' });

  // 1. Validar que la petición viene de Stripe (Opcional pero recomendado con STRIPE_WEBHOOK_SECRET)
  // Por ahora lo haremos simple, pero en producción deberías usar la librería de Stripe para verificar el signature.
  const event = req.body;

  // Solo nos interesa cuando el pago se ha completado con éxito
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const email = session.customer_details.email;
    
    // 2. Generar una clave única
    const randomBuffer = crypto.randomBytes(4).toString('hex').toUpperCase();
    const licenseKey = `INSIDER-${randomBuffer}-${Date.now().toString().slice(-4)}`;

    const SUPABASE_URL = process.env.SUPABASE_URL;
    const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

    try {
      // 3. Guardar en Supabase
      const response = await fetch(`${SUPABASE_URL}/rest/v1/licenses`, {
        method: 'POST',
        headers: {
          'apikey': SUPABASE_KEY,
          'Authorization': `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          license_key: licenseKey,
          email: email,
          plan_type: 'PRO_LIFETIME',
          is_active: true
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error saving license to Supabase:", errorText);
        return res.status(500).json({ error: "Failed to save license" });
      }

      console.log(`License created for ${email}: ${licenseKey}`);

      // 4. (Opcional) Aquí podrías enviar un email al usuario usando Resend o SendGrid.
      // Por ahora, el usuario verá que su cuenta se activa si usa su email o tú se la envías manualmente.
      
      return res.status(200).json({ received: true, licenseCreated: licenseKey });

    } catch (error) {
      console.error("Webhook Error:", error.message);
      return res.status(500).json({ error: error.message });
    }
  }

  return res.status(200).json({ received: true });
}
