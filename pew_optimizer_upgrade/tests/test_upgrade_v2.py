"""Offline tests for security, data contracts, no-overclaim, and source-based changes."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import pytest

from validation_v2 import finite_number, read_local_file, validate_config, load_portfolios, load_observations
from analytics_contract_v2 import load_aggregate_metrics, safe_csv_export, csv_safe_cell
from model_v2 import score_portfolio_platform
from recommendations_v2 import prioritized_actions
from seo_audit_v2 import analyze_html
from rule_review_v2 import demo_proposals


def test_non_finite_values_are_rejected():
    for invalid in (float("nan"), float("inf"), float("-inf"), True, "nan"):
        with pytest.raises(ValueError):
            finite_number(invalid, "risk")


def test_path_traversal_and_symlink_escape_fail(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "private.txt").write_text("sensitive")
    with pytest.raises(ValueError):
        read_local_file(tmp_path, "data/../private.txt", "data", 1000)
    (tmp_path / "data" / "link.html").symlink_to(tmp_path / "private.txt")
    with pytest.raises(ValueError):
        read_local_file(tmp_path, "data/link.html", "data", 1000)


def test_schema_validation_rejects_bad_weights():
    config = {
        "portfolio_id": "test_portfolio", "portfolio_label": "Test", "audience": "Researchers",
        "objective": "Test", "asset": "data/f.html", "priority_terms": ["research"],
        "weights": {k: .2 for k in ("audience", "cooccurrence", "semantic", "technical", "format")},
        "platforms": {"Search": {"audience_fit": .5, "default_format_fit": .5, "desired_format": "html"}},
    }
    assert validate_config(config)["portfolio_id"] == "test_portfolio"
    config["weights"]["semantic"] = float("nan")
    with pytest.raises(ValueError):
        validate_config(config)


def test_accessibility_does_not_treat_decorative_empty_alt_as_failure():
    html = "<html lang='en'><head><title>Test</title></head><body><main><h1>Text</h1><img alt='' src='line.svg'></main></body></html>"
    findings = analyze_html(html)
    assert "alt_attribute_missing" not in {f.code for f in findings}
    assert "empty_alt_review" in {f.code for f in findings}


def test_absent_jsonld_and_canonical_are_not_ai_search_defects():
    html = "<html lang='en'><head><title>Test</title></head><body><main><h1>Text</h1><p>Hello</p></main></body></html>"
    codes = {f.code for f in analyze_html(html)}
    assert "missing_jsonld" not in codes
    assert "missing_canonical" not in codes


def test_invalid_jsonld_and_noindex_are_identified():
    html = "<html lang='en'><head><title>Test</title><meta name='robots' content='noindex'></head><body><main><h1>A</h1><script type='application/ld+json'>{bad</script></main></body></html>"
    found = {f.code for f in analyze_html(html)}
    assert "noindex_found" in found
    assert "invalid_jsonld" in found


def test_model_preserves_five_factors_and_distinct_platform_priorities():
    root = PROJECT
    cfgs = load_portfolios(root)
    assert len(cfgs) >= 2
    outputs = []
    for cfg in cfgs.values():
        html = read_local_file(root, cfg["asset"], "data", 1_000_000)
        observations = load_observations(root, cfg["portfolio_id"])
        for platform in cfg["platforms"]:
            result = score_portfolio_platform(html, cfg, platform, observations.get(platform, {}))
            assert set(result["components"]) == {"audience", "cooccurrence", "semantic", "technical", "format"}
            assert result["score"] is not None and 0 <= result["score"] <= 100
            assert 0 <= result["coverage"] <= 1
            assert all(0 <= v <= 1 for v in result["components"].values() if v is not None)
            outputs.append((cfg["portfolio_id"], platform, result["score"], len(prioritized_actions(cfg, result))))
    assert len({item[2] for item in outputs}) >= 3  # Different platform diagnostics.


def test_noindex_is_search_eligibility_gate():
    cfg = next(iter(load_portfolios(PROJECT).values()))
    html = "<html><head><title>Test</title><meta name='robots' content='noindex'></head><body><main><h1>Test</h1></main></body></html>"
    result = score_portfolio_platform(html, cfg, "Search", {})
    assert result["eligible_for_search"] is False


def test_synthetic_metrics_provenance_and_safe_csv_export():
    metrics = load_aggregate_metrics(PROJECT)
    assert metrics and all(row.synthetic for row in metrics)
    assert all(row.source for row in metrics)
    assert csv_safe_cell("=SUM(A1:A2)").startswith("'=")
    assert safe_csv_export([{"action": "=CMD()", "priority": 7}]).find(b"'=CMD()") >= 0


def test_docs_feed_creates_review_proposal_not_rule_change():
    proposals = demo_proposals()
    assert proposals and all("not applied" in p.status for p in proposals)


def test_no_network_execution_or_unsafe_raw_html():
    source = (PROJECT / "app_v2.py").read_text()
    assert "unsafe_allow_html=True" not in source
    for token in ("requests.get(", "urllib.request.urlopen(", "os.system(", "eval(", "subprocess.run("):
        assert token not in source


def test_new_platform_without_observation_is_usable():
    cfg = next(iter(load_portfolios(PROJECT).values()))
    html = read_local_file(PROJECT, cfg["asset"], "data", 1_000_000)
    result = score_portfolio_platform(html, cfg, "Search", {})
    assert result["components"]["cooccurrence"] is None
    assert result["coverage"] < 1
    recs = prioritized_actions(cfg, result)
    assert any("source" in item["next_action"].lower() for item in recs)


def test_html_script_is_not_treated_as_visible_topic_content():
    cfg = load_portfolios(PROJECT)["state_policy"]
    html = ("<html lang='en'><head><title>Example</title></head>"
            "<body><main><h1>Information</h1><script>var x='budget stabilization fund';</script>"
            "<p>There are no details here.</p></main></body></html>")
    result = score_portfolio_platform(html, cfg, "Search", {})
    assert "budget stabilization fund" in result["missing_terms"]
