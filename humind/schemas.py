"""Shared, provider-neutral contracts for Hu-Mind deliberation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
import math


class Verdict(str, Enum):
    APPROVE = "approve"
    REVISE = "revise"
    REQUEST_EVIDENCE = "request_evidence"
    ESCALATE = "escalate_to_human"
    REJECT = "reject"


@dataclass(frozen=True)
class ThoughtProbe:
    text: str
    category: str
    intensity: float
    rationale: str


@dataclass(frozen=True)
class ProposedAction:
    """A canonical action proposal. Arbitrary executable code is excluded."""

    kind: str
    target: str
    parameters: tuple[tuple[str, str], ...] = ()

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvidenceLink:
    claim: str
    evidence_id: str
    excerpt_sha256: str


@dataclass(frozen=True)
class InferenceTelemetry:
    model_id: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_seconds: float

    def __post_init__(self) -> None:
        if not self.model_id:
            raise ValueError("telemetry model identity is required")
        if min(self.prompt_tokens, self.completion_tokens, self.total_tokens) < 0:
            raise ValueError("token counts cannot be negative")
        if self.prompt_tokens + self.completion_tokens != self.total_tokens:
            raise ValueError("prompt and completion tokens must sum to total tokens")
        if not math.isfinite(self.latency_seconds) or self.latency_seconds < 0:
            raise ValueError("latency must be a finite non-negative number")


@dataclass(frozen=True)
class ModelReview:
    provider: str
    verdict: Verdict
    summary: str
    action: ProposedAction | None = None
    claims: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    evidence_links: tuple[EvidenceLink, ...] = ()
    risks: tuple[str, ...] = ()
    critical_vetoes: tuple[str, ...] = ()
    confidence: float = 0.0
    telemetry: InferenceTelemetry | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class PeerReviewSummary:
    """Shareable review fields; free-form summary and hidden reasoning excluded."""

    provider: str
    verdict: Verdict
    action: ProposedAction | None
    action_fingerprint: str | None
    claims: tuple[str, ...]
    evidence: tuple[str, ...]
    evidence_links: tuple[EvidenceLink, ...]
    risks: tuple[str, ...]
    critical_vetoes: tuple[str, ...]
    confidence: float

    @classmethod
    def from_review(cls, review: ModelReview) -> "PeerReviewSummary":
        return cls(
            provider=review.provider,
            verdict=review.verdict,
            action=review.action,
            action_fingerprint=review.action.fingerprint if review.action else None,
            claims=review.claims,
            evidence=review.evidence,
            evidence_links=review.evidence_links,
            risks=review.risks,
            critical_vetoes=review.critical_vetoes,
            confidence=review.confidence,
        )

    def as_payload(self) -> dict:
        payload = asdict(self)
        payload["verdict"] = self.verdict.value
        return payload


@dataclass(frozen=True)
class ConsensusDecision:
    approved: bool
    status: Verdict
    reasons: tuple[str, ...]
    action: ProposedAction | None = None
