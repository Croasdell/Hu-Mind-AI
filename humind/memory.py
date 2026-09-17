"""Event-sourced, provenance-aware memory for controlled H4 experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
import math

from .audit import AuditError, JsonlAuditLog
from .evidence import EvidencePack


class MemoryPolicyError(ValueError):
    pass


class MemoryKind(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    AUDIT = "audit"


def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise MemoryPolicyError(f"invalid memory timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise MemoryPolicyError("memory timestamps must include a timezone")
    return parsed


def _digest(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class MemoryEntry:
    kind: MemoryKind
    subject: str
    content: str
    provenance_ids: tuple[str, ...]
    evidence_pack_sha256: str
    confidence: float
    created_at: str
    supersedes: str | None = None
    expires_at: str | None = None

    def __post_init__(self) -> None:
        if not self.subject.strip() or not self.content.strip():
            raise MemoryPolicyError("memory subject and content are required")
        if not self.provenance_ids or len(self.provenance_ids) != len(set(self.provenance_ids)):
            raise MemoryPolicyError("memory provenance IDs must be present and unique")
        if len(self.evidence_pack_sha256) != 64:
            raise MemoryPolicyError("memory requires an evidence-pack SHA-256")
        if not math.isfinite(self.confidence) or not 0.0 <= self.confidence <= 1.0:
            raise MemoryPolicyError("memory confidence must be between zero and one")
        created = _parse_time(self.created_at)
        if self.expires_at and _parse_time(self.expires_at) <= created:
            raise MemoryPolicyError("memory expiry must be after creation")

    @property
    def memory_id(self) -> str:
        return "mem-" + _digest(asdict(self))[:20]

    def as_record(self) -> dict:
        value = asdict(self)
        value["kind"] = self.kind.value
        return {"memory_id": self.memory_id, **value}


@dataclass(frozen=True)
class RecalledMemory:
    entry: MemoryEntry
    effective_confidence: float


@dataclass(frozen=True)
class RecallResult:
    memories: tuple[RecalledMemory, ...]
    conflict_subjects: tuple[str, ...]


class MemoryLedger:
    """Memory writes are events; prior content is never updated in place."""

    def __init__(self, journal: JsonlAuditLog, evidence_packs: tuple[EvidencePack, ...]) -> None:
        self.journal = journal
        self._packs = {pack.fingerprint: pack for pack in evidence_packs}
        if len(self._packs) != len(evidence_packs):
            raise MemoryPolicyError("evidence-pack fingerprints must be unique")

    def _verify_provenance(self, entry: MemoryEntry) -> None:
        self._verify_ids(entry.provenance_ids, entry.evidence_pack_sha256)

    def _verify_ids(self, provenance_ids: tuple[str, ...], pack_sha256: str) -> None:
        pack = self._packs.get(pack_sha256)
        if pack is None:
            raise MemoryPolicyError("memory refers to an unavailable evidence pack")
        known = {item.evidence_id for item in pack.items}
        unknown = set(provenance_ids).difference(known)
        if unknown:
            raise MemoryPolicyError("unknown memory provenance: " + ", ".join(sorted(unknown)))

    def _entries_and_retractions(self) -> tuple[dict[str, MemoryEntry], set[str]]:
        entries: dict[str, MemoryEntry] = {}
        retracted: set[str] = set()
        superseded: set[str] = set()
        for record in self.journal.records():
            payload = record.get("payload", {})
            if record.get("event") == "memory_added":
                try:
                    memory_id = str(payload["memory_id"])
                    authority = str(payload["write_authority"])
                    entry = MemoryEntry(
                        kind=MemoryKind(payload["kind"]),
                        subject=str(payload["subject"]),
                        content=str(payload["content"]),
                        provenance_ids=tuple(map(str, payload["provenance_ids"])),
                        evidence_pack_sha256=str(payload["evidence_pack_sha256"]),
                        confidence=float(payload["confidence"]),
                        created_at=str(payload["created_at"]),
                        supersedes=str(payload["supersedes"]) if payload.get("supersedes") else None,
                        expires_at=str(payload["expires_at"]) if payload.get("expires_at") else None,
                    )
                except (KeyError, TypeError, ValueError) as exc:
                    raise AuditError(f"invalid memory event: {exc}") from exc
                if memory_id != entry.memory_id or memory_id in entries:
                    raise AuditError("memory identity mismatch or duplicate")
                if authority not in {"human", "system-observation"}:
                    raise AuditError("invalid memory write authority")
                if entry.kind in {MemoryKind.SEMANTIC, MemoryKind.PROCEDURAL} and authority != "human":
                    raise AuditError("durable semantic/procedural memory lacks human authority")
                if entry.supersedes:
                    old = entries.get(entry.supersedes)
                    if old is None or entry.supersedes in retracted or entry.supersedes in superseded:
                        raise AuditError("memory correction does not reference an active prior entry")
                    if entry.kind is not old.kind or entry.subject != old.subject:
                        raise AuditError("memory correction changed kind or subject")
                    if _parse_time(entry.created_at) <= _parse_time(old.created_at):
                        raise AuditError("memory correction predates prior entry")
                    if authority != "human":
                        raise AuditError("memory correction lacks human authority")
                    superseded.add(entry.supersedes)
                self._verify_provenance(entry)
                entries[memory_id] = entry
            elif record.get("event") == "memory_retracted":
                memory_id = str(payload.get("memory_id", ""))
                if memory_id not in entries or memory_id in retracted or memory_id in superseded:
                    raise AuditError(f"retraction refers to unknown memory: {memory_id}")
                try:
                    provenance_ids = tuple(map(str, payload["provenance_ids"]))
                    pack_sha256 = str(payload["evidence_pack_sha256"])
                except (KeyError, TypeError) as exc:
                    raise AuditError(f"invalid memory retraction: {exc}") from exc
                if payload.get("write_authority") != "human":
                    raise AuditError("memory retraction lacks human authority")
                self._verify_ids(provenance_ids, pack_sha256)
                retracted.add(memory_id)
        return entries, retracted

    def add(self, entry: MemoryEntry, *, human_approved: bool = False) -> str:
        if entry.supersedes:
            raise MemoryPolicyError("use correct() to supersede an existing memory")
        if entry.kind in {MemoryKind.SEMANTIC, MemoryKind.PROCEDURAL} and not human_approved:
            raise MemoryPolicyError("semantic and procedural memory require human approval")
        self._verify_provenance(entry)
        entries, _ = self._entries_and_retractions()
        if entry.memory_id in entries:
            raise MemoryPolicyError(f"memory already exists: {entry.memory_id}")
        payload = {**entry.as_record(), "write_authority": "human" if human_approved else "system-observation"}
        self.journal.append("memory_added", payload)
        return entry.memory_id

    def correct(self, old_memory_id: str, replacement: MemoryEntry, *, human_approved: bool) -> str:
        if not human_approved:
            raise MemoryPolicyError("memory correction requires human approval")
        entries, retracted = self._entries_and_retractions()
        old = entries.get(old_memory_id)
        superseded = {entry.supersedes for entry in entries.values() if entry.supersedes}
        if old is None or old_memory_id in retracted or old_memory_id in superseded:
            raise MemoryPolicyError("only an active known memory can be corrected")
        if replacement.supersedes != old_memory_id:
            raise MemoryPolicyError("replacement must explicitly supersede the old memory")
        if replacement.kind is not old.kind or replacement.subject != old.subject:
            raise MemoryPolicyError("correction must retain memory kind and subject")
        if _parse_time(replacement.created_at) <= _parse_time(old.created_at):
            raise MemoryPolicyError("correction must be created after the old memory")
        self._verify_provenance(replacement)
        if replacement.memory_id in entries:
            raise MemoryPolicyError("replacement memory already exists")
        self.journal.append(
            "memory_added",
            {**replacement.as_record(), "write_authority": "human"},
        )
        return replacement.memory_id

    def retract(
        self,
        memory_id: str,
        *,
        reason: str,
        provenance_ids: tuple[str, ...],
        evidence_pack_sha256: str,
        human_approved: bool,
    ) -> None:
        if not human_approved:
            raise MemoryPolicyError("memory retraction requires human approval")
        entries, retracted = self._entries_and_retractions()
        superseded = {entry.supersedes for entry in entries.values() if entry.supersedes}
        if memory_id not in entries or memory_id in retracted or memory_id in superseded:
            raise MemoryPolicyError("only an active known memory can be retracted")
        if not reason.strip() or not provenance_ids:
            raise MemoryPolicyError("retraction reason and provenance are required")
        self._verify_ids(provenance_ids, evidence_pack_sha256)
        self.journal.append(
            "memory_retracted",
            {
                "memory_id": memory_id,
                "reason": reason,
                "provenance_ids": provenance_ids,
                "evidence_pack_sha256": evidence_pack_sha256,
                "write_authority": "human",
            },
        )

    def recall(
        self,
        *,
        as_of: str,
        subject: str | None = None,
        kind: MemoryKind | None = None,
        half_life_days: float = 90.0,
    ) -> RecallResult:
        if not math.isfinite(half_life_days) or half_life_days <= 0:
            raise MemoryPolicyError("memory half-life must be positive")
        now = _parse_time(as_of)
        entries, retracted = self._entries_and_retractions()
        superseded = {entry.supersedes for entry in entries.values() if entry.supersedes}
        active = []
        for memory_id, entry in entries.items():
            if memory_id in retracted or memory_id in superseded:
                continue
            if subject is not None and entry.subject != subject:
                continue
            if kind is not None and entry.kind is not kind:
                continue
            if entry.expires_at and _parse_time(entry.expires_at) <= now:
                continue
            created = _parse_time(entry.created_at)
            if created > now:
                continue
            age_days = (now - created).total_seconds() / 86_400
            effective = entry.confidence * (0.5 ** (age_days / half_life_days))
            active.append(RecalledMemory(entry, effective))
        active.sort(key=lambda item: (-item.effective_confidence, item.entry.memory_id))
        grouped: dict[tuple[MemoryKind, str], set[str]] = {}
        for recalled in active:
            key = (recalled.entry.kind, recalled.entry.subject)
            grouped.setdefault(key, set()).add(recalled.entry.content)
        conflicts = tuple(
            sorted(f"{memory_kind.value}:{memory_subject}" for (memory_kind, memory_subject), values in grouped.items() if len(values) > 1)
        )
        return RecallResult(tuple(active), conflicts)
