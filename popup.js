let isPro = false;
let allProducts = [];
const STRIPE_CHECKOUT_URL = "https://buy.stripe.com/14A9AN3k26oKg622mwdnW00";

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

  // 1. Cargar estado de Licencia
  chrome.storage.local.get(['isPro', 'licenseKey'], (result) => {
    isPro = result.isPro || false;
    if (isPro) {
      log("Premium License Active");
      proBadge?.classList.remove('hidden');
      upgradeBtn?.classList.add('hidden');
      if(document.getElementById('license-section')) {
          document.getElementById('license-section').style.display = 'none';
      }
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
    if (statusText) statusText.innerText = "Scanning Competitor Data...";
    
    const response = await fetch(productsUrl);
    
    if (response.ok) {
      const data = await response.json();
      if (data.products && data.products.length > 0) {
        allProducts = data.products;
        statusArea?.classList.add('hidden');
        infoCard?.classList.remove('hidden');
        
        // Lógica de Gated Content (15 productos)
        const displayCount = isPro ? allProducts.length : Math.min(allProducts.length, 15);
        if (productCount) productCount.innerText = displayCount;

        if (!isPro && allProducts.length > 15) {
          const limitMsgId = 'limit-msg';
          if (!document.getElementById(limitMsgId)) {
            const limitMsg = document.createElement('p');
            limitMsg.id = limitMsgId;
            limitMsg.className = "premium-alert";
            limitMsg.style.cssText = 'font-size: 11px; color: #f43f5e; margin: 10px 0; font-weight: 800; text-align: center; border: 1px dashed #f43f5e; padding: 5px; border-radius: 4px;';
            limitMsg.innerText = `PRO VERSION REQUIRED: ${allProducts.length - 15} more products hidden.`;
            infoCard?.insertBefore(limitMsg, exportBtn);
          }
        }

        if (exportBtn) {
          exportBtn.onclick = () => {
            const productsToExport = isPro ? allProducts : allProducts.slice(0, 15);
            downloadCSV(productsToExport, url.hostname);
          };
        }

        if (upgradeBtn) {
          upgradeBtn.onclick = () => {
            chrome.tabs.create({ url: STRIPE_CHECKOUT_URL });
          };
        }

        // Sistema de Activación "Adulto"
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
              
              // Simulación de validación profesional
              // En el futuro esto hará un: fetch('tuservidor.com/verify?key=' + key)
              if (key.startsWith("INSIDER-") && key.length > 12) { 
                log("Verifying License Key...");
                chrome.storage.local.set({ isPro: true, licenseKey: key }, () => {
                  alert("INSIDER PRO ACTIVATED SUCCESSFULY!");
                  window.location.reload();
                });
              } else {
                alert("Invalid License Key format. Please use the key sent to your email.");
              }
            }
          };
        }
      } else {
        throw new Error("No items found. Ensure this is a Shopify store.");
      }
    } else {
      throw new Error("Could not access store data. Try refreshing the page.");
    }
  } catch (err) {
    statusArea?.classList.add('hidden');
    errorCard?.classList.remove('hidden');
    if (errorMsgText) errorMsgText.innerText = err.message;
  }
});

function downloadCSV(products, hostname) {
  const headers = ["Title", "Handle", "Created At", "Vendor", "Product Type", "Price", "Compare At Price", "Image URL", "Best Seller Rank"];
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
