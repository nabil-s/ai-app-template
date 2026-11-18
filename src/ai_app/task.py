"""Placeholder task: replace with the app's real logic.

Kept deliberately tiny (sentiment label) so the eval pipeline has something to score.
"""

from __future__ import annotations

from ai_app.llm import LLMClient, complete_logged

LABELS = ("positive", "negative", "neutral")
SYSTEM = (
    "Classify the sentiment of the user's text. "
    "Reply with exactly one word: positive, negative, or neutral."
)


def classify(text: str, client: LLMClient) -> str:
    raw = complete_logged(client, text, SYSTEM).text.strip().lower()
    return next((label for label in LABELS if label in raw), "unknown")
