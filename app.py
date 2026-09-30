"""MineRisk-AI (SafeCast) - Interactive Web Application.
Interactive Predictive Safety & Health (OSH) Risk Intelligence Platform.
Deployable on Hugging Face Spaces and executable in Google Colab.
"""

import os
import sys
from pathlib import Path
from typing import Tuple, Dict, Any, List

# Prevent OpenBLAS memory allocation failure in constrained environments
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import json
import joblib
import numpy as np
import pandas as pd
import gradio as gr
import plotly.graph_objects as go

from src.config import ARTIFACTS_DIR, RISK_TIERS, ALL_FEATURES, NUMERICAL_FEATURES, CATEGORICAL_FEATURES
from src.explainability import MineRiskExplainer, build_plotly_waterfall, build_geospatial_risk_map
from mcp_server import (
    predict_mine_risk,
    simulate_safety_scenario,
    get_high_risk_surveillance_queue,
    get_model_benchmark_info,
)

# Global Artifacts Cache
MODEL_WRAPPER = None
FEATURE_META = None
BENCHMARK_METRICS = None
SAMPLE_PANEL_DF = None
EXPLAINER = None


def load_artifacts():
    """Loads trained calibrated model, sample data, and metadata into memory."""
    global MODEL_WRAPPER, FEATURE_META, BENCHMARK_METRICS, SAMPLE_PANEL_DF, EXPLAINER

    model_path = ARTIFACTS_DIR / "model_calibrated.joblib"
    meta_path = ARTIFACTS_DIR / "feature_metadata.json"
    bench_path = ARTIFACTS_DIR / "benchmark_metrics.json"
    panel_path = ARTIFACTS_DIR / "demo_sample_panel.parquet"

    if not model_path.exists() or not panel_path.exists():
        # Pipeline needs to run first
        return False

    MODEL_WRAPPER = joblib.load(model_path)
    with open(meta_path, "r") as f:
        FEATURE_META = json.load(f)
    with open(bench_path, "r") as f:
        BENCHMARK_METRICS = json.load(f)

    raw_panel = pd.read_parquet(panel_path)
    raw_panel["MINE_ID"] = raw_panel["MINE_ID"].astype(str)
    if "mine_name" in raw_panel.columns:
        raw_panel["mine_name"] = raw_panel["mine_name"].astype(str)
    
    # Compute predictions for sample panel
    feature_cols = FEATURE_META["all_features"]
    for cat_col in CATEGORICAL_FEATURES:
        if cat_col in raw_panel.columns:
            raw_panel[cat_col] = raw_panel[cat_col].astype("category")

    probs = MODEL_WRAPPER.predict_proba(raw_panel[feature_cols])[:, 1]
    raw_panel["predicted_risk_prob"] = probs
    raw_panel["risk_score_pct"] = probs * 100.0

    # Assign risk tier
    def get_tier(p):
        if p < 0.20:
            return "Low"
        elif p < 0.45:
            return "Moderate"
        elif p < 0.70:
            return "Elevated"
        else:
            return "Critical"

    raw_panel["risk_tier"] = raw_panel["predicted_risk_prob"].apply(get_tier)
    SAMPLE_PANEL_DF = raw_panel

    # Initialize SHAP explainer
    EXPLAINER = MineRiskExplainer(MODEL_WRAPPER, feature_cols)
    return True


# ---------------- Tab 1 Callbacks: Surveillance Map & Top-20 ---------------- #
def filter_surveillance_data(state_filter: str, commodity_filter: str, tier_filter: str):
    """Filters the map and table according to user selection."""
    if SAMPLE_PANEL_DF is None:
        return go.Figure(), pd.DataFrame()

    df = SAMPLE_PANEL_DF.copy()

    if state_filter and state_filter != "ALL":
        df = df[df["state"] == state_filter]
    if commodity_filter and commodity_filter != "ALL":
        df = df[df["coal_metal_ind"] == commodity_filter]
    if tier_filter and tier_filter != "ALL":
        df = df[df["risk_tier"] == tier_filter]

    fig = build_geospatial_risk_map(df)

    display_cols = [
        "MINE_ID",
        "mine_name",
        "state",
        "coal_metal_ind",
        "mine_type",
        "hours_worked_q0",
        "viol_count_q0",
        "risk_tier",
        "risk_score_pct",
    ]
    table_df = (
        df[display_cols]
        .sort_values(by="risk_score_pct", ascending=False)
        .head(20)
        .rename(columns={
            "MINE_ID": "Mine ID",
            "mine_name": "Mine Name",
            "state": "State",
            "coal_metal_ind": "Commodity",
            "mine_type": "Type",
            "hours_worked_q0": "Quarter Hours",
            "viol_count_q0": "Violations",
            "risk_tier": "Risk Tier",
            "risk_score_pct": "Predicted Risk (%)",
        })
    )
    return fig, table_df


# ---------------- Tab 2 Callbacks: Individual Mine Inspector ---------------- #
def inspect_single_mine(selected_mine_str: str):
    """Deep-dives into a selected mine: risk badge, peer benchmark, and SHAP waterfall."""
    if SAMPLE_PANEL_DF is None or not selected_mine_str:
        return "", "", go.Figure(), ""

    mine_id = selected_mine_str.split(" - ")[0].strip()
    match = SAMPLE_PANEL_DF[SAMPLE_PANEL_DF["MINE_ID"] == mine_id]
    if match.empty:
        return "Mine not found", "", go.Figure(), ""

    row = match.iloc[0]
    prob = float(row["predicted_risk_prob"])
    tier = row["risk_tier"]
    tier_info = RISK_TIERS[tier]

    badge_html = f"""
    <div style="background-color: {tier_info['color']}; color: white; padding: 18px 24px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
        <h2 style="margin: 0; font-size: 26px;">{tier_info['badge']}</h2>
        <h1 style="margin: 5px 0 0 0; font-size: 42px; font-weight: 800;">{prob*100:.1f}%</h1>
        <p style="margin: 0; font-size: 14px; opacity: 0.9;">Probability of Worker Injury in Next Quarter (t+1)</p>
    </div>
    """

    nat_avg = float(SAMPLE_PANEL_DF["predicted_risk_prob"].mean() * 100.0)
    delta_avg = (prob * 100.0) - nat_avg
    delta_str = f"+{delta_avg:.1f}% above national baseline" if delta_avg > 0 else f"{delta_avg:.1f}% below national baseline"

    summary_text = f"""
    ### **Mine Details: {row['mine_name']}**
    - **Mine ID:** `{row['MINE_ID']}` | **State:** `{row['state']}`
    - **Commodity Group:** `{'Coal' if row['coal_metal_ind'] == 'C' else 'Metal/Non-metal'}` | **Type:** `{row['mine_type']}`
    - **Workforce Hours (Q0):** `{row['hours_worked_q0']:,.0f} hours` (~`{int(row['avg_employees_q0'])}` workers)
    - **Past Quarter Violations:** `{int(row['viol_count_q0'])} citations` (`{int(row['viol_ss_count_q0'])}` Significant & Substantial)
    - **Peer Comparison:** **{delta_str}** (National Average: `{nat_avg:.1f}%`).
    """

    # SHAP Explanation
    features_series = row[FEATURE_META["all_features"]]
    explanation = EXPLAINER.explain_mine(features_series)
    waterfall_fig = build_plotly_waterfall(explanation, prob, mine_name=row["mine_name"])

    # Actionable Guidance
    if tier == "Critical":
        rec = "⚠️ **CRITICAL ACTION REQUIRED:** Immediate on-site audit recommended. Focus inspection on S&S safety citations and overtime fatigue mitigation before start of next quarter."
    elif tier == "Elevated":
        rec = "🟠 **ELEVATED HAZARD:** Prioritize inspection queue. Review hazard training programs and monitor hours worked to avoid worker fatigue spikes."
    elif tier == "Moderate":
        rec = "🟡 **MODERATE RISK:** Routine monitoring. Verify that past inspection citations have been fully abated."
    else:
        rec = "🟢 **LOW RISK:** Operational parameters reflect stable safety performance. Maintain standard quarterly reporting."

    return badge_html, summary_text, waterfall_fig, rec


# ---------------- Tab 3 Callbacks: What-If Sandbox Simulator ---------------- #
def simulate_risk_scenario(
    hours_input: float,
    employees_input: float,
    mine_type_input: str,
    commodity_input: str,
    state_input: str,
    prior_injuries: int,
    insp_hours_input: float,
    viol_count_input: int,
    viol_ss_count_input: int,
):
    """Simulates operational adjustments in real-time and computes updated probability and SHAP."""
    if MODEL_WRAPPER is None:
        return "", go.Figure(), ""

    # Construct synthetic feature row
    comm_code = "C" if commodity_input == "Coal" else "M"
    log_hours = float(np.log(max(1.0, hours_input) + 1.0))
    ss_ratio = float(viol_ss_count_input / (viol_count_input + 1.0))
    viol_per_insp = float(viol_count_input / (insp_hours_input + 0.1))
    inj_rate_200k = float((prior_injuries * 200000.0) / max(1.0, hours_input))

    row_dict = {
        "hours_worked_q0": float(hours_input),
        "avg_employees_q0": float(employees_input),
        "log_hours_q0": log_hours,
        "hours_worked_lag1": float(hours_input),
        "hours_delta_1q": 0.0,
        "hours_pct_change_1q": 0.0,
        "hours_rolling_4q_mean": float(hours_input),
        "injury_count_q0": int(prior_injuries),
        "injury_count_lag1": int(prior_injuries),
        "injury_count_lag2": 0,
        "injury_count_lag3": 0,
        "injury_rolling_4q_sum": int(prior_injuries * 2),
        "days_lost_q0": int(prior_injuries * 15),
        "days_lost_rolling_4q": int(prior_injuries * 30),
        "injury_rate_per_200k_q0": inj_rate_200k,
        "injury_rate_rolling_4q": inj_rate_200k,
        "has_prior_injury_q0": int(prior_injuries >= 1),
        "insp_count_q0": 1 if insp_hours_input > 0 else 0,
        "insp_hours_q0": float(insp_hours_input),
        "insp_hours_rolling_4q": float(insp_hours_input * 2),
        "viol_count_q0": int(viol_count_input),
        "viol_count_lag1": int(viol_count_input),
        "viol_rolling_4q_sum": int(viol_count_input * 2),
        "viol_ss_count_q0": int(viol_ss_count_input),
        "viol_ss_ratio_q0": ss_ratio,
        "viol_high_negligence_q0": int(viol_ss_count_input // 2),
        "viol_per_insp_hour_q0": viol_per_insp,
        "consecutive_zero_injury_qtrs": 1 if prior_injuries == 0 else 0,
        "coal_metal_ind": comm_code,
        "mine_type": mine_type_input,
        "state": state_input,
        "calendar_quarter": 1,
    }

    row_df = pd.DataFrame([row_dict])
    for cat_col in CATEGORICAL_FEATURES:
        row_df[cat_col] = row_df[cat_col].astype("category")

    feature_cols = FEATURE_META["all_features"]
    prob = float(MODEL_WRAPPER.predict_proba(row_df[feature_cols])[0, 1])

    if prob < 0.20:
        tier = "Low"
    elif prob < 0.45:
        tier = "Moderate"
    elif prob < 0.70:
        tier = "Elevated"
    else:
        tier = "Critical"

    tier_info = RISK_TIERS[tier]

    badge_html = f"""
    <div style="background-color: {tier_info['color']}; color: white; padding: 18px 24px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
        <h2 style="margin: 0; font-size: 24px;">SIMULATED RISK: {tier_info['badge']}</h2>
        <h1 style="margin: 5px 0 0 0; font-size: 42px; font-weight: 800;">{prob*100:.1f}%</h1>
        <p style="margin: 0; font-size: 14px; opacity: 0.9;">Projected Probability of Injury Next Quarter</p>
    </div>
    """

    explanation = EXPLAINER.explain_mine(row_df[feature_cols].iloc[0])
    waterfall_fig = build_plotly_waterfall(explanation, prob, mine_name="Simulated Mine Scenario")

    advice = []
    if ss_ratio > 0.4:
        advice.append("⚠️ **High S&S Violation Ratio:** Significant & Substantial violations are heavily driving risk upward. Prioritize remediation of serious electrical and roof-support citations.")
    if hours_input > 100000 and prior_injuries > 1:
        advice.append("🟠 **High Exposure & Incident Recurrence:** Operations with large workforces and recurring injuries require mandatory safety stand-downs.")
    if insp_hours_input > 50 and viol_count_input == 0:
        advice.append("🟢 **Positive Inspection Impact:** Substantial inspection hours with zero violations actively suppress risk score.")
    if not advice:
        advice.append("ℹ️ Operational parameters are within acceptable statistical boundaries for this mine class.")

    recommendation_text = "\n\n".join(advice)
    return badge_html, waterfall_fig, recommendation_text


# ---------------- Build Gradio Blocks Application ---------------- #
def build_gradio_app():
    """Assembles the complete 3-Tab Gradio user interface."""
    artifacts_ready = load_artifacts()

    custom_theme = gr.themes.Soft(
        primary_hue="blue",
        neutral_hue="slate",
    )

    with gr.Blocks(title="MineRisk-AI (SafeCast) | Predictive Safety Intelligence") as demo:
        gr.Markdown("""
        # ⛏️ **MineRisk-AI (SafeCast)**
        ### *Predictive Workplace Safety & Health (OSH) Risk Intelligence System*
        **Authoritative Data:** U.S. Mine Safety and Health Administration (MSHA, 2000–2025)  
        **Methodology:** Leakage-Proof Relational Star-Schema Panel • Strict Out-of-Time Temporal Split • Calibrated LightGBM • SHAP XAI
        """)

        if not artifacts_ready:
            gr.Warning("⚠️ Model artifacts not yet generated. Please execute the training pipeline first.")
            return demo

        bench = BENCHMARK_METRICS["test_metrics"]

        with gr.Row():
            gr.Markdown(f"""
            | 📈 **PR-AUC (Precision-Recall)** | 🎯 **ROC-AUC Score** | 🚀 **Top-10% Decile Lift** | 🛡️ **Brier Score (Calibrated)** |
            |:---:|:---:|:---:|:---:|
            | **`{bench['pr_auc']:.3f}`** | **`{bench['roc_auc']:.3f}`** | **`{bench['lift_top10']:.2f}x` higher risk** | **`{bench['calibrated_brier']:.4f}` (vs {bench['uncalibrated_brier']:.4f} raw)** |
            """)

        with gr.Tabs():
            # ======================== TAB 1: EXECUTIVE SURVEILLANCE ======================== #
            with gr.Tab("🗺️ National Surveillance Map & Top-20"):
                gr.Markdown("### **Executive Mine-Quarter Risk Surveillance Dashboard**")
                with gr.Row():
                    state_dropdown = gr.Dropdown(
                        choices=["ALL", "WV", "KY", "PA", "WY", "TX", "VA", "IL", "IN", "AL", "OH", "AZ", "NV", "CO"],
                        value="ALL",
                        label="Filter by State",
                    )
                    comm_dropdown = gr.Dropdown(
                        choices=["ALL", "C", "M"],
                        value="ALL",
                        label="Commodity (C = Coal, M = Metal/Nonmetal)",
                    )
                    tier_dropdown = gr.Dropdown(
                        choices=["ALL", "Low", "Moderate", "Elevated", "Critical"],
                        value="ALL",
                        label="Risk Tier",
                    )

                map_plot = gr.Plot(label="National Mine Risk Map")
                gr.Markdown("### **Top-20 High-Risk Mines Prioritization Queue (Quarter Ahead)**")
                top_table = gr.DataFrame(interactive=False)

                # Connect reactive events
                for drop in [state_dropdown, comm_dropdown, tier_dropdown]:
                    drop.change(
                        fn=filter_surveillance_data,
                        inputs=[state_dropdown, comm_dropdown, tier_dropdown],
                        outputs=[map_plot, top_table],
                    )

            # ======================== TAB 2: MINE RISK INSPECTOR ======================== #
            with gr.Tab("🔍 Mine Risk Inspector & SHAP Deep-Dive"):
                gr.Markdown("### **Individual Mine Risk Profiler & Explainable AI (SHAP Waterfall)**")
                
                # Mine selection options
                mine_options = [
                    f"{row['MINE_ID']} - {row['mine_name']} ({row['state']})"
                    for _, row in SAMPLE_PANEL_DF.head(200).iterrows()
                ]
                mine_selector = gr.Dropdown(
                    choices=mine_options,
                    value=mine_options[0] if mine_options else None,
                    label="Select Active Mine to Inspect",
                    filterable=True,
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        risk_badge_output = gr.HTML()
                        mine_details_output = gr.Markdown()
                    with gr.Column(scale=2):
                        waterfall_plot_output = gr.Plot(label="SHAP Factor Contribution Breakdown")

                guidance_output = gr.Markdown()

                mine_selector.change(
                    fn=inspect_single_mine,
                    inputs=[mine_selector],
                    outputs=[risk_badge_output, mine_details_output, waterfall_plot_output, guidance_output],
                )

            # ======================== TAB 3: WHAT-IF SCENARIO SIMULATOR ======================== #
            with gr.Tab("🧪 'What-If' Operational Risk Simulator"):
                gr.Markdown("""
                ### **Interactive Safety & Operational Risk Sandbox**
                Adjust operational parameters, hours worked, and regulatory inspection outcomes below to simulate how intervention strategies impact next-quarter injury risk.
                """)
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### **1. Exposure & Operation**")
                        hours_slider = gr.Slider(minimum=5000, maximum=250000, value=45000, step=2500, label="Quarterly Employee Hours")
                        emp_slider = gr.Slider(minimum=5, maximum=400, value=75, step=5, label="Average Workforce Count")
                        type_select = gr.Radio(choices=["Underground", "Surface", "Facility"], value="Underground", label="Mining Method")
                        comm_select = gr.Radio(choices=["Coal", "Metal/Nonmetal"], value="Coal", label="Commodity Group")
                        state_select = gr.Dropdown(choices=["WV", "KY", "PA", "WY", "TX", "VA", "CO", "AL"], value="WV", label="State Jurisdiction")

                    with gr.Column(scale=1):
                        gr.Markdown("#### **2. Enforcement & Safety History**")
                        inj_slider = gr.Slider(minimum=0, maximum=10, value=1, step=1, label="Injuries in Prior Quarter (Q0)")
                        insp_hours_slider = gr.Slider(minimum=0, maximum=150, value=25, step=5, label="MSHA Inspection Hours (Q0)")
                        viol_slider = gr.Slider(minimum=0, maximum=20, value=3, step=1, label="Safety Citations (Q0)")
                        viol_ss_slider = gr.Slider(minimum=0, maximum=10, value=1, step=1, label="Significant & Substantial (S&S) Citations")

                    with gr.Column(scale=2):
                        gr.Markdown("#### **3. Simulated Predictive Intelligence**")
                        sim_badge = gr.HTML()
                        sim_waterfall = gr.Plot(label="Simulated SHAP Risk Drivers")
                        sim_advice = gr.Markdown()

                # Wire simulation sliders
                sim_inputs = [
                    hours_slider,
                    emp_slider,
                    type_select,
                    comm_select,
                    state_select,
                    inj_slider,
                    insp_hours_slider,
                    viol_slider,
                    viol_ss_slider,
                ]

                for inp in sim_inputs:
                    inp.change(
                        fn=simulate_risk_scenario,
                        inputs=sim_inputs,
                        outputs=[sim_badge, sim_waterfall, sim_advice],
                    )

            # ---------------- Tab 4: Model Context Protocol (MCP) Agent Hub ---------------- #
            with gr.TabItem("🤖 MCP Agent Tools & API", id="tab_mcp"):
                gr.Markdown(
                    """
                    ### 🔌 Model Context Protocol (MCP) Server Integration
                    This Space natively exposes an **MCP Server** via Streamable HTTP at `/gradio_api/mcp`. 
                    Any MCP-compatible AI agent (Claude Code, Cursor, Antigravity IDE, VSCode, Windsurf) can connect 
                    directly to this Space to query prospective safety risk and run counterfactual simulations autonomously.

                    > 🌐 **Hugging Face Hub MCP Badge:** Follow the [Hugging Face Spaces MCP documentation](https://huggingface.co/docs/hub/spaces-mcp-servers).
                    > Add this Space via [Hub MCP Settings](https://huggingface.co/settings/mcp) or connect using URL: `https://<space-name>.hf.space/gradio_api/mcp`.
                    """
                )

                with gr.Accordion("🛠️ Tool 1: predict_mine_risk(mine_id_or_name)", open=True):
                    gr.Markdown("Queries prospective quarterly injury risk probability, risk tier badge, peer baseline, and top SHAP drivers.")
                    with gr.Row():
                        mcp_query_input = gr.Textbox(value="6265150", label="MSHA Mine ID or Name", placeholder="e.g. 6265150 or Valley")
                        mcp_query_btn = gr.Button("Invoke Tool: predict_mine_risk", variant="primary")
                    mcp_query_output = gr.Markdown()
                    mcp_query_btn.click(
                        fn=predict_mine_risk,
                        inputs=[mcp_query_input],
                        outputs=[mcp_query_output],
                        api_name="predict_mine_risk",
                    )

                with gr.Accordion("🛠️ Tool 2: simulate_safety_scenario(...)", open=False):
                    gr.Markdown("Simulates prospective risk outcome for custom operational parameters (hours, workforce, citations).")
                    with gr.Row():
                        sim_hrs = gr.Number(value=45000, label="Quarterly Hours Worked")
                        sim_emp = gr.Number(value=75, label="Average Employee Count")
                        sim_typ = gr.Dropdown(choices=["Underground", "Surface", "Facility"], value="Underground", label="Mining Method")
                        sim_comm = gr.Dropdown(choices=["Coal", "Metal/Nonmetal"], value="Coal", label="Commodity Group")
                        sim_st = gr.Dropdown(choices=["WV", "KY", "PA", "WY", "TX", "VA", "CO", "AL"], value="WV", label="State Jurisdiction")
                    with gr.Row():
                        sim_inj = gr.Number(value=1, label="Prior Quarter Injuries")
                        sim_insp = gr.Number(value=25, label="MSHA Inspection Hours")
                        sim_viol = gr.Number(value=3, label="Safety Citations")
                        sim_ss = gr.Number(value=1, label="S&S Citations")
                        sim_run_btn = gr.Button("Invoke Tool: simulate_safety_scenario", variant="primary")
                    mcp_sim_output = gr.Markdown()
                    sim_run_btn.click(
                        fn=simulate_safety_scenario,
                        inputs=[sim_hrs, sim_emp, sim_typ, sim_comm, sim_st, sim_inj, sim_insp, sim_viol, sim_ss],
                        outputs=[mcp_sim_output],
                        api_name="simulate_safety_scenario",
                    )

                with gr.Accordion("🛠️ Tool 3: get_high_risk_surveillance_queue(...)", open=False):
                    gr.Markdown("Retrieves prioritized national surveillance queue ranked by calibrated injury risk.")
                    with gr.Row():
                        q_topn = gr.Slider(minimum=5, maximum=50, value=10, step=5, label="Top N Mines")
                        q_state = gr.Dropdown(choices=["ALL", "WV", "KY", "PA", "WY", "TX", "VA", "CO", "AL"], value="ALL", label="Filter State")
                        q_comm = gr.Dropdown(choices=["ALL", "C", "M"], value="ALL", label="Filter Commodity")
                        q_tier = gr.Dropdown(choices=["ALL", "Critical", "Elevated", "Moderate", "Low"], value="ALL", label="Filter Risk Tier")
                        q_btn = gr.Button("Invoke Tool: get_high_risk_surveillance_queue", variant="primary")
                    mcp_queue_output = gr.Markdown()
                    q_btn.click(
                        fn=get_high_risk_surveillance_queue,
                        inputs=[q_topn, q_state, q_comm, q_tier],
                        outputs=[mcp_queue_output],
                        api_name="get_high_risk_surveillance_queue",
                    )

                with gr.Accordion("🛠️ Tool 4: get_model_benchmark_info()", open=False):
                    gr.Markdown("Returns out-of-time test set (2024–2025) discrimination, calibration metrics, and ablation results.")
                    bench_mcp_btn = gr.Button("Invoke Tool: get_model_benchmark_info", variant="primary")
                    mcp_bench_output = gr.Markdown()
                    bench_mcp_btn.click(
                        fn=get_model_benchmark_info,
                        inputs=[],
                        outputs=[mcp_bench_output],
                        api_name="get_model_benchmark_info",
                    )

        # Trigger initial load
        demo.load(
            fn=filter_surveillance_data,
            inputs=[state_dropdown, comm_dropdown, tier_dropdown],
            outputs=[map_plot, top_table],
        )
        demo.load(
            fn=inspect_single_mine,
            inputs=[mine_selector],
            outputs=[risk_badge_output, mine_details_output, waterfall_plot_output, guidance_output],
        )
        demo.load(
            fn=simulate_risk_scenario,
            inputs=sim_inputs,
            outputs=[sim_badge, sim_waterfall, sim_advice],
        )

    return demo


if __name__ == "__main__":
    app = build_gradio_app()
    app.launch(mcp_server=True)
