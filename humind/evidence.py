"""Content-addressed evidence for the offline deliberation boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .schemas import ModelReview


class EvidenceError(ValueError):
    pass


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source_id: str
    locator: str
    excerpt: str
    document_sha256: str
    excerpt_sha256: str
    imported_at: str

    def as_payload(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EvidencePack:
    items: tuple[EvidenceItem, ...]

    def __post_init__(self) -> None:
        identifiers = [item.evidence_id for item in self.items]
        if len(identifiers) != len(set(identifiers)):
            raise EvidenceError("evidence IDs must be unique")

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            [item.as_payload() for item in self.items],
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def as_payload(self) -> list[dict]:
        return [item.as_payload() for item in self.items]

    def verification_issues(self, review: ModelReview) -> tuple[str, ...]:
        available = {item.evidence_id: item for item in self.items}
        issues: list[str] = []
        if not review.evidence_links:
            return ("review has no claim-linked evidence",)
        for link in review.evidence_links:
            item = available.get(link.evidence_id)
            if item is None:
                issues.append(f"unknown evidence ID: {link.evidence_id}")
                continue
            if link.claim not in review.claims:
                issues.append(f"evidence link refers to an undeclared claim: {link.claim}")
            if link.excerpt_sha256 != item.excerpt_sha256:
                issues.append(f"excerpt hash mismatch: {link.evidence_id}")
        return tuple(issues)


def import_text(
    text: str,
    *,
    source_id: str,
    excerpt: str,
    locator: str,
    imported_at: str | None = None,
    _document_sha256: str | None = None,
) -> EvidenceItem:
    if not source_id or not locator or not excerpt:
        raise EvidenceError("source_id, locator, and excerpt are required")
    if excerpt not in text:
        raise EvidenceError("excerpt does not occur in the imported document")
    document_hash = _document_sha256 or hashlib.sha256(text.encode("utf-8")).hexdigest()
    excerpt_hash = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
    identity = json.dumps(
        {
            "source_id": source_id,
            "locator": locator,
            "document_sha256": document_hash,
            "excerpt_sha256": excerpt_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    evidence_id = "ev-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
    timestamp = imported_at or datetime.now(timezone.utc).isoformat()
    return EvidenceItem(
        evidence_id,
        source_id,
        locator,
        excerpt,
        document_hash,
        excerpt_hash,
        timestamp,
    )


def import_document(
    path: str | Path,
    *,
    source_id: str,
    excerpt: str,
    locator: str,
    imported_at: str | None = None,
) -> EvidenceItem:
    document_path = Path(path)
    try:
        raw_document = document_path.read_bytes()
        text = raw_document.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise EvidenceError(f"cannot import evidence document: {exc}") from exc
    return import_text(
        text,
        source_id=source_id,
        excerpt=excerpt,
        locator=locator,
        imported_at=imported_at,
        _document_sha256=hashlib.sha256(raw_document).hexdigest(),
    )
