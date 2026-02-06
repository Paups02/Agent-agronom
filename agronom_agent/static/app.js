/* AgroNom Agent — Frontend SaaS */

const API = window.location.origin;

/* ===== NAVIGATION ===== */
function showSection(id) {
  document.querySelectorAll('.hero, .section').forEach(s => s.classList.remove('hidden'));
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ===== FORM WIZARD ===== */
function nextStep(step) {
  document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
  document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');

  document.querySelectorAll('.step-indicator').forEach(ind => {
    const s = parseInt(ind.dataset.step);
    ind.classList.remove('active', 'done');
    if (s === step) ind.classList.add('active');
    else if (s < step) ind.classList.add('done');
  });
}

/* ===== LOAD CROPS ===== */
async function loadCrops() {
  try {
    const res = await fetch(`${API}/crops`);
    const data = await res.json();
    const select = document.getElementById('crop_name');
    const grid = document.getElementById('crops-grid');

    data.crops.forEach(name => {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name.charAt(0).toUpperCase() + name.slice(1);
      select.appendChild(opt);
    });

    // Load crop cards
    for (const name of data.crops) {
      try {
        const cres = await fetch(`${API}/crops/${encodeURIComponent(name)}`);
        const crop = await cres.json();
        grid.innerHTML += renderCropCard(name, crop);
      } catch (e) {
        // skip
      }
    }
  } catch (e) {
    console.error('Error loading crops:', e);
  }
}

function renderCropCard(name, crop) {
  return `
    <div class="crop-card">
      <h3>${crop.crop_name}</h3>
      <div class="crop-info">
        <span>pH òptim <strong>${crop.optimal_ph_min} – ${crop.optimal_ph_max}</strong></span>
        <span>Nitrogen <strong>${crop.nitrogen_kg_ha} kg/ha</strong></span>
        <span>Fòsfor <strong>${crop.phosphorus_kg_ha} kg/ha</strong></span>
        <span>Potassi <strong>${crop.potassium_kg_ha} kg/ha</strong></span>
        <span>Aigua <strong>${crop.water_mm_cycle} mm/cicle</strong></span>
        <span>Temp. òptima <strong>${crop.optimal_temp_min}–${crop.optimal_temp_max}°C</strong></span>
      </div>
    </div>
  `;
}

/* ===== SUBMIT DIAGNOSIS ===== */
async function submitDiagnosis() {
  const btn = document.getElementById('submit-btn');
  const loading = document.getElementById('loading');
  const results = document.getElementById('results');
  const wizard = document.querySelector('.form-wizard');

  btn.disabled = true;
  btn.textContent = 'Analitzant...';
  loading.classList.remove('hidden');
  results.classList.add('hidden');

  const payload = {
    soil: {
      ph: parseFloat(document.getElementById('ph').value),
      organic_matter: parseFloat(document.getElementById('organic_matter').value),
      nitrogen_ppm: parseFloat(document.getElementById('nitrogen_ppm').value),
      phosphorus_ppm: parseFloat(document.getElementById('phosphorus_ppm').value),
      potassium_ppm: parseFloat(document.getElementById('potassium_ppm').value),
      texture: document.getElementById('texture').value,
      electrical_conductivity: parseFloat(document.getElementById('ec').value),
    },
    crop: {
      name: document.getElementById('crop_name').value,
      category: 'hortalisses',
      growth_stage: document.getElementById('growth_stage').value,
      area_hectares: parseFloat(document.getElementById('area').value),
      irrigation_type: document.getElementById('irrigation_type').value,
      previous_crop: document.getElementById('previous_crop').value || '',
    },
    weather: {
      temperature_c: parseFloat(document.getElementById('temp').value),
      temp_min_c: parseFloat(document.getElementById('temp_min').value),
      temp_max_c: parseFloat(document.getElementById('temp_max').value),
      humidity_percent: parseFloat(document.getElementById('humidity').value),
      precipitation_mm: parseFloat(document.getElementById('rain').value),
      eto_mm: parseFloat(document.getElementById('eto').value),
    },
  };

  try {
    const res = await fetch(`${API}/diagnosis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Error al servidor');
    }

    const report = await res.json();
    loading.classList.add('hidden');
    wizard.classList.add('hidden');
    results.classList.remove('hidden');
    results.innerHTML = renderReport(report);
    results.scrollIntoView({ behavior: 'smooth' });
  } catch (e) {
    loading.classList.add('hidden');
    results.classList.remove('hidden');
    results.innerHTML = `<div class="result-block"><div class="result-block-body"><p style="color:var(--red-500)">Error: ${e.message}</p></div></div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Generar Diagnòstic Complet';
  }
}

/* ===== RENDER REPORT ===== */
function renderReport(r) {
  const scoreClass = r.soil_score >= 70 ? 'score-high' : r.soil_score >= 40 ? 'score-mid' : 'score-low';
  const scoreLabel = r.soil_score >= 70 ? 'Bon estat' : r.soil_score >= 40 ? 'Millorable' : 'Atenció urgent';

  let html = '';

  // Header with score
  html += `
    <div class="result-header ${scoreClass}">
      <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
        <div class="score-circle"><span>${r.soil_score}</span><small>/100</small></div>
        <div class="result-header-text">
          <h3>Informe Agronòmic — ${r.crop_name}</h3>
          <p>Finca ${r.farm_id} · Salut del sòl: ${scoreLabel}</p>
        </div>
      </div>
      <button class="btn btn-secondary" onclick="resetForm()">Nou diagnòstic</button>
    </div>
  `;

  // Priority actions
  html += `
    <div class="result-block">
      <div class="result-block-header"><span class="icon">🎯</span> Accions Prioritàries (${r.priority_actions.length})</div>
      <div class="result-block-body">
        <ul class="action-list">
          ${r.priority_actions.map(a => {
            let cls = 'action-planned';
            if (a.includes('[URGENT]')) cls = 'action-urgent';
            else if (a.includes('[IMPORTANT]')) cls = 'action-important';
            else if (a.includes('[CORRECCIÓ]')) cls = 'action-correction';
            return `<li class="${cls}">${a}</li>`;
          }).join('')}
        </ul>
      </div>
    </div>
  `;

  // Phytosanitary alerts
  if (r.active_alerts && r.active_alerts.length > 0) {
    html += `
      <div class="result-block">
        <div class="result-block-header"><span class="icon">🐛</span> Alertes Fitosanitàries (${r.active_alerts.length})</div>
        <div class="result-block-body">
          ${r.active_alerts.map(a => `
            <div class="alert-card severity-${a.severity}">
              <h4>${a.pest_name}</h4>
              <span class="alert-severity">${a.severity.toUpperCase()} — Actuar en ${a.action_deadline_days} dies</span>
              <p class="alert-detail">${a.conditions_favoring}</p>
              <p class="alert-detail"><strong>Símptomes:</strong> ${a.symptoms.join(', ')}</p>
              <div class="treatment-group">
                <strong>Prevenció</strong>
                <ul>${a.preventive_measures.map(m => `<li>${m}</li>`).join('')}</ul>
              </div>
              <div class="treatment-group">
                <strong>Tractament curatiu</strong>
                <ul>${a.curative_treatments.map(m => `<li>${m}</li>`).join('')}</ul>
              </div>
              <div class="treatment-group">
                <strong>Alternatives ecològiques</strong>
                <ul>${a.organic_alternatives.map(m => `<li>${m}</li>`).join('')}</ul>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  // Fertilization
  if (r.fertilization_plan) {
    const fp = r.fertilization_plan;
    html += `
      <div class="result-block">
        <div class="result-block-header"><span class="icon">🧪</span> Pla de Fertilització</div>
        <div class="result-block-body">
          <table class="data-table">
            <tr><th>Paràmetre</th><th>Valor</th></tr>
            <tr><td>Nitrogen (N)</td><td><strong>${fp.nitrogen_kg_ha} kg/ha</strong></td></tr>
            <tr><td>Fòsfor (P)</td><td><strong>${fp.phosphorus_kg_ha} kg/ha</strong></td></tr>
            <tr><td>Potassi (K)</td><td><strong>${fp.potassium_kg_ha} kg/ha</strong></td></tr>
            <tr><td>Mètode</td><td>${fp.application_method}</td></tr>
            <tr><td>Moment</td><td>${fp.timing}</td></tr>
            <tr><td>Cost estimat</td><td><strong>${fp.estimated_cost_eur_ha} €/ha</strong></td></tr>
          </table>
          <div style="margin-top:16px;">
            <strong style="font-size:.88rem;color:var(--gray-700);">Productes recomanats:</strong>
            <ul class="note-list" style="margin-top:8px;">
              ${fp.recommended_products.map(p => `<li>${p}</li>`).join('')}
            </ul>
          </div>
          ${fp.organic_alternatives.length ? `
            <div style="margin-top:12px;">
              <strong style="font-size:.88rem;color:var(--gray-700);">Alternatives ecològiques:</strong>
              <ul class="note-list" style="margin-top:8px;">
                ${fp.organic_alternatives.map(p => `<li>${p}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${fp.notes.length ? `
            <div style="margin-top:12px;">
              <strong style="font-size:.88rem;color:var(--gray-700);">Notes:</strong>
              <ul class="note-list" style="margin-top:8px;">
                ${fp.notes.map(n => `<li>${n}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  // Irrigation
  if (r.irrigation_plan) {
    const ip = r.irrigation_plan;
    html += `
      <div class="result-block">
        <div class="result-block-header"><span class="icon">💧</span> Pla de Reg</div>
        <div class="result-block-body">
          <table class="data-table">
            <tr><th>Paràmetre</th><th>Valor</th></tr>
            <tr><td>Necessitat diària</td><td><strong>${ip.daily_water_need_mm} mm/dia</strong></td></tr>
            <tr><td>Dosi per reg</td><td><strong>${ip.gross_dose_mm} mm</strong></td></tr>
            <tr><td>Freqüència</td><td>Cada ${ip.irrigation_frequency_days} dia/es</td></tr>
            <tr><td>Total mensual</td><td><strong>${ip.monthly_total_m3_ha} m³/ha</strong></td></tr>
            <tr><td>Eficiència del sistema</td><td>${(ip.efficiency_factor * 100).toFixed(0)}%</td></tr>
          </table>
          ${ip.notes && ip.notes.length ? `
            <ul class="note-list" style="margin-top:16px;">
              ${ip.notes.map(n => `<li>${n}</li>`).join('')}
            </ul>
          ` : ''}
        </div>
      </div>
    `;
  }

  // Climate risks
  if (r.climate_risks && r.climate_risks.length > 0) {
    html += `
      <div class="result-block">
        <div class="result-block-header"><span class="icon">🌡️</span> Riscos Climàtics</div>
        <div class="result-block-body">
          <ul class="note-list">
            ${r.climate_risks.map(c => `<li>${c}</li>`).join('')}
          </ul>
        </div>
      </div>
    `;
  }

  // Savings
  if (r.estimated_savings_eur > 0) {
    html += `
      <div class="result-block">
        <div class="result-block-header"><span class="icon">💰</span> Estalvi Estimat</div>
        <div class="result-block-body">
          <p style="font-size:1.3rem;font-weight:800;color:var(--green-700);">${r.estimated_savings_eur} € d'estalvi estimat</p>
          <p style="color:var(--gray-500);font-size:.9rem;margin-top:4px;">Comparant amb fertilització genèrica sense assessoria.</p>
        </div>
      </div>
    `;
  }

  return html;
}

/* ===== RESET ===== */
function resetForm() {
  document.getElementById('results').classList.add('hidden');
  document.querySelector('.form-wizard').classList.remove('hidden');
  nextStep(1);
  document.querySelector('.form-wizard').scrollIntoView({ behavior: 'smooth' });
}

/* ===== INIT ===== */
document.addEventListener('DOMContentLoaded', loadCrops);
