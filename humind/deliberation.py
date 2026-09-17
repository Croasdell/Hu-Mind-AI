"""Orchestration for independent review and deterministic consensus."""

from __future__ import annotations

from dataclasses import dataclass

from .consensus import evaluate_consensus
from .providers.base import ReviewerProvider
from .schemas import ConsensusDecision, ModelReview, ThoughtProbe
from .shadow import ShadowProbeGenerator


@dataclass(frozen=True)
class DeliberationResult:
    objective: str
    probe: ThoughtProbe
    reviews: tuple[ModelReview, ModelReview]
    consensus: ConsensusDecision


class DeliberationEngine:
    def __init__(
        self,
        left: ReviewerProvider,
        right: ReviewerProvider,
        shadow: ShadowProbeGenerator | None = None,
    ) -> None:
        if left.name == right.name:
            raise ValueError("reviewers must have distinct provider identities")
        self.left = left
        self.right = right
        self.shadow = shadow or ShadowProbeGenerator()

    def deliberate(self, objective: str, *, round_number: int = 0) -> DeliberationResult:
        probe = self.shadow.generate(objective, round_number=round_number)
        # Calls are kept logically independent: neither reviewer sees the other's answer.
        reviews = (
            self.left.review(objective, probe),
            self.right.review(objective, probe),
        )
        consensus = evaluate_consensus(reviews)
        self.shadow.adapt(reviews)
        return DeliberationResult(objective, probe, reviews, consensus)

