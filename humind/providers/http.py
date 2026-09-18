"""Minimal standard-library JSON HTTP client with an offline boundary.

Every call re-validates the endpoint against the configured network policy,
follows only redirect targets that stay inside the boundary, and caps the
response body so a hostile or misbehaving provider cannot exhaust memory.
"""

from __future__ import annotations

import json
import math
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from ..offline import OfflineNetworkPolicy, OfflinePolicyError


class ProviderError(RuntimeError):
    pass


class _OfflineRedirectHandler(HTTPRedirectHandler):
    """Reject redirect targets that cross the offline deployment boundary."""

    def __init__(self, policy: OfflineNetworkPolicy, max_redirects: int = 3) -> None:
        super().__init__()
        self.policy = policy
        self.max_redirects = max_redirects
        self._count = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        if self._count >= self.max_redirects:
            raise ProviderError("too many redirects")
        try:
            self.policy.validate_url(newurl)
        except OfflinePolicyError as exc:
            raise ProviderError(
                f"redirect target left the offline boundary: {exc}"
            ) from exc
        self._count += 1
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _validate_timeout(timeout: float) -> None:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ProviderError("timeout must be a finite, positive number")


def _read_capped(response, max_bytes: int) -> bytes:
    if max_bytes <= 0:
        raise ProviderError("max_response_bytes must be positive")
    content_length = response.headers.get("Content-Length")
    if content_length is not None:
        try:
            declared = int(content_length)
        except ValueError:
            raise ProviderError("invalid Content-Length header") from None
        if declared > max_bytes:
            raise ProviderError("response body exceeds the configured size limit")
    buffer = bytearray()
    while True:
        chunk = response.read(65536)
        if not chunk:
            break
        buffer.extend(chunk)
        if len(buffer) > max_bytes:
            raise ProviderError("response body exceeds the configured size limit")
    return bytes(buffer)


def post_json(
    url: str,
    api_key: str | None,
    payload: dict,
    *,
    timeout: float = 60.0,
    network_policy: OfflineNetworkPolicy | None = None,
    max_response_bytes: int = 1_048_576,
    max_redirects: int = 3,
) -> dict:
    """POST JSON to a provider while enforcing the offline boundary.

    When a ``network_policy`` is supplied the URL is validated at call time
    and every redirect target is checked against it before it is followed,
    so credentials are never sent toward a host outside the boundary.
    All responses are capped at ``max_response_bytes`` to keep a single
    provider request bounded regardless of what it returns.
    """

    _validate_timeout(timeout)
    if max_response_bytes <= 0:
        raise ProviderError("max_response_bytes must be positive")

    if network_policy is not None:
        try:
            url = network_policy.validate_url(url)
        except OfflinePolicyError as exc:
            raise ProviderError(f"endpoint is outside the offline boundary: {exc}") from exc
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    handlers: list[HTTPRedirectHandler] = []
    if network_policy is not None:
        handlers.append(_OfflineRedirectHandler(network_policy, max_redirects=max_redirects))
    opener = build_opener(*handlers)

    try:
        with opener.open(request, timeout=timeout) as response:
            body = _read_capped(response, max_response_bytes)
            return json.loads(body.decode("utf-8"))
    except HTTPError as exc:
        raise ProviderError(f"provider rejected the request: {exc.code}") from exc
    except (URLError, TimeoutError) as exc:
        raise ProviderError("provider request failed") from exc
    except json.JSONDecodeError as exc:
        raise ProviderError(f"provider response was not valid JSON: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ProviderError("provider response was not valid UTF-8") from exc
