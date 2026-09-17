"""Reviewer adapter for a verified local OpenAI-compatible inference server."""

from __future__ import annotations

import json
from pathlib import Path

from .base import REVIEW_INSTRUCTIONS, review_from_json
from .http import ProviderError, post_json
from ..manifest import VerifiedModelManifest, load_and_verify_manifest
from ..offline import OfflineNetworkPolicy
from ..schemas import ModelReview, ThoughtProbe


class LocalReviewer:
    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        manifest_path: str | Path,
        manifest_key: bytes,
        role: str,
        network_policy: OfflineNetworkPolicy | None = None,
        api_key: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        if not name:
            raise ValueError("a distinct reviewer name is required")
        self.name = name
        self.base_url = (network_policy or OfflineNetworkPolicy()).validate_url(base_url)
        self.manifest: VerifiedModelManifest = load_and_verify_manifest(manifest_path, manifest_key)
        if role not in self.manifest.roles:
            raise ValueError(f"manifest does not approve role {role!r}")
        self.role = role
        self.api_key = api_key
        self.timeout = timeout

    def review(self, objective: str, probe: ThoughtProbe) -> ModelReview:
        payload = {
            "model": self.manifest.endpoint_model,
            "messages": [
                {"role": "system", "content": REVIEW_INSTRUCTIONS},
                {"role": "user", "content": json.dumps({"objective": objective, "shadow_probe": probe.__dict__})},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }
        response = post_json(
            f"{self.base_url}/chat/completions",
            self.api_key,
            payload,
            timeout=self.timeout,
        )
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("local response did not contain message content") from exc
        return review_from_json(self.name, content)
