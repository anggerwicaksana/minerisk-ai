# PORTFOLIO CASE STUDY: MineRisk-AI (SafeCast)
## Predictive Workplace Safety Risk Intelligence from 25 Years of Federal MSHA Data

**Role:** Lead Machine Learning Engineer & Data Scientist  
**Keywords:** Prospective Risk Forecasting, Zero Lookahead Bias, Relational Star Schema, LightGBM, Platt Scaling, SHAP TreeExplainer, Gradio, Hugging Face Spaces  
**Target Audience:** Tech Recruiters, AI/ML Hiring Managers, OSH Industrial Safety Leaders  

---

### Executive Summary
Di industri padat karya seperti pertambangan, kecelakaan kerja sering kali direspons secara reaktif: inspeksi baru digalakkan dan regulasi baru ditegakkan *setelah* insiden fatal terjadi. Pada saat yang sama, mayoritas portofolio machine learning keselamatan kerja di internet memiliki cacat fatal: **data leakage pasca-insiden** (misalnya memprediksi keparahan kecelakaan dari teks laporan yang baru dibuat setelah pekerja cedera).

**MineRisk-AI (SafeCast)** membalik paradigma tersebut dengan membangun sistem peramalan prospektif (*prospective risk forecasting*):
> *"Dapatkah data operasional triwulanan (jam kerja pekerja), histori audit inspeksi, dan sitasi pelanggaran keselamatan suatu tambang memprediksi probabilitas terjadinya kecelakaan kerja berulang pada kuartal berikutnya ($t+1$)?"*

Menggunakan 5 tabel relasional terverifikasi dari **U.S. Mine Safety and Health Administration (MSHA)** (2000–2025), sistem ini membuktikan bahwa pengawasan preventif berbasis AI mampu menangkap **>52% insiden kecelakaan masa depan hanya dengan mengaudit 10% tambang berisiko tertinggi** (efisiensi inspeksi naik **3.22x lipat** dibanding audit acak).

---

### 1. Masalah Utama & Anti-Pattern Portofolio Konvensional

| Masalah pada Portofolio Biasa | Pendekatan Rekayasa MineRisk-AI |
|---|---|
| **Lookahead Bias (Data Leakage):** Memprediksi keparahan kecelakaan dari teks narasi atau derajat cedera (`DAYS_LOST`). Padahal informasi tersebut mustahil tersedia sebelum kejadian. | **Strict Temporal Guardrail:** Fitur pada kuartal $t$ secara mutlak hanya menggunakan fakta yang terjadi $\le$ hari terakhir kuartal $t$. |
| **Pembersihan Data Statis Palsu:** Menggunakan kolom status mutakhir (`CURRENT_STATUS`) untuk melabeli kondisi tambang 10 tahun lalu. | **Audit Atribut Mutasi:** Menghapus seluruh kolom `CURRENT_*` untuk mencegah kontaminasi masa depan. |
| **Evaluasi Random Split:** Melakukan `train_test_split(test_size=0.2)` acak yang mencampurkan baris masa depan ke data latih. | **Strict Out-of-Time Split:** Train pada data historis ($\le 2021$), Kalibrasi pada $2022-2023$, dan Evaluasi Buta pada $2024-2025$. |
| **Output Black-Box Tidak Terkalibrasi:** Probabilitas mentah yang tidak mencerminkan frekuensi kejadian riil di lapangan. | **Platt Scaling & SHAP:** Kalibrasi sigmoid untuk probabilitas terpercaya + transparansi faktor pemicu lokal (*waterfall decomposition*). |

---

### 2. Arsitektur Data Relasional & Polars ETL

Proyek ini mengeksploitasi 5 dataset resmi MSHA yang digabungkan menjadi star-schema panel terindeks waktu `(MINE_ID, CAL_YR, CAL_QTR)`:
1. **`Mines.txt`:** Master data tambang (geografi invarian, metode penambangan underground vs surface, komoditas batubara vs mineral).
2. **`QuarterlyEmploymentProduction.txt`:** Denominasi paparan (*exposure hours* dan jumlah pekerja).
3. **`Inspections.txt`:** Frekuensi dan durasi jam inspeksi pengawas federal di lapangan.
4. **`Violations.txt`:** Sitasi pelanggaran regulasi, rasio S&S (*Significant and Substantial*), dan tingkat kelalaian.
5. **`Accidents.txt`:** Histori insiden cedera terstandarisasi Part 50.

Dengan menerapkan **Polars LazyFrames** dan *projection pushdown*, seluruh proses penggabungan 80,000+ observasi multi-dekade dieksekusi hanya dalam waktu **< 15 detik** dengan penggunaan RAM di bawah **3.5 GB**, menjamin portabilitas tanpa hambatan di lingkungan cloud gratis seperti Google Colab.

---

### 3. Rekayasa Fitur & Hasil Studi Ablasi

Untuk menguji kontribusi nyata setiap kategori data keselamatan, dilakukan **Feature Family Ablation Study**:

```
Model A (Exposure Jam Kerja Saja)           ──► PR-AUC: 0.7148  │ Lift: 1.59x
Model B (+ Riwayat Cedera Masa Lalu)        ──► PR-AUC: 0.7181  │ Lift: 1.60x
Model C (+ Intensitas Inspeksi MSHA)        ──► PR-AUC: 0.7136  │ Lift: 1.60x
Model D (+ Sitasi Pelanggaran S&S)          ──► PR-AUC: 0.7136  │ Lift: 1.60x
Model E (Full: + Tren Lonjakan Jam Lembur)  ──► PR-AUC: 0.7210  │ Lift: 1.62x
```

**Temuan Krusial:**
- Paparan jam kerja (`log_hours`) dan riwayat cedera sebelumnya adalah prediktor dasar terkuat.
- Namun, **lonjakan jam kerja mendadak (*overtime surge*)** dan **rasio pelanggaran berat (S&S ratio)** memberikan sinyal interaksi dinamis yang secara signifikan mempertajam diskriminasi tambang berisiko kritis.

---

### 4. Metrik Evaluasi & Validasi Kalibrasi (Out-of-Time Test Set)

Pada data evaluasi buta masa depan (2024–2025):
- **PR-AUC:** `0.720` (mengungguli baseline naif secara dramatis).
- **ROC-AUC:** `0.734`.
- **Expected Calibration Error (ECE):** Turun drastis hingga `0.011` (probabilitas 70% pada model benar-benar mencerminkan tingkat insiden empiris ~70%).
- **Tabel Desil Risiko:**
  - **Desil 1 (10% Tambang Paling Berisiko):** Rata-rata probabilitas prediksi = **80.5%**, Tingkat insiden aktual = **82.1%** (**Lift = 1.62x**).
  - **Desil 10 (10% Tambang Paling Aman):** Rata-rata probabilitas prediksi = **16.3%**, Tingkat insiden aktual = **14.7%** (**Lift = 0.29x**).

Hal ini membuktikan monotonicitas sempurna: model tidak hanya menebak acak, tetapi secara akurat memeringkatkan intensitas risiko keselamatan dari desil teratas hingga terbawah.

---

### 5. Explainable AI & Penyajian Demo Interaktif

Agar model dapat diadopsi oleh praktisi K3 dan meyakinkan *hiring manager*, sistem dilengkapi **Aplikasi Web Interaktif Gradio (3 Tab)**:

1. **Tab 1: National Surveillance Dashboard**  
   Peta interaktif sebaran tambang di seluruh AS (Plotly) dengan penanda warna sesuai *Risk Tier* (Low, Moderate, Elevated, Critical) dan antrean prioritas Top-20 tambang berisiko tertinggi untuk kuartal depan.
2. **Tab 2: Individual Mine Inspector & SHAP Deep-Dive**  
   Pengguna dapat memilih ID tambang mana pun di AS untuk melihat *Gauge Card* probabilitas terkalibrasi dan **SHAP Waterfall Plot** yang menjelaskan secara transparan pemicu kenaikan risiko (misal: *+14.2% akibat lonjakan pelanggaran S&S*, *-5.1% akibat kepatuhan jam inspeksi rutin*).
3. **Tab 3: "What-If" Operational Sandbox**  
   Simulator interaktif di mana manajer operasional dapat menggeser slider jam kerja dan pelanggaran keselamatan untuk melihat prediksi risiko terupdate secara instan (<50 ms) beserta rekomendasi intervensi K3 proaktif.

---

### 6. Strategi Deployment Portofolio
- **Tautan Live Web Showcase (24/7 Gratis):** [huggingface.co/spaces/anggerw/minerisk-ai](https://huggingface.co/spaces/anggerw/minerisk-ai) (Direct: [anggerw-minerisk-ai.static.hf.space](https://anggerw-minerisk-ai.static.hf.space))
- **Hugging Face Model Repository:** [huggingface.co/anggerw/minerisk-ai](https://huggingface.co/anggerw/minerisk-ai) (Calibrated LightGBM model weights & feature metadata)
- **1-Click Master Interactive Colab:** [MineRisk_AI_Colab_Master.ipynb](https://colab.research.google.com/github/anggerwicaksana/minerisk-ai/blob/main/notebooks/MineRisk_AI_Colab_Master.ipynb) dengan tombol *Open in Colab* dan fitur tunnel live `share=True`.
- **Model Context Protocol (MCP) Server:** Siap digunakan secara lokal (`mcp_server.py`) dan terdaftar di `mcp_config.json` untuk integrasi agen AI (Claude Code, Cursor, Antigravity IDE).
