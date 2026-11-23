"""Local model-to-outcome demo: streamlit run app.py"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import streamlit as st
import yaml

from rules import documentation_change_proposal, generate_recommendations
from scoring import score_asset
from visual_explainer import render_visual_explainer

ROOT = Path(__file__).resolve().parent


def load_config(portfolio: str) -> dict:
    with (ROOT / "config" / f"{portfolio}.yml").open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_observation(portfolio: str, platform: str) -> dict:
    with (ROOT / "data" / "synthetic_observations.csv").open(newline="", encoding="utf-8") as handle:
        for item in csv.DictReader(handle):
            if item["portfolio_id"] == portfolio and item["platform"] == platform:
                return {
                    "organic_mentions": int(item["organic_mentions"]),
                    "qualified_mentions": int(item["qualified_mentions"]),
                    "format_fit": float(item["format_fit"]),
                    "measurement_note": item["measurement_note"],
                }
    return {}


st.set_page_config(page_title="Model-to-Outcome Optimizer | Unofficial Demo", layout="wide")
st.title("Adaptive Cross-Platform Content Optimizer")
st.caption("Independent candidate prototype • not affiliated with or endorsed by Pew • all performance observations are synthetic")

portfolio = st.sidebar.selectbox(
    "Portfolio", ["state_policy", "marine_management"],
    format_func=lambda p: {"state_policy": "State Fiscal Policy", "marine_management": "Marine Management"}[p],
)
config = load_config(portfolio)
platform = st.sidebar.selectbox("Audience platform", list(config["platforms"]))

html = (ROOT / config["asset"]).read_text(encoding="utf-8")
render_visual_explainer(config, html, load_observation, selected_platform=platform)
