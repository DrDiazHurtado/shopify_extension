# 🚀 Shopify Extension Ecosystem - Project Architecture

Welcome to the **Shopify Insider & Inventory Spy** project. This repository is an all-in-one ecosystem designed to mine, store, and monetize Shopify market intelligence.

## 🏗️ Project Pillars

The project is divided into 4 main blocks:

### 1. 📂 `extensions/` (The Monetization Tools)
Chrome Extensions that users download and pay for.
- **`shopify_insider_ext/`**: Focuses on mass exporting product data. (LTD 25€).
- **`shopify_inventory_spy/`**: Focuses on real-time stock and competitor intelligence. (10€/report).

### 2. 🌐 `marketing/` (The Sales Funnel)
Hosted on Vercel, connected to Stripe and GitHub.
- **`landing_page/`**: Contains the main website (`index.html`), the spy tool page (`inventory-spy.html`), and the API endpoints.
- **`api/`**: Serverless functions handling Stripe Webhooks, License Verification, and PDF Generation.

### 3. 🧠 `intelligence_engine/` (The Data Lab)
Python-based tools to find the "Goldmines" before anyone else.
- **`shopify_study/`**: The core scanner and database management.
- **`sync_local_to_cloud.py`**: The bridge that sends your local "Gold" to the online database.
- **`radar.db` / `database.db`**: Local SQLite stores with thousands of mapped stores.

### 4. 📊 `analysis_scripts/` (Intelligence Tools)
Standalone scripts used to find opportunities in the local database.
- `find_active_winners.py`: Detects stores with recent growth.
- `find_niche_goldmine.py`: Identifies high-potential categories.

---

## 🛠️ Typical Workflow

1. **Mine:** Run `python3 shopify_study/massive_scanner.py` to fill your local database.
2. **Sync:** Run `python3 sync_local_to_cloud.py` to upload insights to Supabase.
3. **Sell:** Users buy reports on the landing page or extension.
4. **Deliver:** Vercel generates a PDF based on the synced cloud data.

---

## ⚠️ Legal & Security
- **No Refund Policy:** Clearly stated in `privacy.html`.
- **Infrastructure:** API keys are hidden in Vercel environment variables.
- **Database:** Local DBs are your proprietary asset; Cloud DB only contains the "processed gold".
