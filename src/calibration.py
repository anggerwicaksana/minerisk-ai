"""Probability Calibration Engine for MineRisk-AI.
Implements Platt Scaling (Sigmoid) and Isotonic Regression post-hoc calibration
with Expected Calibration Error (ECE) and Brier Score validation.
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import logging
from typing import Dict, Tuple, Any
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss

logger = logging.getLogger(__name__)


def compute_expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> Tuple[float, np.ndarray, np.ndarray]:
    """Computes Expected Calibration Error (ECE) and reliability curve points."""
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy="uniform")
    
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(y_prob, bin_edges) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)
    
    ece = 0.0
    total_samples = len(y_true)
    for b in range(n_bins):
        mask = (bin_indices == b)
        bin_size = np.sum(mask)
        if bin_size > 0:
            bin_acc = np.mean(y_true[mask])
            bin_conf = np.mean(y_prob[mask])
            ece += (bin_size / total_samples) * np.abs(bin_acc - bin_conf)
            
    return float(ece), prob_true, prob_pred


class CalibratedModelWrapper:
    """Wraps an estimator with a validation-fitted probability calibrator (Platt Scaling or Isotonic)."""

    def __init__(self, base_estimator: Any, method: str = "sigmoid"):
        self.base_estimator = base_estimator
        self.method = method
        if method == "isotonic":
            self.calibrator = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")
        else:
            self.calibrator = LogisticRegression(C=1.0, solver="lbfgs")
        self.is_calibrated = False

    def fit_calibration(self, X_val: Any, y_val: np.ndarray) -> "CalibratedModelWrapper":
        """Fits calibration parameters strictly on the validation set."""
        logger.info(f"Fitting {self.method.upper()} probability calibrator on validation set ({len(y_val)} samples)...")
        val_probs = self.base_estimator.predict_proba(X_val)[:, 1]
        y_val_arr = np.asarray(y_val).astype(int)
        
        if self.method == "isotonic":
            self.calibrator.fit(val_probs, y_val_arr)
        else:
            self.calibrator.fit(val_probs.reshape(-1, 1), y_val_arr)
            
        self.is_calibrated = True
        return self

    def predict_proba(self, X: Any) -> np.ndarray:
        """Returns calibrated probability distributions [P(0), P(1)]."""
        raw_probs = self.base_estimator.predict_proba(X)[:, 1]
        if self.is_calibrated:
            if self.method == "isotonic":
                calib_p1 = self.calibrator.predict(raw_probs)
            else:
                calib_p1 = self.calibrator.predict_proba(raw_probs.reshape(-1, 1))[:, 1]
            calib_p1 = np.clip(calib_p1, 0.0, 1.0)
            return np.column_stack([1.0 - calib_p1, calib_p1])
        return self.base_estimator.predict_proba(X)

    def predict(self, X: Any, threshold: float = 0.5) -> np.ndarray:
        """Predicts binary class based on calibrated probability threshold."""
        probs = self.predict_proba(X)[:, 1]
        return (probs >= threshold).astype(int)

    def evaluate_calibration(
        self,
        X_test: Any,
        y_test: np.ndarray,
    ) -> Dict[str, float]:
        """Evaluates calibration quality using Brier Score and ECE."""
        uncalib_probs = self.base_estimator.predict_proba(X_test)[:, 1]
        calib_probs = self.predict_proba(X_test)[:, 1]

        uncalib_brier = brier_score_loss(y_test, uncalib_probs)
        calib_brier = brier_score_loss(y_test, calib_probs)
        
        uncalib_ece, _, _ = compute_expected_calibration_error(y_test, uncalib_probs)
        calib_ece, _, _ = compute_expected_calibration_error(y_test, calib_probs)

        logger.info("Calibration Evaluation Results:")
        logger.info(f" - Brier Score: Raw = {uncalib_brier:.4f} -> Calibrated = {calib_brier:.4f}")
        logger.info(f" - ECE:         Raw = {uncalib_ece:.4f} -> Calibrated = {calib_ece:.4f}")

        return {
            "uncalibrated_brier": float(uncalib_brier),
            "calibrated_brier": float(calib_brier),
            "uncalibrated_ece": float(uncalib_ece),
            "calibrated_ece": float(calib_ece),
        }
