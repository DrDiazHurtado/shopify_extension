let isPro = false;
let allProducts = [];
const STRIPE_10_EURO_LINK = "https://buy.stripe.com/3cI00d07Q5kG8DA9OYdnW01";
const VERIFY_API_URL = "https://shopify-extension-pro-3ap5.vercel.app/api/verify-license";

document.addEventListener('DOMContentLoaded', async () => {
  const statusText = document.getElementById('status-text');
  const infoCard = document.getElementById('info-card');
  const rankFill = document.getElementById('rank-fill');
  const rankText = document.getElementById('rank-text');
  const productCount = document.getElementById('product-count');
  const winScore = document.getElementById('win-score');
  const exportBtn = document.getElementById('export-btn');
  const upgradeBtn = document.getElementById('upgrade-btn');

  // 1. Check License
  chrome.storage.local.get(['isPro', 'licenseKey'], (result) => {
    isPro = result.isPro || false;
    if (isPro) {
      document.getElementById('pro-badge')?.classList.remove('hidden');
      document.getElementById('upsell-card')?.classList.add('hidden');
      document.getElementById('license-section')?.classList.add('hidden');
    }
  });

  // Activation Logic
  const activateLink = document.getElementById('activate-link');
  const licenseInput = document.getElementById('license-key');
  if (activateLink && licenseInput) {
    activateLink.onclick = (e) => {
      e.preventDefault();
      licenseInput.classList.toggle('hidden');
      activateLink.classList.add('hidden');
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
              alert("PRO VERSION ACTIVATED!");
              window.location.reload();
            });
          } else {
            alert("Invalid key.");
          }
        } catch (err) {
          alert("Error connecting to server.");
        }
      }
    };
  }

  // 2. Identify Tab
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url?.startsWith('http')) {
    statusText.innerText = "Please open a store.";
    return;
  }

  const url = new URL(tab.url);
  const jsonUrl = `${url.protocol}//${url.hostname}/products.json?limit=250`;

  try {
    const response = await fetch(jsonUrl);
    if (!response.ok) throw new Error("Not a Shopify store or access blocked.");
    
    const data = await response.json();
    allProducts = data.products;

    // Calculate basic metrics
    const metrics = calculateMetrics(allProducts);
    
    // UI Update
    statusText.innerText = "Syncing with Radar...";
    productCount.innerText = allProducts.length;
    winScore.innerText = (metrics.hero_score * 10).toFixed(1) + "/10";
    
    // 3. Sync with Central Database (Using the same Vercel project)
    fetch("https://shopify-extension-pro-3ap5.vercel.app/api/sync", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        extension_id: 'inventory_spy',
        domain: url.hostname,
        data: allProducts.slice(0, 10),
        metrics: metrics
      })
    }).then(res => res.json()).then(syncResult => {
        if (syncResult.ranking) {
          const percentile = syncResult.ranking.rank_percentile * 100;
          rankFill.style.width = `${percentile}%`;
          rankText.innerText = `Top ${percentile.toFixed(0)}% in ${syncResult.ranking.category || 'General'}`;
        }
    }).catch(e => console.log("Sync error", e));

    document.getElementById('status-area').classList.add('hidden');
    infoCard.classList.remove('hidden');

    exportBtn.onclick = () => downloadInventoryCSV(allProducts, url.hostname);
    
    upgradeBtn.onclick = () => {
        chrome.tabs.create({ url: STRIPE_10_EURO_LINK });
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
