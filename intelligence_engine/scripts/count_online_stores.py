import requests

SUPABASE_URL = "https://cbffcvgecksspyhnqpqd.supabase.co"
SUPABASE_KEY = "sb_publishable_jwciMUPWBhpORNq5Ffk2Vw_WsNC3iId"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

# Pedimos el conteo exacto de la tabla stores
r = requests.get(f"{SUPABASE_URL}/rest/v1/stores?select=count", headers=headers)
if r.status_code == 200:
    count = r.json()[0]['count']
    print(f"Total stores in Supabase: {count}")
else:
    print(f"Error: {r.status_code} - {r.text}")
