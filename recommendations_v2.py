"""Reviewable optimization recommendations: source-backed, no automated publishing.

SEVERITY + FACTOR GAP + EFFORT are used for SCENARIO triage only; the result
is not predicted search ranking, social engagement, AI citation or impact.
"""
from __future__ import annotations
from typing import Any
from model_v2 import FACTOR_NAMES
from rules import generate_recommendations


def prioritized_actions(config: dict, result: dict) -> list[dict[str, Any]]:
    # Keep user's five-factor proposal; the new HTML audits add documented detail.
    old_result = dict(result)
    # Missing metrics are *not zero*. Replace missing values only in this
    # legacy rule adapter with a neutral skip sentinel; the displayed AVS
    # retains None and reports reduced coverage. New platforms can therefore
    # be added before data collection without crashing or fake negatives.
    old_result["components"] = {k: (1.0 if v is None else v)
                                for k, v in result["components"].items()}
    old_result["technical_gaps"] = []  # Don't trigger obsolete canonical-as-required fixes.
    actions = []
    for rec in generate_recommendations(config, old_result):
        if rec["dimension"] == "technical":
            continue
        # GEO guard: do not mistake topic-term absence for permission to
        # insert repetitive keywords or invent findings. Research must own edits.
        suggested_action = rec["action"]
        if rec["dimension"] == "semantic":
            missing = result.get("missing_terms", [])
            suggested_action = (
                "Check whether the page answers this audience's question. "
                "If supported by the research, clarify the missing concepts in normal language "
                "while keeping the accurate sector terms: " + ", ".join(missing[:3]) + ". "
                "Do not add phrases simply to increase a score."
            )
        actions.append({
            "factor": FACTOR_NAMES[rec["dimension"]],
            "next_action": suggested_action,
            "why": rec["evidence"],
            "caution": rec["caution"],
            "source": "Local fixture or configured assumption",
            "priority": rec["illustrative_priority"],
            "approval": rec["approval"],
        })
    if result["components"].get("cooccurrence") is None:
        actions.append({
            "factor": "Independent conversations about the topic",
            "next_action": "Document an approved source for independent topic conversations, or leave this factor missing.",
            "why": "No synthetic or approved observation was available for this platform.",
            "caution": "Missing data is not evidence that people are not discussing the topic.",
            "source": "Data provenance and platform API/terms review",
            "priority": 0.1,
            "approval": "Analytics and privacy review before acquiring off-site data",
        })
    for f in result["findings"]:
        if f.severity == "info":
            continue
        # Design choice, not scientific lift: highlights direct local defects.
        importance = 9 if f.severity == "important" else 4
        if f.confidence == "contextual":
            importance *= .7
        actions.append({
            "factor": "Technical and accessible content",
            "next_action": f.next_action,
            "why": f.observation,
            "caution": "Review against the published source; no guaranteed discoverability lift.",
            "source": f.reference,
            "priority": round(importance, 1),
            "approval": "Research, editorial and accessibility review where applicable",
        })
    actions.sort(key=lambda a: a["priority"], reverse=True)
    return actions
