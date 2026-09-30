"""Generates the master reproducible Google Colab notebook for MineRisk-AI."""

import json
from pathlib import Path

notebook_data = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# MineRisk AI (SafeCast): Predictive Industrial Safety Risk Intelligence\n",
                "### *A Multi-Table Relational Machine Learning System on 25 Years of U.S. MSHA Government Data*\n",
                "\n",
                "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anggerwicaksana/minerisk-ai/blob/main/notebooks/MineRisk_AI_Colab_Master.ipynb)\n",
                "![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)\n",
                "![LightGBM](https://img.shields.io/badge/Model-Calibrated_LightGBM-green.svg)\n",
                "![SHAP](https://img.shields.io/badge/XAI-SHAP_TreeExplainer-red.svg)\n",
                "![Zero Leakage](https://img.shields.io/badge/Validation-Out--of--Time_Temporal_Split-purple.svg)\n",
                "\n",
                "---\n",
                "\n",
                "## 1. Executive Summary & Problem Formulation\n",
                "Conventional occupational safety & health (OSH) analytics is overwhelmingly **reactive**—conducting post-mortem audits after worker injuries occur. Furthermore, many generic AI portfolio projects commit fatal **lookahead bias / data leakage** (e.g., predicting injury severity from narratives written *after* the incident).\n",
                "\n",
                "**MineRisk-AI (SafeCast)** reformulates the problem into genuine **prospective risk forecasting**:\n",
                "> *\"Given a mine's operational hours worked (exposure), inspection intensity, regulatory violation history, and safety record up to the end of Quarter $t$, what is the calibrated probability of a qualifying worker injury occurring in Quarter $t+1$?\"*\n",
                "\n",
                "### Key Architectural Features:\n",
                "1. **Authoritative Government Data:** Combines 5 official relational tables from the **U.S. Mine Safety and Health Administration (MSHA)** (2000–2025).\n",
                "2. **Zero-Leakage Star-Schema Panel:** Polars-powered time-indexed ETL at `(MINE_ID, CAL_YR, CAL_QTR)` grain with strict elimination of mutable `CURRENT_*` fields.\n",
                "3. **Strict Out-of-Time Temporal Split:** Train ($\\le 2021$), Validation ($2022-2023$), and Unseen Test ($2024-2025$).\n",
                "4. **Calibrated Machine Learning:** LightGBM with Platt Scaling / Isotonic Regression to output reliable probabilistic risk scores.\n",
                "5. **Explainable AI (SHAP):** Decomposes risk drivers globally and at the individual mine level.\n",
                "6. **Interactive Demo Serving:** Self-contained 3-Tab Gradio Web Application with a live shareable public URL."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Environment Setup & Dependency Installation\n",
                "Detects Google Colab environment and installs dependencies silently."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os, sys\n",
                "IN_COLAB = 'google.colab' in str(get_ipython())\n",
                "if IN_COLAB:\n",
                "    print('Menyiapkan lingkungan Google Colab...')\n",
                "    if not os.path.exists('minerisk-ai'):\n",
                "        !git clone https://github.com/anggerwicaksana/minerisk-ai.git\n",
                "        %cd minerisk-ai\n",
                "    elif os.path.basename(os.getcwd()) != 'minerisk-ai':\n",
                "        %cd minerisk-ai\n",
                "    !pip install polars pyarrow lightgbm shap gradio plotly scikit-learn -q\n",
                "    if '.' not in sys.path:\n",
                "        sys.path.append('.')\n",
                "    print('Lingkungan dan repositori siap digunakan.')\n",
                "else:\n",
                "    print('Berjalan di lingkungan lokal.')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Data Sourcing & Relational Ingestion Engine\n",
                "Ingests the 5 official MSHA relational tables (`Mines`, `QuarterlyEmploymentProduction`, `Inspections`, `Violations`, and `Accidents`)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import polars as pl\n",
                "import numpy as np\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "from pathlib import Path\n",
                "\n",
                "# Import project modules\n",
                "from src.ingestion import load_msha_table, generate_synthetic_msha_data\n",
                "from src.panel_builder import build_quarterly_mine_panel\n",
                "from src.feature_engineering import engineer_features, split_temporal_partitions\n",
                "from src.model import prepare_tabular_data, train_baseline_logistic, train_lightgbm_model, run_ablation_study\n",
                "from src.explainability import MineRiskExplainer, build_plotly_waterfall, build_geospatial_risk_map\n",
                "\n",
                "# Ingest or synthesize benchmark tables\n",
                "raw_panel = build_quarterly_mine_panel()\n",
                "print(f'Star-schema quarterly panel constructed: {raw_panel.height:,} mine-quarters, {raw_panel.width} attributes.')\n",
                "raw_panel.head(5)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Leakage-Proof Feature Engineering & Out-of-Time Temporal Split\n",
                "Computes rolling 4-quarter statistics, exposure offsets (`log_hours`), violation severity ratios, and strict out-of-time train/val/test splits."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Compute temporal lag features and forward target (t+1)\n",
                "feature_panel = engineer_features(raw_panel)\n",
                "splits = split_temporal_partitions(feature_panel)\n",
                "\n",
                "print('--- PARTITION OVERVIEW ---')\n",
                "print(f\"Train Set:      {splits['train'].height:,} rows (<= 2021) | Positive Injury Rate: {splits['train']['target_has_injury_next_qtr'].mean():.1%}\")\n",
                "print(f\"Validation Set: {splits['val'].height:,} rows (2022-2023) | Positive Injury Rate: {splits['val']['target_has_injury_next_qtr'].mean():.1%}\")\n",
                "print(f\"Test Set:       {splits['test'].height:,} rows (2024-2025) | Positive Injury Rate: {splits['test']['target_has_injury_next_qtr'].mean():.1%}\")\n",
                "print(f\"Live Serving:   {splits['live'].height:,} active mines for current quarter\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Model Training, Calibration & Out-of-Time Benchmarking\n",
                "Compares Baseline Logistic Regression against the Flagship Calibrated LightGBM model."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "X_train, y_train, X_val, y_val, X_test, y_test = prepare_tabular_data(\n",
                "    splits['train'], splits['val'], splits['test']\n",
                ")\n",
                "\n",
                "# Baseline Logistic Regression\n",
                "lr_pipe, lr_metrics = train_baseline_logistic(X_train, y_train, X_test, y_test)\n",
                "\n",
                "# Flagship LightGBM with Sigmoid Calibration\n",
                "lgbm_raw, calib_model, lgbm_metrics, decile_df = train_lightgbm_model(\n",
                "    X_train, y_train, X_val, y_val, X_test, y_test\n",
                ")\n",
                "\n",
                "print('\\n' + '='*65)\n",
                "print('OUT-OF-TIME TEST BENCHMARK COMPARISON')\n",
                "print('='*65)\n",
                "benchmark_table = pd.DataFrame([\n",
                "    {'Model': 'Baseline L2-Logistic Regression', 'PR-AUC': lr_metrics['pr_auc'], 'ROC-AUC': lr_metrics['roc_auc'], 'Brier Score': lr_metrics['brier_score'], 'Top-10% Lift': f\"{lr_metrics['lift_top10']:.2f}x\"},\n",
                "    {'Model': 'Flagship Calibrated LightGBM', 'PR-AUC': lgbm_metrics['pr_auc'], 'ROC-AUC': lgbm_metrics['roc_auc'], 'Brier Score': lgbm_metrics['calibrated_brier'], 'Top-10% Lift': f\"{lgbm_metrics['lift_top10']:.2f}x\"},\n",
                "])\n",
                "display(benchmark_table)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Decile Risk Lift & Operational Prioritization Analysis\n",
                "Validates how effectively the model concentrates future workplace injuries into the highest-risk deciles."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print('--- 10-DECILE RISK LIFT TABLE ---')\n",
                "display(decile_df[['decile', 'total_mines', 'mean_predicted_risk', 'actual_injury_rate', 'lift', 'cumulative_recall']])\n",
                "\n",
                "# Visualize Decile Lift Bar Chart\n",
                "fig, ax = plt.subplots(figsize=(9, 4.5))\n",
                "ax.bar(decile_df['decile'], decile_df['lift'], color='#3B82F6', edgecolor='#1D4ED8')\n",
                "ax.axhline(1.0, color='#EF4444', linestyle='--', label='Baseline Population Risk (1.0x)')\n",
                "ax.set_title('MineRisk-AI: Lift Across Risk Deciles (Out-of-Time Test Set)', fontsize=13, fontweight='bold')\n",
                "ax.set_xlabel('Predicted Risk Decile (Decile 1 = Highest Scored Mines)', fontsize=11)\n",
                "ax.set_ylabel('Lift Multiplier vs Baseline', fontsize=11)\n",
                "ax.set_xticks(range(1, 11))\n",
                "ax.legend()\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Explainable AI (SHAP TreeExplainer) & Geospatial Intelligence\n",
                "Decomposes risk drivers globally and shows individual mine waterfall contributions."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "explainer = MineRiskExplainer(calib_model, list(X_train.columns))\n",
                "\n",
                "# Pick highest-risk mine in test set\n",
                "test_probs = calib_model.predict_proba(X_test)[:, 1]\n",
                "top_mine_idx = np.argmax(test_probs)\n",
                "sample_mine_row = X_test.iloc[top_mine_idx]\n",
                "sample_prob = test_probs[top_mine_idx]\n",
                "\n",
                "explanation = explainer.explain_mine(sample_mine_row)\n",
                "waterfall_fig = build_plotly_waterfall(explanation, sample_prob, mine_name='High Risk Test Mine')\n",
                "waterfall_fig.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 8. Launch Interactive Web Demo (Gradio 3-Tab UI)\n",
                "Launches the full interactive Gradio application. In Google Colab, `share=True` automatically provisions a public `gradio.live` link active for 72 hours."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from app import build_gradio_app\n",
                "demo_app = build_gradio_app()\n",
                "demo_app.launch(share=True, debug=False)"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

out_file = Path("d:/PROJEK - BUSINESS/Predictive AI/notebooks/MineRisk_AI_Colab_Master.ipynb")
out_file.parent.mkdir(parents=True, exist_ok=True)
with open(out_file, "w") as f:
    json.dump(notebook_data, f, indent=2)

print(f"Generated Colab Master Notebook at: {out_file}")
