"""Configuration and constants for MineRisk-AI (SafeCast).
Centralizes data paths, MSHA endpoints, schema definitions, and model parameters.
"""

from pathlib import Path
from typing import List, Dict, Any

# Root Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Ensure runtime directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, ARTIFACTS_DIR, NOTEBOOKS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Official MSHA Open Government Data Endpoints
MSHA_BASE_URL = "https://arlweb.msha.gov/OpenGovernmentData/DataSets"
MSHA_FILES = {
    "mines": "Mines.zip",
    "employment": "QuarterlyEmploymentProduction.zip",
    "accidents": "Accidents.zip",
    "inspections": "Inspections.zip",
    "violations": "Violations.zip",
}

# Strict Temporal Split Cut-offs
SPLIT_CONFIG = {
    "train_end": (2021, 4),    # Train: 2012 Q1 - 2021 Q4
    "val_start": (2022, 1),    # Val:   2022 Q1 - 2023 Q4
    "val_end": (2023, 4),
    "test_start": (2024, 1),   # Test:  2024 Q1 - 2025 Q4
    "test_end": (2025, 4),
}

# Target Definition
TARGET_COL = "target_has_injury_next_qtr"
TARGET_COUNT_COL = "target_injury_count_next_qtr"

# Feature Definitions
NUMERICAL_FEATURES: List[str] = [
    "hours_worked_q0",
    "avg_employees_q0",
    "log_hours_q0",
    "hours_worked_lag1",
    "hours_delta_1q",
    "hours_pct_change_1q",
    "hours_rolling_4q_mean",
    "injury_count_q0",
    "injury_count_lag1",
    "injury_count_lag2",
    "injury_count_lag3",
    "injury_rolling_4q_sum",
    "days_lost_q0",
    "days_lost_rolling_4q",
    "injury_rate_per_200k_q0",
    "injury_rate_rolling_4q",
    "has_prior_injury_q0",
    "insp_count_q0",
    "insp_hours_q0",
    "insp_hours_rolling_4q",
    "viol_count_q0",
    "viol_count_lag1",
    "viol_rolling_4q_sum",
    "viol_ss_count_q0",
    "viol_ss_ratio_q0",
    "viol_high_negligence_q0",
    "viol_per_insp_hour_q0",
    "consecutive_zero_injury_qtrs",
]

CATEGORICAL_FEATURES: List[str] = [
    "coal_metal_ind",
    "mine_type",
    "state",
    "calendar_quarter",
]

ALL_FEATURES: List[str] = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

# Risk Tiers Configuration
RISK_TIERS: Dict[str, Dict[str, Any]] = {
    "Low": {"min": 0.00, "max": 0.20, "color": "#10B981", "badge": "LOW RISK"},
    "Moderate": {"min": 0.20, "max": 0.45, "color": "#F59E0B", "badge": "MODERATE RISK"},
    "Elevated": {"min": 0.45, "max": 0.70, "color": "#F97316", "badge": "ELEVATED RISK"},
    "Critical": {"min": 0.70, "max": 1.00, "color": "#EF4444", "badge": "CRITICAL RISK"},
}

# Global Random State
RANDOM_STATE = 42
