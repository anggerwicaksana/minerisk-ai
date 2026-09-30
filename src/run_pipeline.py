"""End-to-End Orchestrator Pipeline for MineRisk-AI.
Executes ingestion, star-schema ETL, leakage-safe feature engineering,
model training, calibration, feature ablation, and artifact export.
"""

import logging
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ingestion import load_msha_table, generate_synthetic_msha_data
from src.panel_builder import build_quarterly_mine_panel
from src.feature_engineering import engineer_features, split_temporal_partitions
from src.model import (
    prepare_tabular_data,
    train_baseline_logistic,
    train_lightgbm_model,
    run_ablation_study,
    export_production_artifacts,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run_full_pipeline(force_synth: bool = False):
    """Executes the complete MineRisk-AI predictive engine."""
    logger.info("=" * 70)
    logger.info("STARTING MINERISK-AI (SAFECAST) END-TO-END PREDICTIVE PIPELINE")
    logger.info("=" * 70)

    # 1. Ingestion / Data Sourcing
    logger.info("\n--- STEP 1: DATA INGESTION & SYNTHESIS ---")
    mines_lf = load_msha_table("mines")

    # 2. Relational Panel ETL
    logger.info("\n--- STEP 2: STAR-SCHEMA PANEL CONSTRUCTION ---")
    raw_panel = build_quarterly_mine_panel()

    # 3. Feature Engineering & Out-of-Time Splitting
    logger.info("\n--- STEP 3: LEAKAGE-PROOF FEATURE ENGINEERING ---")
    features_df = engineer_features(raw_panel)
    splits = split_temporal_partitions(features_df)

    # 4. Data Preparation for Modeling
    logger.info("\n--- STEP 4: MODEL DATA PREPARATION ---")
    X_train, y_train, X_val, y_val, X_test, y_test = prepare_tabular_data(
        splits["train"],
        splits["val"],
        splits["test"],
    )

    # 5. Baseline Logistic Regression
    logger.info("\n--- STEP 5: BASELINE BENCHMARKING ---")
    lr_pipe, lr_metrics = train_baseline_logistic(X_train, y_train, X_test, y_test)
    logger.info(f"Baseline Logistic Regression PR-AUC: {lr_metrics['pr_auc']:.4f}, ROC-AUC: {lr_metrics['roc_auc']:.4f}")

    # 6. Flagship LightGBM Model & Probability Calibration
    logger.info("\n--- STEP 6: FLAGSHIP LIGHTGBM TRAINING & CALIBRATION ---")
    lgbm_model, calibrated_wrapper, lgbm_metrics, decile_df = train_lightgbm_model(
        X_train, y_train, X_val, y_val, X_test, y_test
    )

    # 7. Feature Ablation Study
    logger.info("\n--- STEP 7: FEATURE FAMILY ABLATION STUDY ---")
    train_pd = splits["train"].to_pandas()
    val_pd = splits["val"].to_pandas()
    test_pd = splits["test"].to_pandas()
    ablation_results = run_ablation_study(train_pd, val_pd, test_pd)

    # 8. Export Production Artifacts
    logger.info("\n--- STEP 8: PRODUCTION ARTIFACT SERIALIZATION ---")
    export_production_artifacts(
        calibrated_model=calibrated_wrapper,
        metrics=lgbm_metrics,
        ablation_results=ablation_results,
        live_df=splits["live"],
    )

    logger.info("=" * 70)
    logger.info("MINERISK-AI PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info(f"Key Test Benchmarks:")
    logger.info(f" - Out-of-Time PR-AUC:       {lgbm_metrics['pr_auc']:.4f} (vs Logistic {lr_metrics['pr_auc']:.4f})")
    logger.info(f" - Out-of-Time ROC-AUC:      {lgbm_metrics['roc_auc']:.4f} (vs Logistic {lr_metrics['roc_auc']:.4f})")
    logger.info(f" - Top-10% Decile Lift:      {lgbm_metrics['lift_top10']:.2f}x Baseline")
    logger.info(f" - Calibrated Brier Score:   {lgbm_metrics['calibrated_brier']:.4f}")
    logger.info(f" - Top-10% Incident Recall:  {lgbm_metrics['recall_top10']*100:.1f}%")
    logger.info("=" * 70)

    print("\n--- TOP DECILE RISK LIFT SUMMARY ---")
    print(decile_df[["decile", "total_mines", "mean_predicted_risk", "actual_injury_rate", "lift", "cumulative_recall"]].to_string(index=False))

    return {
        "lgbm_metrics": lgbm_metrics,
        "lr_metrics": lr_metrics,
        "ablation_results": ablation_results,
        "decile_df": decile_df,
    }


if __name__ == "__main__":
    run_full_pipeline()
