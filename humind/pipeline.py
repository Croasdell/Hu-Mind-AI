"""Deterministic scaffolding for Hu-Mind's creative/reviewer pipeline."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Candidate:
    """A proposal produced by the creative stage."""

    text: str
    rationale: str = ""
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class Review:
    """A structured decision produced by the logic stage."""

    candidate: Candidate
    score: float
    accepted: bool
    issues: tuple[str, ...] = ()

    @property
    def decision(self) -> str:
        """Human-readable next step for the terminal operator."""

        if self.accepted:
            return "act"
        if self.score > 0:
            return "keep"
        return "reject"


def review_candidates(
    candidates: Iterable[Candidate],
    *,
    minimum_score: float = 0.7,
) -> list[Review]:
    """Apply the baseline gate used before a model-backed reviewer is added.

    This deliberately does not pretend to establish truth. It only enforces
    that proposals are non-empty, explainable, and (for now) sourced.
    """

    if not 0 <= minimum_score <= 1:
        raise ValueError("minimum_score must be between 0 and 1")

    results: list[Review] = []
    for candidate in candidates:
        issues: list[str] = []
        if not candidate.text.strip():
            issues.append("empty proposal")
        if not candidate.rationale.strip():
            issues.append("missing rationale")
        if not candidate.sources:
            issues.append("no provenance supplied")
        score = 0.0 if "empty proposal" in issues else (1.0 if not issues else max(0.0, 1.0 - 0.3 * len(issues)))
        results.append(
            Review(
                candidate=candidate,
                score=score,
                accepted=score >= minimum_score and not issues,
                issues=tuple(issues),
            )
        )
    return results
