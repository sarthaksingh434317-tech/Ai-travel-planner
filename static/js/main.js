/**
 * TravelGenius AI - Main Application Utilities
 */

// Toast notification helper
function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `custom-toast custom-toast-${type}`;

  let icon = 'fa-info-circle text-primary';
  if (type === 'success') icon = 'fa-check-circle text-success';
  if (type === 'error') icon = 'fa-exclamation-circle text-danger';
  if (type === 'warning') icon = 'fa-exclamation-triangle text-warning';

  toast.innerHTML = `
    <i class="fas ${icon} fa-lg"></i>
    <div style="flex-grow: 1;">${message}</div>
    <button type="button" class="btn-close btn-close-sm" style="font-size: 0.75rem;" aria-label="Close"></button>
  `;

  const closeBtn = toast.querySelector('.btn-close');
  closeBtn.addEventListener('click', () => {
    toast.remove();
  });

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 400);
  }, duration);
}

// Format numbers as INR currency (e.g. ₹50,000)
function formatINR(number) {
  if (isNaN(number)) return '₹0';
  return '₹' + Number(number).toLocaleString('en-IN');
}

// Copy text to clipboard with fallback
async function copyToClipboard(text, successMsg = 'Copied to clipboard!') {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand('copy');
      textArea.remove();
    }
    showToast(successMsg, 'success');
    return true;
  } catch (err) {
    console.error('Copy failed:', err);
    showToast('Failed to copy to clipboard', 'error');
    return false;
  }
}

// Share using Web Share API with fallback
async function shareContent(shareData) {
  if (navigator.share) {
    try {
      await navigator.share(shareData);
      showToast('Shared successfully!', 'success');
      return true;
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.warn('Share error:', err);
      }
    }
  }
  // Fallback: copy link or text
  const shareText = `${shareData.title}\n${shareData.text || ''}\n${shareData.url || window.location.href}`;
  return copyToClipboard(shareText, 'Trip details copied to clipboard!');
}

// Local Storage Gemini Key Management
function getSavedGeminiKey() {
  return localStorage.getItem('travelgenius_gemini_key') || '';
}

function saveGeminiKey(key) {
  if (key && key.trim()) {
    localStorage.setItem('travelgenius_gemini_key', key.trim());
    showToast('Gemini API key saved in browser!', 'success');
  } else {
    localStorage.removeItem('travelgenius_gemini_key');
    showToast('Gemini API key cleared from browser.', 'info');
  }
  updateApiKeyBadge();
}

function updateApiKeyBadge() {
  const badge = document.getElementById('navbar-api-badge');
  const modalInput = document.getElementById('user-gemini-key-input');
  const savedKey = getSavedGeminiKey();
  
  if (modalInput) {
    modalInput.value = savedKey;
  }

  if (badge) {
    const hasServerKey = badge.dataset.serverKey === 'true';
    if (savedKey || hasServerKey) {
      badge.className = 'badge bg-success-subtle text-success border border-success-subtle px-2 py-1';
      badge.innerHTML = '<i class="fas fa-sparkles me-1"></i> AI Active';
      badge.title = 'Gemini AI is ready to generate itineraries';
    } else {
      badge.className = 'badge bg-warning-subtle text-warning border border-warning-subtle px-2 py-1';
      badge.innerHTML = '<i class="fas fa-flask me-1"></i> Demo Mode';
      badge.title = 'Running in Demo Mode (Sample Itineraries). Click to configure API Key';
    }
  }
}

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  updateApiKeyBadge();

  // Settings modal save button
  const saveKeyBtn = document.getElementById('btn-save-custom-key');
  if (saveKeyBtn) {
    saveKeyBtn.addEventListener('click', () => {
      const input = document.getElementById('user-gemini-key-input');
      if (input) {
        saveGeminiKey(input.value);
        const modalEl = document.getElementById('apiKeyModal');
        if (modalEl && window.bootstrap) {
          const modalInstance = bootstrap.Modal.getInstance(modalEl);
          if (modalInstance) modalInstance.hide();
        }
      }
    });
  }

  // Clear key button
  const clearKeyBtn = document.getElementById('btn-clear-custom-key');
  if (clearKeyBtn) {
    clearKeyBtn.addEventListener('click', () => {
      saveGeminiKey('');
      const input = document.getElementById('user-gemini-key-input');
      if (input) input.value = '';
    });
  }

  // Auto-close responsive mobile navbar when link is clicked
  const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
  const navCollapse = document.getElementById('navbarNav');
  if (navCollapse && window.bootstrap) {
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        if (navCollapse.classList.contains('show')) {
          const bsCollapse = bootstrap.Collapse.getInstance(navCollapse);
          if (bsCollapse) bsCollapse.hide();
        }
      });
    });
  }
});
