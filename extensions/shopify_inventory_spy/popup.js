let isPro = false;
let allProducts = [];
const STRIPE_10_EURO_LINK = "https://buy.stripe.com/3cI00d07Q5kG8DA9OYdnW01";
const VERIFY_API_URL = "https://shopify-extension-pro-3ap.vercel.app/api/verify-license";

document.addEventListener('DOMContentLoaded', async () => {
  const statusText = document.getElementById('status-text');
  const infoCard = document.getElementById('info-card');
  const rankFill = document.getElementById('rank-fill');
  const rankText = document.getElementById('rank-text');
  const productCount = document.getElementById('product-count');
  const winScore = document.getElementById('win-score');
  const exportBtn = document.getElementById('export-btn');
  const upgradeBtn = document.getElementById('upgrade-btn');

  // 1. Check License & Restore Activation UI
  chrome.storage.local.get(['isPro', 'licenseKey'], (result) => {
    isPro = result.isPro || false;
    const licenseKey = result.licenseKey || '';

    if (isPro) {
      document.getElementById('pro-badge')?.classList.remove('hidden');
      document.getElementById('pro-report-area')?.classList.remove('hidden');
      document.getElementById('free-upsell-area')?.classList.add('hidden');
      document.getElementById('license-section')?.classList.add('hidden');
    }
    
    // License Activation Handler
    const activateLink = document.getElementById('activate-link');
    const licenseInput = document.getElementById('license-key');
    if (activateLink && licenseInput) {
      activateLink.onclick = (e) => {
        e.preventDefault();
        licenseInput.classList.toggle('hidden');
        licenseInput.focus();
      };

      licenseInput.onkeypress = async (e) => {
        if (e.key === 'Enter') {
          const key = licenseInput.value.trim().toUpperCase();
          try {
            const response = await fetch(`${VERIFY_API_URL}?key=${key}`);
            const result = await response.json();
            if (result.valid) {
              chrome.storage.local.set({ isPro: true, licenseKey: key }, () => {
                window.location.reload();
              });
            } else {
              alert("Invalid key.");
            }
          } catch (err) {
            alert("Connection error.");
          }
        }
      };
    }
  });

  // 2. Identify Tab & Fetch Products
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url?.startsWith('http')) {
    statusText.innerText = "Please open a store.";
    return;
  }

  const url = new URL(tab.url);
  const candidateUrls = [`${url.protocol}//${url.hostname}/products.json?limit=250`];
  
  try {
    let response;
    for (const fUrl of candidateUrls) {
      const res = await fetch(fUrl).catch(() => null);
      if (res?.ok) { response = res; break; }
    }

    if (!response) throw new Error("Shopify data not found.");
    const data = await response.json();
    allProducts = data.products;

    const metrics = calculateMetrics(allProducts);
    
    // UI Update: Stage 1 (Local Scan)
    rankFill.style.width = "30%";
    rankText.innerText = "🔍 Local Catalog Crawled...";
    productCount.innerText = allProducts.length;
    winScore.innerText = Math.min(metrics.hero_score, 10).toFixed(1) + "/10";
    
    // UI Update: Stage 2 (Network Connection)
    setTimeout(() => { 
      rankFill.style.width = "55%"; 
      rankText.innerText = "🌐 Connecting to Niche Radar..."; 
    }, 400);

    // 3. Sync & Fetch Competitors
    const syncRes = await fetch("https://shopify-extension-pro-3ap.vercel.app/api/sync", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain: url.hostname,
        data: allProducts.slice(0, 10),
        metrics: metrics
      })
    });
    const syncResult = await syncRes.json();

    // UI Update: Stage 3 (Rival Mapping)
    rankFill.style.width = "85%";
    rankText.innerText = "📊 Mapping Niche Leaders...";
    await new Promise(r => setTimeout(r, 600)); // Fake realistic data processing

    if (syncResult.ranking) {
      let pct = syncResult.ranking.rank_percentile * 100;
      rankFill.style.width = `${Math.max(pct, 5)}%`;
      rankText.innerText = `Top ${pct.toFixed(0)}% performance in ${syncResult.ranking.category || 'General'}`;
    }

    // --- RIVAL LIST LOGIC ---
    if (syncResult.ecosystem?.length > 0) {
        const ecoSection = document.createElement('div');
        ecoSection.className = 'card premium-card';
        ecoSection.style.marginTop = '15px';
        
        let ecoListHtml = syncResult.ecosystem.map(c => `
            <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:11px; border-bottom:1px solid #334155; padding-bottom:3px;">
                <span>🎯 ${c.domain}</span>
                <span style="color:${isPro ? '#10b981' : '#64748b'};">${isPro ? c.strength : '(Pro Only)'}</span>
            </div>
        `).join('');

        ecoSection.innerHTML = `
            <h4 style="color:#ec4899; margin-bottom:10px; font-size:12px;">🌍 NICHE RIVALS MONITOR</h4>
            <div id="eco-list">${ecoListHtml}</div>
        `;
        infoCard.appendChild(ecoSection);
    }

    document.getElementById('status-area').classList.add('hidden');
    infoCard.classList.remove('hidden');

    exportBtn.onclick = () => {
      chrome.storage.local.get(['licenseKey'], (r) => {
        const reportUrl = `https://shopify-extension-pro-3ap.vercel.app/api/generate-report?domain=${url.hostname}&key=${r.licenseKey}`;
        chrome.tabs.create({ url: reportUrl });
      });
    };
    
    upgradeBtn.onclick = () => {
      chrome.tabs.create({ url: "https://buy.stripe.com/3cI00d07Q5kG8DA9OYdnW01" });
    };

  } catch (err) {
    statusText.innerText = "Error: " + err.message;
  }
});

function calculateMetrics(products) {
  if (!products.length) return { avg_price: 0, hero_score: 0, discount_ratio: 0 };
  
  const prices = products.map(p => parseFloat(p.variants[0].price));
  const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
  const max = Math.max(...prices);
  
  return {
    avg_price: avg,
    hero_score: max / avg, // Simplificación: si un producto es mucho más caro, domina.
    discount_ratio: products.filter(p => p.variants[0].compare_at_price > p.variants[0].price).length / products.length
  };
}

function downloadInventoryCSV(products, hostname) {
  const headers = ["Title", "Handle", "Total Stock", "Price", "Vendor"];
  const rows = products.map(p => {
    const totalStock = p.variants.reduce((acc, v) => acc + (v.inventory_quantity || 0), 0);
    return [
      `"${p.title.replace(/"/g, '""')}"`,
      p.handle,
      totalStock,
      p.variants[0].price,
      p.vendor
    ].join(',');
  });

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `inventory_${hostname}.csv`);
  document.body.appendChild(link);
  link.click();
}
