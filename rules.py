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
