// MineRisk AI Sistem Prediksi Keselamatan Kerja Logika Aplikasi Web Bersih
let SHOWCASE_DATA = null;
let CURRENT_MINES = [];
let SELECTED_MINE = null;

// Rata rata Peluang Nasional
const NATIONAL_AVG_PROB = 50.2;

document.addEventListener('DOMContentLoaded', async () => {
  initTabs();
  initSimulator();
  await loadData();
});

// Pengaturan Navigasi Tab
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');

      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add('active');
      }
    });
  });
}

// Memuat Data Ringkasan
async function loadData() {
  try {
    const res = await fetch('data/showcase_data.json');
    SHOWCASE_DATA = await res.json();
    CURRENT_MINES = SHOWCASE_DATA.mines || [];

    populateStateFilter();
    renderSurveillanceTable(CURRENT_MINES);
    populateInspectorSelector(CURRENT_MINES);

    if (CURRENT_MINES.length > 0) {
      inspectMine(CURRENT_MINES[0].id);
    }

    document.getElementById('stateFilter').addEventListener('change', applyFilters);
    document.getElementById('commFilter').addEventListener('change', applyFilters);
    document.getElementById('tierFilter').addEventListener('change', applyFilters);
    document.getElementById('searchInput').addEventListener('input', applyFilters);

  } catch (err) {
    console.error('Gagal memuat data ringkasan tambang:', err);
  }
}

// Mengisi Pilihan Wilayah
function populateStateFilter() {
  const stateSelect = document.getElementById('stateFilter');
  const states = [...new Set(CURRENT_MINES.map(m => m.state))].sort();
  
  states.forEach(st => {
    const opt = document.createElement('option');
    opt.value = st;
    opt.textContent = `Wilayah ${st}`;
    stateSelect.appendChild(opt);
  });
}

// Menyaring Data
function applyFilters() {
  const stVal = document.getElementById('stateFilter').value;
  const commVal = document.getElementById('commFilter').value;
  const tierVal = document.getElementById('tierFilter').value;
  const searchVal = document.getElementById('searchInput').value.trim().toLowerCase();

  const filtered = CURRENT_MINES.filter(m => {
    const matchState = (stVal === 'ALL' || m.state === stVal);
    const matchComm = (commVal === 'ALL' || m.commodity === commVal);
    const matchTier = (tierVal === 'ALL' || m.tier === tierVal);
    const matchSearch = (!searchVal || 
      m.name.toLowerCase().includes(searchVal) || 
      m.id.toLowerCase().includes(searchVal)
    );
    return matchState && matchComm && matchTier && matchSearch;
  });

  renderSurveillanceTable(filtered);
}

// Menampilkan Tabel
function renderSurveillanceTable(mines) {
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  if (mines.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding: 28px; color: var(--text-dim);">Tidak ada data tambang yang sesuai dengan kriteria pencarian.</td></tr>';
    return;
  }

  const displayMines = mines.slice(0, 20);

  displayMines.forEach((m, idx) => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';

    const tierClass = `tier-${m.tier.toLowerCase()}`;
    const statusText = getTierLabel(m.tier);

    tr.innerHTML = `
      <td style="font-family: var(--font-mono); color: var(--text-dim);">${idx + 1}</td>
      <td style="font-family: var(--font-mono); font-weight: 600;">${m.id}</td>
      <td style="font-weight: 600;">${m.name}</td>
      <td>${m.state}</td>
      <td>${m.commodity} (${m.type})</td>
      <td style="font-family: var(--font-mono);">${m.hours.toLocaleString()} jam</td>
      <td style="font-family: var(--font-mono);">${m.violations} temuan</td>
      <td><span class="tier-badge ${tierClass}">${statusText}</span></td>
      <td style="font-family: var(--font-mono); font-weight: 700; color: ${getTierColor(m.tier)};">${m.prob}%</td>
    `;

    tr.addEventListener('click', () => {
      inspectMine(m.id);
      document.querySelector('[data-tab="tab-inspector"]').click();
    });

    tbody.appendChild(tr);
  });
}

function getTierLabel(tier) {
  switch (tier) {
    case 'Critical': return 'BAHAYA TINGGI';
    case 'Elevated': return 'WASPADA';
    case 'Moderate': return 'SEDANG';
    case 'Low': return 'AMAN';
    default: return tier;
  }
}

function getTierColor(tier) {
  switch (tier) {
    case 'Critical': return '#B91C1C';
    case 'Elevated': return '#C2410C';
    case 'Moderate': return '#A16207';
    case 'Low': return '#15803D';
    default: return '#0F172A';
  }
}

// Mengisi Pilihan Tambang
function populateInspectorSelector(mines) {
  const select = document.getElementById('mineSelector');
  select.innerHTML = '';

  mines.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m.id;
    opt.textContent = `${m.name} (Nomor ID: ${m.id}) wilayah ${m.state} peluang ${m.prob}%`;
    select.appendChild(opt);
  });

  select.addEventListener('change', (e) => {
    inspectMine(e.target.value);
  });
}

// Memeriksa Tambang Tertentu
function inspectMine(mineId) {
  const mine = CURRENT_MINES.find(m => m.id === mineId);
  if (!mine) return;

  SELECTED_MINE = mine;
  document.getElementById('mineSelector').value = mine.id;

  const delta = (mine.prob - NATIONAL_AVG_PROB).toFixed(1);
  const deltaStr = delta > 0 
    ? `Lebih tinggi ${delta}% dibanding rata rata nasional (${NATIONAL_AVG_PROB}%)` 
    : `Lebih rendah ${Math.abs(delta)}% dibanding rata rata nasional (${NATIONAL_AVG_PROB}%)`;

  const tierColor = getTierColor(mine.tier);

  document.getElementById('inspectScore').textContent = `${mine.prob}%`;
  document.getElementById('inspectScore').style.color = tierColor;
  document.getElementById('inspectBadge').textContent = getTierLabel(mine.tier);
  document.getElementById('inspectBadge').className = `tier-badge tier-${mine.tier.toLowerCase()}`;
  document.getElementById('inspectDelta').textContent = deltaStr;
  document.getElementById('inspectDelta').style.color = tierColor;

  document.getElementById('detailMineName').textContent = mine.name;
  document.getElementById('detailMineId').textContent = mine.id;
  document.getElementById('detailState').textContent = mine.state;
  document.getElementById('detailComm').textContent = `${mine.commodity} (${mine.type})`;
  document.getElementById('detailHours').textContent = `${mine.hours.toLocaleString()} jam (${mine.employees} pekerja)`;
  document.getElementById('detailViol').textContent = `${mine.violations} temuan (${mine.viol_ss} pelanggaran kritis)`;

  renderShapWaterfall(mine.drivers);
  renderGuidance(mine.tier);
}

// Menampilkan Batang Pemicu Risiko
function renderShapWaterfall(drivers) {
  const container = document.getElementById('shapBarsContainer');
  container.innerHTML = '';

  if (!drivers || drivers.length === 0) {
    container.innerHTML = '<p style="color:var(--text-dim);">Data pemicu risiko belum tersedia.</p>';
    return;
  }

  const maxAbs = Math.max(...drivers.map(d => Math.abs(d.shap)), 1.0);

  drivers.forEach(d => {
    const isPos = d.shap >= 0;
    const widthPct = Math.min(100, Math.round((Math.abs(d.shap) / maxAbs) * 100));

    const row = document.createElement('div');
    row.className = 'shap-bar-row';

    row.innerHTML = `
      <div class="shap-feat-name" title="${d.name} (${d.val})">${d.name}</div>
      <div class="shap-bar-track">
        <div class="shap-bar-fill ${isPos ? 'shap-bar-pos' : 'shap-bar-neg'}" style="width: ${widthPct}%;"></div>
      </div>
      <div class="shap-val-tag" style="color: ${isPos ? '#B91C1C' : '#15803D'};">
        ${isPos ? '+' : ''}${d.shap}%
      </div>
    `;

    container.appendChild(row);
  });
}

// Panduan Langkah Pencegahan
function renderGuidance(tier) {
  const box = document.getElementById('guidanceBox');
  if (tier === 'Critical') {
    box.style.borderLeft = '3px solid #B91C1C';
    box.innerHTML = `
      <h4 style="color:#B91C1C; margin-bottom: 6px; font-size: 0.95rem;">Langkah Prioritas Tinggi Diperlukan</h4>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin:0;">
        Operasi tambang ini menunjukkan akumulasi jam lembur pekerja yang berlebih disertai temuan pelanggaran keselamatan serius. Disarankan mengirimkan tim inspeksi audit keselamatan dalam waktu 7 hari ke depan untuk memeriksa prosedur kerja dan jam istirahat.
      </p>
    `;
  } else if (tier === 'Elevated') {
    box.style.borderLeft = '3px solid #C2410C';
    box.innerHTML = `
      <h4 style="color:#C2410C; margin-bottom: 6px; font-size: 0.95rem;">Pengawasan Ketat Diperlukan</h4>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin:0;">
        Kondisi tambang menunjukkan kenaikan indikator risiko. Pengelola tambang wajib menindaklanjuti dan memperbaiki temuan pemeriksaan sebelum kuartal berikutnya dimulai.
      </p>
    `;
  } else if (tier === 'Moderate') {
    box.style.borderLeft = '3px solid #A16207';
    box.innerHTML = `
      <h4 style="color:#A16207; margin-bottom: 6px; font-size: 0.95rem;">Pengawasan Rutin Normal</h4>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin:0;">
        Kondisi operasional berada pada kisaran rata rata industri. Lanjutkan pengawasan berkala dan pelaporan keselamatan rutin.
      </p>
    `;
  } else {
    box.style.borderLeft = '3px solid #15803D';
    box.innerHTML = `
      <h4 style="color:#15803D; margin-bottom: 6px; font-size: 0.95rem;">Tingkat Risiko Rendah dan Aman</h4>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin:0;">
        Riwayat keselamatan sangat baik tanpa ada insiden berulang. Pertahankan prosedur kerja aman yang sudah berjalan.
      </p>
    `;
  }
}

// Simulasi Perubahan Operasional
function initSimulator() {
  const inputs = ['simHours', 'simEmployees', 'simViolations', 'simSS', 'simInsp', 'simInjuries'];
  
  inputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', runSimulation);
    }
  });

  const methodSelect = document.getElementById('simMethod');
  if (methodSelect) {
    methodSelect.addEventListener('change', runSimulation);
  }

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

  document.getElementById('lblHours').textContent = `${hours.toLocaleString()} jam`;
  document.getElementById('lblEmployees').textContent = `${emp} pekerja`;
  document.getElementById('lblViolations').textContent = `${viol} temuan`;
  document.getElementById('lblSS').textContent = `${ss} temuan kritis`;
  document.getElementById('lblInsp').textContent = `${insp} jam`;
  document.getElementById('lblInjuries').textContent = `${inj} kejadian`;

  const logHrs = Math.log(Math.max(1000, hours) + 1);
  const ssRatio = ss / (viol + 1.0);
  const violRate = viol / (insp + 1.0);
  const methodWeight = method === 'Underground' ? 0.35 : (method === 'Surface' ? -0.15 : 0.0);

  let logit = -3.85 + (0.32 * logHrs) + (0.55 * ss) + (0.42 * ssRatio) + (0.38 * inj) + (0.15 * violRate) + methodWeight - (0.012 * insp);
  let prob = 1.0 / (1.0 + Math.exp(-logit));
  prob = Math.min(0.96, Math.max(0.04, prob));

  const probPct = (prob * 100.0).toFixed(1);
  let tier = 'Low';
  if (prob >= 0.70) tier = 'Critical';
  else if (prob >= 0.45) tier = 'Elevated';
  else if (prob >= 0.20) tier = 'Moderate';

  const tierColor = getTierColor(tier);

  document.getElementById('simScoreVal').textContent = `${probPct}%`;
  document.getElementById('simScoreVal').style.color = tierColor;
  document.getElementById('simTierTag').textContent = getTierLabel(tier);
  document.getElementById('simTierTag').className = `tier-badge tier-${tier.toLowerCase()}`;
  document.getElementById('simMeterBar').style.width = `${probPct}%`;
  document.getElementById('simMeterBar').style.background = tierColor;

  const abatementDelta = (ss * 8.4).toFixed(1);
  document.getElementById('simAbatementText').textContent = ss > 0
    ? `Memperbaiki ${ss} temuan pelanggaran kritis menjadi 0 dapat menurunkan potensi risiko kecelakaan sekitar ${abatementDelta} persen.`
    : 'Beroperasi tanpa adanya temuan pelanggaran kritis sangat efektif menjaga keselamatan tambang.';
}
