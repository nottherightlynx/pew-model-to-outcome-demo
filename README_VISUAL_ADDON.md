# Responsive, single-scroll formula visualizer

Adds a visual explanation to the existing Pew model-to-outcome Streamlit prototype without replacing its calculations or datasets.

## Install in Terminal opened inside `pew-model-to-outcome-demo`

1. Download **Pew_Streamlit_Visual_Addon.zip** from the response.
2. In your existing project folder, run:

```bash
unzip -o ~/Downloads/Pew_Streamlit_Visual_Addon.zip -d .
source .venv/bin/activate
python install_visual_explainer.py
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The installer backs up `app.py`, replaces its presentation-only section with the new responsive page, and appends `plotly` to `requirements.txt`. It does not overwrite your `scoring.py`, `rules.py`, YAML files or datasets. If your app has changed substantially, installation halts safely without writing. The import is `from visual_explainer import render_visual_explainer`.

## Page behavior

- Responsive, **one vertically scrolling page** without tabs or expanders
- Portfolio picker and selected platform remain in your existing sidebar
- **Technical / Non-technical** radio switches explanations throughout the page
- Dynamic five-factor flow diagram, weighted contributions for every configured platform, and platform-factor heatmap
- Per-platform recommended content changes, configuration-dependent format advice, and coverage
- What-if slider demonstrates how changing one modeled condition affects the synthetic score (not observed uplift)
- A plain-language or technical evaluation-and-governance explanation
- Uses only local fixture data and synthetic CSV observations. It does not scrape live platforms or create LLM calls.

## Technical caveats

Existing `scoring.py` uses manually configured weights; the values are illustrative and not measured platform ranking effects. The organic co-occurrence values are synthetic. A scenario score increase is not predicted traffic lift. Charts automatically include new platforms once they are added to both portfolio YAML `platforms` and matching CSV observations.
