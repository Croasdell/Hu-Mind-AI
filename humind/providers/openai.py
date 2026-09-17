"""OpenAI Responses API reviewer adapter."""

from __future__ import annotations

import json

from .base import REVIEW_INSTRUCTIONS, review_from_json
from .http import ProviderError, post_json
from ..schemas import ModelReview, ThoughtProbe


class OpenAIReviewer:
    name = "openai"

    def __init__(self, *, api_key: str, model: str, timeout: float = 60.0) -> None:
        if not api_key or not model:
            raise ValueError("api_key and model are required")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def review(self, objective: str, probe: ThoughtProbe) -> ModelReview:
        payload = {
            "model": self.model,
            "instructions": REVIEW_INSTRUCTIONS,
            "input": json.dumps({"objective": objective, "shadow_probe": probe.__dict__}),
            "store": False,
            "text": {"format": {"type": "json_object"}},
        }
        response = post_json(
            "https://api.openai.com/v1/responses",
            self.api_key,
            payload,
            timeout=self.timeout,
        )
        for item in response.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return review_from_json(self.name, content["text"])
        raise ProviderError("OpenAI response did not contain output_text")

