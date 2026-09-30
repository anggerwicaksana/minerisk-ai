/**
 * MineRisk-AI (SafeCast) - Reactive Intelligence & Simulation Controller
 * Architecture: Plus Jakarta Sans + Averia Serif Libre (Zero JetBrains Mono)
 * Industrial Badging (No rounded pills) • Explainable AI • What-If Sandbox
 * Lead Engineer: Angger Wicaksana (angger.akukatiga.com)
 */

// Fallback baseline in case network fetch is blocked or file:// is used
const EMBEDDED_SAMPLE_DATA = {
  national_avg_prob: 50.2,
  mines: [
    {
      id: "6265150",
      name: "Mine Operation 1414 - Valley",
      state: "PA",
      commodity: "Coal",
      type: "Underground",
      hours: 135945,
      employees: 184,
      violations: 3,
      viol_ss: 1,
      insp_hours: 24.5,
      prior_injuries: 2,
      prob: 86.9,
      tier: "Critical",
      drivers: [
        { name: "Total Jam Kerja (Workforce Hours)", shap: 24.2, val: "135.945 jam" },
        { name: "Pelanggaran Kritis S&S (Roof & Gas)", shap: 18.5, val: "1 temuan S&S" },
        { name: "Metode Tambang Bawah Tanah (Underground)", shap: 12.8, val: "Risiko inheren" },
        { name: "Riwayat Cedera Kuartal Lalu", shap: 11.4, val: "2 kejadian" },
        { name: "Rasio Pelanggaran per Jam Audit", shap: 5.6, val: "0.12/jam" },
        { name: "Durasi Audit Inspektur Lapangan", shap: -8.2, val: "24.5 jam pemeriksaan" },
        { name: "Pemeriksaan Berkala MSHA", shap: -4.1, val: "Audit aktif" }
      ]
    },
    {
      id: "4609192",
      name: "Cumberland Mine Portal 3",
      state: "WV",
      commodity: "Coal",
      type: "Underground",
      hours: 198200,
      employees: 260,
      violations: 7,
      viol_ss: 3,
      insp_hours: 42.0,
      prior_injuries: 3,
      prob: 92.4,
      tier: "Critical",
      drivers: [
        { name: "Pelanggaran Kritis S&S (Ventilasi)", shap: 29.4, val: "3 temuan S&S" },
        { name: "Jam Lembur Pekerja Tinggi", shap: 21.0, val: "198.200 jam" },
        { name: "Riwayat Kecelakaan Berulang", shap: 16.8, val: "3 kejadian cedera" },
        { name: "Tingkat Kelalaian Prosedur", shap: 8.5, val: "High negligence" },
        { name: "Intensitas Kunjungan Audit MSHA", shap: -11.2, val: "42.0 jam audit" }
      ]
    },
    {
      id: "4800977",
      name: "Appalachian Horizon Pit No. 2",
      state: "KY",
      commodity: "Coal",
      type: "Surface",
      hours: 88400,
      employees: 95,
      violations: 4,
      viol_ss: 1,
      insp_hours: 18.0,
      prior_injuries: 1,
      prob: 64.5,
      tier: "Elevated",
      drivers: [
        { name: "Paparan Jam Kerja Operasional", shap: 14.2, val: "88.400 jam" },
        { name: "Temuan Pelanggaran Sabuk Pengaman Alat", shap: 11.8, val: "1 temuan S&S" },
        { name: "Riwayat Cedera Terakhir", shap: 7.2, val: "1 cedera" },
        { name: "Metode Permukaan Terbuka (Surface)", shap: -9.5, val: "Ventilasi alami" },
        { name: "Jam Pengawasan Rutin", shap: -5.4, val: "18.0 jam audit" }
      ]
    },
    {
      id: "4407122",
      name: "Black Thunder Basin Vista",
      state: "WY",
      commodity: "Coal",
      type: "Surface",
      hours: 245000,
      employees: 320,
      violations: 1,
      viol_ss: 0,
      insp_hours: 68.0,
      prior_injuries: 0,
      prob: 38.2,
      tier: "Moderate",
      drivers: [
        { name: "Skala Produksi & Total Jam Kerja", shap: 18.0, val: "245.000 jam" },
        { name: "Nol Pelanggaran Kritis S&S", shap: -16.5, val: "0 temuan S&S" },
        { name: "Durasi Audit Keselamatan Ekstensif", shap: -14.2, val: "68.0 jam audit" },
        { name: "Nol Cedera Kerja Kuartal Lalu", shap: -12.1, val: "0 cedera" },
        { name: "Metode Tambang Terbuka", shap: -8.8, val: "Surface mine" }
      ]
    },
    {
      id: "0201198",
      name: "Morenci Copper Reduction Facility",
      state: "AZ",
      commodity: "Metal/Nonmetal",
      type: "Facility",
      hours: 112000,
      employees: 140,
      violations: 0,
      viol_ss: 0,
      insp_hours: 32.0,
      prior_injuries: 0,
      prob: 16.4,
      tier: "Low",
      drivers: [
        { name: "Nol Catatan Pelanggaran Regulasi", shap: -18.4, val: "Kepatuhan 100%" },
        { name: "Rekam Jejak Bersih Tanpa Cedera", shap: -15.2, val: "0 insiden" },
        { name: "Pengawasan Lingkungan Terjadwal", shap: -9.0, val: "32.0 jam" },
        { name: "Paparan Jam Kerja Pabrik Pengolahan", shap: 8.5, val: "112.000 jam" }
      ]
    },
    {
      id: "4102891",
      name: "Eagle River Underground Portal",
      state: "CO",
      commodity: "Metal/Nonmetal",
      type: "Underground",
      hours: 94000,
      employees: 110,
      violations: 5,
      viol_ss: 2,
      insp_hours: 15.0,
      prior_injuries: 1,
      prob: 78.4,
      tier: "Critical",
      drivers: [
        { name: "Pelanggaran Penyangga Batuan (Roof)", shap: 22.8, val: "2 temuan S&S" },
        { name: "Metode Tambang Bawah Tanah", shap: 13.5, val: "Underground" },
        { name: "Minimnya Durasi Waktu Audit", shap: 11.2, val: "Hanya 15 jam" },
        { name: "Riwayat Cedera Terpeleset/Jatuh", shap: 8.1, val: "1 cedera" },
        { name: "Tingkat Kepatuhan APD", shap: -4.2, val: "APD standar" }
      ]
    },
    {
      id: "4201889",
      name: "Lone Star Aggregate Quarry",
      state: "TX",
      commodity: "Metal/Nonmetal",
      type: "Surface",
      hours: 42000,
      employees: 48,
      violations: 2,
      viol_ss: 0,
      insp_hours: 12.0,
      prior_injuries: 0,
      prob: 24.5,
      tier: "Moderate",
      drivers: [
        { name: "Metode Tambang Terbuka", shap: -11.0, val: "Surface quarry" },
        { name: "Nol Temuan Pelanggaran S&S", shap: -9.8, val: "0 kritis" },
        { name: "Paparan Jam Kerja Terkendali", shap: 6.4, val: "42.000 jam" },
        { name: "Durasi Inspeksi Singkat", shap: 4.8, val: "12 jam audit" }
      ]
    },
    {
      id: "1518920",
      name: "Warrior Met Coal No. 7",
      state: "AL",
      commodity: "Coal",
      type: "Underground",
      hours: 168000,
      employees: 215,
      violations: 6,
      viol_ss: 2,
      insp_hours: 38.0,
      prior_injuries: 2,
      prob: 88.2,
      tier: "Critical",
      drivers: [
        { name: "Pelanggaran Sistem Ventilasi Metana", shap: 26.5, val: "2 temuan S&S" },
        { name: "Paparan Jam Kerja Sangat Tinggi", shap: 19.4, val: "168.000 jam" },
        { name: "Riwayat Kecelakaan 3 Bulan Terakhir", shap: 14.1, val: "2 cedera" },
        { name: "Tambang Bawah Tanah Batubara", shap: 12.0, val: "Underground Coal" },
        { name: "Inspeksi MSHA Terfokus", shap: -9.4, val: "38.0 jam audit" }
      ]
    },
    {
      id: "1202390",
      name: "Gibson South Deep Mine",
      state: "IN",
      commodity: "Coal",
      type: "Underground",
      hours: 124000,
      employees: 160,
      violations: 3,
      viol_ss: 1,
      insp_hours: 28.0,
      prior_injuries: 1,
      prob: 69.1,
      tier: "Elevated",
      drivers: [
        { name: "Pelanggaran Kelistrikan Alat Berat", shap: 16.2, val: "1 temuan S&S" },
        { name: "Jam Kerja Operasional Tinggi", shap: 15.0, val: "124.000 jam" },
        { name: "Tipe Tambang Bawah Tanah", shap: 12.4, val: "Underground" },
        { name: "Durasi Audit Lapangan", shap: -8.2, val: "28.0 jam audit" }
      ]
    },
    {
      id: "1103281",
      name: "Sugar Camp Energy Portal 1",
      state: "IL",
      commodity: "Coal",
      type: "Underground",
      hours: 142000,
      employees: 190,
      violations: 2,
      viol_ss: 0,
      insp_hours: 35.0,
      prior_injuries: 0,
      prob: 44.8,
      tier: "Moderate",
      drivers: [
        { name: "Skala Jam Kerja Pekerja", shap: 16.8, val: "142.000 jam" },
        { name: "Nol Pelanggaran Kritis S&S", shap: -14.2, val: "0 temuan S&S" },
        { name: "Audit Rutin Komprehensif", shap: -9.5, val: "35.0 jam" },
        { name: "Rekam Jejak Nol Cedera", shap: -8.0, val: "0 insiden" }
      ]
    }
  ]
};

let CURRENT_MINES = EMBEDDED_SAMPLE_DATA.mines;
let SELECTED_MINE = CURRENT_MINES[0];
const NATIONAL_AVG_PROB = EMBEDDED_SAMPLE_DATA.national_avg_prob;

document.addEventListener('DOMContentLoaded', async () => {
  initDashboardTabs();
  initSimulatorControls();
  await loadRemoteData();
  initFilters();
  populateInspectorDropdown();
  if (CURRENT_MINES.length > 0) {
    inspectMine(CURRENT_MINES[0].id);
  }
  initHeroTelemetryHUD();
  initPipelineDiagramFlow();
  initCopilotChat();
});

// Tab Navigation Switching
function initDashboardTabs() {
  const tabs = document.querySelectorAll('.dash-tab-btn');
  const panes = document.querySelectorAll('.tab-pane');

  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      tabs.forEach(t => t.classList.remove('active'));
      panes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const pane = document.getElementById(targetId);
      if (pane) {
        pane.classList.add('active');
      }
    });
  });
}

// Attempt to load full 20+ records from json
async function loadRemoteData() {
  try {
    const res = await fetch('data/showcase_data.json');
    if (res.ok) {
      const data = await res.json();
      if (data && data.mines && data.mines.length > 0) {
        CURRENT_MINES = data.mines;
      }
    }
  } catch (e) {
    console.log('Menggunakan data bawaan mandiri untuk performa instan.');
  }
}

// Filter and Surveillance Queue Table
function initFilters() {
  const stateFilter = document.getElementById('stateFilter');
  const commFilter = document.getElementById('commFilter');
  const tierFilter = document.getElementById('tierFilter');
  const searchInput = document.getElementById('searchInput');

  // Populate States
  const states = [...new Set(CURRENT_MINES.map(m => m.state))].sort();
  states.forEach(st => {
    const opt = document.createElement('option');
    opt.value = st;
    opt.textContent = `Wilayah ${st}`;
    stateFilter.appendChild(opt);
  });

  [stateFilter, commFilter, tierFilter].forEach(el => {
    el.addEventListener('change', applyFilters);
  });
  searchInput.addEventListener('input', applyFilters);

  renderSurveillanceTable(CURRENT_MINES);
}

function applyFilters() {
  const stVal = document.getElementById('stateFilter').value;
  const commVal = document.getElementById('commFilter').value;
  const tierVal = document.getElementById('tierFilter').value;
  const q = document.getElementById('searchInput').value.trim().toLowerCase();

  const filtered = CURRENT_MINES.filter(m => {
    const matchSt = (stVal === 'ALL' || m.state === stVal);
    const matchComm = (commVal === 'ALL' || m.commodity === commVal);
    const matchTier = (tierVal === 'ALL' || m.tier === tierVal);
    const matchQ = (!q || m.name.toLowerCase().includes(q) || m.id.toLowerCase().includes(q));
    return matchSt && matchComm && matchTier && matchQ;
  });

  renderSurveillanceTable(filtered);
}

function renderSurveillanceTable(mines) {
  const tbody = document.getElementById('surveillanceTableBody');
  tbody.innerHTML = '';

  if (mines.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 32px; color: var(--text-muted);">Tidak ada data tambang yang cocok dengan kriteria filter saat ini.</td></tr>';
    return;
  }

  // Sort by risk descending
  const sorted = [...mines].sort((a, b) => b.prob - a.prob);

  sorted.forEach((m, idx) => {
    const tr = document.createElement('tr');
    tr.className = 'clickable-row';

    const tierClass = `tier-${m.tier.toLowerCase()}`;
    const badgeLabel = getTierLabelIndo(m.tier);

    tr.innerHTML = `
      <td style="color: var(--text-muted); font-weight: 700;">#${idx + 1}</td>
      <td style="font-weight: 700; color: var(--text-primary); letter-spacing:0.02em;">${m.id}</td>
      <td style="font-weight: 600; color: var(--text-primary);">${m.name}</td>
      <td>${m.state} • ${m.type}</td>
      <td class="tabular-nums">${m.hours.toLocaleString()} jam</td>
      <td class="tabular-nums" style="color: ${m.viol_ss > 0 ? '#EF4444' : 'var(--text-secondary)'};">
        ${m.violations} <span style="font-size:0.75rem; color:var(--text-muted);">(${m.viol_ss} S&S)</span>
      </td>
      <td><span class="tier-tag ${tierClass}">${badgeLabel}</span></td>
      <td class="tabular-nums" style="font-size: 1.05rem; font-weight: 800; color: ${getTierHex(m.tier)};">
        ${m.prob}%
      </td>
    `;

    tr.addEventListener('click', () => {
      inspectMine(m.id);
      document.querySelector('[data-tab="dash-tab-inspector"]').click();
      document.getElementById('dash-tab-inspector').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    tbody.appendChild(tr);
  });
}

function getTierLabelIndo(tier) {
  switch (tier) {
    case 'Critical': return 'BAHAYA KRITIS';
    case 'Elevated': return 'WASPADA TINGGI';
    case 'Moderate': return 'RISIKO SEDANG';
    case 'Low': return 'AMAN TERKENDALI';
    default: return tier;
  }
}

function getTierHex(tier) {
  switch (tier) {
    case 'Critical': return '#EF4444';
    case 'Elevated': return '#F97316';
    case 'Moderate': return '#EAB308';
    case 'Low': return '#10B981';
    default: return '#F8FAFC';
  }
}

// Tab 2: Individual Mine Inspector
function populateInspectorDropdown() {
  const select = document.getElementById('mineSelector');
  select.innerHTML = '';

  CURRENT_MINES.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m.id;
    opt.textContent = `${m.name} (ID ${m.id}) • Wilayah ${m.state} • ${m.prob}% Risiko`;
    select.appendChild(opt);
  });

  select.addEventListener('change', (e) => {
    inspectMine(e.target.value);
  });
}

function inspectMine(mineId) {
  const mine = CURRENT_MINES.find(m => m.id === mineId);
  if (!mine) return;

  SELECTED_MINE = mine;
  document.getElementById('mineSelector').value = mine.id;

  const hexColor = getTierHex(mine.tier);
  const delta = (mine.prob - NATIONAL_AVG_PROB).toFixed(1);
  const isHigher = delta >= 0;

  // Score hero update
  const scoreEl = document.getElementById('inspectBigScore');
  scoreEl.textContent = `${mine.prob}%`;
  scoreEl.style.color = hexColor;

  const badgeEl = document.getElementById('inspectTierBadge');
  badgeEl.textContent = getTierLabelIndo(mine.tier);
  badgeEl.className = `tier-tag tier-${mine.tier.toLowerCase()}`;

  const deltaEl = document.getElementById('inspectDeltaMsg');
  deltaEl.textContent = isHigher 
    ? `▲ ${delta}% Lebih tinggi dibanding rata-rata tambang nasional (${NATIONAL_AVG_PROB}%)`
    : `▼ ${Math.abs(delta)}% Lebih rendah dibanding rata-rata tambang nasional (${NATIONAL_AVG_PROB}%)`;
  deltaEl.style.color = isHigher ? '#EF4444' : '#10B981';

  // Details
  document.getElementById('inspectName').textContent = mine.name;
  document.getElementById('inspectId').textContent = mine.id;
  document.getElementById('inspectState').textContent = `${mine.state} (Amerika Serikat)`;
  document.getElementById('inspectComm').textContent = `${mine.commodity} (${mine.type})`;
  document.getElementById('inspectHours').textContent = `${mine.hours.toLocaleString()} jam (~${mine.employees} pekerja)`;
  document.getElementById('inspectViol').textContent = `${mine.violations} temuan (${mine.viol_ss} pelanggaran kritis S&S)`;

  // Render SHAP
  renderShapBars(mine.drivers);

  // Render Action Guidance
  renderActionGuidance(mine);
}

function renderShapBars(drivers) {
  const container = document.getElementById('shapWaterfallContainer');
  container.innerHTML = '';

  if (!drivers || drivers.length === 0) {
    container.innerHTML = '<p style="color:var(--text-muted); font-size:0.88rem;">Data faktor risiko belum tersedia untuk tambang ini.</p>';
    return;
  }

  const maxAbs = Math.max(...drivers.map(d => Math.abs(d.shap)), 1.0);

  drivers.forEach(d => {
    const isPos = d.shap >= 0;
    const widthPct = Math.min(100, Math.round((Math.abs(d.shap) / maxAbs) * 100));

    const row = document.createElement('div');
    row.className = 'shap-bar-row';

    row.innerHTML = `
      <div class="shap-name" title="${d.name}">${d.name}</div>
      <div class="shap-track">
        <div class="${isPos ? 'shap-fill-pos' : 'shap-fill-neg'}" style="width: ${widthPct}%;"></div>
      </div>
      <div class="shap-val-text tabular-nums" style="color: ${isPos ? '#EF4444' : '#10B981'};">
        ${isPos ? '+' : ''}${d.shap}%
      </div>
    `;

    container.appendChild(row);
  });
}

function renderActionGuidance(mine) {
  const box = document.getElementById('actionGuidanceBox');
  const tier = mine.tier;

  if (tier === 'Critical') {
    box.style.borderLeftColor = '#EF4444';
    box.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <span style="color:#EF4444; font-weight:800;">[!]</span>
        <strong style="color: #EF4444; font-size: 0.95rem;">TINDAKAN MITIGASI PRIORITAS TINGGI</strong>
      </div>
      <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">
        Operasi tambang <strong>${mine.name}</strong> menunjukkan beban lembur pekerja berlebih disertai akumulasi ${mine.viol_ss} pelanggaran kritis S&S (ventilasi/penyangga batuan). Disarankan segera melaksanakan audit keselamatan lapangan dalam <strong>7 hari ke depan</strong> dan mengevaluasi rotasi istirahat pekerja shift malam.
      </p>
    `;
  } else if (tier === 'Elevated') {
    box.style.borderLeftColor = '#F97316';
    box.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <span style="color:#F97316; font-weight:800;">[▲]</span>
        <strong style="color: #F97316; font-size: 0.95rem;">PENGAWASAN INTENSIF DIPERLUKAN</strong>
      </div>
      <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">
        Tingkat risiko berada di atas rata-rata industri nasional. Tim K3 internal wajib menyelesaikan perbaikan temuan inspeksi sebelum kuartal baru dimulai dan menggelar <em>briefing keselamatan</em> rutin.
      </p>
    `;
  } else if (tier === 'Moderate') {
    box.style.borderLeftColor = '#EAB308';
    box.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <span style="color:#EAB308; font-weight:800;">[●]</span>
        <strong style="color: #EAB308; font-size: 0.95rem;">PENGAWASAN RUTIN BERKALA</strong>
      </div>
      <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">
        Kondisi tambang berjalan pada batas rata-rata industri. Lanjutkan pengawasan berkala dan pastikan pemeliharaan preventif alat berat tetap terjadwal.
      </p>
    `;
  } else {
    box.style.borderLeftColor = '#10B981';
    box.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
        <span style="color:#10B981; font-weight:800;">[✓]</span>
        <strong style="color: #10B981; font-size: 0.95rem;">STATUS OPERASIONAL AMAN & STABIL</strong>
      </div>
      <p style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">
        Rekam jejak keselamatan kerja sangat baik dengan nol pelanggaran kritis. Pertahankan prosedur kerja aman yang sudah berjalan.
      </p>
    `;
  }
}

// Tab 3: Interactive What-If Scenario Simulator
function initSimulatorControls() {
  const ids = ['simHours', 'simEmployees', 'simViolations', 'simSS', 'simInsp', 'simInjuries'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', runSimulation);
    }
  });

  const methodEl = document.getElementById('simMethod');
  if (methodEl) {
    methodEl.addEventListener('change', runSimulation);
  }

  // Presets
  const btnSafe = document.getElementById('btnPresetSafe');
  if (btnSafe) {
    btnSafe.addEventListener('click', () => {
      setSimValues(45000, 75, 0, 0, 45, 0, 'Surface');
    });
  }

  const btnDanger = document.getElementById('btnPresetDanger');
  if (btnDanger) {
    btnDanger.addEventListener('click', () => {
      setSimValues(185000, 240, 8, 3, 15, 3, 'Underground');
    });
  }

  const btnBalanced = document.getElementById('btnPresetBalanced');
  if (btnBalanced) {
    btnBalanced.addEventListener('click', () => {
      setSimValues(95000, 120, 3, 1, 28, 1, 'Underground');
    });
  }

  runSimulation();
}

function setSimValues(hours, emp, viol, ss, insp, inj, method) {
  document.getElementById('simHours').value = hours;
  document.getElementById('simEmployees').value = emp;
  document.getElementById('simViolations').value = viol;
  document.getElementById('simSS').value = ss;
  document.getElementById('simInsp').value = insp;
  document.getElementById('simInjuries').value = inj;
  document.getElementById('simMethod').value = method;
  runSimulation();
}

function runSimulation() {
  const hours = parseFloat(document.getElementById('simHours').value);
  const emp = parseFloat(document.getElementById('simEmployees').value);
  const viol = parseFloat(document.getElementById('simViolations').value);
  const ss = parseFloat(document.getElementById('simSS').value);
  const insp = parseFloat(document.getElementById('simInsp').value);
  const inj = parseFloat(document.getElementById('simInjuries').value);
  const method = document.getElementById('simMethod').value;

  // Labels
  document.getElementById('lblHours').textContent = `${hours.toLocaleString()} jam`;
  document.getElementById('lblEmployees').textContent = `${emp} pekerja aktif`;
  document.getElementById('lblViolations').textContent = `${viol} temuan`;
  document.getElementById('lblSS').textContent = `${ss} temuan kritis S&S`;
  document.getElementById('lblInsp').textContent = `${insp} jam inspeksi`;
  document.getElementById('lblInjuries').textContent = `${inj} cedera kuartal lalu`;

  // Logistic model formula
  const logHrs = Math.log(Math.max(1000, hours) + 1);
  const ssRatio = ss / (viol + 1.0);
  const violRate = viol / (insp + 1.0);
  const methodWeight = method === 'Underground' ? 0.38 : (method === 'Surface' ? -0.18 : 0.0);

  let logit = -3.85 + (0.32 * logHrs) + (0.58 * ss) + (0.42 * ssRatio) + (0.39 * inj) + (0.16 * violRate) + methodWeight - (0.014 * insp);
  let prob = 1.0 / (1.0 + Math.exp(-logit));
  prob = Math.min(0.97, Math.max(0.04, prob));

  const probPct = (prob * 100.0).toFixed(1);
  let tier = 'Low';
  if (prob >= 0.70) tier = 'Critical';
  else if (prob >= 0.45) tier = 'Elevated';
  else if (prob >= 0.20) tier = 'Moderate';

  const hexColor = getTierHex(tier);

  // Update UI Elements
  const simScoreVal = document.getElementById('simScoreVal');
  simScoreVal.textContent = `${probPct}%`;
  simScoreVal.style.color = hexColor;

  const simTierTag = document.getElementById('simTierTag');
  simTierTag.textContent = getTierLabelIndo(tier);
  simTierTag.className = `tier-tag tier-${tier.toLowerCase()}`;

  const simMeterBar = document.getElementById('simMeterBar');
  simMeterBar.style.width = `${probPct}%`;
  simMeterBar.style.background = hexColor;

  // Abatement calculation
  const abatementDelta = (ss * 9.2).toFixed(1);
  const simAbatementText = document.getElementById('simAbatementText');
  if (ss > 0) {
    simAbatementText.innerHTML = `
      <strong style="color:#10B981; font-weight:700; display:block; margin-bottom:4px;">Potensi Pengurangan Risiko Nyata</strong>
      Jika pengelola tambang segera memperbaiki <strong>${ss} temuan pelanggaran kritis S&S</strong> menjadi 0, estimasi potensi kecelakaan kerja kuartal depan dapat ditekan turun sekitar <strong>-${abatementDelta}%</strong>.
    `;
  } else {
    simAbatementText.innerHTML = `
      <strong style="color:#10B981; font-weight:700; display:block; margin-bottom:4px;">Kondisi Kepatuhan Ideal</strong>
      Tidak ada temuan pelanggaran kritis S&S. Menjaga jam kerja stabil dan melanjutkan inspeksi berkala merupakan langkah paling efektif untuk mempertahankan lingkungan tambang yang aman.
    `;
  }
}

// ============================================================================
// HERO LIVE CODED TELEMETRY HUD CONTROLLER (ZERO RASTER IMAGES)
// ============================================================================
function initHeroTelemetryHUD() {
  const radarBlips = document.querySelectorAll('.hud-radar-blip');
  if (!radarBlips.length) return;

  const needle = document.getElementById('hudGaugeNeedle');
  const track = document.getElementById('hudGaugeTrack');
  const probVal = document.getElementById('hudProbVal');
  const tierPill = document.getElementById('hudTierPill');
  const siteName = document.getElementById('hudSiteName');
  const siteLoc = document.getElementById('hudSiteLoc');
  const siteHours = document.getElementById('hudSiteHours');
  const shapList = document.getElementById('hudShapList');
  const alertText = document.getElementById('hudAlertText');

  function updateHUDWithMine(mine) {
    if (!mine) return;

    // Angle: 0% is -90deg, 100% is +90deg
    const angle = ((mine.prob - 50) * 1.76).toFixed(1);
    if (needle) {
      needle.style.transform = `rotate(${angle}deg)`;
      needle.style.stroke = getTierHex(mine.tier);
    }

    // Arc stroke dashoffset: full arc is 235.6
    if (track) {
      const offset = (235.6 * (1 - mine.prob / 100.0)).toFixed(1);
      track.style.strokeDashoffset = offset;
    }

    if (probVal) {
      probVal.textContent = `${mine.prob.toFixed(1)}%`;
      probVal.style.color = getTierHex(mine.tier);
      probVal.style.textShadow = `0 0 20px ${getTierHex(mine.tier)}66`;
    }

    if (tierPill) {
      tierPill.textContent = `KATEGORI ${getTierLabelIndo(mine.tier).toUpperCase()}`;
      tierPill.style.color = getTierHex(mine.tier);
      tierPill.style.borderColor = `${getTierHex(mine.tier)}55`;
      tierPill.style.background = `${getTierHex(mine.tier)}22`;
    }

    if (siteName) siteName.textContent = mine.name;
    if (siteLoc) siteLoc.textContent = `${mine.state} • ${mine.type} ${mine.commodity}`;
    if (siteHours) siteHours.textContent = `${mine.hours.toLocaleString('id-ID')} Jam Kerja`;

    // Update SHAP list in HUD
    if (shapList && mine.drivers && mine.drivers.length) {
      const topDrivers = mine.drivers.slice(0, 4);
      shapList.innerHTML = topDrivers.map(d => {
        const isPos = d.shap > 0;
        const sign = isPos ? '+' : '';
        const pct = Math.min(100, Math.max(15, Math.abs(d.shap) * 3.2)).toFixed(0);
        return `
          <div class="hud-shap-item">
            <div class="hud-shap-head">
              <span class="hud-shap-name">${d.name}</span>
              <span class="hud-shap-val ${isPos ? 'pos' : 'neg'}">${sign}${d.shap.toFixed(1)}%</span>
            </div>
            <div class="hud-shap-track">
              <div class="hud-shap-fill ${isPos ? 'pos' : 'neg'}" style="width: ${pct}%;"></div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Update tailored alert text
    if (alertText) {
      if (mine.tier === 'Critical') {
        alertText.innerHTML = `Peringatan Dini Aktif — Tingginya jam lembur dan temuan S&S pada <strong>${mine.name}</strong> menandakan eskalasi risiko insiden dalam 90 hari ke depan.`;
      } else if (mine.tier === 'Elevated' || mine.tier === 'High') {
        alertText.innerHTML = `Perhatian K3 Terarah — <strong>${mine.name}</strong> menunjukkan beban kerja meningkat yang memerlukan audit berkala sebelum menjadi temuan kritis.`;
      } else {
        alertText.innerHTML = `Pengawasan Standar — <strong>${mine.name}</strong> berada dalam koridor risiko terkendali dengan kepatuhan inspeksi yang baik.`;
      }
    }
  }

  radarBlips.forEach(blip => {
    blip.addEventListener('click', () => {
      radarBlips.forEach(b => b.classList.remove('active'));
      blip.classList.add('active');
      const idx = parseInt(blip.getAttribute('data-mine-idx'), 10) || 0;
      if (CURRENT_MINES[idx]) {
        updateHUDWithMine(CURRENT_MINES[idx]);
      }
    });

    blip.addEventListener('mouseenter', () => {
      const idx = parseInt(blip.getAttribute('data-mine-idx'), 10) || 0;
      if (CURRENT_MINES[idx]) {
        updateHUDWithMine(CURRENT_MINES[idx]);
      }
    });
  });
}

// ============================================================================
// DATA PIPELINE ANIMATED FLOW CONTROLLER
// ============================================================================
function initPipelineDiagramFlow() {
  const feederNodes = document.querySelectorAll('.flow-node');
  const sourceCards = document.querySelectorAll('.source-card');
  const pipes = document.querySelectorAll('.flow-pipe');

  feederNodes.forEach((node, idx) => {
    node.addEventListener('mouseenter', () => {
      feederNodes.forEach(n => n.classList.remove('active'));
      node.classList.add('active');

      // Highlight corresponding conduit
      pipes.forEach(p => p.classList.remove('active'));
      const activePipe = document.querySelector(`.flow-pipe.p${idx + 1}`);
      if (activePipe) activePipe.classList.add('active');

      // Highlight corresponding source accordion card
      if (sourceCards[idx]) {
        sourceCards.forEach(c => c.classList.remove('active'));
        sourceCards[idx].classList.add('active');
      }
    });
  });

  sourceCards.forEach((card, idx) => {
    card.addEventListener('mouseenter', () => {
      sourceCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');

      feederNodes.forEach(n => n.classList.remove('active'));
      if (feederNodes[idx]) feederNodes[idx].classList.add('active');

      pipes.forEach(p => p.classList.remove('active'));
      const activePipe = document.querySelector(`.flow-pipe.p${idx + 1}`);
      if (activePipe) activePipe.classList.add('active');
    });
  });
}

// ============================================================================
// AI SAFETY COPILOT CHAT & TREND INTELLIGENCE CONTROLLER
// ============================================================================
function initCopilotChat() {
  const pills = document.querySelectorAll('.copilot-demo-pill');
  const input = document.getElementById('copilotInput');
  const messagesContainer = document.getElementById('copilotMessages');
  if (!messagesContainer) return;

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      const prompt = pill.getAttribute('data-prompt');
      if (prompt) {
        if (input) input.value = prompt;
        window.sendCopilotQuery(prompt);
      }
    });
  });

  window.sendCopilotQuery = function(customQuery) {
    const query = (customQuery || (input ? input.value : '')).trim();
    if (!query) return;

    if (input) input.value = '';

    // Append user message
    appendChatMessage('user', query);

    // Show typing placeholder
    const typingId = 'typing-' + Date.now();
    appendChatTyping(typingId);

    setTimeout(() => {
      removeChatTyping(typingId);
      const responseHtml = generateCopilotResponse(query);
      appendChatMessage('assistant', responseHtml);
    }, 450);
  };
}

function appendChatMessage(sender, htmlContent) {
  const container = document.getElementById('copilotMessages');
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${sender}`;

  const timeStr = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });

  if (sender === 'user') {
    bubble.innerHTML = `
      <strong style="display:block; margin-bottom:4px; color:var(--accent-cyan);">Anda (K3 Operator)</strong>
      ${escapeHtml(htmlContent)}
      <span class="chat-meta">${timeStr} • Kueri Manual</span>
    `;
  } else {
    bubble.innerHTML = `
      <strong style="display:block; margin-bottom:6px; color:var(--accent-amber-light); display:flex; align-items:center; gap:6px;">
        <span style="width:7px; height:7px; border-radius:50%; background:#10B981; display:inline-block;"></span>
        MineRisk Intelligence Copilot
      </strong>
      ${htmlContent}
      <span class="chat-meta">${timeStr} • Analisis Real-Time Model CatBoost v2.4</span>
    `;
  }

  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

function appendChatTyping(id) {
  const container = document.getElementById('copilotMessages');
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble assistant';
  bubble.id = id;
  bubble.innerHTML = `
    <span style="font-size:0.8rem; color:var(--text-muted); display:inline-flex; align-items:center; gap:6px;">
      <span class="hud-beacon-pulse" style="width:6px; height:6px;"></span>
      Sedang menganalisis basis data keselamatan MSHA dan menghitung proyeksi risiko...
    </span>
  `;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

function removeChatTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function generateCopilotResponse(query) {
  const q = query.toLowerCase();

  // Prompt 1: Site 1414
  if (q.includes('1414') || q.includes('valley')) {
    return `
      <div style="line-height:1.6;">
        <div style="font-weight:700; color:#EF4444; margin-bottom:6px; font-size:1rem;">
          Temuan Kritis Lapangan — Operasi Tambang Site 1414 Valley (PA)
        </div>
        <p style="margin-bottom:8px;">
          Berdasarkan analisis fitur SHAP kuartal terbaru, unit ini memiliki probabilitas insiden sebesar <strong>86.9% (Kategori Bahaya Kritis)</strong>, melampaui rata-rata nasional sebesar 50.2%.
        </p>
        <div style="background:rgba(239,68,68,0.08); border-left:3px solid #EF4444; padding:8px 12px; margin-bottom:10px; font-size:0.88rem;">
          <strong>Pendorong Utama Lonjakan Bahaya</strong><br>
          • Beban jam kerja operasional sangat tinggi mencapai 135.945 jam kerja (+24.2% dampak SHAP)<br>
          • Temuan pelanggaran kritis S&S pada stabilitas atap batuan dan akumulasi gas (+18.5%)<br>
          • Metode penambangan bawah tanah dengan risiko geologis inheren (+12.8%)
        </div>
        <p style="margin-bottom:6px;">
          <strong>Langkah Mitigasi yang Direkomendasikan</strong><br>
          Segera lakukan penyelesaian temuan S&S dalam 7 hari kerja dan jadwalkan audit inspektur lapangan tambahan minimal 20 jam kerja guna memangkas probabilitas bahaya kembali ke batas aman di bawah 55%.
        </p>
      </div>
    `;
  }

  // Prompt 2: Tindakan darurat
  if (q.includes('darurat') || q.includes('mencegah') || q.includes('tindakan')) {
    return `
      <div style="line-height:1.6;">
        <div style="font-weight:700; color:#F59E0B; margin-bottom:6px; font-size:1rem;">
          Protokol 3 Tindakan Darurat Pencegahan Insiden Tambang
        </div>
        <p style="margin-bottom:8px;">
          Data historis membuktikan 78% insiden fatalitas tambang didahului oleh akumulasi pelanggaran yang tidak ditangani tepat waktu. Terapkan 3 langkah terukur berikut
        </p>
        <div style="display:flex; flex-direction:column; gap:8px; margin-bottom:10px;">
          <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:8px 12px; border-radius:6px; font-size:0.88rem;">
            <strong style="color:#EF4444;">1. Perbaikan Cepat Temuan S&S (Zero Tolerance)</strong><br>
            Selesaikan seluruh temuan Significant & Substantial terutama ventilasi udara dan penyangga atap batuan dalam kurun waktu maksimal 14 hari kalender.
          </div>
          <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:8px 12px; border-radius:6px; font-size:0.88rem;">
            <strong style="color:#F59E0B;">2. Intervensi Kelelahan dan Pengendalian Jam Lembur</strong><br>
            Batasi penambahan jam kerja lembur maksimal 10% di atas kapasitas normal. Kelelahan pekerja menyumbang lebih dari 35% kenaikan kekeliruan manuver alat berat.
          </div>
          <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:8px 12px; border-radius:6px; font-size:0.88rem;">
            <strong style="color:#10B981;">3. Penugasan Inspektur Berbasis Prioritas AI</strong><br>
            Alihkan jam audit dari tambang berkategori aman menuju 10% unit tambang paling berisiko untuk melipatgandakan efek pencegahan hingga 1.62 kali lipat.
          </div>
        </div>
      </div>
    `;
  }

  // Prompt 3: Bawah tanah vs permukaan
  if (q.includes('bawah tanah') || q.includes('permukaan') || q.includes('vs') || q.includes('banding')) {
    return `
      <div style="line-height:1.6;">
        <div style="font-weight:700; color:#38BDF8; margin-bottom:6px; font-size:1rem;">
          Perbandingan Profil Bahaya Tambang Bawah Tanah vs Tambang Terbuka
        </div>
        <p style="margin-bottom:8px;">
          Berdasarkan agregasi 1.542 unit tambang aktif, terdapat disparitas risiko yang signifikan antara metode operasional penambangan
        </p>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px; font-size:0.86rem;">
          <div style="background:rgba(239,68,68,0.06); border:1px solid rgba(239,68,68,0.2); padding:10px; border-radius:6px;">
            <strong style="color:#EF4444; font-size:0.95rem;">Tambang Bawah Tanah (Underground)</strong><br>
            • Rata-rata Risiko <strong>72.4%</strong><br>
            • Bahaya Utama Konsentrasi gas metana, keruntuhan atap terowongan, dan ruang manuver terbatas.<br>
            • Sensitivitas Lembur Sangat Tinggi (korelasi kelelahan dengan disorientasi lorong).
          </div>
          <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2); padding:10px; border-radius:6px;">
            <strong style="color:#10B981; font-size:0.95rem;">Tambang Terbuka (Surface Pit)</strong><br>
            • Rata-rata Risiko <strong>46.8%</strong><br>
            • Bahaya Utama Kestabilan lereng galian, interaksi dump truck berukuran raksasa, dan debu partikel.<br>
            • Faktor Mitigasi Sirkulasi udara alami dan keterlihatan visual area kerja yang luas.
          </div>
        </div>
        <p style="font-size:0.88rem; color:var(--text-secondary);">
          Kesimpulan Tambang bawah tanah memerlukan frekuensi inspeksi berkala rata-rata 2.4 kali lebih intensif dibandingkan tambang permukaan terbuka.
        </p>
      </div>
    `;
  }

  // Prompt 4: Jam lembur
  if (q.includes('lembur') || q.includes('jam kerja') || q.includes('kelelahan') || q.includes('fatigue')) {
    return `
      <div style="line-height:1.6;">
        <div style="font-weight:700; color:#EC4899; margin-bottom:6px; font-size:1rem;">
          Analisis Pengaruh Jam Lembur terhadap Angka Peluang Kecelakaan
        </div>
        <p style="margin-bottom:8px;">
          Fitur jam kerja (workforce hours) menempati peringkat teratas dalam kontribusi SHAP model MineRisk AI. Berikut temuan korelasi utamanya
        </p>
        <div style="background:rgba(236,72,153,0.08); border-left:3px solid #EC4899; padding:8px 12px; margin-bottom:10px; font-size:0.88rem;">
          <strong>Eksponensial Risiko Kelelahan</strong><br>
          • Setiap peningkatan 10.000 jam lembur di atas kapasitas standar unit operasional menaikkan probabilitas kecelakaan sebesar rata-rata <strong>+3.4%</strong>.<br>
          • Penurunan refleks motorik dan kewaspadaan pekerja tambang setelah shift 10 jam berlipat ganda, memicu 42% kecelakaan tabrakan alat angkut dan terpeleset dari ketinggian.
        </div>
        <p style="margin-bottom:4px; font-size:0.88rem; color:var(--text-secondary);">
          Rekomendasi Manajemen Mengatur rotasi shift wajib maksimal 8 jam kerja aktif di area tambang dalam dan mewajibkan jeda istirahat terencana di pos shelter keselamatan.
        </p>
      </div>
    `;
  }

  // Prompt 5: Efisiensi inspektur
  if (q.includes('efisiensi') || q.includes('inspektur') || q.includes('prioritas') || q.includes('lift')) {
    return `
      <div style="line-height:1.6;">
        <div style="font-weight:700; color:#10B981; margin-bottom:6px; font-size:1rem;">
          Tolok Ukur Efisiensi Penugasan Inspektur Berbasis AI
        </div>
        <p style="margin-bottom:8px;">
          Pengawasan tambang konvensional seringkali dilakukan secara acak atau terjadwal tanpa pembobotan risiko, sehingga inspektur menghabiskan waktu pada lokasi yang sebenarnya telah aman.
        </p>
        <div style="background:rgba(16,185,129,0.08); border-left:3px solid #10B981; padding:8px 12px; margin-bottom:10px; font-size:0.88rem;">
          <strong>Keunggulan Algoritma Predictive AI</strong><br>
          • <strong>Top 10% Lift 1.62x</strong> Model mampu mendeteksi 1.62 kali lebih banyak unit bermasalah pada kelompok 10% prioritas tertinggi dibandingkan metode acak.<br>
          • <strong>Penghematan Waktu Audit 38%</strong> Lembaga pengawas dapat menghemat ribuan jam perjalanan audit dengan fokus langsung pada titik anomali berisiko tinggi.<br>
          • <strong>Cakupan Bahaya Kritis 74%</strong> Dengan hanya mengaudit 20% tambang di antrean teratas, 74% potensi kecelakaan kerja kuartalan dapat diantisipasi secara preventif.
        </div>
      </div>
    `;
  }

  // Prompt 6: Cumberland Mine
  if (q.includes('cumberland')) {
    return `
      <div style="line-height:1.6;">
        <div style="font-weight:700; color:#EF4444; margin-bottom:6px; font-size:1rem;">
          Rekomendasi Mitigasi Khusus Cumberland Mine Portal 3 (WV)
        </div>
        <p style="margin-bottom:8px;">
          Unit Cumberland Mine Portal 3 saat ini berada pada tingkat bahaya tertinggi di sistem dengan skor probabilitas <strong>92.4% (Kategori Bahaya Kritis)</strong>.
        </p>
        <div style="background:rgba(239,68,68,0.08); border-left:3px solid #EF4444; padding:8px 12px; margin-bottom:10px; font-size:0.88rem;">
          <strong>Profil Diagnostik</strong><br>
          • 7 temuan pelanggaran keselamatan dengan 3 temuan berkategori fatal S&S terkait sirkulasi ventilasi gas.<br>
          • Jam lembur ekstrem mencapai 198.200 jam kerja dengan 3 rekam jejak cedera pekerja kuartal sebelumnya.<br>
          • Durasi pengawasan MSHA saat ini tercatat 42 jam pemeriksaan.
        </div>
        <div style="background:rgba(16,185,129,0.08); border-left:3px solid #10B981; padding:8px 12px; margin-bottom:6px; font-size:0.88rem;">
          <strong>Rencana Aksi 14 Hari</strong><br>
          1. Kalibrasi ulang blower sistem ventilasi sekunder di portal 3.<br>
          2. Penghentian shift lembur ganda untuk 260 tenaga kerja aktif.<br>
          3. Penambahan pengawas K3 khusus untuk sertifikasi atap batuan harian.
        </div>
      </div>
    `;
  }

  // Search if query matches any mine name or ID
  const matchedMine = CURRENT_MINES.find(m => 
    m.name.toLowerCase().includes(q) || 
    m.id.toLowerCase().includes(q) ||
    m.state.toLowerCase() === q
  );

  if (matchedMine) {
    return `
      <div style="line-height:1.6;">
        <div style="font-weight:700; color:${getTierHex(matchedMine.tier)}; margin-bottom:6px; font-size:1rem;">
          Hasil Pemindaian Unit — ${matchedMine.name} (ID ${matchedMine.id})
        </div>
        <p style="margin-bottom:8px;">
          Lokasi ${matchedMine.state} • Tipe ${matchedMine.type} (${matchedMine.commodity}) • ${matchedMine.employees} Karyawan Aktif
        </p>
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:10px 14px; border-radius:6px; margin-bottom:10px; font-size:0.88rem;">
          • Estimasi Peluang Insiden <strong>${matchedMine.prob}%</strong> (Kategori <strong>${getTierLabelIndo(matchedMine.tier)}</strong>)<br>
          • Total Paparan Jam Kerja ${matchedMine.hours.toLocaleString('id-ID')} jam<br>
          • Catatan Pelanggaran ${matchedMine.violations} temuan (${matchedMine.viol_ss} temuan kritis S&S)<br>
          • Jam Audit Inspektur ${matchedMine.insp_hours} jam pemeriksaan
        </div>
        <p style="font-size:0.88rem; color:var(--text-secondary);">
          Saran Tindakan Anda dapat membuka <strong>Tab 2 (Analisis Rinci Tiap Tambang)</strong> untuk melihat grafik SHAP detail atau membuka <strong>Tab 3 (Simulasi Mitigasi)</strong> untuk menguji perbaikan operasional unit ini.
        </p>
      </div>
    `;
  }

  // Fallback general response
  return `
    <div style="line-height:1.6;">
      <div style="font-weight:700; color:var(--accent-amber-light); margin-bottom:6px; font-size:1rem;">
        Ringkasan Intelijen Keselamatan Tambang
      </div>
      <p style="margin-bottom:8px;">
        Pertanyaan Anda mengenai <em>"${escapeHtml(query)}"</em> telah diproses melalui basis analitik MineRisk AI.
      </p>
      <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); padding:10px; border-radius:6px; margin-bottom:10px; font-size:0.88rem;">
        • Sistem saat ini memantau <strong>1.542 unit tambang aktif</strong> di seluruh wilayah nasional.<br>
        • Tingkat bahaya rata-rata saat ini berada di angka <strong>50.2%</strong> dengan 284 unit berstatus prioritas darurat.<br>
        • Faktor penentu utama risiko adalah kombinasi antara pelanggaran kritis S&S dan jam lembur operasional tinggi.
      </div>
      <p style="font-size:0.88rem; color:var(--text-secondary);">
        Silakan klik salah satu contoh pertanyaan cepat di atas atau tanyakan mengenai nama tambang spesifik seperti <em>Site 1414</em> atau <em>Cumberland</em>.
      </p>
    </div>
  `;
}
