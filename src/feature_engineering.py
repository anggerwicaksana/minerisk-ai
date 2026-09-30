"""Feature Engineering & Temporal Split Engine for MineRisk-AI.
Constructs rolling windows, lag features, exposure offsets, trend indicators,
and strict out-of-time temporal partitions with zero lookahead bias.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
import polars as pl
import numpy as np

from src.config import (
    PROCESSED_DATA_DIR,
    SPLIT_CONFIG,
    TARGET_COL,
    TARGET_COUNT_COL,
    ALL_FEATURES,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
)

logger = logging.getLogger(__name__)


def engineer_features(raw_panel: Optional[pl.DataFrame] = None) -> pl.DataFrame:
    """Computes time-series lags, exposure metrics, ratios, and forward target labels."""
    if raw_panel is None:
        panel_path = PROCESSED_DATA_DIR / "msha_raw_quarterly_panel.parquet"
        if not panel_path.exists():
            raise FileNotFoundError(f"Raw panel not found at {panel_path}. Run panel_builder.py first.")
        logger.info(f"Loading raw panel from {panel_path}...")
        raw_panel = pl.read_parquet(panel_path)

    logger.info("Computing leakage-proof temporal lag features and exposure offsets...")

    # Ensure strictly sorted by MINE_ID, CAL_YR, CAL_QTR
    df = raw_panel.sort(["MINE_ID", "CAL_YR", "CAL_QTR"])

    # Feature expressions
    df = df.with_columns([
        # Exposure offsets
        (pl.col("hours_worked_q0") + 1.0).log().alias("log_hours_q0"),
        pl.col("hours_worked_q0").shift(1).over("MINE_ID").fill_null(pl.col("hours_worked_q0")).alias("hours_worked_lag1"),
        pl.col("CAL_QTR").alias("calendar_quarter"),
    ])

    df = df.with_columns([
        # Hours trends
        (pl.col("hours_worked_q0") - pl.col("hours_worked_lag1")).alias("hours_delta_1q"),
        ((pl.col("hours_worked_q0") - pl.col("hours_worked_lag1")) / (pl.col("hours_worked_lag1") + 1.0)).alias("hours_pct_change_1q"),
        pl.col("hours_worked_q0").rolling_mean(window_size=4, min_periods=1).over("MINE_ID").alias("hours_rolling_4q_mean"),
        
        # Injury history lags
        pl.col("injury_count_q0").shift(1).over("MINE_ID").fill_null(0).alias("injury_count_lag1"),
        pl.col("injury_count_q0").shift(2).over("MINE_ID").fill_null(0).alias("injury_count_lag2"),
        pl.col("injury_count_q0").shift(3).over("MINE_ID").fill_null(0).alias("injury_count_lag3"),
        pl.col("injury_count_q0").rolling_sum(window_size=4, min_periods=1).over("MINE_ID").alias("injury_rolling_4q_sum"),
        
        # Days lost history
        pl.col("days_lost_q0").rolling_sum(window_size=4, min_periods=1).over("MINE_ID").alias("days_lost_rolling_4q"),
        
        # Injury rates per 200k hours
        ((pl.col("injury_count_q0") * 200000.0) / pl.col("hours_worked_q0")).alias("injury_rate_per_200k_q0"),
        
        # Binary indicator of prior injury
        (pl.col("injury_count_q0") >= 1).cast(pl.Int64).alias("has_prior_injury_q0"),
        
        # Inspection history
        pl.col("insp_hours_q0").rolling_sum(window_size=4, min_periods=1).over("MINE_ID").alias("insp_hours_rolling_4q"),
        
        # Violation history lags & ratios
        pl.col("viol_count_q0").shift(1).over("MINE_ID").fill_null(0).alias("viol_count_lag1"),
        pl.col("viol_count_q0").rolling_sum(window_size=4, min_periods=1).over("MINE_ID").alias("viol_rolling_4q_sum"),
        (pl.col("viol_ss_count_q0") / (pl.col("viol_count_q0") + 1.0)).alias("viol_ss_ratio_q0"),
        (pl.col("viol_count_q0") / (pl.col("insp_hours_q0") + 0.1)).alias("viol_per_insp_hour_q0"),
    ])

    df = df.with_columns([
        ((pl.col("injury_rolling_4q_sum") * 200000.0) / (pl.col("hours_rolling_4q_mean") * 4.0 + 1.0)).alias("injury_rate_rolling_4q"),
        # Consecutive zero-injury quarters proxy
        (pl.col("injury_rolling_4q_sum") == 0).cast(pl.Int64).alias("consecutive_zero_injury_qtrs"),
    ])

    # Construct Forward-Looking Target (Quarter t+1)
    df = df.with_columns([
        pl.col("injury_count_q0").shift(-1).over("MINE_ID").alias(TARGET_COUNT_COL),
        (pl.col("injury_count_q0").shift(-1).over("MINE_ID") >= 1).cast(pl.Int64).alias(TARGET_COL),
    ])

    logger.info(f"Engineered feature panel: {df.height} rows, {df.width} columns.")
    return df


def split_temporal_partitions(df: pl.DataFrame) -> Dict[str, pl.DataFrame]:
    """Partitions the panel into Train, Validation, Test, and Live Inference sets
    strictly by out-of-time calendar years (Zero Lookahead Bias).
    """
    logger.info("Executing strict Out-of-Time temporal partition...")

    train_end_yr = SPLIT_CONFIG["train_end"][0]
    val_start_yr = SPLIT_CONFIG["val_start"][0]
    val_end_yr = SPLIT_CONFIG["val_end"][0]
    test_start_yr = SPLIT_CONFIG["test_start"][0]
    test_end_yr = SPLIT_CONFIG["test_end"][0]

    # Filter labeled rows (where t+1 target is observed)
    labeled_df = df.filter(pl.col(TARGET_COL).is_not_null())

    # Live unlabelled rows for demo serving (latest quarter where t+1 is the future)
    max_yr = df["CAL_YR"].max()
    max_qtr = df.filter(pl.col("CAL_YR") == max_yr)["CAL_QTR"].max()
    live_inference_df = df.filter((pl.col("CAL_YR") == max_yr) & (pl.col("CAL_QTR") == max_qtr))

    train_df = labeled_df.filter(pl.col("CAL_YR") <= train_end_yr)
    val_df = labeled_df.filter((pl.col("CAL_YR") >= val_start_yr) & (pl.col("CAL_YR") <= val_end_yr))
    test_df = labeled_df.filter((pl.col("CAL_YR") >= test_start_yr) & (pl.col("CAL_YR") <= test_end_yr))

    logger.info(f"Partition Summary:")
    logger.info(f" - Train Set (<= {train_end_yr}): {train_df.height} rows, positive rate = {train_df[TARGET_COL].mean():.3f}")
    logger.info(f" - Val Set   ({val_start_yr}-{val_end_yr}): {val_df.height} rows, positive rate = {val_df[TARGET_COL].mean():.3f}")
    logger.info(f" - Test Set  ({test_start_yr}-{test_end_yr}): {test_df.height} rows, positive rate = {test_df[TARGET_COL].mean():.3f}")
    logger.info(f" - Live Serving Panel ({max_yr} Q{max_qtr}): {live_inference_df.height} mines")

    # Save to processed directory
    train_df.write_parquet(PROCESSED_DATA_DIR / "train_features.parquet", compression="snappy")
    val_df.write_parquet(PROCESSED_DATA_DIR / "val_features.parquet", compression="snappy")
    test_df.write_parquet(PROCESSED_DATA_DIR / "test_features.parquet", compression="snappy")
    live_inference_df.write_parquet(PROCESSED_DATA_DIR / "live_inference_panel.parquet", compression="snappy")

    return {
        "train": train_df,
        "val": val_df,
        "test": test_df,
        "live": live_inference_df,
    }


if __name__ == "__main__":
    features_df = engineer_features()
    splits = split_temporal_partitions(features_df)
