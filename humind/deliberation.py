"""Orchestration for independent review and deterministic consensus."""

from __future__ import annotations

from dataclasses import dataclass

from .consensus import evaluate_consensus
from .evidence import EvidencePack
from .providers.base import ReviewerProvider, RevisionProvider
from .schemas import ConsensusDecision, ModelReview, PeerReviewSummary, ThoughtProbe, Verdict
from .shadow import ShadowProbeGenerator


@dataclass(frozen=True)
class DeliberationResult:
    objective: str
    probe: ThoughtProbe
    reviews: tuple[ModelReview, ModelReview]
    consensus: ConsensusDecision
    review_rounds: tuple[tuple[ModelReview, ModelReview], ...]


class DeliberationEngine:
    def __init__(
        self,
        left: ReviewerProvider,
        right: ReviewerProvider,
        shadow: ShadowProbeGenerator | None = None,
        evidence_pack: EvidencePack | None = None,
        require_verified_evidence: bool = False,
    ) -> None:
        if left.name == right.name:
            raise ValueError("reviewers must have distinct provider identities")
        self.left = left
        self.right = right
        self.shadow = shadow or ShadowProbeGenerator()
        if require_verified_evidence and evidence_pack is None:
            raise ValueError("strict evidence mode requires an evidence pack")
        self.evidence_pack = evidence_pack
        self.require_verified_evidence = require_verified_evidence

    def _evaluate(self, reviews: tuple[ModelReview, ModelReview]) -> ConsensusDecision:
        decision = evaluate_consensus(reviews)
        if not self.require_verified_evidence:
            return decision
        assert self.evidence_pack is not None
        evidence_issues = []
        for review in reviews:
            evidence_issues.extend(
                f"{review.provider}: {issue}"
                for issue in self.evidence_pack.verification_issues(review)
            )
        if not evidence_issues:
            return decision
        return ConsensusDecision(
            False,
            Verdict.REQUEST_EVIDENCE,
            tuple((*(decision.reasons if not decision.approved else ()), *evidence_issues)),
        )

    @staticmethod
    def _validate_identities(
        reviews: tuple[ModelReview, ModelReview], expected: tuple[str, str]
    ) -> None:
        actual = (reviews[0].provider, reviews[1].provider)
        if actual != expected or actual[0] == actual[1]:
            raise ValueError(f"reviewer identity mismatch: expected {expected!r}, got {actual!r}")

    def deliberate(
        self,
        objective: str,
        *,
        round_number: int = 0,
        allow_revision: bool = True,
    ) -> DeliberationResult:
        probe = self.shadow.generate(objective, round_number=round_number)
        # Calls are kept logically independent: neither reviewer sees the other's answer.
        reviews = (
            self.left.review(objective, probe),
            self.right.review(objective, probe),
        )
        expected = (self.left.name, self.right.name)
        self._validate_identities(reviews, expected)
        review_rounds = [reviews]
        initial_veto = bool(reviews[0].critical_vetoes or reviews[1].critical_vetoes)
        consensus = self._evaluate(reviews)
        if (
            allow_revision
            and not consensus.approved
            and isinstance(self.left, RevisionProvider)
            and isinstance(self.right, RevisionProvider)
        ):
            left_position = PeerReviewSummary.from_review(reviews[0])
            right_position = PeerReviewSummary.from_review(reviews[1])
            reviews = (
                self.left.revise(objective, probe, left_position, right_position),
                self.right.revise(objective, probe, right_position, left_position),
            )
            self._validate_identities(reviews, expected)
            review_rounds.append(reviews)
            consensus = self._evaluate(reviews)
            if initial_veto and consensus.approved:
                consensus = ConsensusDecision(
                    False,
                    Verdict.ESCALATE,
                    ("a first-round critical veto requires human evidence review",),
                )
        self.shadow.adapt(reviews)
        return DeliberationResult(objective, probe, reviews, consensus, tuple(review_rounds))
