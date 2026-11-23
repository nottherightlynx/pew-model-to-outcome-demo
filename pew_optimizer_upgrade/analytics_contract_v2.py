"""Offline, aggregate-only analytics adapter for the independently built candidate demo.

RELEVANT STACK:
 - Pew's privacy notice explicitly identifies Google Analytics.
 - Pew's role posting requests Google Tag Manager and Facebook Insights skill.
 - Search Console is a proposed OPTIONAL SEO connector, not confirmed in use.
 - SQL/dbt-compatible rows support scalable transformations without per-platform UI code.
No API calls, OAuth, identifiers, cookies, credentials, or personal information are used.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from validation_v2 import MAX_METRIC_CSV_BYTES, read_local_file

# SOURCE-OF-TRUTH: A metric remains attached to its source and unit.
# Never add GA sessions to Search impressions or Facebook reactions.
METRICS = {
    "google_analytics": {"sessions", "engaged_sessions", "key_events"},
    "search_console_proposed": {"impressions", "clicks"},
    "facebook_insights_role": {"post_impressions", "post_engagements"},
}

@dataclass(frozen=True)
class MetricRow:
    portfolio_id: str
    platform: str
    source: str
    metric: str
    value: int
    period_start: str
    period_end: str
    provenance: str
    synthetic: bool = True

    def key(self) -> tuple[str, str, str, str, str, str]:
        return self.portfolio_id, self.platform, self.source, self.metric, self.period_start, self.period_end


def load_aggregate_metrics(root: Path) -> list[MetricRow]:
    """Local data only. Reject unexpected fields, duplicates and person-level data."""
    raw = read_local_file(root, "data/synthetic_owned_metrics.csv", "data", MAX_METRIC_CSV_BYTES)
    reader = csv.DictReader(io.StringIO(raw))
    expected = {"portfolio_id", "platform", "source", "metric", "value", "period_start", "period_end", "provenance", "synthetic"}
    if not reader.fieldnames or set(reader.fieldnames) != expected:
        raise ValueError("Metric data does not match documented aggregate-only contract")
    result: list[MetricRow] = []
    found = set()
    for row in reader:
        if row["source"] not in METRICS or row["metric"] not in METRICS[row["source"]]:
            raise ValueError("Unrecognized source / metric: require reviewed adapter mapping")
        if row["synthetic"].strip().lower() != "true":
            raise ValueError("Candidate demo only accepts rows explicitly labeled synthetic")
        if not re.fullmatch(r"[a-z0-9_]{2,50}", row["portfolio_id"]):
            raise ValueError("Invalid portfolio ID")
        if len(row["platform"]) > 48 or len(row["provenance"]) > 300:
            raise ValueError("Metric fields are too long")
        start = date.fromisoformat(row["period_start"])
        end = date.fromisoformat(row["period_end"])
        if end < start or (end - start).days > 370:
            raise ValueError("Invalid date range")
        # SECURITY: no decimals, negative counts, or overflow-like values.
        if not re.fullmatch(r"[0-9]{1,9}", row["value"]):
            raise ValueError("Metric value must be an aggregate nonnegative integer")
        metric = MetricRow(row["portfolio_id"], row["platform"], row["source"], row["metric"],
                           int(row["value"]), row["period_start"], row["period_end"],
                           row["provenance"], True)
        if metric.key() in found:
            raise ValueError("Duplicate metric source / period / platform")
        found.add(metric.key())
        result.append(metric)
        if len(result) > 5_000:
            raise ValueError("Demo limit of 5,000 aggregate metric rows exceeded")
    return result


def numeric_summary(rows: list[MetricRow], portfolio: str, platform: str) -> list[dict[str, Any]]:
    """Retain source/metric granularity, not a blended engagement score."""
    return [dict(source=r.source, metric=r.metric, value=r.value,
                 period=f"{r.period_start} to {r.period_end}", synthetic=r.synthetic)
            for r in rows if r.portfolio_id == portfolio and r.platform == platform]


def csv_safe_cell(value: Any) -> str:
    """CSV formula-injection guard when someone opens exported data in a spreadsheet."""
    string = str(value)
    if string.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + string
    return string


def safe_csv_export(rows: list[dict[str, Any]]) -> bytes:
    import io
    if not rows:
        return b""
    fields = list(rows[0])
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for item in rows:
        writer.writerow({key: csv_safe_cell(item.get(key, "")) for key in fields})
    return stream.getvalue().encode("utf-8")
