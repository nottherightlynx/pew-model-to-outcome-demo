"""Regression tests: sections 4–7 differ by platform AND stakeholder audience."""
from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from model_v2 import score_portfolio_platform
from platform_insights_v2 import (
    aggregate_rates, important_gap, intervention_for, section4_brief,
    section5_brief, section6_brief, section7_brief, strategy_for,
)
from validation_v2 import load_portfolios, load_observations, read_local_file
from analytics_contract_v2 import load_aggregate_metrics
from scoring import calculate_score


def fixture(portfolio: str, platform: str):
    cfg = load_portfolios(PROJECT)[portfolio]
    html = read_local_file(PROJECT, cfg["asset"], "data", 1_000_000)
    observation = load_observations(PROJECT, portfolio).get(platform, {})
    return cfg, score_portfolio_platform(html, cfg, platform, observation)


def test_sections_four_and_five_are_distinct_by_platform_and_role():
    plain, tech, sim_plain, sim_tech = {}, {}, {}, {}
    for platform in ("LinkedIn", "Search", "YouTube"):
        cfg, result = fixture("state_policy", platform)
        plain[platform] = " ".join(section4_brief(cfg, platform, result, technical=False))
        tech[platform] = " ".join(section4_brief(cfg, platform, result, technical=True))
        sim_plain[platform] = " ".join(section5_brief(platform, "format", technical=False))
        sim_tech[platform] = " ".join(section5_brief(platform, "format", technical=True))
        assert plain[platform] != tech[platform]
        assert sim_plain[platform] != sim_tech[platform]
        assert "Communications" in plain[platform]
        assert "Data/IT" in tech[platform] or "Technical handoff" in tech[platform]
        assert platform in plain[platform] and platform in tech[platform]
    for collection in (plain, tech, sim_plain, sim_tech):
        assert len(set(collection.values())) == 3
    assert "HTML" in plain["Search"]
    assert "native visual" in plain["LinkedIn"]
    assert "captions" in plain["YouTube"]


def test_sections_six_and_seven_are_distinct_by_platform_and_role():
    rows = load_aggregate_metrics(PROJECT)
    for portfolio in ("state_policy", "marine_management"):
        cfg = load_portfolios(PROJECT)[portfolio]
        descriptions = []
        for platform in ("LinkedIn", "Search", "YouTube"):
            plain = " ".join(section6_brief(cfg, platform, rows, technical=False))
            tech = " ".join(section6_brief(cfg, platform, rows, technical=True))
            assert plain != tech
            assert "For Communications" in plain
            assert "Data/IT" in tech
            descriptions.append(plain)
        assert len(set(descriptions)) == 3
    docs = []
    for platform in ("LinkedIn", "Search", "YouTube"):
        plain = " ".join(section7_brief(platform, technical=False))
        tech = " ".join(section7_brief(platform, technical=True))
        assert plain != tech
        refs = strategy_for(platform).documentation
        assert refs and all(ref.status.startswith("Reference only") for ref in refs)
        docs.append(tuple(ref.url for ref in refs))
    assert len(set(docs)) == 3


def test_rates_are_source_and_period_matched_without_blending():
    rows = load_aggregate_metrics(PROJECT)
    search_rates = aggregate_rates([r for r in rows if r.portfolio_id == "state_policy"], "Search")
    assert any("CTR: 7.5%" in value for value in search_rates)
    assert any("engaged-session rate: 64.9%" in value for value in search_rates)
    # YouTube GA referrals without an engaged numerator must not imply retention.
    yt_rates = aggregate_rates([r for r in rows if r.portfolio_id == "state_policy"], "YouTube")
    assert yt_rates == []
    assert all("retention" not in value.lower() for value in search_rates)

    @dataclass
    class Row:
        platform: str
        source: str
        period_start: str
        period_end: str
        metric: str
        value: int

    mixed_dates = [
        Row("Search", "search_console_proposed", "2026-10-01", "2026-10-31", "impressions", 1000),
        Row("Search", "search_console_proposed", "2026-09-01", "2026-09-30", "clicks", 100),
    ]
    assert aggregate_rates(mixed_dates, "Search") == []


def test_scores_remain_original_and_unknown_platform_never_inherits_assumptions():
    cfg, result = fixture("marine_management", "Search")
    assert result["score"] == calculate_score(result["components"], cfg["weights"])["score"]
    a = section7_brief("NewNetwork", technical=False)
    assert "NewNetwork" in " ".join(a)
    assert strategy_for("NewNetwork").documentation == ()
    assert "no validated" in strategy_for("NewNetwork").audience_reason.lower()
    assert intervention_for("NewNetwork", "format", True)
    assert important_gap(cfg, result) is not None


def test_technical_copy_names_appropriate_research_and_portfolio_review():
    cfg, result = fixture("state_policy", "LinkedIn")
    text = " ".join(section4_brief(cfg, "LinkedIn", result, technical=True))
    assert "Data/IT/engineering" in text
    assert "Research" in text
    assert "portfolio manager" in text
