# TECHNICAL ARCHITECTURE SPECIFICATION
## System Name: MineRisk-AI (SafeCast)
### Predictive Industrial Safety & Health (OSH) Risk Intelligence System
**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Target Environments:** Python 3.10+, Google Colab (CPU/T4), Hugging Face Spaces (Gradio)  
**Parent Documents:** [Product Brief](file:///d:/PROJEK%20-%20BUSINESS/Predictive%20AI/product_brief.md) | [PRD.md](file:///d:/PROJEK%20-%20BUSINESS/Predictive%20AI/PRD.md)

---

## 1. System Architecture Overview

MineRisk-AI (SafeCast) dibangun dengan arsitektur **modular multi-tier** yang memisahkan antara *Data Pipeline & Ingestion*, *Feature Store*, *Machine Learning Engine*, *Explainability Layer*, dan *Application Serving Layer*. 

Seluruh alur data dirancang dengan prinsip **Zero Lookahead Bias** (bebas data leakage temporal) dan dioptimalkan agar dapat dieksekusi secara efisien pada resource Google Colab standard ($< 12 \text{ GB RAM}$) serta di-serving secara instan di Hugging Face Spaces.

```mermaid
flowchart TB
    subgraph Data_Sources["1. DATA SOURCES & INGESTION LAYER"]
        M1[Mines.txt]
        M2[QuarterlyEmploymentProduction.txt]
        M3[Inspections.txt]
        M4[Violations.txt]
        M5[Accidents.txt]
        Ingest[data_ingestion.py<br/>Polars Lazy Scan & Schema Enforcer]
        M1 & M2 & M3 & M4 & M5 --> Ingest
    end

    subgraph Relational_ETL["2. RELATIONAL PANEL ETL LAYER"]
        Ingest --> PanelBuilder[panel_builder.py<br/>Star-Schema Time-Indexed Join]
        PanelBuilder --> StarPanel[(Quarterly Mine Panel<br/>Unit: MINE_ID x CAL_YR x CAL_QTR)]
    end

    subgraph Feature_Store["3. LEAKAGE-PROOF FEATURE STORE"]
        StarPanel --> FE[feature_engineering.py<br/>Lags 1Q-4Q, Rolling Windows, Deltas, Ratios]
        FE --> TargetEngine[Target Construction Engine<br/>Label: Injury in Quarter t+1]
        TargetEngine --> TimeSplit[Strict Temporal Splitter<br/>Train: <=2021 | Val: 2022-23 | Test: 2024-25]
        TimeSplit --> ParquetOut[(Curated Parquet Datasets<br/>train.parquet / val.parquet / test.parquet)]
    end

    subgraph ML_Engine["4. MACHINE LEARNING & CALIBRATION"]
        ParquetOut --> Baseline[Baseline Models<br/>Naive Persistence & L2 Logistic]
        ParquetOut --> LGBM[LightGBM Classifier<br/>Hyperparameter Tuned on Validation]
        LGBM --> Calib[calibrator.py<br/>Platt / Isotonic Probability Calibration]
        Calib --> Eval[evaluator.py<br/>PR-AUC, ROC-AUC, Brier Score, Lift@Top-10%]
    end

    subgraph XAI_Engine["5. EXPLAINABILITY & GEOSPATIAL ENGINE"]
        Calib --> TreeSHAP[explainer.py<br/>SHAP TreeExplainer]
        TreeSHAP --> LocalSHAP[Waterfall Plot per Mine]
        TreeSHAP --> GlobalSHAP[Beeswarm & Feature Importance]
        ParquetOut --> GeoEngine[Geospatial Engine<br/>US Mine Risk Coordinates & Choropleth]
    end

    subgraph Artifact_Export["6. SERIALIZED LIGHTWEIGHT ARTIFACTS"]
        Calib --> ArtModel[artifacts/model_calibrated.joblib]
        TreeSHAP --> ArtSHAP[artifacts/shap_explainer.joblib]
        ParquetOut --> ArtSample[artifacts/demo_sample_panel.parquet]
        Eval --> ArtMetrics[artifacts/benchmark_metrics.json]
    end

    subgraph Serving_Layer["7. SERVING, MCP & PRESENTATION LAYER"]
        ArtModel & ArtSHAP & ArtSample & ArtMetrics --> GradioApp[app.py<br/>4-Tab Gradio UI + Native MCP Endpoint]
        ArtModel & ArtSample & ArtMetrics --> FastMCPServer[mcp_server.py<br/>FastMCP Server (Stdio & SSE)]
        GradioApp --> HFSpace["Hugging Face Spaces (Live Web + Official MCP Badge)"]
        GradioApp --> ColabMaster["Google Colab Master Notebook (Run All + Share Link)"]
        HFSpace --> HFHubMCP["Hugging Face Hub MCP Directory (1-Click Install)"]
        FastMCPServer --> LocalIDE["Local AI Agents: Antigravity IDE, Claude Code, Cursor"]
    end
```

---

## 2. Data Architecture & Relational Contracts

### 2.1 MSHA Source Tables Contract
MSHA mendistribusikan data dalam format file teks *pipe-delimited* (`|`). Setiap tabel memiliki peran fungsional spesifik:

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                       MSHA RELATIONAL ENTITY SPECIFICATION                     │
├──────────────────────────────┬──────────────────┬──────────────────────────────┤
│ Entity Name                  │ Grain / Unit     │ Join Key                     │
├──────────────────────────────┼──────────────────┼──────────────────────────────┤
│ Mines                        │ 1 mine           │ MINE_ID                      │
│ QuarterlyEmploymentProd      │ 1 mine x subunit │ MINE_ID, CAL_YR, CAL_QTR     │
│                              │   x quarter      │                              │
│ Inspections                  │ 1 inspection     │ EVENT_NO, MINE_ID            │
│ Violations                   │ 1 citation       │ EVENT_NO, MINE_ID            │
│ Accidents                    │ 1 injury event   │ DOCUMENT_NO, MINE_ID         │
└──────────────────────────────┴──────────────────┴──────────────────────────────┘
```

### 2.2 Star-Schema Panel Index & Aggregation
Unit analisis data modelling adalah **Mine-Quarter** $(i, t)$.  
Setiap baris panel dibentuk melalui agregasi deterministik:

$$\text{Panel Index} = (\text{MINE\_ID}, \text{CAL\_YR}, \text{CAL\_QTR})$$

#### Logika Agregasi Tabel Anak ke Panel Induk:
1. **Employment & Hours (`QuarterlyEmploymentProduction`):**
   - `total_hours` = $\sum \text{EMPLOYEE\_HOURS}$ per `(MINE_ID, CAL_YR, CAL_QTR)`.
   - `avg_employees` = $\frac{\sum \text{AVG_EMPLOYEE_CNT}}{\text{count(subunits)}}$.
   - `coal_production` = $\sum \text{COAL_PRODUCTION}$.
   - Filter integritas: Tambang harus memiliki $\text{total\_hours} > 0$.
2. **Inspections (`Inspections`):**
   - Waktu inspeksi dipetakan ke kuartal kalender berdasarkan `INSP_END_DATE`.
   - `insp_count` = $\text{count}(\text{EVENT\_NO})$ pada kuartal $t$.
   - `insp_hours` = $\sum \text{TOTAL\_INSP\_HOURS}$ pada kuartal $t$.
   - `insp_samples` = $\sum \text{SAMPLE\_CNT}$ pada kuartal $t$.
3. **Violations (`Violations`):**
   - Dipetakan ke kuartal berdasarkan `ISSUE_DATE`.
   - `viol_count` = $\text{count}(\text{VIOLATION\_NO})$ pada kuartal $t$.
   - `viol_ss_count` = $\sum \mathbb{I}(\text{SIG\_AND\_SUB} = \text{'Y'})$ pada kuartal $t$.
   - `viol_high_negligence` = $\sum \mathbb{I}(\text{NEGLIGENCE} \in [\text{'High'}, \text{'Reckless'}])$ pada kuartal $t$.
   - `viol_gravity_fatal` = $\sum \mathbb{I}(\text{LIKELIHOOD} = \text{'Occurred'} \lor \text{INJ\_ILLNESS} = \text{'Fatal'})$.
4. **Accidents & Safety History (`Accidents`):**
   - Dipetakan ke kuartal berdasarkan `ACCIDENT_DATE`.
   - `injury_count` = $\sum \mathbb{I}(\text{INJ\_DEGREE} \in [01..06])$ (Part 50 reportable injuries).
   - `days_lost_total` = $\sum (\text{DAYS\_LOST} + \text{DAYS\_RESTRICT})$.
   - `fatal_count` = $\sum \mathbb{I}(\text{INJ\_DEGREE} = 01)$.

---

## 3. Leakage-Proof Feature Engineering Specification

### 3.1 Strict Lookahead Boundary (Temporal Guardrail)
Untuk setiap observasi pada kuartal $t$ (misal: 2023 Q3, yang berakhir pada 30 September 2023):
- **Wajib:** Semua fitur fitur penjelas ($X_t$) hanya boleh mengagregasikan fakta yang terjadi pada atau sebelum tanggal cut-off kuartal $t$.
- **Dilarang:** Menggunakan variabel status mutakhir tambang (`CURRENT_*` fields di `Mines.txt`, seperti `CURRENT_STATUS`) yang mencerminkan kondisi tahun 2026 ke masa lalu. Hanya atribut fisik statis (`STATE`, `COAL_METAL_IND`, `PRIMARY_CANVASS_CD`, `LATITUDE`, `LONGITUDE`) yang diizinkan.
- **Dilarang:** Menggunakan kolom deskripsi narasi kecelakaan masa depan atau kode keparahan medis pada kuartal $t+1$.

### 3.2 Feature Matrix Catalog (32 Fitur Inti)

| No | Feature Name | Domain | Formula / Definisi | Tipe |
|---|---|---|---|---|
| 1 | `hours_worked_q0` | Exposure | Total jam kerja pekerja pada kuartal $t$ | Float |
| 2 | `avg_employees_q0` | Exposure | Rata-rata jumlah pekerja kuartal $t$ | Float |
| 3 | `log_hours_q0` | Exposure | $\ln(\text{hours\_worked\_q0} + 1)$ (Exposure offset) | Float |
| 4 | `hours_worked_lag1` | Exposure | Total jam kerja pekerja pada kuartal $t-1$ | Float |
| 5 | `hours_delta_1q` | Trend | $\text{hours\_worked\_q0} - \text{hours\_worked\_lag1}$ | Float |
| 6 | `hours_pct_change_1q` | Trend | $\frac{\text{hours\_delta\_1q}}{\text{hours\_worked\_lag1} + 1}$ (Lonjakan lembur) | Float |
| 7 | `hours_rolling_4q_mean`| Exposure | Rata-rata jam kerja 4 kuartal terakhir $(t-3 \dots t)$ | Float |
| 8 | `injury_count_q0` | Prior Safety | Jumlah cedera pekerja pada kuartal $t$ | Int |
| 9 | `injury_count_lag1` | Prior Safety | Jumlah cedera pekerja pada kuartal $t-1$ | Int |
| 10| `injury_count_lag2` | Prior Safety | Jumlah cedera pekerja pada kuartal $t-2$ | Int |
| 11| `injury_count_lag3` | Prior Safety | Jumlah cedera pekerja pada kuartal $t-3$ | Int |
| 12| `injury_rolling_4q_sum`| Prior Safety | Total cedera dalam 4 kuartal $(t-3 \dots t)$ | Int |
| 13| `days_lost_q0` | Prior Safety | Total hari kerja hilang/dibatasi pada kuartal $t$ | Int |
| 14| `days_lost_rolling_4q` | Prior Safety | Total hari kerja hilang dalam 4 kuartal | Int |
| 15| `injury_rate_per_200k_q0` | Prior Safety | $\frac{\text{injury\_count\_q0} \times 200{,}000}{\text{hours\_worked\_q0}}$ | Float |
| 16| `injury_rate_rolling_4q` | Prior Safety | $\frac{\text{injury\_rolling\_4q\_sum} \times 200{,}000}{\text{hours\_rolling\_4q\_mean} \times 4}$ | Float |
| 17| `has_prior_injury_q0` | Prior Safety | $\mathbb{I}(\text{injury\_count\_q0} \ge 1)$ | Binary |
| 18| `insp_count_q0` | Inspection | Jumlah sesi inspeksi MSHA pada kuartal $t$ | Int |
| 19| `insp_hours_q0` | Inspection | Total jam kerja inspektur MSHA di lapangan | Float |
| 20| `insp_hours_rolling_4q` | Inspection | Total jam inspeksi dalam 4 kuartal | Float |
| 21| `viol_count_q0` | Violations | Jumlah sitasi pelanggaran pada kuartal $t$ | Int |
| 22| `viol_count_lag1` | Violations | Jumlah sitasi pelanggaran pada kuartal $t-1$ | Int |
| 23| `viol_rolling_4q_sum` | Violations | Total pelanggaran dalam 4 kuartal | Int |
| 24| `viol_ss_count_q0` | Violations | Pelanggaran Significant & Substantial (S&S) | Int |
| 25| `viol_ss_ratio_q0` | Violations | $\frac{\text{viol\_ss\_count\_q0}}{\text{viol\_count\_q0} + 1}$ (Tingkat keparahan audit) | Float |
| 26| `viol_high_negligence_q0`| Violations | Pelanggaran berkategori kelalaian tinggi | Int |
| 27| `viol_per_insp_hour_q0` | Violations | $\frac{\text{viol\_count\_q0}}{\text{insp\_hours\_q0} + 0.1}$ (Kepadatan pelanggaran) | Float |
| 28| `coal_metal_ind` | Context | Kategori komoditas (`C` = Coal, `M` = Metal/Nonmetal) | Categorical |
| 29| `mine_type` | Context | Metode tambang (`Underground`, `Surface`, `Facility`) | Categorical |
| 30| `state` | Geography | Kode negara bagian AS (2-letter FIPS code) | Categorical |
| 31| `calendar_quarter` | Seasonality | Kuartal kalender ($1, 2, 3, 4$) | Categorical |
| 32| `consecutive_zero_injury_qtrs`| Dynamics | Jumlah kuartal berturut-turut tanpa cedera | Int |

### 3.3 Target Label Construction
$$\text{TARGET}_{i, t+1} = \mathbb{I}(\text{injury\_count}_{i, t+1} \ge 1)$$
Label target diekstraksi dari rekam jejak kecelakaan pada kuartal $t+1$.  
Baris kuartal observasi terbaru (misal: 2025 Q4 yang belum memiliki kuartal $t+1$) dipisahkan secara eksklusif ke dalam `unlabeled_latest_panel` yang digunakan untuk **prediksi operasional langsung pada aplikasi demo**.

---

## 4. Machine Learning & Calibration Engine

### 4.1 Strict Out-of-Time Splitting Strategy
Untuk menguji performa nyata model di dunia industri, dataset dipartisi berdasarkan garis waktu kalender:

```
  2012 Q1 ───────────────────────── 2021 Q4 │ 2022 Q1 ────── 2023 Q4 │ 2024 Q1 ────── 2025 Q4
               TRAIN SET                    │    VALIDATION SET      │       TEST SET
            (Model Training)                │ (Tuning & Calibration) │ (Final Benchmark Proof)
```

- **Train Set (2012–2021):** Digunakan untuk melatih algoritma dan mengestimasi bobot fitur.
- **Validation Set (2022–2023):** Digunakan untuk hyperparameter search, early stopping LightGBM, dan fitting post-hoc calibration (Platt/Isotonic).
- **Test Set (2024–2025):** Data evaluasi buta (*unseen out-of-time test*) untuk membuktikan bahwa model mampu mengantisipasi risiko masa depan secara akurat.

### 4.2 Model Zoo & Benchmarks
Sistem membandingkan 3 model untuk membuktikan keunggulan arsitektur:

1. **Model 0 — Naive Historical Persistence Baseline:**
   - Aturan: $\hat{y}_{t+1} = \mathbb{I}(\text{injury\_count}_t \ge 1)$.
   - Rationale: Mengukur seberapa banyak informasi yang didapat hanya dengan mengasumsikan "tambang yang celaka kemarin akan celaka lagi besok".
2. **Model 1 — L2-Regularized Logistic Regression:**
   - Pipeline: Standard Scaler + Simple Imputer + Logistic Regression (C=1.0).
   - Rationale: Model linier terstandardisasi sebagai pembanding interpretasi klasik.
3. **Model 2 — Flagship Calibrated LightGBM (`LGBMClassifier`):**
   - Hyperparameter space:
     ```python
     params = {
         "n_estimators": 500,
         "learning_rate": 0.03,
         "num_leaves": 31,
         "max_depth": 6,
         "min_child_samples": 50,
         "subsample": 0.8,
         "colsample_bytree": 0.8,
         "scale_pos_weight": 2.5,  # Penyeimbang class imbalance
         "random_state": 42,
         "n_jobs": -1
     }
     ```
   - Early stopping: 30 rounds dievaluasi pada Validation Set PR-AUC.

### 4.3 Probability Calibration Engine
Model tree seperti LightGBM sering menghasilkan probabilitas mentah yang terdistorsi di dekat margin batas keputusan. MineRisk-AI menerapkan **Platt Scaling (Logistic Sigmoid)** atau **Isotonic Regression**:

$$P(\text{Risk} = 1 \mid f(x)) = \frac{1}{1 + \exp(A \cdot f(x) + B)}$$

Di mana parameter $A$ dan $B$ di-fit secara ketat hanya pada **Validation Set**.  
Evaluasi kalibrasi diukur menggunakan **Brier Score** dan kurva reliabilitas 10-bin decile:

$$\text{Brier Score} = \frac{1}{N} \sum_{i=1}^N (P_i - y_i)^2$$

### 4.4 Feature Family Ablation Framework
Untuk menjawab pertanyaan evaluasi bisnis, model dilatih secara bertingkat pada 5 keluarga fitur:
- **Ablation A:** Exposure Sahaja (`log_hours`, `avg_employees`, `state`, `mine_type`).
- **Ablation B:** A + Histori Cedera Lampau (`injury_count_lags`, `days_lost`).
- **Ablation C:** B + Intensitas Inspeksi (`insp_hours`, `insp_count`).
- **Ablation D:** C + Rekam Jejak Pelanggaran Regulasi (`viol_count`, `viol_ss_ratio`, `high_negligence`).
- **Ablation E:** D + Tren Lonjakan Jam Lembur & Interaksi Dinamis.

---

## 5. Explainable AI (XAI) & Geospatial Intelligence

### 5.1 SHAP TreeExplainer Implementation
Sistem menggunakan modul `shap.TreeExplainer` yang dioptimalkan untuk model berbasis pohon (Tree Models):
- **Global Explainability:**
  - Menghasilkan ringkasan dampak fitur nasional (*Summary Beeswarm Plot*) dan ranking fitur absolut.
- **Local Instance Explainability:**
  - Setiap kali tambang dianalisis di aplikasi web, sistem mengekstraksi vektor nilai SHAP individu:
    $$f(x) = \phi_0 + \sum_{j=1}^M \phi_j(x)$$
    di mana $\phi_0$ adalah baseline probabilitas nasional dan $\phi_j$ adalah dampak marginal dari fitur $j$.
  - Dirender menjadi **Waterfall Plot** yang menampilkan 5 faktor pemicu kenaikan risiko terbesar dan 3 faktor peredam risiko.

### 5.2 Geospatial Risk Intelligence
Panel tambang kuartal mutakhir digabungkan dengan koordinat (`LATITUDE`, `LONGITUDE` dari `Mines.txt`):
- Diklasifikasikan ke dalam 4 Tier Risiko:
  - **Low Risk:** $P < 20\%$ (Hijau)
  - **Moderate Risk:** $20\% \le P < 45\%$ (Kuning)
  - **Elevated Risk:** $45\% \le P < 70\%$ (Oranye)
  - **Critical Risk:** $P \ge 70\%$ (Merah)
- Ditampilkan melalui peta interaktif Plotly/Folium dengan klasterisasi titik dan tooltip rincian nama tambang, komoditas, dan probabilitas risiko.

---

## 6. Interactive Web Application Architecture (`app.py`)

Aplikasi web dibangun menggunakan **Gradio 4.x / 5.x** dengan layout responsif:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MINERISK-AI WEB APPLICATION                     │
├────────────────────────────────────────────────────────────────────────┤
│ [Header] Title, Live Status Badge, Model Performance Summary           │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────┬──────────────────────┬──────────────────────────┐ │
│ │ TAB 1: DASHBOARD │ TAB 2: MINE EXAMINER │ TAB 3: WHAT-IF SIMULATOR │ │
│ └──────────────────┴──────────────────────┴──────────────────────────┘ │
│                                                                        │
│ TAB 1 CONTENT:                                                         │
│ • Key Performance Indicator Cards (Total Mines, High Risk %, Top Lift) │
│ • Interactive US Map with Risk Filters (Commodity, State, Risk Tier)   │
│ • Sortable Top-20 High Risk Mines Table for Next Quarter               │
│                                                                        │
│ TAB 2 CONTENT:                                                         │
│ • Search / Select Mine by ID or Name                                   │
│ • Gauge Chart: Calibrated Risk Probability (e.g., 74.2% - CRITICAL)    │
│ • Benchmark Comparison Bar (This Mine vs National Industry Average)    │
│ • Interactive SHAP Waterfall Plot (Top Positive & Negative Risk Drivers│
│                                                                        │
│ TAB 3 CONTENT:                                                         │
│ • Sliders: Quarterly Hours, Safety Violations, S&S Citations, Mine Type│
│ • Instant Real-Time Probability Re-calculation (< 50ms)                │
│ • Dynamic Actionable OSH Safety Recommendation Text                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Storage, Directory Structure & Code Organization

Untuk menjaga kebersihan, keteraturan, dan kemudahan pemeliharaan kode:

```
Predictive AI/
├── product_brief.md                     # Visi produk & tracking status
├── PRD.md                               # Dokumen kebutuhan produk
├── ARCHITECTURE.md                      # Dokumen arsitektur teknis (this file)
├── requirements.txt                     # Dependensi Python
├── app.py                               # Entry-point aplikasi web Gradio
│
├── src/                                 # Modul inti Python (reusable & testable)
│   ├── __init__.py
│   ├── config.py                        # Konfigurasi konstanta, URL, direktori
│   ├── ingestion.py                     # Polars lazy data ingestion & validation
│   ├── panel_builder.py                 # Star-schema time-indexed join engine
│   ├── feature_engineering.py           # Komputasi lag, rolling, ratios, target
│   ├── model.py                         # LightGBM training, baselines, ablation
│   ├── calibration.py                   # Platt scaling & Isotonic calibrator
│   ├── evaluation.py                    # PR-AUC, ROC-AUC, Lift, Brier, calibration curves
│   └── explainability.py                # SHAP TreeExplainer & geospatial visualizer
│
├── artifacts/                           # Output serialisasi ringan (< 50 MB)
│   ├── model_calibrated.joblib          # Pipeline model final terkalibrasi
│   ├── feature_metadata.json            # Daftar fitur, tipe, dan statistik ringkas
│   ├── benchmark_metrics.json           # Hasil evaluasi numerik lengkap
│   └── demo_sample_panel.parquet        # Sampel data kuartal terbaru untuk web app
│
└── notebooks/
    └── MineRisk_AI_Colab_Master.ipynb   # Master reproducible notebook untuk Google Colab
```

---

## 8. Multi-Environment Deployment & Packaging

### 8.1 Lingkungan 1: Google Colab Master Notebook
- Berkas tunggal: `notebooks/MineRisk_AI_Colab_Master.ipynb`.
- Dilengkapi blok setup otomatis:
  ```python
  # Otomatis deteksi Colab vs Local
  import os
  IN_COLAB = "google.colab" in str(get_ipython())
  if IN_COLAB:
      !pip install polars lightgbm shap gradio plotly -q
  ```
- Menjalankan seluruh pipeline dari ekstraksi data sampel MSHA hingga meluncurkan Gradio secara in-notebook dan memunculkan link publik `gradio.live`.

### 8.2 Lingkungan 2: Hugging Face Spaces (Permanent Live Demo Link)
- Repository Git terpisah atau deploy direct ke Spaces dengan runtime **Gradio**.
- Folder root berisi:
  - `app.py`
  - `requirements.txt`
  - `artifacts/` (berisi model terkompresi dan sampel data kuartal terbaru).
- Memungkinkan recruiter mengakses aplikasi web kapan pun secara instan tanpa perlu menjalankan Colab.

---

## 9. Technical Risk Mitigation & Edge Cases

| Risiko Teknis | Dampak | Strategi Mitigasi Arsitektur |
|---|---|---|
| **RAM Crash di Colab (OOM)** | Fatal pipeline error | Menggunakan Polars lazy scan, memilih hanya kolom esensial (*projection pushdown*), dan membuang tabel raw setelah agregasi kuartal selesai. |
| **Data Leakage Kolom `CURRENT_*`** | Klaim AI tidak valid | Secara eksplisit mendrop seluruh kolom yang berawalan `CURRENT_` sebelum pembentukan panel historis. |
| **Tambang Baru Tanpa Riwayat Lags** | Nilai NaN pada fitur lag | Imputasi cerdas berbasis median kelompok komoditas sejenis (`COAL_METAL_IND`) disertai flag indikator `is_new_mine = 1`. |
| **Extreme Class Imbalance** | Model memprediksi 0 sepanjang waktu | Mengatur `scale_pos_weight` pada LightGBM dan menggunakan PR-AUC serta decile lift sebagai panduan tuning utama (bukan akurasi). |
| **Cold-Start Lambat di HF Spaces** | Pengguna/recruiter menunggu lama | Model dan panel sampel dioptimalkan dalam format joblib dan parquet terkompresi ($< 30 \text{ MB}$ total), menjamin loading $< 5$ detik. |

---
*Dokumen ARCHITECTURE.md ini mengunci seluruh spesifikasi teknis sistem MineRisk-AI. Tahap berikutnya adalah mengeksekusi Phase 2: Data Ingestion & Relational Panel Engineering.*
