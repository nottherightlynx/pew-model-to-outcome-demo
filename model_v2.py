"""Apply the user's five-factor model without inventing platform ranking rules.

A = audience/platform alignment (portfolio hypothesis)
C = independent topic co-occurrence (synthetic scenario here)
S = visible semantic / entity coverage (bounded lexical diagnostic)
T = technically usable and accessible content (documented local checks)
P = channel-format alignment (portfolio hypothesis)

The diagnostic index is NOT predicted reach, traffic, citations or actual lift.
"""
from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

from scoring import calculate_score, organic_cooccurrence_proxy
from validation_v2 import finite_number
from seo_audit_v2 import Finding, analyze_html

FACTORS = ("audience", "cooccurrence", "semantic", "technical", "format")
FACTOR_NAMES = {
    "audience": "Audience and platform fit",
    "cooccurrence": "Independent conversations about the topic",
    "semantic": "Clear topic and entity language",
    "technical": "Technical and accessible content",
    "format": "Content format for this platform",
}
FACTOR_PLAIN = {
    "audience": "Is this where the people we need to reach are likely to look?",
    "cooccurrence": "Are people already talking about this issue outside our own channels?",
    "semantic": "Does the content answer the real question using accurate terms people recognize?",
    "technical": "Can the material be accessed and understood without relying on a hidden graphic or complicated page?",
    "format": "Is this the right way to present the material on this particular platform?",
}
FACTOR_TECH = {
    "audience": "Configured audience-channel fit; review it against authorized audience research and first-party engagement.",
    "cooccurrence": "Synthetic organic/qualified mention proxy; no ranking-factor claim or third-party scraping.",
    "semantic": "Ratio of configured, exact or normalized topic phrases in visible text; proxies semantic fit, not embeddings.",
    "technical": "Local HTML accessibility/extractability checks, without requiring schema or canonical on every page.",
    "format": "Configured format suitability; test approved native channel variants rather than assuming a platform penalty.",
}


def _visible_text(soup: BeautifulSoup) -> str:
    # No dangerous execution; source text is data, not instructions.
    main = soup.find("main") or soup.body or soup
    for elt in main.find_all(["script", "style", "template", "noscript"]):
        elt.decompose()
    return " ".join(main.stripped_strings)


def _term_in_text(text: str, term: str) -> bool:
    # Normalize hyphenation/whitespace. Exact topics may still miss synonyms.
    normalize = lambda x: " ".join(re.sub(r"[^\w]+", " ", x.casefold()).split())
    clean = normalize(text)
    needle = normalize(term)
    return bool(needle) and bool(re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", clean))


def semantic_proxy(html: str, priority_terms: list[str]) -> tuple[float, list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    text = _visible_text(soup)
    missing = [term for term in priority_terms if not _term_in_text(text, term)]
    return round((len(priority_terms) - len(missing)) / len(priority_terms), 3), missing


def technical_proxy(html: str, findings: list[Finding]) -> tuple[float, list[str]]:
    """A documented heuristic from local page properties; not Google's score.

    Important shortcomings count more heavily; an intentionally noindexed page
    is marked ineligible for Search, rather than treated as a simple weakness.
    No penalty for missing JSON-LD, meta description or canonical by default.
    """
    weighted_checks = {
        "title_missing": .17,
        "main_missing": .12,
        "language_missing": .12,
        "primary_heading_missing": .14,
        "thin_extractable_text": .18,
        "alt_attribute_missing": .17,
        "invalid_jsonld": .10,
    }
    present = {finding.code for finding in findings}
    loss = sum(weight for code, weight in weighted_checks.items() if code in present)
    return round(max(0.0, 1.0 - loss), 3), sorted(present)


def score_portfolio_platform(html: str, cfg: dict[str, Any], platform: str,
                             observation: dict[str, Any]) -> dict[str, Any]:
    if platform not in cfg["platforms"]:
        raise ValueError("Platform is not configured for this portfolio")
    p = cfg["platforms"][platform]
    # Confidence is a property of data provenance, not a fabricated probability.
    seo_findings = analyze_html(html)
    sem, missing_terms = semantic_proxy(html, cfg["priority_terms"])
    tech, codes = technical_proxy(html, seo_findings)
    co = organic_cooccurrence_proxy(observation.get("organic_mentions"),
                                    observation.get("qualified_mentions"))
    components = {
        "audience": finite_number(p["audience_fit"], "audience_fit"),
        "cooccurrence": co,
        "semantic": sem,
        "technical": tech,
        "format": finite_number(observation.get("format_fit", p["default_format_fit"]), "format_fit"),
    }
    result = calculate_score(components, cfg["weights"])
    # Hard gate: noindex normally means not eligible for Google Search indexing.
    search_eligible = not any(item.code == "noindex_found" for item in seo_findings)
    result.update({
        "platform": platform,
        "portfolio_id": cfg["portfolio_id"],
        "missing_terms": missing_terms,
        "technical_gaps": codes,
        "findings": seo_findings,
        "eligible_for_search": search_eligible,
        "components": components,
        "provenance": {
            "audience": "Portfolio configuration — unverified hypothesis",
            "cooccurrence": "Synthetic, non-individual-level observation" if co is not None else "Unavailable",
            "semantic": "Deterministic local HTML phrase check",
            "technical": "Local HTML checks; manual WCAG review still required",
            "format": "Portfolio configuration / synthetic observation",
        },
    })
    return result
