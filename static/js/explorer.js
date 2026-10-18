/**
 * TravelGenius AI - Destination Explorer Filtering & Quick View Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  initExplorerFilters();
  initDestinationModal();
});

function initExplorerFilters() {
  const searchInput = document.getElementById('search-destination');
  const regionSelect = document.getElementById('filter-region');
  const budgetSelect = document.getElementById('filter-budget');
  const styleSelect = document.getElementById('filter-style');
  const resetBtn = document.getElementById('btn-reset-filters');
  const destCards = document.querySelectorAll('.destination-item');
  const counterSpan = document.getElementById('destinations-count-badge');
  const emptyState = document.getElementById('explorer-empty-state');

  function applyFilters() {
    const q = (searchInput?.value || '').toLowerCase().trim();
    const region = (regionSelect?.value || 'all').toLowerCase();
    const budget = (budgetSelect?.value || 'all').toLowerCase();
    const style = (styleSelect?.value || 'all').toLowerCase();

    let visibleCount = 0;

    destCards.forEach(card => {
      const cardRegion = (card.dataset.region || '').toLowerCase();
      const cardBudget = (card.dataset.budget || '').toLowerCase();
      const cardStyles = (card.dataset.styles || '').toLowerCase();
      const cardName = (card.dataset.name || '').toLowerCase();
      const cardCountry = (card.dataset.country || '').toLowerCase();
      const cardDesc = (card.dataset.desc || '').toLowerCase();

      let matches = true;

      if (region !== 'all' && cardRegion !== region) {
        matches = false;
      }
      if (budget !== 'all' && cardBudget !== budget) {
        matches = false;
      }
      if (style !== 'all' && !cardStyles.includes(style)) {
        matches = false;
      }
      if (q) {
        const textToSearch = `${cardName} ${cardCountry} ${cardDesc} ${cardStyles}`;
        if (!textToSearch.includes(q)) {
          matches = false;
        }
      }

      if (matches) {
        card.style.display = 'block';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (counterSpan) {
      counterSpan.innerText = `Showing ${visibleCount} destinations`;
    }

    if (emptyState) {
      emptyState.style.display = (visibleCount === 0) ? 'block' : 'none';
    }
  }

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (regionSelect) regionSelect.addEventListener('change', applyFilters);
  if (budgetSelect) budgetSelect.addEventListener('change', applyFilters);
  if (styleSelect) styleSelect.addEventListener('change', applyFilters);

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (regionSelect) regionSelect.value = 'all';
      if (budgetSelect) budgetSelect.value = 'all';
      if (styleSelect) styleSelect.value = 'all';
      applyFilters();
    });
  }
}

// Quick View Destination Modal
function initDestinationModal() {
  const modalEl = document.getElementById('destinationModal');
  if (!modalEl) return;

  const viewBtns = document.querySelectorAll('.btn-view-destination');
  viewBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const destId = btn.dataset.destId;
      if (!destId) return;

      fetch(`/api/destinations/${destId}`)
        .then(res => res.json())
        .then(result => {
          if (result.success && result.destination) {
            populateDestinationModal(result.destination);
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
          }
        })
        .catch(err => {
          console.error('Failed to load destination details:', err);
        });
    });
  });
}

function populateDestinationModal(dest) {
  const title = document.getElementById('modal-dest-title');
  const tagline = document.getElementById('modal-dest-tagline');
  const img = document.getElementById('modal-dest-img');
  const desc = document.getElementById('modal-dest-desc');
  const season = document.getElementById('modal-dest-season');
  const budget = document.getElementById('modal-dest-budget');
  const duration = document.getElementById('modal-dest-duration');
  const attractionsList = document.getElementById('modal-dest-attractions');
  const highlightsList = document.getElementById('modal-dest-highlights');
  const planBtn = document.getElementById('modal-dest-plan-btn');

  if (title) title.innerText = `${dest.name}, ${dest.country}`;
  if (tagline) tagline.innerText = dest.tagline;
  if (img) {
    img.src = dest.image_url;
    img.alt = dest.name;
    img.onerror = function() { this.src = '/static/images/hero-bg.svg'; };
  }
  if (desc) desc.innerText = dest.description;
  if (season) season.innerText = dest.best_time;
  if (budget) budget.innerText = dest.budget_range_inr;
  if (duration) duration.innerText = dest.ideal_duration;

  if (attractionsList) {
    attractionsList.innerHTML = (dest.popular_attractions || []).map(a => `
      <span class="badge bg-light text-secondary border p-2 me-1 mb-1">
        <i class="fas fa-check-circle text-primary me-1"></i> ${a}
      </span>
    `).join('');
  }

  if (highlightsList) {
    highlightsList.innerHTML = (dest.highlights || []).map(h => `
      <li class="mb-2 text-muted small"><i class="fas fa-star text-warning me-2"></i> ${h}</li>
    `).join('');
  }

  if (planBtn) {
    planBtn.href = `/plan?destination=${encodeURIComponent(dest.name)}`;
  }
}
