import json
import unittest

from humind.benchmark import DeterministicBenchmarkReviewer, gate1_tasks, run_benchmark
from humind.deliberation import DeliberationEngine


class BenchmarkTests(unittest.TestCase):
    def test_gate1_suite_contains_exactly_100_versioned_tasks(self):
        tasks = gate1_tasks()
        self.assertEqual(len(tasks), 100)
        self.assertEqual(len({task.task_id for task in tasks}), 100)
        self.assertEqual(len({task.category for task in tasks}), 10)

    def test_smoke_report_is_machine_readable_and_clearly_limited(self):
        report = run_benchmark(
            DeliberationEngine(
                DeterministicBenchmarkReviewer("fixture-left"),
                DeterministicBenchmarkReviewer("fixture-right"),
            )
        )
        self.assertEqual(report.correct, 100)
        self.assertTrue(report.infrastructure_only)
        self.assertEqual(json.loads(report.to_json())["task_count"], 100)


if __name__ == "__main__":
    unittest.main()
