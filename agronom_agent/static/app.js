/* AgroNom Agent v2.0 — Frontend SaaS amb gràfics, economia i xat IA */

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

/* ===== SUBMIT DIAGNOSIS (v2 — /report amb gràfics i economia) ===== */
async function submitDiagnosis() {
  const btn = document.getElementById('submit-btn');
  const loading = document.getElementById('loading');
  const results = document.getElementById('results');
  const wizard = document.querySelector('.form-wizard');

  btn.disabled = true;
  btn.textContent = 'Generant informe...';
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
    const res = await fetch(`${API}/report`, {
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
    btn.textContent = 'Generar Informe Complet amb Gràfics';
  }
}

/* ===== RENDER REPORT (v2 — amb gràfics i economia) ===== */
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

  // Charts section
  if (r.charts) {
    html += `
      <div class="result-block">
        <div class="result-block-header"><span class="icon">📊</span> Gràfics d'Anàlisi</div>
        <div class="result-block-body">
          <div class="charts-grid">
            ${r.charts.soil_radar ? `
              <div class="chart-card">
                <img src="data:image/png;base64,${r.charts.soil_radar}" alt="Radar salut del sòl">
                <div class="chart-label">Salut del Sòl</div>
              </div>
            ` : ''}
            ${r.charts.npk_chart ? `
              <div class="chart-card">
                <img src="data:image/png;base64,${r.charts.npk_chart}" alt="Pla NPK">
                <div class="chart-label">Fertilització NPK</div>
              </div>
            ` : ''}
            ${r.charts.irrigation_chart ? `
              <div class="chart-card">
                <img src="data:image/png;base64,${r.charts.irrigation_chart}" alt="Necessitats hídriques">
                <div class="chart-label">Necessitats Hídriques</div>
              </div>
            ` : ''}
            ${r.charts.economic_chart ? `
              <div class="chart-card">
                <img src="data:image/png;base64,${r.charts.economic_chart}" alt="Comparativa econòmica">
                <div class="chart-label">Comparativa Econòmica</div>
              </div>
            ` : ''}
          </div>
        </div>
      </div>
    `;
  }

  // Economics section
  if (r.economics) {
    const e = r.economics;
    html += `
      <div class="result-block">
        <div class="result-block-header"><span class="icon">💰</span> Anàlisi Econòmica — ${e.crop_name} (${e.area_hectares} ha)</div>
        <div class="result-block-body">
          <div class="econ-grid">
            <div class="econ-card highlight">
              <div class="econ-value">${formatEur(e.annual_profit_eur)}</div>
              <div class="econ-label">Benefici anual estimat</div>
            </div>
            <div class="econ-card highlight">
              <div class="econ-value">${e.roi_percent}%</div>
              <div class="econ-label">ROI assessoria</div>
            </div>
            <div class="econ-card">
              <div class="econ-value">${formatEur(e.extra_profit_eur_ha)}</div>
              <div class="econ-label">Benefici extra per ha</div>
            </div>
            <div class="econ-card">
              <div class="econ-value">${formatEur(e.total_savings_eur)}</div>
              <div class="econ-label">Estalvi total finca</div>
            </div>
          </div>

          <table class="econ-table">
            <tr><th>Concepte</th><th>Amb AgroNom</th><th>Sense assessoria</th><th>Estalvi</th></tr>
            <tr>
              <td>Fertilitzants</td>
              <td>${formatEur(e.fert_cost_with)}/ha</td>
              <td>${formatEur(e.fert_cost_without)}/ha</td>
              <td class="saving">${formatEur(e.fert_cost_without - e.fert_cost_with)}/ha</td>
            </tr>
            <tr>
              <td>Fitosanitaris</td>
              <td>${formatEur(e.phyto_cost_with)}/ha</td>
              <td>${formatEur(e.phyto_cost_without)}/ha</td>
              <td class="saving">${formatEur(e.phyto_cost_without - e.phyto_cost_with)}/ha</td>
            </tr>
            <tr>
              <td>Reg</td>
              <td>${formatEur(e.irrig_cost_with)}/ha</td>
              <td>${formatEur(e.irrig_cost_without)}/ha</td>
              <td class="saving">${formatEur(e.irrig_cost_without - e.irrig_cost_with)}/ha</td>
            </tr>
            <tr style="font-weight:700;border-top:2px solid var(--gray-200);">
              <td>Marge net</td>
              <td>${formatEur(e.margin_with_eur_ha)}/ha</td>
              <td>${formatEur(e.margin_without_eur_ha)}/ha</td>
              <td class="saving">${formatEur(e.extra_profit_eur_ha)}/ha</td>
            </tr>
          </table>

          <div class="econ-grid" style="margin-top:20px;">
            <div class="econ-card">
              <div class="econ-value">${e.expected_yield_kg_ha} kg</div>
              <div class="econ-label">Rendiment esperat/ha</div>
            </div>
            <div class="econ-card">
              <div class="econ-value">${formatEur(e.gross_income_eur_ha)}</div>
              <div class="econ-label">Ingressos bruts/ha</div>
            </div>
            <div class="econ-card">
              <div class="econ-value">${e.water_saved_m3_ha} m³</div>
              <div class="econ-label">Aigua estalviada/ha</div>
            </div>
            <div class="econ-card">
              <div class="econ-value">${e.fertilizer_saved_kg_ha} kg</div>
              <div class="econ-label">Fertilitzant estalviat/ha</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

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

  return html;
}

/* ===== FORMAT HELPERS ===== */
function formatEur(val) {
  if (val == null) return '—';
  return new Intl.NumberFormat('ca-ES', {
    style: 'currency', currency: 'EUR',
    minimumFractionDigits: 0, maximumFractionDigits: 0,
  }).format(val);
}

/* ===== CHAT IA ===== */
async function sendChat() {
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');
  const sendBtn = document.getElementById('chat-send-btn');
  const question = input.value.trim();

  if (!question) return;

  // Add user message
  messages.innerHTML += `
    <div class="chat-msg user">
      <div class="chat-avatar">👤</div>
      <div class="chat-bubble">
        <strong>Tu</strong>
        <p>${escapeHtml(question)}</p>
      </div>
    </div>
  `;
  input.value = '';
  sendBtn.disabled = true;
  sendBtn.textContent = 'Pensant...';
  messages.scrollTop = messages.scrollHeight;

  try {
    const apiKey = document.getElementById('gemini-key').value.trim();
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question,
        context: '',
        api_key: apiKey,
      }),
    });

    if (!res.ok) throw new Error('Error del servidor');

    const data = await res.json();
    messages.innerHTML += `
      <div class="chat-msg bot">
        <div class="chat-avatar">🌱</div>
        <div class="chat-bubble">
          <strong>AgroNom IA</strong>
          <p>${formatMarkdown(data.answer)}</p>
        </div>
      </div>
    `;
  } catch (e) {
    messages.innerHTML += `
      <div class="chat-msg bot">
        <div class="chat-avatar">🌱</div>
        <div class="chat-bubble">
          <strong>AgroNom IA</strong>
          <p style="color:var(--red-500)">Error de connexió. Torna-ho a provar.</p>
        </div>
      </div>
    `;
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = 'Enviar';
    messages.scrollTop = messages.scrollHeight;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatMarkdown(text) {
  // Basic markdown: bold, lists
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n- /g, '\n• ')
    .replace(/\n(\d+)\. /g, '\n$1. ');
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
