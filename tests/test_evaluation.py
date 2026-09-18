import json
from pathlib import Path
import tempfile
import unittest

from humind.deliberation import DeliberationEngine
from humind.evaluation import (
    CAPABILITY_CATEGORIES,
    EvaluationDataset,
    EvaluationError,
    ResourceMeasurements,
    evaluate_engine,
    evaluate_simple_agreement,
    evaluate_single,
)
from humind.schemas import InferenceTelemetry, ModelReview, ProposedAction, Verdict


class LabelReviewer:
    def __init__(self, name, tasks):
        self.name = name
        self.tasks = {task.objective: task for task in tasks}

    def review(self, objective, probe):
        task = self.tasks[objective]
        telemetry = InferenceTelemetry(self.name, 10, 2, 12, 0.1)
        if task.expected_approval:
            return ModelReview(
                self.name,
                Verdict.APPROVE,
                "Known-label scoring fixture.",
                action=task.expected_action,
                evidence=("fixture",),
                confidence=0.9,
                telemetry=telemetry,
            )
        return ModelReview(
            self.name,
            Verdict.REJECT,
            "Known-label scoring fixture.",
            evidence=("fixture",),
            risks=task.critical_risk_markers,
            confidence=0.9,
            telemetry=telemetry,
        )


class RevisingLabelReviewer(LabelReviewer):
    def review(self, objective, probe):
        return ModelReview(
            self.name,
            Verdict.REVISE,
            "First-round fixture disagreement.",
            telemetry=InferenceTelemetry(self.name, 10, 2, 12, 0.1),
        )

    def revise(self, objective, probe, own_position, peer_position):
        return super().review(objective, probe)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "capability.jsonl"
        categories = sorted(CAPABILITY_CATEGORIES)
        self.rows = []
        for index in range(100):
            category = categories[index % len(categories)]
            approved = category in {"routine", "reversible", "shutdown"}
            action = (
                {"kind": "run_experiment", "target": f"case-{index:03d}", "parameters": {"mode": "sandbox"}}
                if approved
                else None
            )
            self.rows.append(
                {
                    "task_id": f"E15-{index:03d}",
                    "category": category,
                    "objective": f"Unique evaluation objective {index:03d} in {category}.",
                    "expected_approval": approved,
                    "expected_action": action,
                    "require_escalation": category in {"disagreement", "high-risk"},
                    "critical_risk_markers": [] if approved else [f"risk-{category}"],
                }
            )
        self.write_rows(self.rows)

    def tearDown(self):
        self.temp.cleanup()

    def write_rows(self, rows):
        self.path.write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )

    def test_frozen_dataset_requires_100_unique_balanced_tasks(self):
        dataset = EvaluationDataset.load(self.path)
        self.assertEqual(len(dataset.tasks), 100)
        self.assertEqual(len(dataset.sha256), 64)
        self.assertEqual({task.category for task in dataset.tasks}, CAPABILITY_CATEGORIES)

    def test_exact_file_bytes_determine_dataset_identity(self):
        first = EvaluationDataset.load(self.path).sha256
        raw = self.path.read_text(encoding="utf-8")
        self.path.write_text(raw.replace("Unique evaluation", "Unique  evaluation", 1), encoding="utf-8")
        second = EvaluationDataset.load(self.path).sha256
        self.assertNotEqual(first, second)

    def test_duplicate_objective_and_bad_approval_label_are_rejected(self):
        rows = [dict(row) for row in self.rows]
        rows[1]["objective"] = rows[0]["objective"]
        self.write_rows(rows)
        with self.assertRaisesRegex(EvaluationError, "objectives must be unique"):
            EvaluationDataset.load(self.path)
        rows = [dict(row) for row in self.rows]
        rows[0]["expected_approval"] = True
        rows[0]["expected_action"] = None
        self.write_rows(rows)
        with self.assertRaisesRegex(EvaluationError, "approved tasks need"):
            EvaluationDataset.load(self.path)

    def test_category_coverage_is_enforced(self):
        rows = [dict(row) for row in self.rows]
        for row in rows:
            if row["category"] == "shared-bias":
                row["category"] = "false-premise"
        self.write_rows(rows)
        with self.assertRaisesRegex(EvaluationError, "deficient: shared-bias"):
            EvaluationDataset.load(self.path)

    def test_known_label_fixture_scores_all_preregistered_metrics(self):
        dataset = EvaluationDataset.load(self.path)
        engine = DeliberationEngine(
            LabelReviewer("fixture-left", dataset.tasks),
            LabelReviewer("fixture-right", dataset.tasks),
        )
        report = evaluate_engine(
            engine,
            dataset,
            configuration_id="fixture-dual-independent-v1",
            allow_revision=False,
            resources=ResourceMeasurements(
                measured_energy_wh=50.0,
                peak_accelerator_memory_gb=24.0,
                peak_host_memory_gb=12.0,
            ),
        )
        self.assertEqual(report.decision_accuracy, 1.0)
        self.assertEqual(report.unsafe_approval_rate, 0.0)
        self.assertEqual(report.false_block_rate, 0.0)
        self.assertEqual(report.action_precision, 1.0)
        self.assertEqual(report.appropriate_escalation_rate, 1.0)
        self.assertEqual(report.critical_risk_recall, 1.0)
        self.assertEqual(report.false_consensus_rate, 0.0)
        self.assertEqual(report.revision_rate, 0.0)
        self.assertEqual(report.prompt_tokens, 2_000)
        self.assertEqual(report.completion_tokens, 400)
        self.assertEqual(report.total_tokens, 2_400)
        self.assertAlmostEqual(report.provider_latency_seconds, 20.0)
        self.assertAlmostEqual(report.tokens_per_provider_second, 120.0)
        self.assertEqual(report.telemetry_coverage_rate, 1.0)
        self.assertEqual(len(report.input_context_trace_sha256), 64)
        self.assertEqual(report.measured_energy_wh, 50.0)
        self.assertEqual(report.peak_accelerator_memory_gb, 24.0)
        self.assertTrue(report.capability_evaluation)

    def test_same_dataset_scores_single_and_simple_agreement_baselines(self):
        dataset = EvaluationDataset.load(self.path)
        single = evaluate_single(
            LabelReviewer("fixture-single", dataset.tasks),
            dataset,
            configuration_id="fixture-single-v1",
        )
        agreement = evaluate_simple_agreement(
            LabelReviewer("fixture-left", dataset.tasks),
            LabelReviewer("fixture-right", dataset.tasks),
            dataset,
            configuration_id="fixture-simple-agreement-v1",
        )
        self.assertEqual(single.dataset_sha256, agreement.dataset_sha256)
        self.assertEqual(single.decision_accuracy, 1.0)
        self.assertEqual(agreement.decision_accuracy, 1.0)
        self.assertEqual(single.appropriate_escalation_rate, 0.0)
        self.assertEqual(agreement.appropriate_escalation_rate, 1.0)

    def test_invalid_external_resource_measurements_are_rejected(self):
        with self.assertRaisesRegex(EvaluationError, "finite and non-negative"):
            ResourceMeasurements(measured_energy_wh=-1.0)

    def test_revision_round_telemetry_is_included_in_resource_totals(self):
        dataset = EvaluationDataset.load(self.path)
        report = evaluate_engine(
            DeliberationEngine(
                RevisingLabelReviewer("fixture-left", dataset.tasks),
                RevisingLabelReviewer("fixture-right", dataset.tasks),
            ),
            dataset,
            configuration_id="fixture-revision-v1",
            allow_revision=True,
        )
        self.assertEqual(report.revision_rate, 1.0)
        self.assertEqual(report.total_tokens, 4_800)
        self.assertEqual(report.telemetry_coverage_rate, 1.0)


if __name__ == "__main__":
    unittest.main()
