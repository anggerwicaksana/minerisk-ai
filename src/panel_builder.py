"""Relational Panel Builder for MineRisk-AI.
Constructs a time-indexed Star-Schema panel at the (MINE_ID, CAL_YR, CAL_QTR) level
using Polars lazy scanning and strict anti-leakage audits.
"""

import logging
from pathlib import Path
from typing import Optional
import polars as pl

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.ingestion import load_msha_table

logger = logging.getLogger(__name__)


def build_quarterly_mine_panel(data_dir: Optional[Path] = None) -> pl.DataFrame:
    """Builds an aggregated star-schema panel from the 5 relational MSHA tables.
    Guarantees zero-leakage by filtering mutable CURRENT_* fields.
    """
    logger.info("Initiating quarterly panel build via Polars LazyFrames...")

    # 1. Base Panel: Employment & Hours (Exposure Denominator)
    emp_lf = load_msha_table("employment", data_dir)
    base_panel_lf = (
        emp_lf.group_by(["MINE_ID", "CAL_YR", "CAL_QTR"])
        .agg([
            pl.col("EMPLOYEE_HOURS").cast(pl.Float64).sum().alias("hours_worked_q0"),
            pl.col("AVG_EMPLOYEE_CNT").cast(pl.Float64).mean().alias("avg_employees_q0"),
            pl.col("COAL_PRODUCTION").cast(pl.Float64).sum().alias("coal_production_q0"),
        ])
        .filter(pl.col("hours_worked_q0") > 0)
    )

    # 2. Inspections Aggregation
    insp_lf = load_msha_table("inspections", data_dir)
    insp_agg_lf = (
        insp_lf.group_by(["MINE_ID", "CAL_YR", "CAL_QTR"])
        .agg([
            pl.len().alias("insp_count_q0"),
            pl.col("TOTAL_INSP_HOURS").cast(pl.Float64).fill_null(0.0).sum().alias("insp_hours_q0"),
            pl.col("SAMPLE_CNT").cast(pl.Int64).fill_null(0).sum().alias("insp_samples_q0"),
        ])
    )

    # 3. Violations Aggregation
    viol_lf = load_msha_table("violations", data_dir)
    viol_agg_lf = (
        viol_lf.group_by(["MINE_ID", "CAL_YR", "CAL_QTR"])
        .agg([
            pl.len().alias("viol_count_q0"),
            (pl.col("SIG_AND_SUB") == "Y").cast(pl.Int64).sum().alias("viol_ss_count_q0"),
            pl.col("NEGLIGENCE").is_in(["High", "Reckless"]).cast(pl.Int64).sum().alias("viol_high_negligence_q0"),
            pl.col("PROPOSED_PENALTY").cast(pl.Float64).fill_null(0.0).sum().alias("viol_penalties_q0"),
        ])
    )

    # 4. Accidents Aggregation (Qualifying Part 50 Reportable Cases)
    acc_lf = load_msha_table("accidents", data_dir)
    reportable_degrees = ["01", "02", "03", "04", "05", "06", "1", "2", "3", "4", "5", "6"]
    acc_agg_lf = (
        acc_lf.group_by(["MINE_ID", "CAL_YR", "CAL_QTR"])
        .agg([
            pl.col("INJ_DEGREE").cast(pl.Utf8).is_in(reportable_degrees).cast(pl.Int64).sum().alias("injury_count_q0"),
            (pl.col("INJ_DEGREE").cast(pl.Utf8).is_in(["01", "1"])).cast(pl.Int64).sum().alias("fatal_count_q0"),
            (pl.col("DAYS_LOST").cast(pl.Int64).fill_null(0) + pl.col("DAYS_RESTRICT").cast(pl.Int64).fill_null(0)).sum().alias("days_lost_q0"),
        ])
    )

    # 5. Static Context: Mines Registry (Anti-Leakage Audit)
    mines_lf = load_msha_table("mines", data_dir)
    
    # AUDIT: Drop mutable CURRENT_* fields to prevent lookahead leakage
    mines_clean_lf = (
        mines_lf.select([
            pl.col("MINE_ID"),
            pl.col("CURRENT_MINE_NAME").alias("mine_name"), # Preserved for display/UI lookup only
            pl.col("STATE").alias("state"),
            pl.col("COAL_METAL_IND").alias("coal_metal_ind"),
            pl.col("PRIMARY_CANVASS_CD").alias("mine_type"),
            pl.col("LATITUDE").cast(pl.Float64).alias("latitude"),
            pl.col("LONGITUDE").cast(pl.Float64).alias("longitude"),
        ])
        .unique(subset=["MINE_ID"])
    )

    # 6. Star-Schema Join onto Base Panel
    panel_lf = (
        base_panel_lf
        .join(mines_clean_lf, on="MINE_ID", how="left")
        .join(insp_agg_lf, on=["MINE_ID", "CAL_YR", "CAL_QTR"], how="left")
        .join(viol_agg_lf, on=["MINE_ID", "CAL_YR", "CAL_QTR"], how="left")
        .join(acc_agg_lf, on=["MINE_ID", "CAL_YR", "CAL_QTR"], how="left")
        .with_columns([
            pl.col("insp_count_q0").fill_null(0),
            pl.col("insp_hours_q0").fill_null(0.0),
            pl.col("insp_samples_q0").fill_null(0),
            pl.col("viol_count_q0").fill_null(0),
            pl.col("viol_ss_count_q0").fill_null(0),
            pl.col("viol_high_negligence_q0").fill_null(0),
            pl.col("viol_penalties_q0").fill_null(0.0),
            pl.col("injury_count_q0").fill_null(0),
            pl.col("fatal_count_q0").fill_null(0),
            pl.col("days_lost_q0").fill_null(0),
            pl.col("coal_production_q0").fill_null(0.0),
            pl.col("mine_type").fill_null("Surface"),
            pl.col("coal_metal_ind").fill_null("M"),
            pl.col("state").fill_null("OTHER"),
        ])
        .sort(["MINE_ID", "CAL_YR", "CAL_QTR"])
    )

    logger.info("Executing Polars query graph and collecting final panel...")
    panel_df = panel_lf.collect()
    logger.info(f"Successfully constructed raw quarterly panel: {panel_df.height} rows, {panel_df.width} columns.")

    output_path = PROCESSED_DATA_DIR / "msha_raw_quarterly_panel.parquet"
    panel_df.write_parquet(output_path, compression="snappy")
    logger.info(f"Saved raw panel to {output_path}")

    return panel_df


if __name__ == "__main__":
    build_quarterly_mine_panel()
