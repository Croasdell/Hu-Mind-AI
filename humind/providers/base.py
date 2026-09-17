"""Provider contract for independent reviewers."""

from __future__ import annotations

import json
from typing import Any, Protocol

from .http import ProviderError
from ..schemas import ModelReview, ProposedAction, ThoughtProbe, Verdict


class ReviewerProvider(Protocol):
    name: str

    def review(self, objective: str, probe: ThoughtProbe) -> ModelReview:
        """Return a structured review without executing any proposed action."""


def review_from_json(provider: str, content: str) -> ModelReview:
    """Validate the common JSON contract returned by remote providers."""

    try:
        data: dict[str, Any] = json.loads(content)
        if not isinstance(data, dict):
            raise TypeError("review must be a JSON object")
        raw_action = data.get("action")
        action = None
        if raw_action is not None:
            if not isinstance(raw_action, dict):
                raise TypeError("action must be an object or null")
            raw_parameters = raw_action.get("parameters", {})
            if not isinstance(raw_parameters, dict):
                raise TypeError("action parameters must be an object")
            parameters = tuple(sorted((str(key), str(value)) for key, value in raw_parameters.items()))
            action = ProposedAction(
                kind=str(raw_action["kind"]),
                target=str(raw_action["target"]),
                parameters=parameters,
            )
        sequence_fields = ("claims", "assumptions", "evidence", "risks", "critical_vetoes")
        for field in sequence_fields:
            if field in data and not isinstance(data[field], list):
                raise TypeError(f"{field} must be an array")
        return ModelReview(
            provider=provider,
            verdict=Verdict(data["verdict"]),
            summary=str(data["summary"]),
            action=action,
            claims=tuple(map(str, data.get("claims", ()))),
            assumptions=tuple(map(str, data.get("assumptions", ()))),
            evidence=tuple(map(str, data.get("evidence", ()))),
            risks=tuple(map(str, data.get("risks", ()))),
            critical_vetoes=tuple(map(str, data.get("critical_vetoes", ()))),
            confidence=float(data.get("confidence", 0.0)),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ProviderError(f"invalid structured review: {exc}") from exc


REVIEW_INSTRUCTIONS = """You are one independent reviewer in a dual-review system.
Assess the objective and the supplied counterthought. Do not execute tools or claim
that agreement proves truth. Return JSON only with: verdict, summary, action,
claims, assumptions, evidence, risks, critical_vetoes, confidence. verdict must be
approve, revise, request_evidence, escalate_to_human, or reject. action must be null
or an object with kind, target, and string-valued parameters. Approve only when the
action is sufficiently evidenced, bounded, reversible where possible, and safe.
"""
