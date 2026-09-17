"""Provider contract for independent reviewers."""

from __future__ import annotations

import json
from typing import Any, Protocol, runtime_checkable

from .http import ProviderError
from ..schemas import EvidenceLink, ModelReview, PeerReviewSummary, ProposedAction, ThoughtProbe, Verdict


class ReviewerProvider(Protocol):
    name: str

    def review(self, objective: str, probe: ThoughtProbe) -> ModelReview:
        """Return a structured review without executing any proposed action."""


@runtime_checkable
class RevisionProvider(Protocol):
    name: str

    def revise(
        self,
        objective: str,
        probe: ThoughtProbe,
        own_position: PeerReviewSummary,
        peer_position: PeerReviewSummary,
    ) -> ModelReview:
        """Reassess using bounded structured positions, never private reasoning."""


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
        raw_links = data.get("evidence_links", [])
        if not isinstance(raw_links, list):
            raise TypeError("evidence_links must be an array")
        evidence_links = tuple(
            EvidenceLink(
                claim=str(link["claim"]),
                evidence_id=str(link["evidence_id"]),
                excerpt_sha256=str(link["excerpt_sha256"]),
            )
            for link in raw_links
            if isinstance(link, dict)
        )
        if len(evidence_links) != len(raw_links):
            raise TypeError("each evidence link must be an object")
        return ModelReview(
            provider=provider,
            verdict=Verdict(data["verdict"]),
            summary=str(data["summary"]),
            action=action,
            claims=tuple(map(str, data.get("claims", ()))),
            assumptions=tuple(map(str, data.get("assumptions", ()))),
            evidence=tuple(map(str, data.get("evidence", ()))),
            evidence_links=evidence_links,
            risks=tuple(map(str, data.get("risks", ()))),
            critical_vetoes=tuple(map(str, data.get("critical_vetoes", ()))),
            confidence=float(data.get("confidence", 0.0)),
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ProviderError(f"invalid structured review: {exc}") from exc


REVIEW_INSTRUCTIONS = """You are one independent reviewer in a dual-review system.
Assess the objective and the supplied counterthought. Do not execute tools or claim
that agreement proves truth. Return JSON only with: verdict, summary, action,
claims, assumptions, evidence, evidence_links, risks, critical_vetoes, confidence. verdict must be
approve, revise, request_evidence, escalate_to_human, or reject. action must be null
or an object with kind, target, and string-valued parameters. evidence_links must
contain claim, evidence_id, and excerpt_sha256 copied from the supplied evidence
pack. Approve only when the action is sufficiently evidenced, bounded, reversible
where possible, and safe. Never invent an evidence ID, excerpt, or hash.
"""


REVISION_INSTRUCTIONS = REVIEW_INSTRUCTIONS + """
This is the single permitted peer-critique round. You receive redacted structured
positions, not private reasoning. Reassess the evidence and action independently.
Do not agree merely to reach consensus. Preserve any unresolved critical veto.
"""
