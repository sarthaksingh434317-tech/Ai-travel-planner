/**
 * TravelGenius AI - Smart AI Trip Planner Form & Itinerary Renderer
 */

let currentGeneratedItinerary = null;
let currentInputParams = null;

document.addEventListener('DOMContentLoaded', () => {
  initFormControls();
  initFormSubmit();
});

// Setup form controls, date limits, traveler counters, and budget presets
function initFormControls() {
  const departureInput = document.getElementById('departure_date');
  const returnInput = document.getElementById('return_date');
  const durationBadge = document.getElementById('trip-duration-display');

  // Set today as minimum departure date
  const today = new Date().toISOString().split('T')[0];
  if (departureInput) {
    departureInput.min = today;
    if (!departureInput.value) {
      // Default to 14 days from now
      const defaultDep = new Date();
      defaultDep.setDate(defaultDep.getDate() + 14);
      departureInput.value = defaultDep.toISOString().split('T')[0];
    }
  }

  if (returnInput && departureInput) {
    returnInput.min = departureInput.value || today;
    if (!returnInput.value && departureInput.value) {
      // Default to 4 days trip
      const defaultRet = new Date(departureInput.value);
      defaultRet.setDate(defaultRet.getDate() + 4);
      returnInput.value = defaultRet.toISOString().split('T')[0];
    }
    updateDurationText();

    departureInput.addEventListener('change', () => {
      returnInput.min = departureInput.value;
      if (returnInput.value && returnInput.value < departureInput.value) {
        returnInput.value = departureInput.value;
      }
      updateDurationText();
    });

    returnInput.addEventListener('change', () => {
      updateDurationText();
    });
  }

  function updateDurationText() {
    if (!departureInput || !returnInput || !durationBadge) return;
    const dep = new Date(departureInput.value);
    const ret = new Date(returnInput.value);
    if (!isNaN(dep) && !isNaN(ret) && ret >= dep) {
      const days = Math.round((ret - dep) / (1000 * 60 * 60 * 24)) + 1;
      const nights = Math.max(0, days - 1);
      durationBadge.innerText = `${days} Days / ${nights} Nights`;
      durationBadge.className = 'badge bg-primary-subtle text-primary border border-primary-subtle px-3 py-2 fs-6';
    } else {
      durationBadge.innerText = 'Select valid dates';
      durationBadge.className = 'badge bg-danger-subtle text-danger border border-danger-subtle px-3 py-2 fs-6';
    }
  }

  // Traveler Counters (Adults & Children)
  setupCounter('adults-minus', 'adults-plus', 'adults-count', 'adults-input', 1, 15);
  setupCounter('children-minus', 'children-plus', 'children-count', 'children-input', 0, 10);

  function setupCounter(minusId, plusId, displayId, inputId, minVal, maxVal) {
    const minusBtn = document.getElementById(minusId);
    const plusBtn = document.getElementById(plusId);
    const display = document.getElementById(displayId);
    const input = document.getElementById(inputId);

    if (!minusBtn || !plusBtn || !display || !input) return;

    minusBtn.addEventListener('click', () => {
      let val = parseInt(input.value) || minVal;
      if (val > minVal) {
        val--;
        input.value = val;
        display.innerText = val;
      }
    });

    plusBtn.addEventListener('click', () => {
      let val = parseInt(input.value) || minVal;
      if (val < maxVal) {
        val++;
        input.value = val;
        display.innerText = val;
      }
    });
  }

  // Budget Presets
  const budgetInput = document.getElementById('budget_inr');
  const presetPills = document.querySelectorAll('.preset-pill');

  presetPills.forEach(pill => {
    pill.addEventListener('click', () => {
      presetPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const amount = pill.dataset.amount;
      if (amount && budgetInput) {
        budgetInput.value = amount;
      }
    });
  });

  if (budgetInput) {
    budgetInput.addEventListener('input', () => {
      presetPills.forEach(p => {
        if (p.dataset.amount === budgetInput.value) {
          p.classList.add('active');
        } else {
          p.classList.remove('active');
        }
      });
    });
  }
}

// Form Submit & Loading Stepper Animation
function initFormSubmit() {
  const form = document.getElementById('trip-planner-form');
  const loadingOverlay = document.getElementById('planner-loading-overlay');
  const itineraryContainer = document.getElementById('itinerary-result-container');
  const formCard = document.querySelector('.planner-form-card');

  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Frontend validation
    const destination = document.getElementById('destination').value.trim();
    const startingCity = document.getElementById('starting_city').value.trim();
    const departureDate = document.getElementById('departure_date').value;
    const returnDate = document.getElementById('return_date').value;
    const budget = parseInt(document.getElementById('budget_inr').value);
    const adults = parseInt(document.getElementById('adults-input').value) || 1;
    const children = parseInt(document.getElementById('children-input').value) || 0;

    if (!destination) {
      showToast('Please enter your destination city or country.', 'warning');
      return;
    }
    if (!startingCity) {
      showToast('Please enter your starting city.', 'warning');
      return;
    }
    if (!departureDate || !returnDate) {
      showToast('Please select both departure and return dates.', 'warning');
      return;
    }
    if (new Date(returnDate) < new Date(departureDate)) {
      showToast('Return date cannot be earlier than departure date.', 'error');
      return;
    }
    if (isNaN(budget) || budget < 1000) {
      showToast('Please specify a realistic budget of at least ₹1,000 INR.', 'warning');
      return;
    }

    // Collect selected interests
    const selectedInterests = [];
    document.querySelectorAll('.interest-badge-checkbox:checked').forEach(cb => {
      selectedInterests.push(cb.value);
    });

    const payload = {
      destination: destination,
      starting_city: startingCity,
      departure_date: departureDate,
      return_date: returnDate,
      budget_inr: budget,
      adults: adults,
      children: children,
      travel_style: document.getElementById('travel_style').value,
      accommodation_pref: document.getElementById('accommodation_pref').value,
      transport_pref: document.getElementById('transport_pref').value,
      dietary_pref: document.getElementById('dietary_pref').value,
      additional_notes: document.getElementById('additional_notes').value.trim(),
      interests: selectedInterests
    };

    // UI State: Show Loading Stepper
    if (formCard) formCard.style.display = 'none';
    if (itineraryContainer) itineraryContainer.style.display = 'none';
    if (loadingOverlay) {
      loadingOverlay.style.display = 'block';
      loadingOverlay.scrollIntoView({ behavior: 'smooth', block: 'center' });
      runLoadingStepper();
    }

    // User Gemini Key check
    const userKey = getSavedGeminiKey();
    const headers = { 'Content-Type': 'application/json' };
    if (userKey) {
      headers['X-Gemini-Key'] = userKey;
    }

    try {
      const response = await fetch('/api/generate-itinerary', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.error || 'Failed to generate itinerary.');
      }

      currentGeneratedItinerary = result.data;
      currentInputParams = result.inputs || payload;

      // Render the itinerary
      renderItinerary(currentGeneratedItinerary, currentInputParams);

      if (loadingOverlay) loadingOverlay.style.display = 'none';
      if (itineraryContainer) {
        itineraryContainer.style.display = 'block';
        itineraryContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }

      if (result.is_sample) {
        showToast('Sample Itinerary generated in Demo Mode.', 'warning', 6000);
      } else {
        showToast('Your personalized AI itinerary is ready!', 'success', 5000);
      }

    } catch (err) {
      console.error('Error generating itinerary:', err);
      if (loadingOverlay) loadingOverlay.style.display = 'none';
      if (formCard) formCard.style.display = 'block';
      showToast(err.message || 'Error communicating with AI service. Please try again.', 'error', 6000);
    }
  });
}

// Stepper animation
function runLoadingStepper() {
  const steps = [
    document.getElementById('step-1'),
    document.getElementById('step-2'),
    document.getElementById('step-3'),
    document.getElementById('step-4')
  ];

  // Reset steps
  steps.forEach(s => {
    if (s) {
      s.className = 'step-item';
      const icon = s.querySelector('.step-icon-circle');
      if (icon) icon.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i>';
    }
  });

  let current = 0;
  if (steps[0]) {
    steps[0].classList.add('active');
  }

  const interval = setInterval(() => {
    if (current < steps.length) {
      if (steps[current]) {
        steps[current].classList.remove('active');
        steps[current].classList.add('done');
        const icon = steps[current].querySelector('.step-icon-circle');
        if (icon) icon.innerHTML = '<i class="fas fa-check"></i>';
      }
      current++;
      if (current < steps.length && steps[current]) {
        steps[current].classList.add('active');
      }
    } else {
      clearInterval(interval);
    }
  }, 1200);
}

// Render generated itinerary into DOM
function renderItinerary(itinerary, params) {
  const container = document.getElementById('itinerary-result-container');
  if (!container) return;

  const isSample = Boolean(itinerary.is_sample);
  const totalDays = itinerary.days ? itinerary.days.length : params.duration_days;
  const travelersTotal = params.adults + params.children;
  const budgetINR = params.budget_inr;

  let badgeHTML = isSample
    ? `<span class="ai-engine-badge badge-sample-mode"><i class="fas fa-flask me-1"></i> Demo Mode • Sample Itinerary</span>`
    : `<span class="ai-engine-badge badge-gemini-live"><i class="fas fa-sparkles me-1"></i> Generated by Gemini AI</span>`;

  let noticeAlertHTML = isSample ? `
    <div class="alert alert-warning border-warning-subtle d-flex align-items-center mb-4" role="alert">
      <i class="fas fa-info-circle fa-lg me-3 text-warning"></i>
      <div>
        <strong>Demo Mode Notice:</strong> This realistic itinerary was curated by our template engine because no live Gemini API key was provided or reachable.
        You can configure your free Gemini API key using the top-right button to experience real-time AI creation.
      </div>
    </div>
  ` : '';

  // Header and Stats
  let html = `
    <!-- Action Bar -->
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4 action-bar-buttons">
      <button class="btn btn-outline-secondary btn-sm" id="btn-edit-preferences">
        <i class="fas fa-sliders-h me-1"></i> Modify Preferences
      </button>
      <div class="d-flex flex-wrap gap-2">
        <button class="btn btn-primary-gradient btn-sm" id="btn-save-trip">
          <i class="fas fa-bookmark me-1"></i> Save to My Trips
        </button>
        <button class="btn btn-outline-primary btn-sm" id="btn-copy-itinerary">
          <i class="fas fa-copy me-1"></i> Copy Plan
        </button>
        <button class="btn btn-outline-primary btn-sm" id="btn-share-itinerary">
          <i class="fas fa-share-alt me-1"></i> Share
        </button>
        <button class="btn btn-outline-dark btn-sm" id="btn-print-itinerary">
          <i class="fas fa-print me-1"></i> Print / PDF
        </button>
      </div>
    </div>

    ${noticeAlertHTML}

    <!-- Hero Banner -->
    <div class="itinerary-header-banner">
      ${badgeHTML}
      <h1 class="display-6 fw-bold mb-2">${escapeHtml(itinerary.title || `Adventure in ${params.destination}`)}</h1>
      <p class="lead text-info mb-4">${escapeHtml(itinerary.tagline || '')}</p>

      <!-- Stat Badges -->
      <div class="row g-3">
        <div class="col-6 col-md-3">
          <div class="stat-widget">
            <div class="stat-label">Duration</div>
            <div class="stat-value">${totalDays} Days</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="stat-widget">
            <div class="stat-label">Travelers</div>
            <div class="stat-value">${travelersTotal} (${params.adults}A, ${params.children}C)</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="stat-widget">
            <div class="stat-label">Total Budget</div>
            <div class="stat-value text-success">${formatINR(budgetINR)}</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="stat-widget">
            <div class="stat-label">Travel Style</div>
            <div class="stat-value">${escapeHtml(params.travel_style)}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Overview & Destination Introduction -->
    <div class="row g-4 mb-5">
      <div class="col-lg-7">
        <div class="card h-100 border-0 shadow-sm rounded-4 p-4 bg-white">
          <h4 class="fw-bold mb-3 text-secondary d-flex align-items-center">
            <i class="fas fa-compass text-primary me-2"></i> Trip Overview
          </h4>
          <p class="text-muted mb-4">${escapeHtml(itinerary.overview?.summary || '')}</p>
          <div class="d-flex flex-wrap gap-2">
            <span class="badge bg-light text-secondary border px-3 py-2">
              <i class="fas fa-tachometer-alt me-1 text-primary"></i> Pace: <strong>${escapeHtml(itinerary.overview?.ideal_pace || 'Balanced')}</strong>
            </span>
            <span class="badge bg-light text-secondary border px-3 py-2">
              <i class="fas fa-sun me-1 text-warning"></i> Season: <strong>${escapeHtml(itinerary.overview?.best_season_note || 'Ideal')}</strong>
            </span>
            <span class="badge bg-light text-secondary border px-3 py-2">
              <i class="fas fa-heart me-1 text-danger"></i> Vibe: <strong>${escapeHtml(itinerary.overview?.cultural_vibe || 'Welcoming')}</strong>
            </span>
          </div>
        </div>
      </div>
      <div class="col-lg-5">
        <div class="card h-100 border-0 shadow-sm rounded-4 p-4 bg-white">
          <h4 class="fw-bold mb-3 text-secondary d-flex align-items-center">
            <i class="fas fa-landmark text-primary me-2"></i> Destination Highlights
          </h4>
          <div class="mb-3">
            <strong class="d-block text-secondary small text-uppercase">History & Heritage</strong>
            <p class="text-muted small mb-2">${escapeHtml(itinerary.destination_intro?.history_and_heritage || '')}</p>
          </div>
          <div class="mb-3">
            <strong class="d-block text-secondary small text-uppercase">Culture & Etiquette</strong>
            <p class="text-muted small mb-0">${escapeHtml(itinerary.destination_intro?.local_culture_and_etiquette || '')}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Day-by-Day Travel Schedule -->
    <div class="mb-5">
      <div class="d-flex justify-content-between align-items-end mb-3">
        <div>
          <h3 class="fw-bold text-secondary mb-1">
            <i class="fas fa-calendar-alt text-primary me-2"></i> Day-by-Day Schedule
          </h3>
          <p class="text-muted mb-0">Detailed morning, afternoon, and evening itinerary for your trip.</p>
        </div>
      </div>

      <!-- Day Tabs Navigation -->
      <div class="itinerary-nav-pills no-print" id="day-tabs-bar">
        ${renderDayTabs(itinerary.days)}
      </div>

      <!-- Day Panes Container -->
      <div id="day-panes-wrapper">
        ${renderDayPanes(itinerary.days)}
      </div>
    </div>

    <!-- Recommended Attractions Grid -->
    <div class="mb-5">
      <h3 class="fw-bold text-secondary mb-3">
        <i class="fas fa-map-marked-alt text-primary me-2"></i> Must-Visit Attractions
      </h3>
      <div class="row g-3">
        ${renderAttractionsCards(itinerary.recommended_attractions)}
      </div>
    </div>

    <!-- Food & Dining -->
    <div class="card border-0 shadow-sm rounded-4 p-4 bg-white mb-5">
      <h3 class="fw-bold text-secondary mb-3">
        <i class="fas fa-utensils text-primary me-2"></i> Local Gastronomy & Dining
      </h3>
      <div class="row g-4">
        <div class="col-md-6">
          <h5 class="fw-bold text-secondary mb-2">Must-Try Iconic Dishes</h5>
          <div class="list-group list-group-flush">
            ${renderDishesList(itinerary.food_and_dining?.must_try_dishes)}
          </div>
        </div>
        <div class="col-md-6">
          <h5 class="fw-bold text-secondary mb-2">Recommended Eateries</h5>
          <div class="list-group list-group-flush">
            ${renderEateriesList(itinerary.food_and_dining?.recommended_eateries)}
          </div>
          ${itinerary.food_and_dining?.dietary_notes ? `
            <div class="alert alert-info border-0 rounded-3 mt-3 py-2 px-3 small">
              <i class="fas fa-seedling me-1"></i> <strong>Dietary Note:</strong> ${escapeHtml(itinerary.food_and_dining.dietary_notes)}
            </div>
          ` : ''}
        </div>
      </div>
    </div>

    <!-- Transportation & Where to Stay -->
    <div class="row g-4 mb-5">
      <div class="col-lg-6">
        <div class="card h-100 border-0 shadow-sm rounded-4 p-4 bg-white">
          <h4 class="fw-bold text-secondary mb-3">
            <i class="fas fa-route text-primary me-2"></i> Transportation Guide
          </h4>
          <div class="mb-3">
            <span class="badge bg-primary-subtle text-primary mb-1">Getting There</span>
            <p class="text-muted small">${escapeHtml(itinerary.transportation?.getting_there || '')}</p>
          </div>
          <div class="mb-3">
            <span class="badge bg-info-subtle text-info mb-1">Getting Around</span>
            <p class="text-muted small">${escapeHtml(itinerary.transportation?.getting_around || '')}</p>
          </div>
          <div class="p-3 bg-light rounded-3 small text-muted">
            <i class="fas fa-lightbulb text-warning me-1"></i> <strong>Pro Tip:</strong> ${escapeHtml(itinerary.transportation?.pro_travel_tip || '')}
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card h-100 border-0 shadow-sm rounded-4 p-4 bg-white">
          <h4 class="fw-bold text-secondary mb-3">
            <i class="fas fa-hotel text-primary me-2"></i> Where to Stay
          </h4>
          <p class="text-muted small mb-3">Top recommended neighborhoods for your travel style:</p>
          ${renderAccommodationAreas(itinerary.accommodation_areas)}
        </div>
      </div>
    </div>

    <!-- Estimated Budget Breakdown in INR -->
    <div class="card border-0 shadow-sm rounded-4 p-4 bg-white mb-5">
      <div class="d-flex flex-wrap justify-content-between align-items-center mb-3">
        <div>
          <h3 class="fw-bold text-secondary mb-1">
            <i class="fas fa-rupee-sign text-primary me-2"></i> Estimated Budget Breakdown
          </h3>
          <p class="text-muted mb-0">Realistic expense allocation in Indian Rupees (INR).</p>
        </div>
        <span class="badge bg-success-subtle text-success fs-6 px-3 py-2">
          Total: ${formatINR(itinerary.budget_breakdown?.total_estimated_budget_inr || budgetINR)}
        </span>
      </div>

      ${renderBudgetBars(itinerary.budget_breakdown, budgetINR)}

      <div class="row g-3 mt-2">
        <div class="col-md-4 col-sm-6">
          <div class="p-3 bg-light rounded-3">
            <div class="text-muted small">Accommodation</div>
            <div class="fw-bold fs-5 text-primary">${formatINR(itinerary.budget_breakdown?.accommodation_total_inr || 0)}</div>
          </div>
        </div>
        <div class="col-md-4 col-sm-6">
          <div class="p-3 bg-light rounded-3">
            <div class="text-muted small">Food & Dining</div>
            <div class="fw-bold fs-5 text-success">${formatINR(itinerary.budget_breakdown?.food_dining_total_inr || 0)}</div>
          </div>
        </div>
        <div class="col-md-4 col-sm-6">
          <div class="p-3 bg-light rounded-3">
            <div class="text-muted small">Sightseeing & Tickets</div>
            <div class="fw-bold fs-5 text-warning">${formatINR(itinerary.budget_breakdown?.activities_tickets_total_inr || 0)}</div>
          </div>
        </div>
        <div class="col-md-4 col-sm-6">
          <div class="p-3 bg-light rounded-3">
            <div class="text-muted small">Local Transport</div>
            <div class="fw-bold fs-5" style="color: #8b5cf6;">${formatINR(itinerary.budget_breakdown?.local_transport_total_inr || 0)}</div>
          </div>
        </div>
        <div class="col-md-4 col-sm-6">
          <div class="p-3 bg-light rounded-3">
            <div class="text-muted small">Contingency & Shopping</div>
            <div class="fw-bold fs-5 text-secondary">${formatINR(itinerary.budget_breakdown?.shopping_contingency_total_inr || 0)}</div>
          </div>
        </div>
        <div class="col-md-4 col-sm-6">
          <div class="p-3 bg-light rounded-3">
            <div class="text-muted small">Est. Daily / Person</div>
            <div class="fw-bold fs-5 text-dark">${formatINR(itinerary.budget_breakdown?.estimated_daily_cost_per_person_inr || 0)}</div>
          </div>
        </div>
      </div>

      <div class="alert alert-light border rounded-3 mt-4 mb-0 small text-muted">
        <i class="fas fa-check-circle text-success me-1"></i> <strong>Budget Verdict:</strong> ${escapeHtml(itinerary.budget_breakdown?.budget_verdict || '')}
      </div>
    </div>

    <!-- Interactive Packing Checklist -->
    <div class="card border-0 shadow-sm rounded-4 p-4 bg-white mb-5">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3 class="fw-bold text-secondary mb-0">
          <i class="fas fa-suitcase-rolling text-primary me-2"></i> Interactive Packing Checklist
        </h3>
        <span class="badge bg-secondary-subtle text-secondary">Click to check off</span>
      </div>
      <div class="row g-4">
        ${renderPackingColumns(itinerary.packing_checklist)}
      </div>
    </div>

    <!-- Safety, Tips & Bad Weather Alternatives -->
    <div class="row g-4 mb-5">
      <div class="col-lg-4">
        <div class="card h-100 border-0 shadow-sm rounded-4 p-4 bg-white">
          <h5 class="fw-bold text-danger mb-3">
            <i class="fas fa-shield-alt me-2"></i> Safety & Health
          </h5>
          <ul class="list-unstyled mb-0">
            ${(itinerary.safety_and_health || []).map(tip => `
              <li class="mb-2 small d-flex align-items-start">
                <i class="fas fa-check text-danger me-2 mt-1"></i>
                <span>${escapeHtml(tip)}</span>
              </li>
            `).join('')}
          </ul>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card h-100 border-0 shadow-sm rounded-4 p-4 bg-white">
          <h5 class="fw-bold text-primary mb-3">
            <i class="fas fa-lightbulb me-2"></i> Practical Travel Tips
          </h5>
          <ul class="list-unstyled mb-0">
            ${(itinerary.useful_travel_tips || []).map(tip => `
              <li class="mb-2 small d-flex align-items-start">
                <i class="fas fa-info-circle text-primary me-2 mt-1"></i>
                <span>${escapeHtml(tip)}</span>
              </li>
            `).join('')}
          </ul>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card h-100 border-0 shadow-sm rounded-4 p-4 bg-white">
          <h5 class="fw-bold text-warning mb-3">
            <i class="fas fa-cloud-showers-heavy me-2"></i> Rainy Day Backups
          </h5>
          <ul class="list-unstyled mb-0">
            ${(itinerary.bad_weather_alternatives || []).map(alt => `
              <li class="mb-3 small">
                <strong class="d-block text-secondary">${escapeHtml(alt.activity)}</strong>
                <span class="text-muted">${escapeHtml(alt.description)}</span>
              </li>
            `).join('')}
          </ul>
        </div>
      </div>
    </div>

    <!-- Legal & Price Disclaimer -->
    <div class="p-3 bg-light border rounded-3 text-center small text-muted mb-5">
      <i class="fas fa-info-circle me-1"></i>
      <strong>Disclaimer:</strong> ${escapeHtml(itinerary.disclaimer || 'All costs and prices are realistic estimates in INR and subject to seasonal fluctuation. Please confirm live bookings, flight fares, and opening hours independently before traveling.')}
    </div>
  `;

  container.innerHTML = html;

  // Attach event handlers to buttons in the newly rendered HTML
  attachItineraryActionHandlers(itinerary, params);
  initDayTabSwitching();
  initPackingCheckboxListeners();
}

// Render Day Tabs
function renderDayTabs(days) {
  if (!days || !days.length) return '';
  return days.map((day, idx) => `
    <button type="button" class="day-tab-pill ${idx === 0 ? 'active' : ''}" data-day-index="${idx}">
      Day ${day.day_number}
      <span class="d-none d-sm-inline small ms-1 text-muted">(${escapeHtml(day.date || '')})</span>
    </button>
  `).join('');
}

// Render Day Schedule Panes
function renderDayPanes(days) {
  if (!days || !days.length) return '';
  return days.map((day, idx) => `
    <div class="day-schedule-pane" id="day-pane-${idx}" style="${idx === 0 ? 'display: block;' : 'display: none;'}">
      <div class="day-schedule-card">
        <div class="d-flex flex-wrap justify-content-between align-items-center mb-4">
          <div>
            <span class="badge bg-primary px-3 py-2 mb-1">Day ${day.day_number} • ${escapeHtml(day.date || '')}</span>
            <h4 class="fw-bold text-secondary mb-0">${escapeHtml(day.theme || '')}</h4>
          </div>
          ${day.daily_highlight ? `
            <div class="badge bg-warning-subtle text-dark border border-warning-subtle p-2">
              <i class="fas fa-star text-warning me-1"></i> ${escapeHtml(day.daily_highlight)}
            </div>
          ` : ''}
        </div>

        <!-- Morning Slot -->
        <div class="time-slot-card time-slot-morning">
          <span class="slot-time-badge slot-time-morning">
            <i class="fas fa-sun me-1"></i> Morning • ${escapeHtml(day.morning?.time || '09:00 AM')}
          </span>
          <h5 class="fw-bold text-secondary mb-1">${escapeHtml(day.morning?.activity || '')}</h5>
          <p class="text-muted small mb-2">${escapeHtml(day.morning?.description || '')}</p>
          <div class="d-flex flex-wrap justify-content-between align-items-center small text-muted">
            <span><i class="fas fa-lightbulb text-warning me-1"></i> ${escapeHtml(day.morning?.tips || '')}</span>
            <span class="badge bg-white text-secondary border">Est. ${formatINR(day.morning?.estimated_cost_inr || 0)}</span>
          </div>
        </div>

        <!-- Afternoon Slot -->
        <div class="time-slot-card time-slot-afternoon">
          <span class="slot-time-badge slot-time-afternoon">
            <i class="fas fa-cloud-sun me-1"></i> Afternoon • ${escapeHtml(day.afternoon?.time || '01:00 PM')}
          </span>
          <h5 class="fw-bold text-secondary mb-1">${escapeHtml(day.afternoon?.activity || '')}</h5>
          <p class="text-muted small mb-2">${escapeHtml(day.afternoon?.description || '')}</p>
          <div class="d-flex flex-wrap justify-content-between align-items-center small text-muted">
            <span><i class="fas fa-lightbulb text-info me-1"></i> ${escapeHtml(day.afternoon?.tips || '')}</span>
            <span class="badge bg-white text-secondary border">Est. ${formatINR(day.afternoon?.estimated_cost_inr || 0)}</span>
          </div>
        </div>

        <!-- Evening Slot -->
        <div class="time-slot-card time-slot-evening">
          <span class="slot-time-badge slot-time-evening">
            <i class="fas fa-moon me-1"></i> Evening • ${escapeHtml(day.evening?.time || '06:00 PM')}
          </span>
          <h5 class="fw-bold text-secondary mb-1">${escapeHtml(day.evening?.activity || '')}</h5>
          <p class="text-muted small mb-2">${escapeHtml(day.evening?.description || '')}</p>
          <div class="d-flex flex-wrap justify-content-between align-items-center small text-muted">
            <span><i class="fas fa-lightbulb text-purple me-1"></i> ${escapeHtml(day.evening?.tips || '')}</span>
            <span class="badge bg-white text-secondary border">Est. ${formatINR(day.evening?.estimated_cost_inr || 0)}</span>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}

// Render Attractions Cards
function renderAttractionsCards(attractions) {
  if (!attractions || !attractions.length) return '<div class="col-12 text-muted">No attractions listed.</div>';
  return attractions.map(attr => `
    <div class="col-md-6 col-lg-4">
      <div class="card h-100 border-0 shadow-sm rounded-4 p-3 bg-white">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <span class="badge bg-primary-subtle text-primary">${escapeHtml(attr.category || 'Sightseeing')}</span>
          <span class="badge bg-light text-secondary border">
            ${attr.entry_fee_inr === 0 ? 'Free Entry' : formatINR(attr.entry_fee_inr)}
          </span>
        </div>
        <h5 class="fw-bold text-secondary mb-1">${escapeHtml(attr.name)}</h5>
        <p class="text-muted small flex-grow-1 mb-2">${escapeHtml(attr.description || '')}</p>
        <div class="d-flex justify-content-between text-muted small border-top pt-2">
          <span><i class="far fa-clock me-1"></i> ${escapeHtml(attr.recommended_time_hours || '2 hrs')}</span>
          <span><i class="far fa-sun me-1"></i> ${escapeHtml(attr.best_time_of_day || 'Anytime')}</span>
        </div>
      </div>
    </div>
  `).join('');
}

// Food Lists
function renderDishesList(dishes) {
  if (!dishes || !dishes.length) return '<p class="text-muted small">Local favorites</p>';
  return dishes.map(d => `
    <div class="list-group-item px-0 py-2 border-0">
      <strong class="text-secondary d-block">${escapeHtml(d.dish)}</strong>
      <span class="text-muted small">${escapeHtml(d.description)}</span>
    </div>
  `).join('');
}

function renderEateriesList(eateries) {
  if (!eateries || !eateries.length) return '<p class="text-muted small">Popular cafes & restaurants</p>';
  return eateries.map(e => `
    <div class="list-group-item px-0 py-2 border-0">
      <div class="d-flex justify-content-between">
        <strong class="text-secondary">${escapeHtml(e.name)}</strong>
        <span class="badge bg-light text-secondary border">${escapeHtml(e.price_range_inr || '')}</span>
      </div>
      <span class="text-muted small">${escapeHtml(e.cuisine || '')} • ${escapeHtml(e.vibe || '')}</span>
    </div>
  `).join('');
}

// Accommodation Neighborhoods
function renderAccommodationAreas(areas) {
  if (!areas || !areas.length) return '<p class="text-muted small">Central accommodation options</p>';
  return areas.map(area => `
    <div class="p-3 bg-light rounded-3 mb-2">
      <div class="d-flex justify-content-between align-items-center mb-1">
        <strong class="text-secondary">${escapeHtml(area.neighborhood)}</strong>
        <span class="badge bg-white text-primary border">Avg ${formatINR(area.average_nightly_rate_inr || 4000)}/night</span>
      </div>
      <div class="small text-muted mb-1"><i class="fas fa-users text-primary me-1"></i> Best for: ${escapeHtml(area.best_for || 'All travelers')}</div>
      <p class="text-muted small mb-0">${escapeHtml(area.vibe_description || '')}</p>
    </div>
  `).join('');
}

// Budget Stacked Bars
function renderBudgetBars(breakdown, totalBudget) {
  if (!breakdown) return '';
  const total = breakdown.total_estimated_budget_inr || totalBudget || 1;
  const stayPct = Math.round(((breakdown.accommodation_total_inr || 0) / total) * 100);
  const foodPct = Math.round(((breakdown.food_dining_total_inr || 0) / total) * 100);
  const actPct = Math.round(((breakdown.activities_tickets_total_inr || 0) / total) * 100);
  const transPct = Math.round(((breakdown.local_transport_total_inr || 0) / total) * 100);
  const contPct = Math.max(0, 100 - (stayPct + foodPct + actPct + transPct));

  return `
    <div class="budget-bar-container">
      <div class="budget-bar-segment budget-stay" style="width: ${stayPct}%;" title="Accommodation: ${stayPct}%"></div>
      <div class="budget-bar-segment budget-food" style="width: ${foodPct}%;" title="Food & Dining: ${foodPct}%"></div>
      <div class="budget-bar-segment budget-activities" style="width: ${actPct}%;" title="Sightseeing: ${actPct}%"></div>
      <div class="budget-bar-segment budget-transport" style="width: ${transPct}%;" title="Transport: ${transPct}%"></div>
      <div class="budget-bar-segment budget-contingency" style="width: ${contPct}%;" title="Contingency: ${contPct}%"></div>
    </div>
    <div class="d-flex flex-wrap gap-3 small text-muted">
      <span><i class="fas fa-circle text-primary me-1"></i> Stay (${stayPct}%)</span>
      <span><i class="fas fa-circle text-success me-1"></i> Food (${foodPct}%)</span>
      <span><i class="fas fa-circle text-warning me-1"></i> Activities (${actPct}%)</span>
      <span><i class="fas fa-circle text-purple me-1" style="color: #8b5cf6;"></i> Transport (${transPct}%)</span>
      <span><i class="fas fa-circle text-secondary me-1"></i> Contingency (${contPct}%)</span>
    </div>
  `;
}

// Packing Checklist Columns
function renderPackingColumns(checklist) {
  if (!checklist) return '<div class="col-12 text-muted">Checklist ready.</div>';

  const categories = [
    { title: 'Clothing', key: 'clothing', icon: 'fa-tshirt text-primary' },
    { title: 'Essentials & Documents', key: 'essentials', icon: 'fa-passport text-success' },
    { title: 'Tech & Electronics', key: 'electronics', icon: 'fa-laptop text-info' },
    { title: 'Health & Toiletries', key: 'health_and_medical', icon: 'fa-medkit text-danger' }
  ];

  return categories.map(cat => `
    <div class="col-md-6 col-lg-3">
      <h6 class="fw-bold text-secondary mb-2">
        <i class="fas ${cat.icon} me-1"></i> ${cat.title}
      </h6>
      <div class="checklist-group">
        ${(checklist[cat.key] || []).map((item, i) => `
          <label class="packing-item">
            <input type="checkbox" class="packing-checkbox" data-cat="${cat.key}" data-index="${i}">
            <span class="small">${escapeHtml(item)}</span>
          </label>
        `).join('')}
      </div>
    </div>
  `).join('');
}

// Day Tab Switching
function initDayTabSwitching() {
  const tabs = document.querySelectorAll('.day-tab-pill');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const dayIdx = tab.dataset.dayIndex;
      document.querySelectorAll('.day-schedule-pane').forEach((pane, idx) => {
        pane.style.display = (idx == dayIdx) ? 'block' : 'none';
      });
    });
  });
}

// Packing Checkbox Toggle
function initPackingCheckboxListeners() {
  document.querySelectorAll('.packing-checkbox').forEach(cb => {
    cb.addEventListener('change', () => {
      const parentLabel = cb.closest('.packing-item');
      if (parentLabel) {
        if (cb.checked) {
          parentLabel.classList.add('checked');
        } else {
          parentLabel.classList.remove('checked');
        }
      }
    });
  });
}

// Attach Action Buttons (Save, Copy, Share, Print)
function attachItineraryActionHandlers(itinerary, params) {
  // Modify Preferences (re-shows form)
  const editBtn = document.getElementById('btn-edit-preferences');
  if (editBtn) {
    editBtn.addEventListener('click', () => {
      const formCard = document.querySelector('.planner-form-card');
      if (formCard) {
        formCard.style.display = 'block';
        formCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  // Save to My Trips
  const saveBtn = document.getElementById('btn-save-trip');
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      saveBtn.disabled = true;
      saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Saving...';

      const payload = {
        title: itinerary.title || `Trip to ${params.destination}`,
        destination: params.destination,
        starting_city: params.starting_city,
        departure_date: params.departure_date,
        return_date: params.return_date,
        duration_days: params.duration_days,
        travelers: params.travelers,
        adults: params.adults,
        children: params.children,
        budget_inr: params.budget_inr,
        travel_style: params.travel_style,
        interests: params.interests,
        itinerary: itinerary,
        is_sample: Boolean(itinerary.is_sample)
      };

      try {
        const res = await fetch('/api/save-trip', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (res.ok && result.success) {
          showToast('Itinerary saved to My Trips!', 'success');
          saveBtn.innerHTML = '<i class="fas fa-check me-1"></i> Saved in My Trips';
          saveBtn.classList.replace('btn-primary-gradient', 'btn-success');
        } else {
          throw new Error(result.error || 'Failed to save trip.');
        }
      } catch (err) {
        showToast(err.message || 'Error saving trip to database.', 'error');
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-bookmark me-1"></i> Save to My Trips';
      }
    });
  }

  // Copy Itinerary Text
  const copyBtn = document.getElementById('btn-copy-itinerary');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      let copyText = `✈️ ${itinerary.title || 'TravelGenius AI Itinerary'}\n`;
      copyText += `Destination: ${params.destination}\n`;
      copyText += `Dates: ${params.departure_date} to ${params.return_date} (${params.duration_days} Days)\n`;
      copyText += `Budget: ₹${Number(params.budget_inr).toLocaleString('en-IN')}\n\n`;
      copyText += `Trip Overview:\n${itinerary.overview?.summary || ''}\n\n`;

      if (itinerary.days) {
        itinerary.days.forEach(d => {
          copyText += `Day ${d.day_number}: ${d.theme} (${d.date})\n`;
          copyText += `  • Morning: ${d.morning?.activity} - ${d.morning?.description}\n`;
          copyText += `  • Afternoon: ${d.afternoon?.activity} - ${d.afternoon?.description}\n`;
          copyText += `  • Evening: ${d.evening?.activity} - ${d.evening?.description}\n\n`;
        });
      }
      copyText += `Generated by TravelGenius AI – Smart Travel Planner`;
      copyToClipboard(copyText, 'Itinerary copied to clipboard!');
    });
  }

  // Share Itinerary
  const shareBtn = document.getElementById('btn-share-itinerary');
  if (shareBtn) {
    shareBtn.addEventListener('click', () => {
      shareContent({
        title: itinerary.title || `Trip to ${params.destination}`,
        text: `Check out my ${params.duration_days}-day travel plan to ${params.destination} created with TravelGenius AI!`,
        url: window.location.href
      });
    });
  }

  // Print / PDF
  const printBtn = document.getElementById('btn-print-itinerary');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }
}

// Escape HTML helper
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
