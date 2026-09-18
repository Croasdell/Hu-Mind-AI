"""Deterministic provider used by tests and offline demonstrations."""

from __future__ import annotations

from dataclasses import replace

from ..schemas import ModelReview, ThoughtProbe


class MockReviewer:
    def __init__(self, review: ModelReview) -> None:
        self.name = review.provider
        self._review = review

    def review(self, objective: str, probe: ThoughtProbe) -> ModelReview:
        summary = self._review.summary or f"Reviewed {objective!r} against {probe.category}."
        return replace(self._review, summary=summary)

