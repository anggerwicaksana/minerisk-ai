# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Project Name: MineRisk-AI (SafeCast)
### Predictive Workplace Safety & Health (OSH) Risk Intelligence System
**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Target Environment:** Python 3.10+, Google Colab (Standard CPU/T4 GPU), Hugging Face Spaces (Gradio)  
**Parent Document:** [Product Brief](file:///d:/PROJEK%20-%20BUSINESS/Predictive%20AI/product_brief.md)

---

## 1. Overview & Strategic Goals

### 1.1 Problem Statement
Pengawasan Keselamatan dan Kesehatan Kerja (K3) di industri pertambangan dan ekstraktif skala besar saat ini didominasi oleh pendekatan reaktif—analisis investigasi baru dilakukan setelah insiden cedera, kecelakaan berat, atau korban jiwa terjadi. Upaya preventif sering kali terhambat oleh keterbatasan rasio inspektur terhadap jumlah site tambang yang aktif, serta pemisahan (*data silo*) antara catatan operasional tambang (jam kerja, tonase produksi), data kepatuhan audit regulasi (inspeksi, sitasi pelanggaran), dan histori insiden.

### 1.2 Product Vision
**MineRisk-AI (SafeCast)** adalah platform *predictive safety intelligence* yang mengonsolidasikan data relasional resmi pemerintah federal AS (**U.S. Mine Safety and Health Administration - MSHA**) selama periode multi-dekade (2000–2025). Sistem ini memberikan kemampuan peramalan prospektif (*prospective risk forecasting*):
> **Menilai probabilitas sebuah tambang aktif akan mengalami insiden cedera kerja pada kuartal mendatang ($t+1$) berdasarkan sinyal operasional, intensitas inspeksi, dan kepatuhan keselamatan historis hingga akhir kuartal berjalan ($t$).**

### 1.3 Target Audience & User Personas
1. **Persona 1 — Recruiter / AI Hiring Manager (Primary Portfolio Audience):**
   - *Tujuan:* Mengevaluasi kedalaman teknis kandidat dalam data engineering relasional, pemahaman *lookahead bias / data leakage*, pemodelan tabular modern (LightGBM), kalibrasi probabilitas, dan *Explainable AI* (SHAP).
   - *Kebutuhan:* Akses instan ke demo interaktif 24/7 via tautan web publik (Hugging Face Spaces), kode transparan di Google Colab, serta dokumentasi arsitektur yang solid.
2. **Persona 2 — Chief Safety Officer / Mine General Manager:**
   - *Tujuan:* Mengidentifikasi site operasi tambang mana yang memiliki eskalasi risiko tersembunyi (*latent hazard*) sebelum insiden terjadi.
   - *Kebutuhan:* *Early-warning risk score*, visualisasi pemicu risiko lokal (SHAP), dan simulator *What-If* untuk menguji dampak intervensi keselamatan (misal: pengurangan jam lembur atau pemenuhan audit).
3. **Persona 3 — OSH Inspector / Regulatory Compliance Officer:**
   - *Tujuan:* Melakukan alokasi sumber daya inspeksi lapangan berbasis prioritas risiko (*risk-based audit scheduling*).
   - *Kebutuhan:* Peta geospasial sebaran tambang berisiko tinggi dan daftar prioritas kuartalan (*Top-Decile Risk Ranking*).

---

## 2. Success Metrics & Key Results (OKRs)

### 2.1 Model Performance Benchmarks (Out-of-Time Test Set)
Pengujian dilakukan secara ketat pada data masa depan yang belum pernah dilihat model (*strict out-of-time temporal test set*, misal: Train $\le 2021$, Val 2022–2023, Test 2024–2025):

| Metrik Evaluasi | Target Minimum | Target Unggul (Flagship) | Rationale |
|---|---|---|---|
| **PR-AUC (Precision-Recall AUC)** | $\ge 0.45$ | $\ge 0.55$ | Metrik utama untuk data kelas tidak seimbang (*imbalanced positive rate* ~15-25%). |
| **ROC-AUC** | $\ge 0.75$ | $\ge 0.82$ | Kemampuan diskriminasi pemeringkatan tambang berisiko vs tidak berisiko. |
| **Lift @ Top 10% Scored Mines** | $\ge 2.5\times$ | $\ge 3.2\times$ | Tambang dalam desil risiko tertinggi model harus memiliki rasio insiden riil minimal 2.5× lipat rata-rata populasi. |
| **Recall @ Top 10% / Top 20%** | $\ge 40\%$ / $\ge 60\%$ | $\ge 50\%$ / $\ge 70\%$ | Mengonfirmasi sebagian besar insiden masa depan terkonsentrasi pada kelompok yang diprioritaskan. |
| **Brier Score (Probabilitas Terkalibrasi)** | $\le 0.15$ | $\le 0.12$ | Mengukur keakuratan estimasi probabilitas numerik (bukan sekadar prediksi biner 0/1). |
| **Expected Calibration Error (ECE)** | $\le 0.05$ | $\le 0.03$ | Memastikan probabilitas 70% benar-benar mencerminkan 70% frekuensi kejadian empiris. |

### 2.2 System & Portfolio OKRs
- **KR1 (Zero Leakage):** Terbukti 100% bebas dari fitur masa depan atau post-event artifacts (audit formal pada metadata kolom dan cut-off tanggal).
- **KR2 (Reproducibility):** Pipeline end-to-end dapat dijalankan dalam sekali klik (*Run All*) di Google Colab runtime gratis dalam waktu $< 15$ menit.
- **KR3 (Live Availability):** Demo interaktif berbasis Gradio ter-deploy aktif 24/7 di Hugging Face Spaces tanpa error cold-start.

---

## 3. Data Specification & Data Contracts

### 3.1 Raw Datasets (MSHA Federal Open Data)
Semua dataset bersumber langsung dari U.S. Mine Safety and Health Administration (MSHA) tanpa modifikasi manual:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MSHA OPEN DATA ENDPOINTS                        │
├───────────────────────────────┬────────────────────────────────────────┤
│ Dataset Name                  │ Official Source File / Format          │
├───────────────────────────────┼────────────────────────────────────────┤
│ 1. Mines Registry             │ Mines.txt (Pipe-delimited |)           │
│ 2. Quarterly Employment/Prod  │ QuarterlyEmploymentProduction.txt (|)  │
│ 3. Accident, Injury & Illness │ Accidents.txt (|)                      │
│ 4. Inspections                │ Inspections.txt (|)                    │
│ 5. Violations                 │ Violations.txt (|)                     │
└───────────────────────────────┴────────────────────────────────────────┘
```

#### Detail Kontrak Data Relasional:
1. **`Mines.txt` (Entitas Master Tambang):**
   - *Primary Key:* `MINE_ID` (7-digit string).
   - *Kolom Kunci:* `CURRENT_MINE_NAME`, `STATE`, `FIPS_CNTY_CD`, `COAL_METAL_IND`, `PRIMARY_SIC_CD`, `PRIMARY_CANVASS_CD` (Surface vs Underground), `LATITUDE`, `LONGITUDE`.
   - *Aturan Khusus:* Kolom berawalan `CURRENT_*` adalah status operasional mutakhir saat file diekspor. **Dilarang** digunakan sebagai fitur temporal lampau jika nilainya berubah seiring waktu; hanya gunakan atribut geografis dan tipe tambang fisik yang invarian.
2. **`QuarterlyEmploymentProduction.txt` (Denominasi Paparan / Exposure):**
   - *Composite Key:* `MINE_ID` + `CAL_YR` + `CAL_QTR` + `SUBUNIT_CD`.
   - *Kolom Kunci:* `AVG_EMPLOYEE_CNT`, `EMPLOYEE_HOURS`, `COAL_PRODUCTION`.
   - *Aturan Khusus:* Agregasi ke level `(MINE_ID, CAL_YR, CAL_QTR)` dengan menjumlahkan `EMPLOYEE_HOURS` dan `COAL_PRODUCTION`, serta merata-ratakan `AVG_EMPLOYEE_CNT`. Baris dengan `EMPLOYEE_HOURS <= 0` difilter atau ditandai sebagai tambang tidak aktif (*idle*).
3. **`Inspections.txt` (Aktivitas Penegakan Hukum):**
   - *Primary Key:* `EVENT_NO`.
   - *Foreign Key:* `MINE_ID`.
   - *Kolom Kunci:* `INSP_START_DATE`, `INSP_END_DATE`, `INSPECTION_TYPE_CODE`, `TOTAL_INSP_HOURS`, `SAMPLE_CNT`.
   - *Aturan Khusus:* Tanggal inspeksi dipetakan ke kuartal kalender berdasarkan `INSP_END_DATE`.
4. **`Violations.txt` (Sitasi Pelanggaran Regulasi):**
   - *Foreign Keys:* `EVENT_NO`, `MINE_ID`.
   - *Kolom Kunci:* `ISSUE_DATE`, `SIG_AND_SUB` (Significant & Substantial: Y/N), `NEGLIGENCE_CD`, `LIKELIHOOD_CD`, `INJ_ILLNESS_CD`, `PROPOSED_PENALTY`.
   - *Aturan Khusus:* Tanggal pelanggaran dipetakan ke kuartal kalender berdasarkan `ISSUE_DATE`.
5. **`Accidents.txt` (Histori Insiden & Target Ground Truth):**
   - *Primary Key:* `DOCUMENT_NO`.
   - *Foreign Key:* `MINE_ID`.
   - *Kolom Kunci:* `ACCIDENT_DATE`, `CAL_YR`, `CAL_QTR`, `INJ_DEGREE_CD`, `DAYS_RESTRICT`, `DAYS_LOST`, `ACCIDENT_TYPE`, `NARRATIVE`.
   - *Aturan Khusus:* Digunakan ganda:
     - Sebagai **Target Prediksi Masa Depan** pada kuartal $t+1$.
     - Sebagai **Fitur Riwayat Keselamatan Lampau (*Lag Features*)** hanya untuk kejadian yang terjadi $\le$ kuartal $t$.

---

## 4. Functional Requirements (FR)

### Module 1: Ingestion & Panel ETL Engine (`pipeline/`)
- **FR-1.1 (Automated Fetching):** Sistem harus dapat mengunduh atau membaca arsip raw MSHA secara langsung melalui URL resmi atau cache lokal terkompresi.
- **FR-1.2 (Lazy Ingestion via Polars):** Ingestion wajib menggunakan Polars dengan teknik *lazy scan* dan pemilihan kolom spesifik (*projection pushdown*) untuk menjamin penggunaan memori RAM tetap di bawah 4 GB pada Google Colab standard.
- **FR-1.3 (Star Schema Panel Construction):** Sistem wajib membentuk panel observasi dengan unit analisis unik per tambang-kuartal:
  $$\text{Index} = (\text{MINE\_ID}, \text{CAL\_YR}, \text{CAL\_QTR})$$
  untuk semua tambang aktif yang memiliki $\text{EMPLOYEE\_HOURS} > 0$.
- **FR-1.4 (Temporal Aggregation Join):** Menggabungkan tabel Inspeksi, Pelanggaran, dan Kecelakaan ke panel kuartal berjalan melalui join agregasi temporal:
  - Jumlah inspeksi dan total jam inspeksi pada kuartal $t$.
  - Jumlah sitasi pelanggaran, jumlah pelanggaran S&S, dan rasio kelalaian berat pada kuartal $t$.
  - Jumlah kasus cedera dan total *days lost* pada kuartal $t$.

### Module 2: Feature Engineering & Target Construction (`features/`)
- **FR-2.1 (Target Variable Formulation):**
  - *Primary Target (`target_has_injury_next_qtr`):* Nilai biner $\in \{0, 1\}$. Bernilai 1 jika tambang mencatat minimal 1 kasus cedera pekerja terkualifikasi (MSHA Part 50 qualifying cases, `INJ_DEGREE_CD` $\in [01..06]$) pada kuartal $t+1$.
  - *Secondary Target (`target_injury_count_next_qtr`):* Jumlah kejadian cedera pada kuartal $t+1$ (untuk analisis regresi count/Poisson).
- **FR-2.2 (Lag & Rolling Window Features):**
  - Lag 1 Kuartal ($t$), Lag 2 Kuartal ($t-1$), Lag 4 Kuartal ($t-3$).
  - Rolling mean 4 kuartal untuk jam kerja, rasio cedera per 200,000 jam, dan rasio sitasi per jam inspeksi.
  - Sinyal tren ($\Delta = \text{val}_t - \text{val}_{t-1}$) untuk mendeteksi lonjakan mendadak jam lembur (*overtime surge*) atau eskalasi pelanggaran keselamatan.
- **FR-2.3 (Categorical & Interaction Encodings):**
  - Tipe komoditas (`COAL_METAL_IND`), metode penambangan (`SURFACE_UNDERGROUND`), dan kode negara bagian (`STATE`).
  - Fitur interaksi: rasio pelanggaran per jam kerja ($\frac{\text{Violations}_t}{\text{Hours}_t / 200{,}000}$).
- **FR-2.4 (Strict Temporal Partitioning):**
  - **Train Set:** Kuartal historis (misal: 2012 Q1 – 2021 Q4).
  - **Validation Set (Tuning & Calibration):** Kuartal transisi (misal: 2022 Q1 – 2023 Q4).
  - **Test Set (Out-of-Time Final Evaluation):** Kuartal kontemporer (misal: 2024 Q1 – 2025 Q4).
  - *Banned:* Penggunaan `train_test_split` acak / K-Fold standar dilarang keras untuk mencegah temporal leakage.

### Module 3: Machine Learning & Calibration Engine (`models/`)
- **FR-3.1 (Baseline Benchmarks):**
  - *Baseline 1 (Naive Historical Persistence):* Memprediksi kuartal $t+1$ berisiko jika kuartal $t$ memiliki cedera $\ge 1$.
  - *Baseline 2 (L2-Regularized Logistic Regression):* Model linear dengan standardisasi fitur sebagai pembanding interpretasi klasik.
- **FR-3.2 (Production Model - LightGBM Classifier):**
  - Implementasi *Gradient Boosted Decision Trees* (LightGBM) dengan penanganan data tidak seimbang (*scale_pos_weight* atau focal loss terbobot).
  - Hyperparameter tuning terarah (learning rate, num_leaves, min_child_samples, feature_fraction) yang dievaluasi pada Validation Set.
- **FR-3.3 (Post-Hoc Probability Calibration):**
  - Melakukan kalibrasi probabilitas output model menggunakan *Isotonic Regression* atau *Platt Scaling* (Sigmoid) yang di-fit pada Validation Set.
  - Memastikan kurva reliabilitas (*calibration curve*) mendekati diagonal sempurna ($y = x$).
- **FR-3.4 (Feature Family Ablation Study):**
  - Mengevaluasi performa model secara bertahap untuk menjawab pertanyaan bisnis: *"Berapa banyak daya prediksi tambahan yang diberikan oleh data audit inspeksi regulasi dibandingkan histori kecelakaan saja?"*
    - Model A: Baseline Exposure & Lokasi.
    - Model B: Model A + Riwayat Kecelakaan Masa Lalu.
    - Model C: Model B + Data Frekuensi Inspeksi MSHA.
    - Model D: Model C + Pelanggaran Regulasi & Sitasi S&S.
    - Model E: Model D + Sinyal Tren & Rolling Averages.

### Module 4: Explainability & Geospatial Intelligence (`explainability/`)
- **FR-4.1 (Global SHAP Explainer):**
  - Menghitung nilai SHAP (SHapley Additive exPlanations) menggunakan `shap.TreeExplainer`.
  - Menghasilkan plot ringkasan global (*SHAP Beeswarm Plot* dan *Feature Importance Bar Chart*).
- **FR-4.2 (Local Instance-Level Explainer):**
  - Untuk setiap tambang spesifik, menghasilkan *SHAP Waterfall Plot* yang merinci kontribusi setiap faktor terhadap deviasi risiko dari baseline nasional.
- **FR-4.3 (Geospatial Mapping Engine):**
  - Menghasilkan peta sebaran tambang interaktif (menggunakan Plotly / Folium) di seluruh Amerika Serikat, dengan penanda warna sesuai tingkat risiko (*Risk Tier*).

### Module 5: Interactive Web Application (`app.py` & Gradio UI)
- **FR-5.1 (Tab 1: National Surveillance Dashboard):**
  - Ringkasan KPI nasional (Total tambang dipantau, proporsi berisiko tinggi, desil risiko).
  - Peta interaktif US Mine Risk Map dengan filter negara bagian dan komoditas.
  - Tabel interaktif Top-20 Tambang Berisiko Tinggi untuk kuartal mendatang.
- **FR-5.2 (Tab 2: Mine Risk Inspector & SHAP Deep-Dive):**
  - Input: Dropdown pemilihan ID Tambang atau nama tambang.
  - Output: Kartu Skor Risiko (*Predicted Risk Probability* $\in [0\%, 100\%]$, *Risk Tier Badge*: Low / Moderate / Elevated / Critical), perbandingan terhadap rata-rata industri sejenis, dan visualisasi interaktif SHAP Waterfall.
- **FR-5.3 (Tab 3: "What-If" Operational Risk Sandbox):**
  - Slider kontrol interaktif:
    - Estimasi jam kerja pekerja kuartalan (0 – 250,000 jam).
    - Jumlah pelanggaran keselamatan (0 – 20 sitasi).
    - Status pelanggaran S&S (Ya/Tidak).
    - Metode penambangan (Surface vs Underground).
    - Komoditas (Coal, Stone, Metal).
  - Output Real-Time: Kalkulasi ulang probabilitas risiko dan narasi rekomendasi pencegahan keselamatan yang dihasilkan secara otomatis.

---

## 5. Non-Functional Requirements (NFR)

- **NFR-1 (Compute & Memory Efficiency):**
  - Seluruh pipeline pembuatan panel kuartalan wajib dapat dieksekusi pada lingkungan RAM standar 12 GB (Google Colab free tier) tanpa memicu crash *Out-of-Memory* (OOM).
  - Format penyimpanan perantara (*intermediate artifacts*) wajib menggunakan **Apache Parquet** terkompresi Snappy/ZSTD, bukan CSV mentah berukuran gigabyte.
- **NFR-2 (Inference Latency):**
  - Latensi inferensi lokal pada aplikasi Gradio untuk satu tambang atau simulasi *What-If* wajib $< 200 \text{ ms}$.
- **NFR-3 (Strict Reproducibility):**
  - Seluruh algoritma acak (split data, inisialisasi LightGBM) wajib menggunakan `random_state = 42`.
  - Skrip pengujian otomatis harus memastikan hasil evaluasi identik saat dieksekusi ulang.
- **NFR-4 (Robust Error Handling & Graceful Degradation):**
  - Jika tambang yang dipilih memiliki data historis yang hilang (*missing values*), model harus menggunakan imputasi berbasis peer-group NAICS/komoditas tanpa menimbulkan fatal runtime error.
- **NFR-5 (Data Privacy & Compliance):**
  - Proyek ini menggunakan 100% data publik domain pemerintah AS (Public Domain). Tidak boleh ada ekstraksi data identitas pribadi pekerja (PII). Seluruh analisis berfokus pada level entitas tambang (*establishment-level*).

---

## 6. System Architecture & Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             MINERISK-AI ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ MSHA Open Data (5 Raw Tables) ]                                          │
│        │                                                                    │
│        ▼                                                                    │
│  [ Ingestion & Validation Engine (Polars Lazy Scan) ]                       │
│        │                                                                    │
│        ▼                                                                    │
│  [ Quarterly Star-Schema Panel Builder: (MINE_ID, YR, QTR) ]                │
│        │                                                                    │
│        ▼                                                                    │
│  [ Leakage-Proof Feature Engineering & Lag Pipeline ]                       │
│        │                                                                    │
│        ▼                                                                    │
│  [ Strict Out-of-Time Split (Train <= 2021 | Val 2022-23 | Test 2024-25) ] │
│        │                                                                    │
│        ├────────────────────────────┬─────────────────────────────┐         │
│        ▼                            ▼                             ▼         │
│  [ Baseline Logistic ]    [ LightGBM Classifier ]       [ Ablation Suite ]  │
│                                     │                                       │
│                                     ▼                                       │
│                           [ Probability Calibration ]                       │
│                                (Platt / Isotonic)                           │
│                                     │                                       │
│                                     ▼                                       │
│                           [ SHAP TreeExplainer ]                            │
│                                     │                                       │
│                                     ▼                                       │
│                     [ Exported Lightweight Artifacts ]                      │
│                       (model.joblib, calib.joblib,                          │
│                        sample_panel.parquet)                                │
│                                     │                                       │
│        ┌────────────────────────────┴─────────────────────────────┐         │
│        ▼                                                          ▼         │
│  [ Google Colab Master ]                                  [ Gradio Web App] │
│   - End-to-end execution                                   - 3 Interactive  │
│   - Visual analysis plots                                    Tabs           │
│   - Colab share link                                       - HF Spaces 24/7 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Delivery Strategy: Colab & Hugging Face Spaces

### 7.1 Struktur Folder Proyek
```
Predictive AI/
├── product_brief.md                    # Ringkasan visi produk
├── PRD.md                              # Dokumen spesifikasi kebutuhan produk (this file)
├── ARCHITECTURE.md                     # Desain detail arsitektur teknis
├── requirements.txt                    # Dependensi runtime Python
├── app.py                              # Gradio web app untuk deployment Hugging Face
│
├── src/                                # Core Engine Module
│   ├── __init__.py
│   ├── config.py                       # URL, parameter, cut-off dates
│   ├── data_ingestion.py               # Downloader & Polars loader
│   ├── panel_builder.py                # Star-schema join kuartalan
│   ├── feature_engineering.py          # Lags, rolling, exposure offsets
│   ├── model_trainer.py                # LightGBM, baselines & tuning
│   ├── calibrator.py                   # Platt / Isotonic probability calibration
│   ├── evaluator.py                    # PR-AUC, ROC-AUC, Lift, Brier, Deciles
│   └── explainer.py                    # SHAP tree explainer & plotters
│
├── artifacts/                          # Serialized lightweight outputs untuk demo
│   ├── model_calibrated.joblib         # Model final terkalibrasi (~2-5 MB)
│   ├── feature_metadata.json           # Skema & urutan kolom fitur
│   ├── benchmark_metrics.json          # Metrik evaluasi lengkap
│   └── demo_sample_panel.parquet       # Sampel data kuartal terbaru (~10-20 MB)
│
└── notebooks/
    └── MineRisk_AI_Colab_Master.ipynb  # Master reproducible notebook untuk Colab
```

### 7.2 Deployment Plan Hugging Face Spaces
1. **Repository Target:** Hugging Face Space dengan SDK: `gradio`.
2. **Kemandirian File:** Folder root berisi `app.py`, `requirements.txt`, dan folder `artifacts/`.
3. **Cold-Start Optimization:** Ukuran artefak di bawah 50 MB, memungkinkan aplikasi menyala dalam waktu $< 15$ detik saat diakses oleh *recruiter*.

---

## 8. Ethics, Governance & Regulatory Disclaimer

1. **Decision Support, Not Autonomous Sanction:**  
   Model ini dirancang sebagai instrumen pendukung keputusan (*decision-support system*) untuk memprioritaskan alokasi audit preventif, bukan sebagai sistem otomatis untuk menjatuhkan sanksi hukum atau melabeli tambang sebagai "berbahaya mutlak".
2. **Observational Data Nuance:**  
   Frekuensi pelanggaran dan laporan cedera dapat dipengaruhi oleh intensitas pengawasan dan variasi keterbukaan pelaporan (*reporting propensity*), bukan semata-mata risiko murni. Dokumentasi portofolio wajib menyertakan catatan keterbatasan ini secara eksplisit untuk menunjukkan kedewasaan metodologi seorang Data Scientist senior.

---

## 9. Sign-off & Next Steps

Dengan disetujuinya dokumen **PRD.md** ini, implementasi akan melangkah ke:
1. **Fase 1.3:** Penyusunan dokumen arsitektur teknis mendalam (**`ARCHITECTURE.md`**).
2. **Fase 2:** Implementasi modul *data ingestion* dan *panel ETL* menggunakan Polars.
