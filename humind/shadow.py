"""Bounded, adaptive counterthought generation."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib

from .schemas import ModelReview, ThoughtProbe


@dataclass(frozen=True)
class ShadowProfile:
    novelty: float = 0.4
    contradiction: float = 0.3
    risk_focus: float = 0.5
    evidence_scepticism: float = 0.6
    intensity_cap: float = 0.65

    def __post_init__(self) -> None:
        for name, value in vars(self).items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


class ShadowProbeGenerator:
    """Generates constructive adversity and learns which checks are useful.

    Adaptation changes only bounded numeric weights. It never rewrites its own
    instructions, executes tools, or treats a counterthought as a fact.
    """

    _TEMPLATES = (
        ("assumption", "Which hidden assumption would make this objective fail?"),
        ("evidence", "What evidence would contradict the preferred conclusion?"),
        ("risk", "Who or what could be harmed if this plan is wrong?"),
        ("alternative", "What cheaper or simpler explanation has been ignored?"),
        ("failure", "Describe a plausible failure mode and an early warning sign."),
    )

    def __init__(self, profile: ShadowProfile | None = None) -> None:
        self.profile = profile or ShadowProfile()

    def generate(self, objective: str, *, round_number: int = 0) -> ThoughtProbe:
        clean = " ".join(objective.split())
        if not clean:
            raise ValueError("objective must not be empty")
        digest = hashlib.sha256(f"{clean}:{round_number}".encode()).digest()
        category, prompt = self._TEMPLATES[digest[0] % len(self._TEMPLATES)]
        raw_intensity = (
            self.profile.contradiction
            + self.profile.risk_focus
            + self.profile.evidence_scepticism
        ) / 3
        intensity = min(self.profile.intensity_cap, raw_intensity)
        return ThoughtProbe(
            text=f"For the objective '{clean}': {prompt}",
            category=category,
            intensity=round(intensity, 3),
            rationale="Surface a neglected constraint without assuming the counterthought is true.",
        )

    def adapt(self, reviews: tuple[ModelReview, ModelReview]) -> ShadowProfile:
        left, right = reviews
        disagreement = left.verdict != right.verdict or (
            left.action is not None
            and right.action is not None
            and left.action.fingerprint != right.action.fingerprint
        )
        missed_evidence = not left.evidence or not right.evidence
        reported_risks = bool(left.risks or right.risks)

        def bounded(value: float) -> float:
            return round(min(1.0, max(0.0, value)), 3)

        self.profile = replace(
            self.profile,
            contradiction=bounded(self.profile.contradiction + (0.05 if disagreement else -0.02)),
            evidence_scepticism=bounded(
                self.profile.evidence_scepticism + (0.05 if missed_evidence else -0.02)
            ),
            risk_focus=bounded(self.profile.risk_focus + (0.03 if reported_risks else 0.01)),
        )
        return self.profile

