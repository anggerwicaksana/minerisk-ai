"""Comprehensive Evaluation & Benchmarking Engine for MineRisk-AI.
Computes PR-AUC, ROC-AUC, Brier Score, Lift@Top-10%, Recall@Top-10%,
and Risk Decile Lift tables for executive decision support.
"""

import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    brier_score_loss,
    precision_score,
    recall_score,
    f1_score,
)

logger = logging.getLogger(__name__)


def compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """Computes all primary portfolio and business metrics on test predictions."""
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)
    y_pred = (y_prob >= threshold).astype(int)

    base_rate = float(np.mean(y_true))
    pr_auc = float(average_precision_score(y_true, y_prob))
    roc_auc = float(roc_auc_score(y_true, y_prob))
    brier = float(brier_score_loss(y_true, y_prob))

    # Top-K% Metrics (Top 10% and Top 20% highest predicted risk mines)
    n = len(y_true)
    k10 = max(1, int(n * 0.10))
    k20 = max(1, int(n * 0.20))

    sorted_indices = np.argsort(y_prob)[::-1]
    top10_true = y_true[sorted_indices[:k10]]
    top20_true = y_true[sorted_indices[:k20]]

    precision_top10 = float(np.mean(top10_true))
    recall_top10 = float(np.sum(top10_true) / max(1, np.sum(y_true)))
    lift_top10 = float(precision_top10 / max(1e-6, base_rate))

    precision_top20 = float(np.mean(top20_true))
    recall_top20 = float(np.sum(top20_true) / max(1, np.sum(y_true)))
    lift_top20 = float(precision_top20 / max(1e-6, base_rate))

    return {
        "base_rate": base_rate,
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "brier_score": brier,
        "precision_top10": precision_top10,
        "recall_top10": recall_top10,
        "lift_top10": lift_top10,
        "precision_top20": precision_top20,
        "recall_top20": recall_top20,
        "lift_top20": lift_top20,
        "f1_at_threshold": float(f1_score(y_true, y_pred, zero_division=0)),
        "precision_at_threshold": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall_at_threshold": float(recall_score(y_true, y_pred, zero_division=0)),
    }


def compute_decile_table(
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> pd.DataFrame:
    """Computes a 10-tier Decile Risk Lift table."""
    df = pd.DataFrame({"y_true": y_true, "y_prob": y_prob})
    df["decile"] = pd.qcut(df["y_prob"].rank(method="first"), q=10, labels=False)
    # Decile 10 = highest risk
    df["decile"] = 10 - df["decile"]

    base_rate = df["y_true"].mean()
    decile_summary = (
        df.groupby("decile")
        .agg(
            total_mines=("y_true", "count"),
            mean_predicted_risk=("y_prob", "mean"),
            actual_injury_mines=("y_true", "sum"),
            actual_injury_rate=("y_true", "mean"),
        )
        .reset_index()
    )

    decile_summary["lift"] = decile_summary["actual_injury_rate"] / max(1e-6, base_rate)
    decile_summary["cumulative_actual_injuries"] = decile_summary["actual_injury_mines"].cumsum()
    decile_summary["cumulative_recall"] = (
        decile_summary["cumulative_actual_injuries"] / max(1, df["y_true"].sum())
    )

    return decile_summary
