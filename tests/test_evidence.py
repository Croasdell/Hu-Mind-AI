import hashlib
import tempfile
from pathlib import Path
import unittest

from humind.deliberation import DeliberationEngine
from humind.evidence import EvidenceError, EvidencePack, import_document, import_text
from humind.providers.mock import MockReviewer
from humind.schemas import EvidenceLink, ModelReview, ProposedAction, Verdict


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.item = import_text(
            "The controlled benchmark completed 100 cases. No action tools were enabled.",
            source_id="benchmark-report-v1",
            excerpt="The controlled benchmark completed 100 cases.",
            locator="line 1",
            imported_at="2026-09-17T12:00:00+00:00",
        )
        self.pack = EvidencePack((self.item,))
        self.action = ProposedAction("run_experiment", "next-benchmark")

    def review(self, provider, *, evidence_id=None, excerpt_hash=None, claim=None):
        supported_claim = claim or "The controlled benchmark completed 100 cases."
        link = EvidenceLink(
            supported_claim,
            evidence_id or self.item.evidence_id,
            excerpt_hash or self.item.excerpt_sha256,
        )
        return ModelReview(
            provider,
            Verdict.APPROVE,
            "Evidence supports a bounded follow-up.",
            action=self.action,
            claims=(supported_claim,),
            evidence_links=(link,),
            confidence=0.9,
        )

    def engine(self, left, right):
        return DeliberationEngine(
            MockReviewer(left),
            MockReviewer(right),
            evidence_pack=self.pack,
            require_verified_evidence=True,
        )

    def test_content_address_is_stable_for_same_source_material(self):
        duplicate = import_text(
            "The controlled benchmark completed 100 cases. No action tools were enabled.",
            source_id="benchmark-report-v1",
            excerpt="The controlled benchmark completed 100 cases.",
            locator="line 1",
            imported_at="2027-01-01T00:00:00+00:00",
        )
        self.assertEqual(duplicate.evidence_id, self.item.evidence_id)
        self.assertEqual(duplicate.document_sha256, self.item.document_sha256)

    def test_excerpt_must_exist_in_imported_document(self):
        with self.assertRaisesRegex(EvidenceError, "does not occur"):
            import_text("actual text", source_id="source", excerpt="invented", locator="line 1")

    def test_document_import_records_document_and_excerpt_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.txt"
            path.write_text("verified offline result", encoding="utf-8")
            item = import_document(
                path,
                source_id="local-report",
                excerpt="offline result",
                locator="line 1",
                imported_at="2026-09-17T12:00:00+00:00",
            )
        self.assertEqual(len(item.document_sha256), 64)
        self.assertEqual(len(item.excerpt_sha256), 64)

    def test_document_hash_covers_exact_file_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.txt"
            path.write_bytes(b"line one\r\nline two")
            item = import_document(
                path,
                source_id="byte-exact-report",
                excerpt="line one\r\nline two",
                locator="whole file",
                imported_at="2026-09-17T12:00:00+00:00",
            )
        self.assertEqual(item.document_sha256, hashlib.sha256(b"line one\r\nline two").hexdigest())

    def test_verified_claim_links_allow_consensus(self):
        result = self.engine(self.review("left"), self.review("right")).deliberate("Continue test")
        self.assertTrue(result.consensus.approved)

    def test_unknown_or_tampered_evidence_blocks_consensus(self):
        unknown = self.review("left", evidence_id="ev-invented")
        tampered = self.review("right", excerpt_hash="0" * 64)
        result = self.engine(unknown, tampered).deliberate("Continue test")
        self.assertFalse(result.consensus.approved)
        reasons = " ".join(result.consensus.reasons)
        self.assertIn("unknown evidence ID", reasons)
        self.assertIn("excerpt hash mismatch", reasons)

    def test_link_to_undeclared_claim_blocks_consensus(self):
        review = self.review("left")
        altered = ModelReview(
            **{
                **review.__dict__,
                "claims": ("a different claim",),
            }
        )
        result = self.engine(altered, self.review("right")).deliberate("Continue test")
        self.assertFalse(result.consensus.approved)
        self.assertIn("undeclared claim", " ".join(result.consensus.reasons))


if __name__ == "__main__":
    unittest.main()
