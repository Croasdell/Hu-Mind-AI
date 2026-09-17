"""Append-only JSONL audit support for deliberation metadata."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


class JsonlAuditLog:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: str, payload: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        value = asdict(payload) if hasattr(payload, "__dataclass_fields__") else payload
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "payload": value,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

