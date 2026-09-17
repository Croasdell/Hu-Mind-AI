"""Reviewer adapter for a verified local OpenAI-compatible inference server."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import time

from .base import REVIEW_INSTRUCTIONS, review_from_json
from .http import ProviderError, post_json
from ..manifest import VerifiedModelManifest, load_and_verify_manifest
from ..offline import OfflineNetworkPolicy
from ..schemas import ModelReview, ThoughtProbe


@dataclass(frozen=True)
class InferenceBudget:
    max_input_chars: int = 32_768
    max_output_tokens: int = 2_048
    max_total_tokens: int = 8_192
    timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        if min(self.max_input_chars, self.max_output_tokens, self.max_total_tokens) <= 0:
            raise ValueError("inference budget limits must be positive")
        if self.max_output_tokens > self.max_total_tokens:
            raise ValueError("output token limit cannot exceed total token limit")
        if self.timeout_seconds <= 0:
            raise ValueError("inference timeout must be positive")


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
        budget: InferenceBudget | None = None,
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
        self.budget = budget or InferenceBudget()

    def review(self, objective: str, probe: ThoughtProbe) -> ModelReview:
        user_content = json.dumps({"objective": objective, "shadow_probe": probe.__dict__})
        input_chars = len(REVIEW_INSTRUCTIONS) + len(user_content)
        if input_chars > self.budget.max_input_chars:
            raise ProviderError(
                f"input budget exceeded: {input_chars} > {self.budget.max_input_chars} characters"
            )
        payload = {
            "model": self.manifest.endpoint_model,
            "messages": [
                {"role": "system", "content": REVIEW_INSTRUCTIONS},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
            "max_tokens": self.budget.max_output_tokens,
        }
        started = time.monotonic()
        response = post_json(
            f"{self.base_url}/chat/completions",
            self.api_key,
            payload,
            timeout=self.budget.timeout_seconds,
        )
        elapsed = time.monotonic() - started
        if elapsed > self.budget.timeout_seconds:
            raise ProviderError("local response exceeded the inference time budget")
        try:
            response_model = response["model"]
            total_tokens = int(response["usage"]["total_tokens"])
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError("local response omitted model identity, usage, or message content") from exc
        if response_model != self.manifest.endpoint_model:
            raise ProviderError(
                f"runtime model mismatch: expected {self.manifest.endpoint_model!r}, got {response_model!r}"
            )
        if total_tokens < 0 or total_tokens > self.budget.max_total_tokens:
            raise ProviderError(
                f"token budget exceeded: {total_tokens} > {self.budget.max_total_tokens}"
            )
        return review_from_json(self.name, content)
