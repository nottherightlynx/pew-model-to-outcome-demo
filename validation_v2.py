"""Validate local fixture configuration before handing it to existing scoring.py.

SECURITY: Reject unsafe paths, oversized inputs, YAML types and NaN/Infinity.
SCALE: Validate once at the data boundary, not repeatedly in the view.
The app intentionally does not crawl external URLs, run generated code, or use secrets.
"""
from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Any

import yaml

KNOWN_COMPONENTS = ("audience", "cooccurrence", "semantic", "technical", "format")
ID = re.compile(r"^[a-z][a-z0-9_]{1,48}$")
MAX_CONFIG_BYTES = 80_000
MAX_HTML_BYTES = 1_000_000
MAX_METRIC_CSV_BYTES = 1_000_000


def finite_number(value: Any, label: str, lo: float = 0, hi: float = 1) -> float:
    """Numbers must be real finite numbers, not bools, NaN or infinity."""
    if isinstance(value, bool):
        raise ValueError(f"{label}: true/false is not a number")
    try:
        number = float(value)
    except (ValueError, TypeError) as error:
        raise ValueError(f"{label}: expected a number") from error
    if not math.isfinite(number) or not lo <= number <= hi:
        raise ValueError(f"{label}: expected a finite value from {lo} to {hi}")
    return number


def read_local_file(root: Path, relative: str, directory: str, max_bytes: int) -> str:
    """Allow only bounded files within the expected project subdirectory.

    SECURITY: Absolute paths, ../ traversal, symlinks to outside, and huge files fail closed.
    """
    root = root.resolve()
    if not isinstance(relative, str) or not relative:
        raise ValueError("A local file path is required")
    target = (root / relative).resolve()
    allowed = (root / directory).resolve()
    if not target.is_relative_to(allowed) or not target.is_file():
        raise ValueError(f"File must exist inside {directory}/")
    if target.stat().st_size > max_bytes:
        raise ValueError(f"File is too large; limit is {max_bytes} bytes")
    return target.read_text(encoding="utf-8")


def validate_config(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Portfolio configuration must be a map")
    pid = value.get("portfolio_id")
    if not isinstance(pid, str) or not ID.fullmatch(pid):
        raise ValueError("portfolio_id must be a simple name (letters, numbers, underscores)")
    for label in ("portfolio_label", "audience", "objective"):
        if not isinstance(value.get(label), str) or not 1 <= len(value[label]) <= 500:
            raise ValueError(f"{label} must be short readable text")
    asset = value.get("asset")
    if not isinstance(asset, str) or not asset.startswith("data/") or not asset.endswith(".html"):
        raise ValueError("asset must be a local data/*.html fixture")
    if any(char in asset for char in ("\\", "\x00")):
        raise ValueError("Invalid asset path")
    terms = value.get("priority_terms")
    if not isinstance(terms, list) or not 1 <= len(terms) <= 40:
        raise ValueError("Include 1–40 priority terms")
    if not all(isinstance(x, str) and 1 <= len(x) <= 100 for x in terms):
        raise ValueError("Priority terms must be short strings")
    weights = value.get("weights")
    if not isinstance(weights, dict) or set(weights) != set(KNOWN_COMPONENTS):
        raise ValueError("weights must include exactly the five factors")
    if sum(finite_number(weights[k], f"weight {k}") for k in KNOWN_COMPONENTS) <= 0:
        raise ValueError("At least one weight must be non-zero")
    finite_number(value.get("mission_value", 1.0), "mission_value", 0, 10)
    platforms = value.get("platforms")
    if not isinstance(platforms, dict) or not 1 <= len(platforms) <= 20:
        raise ValueError("Include 1–20 named platforms")
    for platform, cfg in platforms.items():
        if not isinstance(platform, str) or not 1 <= len(platform) <= 48:
            raise ValueError("Platform names must be short")
        if not isinstance(cfg, dict):
            raise ValueError("Platform settings must be maps")
        finite_number(cfg.get("audience_fit"), platform + " audience_fit")
        finite_number(cfg.get("default_format_fit"), platform + " default_format_fit")
        if not isinstance(cfg.get("desired_format"), str) or len(cfg["desired_format"]) > 300:
            raise ValueError("desired_format must be a short text description")
    return value


def load_portfolios(root: Path) -> dict[str, dict[str, Any]]:
    result = {}
    config_dir = (root / "config").resolve()
    # SCALE: bounded files and a maximum of 24 portfolios in this local demo.
    for path in sorted(config_dir.glob("*.yml"))[:24]:
        body = read_local_file(root, str(path.relative_to(root)), "config", MAX_CONFIG_BYTES)
        cfg = validate_config(yaml.safe_load(body))  # SECURITY: never yaml.load on untrusted input
        if cfg["portfolio_id"] in result:
            raise ValueError(f"Duplicate portfolio id: {cfg['portfolio_id']}")
        # Fail early if the referenced fixture is unavailable or unsafe.
        read_local_file(root, cfg["asset"], "data", MAX_HTML_BYTES)
        result[cfg["portfolio_id"]] = cfg
    if not result:
        raise ValueError("No usable configurations in config/*.yml")
    return result


def load_observations(root: Path, portfolio_id: str) -> dict[str, dict[str, Any]]:
    """Read synthetic fixtures with strict integer/range validation; no individual-level data."""
    raw = read_local_file(root, "data/synthetic_observations.csv", "data", MAX_METRIC_CSV_BYTES)
    import io
    result: dict[str, dict[str, Any]] = {}
    for row in csv.DictReader(io.StringIO(raw)):
        if row.get("portfolio_id") != portfolio_id:
            continue
        name = row.get("platform", "")
        if not name or len(name) > 48 or name in result:
            raise ValueError("Duplicate or invalid platform in observation CSV")
        for field in ("organic_mentions", "qualified_mentions"):
            try:
                n = int(row.get(field, ""))
            except (TypeError, ValueError) as error:
                raise ValueError(f"{field} must be a whole number") from error
            if n < 0 or n > 1_000_000:
                raise ValueError(f"{field} is outside allowed bounds")
        total = int(row["organic_mentions"])
        qualified = int(row["qualified_mentions"])
        if qualified > total:
            raise ValueError("Qualified mentions cannot exceed all mentions")
        result[name] = {"organic_mentions": total,
                        "qualified_mentions": qualified,
                        "format_fit": finite_number(row.get("format_fit"), "format_fit"),
                        "measurement_note": str(row.get("measurement_note", ""))[:400]}
    return result
