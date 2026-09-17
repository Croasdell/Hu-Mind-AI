"""Deterministic consensus checks; models cannot waive these rules."""

from __future__ import annotations

from .schemas import ConsensusDecision, ModelReview, Verdict


def evaluate_consensus(
    reviews: tuple[ModelReview, ModelReview],
    *,
    minimum_confidence: float = 0.75,
    require_evidence: bool = True,
) -> ConsensusDecision:
    if not 0.0 <= minimum_confidence <= 1.0:
        raise ValueError("minimum_confidence must be between 0 and 1")

    left, right = reviews
    reasons: list[str] = []
    if left.provider == right.provider:
        reasons.append("reviewers must have distinct provider identities")
    if left.verdict is not Verdict.APPROVE or right.verdict is not Verdict.APPROVE:
        reasons.append("both reviewers must approve")
    if left.critical_vetoes or right.critical_vetoes:
        reasons.append("a critical veto remains unresolved")
    if min(left.confidence, right.confidence) < minimum_confidence:
        reasons.append("review confidence is below threshold")
    if require_evidence and (not left.evidence or not right.evidence):
        reasons.append("both reviewers must provide evidence")
    if left.action is None or right.action is None:
        reasons.append("both reviewers must propose an action")
    elif left.action.fingerprint != right.action.fingerprint:
        reasons.append("reviewers proposed different actions")

    if reasons:
        next_status = (
            Verdict.REQUEST_EVIDENCE
            if any("evidence" in reason for reason in reasons)
            else Verdict.ESCALATE
        )
        return ConsensusDecision(False, next_status, tuple(reasons))

    return ConsensusDecision(
        True,
        Verdict.APPROVE,
        ("independent reviewers approved the same canonical action",),
        left.action,
    )
