import json
from pathlib import Path
import tempfile
import unittest

from humind.audit import AuditError, GENESIS_HASH, JsonlAuditLog
from humind.experiments import ExperimentLedger, ExperimentPlan, ExperimentResult


class AuditChainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "audit.jsonl"
        self.log = JsonlAuditLog(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_empty_and_appended_chain_verify(self):
        self.assertEqual(self.log.verify().head_hash, GENESIS_HASH)
        first = self.log.append("first", {"value": 1}, timestamp="2026-09-17T12:00:00+00:00")
        second = self.log.append("second", {"value": 2}, timestamp="2026-09-17T12:01:00+00:00")
        verification = self.log.verify()
        self.assertTrue(verification.valid)
        self.assertEqual(verification.record_count, 2)
        self.assertEqual(verification.head_hash, second)
        self.assertNotEqual(first, second)

    def test_changed_historical_payload_is_detected_and_blocks_append(self):
        self.log.append("first", {"result": "negative"}, timestamp="2026-09-17T12:00:00+00:00")
        self.log.append("second", {"result": "kept"}, timestamp="2026-09-17T12:01:00+00:00")
        lines = self.path.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[0])
        record["payload"]["result"] = "rewritten-positive"
        lines[0] = json.dumps(record, sort_keys=True, separators=(",", ":"))
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        verification = self.log.verify()
        self.assertFalse(verification.valid)
        self.assertIn("record hash mismatch", " ".join(verification.errors))
        with self.assertRaisesRegex(AuditError, "refusing to append"):
            self.log.append("third", {})

    def test_broken_json_is_reported(self):
        self.path.write_text('{"incomplete":', encoding="utf-8")
        self.assertFalse(self.log.verify().valid)

    def test_external_checkpoint_detects_tail_deletion(self):
        self.log.append("first", {"value": 1}, timestamp="2026-09-17T12:00:00+00:00")
        self.log.append("second", {"value": 2}, timestamp="2026-09-17T12:01:00+00:00")
        checkpoint = self.log.create_checkpoint(
            b"independent-checkpoint-key",
            created_at="2026-09-17T12:02:00+00:00",
        )
        lines = self.path.read_text(encoding="utf-8").splitlines()
        self.path.write_text(lines[0] + "\n", encoding="utf-8")
        self.assertTrue(self.log.verify().valid)
        anchored = self.log.verify_checkpoint(checkpoint, b"independent-checkpoint-key")
        self.assertFalse(anchored.valid)
        self.assertIn("record count mismatch", " ".join(anchored.errors))

    def test_checkpoint_signature_cannot_be_rewritten(self):
        checkpoint = self.log.create_checkpoint(b"checkpoint-key")
        checkpoint["record_count"] = 99
        verification = self.log.verify_checkpoint(checkpoint, b"checkpoint-key")
        self.assertFalse(verification.valid)
        self.assertIn("signature mismatch", verification.errors[0])


class ExperimentLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.log = JsonlAuditLog(Path(self.temp.name) / "experiments.jsonl")
        self.ledger = ExperimentLedger(self.log)
        self.plan = ExperimentPlan(
            title="Heterogeneous review ablation",
            hypothesis_ids=("H1", "H5"),
            baseline="best cost-matched single model",
            primary_metrics=("critical_error_rate", "false_consensus_rate"),
            success_criteria=("critical_error_rate improves by >= 10%",),
            failure_criteria=("no improvement after cost matching",),
            protocol_sha256="a" * 64,
            dataset_sha256="b" * 64,
            configuration_sha256="c" * 64,
            preregistered_at="2026-09-17T12:00:00+00:00",
        )

    def tearDown(self):
        self.temp.cleanup()

    def result(self, **overrides):
        values = {
            "run_id": "run-001",
            "plan_id": self.plan.plan_id,
            "outcome": "inconclusive",
            "metrics": (("critical_error_rate", 0.12),),
            "artifact_sha256s": ("d" * 64,),
            "model_manifest_sha256s": ("e" * 64, "f" * 64),
            "evidence_pack_sha256": None,
            "started_at": "2026-09-18T12:00:00+00:00",
            "completed_at": "2026-09-18T13:00:00+00:00",
            "reproduction_status": "not yet reproduced",
            "conclusion": "More runs are required.",
        }
        values.update(overrides)
        return ExperimentResult(**values)

    def test_plan_must_be_registered_before_result(self):
        with self.assertRaisesRegex(AuditError, "unregistered plan"):
            self.ledger.record_result(self.result())
        plan_id = self.ledger.register(self.plan)
        self.ledger.record_result(self.result())
        self.assertEqual(plan_id, self.plan.plan_id)
        self.assertTrue(self.log.verify().valid)
        self.assertEqual(self.log.verify().record_count, 2)

    def test_duplicate_plan_and_run_are_rejected(self):
        self.ledger.register(self.plan)
        with self.assertRaisesRegex(AuditError, "already registered"):
            self.ledger.register(self.plan)
        self.ledger.record_result(self.result())
        with self.assertRaisesRegex(AuditError, "already recorded"):
            self.ledger.record_result(self.result())

    def test_negative_result_requires_failure_record(self):
        with self.assertRaisesRegex(ValueError, "failure-record"):
            self.result(outcome="contradicts")
        result = self.result(outcome="contradicts", failure_record_id="FAIL-0001")
        self.assertEqual(result.failure_record_id, "FAIL-0001")

    def test_unknown_hypothesis_and_nonfinite_metric_are_rejected(self):
        values = {**self.plan.__dict__, "hypothesis_ids": ("H99",)}
        with self.assertRaisesRegex(ValueError, "H1-H6"):
            ExperimentPlan(**values)
        with self.assertRaisesRegex(ValueError, "finite"):
            self.result(metrics=(("bad", float("nan")),))


if __name__ == "__main__":
    unittest.main()
