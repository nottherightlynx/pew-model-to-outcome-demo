"""Mobile-first, one-scroll demonstration of the candidate's optimization model.

Run inside pew-model-to-outcome-demo: python -m streamlit run app_v2.py

DESIGN: all selection and content live in one vertical reading order; no hover-only facts.
ACCESSIBILITY: native labeled controls, real headings, alt chart + equivalent text/table.
SECURITY: local bounded fixtures; no unsafe HTML, URL fetches, tokens or API calls.
SCALE: portfolio configs are the extension point; no platform names hard-coded in UI.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pandas as pd
import streamlit as st

from analytics_contract_v2 import load_aggregate_metrics, numeric_summary, safe_csv_export
from model_v2 import FACTORS, FACTOR_NAMES, FACTOR_PLAIN, FACTOR_TECH, score_portfolio_platform
from recommendations_v2 import prioritized_actions
from rule_review_v2 import demo_proposals
from scoring import calculate_score, normalize_weights
from validation_v2 import MAX_HTML_BYTES, load_observations, load_portfolios, read_local_file

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Content optimization model | Independent demo", page_icon="🔎", layout="centered", initial_sidebar_state="collapsed")


def _chart(df: pd.DataFrame, x: str, y: str, alt: str, height: int = 270):
    """Native responsive chart; tolerate older installed Streamlit alt-signature versions."""
    kwargs = {"x": x, "y": y, "height": height}
    try:
        params = inspect.signature(st.bar_chart).parameters
        if "alt" in params:
            kwargs["alt"] = alt
        if "width" in params:
            kwargs["width"] = "stretch"
        elif "use_container_width" in params:
            kwargs["use_container_width"] = True
    except (ValueError, TypeError):
        pass
    st.bar_chart(df, **kwargs)


def _explanation_choice() -> str:
    """Native controls preserve keyboard/focus behaviors; never hide labels."""
    if hasattr(st, "segmented_control"):
        chosen = st.segmented_control(
            "Explanation for", options=["Non-technical", "Technical"],
            default="Non-technical", key="explanation_level",
        )
        return chosen or "Non-technical"
    return st.radio("Explanation for", ["Non-technical", "Technical"],
                    horizontal=True, key="explanation_level")


def _status_message(score: float | None) -> str:
    if score is None:
        return "There is not enough observed/configured information for a score."
    if score < 45:
        return "Several conditions need attention before we prioritize where to distribute this content."
    if score < 70:
        return "The model found workable conditions and some gaps worth addressing first."
    return "The content meets more of the model's configured conditions; this is not a visibility guarantee."


def _factor_rows(result: dict, weights: dict) -> list[dict]:
    normalized = normalize_weights(weights)
    return [
        {"Condition": FACTOR_NAMES[k],
         "Input / 100": None if result["components"].get(k) is None else round(result["components"][k] * 100),
         "Configured weight": f"{normalized[k]:.0%}",
         "Evidence source": result["provenance"][k]}
        for k in FACTORS
    ]


def _rule_summary(cfg: dict, result: dict) -> str:
    arr = prioritized_actions(cfg, result)
    if not arr:
        return "No automatic recommendation fired. A reviewer should still check whether the content meets the intended audience's needs."
    return arr[0]["next_action"]


# Streamlit reruns on user changes. Keep all I/O bounded and local.
st.title("Adaptive content optimization")
st.caption("Independent candidate demonstration · not affiliated with Pew · all engagement observations are synthetic")
st.write("The model checks the **audience, independent conversations, content language, technical setup and platform format**. It then shows what needs to change and how we would check whether the change worked.")

try:
    portfolios = load_portfolios(ROOT)
except (ValueError, OSError, UnicodeError) as exc:
    st.error(f"The local portfolio files need attention: {exc}")
    st.stop()

# MOBILE-FIRST: controls appear where the reading starts, not in a collapsed sidebar.
portfolio_id = st.selectbox("Research portfolio", list(portfolios),
                            format_func=lambda pid: portfolios[pid]["portfolio_label"])
cfg = portfolios[portfolio_id]
selected = st.selectbox("Platform to focus on", list(cfg["platforms"]))
mode = _explanation_choice()
technical = mode == "Technical"
st.caption(f"Audience: {cfg['audience']}")
st.caption(f"Goal: {cfg['objective']}")

try:
    html = read_local_file(ROOT, cfg["asset"], "data", MAX_HTML_BYTES)
    observations = load_observations(ROOT, portfolio_id)
    results = {
        name: score_portfolio_platform(html, cfg, name, observations.get(name, {}))
        for name in cfg["platforms"]
    }
    owned_metrics = load_aggregate_metrics(ROOT)
except (ValueError, OSError, UnicodeError) as exc:
    st.error(f"The local demonstration data could not be used safely: {exc}")
    st.stop()

focus = results[selected]
st.info("The numbers below are an **illustrative diagnostic**, not actual Pew performance, an AI citation rate, or a prediction of a platform's ranking algorithm.")

st.header("1. The logic behind the formula")
if technical:
    st.latex(r"\mathrm{AVS}_{p}=100\frac{\sum_{i\in K_p} w_i x_{i,p}}{\sum_{i\in K_p} w_i}")
    st.write("For each platform, the engine calculates five inputs from 0 to 1, then applies weights chosen for that portfolio. **x** is the condition score, **w** is how much importance the portfolio assigns it, and **K** means we only include inputs that have a value. Missing inputs are reported separately.")
    st.write("The formula is a **working diagnostic**. The weights have not been learned from actual engagement results, and platform ranking formulas are not available to us.")
    st.write("For AI-assisted search, Google says the core SEO practices still matter: accessible content, helpful original information, honest metadata, and useful visual context. No special schema or volume of organic mentions guarantees inclusion.")
else:
    st.write("The same content can work differently for different people and platforms. This is why the engine doesn't use one SEO checklist for everything.")
    st.write("The score combines five checks. It helps us find gaps and decide what to change first. A higher score means **better alignment with our own model**, not proof of better search results or more engagement.")
    st.write("It's the right mix of natural language and accurate sector terms, a webpage people can actually use, and the format that works for the audience—not just adding tags or repeating phrases.")

for i, factor in enumerate(FACTORS, 1):
    st.markdown(f"**{i}. {FACTOR_NAMES[factor]}**")
    st.write(FACTOR_TECH[factor] if technical else FACTOR_PLAIN[factor])

st.header("2. Compare the platforms")
platform_data = pd.DataFrame([
    {"Platform": name, "Diagnostic score": round(res["score"], 1) if res["score"] is not None else None}
    for name, res in results.items()
])
_chart(platform_data.dropna(), "Platform", "Diagnostic score",
       "Comparison of hypothetical optimization diagnostic scores by configured platform")
st.caption("These are scores produced by the candidate's five-factor formula, using synthetic observations and configured assumptions.")
for row in platform_data.to_dict("records"):
    st.write(f"**{row['Platform']}:** " + ("not enough data" if row['Diagnostic score'] is None else f"{row['Diagnostic score']:.1f} out of 100"))

if technical:
    with st.expander("See exactly where the platform scores come from", expanded=False):
        for name, result in results.items():
            st.markdown(f"**{name}**")
            st.dataframe(pd.DataFrame(_factor_rows(result, cfg["weights"])), hide_index=True)
            st.caption(f"Configured/observed factor coverage: {100 * result['coverage']:.0f}%. Coverage is NOT empirical measurement quality.")
else:
    st.write("**The point of the comparison:** the engine is not telling every portfolio to use the same platform or the same content format. It shows where this audience-content combination has the most gaps.")

st.header(f"3. What this means for {selected}")
score = focus["score"]
st.metric("Illustrative optimization diagnostic", "Not available" if score is None else f"{score:.1f} / 100")
st.write(_status_message(score))
if not focus["eligible_for_search"]:
    st.warning("This HTML fixture includes 'noindex'. Search eligibility should be reviewed before treating its score as an organic search opportunity.")
if focus["coverage"] < .999:
    st.warning(f"Some factors are missing. Data coverage is {focus['coverage']:.0%}; don't compare this score to fully populated assets without reviewing the missing sources.")

st.markdown("**The five inputs for this platform**")
for row in _factor_rows(focus, cfg["weights"]):
    number = row["Input / 100"]
    if technical:
        st.write(f"**{row['Condition']}:** {number if number is not None else 'missing'}/100; weight {row['Configured weight']}. {row['Evidence source']}.")
    else:
        st.write(f"**{row['Condition']}:** {number if number is not None else 'missing'}/100. "
                 + FACTOR_PLAIN[FACTORS[list(FACTOR_NAMES.values()).index(row["Condition"])]])

st.header("4. What needs to change")
actions = prioritized_actions(cfg, focus)
if not actions:
    st.write("Nothing crossed the demo's current recommendation thresholds. A human review is still needed.")
else:
    for i, action in enumerate(actions[:8], 1):
        st.markdown(f"**{i}. {action['next_action']}**")
        st.write("**Why:** " + action["why"])
        if technical:
            st.caption(f"Factor: {action['factor']} · Scenario priority: {action['priority']:.1f} · Review: {action['approval']}")
            st.caption("Evidence/reference: " + action["source"])
            st.caption("Limit: " + action["caution"])
        else:
            st.caption("A communications or research reviewer decides whether the change is right for this content.")

if technical:
    exported = safe_csv_export(actions)
    if exported:
        st.download_button("Export the review queue as CSV", exported,
                           file_name="candidate_optimization_review_queue.csv", mime="text/csv")

st.header("5. What if we fix one gap?")
choices = [k for k in FACTORS if focus["components"].get(k) is not None]
if choices:
    condition = st.selectbox("Condition to explore", choices, format_func=lambda k: FACTOR_NAMES[k])
    old = focus["components"][condition]
    candidate = st.slider("Illustrative level after an approved change", min_value=0, max_value=100,
                          value=round(old * 100), step=1)
    altered = dict(focus["components"])
    altered[condition] = candidate / 100
    projected = calculate_score(altered, cfg["weights"])
    if projected["score"] is not None and score is not None:
        diff = projected["score"] - score
        st.metric("Scenario diagnostic after the change", f"{projected['score']:.1f} / 100", delta=f"{diff:+.1f} diagnostic points")
    if technical:
        st.write(f"Only the **{FACTOR_NAMES[condition]}** input changed from {old:.2f} to {candidate/100:.2f}. Other inputs and weights stayed the same. That makes this a sensitivity calculation—not an estimate of real search lift.")
    else:
        st.write("This slider shows how the formula responds when one condition improves. Whether real people find or use the content more often still has to be tested.")

st.header("6. How we would know it worked")
st.write("After someone approves an edit, we compare actual performance against a fair baseline and keep track of what changed. The demo is not connected to anyone's live analytics.")
metrics = numeric_summary(owned_metrics, portfolio_id, selected)
if metrics:
    st.markdown("**Synthetic example of an aggregate measurement export**")
    metric_table = pd.DataFrame(metrics)
    st.dataframe(metric_table, hide_index=True)
else:
    st.caption("No synthetic measurement rows were provided for this platform. This is missing data, not zero engagement.")
if technical:
    st.write("An authorized implementation could map **Google Analytics** aggregate metrics, tag definitions managed through **Google Tag Manager** if confirmed, and **Facebook Insights** data where available. Google Search Console is a potential SEO integration, not a confirmed Pew deployment. Keep impressions, sessions and engagements separate by source and time period; do not blend them into invented causal lift.")
    st.write("SQL/dbt-style transformations should test unique asset IDs, source names, date windows, data ranges and documented denominators before comparing variants.")
else:
    st.write("The numbers should answer whether the intended audience actually responded better. An improved formula score by itself is not the result we're trying to produce.")

st.header("7. Keep the strategy current without making silent changes")
st.write("Official documentation changes are useful inputs, but they do not automatically tell us a platform has changed its ranking algorithm.")
for proposal in demo_proposals():
    st.markdown(f"**{proposal.source_title}**")
    st.write(proposal.review_question)
    st.caption(proposal.status + " · " + proposal.research_note)
    if technical:
        st.caption("Affected component: " + proposal.affected_module)
    st.markdown(f"[Read the official documentation]({proposal.source_url})")

with st.expander("Source use, accessibility and model limits", expanded=False):
    st.write("No real Pew performance or internal records are included. The candidate app reads only local fixtures and synthetic aggregate data. It does not scrape social networks, call cloud LLMs, identify individual users, modify websites, or publish changes.")
    st.write("The demo checks some HTML properties, but it is not a full accessibility certification, a rich-result validator, or an AI citation measurement service.")
    st.markdown("Official sources: [Google AI search guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) · [Google image guidance](https://developers.google.com/search/docs/appearance/google-images) · [OpenAI crawlers](https://developers.openai.com/api/docs/bots) · [WCAG 2.2](https://www.w3.org/TR/WCAG22/) · [Streamlit design](https://docs.streamlit.io/develop/concepts/design/best-practices)")
