"""Human and policy gate between model consensus and execution."""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import ConsensusDecision, ProposedAction


@dataclass(frozen=True)
class ActionAuthorization:
    allowed: bool
    action: ProposedAction | None
    reasons: tuple[str, ...]


class ActionGate:
    def __init__(self, allowed_kinds: set[str] | frozenset[str]) -> None:
        self.allowed_kinds = frozenset(allowed_kinds)

    def authorize(
        self,
        decision: ConsensusDecision,
        *,
        human_approved: bool,
    ) -> ActionAuthorization:
        reasons: list[str] = []
        if not decision.approved or decision.action is None:
            reasons.append("consensus has not approved an action")
        if not human_approved:
            reasons.append("human approval is required")
        if decision.action and decision.action.kind not in self.allowed_kinds:
            reasons.append(f"action kind '{decision.action.kind}' is not allowlisted")
        return ActionAuthorization(not reasons, decision.action if not reasons else None, tuple(reasons))

