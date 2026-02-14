===================================================
🚀 SHOPIFY INTELLIGENCE SUITE - DISTRIBUTION GUIDE
===================================================

This package contains two advanced browser extensions for Shopify store analysis and business intelligence. 

---------------------------------------------------
1. EXTENSIONS OVERVIEW
---------------------------------------------------

📊 EXTENSION 1: Shopify Insider (The Exporter)
-----------------------------------------------
Folder: shopify_insider_ext
-----------------------------------------------
Description: A powerful tool designed for bulk product data extraction.
Key Features:
- Scrapes up to 250 products per page in one click.
- Exports a clean CSV file directly compatible with Shopify Import.
- Reveals "Hidden Fields" like tags, handles, and vendor names usually invisible to the public.
- Sorts products by "Best Selling" algorithm to reveal top performers.

Target Customer: 
- Dropshippers cloning winning stores.
- Analysts needing raw data for Excel/Google Sheets.
- Price monitoring services.

🕵️ EXTENSION 2: Inventory Spy (The Strategist)
-----------------------------------------------
Folder: shopify_inventory_spy
-----------------------------------------------
Description: A competitive intelligence radar that maps the market ecosystem.
Key Features:
- Real-time "Niche Authority Score" (0-10).
- Automatic detection of top 5 direct competitors in the same niche.
- "Hero Product" identification (finds the product driving the revenue).
- Generates a premium Strategic PDF Report for clients.
- Filters out low-quality stores (<10 products) to ensure high-value comparisons.

Target Customer:
- Serious brand owners looking for market positioning.
- Agencies providing audit reports to clients.
- Data-driven marketers.

---------------------------------------------------
2. BUSINESS MODEL & PRICING
---------------------------------------------------

The suite operates on a tiered "Freemium + Micro-Transaction" model to maximize conversion.

Tier 1: Free (Lead Magnet)
--------------------------
- Users can install both extensions for free.
- Insider: Basic export limited (or full - depends on current strategy).
- Spy: Shows Niche Rank and Competitor Domains, but hides product details and PDF access.

Tier 2: Inventory Spy Unlock (The "Impulse Buy")
------------------------------------------------
- Price: 3€ / Store
- Trigger: User clicks to unlock the "Hidden" competitor data or download the PDF.
- Value Proposition: Getting a full strategic audit for the price of a coffee.
- Payment Flow: Direct Stripe Link -> Key Generation.

Tier 3: Shopify Insider License (The "Pro Tool")
------------------------------------------------
- Price: 25€ / Lifetime
- Trigger: Unlimited bulk exports and advanced CSV formatting.
- Target: Power users who scrape daily.

Tier 4: Elite Radar Bundle
--------------------------
- Price: 49€ / Lifetime
- Includes: Both extensions unlocked forever + Future updates.

---------------------------------------------------
3. TECHNICAL INFRASTRUCTURE
---------------------------------------------------

This ecosystem is built on a modern, serverless stack for near-zero maintenance costs.

Backend & Hosting: Vercel
-------------------------
- Role: Hosts the API endpoints and the Landing Page.
- Functions:
  - `api/sync.js`: Receives store data, classifies niche, and syncs to DB.
  - `api/generate-report.js`: Creates the PDF strategic report dynamically.
  - `api/verify-license.js`: Checks license keys.

Database: Supabase (PostgreSQL)
-------------------------------
- Role: The "Brain" of the operation.
- Tables:
  - `stores`: Stores millions of scanned products and store metrics.
  - `licenses`: Manages user access keys and payment status.
- Sync: Automatically updated by the `auto_pulse.py` background script (runs on local server or cloud worker).

Payments: Stripe
----------------
- Role: Handles all transactions.
- Integration: Direct payment links that webhook into Supabase to generate/activate keys.

---------------------------------------------------
4. INSTALLATION GUIDE (For Chrome/Edge/Brave)
---------------------------------------------------

1. Unzip this package.
2. Open your browser and go to `chrome://extensions`.
3. Enable "Developer Mode" (toggle at the top right).
4. Click "Load Unpacked" (top left).
5. Select the folder `shopify_insider_ext` to install the Exporter.
6. Repeat step 4 and select `shopify_inventory_spy` to install the Spy tool.

You are now ready to spy on any Shopify store!

---------------------------------------------------
5. HOW TO MAKE MONEY
---------------------------------------------------

Strategy A: Direct Sales (B2C)
- Drive traffic to the Landing Page (included in repo).
- Target Facebook/TikTok Ads at "Dropshipping" interests.
- Sell the 3€ reports as an impulse buy and upsell the 25€ tool.

Strategy B: Agency Audit (B2B)
- Use "Inventory Spy" to generate PDF reports for prospective clients.
- Send them the report: "I analyzed your store and found 5 competitors beating you..."
- Sell them your marketing services to fix it.

Strategy C: Data Selling
- The system automatically builds a massive database of products and stores (via `auto_pulse.py`).
- Sell acces to this database as a "Winning Product Finder" SaaS in the future.

===================================================
Generated by Opportunity Radar AI
===================================================
