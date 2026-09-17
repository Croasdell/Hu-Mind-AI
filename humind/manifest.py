"""Model artifact manifests for controlled offline provisioning."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    pass


def _canonical(data: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in data.items() if key != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class VerifiedModelManifest:
    model_id: str
    revision: str
    runtime: str
    endpoint_model: str
    roles: tuple[str, ...]
    path: Path


def sign_manifest(data: dict[str, Any], key: bytes) -> dict[str, Any]:
    """Return a copy carrying a detached-style HMAC-SHA256 signature.

    HMAC is used for the prototype's controlled provisioning path. A consortium
    deployment should replace this shared-key scheme with threshold/public-key
    signatures while retaining the canonical payload.
    """

    if not key:
        raise ManifestError("signing key must not be empty")
    signed = dict(data)
    signed["signature"] = {
        "algorithm": "hmac-sha256",
        "value": hmac.new(key, _canonical(data), hashlib.sha256).hexdigest(),
    }
    return signed


def load_and_verify_manifest(path: str | Path, key: bytes, *, verify_files: bool = True) -> VerifiedModelManifest:
    manifest_path = Path(path).resolve()
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read model manifest: {exc}") from exc

    required = {
        "schema_version", "model_id", "revision", "source", "license",
        "runtime", "endpoint_model", "quantization", "hardware_requirements",
        "evaluation_status", "roles", "artifacts", "signature",
    }
    missing = required.difference(data)
    if missing:
        raise ManifestError(f"manifest is missing: {', '.join(sorted(missing))}")
    if data["schema_version"] != 1:
        raise ManifestError("unsupported manifest schema version")
    signature = data["signature"]
    if not isinstance(signature, dict) or signature.get("algorithm") != "hmac-sha256":
        raise ManifestError("unsupported manifest signature")
    expected = hmac.new(key, _canonical(data), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(signature.get("value", "")), expected):
        raise ManifestError("model manifest signature is invalid")

    if verify_files:
        if not isinstance(data["artifacts"], list) or not data["artifacts"]:
            raise ManifestError("at least one model artifact is required")
        for artifact in data["artifacts"]:
            if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256"}:
                raise ManifestError("each artifact requires only path and sha256")
            artifact_path = (manifest_path.parent / str(artifact["path"])).resolve()
            if manifest_path.parent not in artifact_path.parents:
                raise ManifestError("artifact path escapes the manifest directory")
            try:
                digest = _sha256_file(artifact_path)
            except OSError as exc:
                raise ManifestError(f"cannot read artifact {artifact_path.name}: {exc}") from exc
            if not hmac.compare_digest(digest, str(artifact["sha256"])):
                raise ManifestError(f"artifact hash mismatch: {artifact_path.name}")

    roles = tuple(map(str, data["roles"]))
    if not roles:
        raise ManifestError("at least one approved role is required")
    return VerifiedModelManifest(
        model_id=str(data["model_id"]),
        revision=str(data["revision"]),
        runtime=str(data["runtime"]),
        endpoint_model=str(data["endpoint_model"]),
        roles=roles,
        path=manifest_path,
    )
