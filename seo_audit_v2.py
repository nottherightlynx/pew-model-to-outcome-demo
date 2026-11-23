"""Evidence-tagged, local-only, non-predictive discoverability checks.

Each finding includes the official reference that motivates the audit. These checks
help a human reviewer; they do NOT claim to know ranking weights or AI citations.
No network requests, LLM calls, DOM injection, or user-controlled path access.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from urllib.parse import urlparse

from bs4 import BeautifulSoup

GOOGLE_AI = "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide"
GOOGLE_IMAGE = "https://developers.google.com/search/docs/appearance/google-images"
GOOGLE_SCHEMA = "https://developers.google.com/search/docs/appearance/structured-data/sd-policies"
GOOGLE_JS = "https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics"
WCAG = "https://www.w3.org/TR/WCAG22/"
OPENAI_BOTS = "https://developers.openai.com/api/docs/bots"


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str  # review | important | info
    observation: str
    next_action: str
    reference: str
    confidence: str  # direct | contextual

    def to_dict(self) -> dict:
        return asdict(self)


def _external_web_links(soup: BeautifulSoup) -> int:
    return sum(bool(urlparse(a.get("href", "")).netloc) for a in soup.select("a[href]"))


def analyze_html(html: str) -> list[Finding]:
    """Interpret visible on-page facts, avoid claims about proprietary algorithms."""
    soup = BeautifulSoup(html, "html.parser")
    # Capture JSON-LD BEFORE filtering out executable/non-visible nodes.
    # A JSON-LD script is data to parse, never code to execute.
    structured_scripts = [x.string or x.get_text() for x in soup.find_all("script", type="application/ld+json")]
    body = soup.body or soup
    for node in body.find_all(["script", "style", "template", "noscript"]):
        node.decompose()  # SECURITY: do not show code as visible research text.
    text = " ".join(body.stripped_strings)
    findings: list[Finding] = []

    def add(code: str, severity: str, observation: str, next_action: str, ref: str,
            confidence: str = "direct") -> None:
        findings.append(Finding(code, severity, observation, next_action, ref, confidence))

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if not title:
        add("title_missing", "important", "The HTML has no readable page title.",
            "Add an accurate title that distinguishes the research from similar pages.", GOOGLE_AI)
    elif len(title) > 110:
        add("title_review", "review", "The page title is unusually long.",
            "Review whether the title clearly names the question, geography and research topic; do not keyword-stuff.", GOOGLE_AI, "contextual")

    if not body.find("main"):
        add("main_missing", "review", "There is no main landmark in this HTML fixture.",
            "Identify the main page content for keyboard and assistive-technology navigation.", WCAG)
    if not (soup.html and soup.html.get("lang")):
        add("language_missing", "review", "The document language is not declared.",
            "Set the correct HTML lang value on the root element.", WCAG)
    h1s = soup.find_all("h1")
    if not h1s:
        add("primary_heading_missing", "important", "There is no primary H1 heading.",
            "Give the page a descriptive, accessible main heading.", WCAG)
    elif len(h1s) > 1:
        add("primary_heading_review", "review", "Multiple H1 headings may complicate navigation.",
            "Check the heading hierarchy for clarity; multiple H1s are not an automatic ranking failure.", WCAG, "contextual")
    if not soup.find(["h2", "h3"]):
        add("section_headings", "review", "The page has no secondary headings.",
            "Break the main finding and method into descriptive sections where useful.", GOOGLE_AI, "contextual")
    if len(text.split()) < 70:
        add("thin_extractable_text", "review", "This fixture contains little extractable text.",
            "Check whether the report's key question, qualified finding and evidence are readable as HTML. Do not add filler.", GOOGLE_AI, "contextual")

    desc = soup.find("meta", attrs={"name": lambda v: isinstance(v, str) and v.lower() == "description"})
    if not desc or not desc.get("content", "").strip():
        add("description_review", "review", "No authored meta description was detected.",
            "Consider a concise factual snippet; Google may use different on-page text.", GOOGLE_AI, "contextual")

    robots = [m.get("content", "").lower() for m in soup.find_all("meta")
              if str(m.get("name", "")).lower() in ("robots", "googlebot")]
    if any("noindex" in val for val in robots):
        add("noindex_found", "important", "The HTML contains a noindex directive.",
            "Verify whether exclusion from search is intentional before suggesting any change.", GOOGLE_JS)

    images = soup.find_all("img")
    missing_alt = [img for img in images if not img.has_attr("alt")]
    empty_alt = [img for img in images if img.has_attr("alt") and not (img.get("alt") or "").strip()]
    if missing_alt:
        add("alt_attribute_missing", "important", f"{len(missing_alt)} image(s) lack an alt attribute.",
            "Review each image; supply useful alternative text or use empty alt only when genuinely decorative.", WCAG)
    if empty_alt:
        add("empty_alt_review", "review", f"{len(empty_alt)} image(s) use empty alt text.",
            "Confirm each is decorative; charts and maps need meaningful text alternatives.", GOOGLE_IMAGE, "contextual")
    if images and not soup.find("table") and not soup.find("figcaption"):
        add("visual_context_review", "review", "Images have no adjacent table or figcaption in this HTML.",
            "For charts/maps, provide an adjacent explanation or accessible data equivalent if needed; inspect visuals first.", WCAG, "contextual")

    generic = {"click here", "read more", "learn more", "here"}
    weak_links = [a.get_text(" ", strip=True) for a in soup.find_all("a", href=True)
                  if a.get_text(" ", strip=True).lower() in generic]
    if weak_links:
        add("link_text_review", "review", "Some links don't identify their destination in isolation.",
            "Use link text that names the source or destination in context.", WCAG)
    if _external_web_links(soup) == 0:
        add("source_links_review", "review", "No external reference links were found in this fixture.",
            "Check whether the report should link its methodology, source tables or original evidence.", GOOGLE_AI, "contextual")

    for script in structured_scripts:
        try:
            data = json.loads(script)
        except (ValueError, TypeError):
            add("invalid_jsonld", "important", "JSON-LD markup could not be parsed as JSON.",
                "Correct syntax, then validate the markup against the matching supported feature.", GOOGLE_SCHEMA)
            continue
        if not isinstance(data, (dict, list)):
            add("jsonld_review", "review", "JSON-LD is neither an object nor a list of objects.",
                "Check that any structured data accurately represents visible page content.", GOOGLE_SCHEMA, "contextual")
    # Critical: absence of schema.org markup is NOT a defect for generative AI search.
    # Google says no special markup is required for AI Overviews or AI Mode.
    return findings


def summaries(findings: list[Finding]) -> dict[str, int]:
    return {k: sum(f.severity == k for f in findings) for k in ("important", "review", "info")}
