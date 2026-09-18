"""Tests for the bounded, policy-enforcing HTTP provider client."""

from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from humind.offline import OfflineNetworkPolicy
from humind.providers.http import ProviderError, post_json


class _TestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return None

    def do_POST(self):
        if self.path == "/ok":
            self._send_json({"ok": True})
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "http://example.com/external")
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif self.path == "/big":
            body = b"x" * 100
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/error":
            self.send_response(500)
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class HttpClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _TestHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def test_post_json_succeeds_for_loopback_server(self):
        result = post_json(
            self.url("/ok"),
            None,
            {"value": 1},
            network_policy=OfflineNetworkPolicy(),
            timeout=10,
        )
        self.assertEqual(result, {"ok": True})

    def test_endpoint_outside_offline_policy_is_rejected(self):
        with self.assertRaisesRegex(ProviderError, "outside the offline boundary"):
            post_json(
                "http://example.com/",
                None,
                {},
                network_policy=OfflineNetworkPolicy(),
                timeout=10,
            )

    def test_redirect_to_external_host_is_rejected_before_credentials_are_sent(self):
        with self.assertRaisesRegex(ProviderError, "redirect target left the offline boundary"):
            post_json(
                self.url("/redirect"),
                "secret-key",
                {},
                network_policy=OfflineNetworkPolicy(),
                timeout=10,
            )

    def test_oversized_response_is_rejected(self):
        with self.assertRaisesRegex(ProviderError, "size limit"):
            post_json(
                self.url("/big"),
                None,
                {},
                network_policy=OfflineNetworkPolicy(),
                timeout=10,
                max_response_bytes=8,
            )

    def test_non_positive_timeout_is_rejected(self):
        with self.assertRaisesRegex(ProviderError, "timeout must be a finite, positive number"):
            post_json(
                self.url("/ok"),
                None,
                {},
                network_policy=OfflineNetworkPolicy(),
                timeout=0,
            )

    def test_non_finite_timeout_is_rejected(self):
        with self.assertRaisesRegex(ProviderError, "timeout must be a finite, positive number"):
            post_json(
                self.url("/ok"),
                None,
                {},
                network_policy=OfflineNetworkPolicy(),
                timeout=float("inf"),
            )

    def test_api_key_is_not_leaked_in_error_message(self):
        with self.assertRaises(ProviderError) as raised:
            post_json(
                self.url("/error"),
                "secret-key",
                {},
                network_policy=OfflineNetworkPolicy(),
                timeout=10,
            )
        self.assertNotIn("secret-key", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
