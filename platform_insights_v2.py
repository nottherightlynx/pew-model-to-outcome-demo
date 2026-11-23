"""Section 4–7 stakeholder briefs for a five-factor, platform-specific optimizer.

CHANGE SCOPE: presentation and decision guidance ONLY. This module does not
modify component scores, weights, priorities, fixtures, connections, or content.

Use documented platform guidance as a *review reference*, not a secret-ranking
formula. All copy is deterministic and local. Other platforms receive a cautious
fallback until their strategy and official sources are reviewed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from model_v2 import FACTOR_NAMES, FACTORS
from scoring import normalize_weights


@dataclass(frozen=True)
class DocumentReference:
    name: str
    url: str
    issue_to_review: str
    technical_review: str
    # These are manually curated links, NOT a live documentation-change alert.
    status: str = "Reference only · no live change detected · no rule applied"


@dataclass(frozen=True)
class PlatformStrategy:
    plain_goal: str
    content_package: str
    audience_reason: str
    technical_handoff: str
    observed_measure: str
    proposed_measure: str
    experiment: str
    limits: str
    portfolio_review: str
    documentation: tuple[DocumentReference, ...]


STRATEGIES: dict[str, PlatformStrategy] = {
    "Search": PlatformStrategy(
        plain_goal="Make the research page easy to find for a relevant question, and easy to understand once someone lands on it.",
        content_package="Put a direct answer and accurately defined terms in visible HTML, make supporting tables usable, and link to methods and source data.",
        audience_reason="People arrive with questions, not necessarily with the exact title of a Pew publication. The page has to answer the question without losing the underlying research.",
        technical_handoff="Data/IT: check indexing eligibility, accessible HTML, heading structure and source links; use Search Console only with approved access. Keep GA engagement separate from search-result metrics.",
        observed_measure="Search impressions and clicks for the relevant page/query group, plus GA engaged sessions for the landing page, measured separately.",
        proposed_measure="Authorized Search Console page/query impressions and clicks; GA landing-page sessions and key events where permitted.",
        experiment="Compare a page or matched query group before and after a reviewed heading/HTML update; check seasonality, indexing and unrelated site changes.",
        limits="No automatic AI-citation probability follows from schema, mentions or a higher score. Eligibility, retrieval and engagement are different outcomes.",
        portfolio_review="Research reviews any new or rephrased findings, definitions, date ranges and methodology; the portfolio manager confirms the audience question and priority for this portfolio.",
        documentation=(
            DocumentReference(
                "Google Search Central — generative AI guidance",
                "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide",
                "Does the suggested HTML and content edit still follow current Search and AI-feature guidance?",
                "Check updated crawl/index requirements against a test fixture, review structured-data eligibility without assuming a ranking boost, and request Search/editorial approval.",
            ),
            DocumentReference(
                "OpenAI — crawler controls",
                "https://developers.openai.com/api/docs/bots",
                "Are search and training crawler controls being interpreted separately?",
                "Validate approved robots directives for the intended crawler; do not treat a crawler user agent as proof of citation or ranking.",
            ),
        ),
    ),
    "LinkedIn": PlatformStrategy(
        plain_goal="Put the specific finding in front of the professional audience that would use it, in a format that gives them something useful to share or discuss.",
        content_package="Build a concise, professionally relevant post and the configured native visual or carousel; retain the original source and limits of the research.",
        audience_reason="A legislative analyst or program professional needs the finding and its relevance quickly; copying the website abstract into a post doesn't necessarily answer that need.",
        technical_handoff="Data/IT: request authorized native LinkedIn post analytics and join to GA referral sessions by campaign/content ID and date. Do not substitute GA referral sessions for post impressions or feed reach.",
        observed_measure="Native post impressions and engagement, where authorized, followed separately by GA LinkedIn referral sessions and engaged sessions.",
        proposed_measure="LinkedIn Page analytics for approved posts; GA tagged referral sessions and key events, joined by stable content/campaign ID if available.",
        experiment="Compare two editorially approved post packages for the same audience and publication, controlling for timing and distribution where feasible; compare qualified actions, not just raw likes.",
        limits="LinkedIn describes personalized, multi-signal relevance. The engine cannot infer proprietary feed weights or presume that outbound links are penalized.",
        portfolio_review="Research reviews new or reframed findings, figures and caveats in the visual. The portfolio manager confirms that this portfolio's post speaks to the intended professional audience.",
        documentation=(
            DocumentReference(
                "LinkedIn — how the Feed ranks content",
                "https://www.linkedin.com/help/linkedin/answer/a9554004",
                "Does the professional-audience and content-format advice remain consistent with LinkedIn's published Feed guidance?",
                "Review documentation changes and the authorized post-metric schema; update only a tested guidance rule after Communications and analytics sign-off.",
            ),
            DocumentReference(
                "LinkedIn — relevance overview",
                "https://www.linkedin.com/help/linkedin/answer/a1339724",
                "Do any proposed claims about ranking or engagement overstate what LinkedIn discloses?",
                "Flag unsupported claims and run a controlled channel experiment instead of assigning new secret-ranking weights.",
            ),
        ),
    ),
    "YouTube": PlatformStrategy(
        plain_goal="Make a video worth choosing and worth finishing for the people who need the finding.",
        content_package="Lead with a direct audience question, show the finding early, and provide accurate captions, a useful description and source links.",
        audience_reason="If the topic is right but the opening doesn't answer why the viewer should watch, the video can miss the audience even when its title and description are technically correct.",
        technical_handoff="Data/IT: request authorized YouTube Studio/video analytics for impressions, click-through and audience retention; keep those separate from GA sessions referred from YouTube. Verify accessible captions/transcript artifacts.",
        observed_measure="Video impressions/thumbnail CTR and audience-retention segments if approved YouTube analytics exist; GA YouTube referral engagement is a separate downstream measure.",
        proposed_measure="YouTube Studio per-video impressions, thumbnail CTR, first-30-second retention and watch-time context, if access is approved; GA referrals separately.",
        experiment="Compare research-approved opening scripts, title/thumbnail concepts or caption fixes on comparable videos; report audience mix and content-length differences.",
        limits="Retention and viewer choice are documented diagnostic indicators, not one universal ranking formula. This offline fixture has no YouTube Studio connection.",
        portfolio_review="Research reviews new or reframed claims in the visuals, script and captions; the portfolio manager checks that the opening addresses this portfolio's audience without oversimplifying.",
        documentation=(
            DocumentReference(
                "YouTube Help — content performance and recommendations",
                "https://support.google.com/youtube/answer/16559650?hl=en",
                "Does the proposed opening, packaging and measurement align with YouTube's published appeal, engagement and satisfaction guidance?",
                "Review the updated Studio metric definitions and accessible transcript/caption checks; keep channel signals out of the formula until validated.",
            ),
            DocumentReference(
                "YouTube Help — performance FAQ",
                "https://support.google.com/youtube/answer/141805?hl=en",
                "Are we describing video discovery as audience-specific rather than claiming one universal engagement factor?",
                "Revise the experiment protocol and request Communications, research and analytics review before changing rules.",
            ),
        ),
    ),
}


FACTOR_CHANGE: dict[str, dict[str, tuple[str, str]]] = {
    "Search": {
        "audience": ("Refocus the page on the questions this audience searches for.", "Validate intended query groups with approved search and audience data."),
        "cooccurrence": ("Use legitimate third-party questions to identify missing explanations, not to manufacture mentions.", "Keep cited public sources and permissions attached to any question mapping."),
        "semantic": ("Answer the actual question in a clear heading and paragraph, with the correct research terms.", "Check main-content extraction and human-approved topic terms, not keyword density."),
        "technical": ("Make the finding, tables and source links usable in accessible HTML.", "Audit index eligibility, main content, document structure and manual accessibility findings."),
        "format": ("Give the reader an extractable summary next to supporting research and charts.", "Test an accessible HTML asset; do not assume schema alone causes AI citations."),
    },
    "LinkedIn": {
        "audience": ("Frame the finding around a professional decision this audience makes.", "Validate professional-audience relevance from authorized audience research or native analytics."),
        "cooccurrence": ("Use existing professional discussions to find what needs explaining.", "Document the source, legal basis and editorial use of external discussion themes."),
        "semantic": ("Make the first lines of the post state the actual finding and who it applies to.", "Check post copy and visual claims against the approved publication, including qualifiers."),
        "technical": ("Make charts readable on a small screen and give viewers a clear source.", "Check image text alternatives where supported, visual contrast and source URLs in publishing assets."),
        "format": ("Turn the finding into a professional-facing visual or carousel instead of pasting the article abstract.", "Prepare the portfolio's specified native format and track the approved post/content ID."),
    },
    "YouTube": {
        "audience": ("Start by explaining why this specific audience should watch.", "Validate intended viewer segment and avoid treating general platform reach as qualified reach."),
        "cooccurrence": ("Use legitimate audience questions to identify a clearer opening, not artificial engagement.", "Keep documented research questions separate from unverified social sentiment."),
        "semantic": ("Use a clear title, spoken explanation and transcript that define the topic accurately.", "Validate transcript-to-script terms and the research source for every claim."),
        "technical": ("Add accurate captions and a source-linked description that can be used without sound.", "Review caption accuracy, transcript availability and accessibility of charts shown in the video."),
        "format": ("Show the relevant result early, with an opening that matches the viewer's question.", "Prepare a reviewed opening/thumbnail variant and record video ID, publication time and duration."),
    },
}


def strategy_for(platform: str) -> PlatformStrategy:
    """Unknown configured platforms are safe, and never inherit false channel rules."""
    if platform in STRATEGIES:
        return STRATEGIES[platform]
    return PlatformStrategy(
        plain_goal=f"Confirm how the intended audience uses {platform} before making a channel-specific optimization claim.",
        content_package="Use the portfolio's configured format as a hypothesis, pending a reviewed channel playbook.",
        audience_reason="No validated platform-specific engagement logic has been configured for this channel.",
        technical_handoff="Data/IT: document approved API access, metric definitions and source permissions before enabling an adapter.",
        observed_measure="No validated platform-specific measure configured; use explicitly sourced permitted aggregates only.",
        proposed_measure="Define a channel-owned metric and a first-party downstream metric with separate denominators.",
        experiment="Agree on one audience outcome and controlled content variant before interpreting performance.",
        limits="Unknown platform. Do not reuse the Search, LinkedIn or YouTube ranking assumptions.",
        portfolio_review="Research validates source accuracy; portfolio leadership validates relevance; Communications owns presentation.",
        documentation=(),
    )


def important_gap(cfg: dict, result: dict) -> tuple[str, float] | None:
    """Largest configured weighted shortfall, not strongest causal ranking lever."""
    weights = normalize_weights(cfg["weights"])
    ranked = [(key, (1.0 - result["components"][key]) * weights[key])
              for key in FACTORS if result["components"].get(key) is not None]
    return max(ranked, key=lambda x: x[1]) if ranked else None


def intervention_for(platform: str, factor: str, technical: bool) -> str:
    pair = FACTOR_CHANGE.get(platform, {}).get(factor)
    if pair is None:
        return ("Record the tested input definition and permitted data source before proposing an implementation."
                if technical else "Review this condition with the intended audience before changing the content.")
    return pair[1 if technical else 0]


def section4_brief(cfg: dict, platform: str, result: dict, *, technical: bool) -> list[str]:
    """Return distinct decision messages for the appropriate stakeholder group."""
    spec = strategy_for(platform)
    gap = important_gap(cfg, result)
    gap_line = (f"The biggest configured shortfall is {FACTOR_NAMES[gap[0]]} "
                f"({gap[1] * 100:.1f} weighted diagnostic points), not an observed ranking cause."
                if gap else "No comparable configured gap is available; do not assign a fake zero.")
    if technical:
        return [
            f"Technical handoff for {platform}: {spec.technical_handoff}",
            gap_line,
            ("Data/IT/engineering: retain portfolio_id, content ID, platform, observation source, "
             "metric definition, date range, formula version and test status in the implementation ticket."),
            f"Research / portfolio review: {spec.portfolio_review}",
            f"Constraint: {spec.limits}",
        ]
    return [
        f"For Communications on {platform}: {spec.plain_goal}",
        f"Content package: {cfg['platforms'][platform]['desired_format']}. {spec.content_package}",
        f"Why for this audience: {spec.audience_reason}",
        (f"First gap to check: {FACTOR_NAMES[gap[0]]}. "
         f"{intervention_for(platform, gap[0], False)}" if gap else
         "First check that the team has enough information to make a channel-specific recommendation."),
        f"Before publication: {spec.portfolio_review}",
    ]


def section5_brief(platform: str, factor: str, *, technical: bool) -> list[str]:
    spec = strategy_for(platform)
    if technical:
        return [
            f"{platform} implementation example for {FACTOR_NAMES[factor]}: {intervention_for(platform, factor, True)}",
            "Change the one configured input only. The formula recomputes a diagnostic index; it does not estimate traffic, feed distribution or watch time.",
            f"Validation plan: {spec.experiment}",
        ]
    return [
        f"For {platform}, improving {FACTOR_NAMES[factor].lower()} would look like this: {intervention_for(platform, factor, False)}",
        "The slider changes the model's assessment. It cannot tell us how much real engagement will increase.",
        f"What to try next: {spec.experiment}",
    ]


def aggregate_rates(rows: Iterable[Any], platform: str) -> list[str]:
    """Only derive rates with identical source and period; never join source totals."""
    batches: dict[tuple[str, str, str], dict[str, int]] = {}
    for row in rows:
        # Input contract already validates allowed metrics, sources and periods.
        if row.platform != platform:
            continue
        key = (row.source, row.period_start, row.period_end)
        batches.setdefault(key, {})[row.metric] = row.value
    summaries: list[str] = []
    for (source, start, end), values in sorted(batches.items()):
        if source == "search_console_proposed" and platform == "Search":
            impressions, clicks = values.get("impressions"), values.get("clicks")
            if impressions and clicks is not None and 0 <= clicks <= impressions:
                summaries.append(f"Synthetic Search Console-like CTR: {clicks / impressions:.1%} ({clicks}/{impressions}; {start}–{end}).")
        if source == "google_analytics":
            sessions, engaged = values.get("sessions"), values.get("engaged_sessions")
            if sessions and engaged is not None and 0 <= engaged <= sessions:
                summaries.append(f"Synthetic GA engaged-session rate: {engaged / sessions:.1%} ({engaged}/{sessions}; {start}–{end}).")
    return summaries


def section6_brief(cfg: dict, platform: str, rows: list[Any], *, technical: bool) -> list[str]:
    spec = strategy_for(platform)
    found = [r for r in rows if r.portfolio_id == cfg["portfolio_id"] and r.platform == platform]
    observed = aggregate_rates(found, platform)
    if technical:
        return [
            f"Data/IT measurement design for {platform}: {spec.proposed_measure}",
            f"Expected outcome dimensions: {spec.observed_measure}",
            "Data contract: keep source, portfolio, content/campaign ID, date range, metric, denominator and a synthetic/real flag. Do not merge native-platform reach with GA referrals.",
            ("Rates from provided aggregate fixture (not Pew): " + " ".join(observed)) if observed else
            "No valid same-source numerator/denominator pair exists in the fixture for this platform; do not report a rate.",
            f"Research/portfolio guardrail: {spec.portfolio_review}",
            f"Experiment and limitations: {spec.experiment} {spec.limits}",
        ]
    return [
        f"For Communications, success on {platform} would mean: {spec.observed_measure}",
        f"Test: {spec.experiment}",
        ("The demo's sample data currently shows: " + " ".join(observed)) if observed else
        "The demo does not contain enough matched measures to calculate a channel engagement rate. That does not mean there was no engagement.",
        f"Important: {spec.limits}",
    ]


def section7_brief(platform: str, *, technical: bool) -> list[str]:
    spec = strategy_for(platform)
    if technical:
        return [
            f"Platform: {platform}. {spec.technical_handoff}",
            "Review protocol: verify the exact official change and effective date; identify affected tests, metric definitions, ingestion rules and content guidance; run regression tests; request human approval; version the rule before release.",
            f"Do not auto-update weights: {spec.limits}",
        ]
    return [
        f"For Communications on {platform}: published platform guidance can change what we should test, but it does not automatically tell us what will rank.",
        f"When guidance changes, the content decision to revisit is: {spec.content_package}",
        "The engine would flag a proposed change for review. Nothing gets rewritten, published or rescored automatically.",
    ]
