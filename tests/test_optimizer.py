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
