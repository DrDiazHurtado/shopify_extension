let isPro = false;
let allProducts = [];

const log = (msg) => {
  console.log(`[ShopifyInsider] ${msg}`);
};

document.addEventListener('DOMContentLoaded', async () => {
  const statusText = document.getElementById('status-text');
  const infoCard = document.getElementById('info-card');
  const errorCard = document.getElementById('error-card');
  const productCount = document.getElementById('product-count');
  const exportBtn = document.getElementById('export-btn');
  const statusArea = document.getElementById('status-area');
  const proBadge = document.getElementById('pro-badge');
  const upgradeBtn = document.getElementById('upgrade-btn');
  const errorMsgText = errorCard ? errorCard.querySelector('p') : null;

  log("Popup initialized");

  // Check state
  chrome.storage.local.get(['isPro'], (result) => {
    isPro = result.isPro || false;
    log(`Pro status: ${isPro}`);
    if (isPro) {
      proBadge?.classList.remove('hidden');
      upgradeBtn?.classList.add('hidden');
    }
  });

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (!tab || !tab.url || !tab.url.startsWith('http')) {
    if (statusText) statusText.innerText = "Please open a store website.";
    return;
  }

  const url = new URL(tab.url);
  const productsUrl = `${url.origin}/products.json?limit=250`;

  try {
    if (statusText) statusText.innerText = "Scanning for products...";
    
    const response = await fetch(productsUrl);
    log(`Fetch status: ${response.status}`);
    
    if (response.ok) {
      const data = await response.json();
      if (data.products && data.products.length > 0) {
        allProducts = data.products;
        log(`Found ${allProducts.length} products`);
        
        statusArea?.classList.add('hidden');
        infoCard?.classList.remove('hidden');
        
        const displayCount = isPro ? allProducts.length : Math.min(allProducts.length, 50);
        if (productCount) productCount.innerText = displayCount;

        if (!isPro && allProducts.length > 50) {
          const limitMsgId = 'limit-msg';
          if (!document.getElementById(limitMsgId)) {
            const limitMsg = document.createElement('p');
            limitMsg.id = limitMsgId;
            limitMsg.style.cssText = 'font-size: 10px; color: #ff4081; margin: 10px 0; font-weight: bold;';
            limitMsg.innerText = `PREMIUM REVELATION: +${allProducts.length - 50} more items hidden.`;
            infoCard?.insertBefore(limitMsg, exportBtn);
          }
        }

        if (exportBtn) {
          exportBtn.onclick = () => {
            const productsToExport = isPro ? allProducts : allProducts.slice(0, 50);
            downloadCSV(productsToExport, url.hostname);
          };
        }

        if (upgradeBtn) {
          upgradeBtn.onclick = () => {
            log("Redirecting to Stripe...");
            const checkoutUrl = "https://buy.stripe.com/14A9AN3k26oKg622mwdnW00";
            chrome.tabs.create({ url: checkoutUrl });
          };
        }

        const activateLink = document.getElementById('activate-link');
        const licenseInput = document.getElementById('license-key');

        if (activateLink && licenseInput) {
          activateLink.onclick = (e) => {
            e.preventDefault();
            licenseInput.classList.toggle('hidden');
            activateLink.classList.add('hidden');
            licenseInput.focus();
          };

          licenseInput.onkeypress = (e) => {
            if (e.key === 'Enter') {
              const key = licenseInput.value.trim();
              if (key.length > 5) { 
                log("Activating License...");
                chrome.storage.local.set({ isPro: true, licenseKey: key }, () => {
                  alert("Success! Premium Features Unlocked.");
                  window.location.reload();
                });
              } else {
                alert("Invalid License Key.");
              }
            }
          };
        }
      } else {
        throw new Error("No products found in this store.");
      }
    } else {
      if (response.status === 404) {
        throw new Error("This doesn't seem to be a Shopify store.");
      } else {
        throw new Error(`Store responded with status ${response.status}`);
      }
    }
  } catch (err) {
    log(`Error: ${err.message}`);
    statusArea?.classList.add('hidden');
    errorCard?.classList.remove('hidden');
    if (errorMsgText) errorMsgText.innerText = err.message;
  }
});

function downloadCSV(products, hostname) {
  const headers = ["Title", "Handle", "Created At", "Vendor", "Product Type", "Price", "Compare At Price", "Image URL", "Rank"];
  const rows = products.map((p, index) => {
    const variant = (p.variants && p.variants[0]) || {};
    const image = (p.images && p.images[0]) || {};
    return [
      `"${(p.title || '').replace(/"/g, '""')}"`,
      p.handle || '',
      p.created_at || '',
      p.vendor || '',
      p.product_type || '',
      variant.price || '0',
      variant.compare_at_price || '',
      `"${image.src || ''}"`,
      index + 1
    ].join(',');
  });

  const csvContent = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `shopify_insider_${hostname.replace(/\./g, '_')}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
