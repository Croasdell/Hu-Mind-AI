"""Hash-chained JSONL audit journal for offline experiment metadata."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any


GENESIS_HASH = "0" * 64


class AuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class AuditVerification:
    valid: bool
    record_count: int
    head_hash: str
    errors: tuple[str, ...] = ()


def _value(payload: Any) -> Any:
    return asdict(payload) if hasattr(payload, "__dataclass_fields__") else payload


def _canonical(record: dict) -> bytes:
    return json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")


class JsonlAuditLog:
    """Append records whose hashes commit to the complete preceding history."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _read_locked(self, handle) -> list[dict]:
        handle.seek(0)
        records = []
        for line_number, raw_line in enumerate(handle, 1):
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise AuditError(f"invalid JSON on audit line {line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise AuditError(f"audit line {line_number} is not an object")
            records.append(record)
        return records

    @staticmethod
    def verify_records(records: list[dict]) -> AuditVerification:
        previous = GENESIS_HASH
        errors: list[str] = []
        for index, record in enumerate(records):
            sequence = index + 1
            if record.get("sequence") != sequence:
                errors.append(f"record {sequence}: sequence mismatch")
            if record.get("previous_hash") != previous:
                errors.append(f"record {sequence}: previous hash mismatch")
            supplied = record.get("record_hash")
            unsigned = {key: value for key, value in record.items() if key != "record_hash"}
            calculated = hashlib.sha256(_canonical(unsigned)).hexdigest()
            if supplied != calculated:
                errors.append(f"record {sequence}: record hash mismatch")
            previous = str(supplied or calculated)
        return AuditVerification(not errors, len(records), previous, tuple(errors))

    def verify(self) -> AuditVerification:
        if not self.path.exists():
            return AuditVerification(True, 0, GENESIS_HASH)
        with self.path.open("r", encoding="utf-8") as handle:
            try:
                records = self._read_locked(handle)
            except AuditError as exc:
                return AuditVerification(False, 0, GENESIS_HASH, (str(exc),))
        return self.verify_records(records)

    def records(self) -> tuple[dict, ...]:
        if not self.path.exists():
            return ()
        with self.path.open("r", encoding="utf-8") as handle:
            records = self._read_locked(handle)
        verification = self.verify_records(records)
        if not verification.valid:
            raise AuditError("audit verification failed: " + "; ".join(verification.errors))
        return tuple(records)

    def create_checkpoint(self, key: bytes, *, created_at: str | None = None) -> dict:
        """Create an authenticated head for publication outside this journal."""
        if not key:
            raise AuditError("checkpoint key must not be empty")
        verification = self.verify()
        if not verification.valid:
            raise AuditError("cannot checkpoint an invalid audit chain")
        checkpoint = {
            "algorithm": "hmac-sha256",
            "created_at": created_at or datetime.now(timezone.utc).isoformat(),
            "record_count": verification.record_count,
            "head_hash": verification.head_hash,
        }
        checkpoint["signature"] = hmac.new(key, _canonical(checkpoint), hashlib.sha256).hexdigest()
        return checkpoint

    def verify_checkpoint(self, checkpoint: dict, key: bytes) -> AuditVerification:
        if not key or checkpoint.get("algorithm") != "hmac-sha256":
            return AuditVerification(False, 0, GENESIS_HASH, ("invalid checkpoint scheme or key",))
        signature = str(checkpoint.get("signature", ""))
        unsigned = {field: value for field, value in checkpoint.items() if field != "signature"}
        expected = hmac.new(key, _canonical(unsigned), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return AuditVerification(False, 0, GENESIS_HASH, ("checkpoint signature mismatch",))
        verification = self.verify()
        if not verification.valid:
            return verification
        errors = []
        if checkpoint.get("record_count") != verification.record_count:
            errors.append("checkpoint record count mismatch")
        if checkpoint.get("head_hash") != verification.head_hash:
            errors.append("checkpoint head hash mismatch")
        return AuditVerification(
            not errors,
            verification.record_count,
            verification.head_hash,
            tuple(errors),
        )

    def append(self, event: str, payload: Any, *, timestamp: str | None = None) -> str:
        if not event:
            raise AuditError("audit event is required")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            records = self._read_locked(handle)
            verification = self.verify_records(records)
            if not verification.valid:
                raise AuditError("refusing to append to invalid audit chain: " + "; ".join(verification.errors))
            record = {
                "sequence": len(records) + 1,
                "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
                "event": event,
                "payload": _value(payload),
                "previous_hash": verification.head_hash,
            }
            record["record_hash"] = hashlib.sha256(_canonical(record)).hexdigest()
            handle.seek(0, os.SEEK_END)
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            return record["record_hash"]
