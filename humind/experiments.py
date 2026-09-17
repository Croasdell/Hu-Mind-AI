"""Preregistered experiment plans and results tied to the programme hypotheses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
import math

from .audit import AuditError, JsonlAuditLog


HYPOTHESIS_IDS = frozenset({"H1", "H2", "H3", "H4", "H5", "H6"})
OUTCOMES = frozenset({"supports", "contradicts", "inconclusive", "aborted"})


def _fingerprint(value: dict) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("experiment timestamps must include a timezone")
    return parsed


@dataclass(frozen=True)
class ExperimentPlan:
    title: str
    hypothesis_ids: tuple[str, ...]
    baseline: str
    primary_metrics: tuple[str, ...]
    success_criteria: tuple[str, ...]
    failure_criteria: tuple[str, ...]
    protocol_sha256: str
    dataset_sha256: str
    configuration_sha256: str
    preregistered_at: str

    def __post_init__(self) -> None:
        if not self.title or not self.baseline:
            raise ValueError("experiment title and baseline are required")
        if (
            not self.hypothesis_ids
            or len(self.hypothesis_ids) != len(set(self.hypothesis_ids))
            or not set(self.hypothesis_ids) <= HYPOTHESIS_IDS
        ):
            raise ValueError("experiment must reference only programme hypotheses H1-H6")
        if not self.primary_metrics or not self.success_criteria or not self.failure_criteria:
            raise ValueError("metrics and both decision criteria are required before registration")
        for digest in (self.protocol_sha256, self.dataset_sha256, self.configuration_sha256):
            if not _valid_digest(digest):
                raise ValueError("experiment artifact identities must be lowercase SHA-256 digests")
        _time(self.preregistered_at)

    @property
    def plan_id(self) -> str:
        return "exp-" + _fingerprint(asdict(self))[:20]

    def as_record(self) -> dict:
        return {"plan_id": self.plan_id, **asdict(self)}


@dataclass(frozen=True)
class ExperimentResult:
    run_id: str
    plan_id: str
    outcome: str
    metrics: tuple[tuple[str, float], ...]
    artifact_sha256s: tuple[str, ...]
    model_manifest_sha256s: tuple[str, ...]
    evidence_pack_sha256: str | None
    started_at: str
    completed_at: str
    reproduction_status: str
    conclusion: str
    failure_record_id: str | None = None

    def __post_init__(self) -> None:
        if not self.run_id or not self.plan_id or self.outcome not in OUTCOMES:
            raise ValueError("valid run, plan, and outcome are required")
        if not self.metrics or not self.artifact_sha256s or not self.model_manifest_sha256s:
            raise ValueError("metrics, result artifacts, and model manifests are required")
        metric_names = [name for name, _ in self.metrics]
        if len(metric_names) != len(set(metric_names)) or any(
            not name or not math.isfinite(value) for name, value in self.metrics
        ):
            raise ValueError("result metrics must have unique names and finite values")
        if self.outcome in {"contradicts", "aborted"} and not self.failure_record_id:
            raise ValueError("negative or aborted results require a failure-record ID")
        digests = (*self.artifact_sha256s, *self.model_manifest_sha256s)
        if self.evidence_pack_sha256:
            digests = (*digests, self.evidence_pack_sha256)
        if any(not _valid_digest(digest) for digest in digests):
            raise ValueError("result identities must be lowercase SHA-256 digests")
        if _time(self.completed_at) < _time(self.started_at):
            raise ValueError("experiment completion cannot precede its start")


class ExperimentLedger:
    def __init__(self, journal: JsonlAuditLog) -> None:
        self.journal = journal

    def register(self, plan: ExperimentPlan) -> str:
        records = self.journal.records()
        if any(
            record.get("event") == "experiment_plan_registered"
            and record.get("payload", {}).get("plan_id") == plan.plan_id
            for record in records
        ):
            raise AuditError(f"experiment plan already registered: {plan.plan_id}")
        self.journal.append("experiment_plan_registered", plan.as_record())
        return plan.plan_id

    def record_result(self, result: ExperimentResult) -> str:
        records = self.journal.records()
        plan_exists = any(
            record.get("event") == "experiment_plan_registered"
            and record.get("payload", {}).get("plan_id") == result.plan_id
            for record in records
        )
        if not plan_exists:
            raise AuditError(f"result refers to an unregistered plan: {result.plan_id}")
        if any(
            record.get("event") == "experiment_result_recorded"
            and record.get("payload", {}).get("run_id") == result.run_id
            for record in records
        ):
            raise AuditError(f"experiment run already recorded: {result.run_id}")
        return self.journal.append("experiment_result_recorded", result)
