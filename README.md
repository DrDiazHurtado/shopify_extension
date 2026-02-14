# 🚀 Shopify SaaS Master Dashboard

This is the central control center for the **Shopify Insider** and **Inventory Spy** ecosystem. Use this as your landing page for every coding session.

## 🔗 Infrastructure & Links
| Service | Purpose | URL / Status |
| :--- | :--- | :--- |
| **Vercel Production** | Public Website | [shopify-extension-pro-3ap.vercel.app](https://shopify-extension-pro-3ap.vercel.app/) |
| **Stripe (Insider)** | LTD 25€ Payment | [Checkout Link](https://buy.stripe.com/14A9AN3k26oKg622mwdnW00) |
| **Stripe (Spy)** | Report 10€ Payment | [Checkout Link](https://buy.stripe.com/3cI00d07Q5kG8DA9OYdnW01) |
| **Supabase DB** | Cloud Database | `cbffcvgecksspyhnqpqd.supabase.co` |
| **GitHub Repo** | Marketing Source | `DrDiazHurtado/shopify_extension_pro` |

---

## 🏗️ Project Structure (The Brain Map)

### 1. 📂 `extensions/` (Frontend Tools)
*   `shopify_insider_ext/`: Tool for mass product exporting. Includes `manifest.json` and `popup.js`.
*   `shopify_inventory_spy/`: Tool for stock analysis and PDF reports.

### 2. 📂 `marketing/` (Revenue & Logic)
*   `landing_page/`: The HTML/CSS for the sales sites.
    *   `index.html`: Home for Insider Exporter (25€).
    *   `inventory-spy.html`: Home for Inventory Spy (10€).
    *   `api/`: **CRITICAL** - Serverless functions (Webhooks, Verify, PDF Generator).
*   `assets/`: Icons, promotional images, and ready-to-upload ZIP files.

### 3. 📂 `intelligence_engine/` (Backoffice Intelligence)
*   `shopify_study/`: Python crawler used to build your proprietary market database.
*   `databases/`: Local `radar.db` and `database.db`. **This is your real gold.**
*   `scripts/`: Automation tools (`sync_local_to_cloud.py`) to feed the Cloud DB.

### 4. 📂 `analysis_scripts/` (Data Mining)
*   Specific Python scripts to find "Hidden Winners" and "Niche Goldmines" within your local data.

---

## 🛠️ Operational Workflow (Next Step Guide)

### 📊 To update the "Market Cloud" with new stores:
1.  **Mine:** `PYTHONPATH=. python3 shopify_study/massive_scanner.py` (fills local DB).
2.  **Sync:** `python3 intelligence_engine/scripts/sync_local_to_cloud.py` (uploads to Supabase).
3.  **Deploy:** Changes in `marketing/` are auto-deployed to Vercel via GitHub Sync.

### ⚖️ Legal & Security
*   **Refund Policy:** Explicitly "No Refunds" due to Shopify API changes (Fixed in `privacy.html`).
*   **Cross-Marketing:** Both landing pages now link to each other to increase AOV.
*   **Reports:** PDF generation now includes **Top 5 Products** and **Sales Velocity** insights.

---

## 📋 Environment Variables (Vercel)
Ensure these are set in Vercel for the API to work:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
