"""Data Ingestion & Extraction Engine for MSHA Open Data.
Supports automated download, Polars lazy reading, schema validation,
and realistic benchmark synthesis for offline/testing reproducibility.
"""

import os
import zipfile
import urllib.request
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import polars as pl
import numpy as np

from src.config import (
    RAW_DATA_DIR,
    MSHA_BASE_URL,
    MSHA_FILES,
    RANDOM_STATE,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def download_msha_file(table_name: str, target_dir: Optional[Path] = None) -> Optional[Path]:
    """Downloads an official MSHA table zip file if not present locally."""
    target_dir = target_dir or RAW_DATA_DIR
    filename = MSHA_FILES.get(table_name)
    if not filename:
        raise ValueError(f"Unknown table name: {table_name}. Available: {list(MSHA_FILES.keys())}")

    dest_zip = target_dir / filename
    if dest_zip.exists():
        logger.info(f"File already exists: {dest_zip}")
        return dest_zip

    url = f"{MSHA_BASE_URL}/{filename}"
    logger.info(f"Attempting download from {url} to {dest_zip}...")
    try:
        urllib.request.urlretrieve(url, dest_zip)
        logger.info(f"Successfully downloaded {filename}")
        return dest_zip
    except Exception as e:
        logger.warning(f"Could not download {filename} from {url} ({e}).")
        return None


def extract_zip(zip_path: Path, extract_to: Optional[Path] = None) -> Path:
    """Extracts a zip file containing MSHA text/pipe-delimited files."""
    extract_to = extract_to or RAW_DATA_DIR
    logger.info(f"Extracting {zip_path.name} to {extract_to}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    return extract_to


def generate_synthetic_msha_data(
    output_dir: Optional[Path] = None,
    n_mines: int = 1500,
    start_year: int = 2012,
    end_year: int = 2025,
    seed: int = RANDOM_STATE,
) -> Dict[str, Path]:
    """Generates realistic MSHA benchmark relational tables matching official schemas.
    Enables instant offline execution, CI/CD testing, and reproducible Colab demonstrations.
    """
    output_dir = output_dir or RAW_DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    logger.info(f"Synthesizing realistic MSHA benchmark panel for {n_mines} mines ({start_year}-{end_year})...")

    # 1. Mines Registry (Mines.txt)
    mine_ids = [f"{rng.integers(1000000, 9999999):07d}" for _ in range(n_mines)]
    states = ["WV", "KY", "PA", "WY", "TX", "VA", "IL", "IN", "AL", "OH", "AZ", "NV", "CO"]
    state_probs = [0.18, 0.16, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.03, 0.03, 0.03]
    commodities = ["C", "M"]
    comm_probs = [0.45, 0.55]
    types = ["Underground", "Surface", "Facility"]
    type_probs = [0.35, 0.55, 0.10]

    mine_names = [f"Mine Operation {i+1} - {rng.choice(['Alpha', 'Ridge', 'Valley', 'Creek', 'Hollow'])}" for i in range(n_mines)]
    assigned_states = rng.choice(states, size=n_mines, p=state_probs)
    assigned_comm = rng.choice(commodities, size=n_mines, p=comm_probs)
    assigned_types = rng.choice(types, size=n_mines, p=type_probs)
    
    # State lat/lon centers for realistic US coordinates
    state_coords = {
        "WV": (38.5, -80.5), "KY": (37.5, -85.3), "PA": (41.2, -77.2), "WY": (43.0, -107.5),
        "TX": (31.9, -99.9), "VA": (37.5, -78.6), "IL": (40.6, -89.4), "IN": (40.2, -86.1),
        "AL": (32.3, -86.9), "OH": (40.4, -82.9), "AZ": (34.0, -111.0), "NV": (38.8, -116.4), "CO": (39.5, -105.7)
    }
    latitudes = [state_coords[s][0] + rng.normal(0, 0.6) for s in assigned_states]
    longitudes = [state_coords[s][1] + rng.normal(0, 0.6) for s in assigned_states]

    mines_df = pl.DataFrame({
        "MINE_ID": mine_ids,
        "CURRENT_MINE_NAME": mine_names,
        "CURRENT_STATUS": rng.choice(["Active", "Temporarily Idled"], size=n_mines, p=[0.92, 0.08]),
        "STATE": assigned_states,
        "COAL_METAL_IND": assigned_comm,
        "PRIMARY_CANVASS_CD": assigned_types,
        "LATITUDE": latitudes,
        "LONGITUDE": longitudes,
    })
    mines_path = output_dir / "Mines.txt"
    mines_df.write_csv(mines_path, separator="|")

    # 2. Quarterly Employment & Production
    emp_rows = []
    years = list(range(start_year, end_year + 1))
    quarters = [1, 2, 3, 4]

    for m_id, m_type, m_comm in zip(mine_ids, assigned_types, assigned_comm):
        base_emp = rng.integers(15, 350) if m_type == "Underground" else rng.integers(10, 200)
        base_hours_per_emp = rng.integers(400, 550)

        for yr in years:
            for qtr in quarters:
                # 5% chance of idle quarter
                if rng.random() < 0.05:
                    continue
                emp_count = max(5, int(base_emp * rng.normal(1.0, 0.12)))
                hours = emp_count * int(base_hours_per_emp * rng.normal(1.0, 0.08))
                prod = (hours * rng.uniform(2.5, 8.0)) if m_comm == "C" else 0.0

                emp_rows.append({
                    "MINE_ID": m_id,
                    "CAL_YR": yr,
                    "CAL_QTR": qtr,
                    "SUBUNIT_CD": 1,
                    "AVG_EMPLOYEE_CNT": emp_count,
                    "EMPLOYEE_HOURS": hours,
                    "COAL_PRODUCTION": round(prod, 1),
                })

    emp_df = pl.DataFrame(emp_rows)
    emp_path = output_dir / "QuarterlyEmploymentProduction.txt"
    emp_df.write_csv(emp_path, separator="|")

    # 3. Inspections & 4. Violations
    insp_rows = []
    viol_rows = []
    event_counter = 10000000

    for m_id, s in zip(mine_ids, assigned_states):
        for yr in years:
            for qtr in quarters:
                # 0-3 inspections per quarter
                n_insp = rng.choice([0, 1, 2, 3], p=[0.35, 0.45, 0.15, 0.05])
                for _ in range(n_insp):
                    event_counter += 1
                    event_no = str(event_counter)
                    insp_hours = round(float(rng.uniform(10.0, 120.0)), 1)
                    samples = int(rng.choice([0, 1, 2, 5], p=[0.6, 0.2, 0.15, 0.05]))

                    insp_rows.append({
                        "EVENT_NO": event_no,
                        "MINE_ID": m_id,
                        "CAL_YR": yr,
                        "CAL_QTR": qtr,
                        "INSP_START_DATE": f"{yr}-{(qtr-1)*3+1:02d}-05",
                        "INSP_END_DATE": f"{yr}-{(qtr-1)*3+2:02d}-20",
                        "TOTAL_INSP_HOURS": insp_hours,
                        "SAMPLE_CNT": samples,
                    })

                    # Each inspection may generate 0-6 violations
                    n_viols = rng.choice([0, 1, 2, 3, 5], p=[0.40, 0.30, 0.15, 0.10, 0.05])
                    for v_idx in range(n_viols):
                        sig_sub = "Y" if rng.random() < 0.28 else "N"
                        negligence = rng.choice(["Low", "Moderate", "High", "Reckless"], p=[0.20, 0.55, 0.20, 0.05])
                        likelihood = rng.choice(["Unlikely", "Reasonably Likely", "Highly Likely", "Occurred"], p=[0.30, 0.45, 0.20, 0.05])

                        viol_rows.append({
                            "EVENT_NO": event_no,
                            "MINE_ID": m_id,
                            "VIOLATION_NO": f"{event_no}{v_idx}",
                            "CAL_YR": yr,
                            "CAL_QTR": qtr,
                            "ISSUE_DATE": f"{yr}-{(qtr-1)*3+2:02d}-15",
                            "SIG_AND_SUB": sig_sub,
                            "NEGLIGENCE": negligence,
                            "LIKELIHOOD": likelihood,
                            "PROPOSED_PENALTY": float(rng.choice([150, 400, 1200, 3500, 10000], p=[0.3, 0.4, 0.18, 0.09, 0.03])),
                        })

    insp_df = pl.DataFrame(insp_rows)
    insp_path = output_dir / "Inspections.txt"
    insp_df.write_csv(insp_path, separator="|")

    viol_df = pl.DataFrame(viol_rows)
    viol_path = output_dir / "Violations.txt"
    viol_df.write_csv(viol_path, separator="|")

    # 5. Accidents & Safety History
    # Injury rate is realistically correlated with hours, underground type, and past violations
    accident_rows = []
    doc_counter = 50000000

    # Build quick lookup for violations per mine-quarter
    viol_counts = {}
    for v in viol_rows:
        key = (v["MINE_ID"], v["CAL_YR"], v["CAL_QTR"])
        viol_counts[key] = viol_counts.get(key, 0) + (2 if v["SIG_AND_SUB"] == "Y" else 1)

    for emp in emp_rows:
        m_id = emp["MINE_ID"]
        yr = emp["CAL_YR"]
        qtr = emp["CAL_QTR"]
        hours = emp["EMPLOYEE_HOURS"]

        v_score = viol_counts.get((m_id, yr, qtr), 0)
        # Baseline incident expectation: ~2.5 injuries per 200k hours, scaled by violations
        lambda_rate = (hours / 200000.0) * 2.2 * (1.0 + 0.15 * min(v_score, 8))
        n_accidents = rng.poisson(lambda_rate)

        for a_idx in range(n_accidents):
            doc_counter += 1
            # Severity degrees: 01=Fatal, 02=Perm Total, 03=Perm Partial, 04=Days Away, 05=Restricted, 06=No Lost Time
            inj_deg = rng.choice(["01", "03", "04", "05", "06"], p=[0.01, 0.03, 0.45, 0.25, 0.26])
            days_lost = 0
            if inj_deg in ["04", "05"]:
                days_lost = int(rng.exponential(22)) + 1
            
            accident_rows.append({
                "DOCUMENT_NO": str(doc_counter),
                "MINE_ID": m_id,
                "CAL_YR": yr,
                "CAL_QTR": qtr,
                "ACCIDENT_DATE": f"{yr}-{(qtr-1)*3+rng.integers(1, 4):02d}-{rng.integers(1, 28):02d}",
                "INJ_DEGREE": inj_deg,
                "DAYS_LOST": days_lost,
                "DAYS_RESTRICT": int(days_lost * 0.4) if inj_deg == "05" else 0,
                "ACCIDENT_TYPE": rng.choice(["Fall of Roof", "Struck by Object", "Slips and Falls", "Machinery", "Powered Haulage", "Handling Material"]),
                "NARRATIVE": f"Worker experienced incident during standard operational shift in subunit.",
            })

    acc_df = pl.DataFrame(accident_rows)
    acc_path = output_dir / "Accidents.txt"
    acc_df.write_csv(acc_path, separator="|")

    logger.info(f"Synthesis complete! Files written to {output_dir}:")
    logger.info(f" - Mines: {mines_df.height} rows")
    logger.info(f" - Quarterly Employment: {emp_df.height} rows")
    logger.info(f" - Inspections: {insp_df.height} rows")
    logger.info(f" - Violations: {viol_df.height} rows")
    logger.info(f" - Accidents: {acc_df.height} rows")

    return {
        "mines": mines_path,
        "employment": emp_path,
        "inspections": insp_path,
        "violations": viol_path,
        "accidents": acc_path,
    }


def load_msha_table(table_name: str, data_dir: Optional[Path] = None) -> pl.LazyFrame:
    """Loads an MSHA pipe-delimited table as a memory-efficient Polars LazyFrame."""
    data_dir = data_dir or RAW_DATA_DIR
    filename_map = {
        "mines": "Mines.txt",
        "employment": "QuarterlyEmploymentProduction.txt",
        "inspections": "Inspections.txt",
        "violations": "Violations.txt",
        "accidents": "Accidents.txt",
    }
    
    file_path = data_dir / filename_map[table_name]
    if not file_path.exists():
        # Check if zip exists
        zip_path = data_dir / MSHA_FILES.get(table_name, "")
        if zip_path.exists():
            extract_zip(zip_path, data_dir)
        else:
            logger.info(f"{file_path} not found. Synthesizing realistic benchmark dataset...")
            generate_synthetic_msha_data(output_dir=data_dir)

    logger.info(f"Scanning {table_name} from {file_path}...")
    lf = pl.scan_csv(
        file_path,
        separator="|",
        infer_schema_length=10000,
        ignore_errors=True,
    )
    return lf
