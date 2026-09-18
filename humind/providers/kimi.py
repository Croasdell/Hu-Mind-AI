"""Moonshot Kimi chat-completions reviewer adapter."""

from __future__ import annotations

import json

from .base import REVIEW_INSTRUCTIONS, review_from_json
from .http import ProviderError, post_json
from ..schemas import ModelReview, ThoughtProbe


class KimiReviewer:
    name = "kimi"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.moonshot.ai/v1",
        timeout: float = 60.0,
    ) -> None:
        if not api_key or not model:
            raise ValueError("api_key and model are required")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def review(self, objective: str, probe: ThoughtProbe) -> ModelReview:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": REVIEW_INSTRUCTIONS},
                {
                    "role": "user",
                    "content": json.dumps({"objective": objective, "shadow_probe": probe.__dict__}),
                },
            ],
            "response_format": {"type": "json_object"},
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
            raise ProviderError("Kimi response did not contain message content") from exc
        return review_from_json(self.name, content)

