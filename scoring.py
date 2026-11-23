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
