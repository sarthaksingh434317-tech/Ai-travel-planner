/**
 * TravelGenius AI - Interactive Trip Budget Estimator Widget
 */

document.addEventListener('DOMContentLoaded', () => {
  initBudgetCalculator();
});

function initBudgetCalculator() {
  const calcForm = document.getElementById('budget-calculator-form');
  if (!calcForm) return;

  const daysSlider = document.getElementById('calc-days');
  const daysVal = document.getElementById('calc-days-val');
  const travelersSlider = document.getElementById('calc-travelers');
  const travelersVal = document.getElementById('calc-travelers-val');
  const tierRadios = document.querySelectorAll('input[name="calc-tier"]');
  const destTypeRadios = document.querySelectorAll('input[name="calc-dest-type"]');
  const planBtn = document.getElementById('calc-apply-btn');

  function calculate() {
    const days = parseInt(daysSlider?.value || 4);
    const travelers = parseInt(travelersSlider?.value || 2);
    if (daysVal) daysVal.innerText = `${days} Days`;
    if (travelersVal) travelersVal.innerText = `${travelers} ${travelers === 1 ? 'Traveler' : 'Travelers'}`;

    let tier = 'mid';
    tierRadios.forEach(r => { if (r.checked) tier = r.value; });

    let isInternational = false;
    destTypeRadios.forEach(r => { if (r.checked) isInternational = (r.value === 'international'); });

    // Rates in INR per day per person
    let dailyRate = 3800; // default domestic mid
    if (tier === 'budget') {
      dailyRate = isInternational ? 4000 : 2000;
    } else if (tier === 'luxury') {
      dailyRate = isInternational ? 20000 : 9000;
    } else {
      dailyRate = isInternational ? 8500 : 4000;
    }

    const total = dailyRate * days * travelers;
    const stay = Math.round(total * 0.40);
    const food = Math.round(total * 0.25);
    const activities = Math.round(total * 0.15);
    const transport = Math.round(total * 0.12);
    const contingency = total - (stay + food + activities + transport);

    // Update UI elements
    const totalEl = document.getElementById('calc-total-display');
    const perPersonEl = document.getElementById('calc-per-person-display');
    const stayEl = document.getElementById('calc-stay-display');
    const foodEl = document.getElementById('calc-food-display');
    const actEl = document.getElementById('calc-activities-display');
    const transEl = document.getElementById('calc-transport-display');
    const contEl = document.getElementById('calc-contingency-display');

    if (totalEl) totalEl.innerText = '₹' + total.toLocaleString('en-IN');
    if (perPersonEl) perPersonEl.innerText = '₹' + Math.round(total / travelers).toLocaleString('en-IN');
    if (stayEl) stayEl.innerText = '₹' + stay.toLocaleString('en-IN');
    if (foodEl) foodEl.innerText = '₹' + food.toLocaleString('en-IN');
    if (actEl) actEl.innerText = '₹' + activities.toLocaleString('en-IN');
    if (transEl) transEl.innerText = '₹' + transport.toLocaleString('en-IN');
    if (contEl) contEl.innerText = '₹' + contingency.toLocaleString('en-IN');

    // Update plan button href
    if (planBtn) {
      planBtn.href = `/plan?budget=${total}&travelers=${travelers}`;
    }
  }

  if (daysSlider) daysSlider.addEventListener('input', calculate);
  if (travelersSlider) travelersSlider.addEventListener('input', calculate);
  tierRadios.forEach(r => r.addEventListener('change', calculate));
  destTypeRadios.forEach(r => r.addEventListener('change', calculate));

  // Run initial calculation
  calculate();
}
