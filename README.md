# 🚀 Shopify Insider: Competitor Intelligence MVP

Professional Chrome Extension designed for e-commerce entrepreneurs to spy on Shopify competitors, reveal best-selling products, and export data instantly.

## 📦 Project Structure
- `/shopify_insider_ext`: Core Chrome Extension (Manifest V3).
- `/landing_page`: Premium Marketing Website (Built with HTML/Vanilla CSS).
- `shopify_insider_final_v3.zip`: Production-ready package for Chrome Web Store.

## ✨ Features
- **One-Click Export**: Extract up to 250 products to CSV from any Shopify store.
- **Best-Seller Ranking**: Intelligent detection of top-performing products.
- **Monetization Ready**: Integrated "Pro" gate with Stripe Lifetime billing logic.
- **Privacy First**: Uses `activeTab` permissions for fast review and user trust.

## 🛠️ Setup & Deployment
### Extension
1. Load `shopify_insider_ext` in Chrome via `Developer Mode`.
2. For production, upload the `.zip` to Chrome Web Store Developer Console.

### Landing Page
- Hosted on Vercel/GitHub Pages.
- Integrated with Stripe Payment Links for the 25€ Lifetime Deal.

## 🔐 Licensing
- Basic Version: Limited to 50 products per export.
- Pro Version: Unlimited products + Best Seller ranking.
- Activation: License key stored in `chrome.storage.local`.

---
*Developed as part of the Opportunity Radar ecosystem.*
