import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from humind.manifest import ManifestError, load_and_verify_manifest, sign_manifest
from humind.offline import OfflineNetworkPolicy, OfflinePolicyError
from humind.providers.http import ProviderError
from humind.providers.local import InferenceBudget, LocalReviewer
from humind.schemas import ModelReview, PeerReviewSummary, Verdict


class OfflinePolicyTests(unittest.TestCase):
    def test_loopback_is_allowed_and_public_network_is_denied(self):
        policy = OfflineNetworkPolicy()
        self.assertEqual(policy.validate_url("http://127.0.0.1:8000/v1"), "http://127.0.0.1:8000/v1")
        with self.assertRaises(OfflinePolicyError):
            policy.validate_url("https://api.openai.com/v1")

    def test_isolated_network_must_be_explicit(self):
        policy = OfflineNetworkPolicy(allowed_networks=("10.44.0.0/24",))
        self.assertEqual(policy.validate_url("http://10.44.0.8:8000/v1"), "http://10.44.0.8:8000/v1")
        with self.assertRaises(OfflinePolicyError):
            policy.validate_url("http://10.45.0.8:8000/v1")


class ManifestAndLocalProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.artifact = self.root / "weights.bin"
        self.artifact.write_bytes(b"offline-model-fixture")
        self.key = b"test-provisioning-key"

    def tearDown(self):
        self.temp.cleanup()

    def write_manifest(self):
        data = {
            "schema_version": 1,
            "model_id": "fixture/model-a",
            "revision": "exact-revision-1",
            "source": "controlled test fixture",
            "license": "test-only",
            "runtime": "local-compatible-server",
            "endpoint_model": "model-a",
            "quantization": "fixture",
            "hardware_requirements": {"vram_gb": 1},
            "evaluation_status": "unvalidated fixture",
            "roles": ["reviewer-left"],
            "artifacts": [{"path": "weights.bin", "sha256": hashlib.sha256(self.artifact.read_bytes()).hexdigest()}],
        }
        path = self.root / "manifest.json"
        path.write_text(json.dumps(sign_manifest(data, self.key)), encoding="utf-8")
        return path

    def reviewer(self, **kwargs):
        return LocalReviewer(
            name="local-a",
            base_url="http://127.0.0.1:8000/v1",
            manifest_path=self.write_manifest(),
            manifest_key=self.key,
            role="reviewer-left",
            **kwargs,
        )

    @staticmethod
    def valid_response(**overrides):
        response = {
            "model": "model-a",
            "usage": {"total_tokens": 120},
            "choices": [{"message": {"content": '{"verdict":"request_evidence","summary":"need proof","action":null,"confidence":0.4}'}}],
        }
        response.update(overrides)
        return response

    def test_signed_manifest_and_artifact_are_verified(self):
        verified = load_and_verify_manifest(self.write_manifest(), self.key)
        self.assertEqual(verified.endpoint_model, "model-a")

    def test_tampered_artifact_fails_closed(self):
        path = self.write_manifest()
        self.artifact.write_bytes(b"tampered")
        with self.assertRaisesRegex(ManifestError, "hash mismatch"):
            load_and_verify_manifest(path, self.key)

    def test_local_reviewer_uses_verified_model_and_loopback_only(self):
        reviewer = self.reviewer()
        response = self.valid_response()
        with patch("humind.providers.local.post_json", return_value=response) as request:
            review = reviewer.review("objective", type("Probe", (), {"__dict__": {"text": "test"}})())
        self.assertEqual(review.provider, "local-a")
        self.assertEqual(request.call_args.args[2]["model"], "model-a")
        self.assertEqual(request.call_args.args[2]["max_tokens"], 2_048)

    def test_runtime_model_mismatch_fails_closed(self):
        with patch("humind.providers.local.post_json", return_value=self.valid_response(model="wrong-model")):
            with self.assertRaisesRegex(ProviderError, "model mismatch"):
                self.reviewer().review("objective", type("Probe", (), {"__dict__": {}})())

    def test_missing_usage_and_malformed_review_fail_closed(self):
        response = self.valid_response()
        del response["usage"]
        with patch("humind.providers.local.post_json", return_value=response):
            with self.assertRaisesRegex(ProviderError, "omitted"):
                self.reviewer().review("objective", type("Probe", (), {"__dict__": {}})())
        malformed = self.valid_response()
        malformed["choices"][0]["message"]["content"] = "not-json"
        with patch("humind.providers.local.post_json", return_value=malformed):
            with self.assertRaisesRegex(ProviderError, "invalid structured review"):
                self.reviewer().review("objective", type("Probe", (), {"__dict__": {}})())

    def test_input_and_total_token_budgets_fail_closed(self):
        tiny_input = self.reviewer(budget=InferenceBudget(max_input_chars=10))
        with self.assertRaisesRegex(ProviderError, "input budget exceeded"):
            tiny_input.review("objective", type("Probe", (), {"__dict__": {}})())
        response = self.valid_response(usage={"total_tokens": 8_193})
        with patch("humind.providers.local.post_json", return_value=response):
            with self.assertRaisesRegex(ProviderError, "token budget exceeded"):
                self.reviewer().review("objective", type("Probe", (), {"__dict__": {}})())

    def test_provider_loss_produces_no_review(self):
        with patch("humind.providers.local.post_json", side_effect=ProviderError("provider unavailable")):
            with self.assertRaisesRegex(ProviderError, "provider unavailable"):
                self.reviewer().review("objective", type("Probe", (), {"__dict__": {}})())

    def test_local_revision_transmits_only_redacted_positions(self):
        reviewer = self.reviewer()
        own = PeerReviewSummary.from_review(
            ModelReview("local-a", Verdict.REVISE, "private own narrative", claims=("claim-a",))
        )
        peer = PeerReviewSummary.from_review(
            ModelReview("local-b", Verdict.REJECT, "private peer narrative", risks=("risk-b",))
        )
        with patch("humind.providers.local.post_json", return_value=self.valid_response()) as request:
            reviewer.revise("objective", type("Probe", (), {"__dict__": {}})(), own, peer)
        encoded = request.call_args.args[2]["messages"][1]["content"]
        self.assertIn("claim-a", encoded)
        self.assertIn("risk-b", encoded)
        self.assertNotIn("private own narrative", encoded)
        self.assertNotIn("private peer narrative", encoded)

    def test_elapsed_time_budget_fails_closed(self):
        budget = InferenceBudget(timeout_seconds=0.5)
        with patch("humind.providers.local.post_json", return_value=self.valid_response()):
            with patch("humind.providers.local.time.monotonic", side_effect=(10.0, 10.6)):
                with self.assertRaisesRegex(ProviderError, "time budget"):
                    self.reviewer(budget=budget).review(
                        "objective", type("Probe", (), {"__dict__": {}})()
                    )

    def test_external_endpoint_is_rejected_before_manifest_use(self):
        with self.assertRaises(OfflinePolicyError):
            LocalReviewer(
                name="local-a",
                base_url="https://api.example.com/v1",
                manifest_path=self.root / "missing.json",
                manifest_key=self.key,
                role="reviewer-left",
            )


if __name__ == "__main__":
    unittest.main()
