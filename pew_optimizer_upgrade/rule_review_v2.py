"""Static documentation change review queue; never auto-edit model weights.

The demo is intentionally offline. A future RSS integration should only
create SOURCE-VERIFIED proposals for tests and human sign-off. These sources
are not themselves evidence that any platform algorithm has changed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ChangeProposal:
    source_title: str
    source_url: str
    review_question: str
    affected_module: str
    status: str = "Needs human review — not applied"
    research_note: str = "Example review item, not a detected or verified live change"

    def to_dict(self) -> dict:
        return asdict(self)


def demo_proposals() -> list[ChangeProposal]:
    return [
        ChangeProposal(
            "Google Search Central: guidance for generative AI",
            "https://developers.google.com/search/docs/fundamentals/ai-optimization-guide",
            "Do our recommendations rely on structured-data or mention claims this guidance does not support?",
            "seo_audit_v2.py / documentation and tests",
        ),
        ChangeProposal(
            "OpenAI crawler documentation",
            "https://developers.openai.com/api/docs/bots",
            "Have we kept OAI-SearchBot (search) separate from GPTBot (training)?",
            "Crawler assumptions and documentation",
        ),
    ]
