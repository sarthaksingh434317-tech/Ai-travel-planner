/**
 * TravelGenius AI - My Trips Manager
 * View, delete, export, and manage saved travel plans in SQLite
 */

let tripToDeleteId = null;
let currentModalTrip = null;

document.addEventListener('DOMContentLoaded', () => {
  initSavedTripActions();
  initDeleteTripModal();
});

function initSavedTripActions() {
  // View Details
  document.querySelectorAll('.btn-view-saved-trip').forEach(btn => {
    btn.addEventListener('click', () => {
      const tripId = btn.dataset.tripId;
      if (tripId) {
        loadAndDisplayTripDetails(tripId);
      }
    });
  });

  // Delete Trip
  document.querySelectorAll('.btn-delete-saved-trip').forEach(btn => {
    btn.addEventListener('click', () => {
      tripToDeleteId = btn.dataset.tripId;
      const tripTitle = btn.dataset.tripTitle || 'this trip';
      const titleSpan = document.getElementById('delete-trip-title');
      if (titleSpan) titleSpan.innerText = tripTitle;

      const deleteModalEl = document.getElementById('deleteConfirmModal');
      if (deleteModalEl && window.bootstrap) {
        const modal = new bootstrap.Modal(deleteModalEl);
        modal.show();
      }
    });
  });
}

function initDeleteTripModal() {
  const confirmBtn = document.getElementById('btn-confirm-delete-trip');
  if (!confirmBtn) return;

  confirmBtn.addEventListener('click', async () => {
    if (!tripToDeleteId) return;

    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Deleting...';

    try {
      const res = await fetch(`/api/trips/${tripToDeleteId}`, {
        method: 'DELETE'
      });
      const data = await res.json();

      if (res.ok && data.success) {
        showToast('Trip deleted successfully.', 'success');
        
        // Remove card from UI
        const card = document.getElementById(`trip-card-${tripToDeleteId}`);
        if (card) {
          card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
          card.style.opacity = '0';
          card.style.transform = 'scale(0.9)';
          setTimeout(() => {
            card.remove();
            checkEmptyState();
          }, 400);
        }

        const deleteModalEl = document.getElementById('deleteConfirmModal');
        if (deleteModalEl && window.bootstrap) {
          const modalInstance = bootstrap.Modal.getInstance(deleteModalEl);
          if (modalInstance) modalInstance.hide();
        }
      } else {
        throw new Error(data.error || 'Failed to delete trip.');
      }
    } catch (err) {
      showToast(err.message || 'Error deleting trip.', 'error');
    } finally {
      confirmBtn.disabled = false;
      confirmBtn.innerHTML = 'Delete Trip';
      tripToDeleteId = null;
    }
  });
}

function checkEmptyState() {
  const tripCards = document.querySelectorAll('.saved-trip-item');
  const emptyState = document.getElementById('no-saved-trips');
  if (tripCards.length === 0 && emptyState) {
    emptyState.style.display = 'block';
  }
}

async function loadAndDisplayTripDetails(tripId) {
  try {
    const res = await fetch(`/api/trips/${tripId}`);
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error || 'Failed to load trip details.');
    }

    const trip = data.trip;
    currentModalTrip = trip;
    const itin = trip.itinerary || {};

    // Populate Modal Elements
    document.getElementById('modal-trip-title').innerText = trip.title;
    document.getElementById('modal-trip-destination').innerText = `${trip.destination} • Starting from ${trip.starting_city || 'Origin'}`;
    document.getElementById('modal-trip-dates').innerText = `${trip.departure_date} to ${trip.return_date} (${trip.duration_days} Days)`;
    document.getElementById('modal-trip-budget').innerText = `₹${Number(trip.budget_inr).toLocaleString('en-IN')}`;
    document.getElementById('modal-trip-travelers').innerText = `${trip.travelers} Traveler(s)`;

    const badge = document.getElementById('modal-trip-badge');
    if (badge) {
      if (trip.is_sample) {
        badge.className = 'badge bg-warning-subtle text-warning border border-warning-subtle';
        badge.innerHTML = '<i class="fas fa-flask me-1"></i> Sample Plan';
      } else {
        badge.className = 'badge bg-success-subtle text-success border border-success-subtle';
        badge.innerHTML = '<i class="fas fa-sparkles me-1"></i> AI Generated';
      }
    }

    // Itinerary Body
    const bodyEl = document.getElementById('modal-trip-body');
    if (bodyEl) {
      let bodyHTML = `
        <div class="mb-4">
          <h5 class="fw-bold text-secondary mb-2">Overview</h5>
          <p class="text-muted">${escapeHtml(itin.overview?.summary || 'Custom generated itinerary.')}</p>
        </div>

        <div class="mb-4">
          <h5 class="fw-bold text-secondary mb-3">Day-by-Day Schedule</h5>
          ${(itin.days || []).map(day => `
            <div class="card border rounded-3 p-3 mb-3 bg-light">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <strong class="text-primary">Day ${day.day_number}: ${escapeHtml(day.theme || '')}</strong>
                <span class="small text-muted">${escapeHtml(day.date || '')}</span>
              </div>
              <div class="small mb-1"><strong>Morning:</strong> ${escapeHtml(day.morning?.activity || '')} - <span class="text-muted">${escapeHtml(day.morning?.description || '')}</span></div>
              <div class="small mb-1"><strong>Afternoon:</strong> ${escapeHtml(day.afternoon?.activity || '')} - <span class="text-muted">${escapeHtml(day.afternoon?.description || '')}</span></div>
              <div class="small mb-0"><strong>Evening:</strong> ${escapeHtml(day.evening?.activity || '')} - <span class="text-muted">${escapeHtml(day.evening?.description || '')}</span></div>
            </div>
          `).join('')}
        </div>

        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <h6 class="fw-bold text-secondary mb-2">Transportation</h6>
            <p class="small text-muted mb-0">${escapeHtml(itin.transportation?.getting_around || 'Local transit & cabs')}</p>
          </div>
          <div class="col-md-6">
            <h6 class="fw-bold text-secondary mb-2">Estimated Budget Breakdown</h6>
            <div class="small text-muted">
              <div>Stay: ₹${Number(itin.budget_breakdown?.accommodation_total_inr || 0).toLocaleString('en-IN')}</div>
              <div>Food: ₹${Number(itin.budget_breakdown?.food_dining_total_inr || 0).toLocaleString('en-IN')}</div>
              <div>Activities: ₹${Number(itin.budget_breakdown?.activities_tickets_total_inr || 0).toLocaleString('en-IN')}</div>
            </div>
          </div>
        </div>
      `;
      bodyEl.innerHTML = bodyHTML;
    }

    // Modal Action Buttons
    const printBtn = document.getElementById('btn-modal-print');
    if (printBtn) {
      printBtn.onclick = () => {
        window.print();
      };
    }

    const copyBtn = document.getElementById('btn-modal-copy');
    if (copyBtn) {
      copyBtn.onclick = () => {
        let copyText = `✈️ ${trip.title}\n`;
        copyText += `Destination: ${trip.destination}\n`;
        copyText += `Dates: ${trip.departure_date} to ${trip.return_date}\n`;
        copyText += `Budget: ₹${Number(trip.budget_inr).toLocaleString('en-IN')}\n\n`;
        if (itin.days) {
          itin.days.forEach(d => {
            copyText += `Day ${d.day_number}: ${d.theme}\n`;
            copyText += `  • Morning: ${d.morning?.activity}\n`;
            copyText += `  • Afternoon: ${d.afternoon?.activity}\n`;
            copyText += `  • Evening: ${d.evening?.activity}\n`;
          });
        }
        copyToClipboard(copyText, 'Trip itinerary copied to clipboard!');
      };
    }

    const shareBtn = document.getElementById('btn-modal-share');
    if (shareBtn) {
      shareBtn.onclick = () => {
        shareContent({
          title: trip.title,
          text: `Take a look at my saved trip to ${trip.destination}!`,
          url: window.location.href
        });
      };
    }

    // Show Details Modal
    const detailsModalEl = document.getElementById('tripDetailsModal');
    if (detailsModalEl && window.bootstrap) {
      const modal = new bootstrap.Modal(detailsModalEl);
      modal.show();
    }

  } catch (err) {
    showToast(err.message || 'Error loading trip details.', 'error');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
