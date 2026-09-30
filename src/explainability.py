"""Explainability & Geospatial Visualization Engine for MineRisk-AI.
Generates SHAP TreeExplainer local waterfall explanations and
interactive Plotly geographic risk maps for the Gradio UI.
"""

import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import shap

from src.config import RISK_TIERS, CATEGORICAL_FEATURES

logger = logging.getLogger(__name__)


class MineRiskExplainer:
    """Wrapper for SHAP TreeExplainer to produce interpretable risk factor breakdowns."""

    def __init__(self, model_estimator: Any, feature_names: List[str]):
        self.model = model_estimator
        self.feature_names = feature_names
        # If calibrated wrapper passed, extract base tree estimator
        if hasattr(model_estimator, "base_estimator"):
            self.tree_model = model_estimator.base_estimator
        else:
            self.tree_model = model_estimator
            
        logger.info("Initializing SHAP TreeExplainer on LightGBM tree ensemble...")
        self.explainer = shap.TreeExplainer(self.tree_model)

    def explain_mine(
        self,
        features_row: pd.Series,
    ) -> Dict[str, Any]:
        """Calculates SHAP values for a single mine observation."""
        row_df = pd.DataFrame([features_row])[self.feature_names].copy()
        
        # Ensure categorical columns retain the exact training categories
        booster = getattr(self.tree_model, "booster_", None)
        if booster is not None and hasattr(booster, "pandas_categorical") and booster.pandas_categorical:
            cat_cols = [c for c in self.feature_names if c in CATEGORICAL_FEATURES]
            for c, cats in zip(cat_cols, booster.pandas_categorical):
                if c in row_df.columns:
                    row_df[c] = pd.Categorical(row_df[c], categories=cats)

        shap_vals = self.explainer.shap_values(row_df)
        
        # For binary classifier, extract positive class (class 1)
        if isinstance(shap_vals, list):
            sv = shap_vals[1][0]
            base_val = self.explainer.expected_value[1]
        elif len(shap_vals.shape) == 3:
            sv = shap_vals[0, :, 1]
            base_val = self.explainer.expected_value[1]
        else:
            sv = shap_vals[0]
            base_val = (
                self.explainer.expected_value[1]
                if isinstance(self.explainer.expected_value, (list, np.ndarray))
                else self.explainer.expected_value
            )

        # Pair features with their SHAP values and actual values
        contributions = []
        for name, val, s in zip(self.feature_names, row_df.iloc[0], sv):
            contributions.append({
                "feature": name,
                "value": val,
                "shap_value": float(s),
                "abs_shap": abs(float(s)),
            })

        contributions.sort(key=lambda x: x["abs_shap"], reverse=True)

        return {
            "base_value": float(base_val),
            "contributions": contributions,
            "top_drivers": contributions[:8],
        }


def build_plotly_waterfall(
    explanation: Dict[str, Any],
    calibrated_prob: float,
    mine_name: str = "Selected Mine",
) -> go.Figure:
    """Builds a Plotly Waterfall chart visualizing SHAP risk drivers."""
    drivers = explanation["top_drivers"]
    
    # Feature display name beautifier
    display_names = {
        "viol_ss_ratio_q0": "S&S Violation Ratio",
        "viol_count_q0": "Total Violations (Q0)",
        "viol_rolling_4q_sum": "4-Quarter Total Violations",
        "injury_count_q0": "Recent Injuries (Q0)",
        "injury_rolling_4q_sum": "4-Quarter Injuries",
        "hours_pct_change_1q": "Overtime Surge / Hours Delta",
        "log_hours_q0": "Workforce Exposure (Log Hours)",
        "hours_worked_q0": "Hours Worked (Q0)",
        "insp_hours_q0": "MSHA Inspection Hours",
        "insp_count_q0": "Inspection Count",
        "mine_type": "Mine Type (Underground/Surface)",
        "coal_metal_ind": "Commodity Group",
        "state": "State Jurisdiction",
        "viol_high_negligence_q0": "High Negligence Violations",
    }

    labels = [display_names.get(d["feature"], d["feature"].replace("_", " ").title()) for d in drivers]
    values = [d["shap_value"] * 100.0 for d in drivers] # express in percentage impact points

    colors = ["#EF4444" if v > 0 else "#10B981" for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in values],
        textposition="outside",
    ))

    fig.update_layout(
        title=f"<b>Key Risk Drivers for {mine_name}</b> (Predicted Risk: {calibrated_prob*100:.1f}%)",
        xaxis_title="Marginal Contribution to Next-Quarter Risk Probability (%)",
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        margin=dict(l=20, r=40, t=50, b=40),
        height=380,
    )
    return fig


def build_geospatial_risk_map(panel_df: pd.DataFrame) -> go.Figure:
    """Creates a high-performance US geographic scatter map of mine risk tiers."""
    df = panel_df.copy()
    
    # Map tier color
    color_map = {
        "Low": "#10B981",
        "Moderate": "#F59E0B",
        "Elevated": "#F97316",
        "Critical": "#EF4444",
    }

    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        color="risk_tier",
        color_discrete_map=color_map,
        size="hours_worked_q0",
        size_max=18,
        hover_name="mine_name",
        hover_data={
            "latitude": False,
            "longitude": False,
            "state": True,
            "risk_score_pct": ":.1f%",
            "risk_tier": True,
            "hours_worked_q0": ":,.0f",
            "coal_metal_ind": True,
            "mine_type": True,
        },
        scope="usa",
        title="<b>National Mine-Quarter Risk Surveillance Map (US MSHA)</b>",
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(
            title="Next-Quarter Risk Tier",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        height=480,
    )
    return fig
