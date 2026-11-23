#!/usr/bin/env bash
set -euo pipefail

# Run from inside pew-model-to-outcome-demo.
# Set OVERWRITE=1 to replace generated files if you intentionally rerun.
if [[ "$(basename "$PWD")" != "pew-model-to-outcome-demo" ]]; then
  echo "ERROR: Open Terminal inside the pew-model-to-outcome-demo folder first." >&2
  echo "Current directory: $PWD" >&2
  exit 1
fi

mkdir -p config data docs tests
files=(
  app.py scoring.py rules.py
  config/state_policy.yml config/marine_management.yml
  data/state_policy_fixture.html data/marine_fixture.html
  data/synthetic_observations.csv data/source_register.csv
  tests/test_optimizer.py docs/score_methodology.md docs/disclaimer.md
  requirements.txt
)
if [[ "${OVERWRITE:-0}" != "1" ]]; then
  for file in "${files[@]}"; do
    if [[ -e "$file" ]]; then
      echo "STOP: $file already exists. Existing work was not overwritten." >&2
      echo "To replace the generated files intentionally, run OVERWRITE=1 bash create_pew_model_demo.sh" >&2
      exit 1
    fi
  done
fi

cat > requirements.txt <<'EOF'
streamlit>=1.38,<2
pandas>=2.0,<3
PyYAML>=6.0,<7
beautifulsoup4>=4.12,<5
pytest>=8.0,<10
EOF

cat > config/state_policy.yml <<'EOF'
portfolio_id: state_policy
portfolio_label: State Fiscal Policy — illustrative demo
asset: data/state_policy_fixture.html
audience: State fiscal analysts, legislative staff, and policy journalists
objective: Improve qualified discoverability of fiscal research while retaining precise definitions.
priority_terms:
  - state budget
  - fiscal sustainability
  - budget stabilization fund
  - rainy day fund
platforms:
  LinkedIn:
    audience_fit: 0.90
    default_format_fit: 0.48
    desired_format: "a 5-card, source-linked PDF carousel for analysts"
  Search:
    audience_fit: 0.95
    default_format_fit: 0.78
    desired_format: "an accessible HTML explainer with clear question-based headings"
  YouTube:
    audience_fit: 0.35
    default_format_fit: 0.25
    desired_format: "a short captioned explainer with an immediate question-led opening"
weights:
  audience: 0.20
  cooccurrence: 0.18
  semantic: 0.24
  technical: 0.23
  format: 0.15
mission_value: 1.0
EOF

cat > config/marine_management.yml <<'EOF'
portfolio_id: marine_management
portfolio_label: Marine Management — illustrative demo
asset: data/marine_fixture.html
audience: Marine scientists, conservation practitioners, and environmental journalists
objective: Improve the retrievability and usability of marine management research and visual assets.
priority_terms:
  - marine protected areas
  - fisheries management
  - habitat monitoring
  - marine biodiversity
platforms:
  LinkedIn:
    audience_fit: 0.65
    default_format_fit: 0.45
    desired_format: "an expert-oriented graphic with a linked methodology"
  Search:
    audience_fit: 0.90
    default_format_fit: 0.55
    desired_format: "a searchable map explanation with accessible text equivalents"
  YouTube:
    audience_fit: 0.80
    default_format_fit: 0.40
    desired_format: "a captioned 60-second visual explainer with citations"
weights:
  audience: 0.17
  cooccurrence: 0.20
  semantic: 0.24
  technical: 0.19
  format: 0.20
mission_value: 1.0
EOF

cat > data/state_policy_fixture.html <<'EOF'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>State Fiscal Trends | Demo Fixture</title></head>
<body>
  <main>
    <h1>New Data on State Finances</h1>
    <p>This example explores state budget decisions and fiscal sustainability across changing economic conditions.</p>
    <h2>Why does this matter?</h2>
    <p>Analysts may compare state budget strategies, but definitions vary among states.</p>
    <img src="demo-chart.png" alt="">
    <p><a href="https://www.pew.org/">Illustrative source organization homepage</a></p>
  </main>
</body></html>
EOF

cat > data/marine_fixture.html <<'EOF'
<!doctype html>
<html lang="en"><head>
  <meta charset="utf-8"><title>Marine Management | Demo Fixture</title>
  <meta name="description" content="Illustrative summary of marine management research and habitat monitoring.">
  <link rel="canonical" href="https://example.org/demo/marine-management">
</head><body>
  <main>
    <h1>Marine Protected Areas and Fisheries Management</h1>
    <p>Marine protected areas can intersect with fisheries management and marine biodiversity goals.</p>
    <h2>Mapping management conditions</h2>
    <p>The demo map presents habitat monitoring observations; its data are fictional and not Pew findings.</p>
    <img src="demo-map.png" alt="Illustrative map showing three fictional habitat monitoring zones">
    <p>See the <a href="https://www.pew.org/">research institution's public homepage</a> for actual published work.</p>
  </main>
</body></html>
EOF

cat > data/synthetic_observations.csv <<'EOF'
portfolio_id,platform,organic_mentions,qualified_mentions,format_fit,measurement_note
state_policy,LinkedIn,6,2,0.48,Entire row is synthetic; not LinkedIn or Pew performance data
state_policy,Search,10,5,0.78,Entire row is synthetic; not search engine or Pew performance data
state_policy,YouTube,2,0,0.25,Entire row is synthetic; not YouTube or Pew performance data
marine_management,LinkedIn,5,2,0.45,Entire row is synthetic; not LinkedIn or Pew performance data
marine_management,Search,8,4,0.55,Entire row is synthetic; not search engine or Pew performance data
marine_management,YouTube,12,8,0.40,Entire row is synthetic; not YouTube or Pew performance data
EOF

cat > data/source_register.csv <<'EOF'
source_id,source_type,location,rights_or_basis,role,real_or_synthetic
fixture_state,local_fixture,data/state_policy_fixture.html,Created for candidate demo,HTML structural audit,synthetic
fixture_marine,local_fixture,data/marine_fixture.html,Created for candidate demo,HTML structural audit,synthetic
sample_observations,local_fixture,data/synthetic_observations.csv,Created for candidate demo,Platform observation scenario,synthetic
pew_homepage,official_website,https://www.pew.org/,Public website linked for context only,Institutional reference; not scraped,real
schema_org,technical_documentation,https://schema.org/,Public standards documentation,Metadata research reference,real
w3c_wcag,technical_documentation,https://www.w3.org/TR/WCAG22/,Public standard,Accessibility validation reference,real
search_central,technical_documentation,https://developers.google.com/search/docs,Public documentation,Search and structured data guidance,real
EOF

cat > scoring.py <<'EOF'
"""Transparent scenario scoring for the Pew model-to-outcome demo.

This is an illustrative *optimization diagnostic*, NOT a prediction of
traffic, an algorithm ranking, or the probability of AI citation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

COMPONENTS = ("audience", "cooccurrence", "semantic", "technical", "format")


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    if set(weights) != set(COMPONENTS):
        raise ValueError(f"Weights must include exactly: {', '.join(COMPONENTS)}")
    if any(float(v) < 0 for v in weights.values()):
        raise ValueError("Weights cannot be negative")
    total = sum(float(v) for v in weights.values())
    if total <= 0:
        raise ValueError("At least one weight must be positive")
    return {key: float(weights[key]) / total for key in COMPONENTS}


def parse_html(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body or soup
    text = " ".join(body.stripped_strings)
    images = soup.find_all("img")
    h1 = soup.find_all("h1")
    h2 = soup.find_all("h2")
    meta_desc = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    canonical = soup.find("link", attrs={"rel": lambda value: value and "canonical" in value})
    jsonld = soup.find_all("script", attrs={"type": "application/ld+json"})
    return {
        "visible_text": text,
        "h1_count": len(h1),
        "h2_count": len(h2),
        "has_meta_description": bool(meta_desc and meta_desc.get("content", "").strip()),
        "has_canonical": bool(canonical and canonical.get("href")),
        "has_jsonld": bool(jsonld),
        "images_total": len(images),
        "images_with_alt": sum(bool((img.get("alt") or "").strip()) for img in images),
    }


def semantic_coverage(content: dict[str, Any], terms: list[str]) -> tuple[float, list[str]]:
    if not terms:
        return 0.0, []
    text = " ".join(content["visible_text"].lower().split())
    missing = [term for term in terms if " ".join(term.lower().split()) not in text]
    return clamp01((len(terms) - len(missing)) / len(terms)), missing


def technical_readiness(content: dict[str, Any]) -> tuple[float, list[str]]:
    """Checks are observable page properties, not ranking-factor claims."""
    checks = {
        "one_h1": content["h1_count"] == 1,
        "has_subheadings": content["h2_count"] >= 1,
        "meta_description": content["has_meta_description"],
        "canonical": content["has_canonical"],
        "image_alternatives": content["images_total"] == content["images_with_alt"],
        "extractable_body": len(content["visible_text"].split()) >= 20,
    }
    # JSON-LD is flagged as an optional, context-dependent recommendation;
    # it is not universally required or evidence of improved AI ranking.
    missing = [name for name, passes in checks.items() if not passes]
    return sum(checks.values()) / len(checks), missing


def organic_cooccurrence_proxy(mentions: int | None, qualified: int | None) -> float | None:
    """Synthetic demo proxy: coverage × relevance; not a platform algorithm signal."""
    if mentions is None or qualified is None:
        return None
    mentions = int(mentions)
    qualified = int(qualified)
    if mentions < 0 or qualified < 0 or qualified > mentions:
        raise ValueError("Invalid organic mention counts")
    if mentions == 0:
        return 0.0
    coverage = min(mentions / 20, 1.0)  # 20 is a documented DEMO scenario threshold.
    relevance = qualified / mentions
    return round(coverage * relevance, 4)


def calculate_score(components: dict[str, float | None], weights: dict[str, float]) -> dict[str, Any]:
    """Missing dimensions are omitted and coverage is reported separately."""
    normalized = normalize_weights(weights)
    available = {k: clamp01(v) for k, v in components.items() if k in normalized and v is not None}
    denom = sum(normalized[k] for k in available)
    if denom <= 0:
        return {"score": None, "coverage": 0.0, "components": available}
    score = sum(available[k] * normalized[k] for k in available) / denom
    return {
        "score": round(score * 100, 1),
        "coverage": round(denom, 3),
        "components": {k: round(v, 3) for k, v in available.items()},
        "weight_version": "demo-1.0",
    }


def score_asset(html: str, config: dict[str, Any], platform: str, observation: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_html(html)
    semantic, missing_terms = semantic_coverage(parsed, config["priority_terms"])
    technical, technical_gaps = technical_readiness(parsed)
    platform_config = config["platforms"][platform]
    cooccurrence = organic_cooccurrence_proxy(
        observation.get("organic_mentions"), observation.get("qualified_mentions")
    )
    components = {
        "audience": clamp01(platform_config["audience_fit"]),
        "cooccurrence": cooccurrence,
        "semantic": semantic,
        "technical": technical,
        "format": clamp01(observation.get("format_fit", platform_config["default_format_fit"])),
    }
    result = calculate_score(components, config["weights"])
    result.update({
        "missing_terms": missing_terms,
        "technical_gaps": technical_gaps,
        "parsed": parsed,
        "platform": platform,
        "portfolio_id": config["portfolio_id"],
        "score_label": "Illustrative AI visibility / optimization readiness index",
        "warning": "Synthetic observations and uncalibrated weights; not observed Pew performance.",
    })
    return result
EOF

cat > rules.py <<'EOF'
"""Generate auditable, prescriptive content optimization recommendations."""
from __future__ import annotations

from typing import Any


EFFORT_HOURS = {
    "semantic": 1.5,
    "technical": 1.0,
    "format": 2.0,
    "cooccurrence": 3.0,
    "audience": 2.0,
}


def generate_recommendations(config: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    platform = result["platform"]
    components = result["components"]
    recommendations: list[dict[str, Any]] = []

    def add(dimension: str, action: str, evidence: str, caution: str) -> None:
        observed = components.get(dimension)
        if observed is None:
            return
        gap = max(0.0, 1.0 - float(observed))
        weight = float(config["weights"][dimension])
        effort = EFFORT_HOURS[dimension]
        # Scenario priority only. Not predicted traffic/engagement lift.
        priority = round(100 * gap * weight * float(config.get("mission_value", 1.0)) / effort, 2)
        recommendations.append({
            "dimension": dimension,
            "action": action,
            "evidence": evidence,
            "illustrative_priority": priority,
            "effort_hours_assumed": effort,
            "caution": caution,
            "approval": "Editorial and subject-matter approval required",
        })

    missing = result["missing_terms"]
    if missing:
        add(
            "semantic",
            "Add a concise, properly sourced plain-language section defining "
            + ", ".join(missing[:3])
            + "; preserve accurate domain terminology and do not insert claims unsupported by the source.",
            "Priority concepts absent from visible HTML: " + ", ".join(missing),
            "Term coverage is a proxy for audience-query alignment, not a ranking guarantee.",
        )
    gaps = result["technical_gaps"]
    if gaps:
        fixes = []
        if "meta_description" in gaps:
            fixes.append("write a factual, audience-oriented meta description")
        if "canonical" in gaps:
            fixes.append("review canonical URL")
        if "image_alternatives" in gaps:
            fixes.append("write meaningful image alternatives and data-equivalent descriptions")
        if "one_h1" in gaps:
            fixes.append("use one clear H1")
        if "extractable_body" in gaps:
            fixes.append("add an accessible HTML finding summary")
        if "has_subheadings" in gaps:
            fixes.append("add descriptive H2 sections")
        add("technical", "; ".join(fixes).capitalize() + ".", "Failed checks: " + ", ".join(gaps),
            "Technical checks verify page properties; they do not prove platform rankings.")
    if components.get("format", 1) < 0.75:
        add(
            "format",
            "Prepare " + config["platforms"][platform]["desired_format"]
            + ", keeping claims, dates, visuals and methodological caveats faithful to the source.",
            f"Illustrative platform-format fit: {components['format']:.2f}",
            "A/B test the adaptation on the selected channel; platform ranking effects are not assumed.",
        )
    if components.get("cooccurrence", 1) < 0.30:
        add(
            "cooccurrence",
            "Identify legitimate existing conversations and independent information needs; offer a reusable source-linked chart or explainer through normal editorial channels.",
            f"Synthetic qualified co-occurrence proxy: {components['cooccurrence']:.2f}",
            "Do not manufacture mentions, incentivize endorsements, or scrape restricted platforms.",
        )
    if components.get("audience", 1) < 0.60:
        add(
            "audience",
            f"Reconsider whether {platform} should be a priority channel for {config['audience']}; test a better-matched channel before producing new assets.",
            f"Illustrative audience-platform fit: {components['audience']:.2f}",
            "Platform fit is a configured hypothesis; validate it with permitted analytics or audience research.",
        )
    return sorted(recommendations, key=lambda r: r["illustrative_priority"], reverse=True)


def documentation_change_proposal(source_url: str, change_summary: str) -> dict[str, str]:
    """Documentation updates never automatically alter weights or publication."""
    return {
        "source": source_url,
        "summary": change_summary,
        "status": "PROPOSED — requires source verification, regression tests and human approval",
        "action": "Review affected rules; document rationale and version before release.",
    }
EOF

cat > app.py <<'EOF'
"""Local model-to-outcome demo: streamlit run app.py"""
from __future__ import annotations

import csv
from pathlib import Path

import streamlit as st
import yaml

from rules import documentation_change_proposal, generate_recommendations
from scoring import score_asset

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

st.subheader(config["portfolio_label"])
st.write("**Target audience:**", config["audience"])
st.write("**Optimization objective:**", config["objective"])

html_path = ROOT / config["asset"]
html = html_path.read_text(encoding="utf-8")
obs = load_observation(portfolio, platform)
result = score_asset(html, config, platform, obs)
recommendations = generate_recommendations(config, result)

left, middle, right = st.columns(3)
left.metric("Illustrative diagnostic score", f"{result['score']:.1f} / 100")
middle.metric("Data dimension coverage", f"{result['coverage'] * 100:.0f}%")
right.metric("Ranked optimization actions", len(recommendations))
st.warning(result["warning"])

with st.expander("1. Model inputs and components", expanded=True):
    labels = {
        "audience": "Audience-platform fit",
        "cooccurrence": "Organic co-occurrence proxy",
        "semantic": "Semantic/entity term coverage",
        "technical": "Technical page readiness",
        "format": "Platform-format fit",
    }
    for key, val in result["components"].items():
        st.write(f"**{labels[key]}:** {val:.2f}  | configured weight: {config['weights'][key]:.0%}")
    st.caption("Scores represent diagnostic conditions; no lift or ranking improvement is claimed.")

st.subheader("2. Recommended changes, ranked by scenario priority")
if recommendations:
    for index, rec in enumerate(recommendations, 1):
        with st.container(border=True):
            st.markdown(f"**{index}. {rec['dimension'].title()} — scenario priority {rec['illustrative_priority']}**")
            st.write(rec["action"])
            st.caption("Evidence: " + rec["evidence"])
            st.caption("Assumed work: " + str(rec["effort_hours_assumed"]) + " hours | " + rec["approval"])
            st.caption("Limit: " + rec["caution"])
else:
    st.info("No rule thresholds triggered; review source quality before publishing.")

st.subheader("3. Test the recommendation, not the algorithm myth")
st.markdown(
    """Choose one recommended change; record the original asset and an editorially approved variant.
    Pre-register a platform-specific primary measure (e.g. qualified click-through or attributable
    completion) and guardrails (accuracy, accessibility and negative feedback). Randomize when permitted;
    otherwise use repeated matched windows and disclose confounders. Do not equate score change with
    a percentage change in actual visibility."""
)
st.subheader("4. Documentation change review")
proposal = documentation_change_proposal(
    "https://developers.google.com/search/docs",
    "Example only: suppose documentation changes a structured-data eligibility requirement.",
)
st.json(proposal)
st.caption("No feed is being polled in this offline MVP; production feed monitoring needs source verification and approval.")

with st.expander("Source and licensing register"):
    st.dataframe(ROOT.joinpath("data/source_register.csv").read_text(encoding="utf-8"), use_container_width=True)
EOF

cat > tests/test_optimizer.py <<'EOF'
from pathlib import Path
import csv
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scoring import calculate_score, parse_html, score_asset, normalize_weights
from rules import generate_recommendations, documentation_change_proposal


def config_for(portfolio):
    return yaml.safe_load((ROOT / "config" / f"{portfolio}.yml").read_text(encoding="utf-8"))


def fixture_for(portfolio):
    config = config_for(portfolio)
    return (ROOT / config["asset"]).read_text(encoding="utf-8")


def test_weights_reject_invalid_values():
    with pytest.raises(ValueError):
        normalize_weights({"audience": -1, "cooccurrence": 1, "semantic": 1, "technical": 1, "format": 1})


def test_missing_dimension_is_not_zero():
    result = calculate_score(
        {"audience": 0.8, "cooccurrence": None, "semantic": 0.6, "technical": 0.6, "format": 0.5},
        {"audience": 0.2, "cooccurrence": 0.2, "semantic": 0.2, "technical": 0.2, "format": 0.2},
    )
    assert result["score"] == 62.5
    assert result["coverage"] == 0.8


def test_state_fixture_finds_technical_and_semantic_gaps():
    config = config_for("state_policy")
    result = score_asset(fixture_for("state_policy"), config, "LinkedIn",
                         {"organic_mentions": 6, "qualified_mentions": 2, "format_fit": 0.48})
    assert "meta_description" in result["technical_gaps"]
    assert "budget stabilization fund" in result["missing_terms"]
    recs = generate_recommendations(config, result)
    assert any(r["dimension"] == "technical" for r in recs)
    assert all(r["approval"] for r in recs)


def test_portfolios_have_different_optimization_outputs():
    state = config_for("state_policy")
    marine = config_for("marine_management")
    state_score = score_asset(fixture_for("state_policy"), state, "YouTube",
                              {"organic_mentions": 2, "qualified_mentions": 0, "format_fit": 0.25})
    marine_score = score_asset(fixture_for("marine_management"), marine, "YouTube",
                               {"organic_mentions": 12, "qualified_mentions": 8, "format_fit": 0.40})
    assert state_score["components"]["audience"] != marine_score["components"]["audience"]
    assert generate_recommendations(state, state_score) != generate_recommendations(marine, marine_score)


def test_official_change_cannot_auto_approve():
    proposal = documentation_change_proposal("https://schema.org/", "Illustrative update")
    assert proposal["status"].startswith("PROPOSED")
EOF

cat > docs/score_methodology.md <<'EOF'
# Score methodology — model-to-outcome candidate demo

## Purpose
The core invention proposed here is a **prescriptive, adaptive cross-platform content optimizer**, not a conventional dashboard. It analyzes the conditions under which a particular audience may discover and engage with a piece of content, surfaces gaps, recommends specific changes, and supports subsequent tests. The score is a routing aid for decisions, **not** a published algorithm score or prediction of traffic, ranking, citations, or impact.

## Five modeled dimensions

1. **Audience/platform fit (A):** the portfolio's assumed relative audience presence and information needs on each platform. Configured in YAML; must eventually be validated with audience research and permitted channel analytics.
2. **Organic third-party co-occurrence (C):** a *synthetic observation proxy* of independently originated conversation mentioning the relevant subject in credible contexts. Demo formula: `min(mentions / 20, 1) × (qualified_mentions / mentions)`, with zero when there are no mentions. The threshold of 20 is **arbitrary for demonstration**, not a ranking factor. Never manufacture conversation or scrape without authorization.
3. **Semantic/entity fit (S):** share of configured priority multiword terms present in visible page text. This is an intentionally simple recall proxy, not a semantic embedding or evidence of meaning/satisfaction. Future research should test phrase variants, embeddings and factual quality with human judgments.
4. **Technical readiness (T):** fraction of six deterministic checks passed (one H1, subheadings, a meta description, canonical URL, image alternatives, sufficient extractable HTML). Absence of any single check does not imply a search penalty. Structured data is inspected but not universally scored as a ranking factor.
5. **Platform-format fit (P):** an illustrative assumption about how well current packaging serves a platform and audience. For production, operationalize with controlled tests and platform-authorized analytics.

## Formula
For configured nonnegative weights `w_i` summing to one and normalized component values `x_i ∈ [0,1]`:

`DemoDiagnosticScore = 100 × Σ(w_i × x_i)`, only across observed dimensions; if a component is missing, the score renormalizes over available weights and separately publishes `coverage = Σ(available weights)`. **Missing is never silently zero.** No universal factor weights are asserted.

The original conversation's freshness multiplier was supplied by an earlier assistant and is not treated as an empirically validated determinant. Official RSS/documentation updates should instead trigger human-reviewed, versioned rule proposals and regression tests.

## Recommendation priority
`ScenarioPriority = 100 × gap × configured_weight × mission_value / assumed_effort_hours`.

This is an **illustrative gap-to-effort ordering**, not expected visibility lift. A production decision rule should separately estimate effect sizes and uncertainty, editorial/research risk, accessibility impact, and implementation effort from experimental evidence.

## Data provenance
The two HTML source fixtures and all channel observations are fabricated for testing. They are not copied from Pew and are not statements of Pew's actual digital performance. Public institutional/standard links in `source_register.csv` are context only. The app uses no live crawling, social media API, analytics account, or AI engine calls.

## Appropriate evaluation
Pre-register a portfolio-specific channel outcome (qualified search traffic, content engagement, video completion, audience-relevant citations when available), plus accuracy/accessibility guardrails. Test one intervention at a time where feasible; distinguish randomized experimental comparisons from observational before/after changes. Avoid causal claims where suitable controls are absent. Examine whether the combined model generates higher-value suggestions than independent technical/semantic/platform audits.

## Governance
All public-facing edits and rule updates require human approval. Only authorized APIs or licensed datasets should ever be ingested. Honor privacy, copyright, platform terms and nonpartisanship requirements; follow W3C WCAG 2.2 for accessibility review. Do not turn organic co-occurrence analysis into stealth promotion.
EOF

cat > docs/disclaimer.md <<'EOF'
# Independent candidate demonstration — disclosure

This is an **unofficial, independent candidate proof of concept**. It is not produced by, affiliated with, sponsored by or endorsed by The Pew Charitable Trusts or Pew Research Center.

- **All HTML test assets are synthetic.** They are not Pew articles and do not contain real Pew findings.
- **All engagement, off-site mention and channel-format observations are synthetic.** They do not represent real results for Pew or any platform.
- **Weights, thresholds, priority values and audience-fit estimates are illustrative hypotheses**, not empirically calibrated algorithmic rankings or forecasts of lift.
- **No data is scraped** or retrieved from platforms in this prototype. Public links serve attribution/context purposes only.
- **No optimization automatically publishes.** A subject-matter expert and editorial approver must review accuracy, nonpartisanship, accessibility, and context.
- **Source integrity:** preserve the meaning of policy findings, sample sizes, limitations and citations. The goal is discoverability and accessible engagement, not manufactured social proof or misleading clickbait.
- **Security/privacy:** never add API credentials or personally identifiable information to this repository; use a secret manager and approved access policies in any production implementation.
- **Provenance:** see `data/source_register.csv` and `docs/score_methodology.md`.
EOF

printf '\nCreated %s files in %s\n' "${#files[@]}" "$PWD"
printf '%s\n' 'Next commands:' '  python3 -m venv .venv' '  source .venv/bin/activate' '  python -m pip install -r requirements.txt' '  python -m pytest -q' '  streamlit run app.py'
