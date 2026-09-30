"""Model Training, Benchmarking & Serialization Engine for MineRisk-AI.
Implements Naive Baseline, Regularized Logistic Regression, LightGBM,
Feature Ablation Study, and saves artifacts for deployment.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, List
import joblib
import numpy as np
import pandas as pd
import polars as pl
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from src.config import (
    PROCESSED_DATA_DIR,
    ARTIFACTS_DIR,
    ALL_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COL,
    RANDOM_STATE,
)
from src.calibration import CalibratedModelWrapper
from src.evaluation import compute_metrics, compute_decile_table

logger = logging.getLogger(__name__)


def prepare_tabular_data(
    train_df: pl.DataFrame,
    val_df: pl.DataFrame,
    test_df: pl.DataFrame,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Converts Polars DataFrames to Pandas and encodes categorical variables."""
    # Convert to Pandas
    train_pd = train_df.to_pandas()
    val_pd = val_df.to_pandas()
    test_pd = test_df.to_pandas()

    for cat_col in CATEGORICAL_FEATURES:
        train_pd[cat_col] = train_pd[cat_col].astype("category")
        val_pd[cat_col] = pd.Categorical(val_pd[cat_col], categories=train_pd[cat_col].cat.categories)
        test_pd[cat_col] = pd.Categorical(test_pd[cat_col], categories=train_pd[cat_col].cat.categories)

    X_train = train_pd[ALL_FEATURES]
    y_train = train_pd[TARGET_COL].astype(int)

    X_val = val_pd[ALL_FEATURES]
    y_val = val_pd[TARGET_COL].astype(int)

    X_test = test_pd[ALL_FEATURES]
    y_test = test_pd[TARGET_COL].astype(int)

    return X_train, y_train, X_val, y_val, X_test, y_test


def train_baseline_logistic(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> Tuple[Pipeline, Dict[str, Any]]:
    """Trains an L2-regularized Logistic Regression model on numerical features."""
    logger.info("Training Baseline 2: L2-Regularized Logistic Regression...")
    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(C=1.0, max_iter=1000, random_state=RANDOM_STATE)),
    ])
    
    # Train only on numerical features for clean linear interpretation
    pipe.fit(X_train[NUMERICAL_FEATURES], y_train)
    probs = pipe.predict_proba(X_test[NUMERICAL_FEATURES])[:, 1]
    metrics = compute_metrics(y_test, probs)
    return pipe, metrics


def train_lightgbm_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> Tuple[LGBMClassifier, CalibratedModelWrapper, Dict[str, Any], pd.DataFrame]:
    """Trains the flagship LightGBM model, applies calibration, and computes benchmark metrics."""
    logger.info("Training Flagship Model: LightGBM Classifier...")
    
    # Calculate scale_pos_weight
    neg_count = np.sum(y_train == 0)
    pos_count = np.sum(y_train == 1)
    scale_weight = float(neg_count / max(1, pos_count))

    lgbm = LGBMClassifier(
        n_estimators=400,
        learning_rate=0.03,
        num_leaves=31,
        max_depth=6,
        min_child_samples=30,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=min(scale_weight, 3.5),
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=-1,
    )

    lgbm.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="binary_logloss",
    )

    # Post-hoc Probability Calibration on Validation Set
    calibrated_wrapper = CalibratedModelWrapper(base_estimator=lgbm, method="sigmoid")
    calibrated_wrapper.fit_calibration(X_val, y_val)

    # Evaluate on Unseen Out-of-Time Test Set
    raw_test_probs = lgbm.predict_proba(X_test)[:, 1]
    calib_test_probs = calibrated_wrapper.predict_proba(X_test)[:, 1]

    raw_metrics = compute_metrics(y_test, raw_test_probs)
    calib_metrics = compute_metrics(y_test, calib_test_probs)
    calib_metrics.update(calibrated_wrapper.evaluate_calibration(X_test, y_test))

    decile_df = compute_decile_table(y_test, calib_test_probs)

    logger.info("LightGBM Out-of-Time Test Results:")
    logger.info(f" - PR-AUC:      {calib_metrics['pr_auc']:.4f}")
    logger.info(f" - ROC-AUC:     {calib_metrics['roc_auc']:.4f}")
    logger.info(f" - Brier Score: {calib_metrics['brier_score']:.4f}")
    logger.info(f" - Lift@Top-10%: {calib_metrics['lift_top10']:.2f}x")
    logger.info(f" - Recall@Top-10%: {calib_metrics['recall_top10']*100:.1f}%")

    return lgbm, calibrated_wrapper, calib_metrics, decile_df


def run_ablation_study(
    train_pd: pd.DataFrame,
    val_pd: pd.DataFrame,
    test_pd: pd.DataFrame,
) -> Dict[str, Dict[str, float]]:
    """Conducts a 5-layer Feature Family Ablation Study."""
    logger.info("Initiating 5-Layer Feature Family Ablation Study...")
    
    ablation_suites = {
        "Model A (Exposure Only)": [
            "hours_worked_q0", "avg_employees_q0", "log_hours_q0", "coal_metal_ind", "mine_type", "state"
        ],
        "Model B (A + Safety History)": [
            "hours_worked_q0", "avg_employees_q0", "log_hours_q0", "coal_metal_ind", "mine_type", "state",
            "injury_count_q0", "injury_count_lag1", "injury_count_lag2", "injury_rolling_4q_sum", "days_lost_rolling_4q"
        ],
        "Model C (B + Inspections)": [
            "hours_worked_q0", "avg_employees_q0", "log_hours_q0", "coal_metal_ind", "mine_type", "state",
            "injury_count_q0", "injury_count_lag1", "injury_count_lag2", "injury_rolling_4q_sum", "days_lost_rolling_4q",
            "insp_count_q0", "insp_hours_q0", "insp_hours_rolling_4q"
        ],
        "Model D (C + Violations)": [
            "hours_worked_q0", "avg_employees_q0", "log_hours_q0", "coal_metal_ind", "mine_type", "state",
            "injury_count_q0", "injury_count_lag1", "injury_count_lag2", "injury_rolling_4q_sum", "days_lost_rolling_4q",
            "insp_count_q0", "insp_hours_q0", "insp_hours_rolling_4q",
            "viol_count_q0", "viol_rolling_4q_sum", "viol_ss_count_q0", "viol_ss_ratio_q0", "viol_high_negligence_q0"
        ],
        "Model E (Full: D + Trends & Interactivity)": ALL_FEATURES,
    }

    results = {}
    train_pd = train_pd.copy()
    test_pd = test_pd.copy()
    for cat_col in CATEGORICAL_FEATURES:
        if cat_col in train_pd.columns:
            train_pd[cat_col] = train_pd[cat_col].astype("category")
        if cat_col in test_pd.columns:
            test_pd[cat_col] = pd.Categorical(test_pd[cat_col], categories=train_pd[cat_col].cat.categories)

    y_train = train_pd[TARGET_COL].astype(int)
    y_test = test_pd[TARGET_COL].astype(int)

    for name, feature_subset in ablation_suites.items():
        clf = LGBMClassifier(
            n_estimators=250,
            learning_rate=0.04,
            num_leaves=25,
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbose=-1,
        )
        clf.fit(train_pd[feature_subset], y_train)
        probs = clf.predict_proba(test_pd[feature_subset])[:, 1]
        m = compute_metrics(y_test, probs)
        results[name] = {
            "pr_auc": m["pr_auc"],
            "roc_auc": m["roc_auc"],
            "lift_top10": m["lift_top10"],
            "brier_score": m["brier_score"],
        }
        logger.info(f" - {name}: PR-AUC = {m['pr_auc']:.4f}, Lift@Top-10% = {m['lift_top10']:.2f}x")

    return results


def export_production_artifacts(
    calibrated_model: CalibratedModelWrapper,
    metrics: Dict[str, Any],
    ablation_results: Dict[str, Any],
    live_df: pl.DataFrame,
) -> None:
    """Serializes the lightweight model and metadata for web app deployment (< 30 MB)."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Serializing deployment artifacts to {ARTIFACTS_DIR}...")

    # 1. Calibrated Model
    model_path = ARTIFACTS_DIR / "model_calibrated.joblib"
    joblib.dump(calibrated_model, model_path, compress=3)
    logger.info(f"Saved calibrated model to {model_path} ({model_path.stat().st_size / (1024*1024):.2f} MB)")

    # 2. Feature Metadata & Statistics
    meta = {
        "all_features": ALL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "feature_count": len(ALL_FEATURES),
    }
    with open(ARTIFACTS_DIR / "feature_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    # 3. Benchmark Metrics
    benchmark_payload = {
        "test_metrics": metrics,
        "ablation_study": ablation_results,
    }
    with open(ARTIFACTS_DIR / "benchmark_metrics.json", "w") as f:
        json.dump(benchmark_payload, f, indent=2)

    # 4. Live Sample Panel for Web App Demonstration
    sample_path = ARTIFACTS_DIR / "demo_sample_panel.parquet"
    live_df.write_parquet(sample_path, compression="snappy")
    logger.info(f"Saved demo sample panel ({live_df.height} mines) to {sample_path}")
