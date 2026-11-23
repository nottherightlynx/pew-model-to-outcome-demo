"""Run once from inside pew-model-to-outcome-demo: python install_visual_explainer.py

Makes a timestamped backup of app.py and swaps only the presentation layer.
It preserves your scoring.py, rules.py, configs, fixtures, and tests.
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

root = Path.cwd()
app = root / "app.py"
visual = root / "visual_explainer.py"
if not all((app.exists(), visual.exists(), (root / "scoring.py").exists(), (root / "rules.py").exists())):
    raise SystemExit("Run this inside pew-model-to-outcome-demo after placing visual_explainer.py here.")
source = app.read_text(encoding="utf-8")
if "render_visual_explainer(config, html, load_observation" in source:
    print("Visual explainer already installed; no changes made.")
    raise SystemExit(0)
anchor = 'st.subheader(config["portfolio_label"])'
if anchor not in source:
    raise SystemExit("Cannot find the expected original display section. No files changed. Edit app.py manually using the instructions.")
if "from visual_explainer import render_visual_explainer" not in source:
    source = source.replace('from scoring import score_asset', 'from scoring import score_asset\nfrom visual_explainer import render_visual_explainer', 1)
    if "from visual_explainer import render_visual_explainer" not in source:
        raise SystemExit("Cannot find expected import anchor; no files changed.")
source = source[:source.index(anchor)] + '''html = (ROOT / config["asset"]).read_text(encoding="utf-8")
render_visual_explainer(config, html, load_observation, selected_platform=platform)
'''
compile(source, str(app), "exec")
backup = root / f"app.py.backup_{datetime.now():%Y%m%d_%H%M%S}"
shutil.copy2(app, backup)
app.write_text(source, encoding="utf-8")
requirements = root / "requirements.txt"
if requirements.exists():
    req = requirements.read_text(encoding="utf-8")
    if not any(line.strip().lower().startswith("plotly") for line in req.splitlines()):
        requirements.write_text(req.rstrip() + "\nplotly>=5.20,<7\n", encoding="utf-8")
print(f"Installed successfully. Backup: {backup.name}")
print("Next: python -m pip install plotly && python -m streamlit run app.py")
