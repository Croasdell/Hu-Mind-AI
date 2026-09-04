import unittest

from humind.pipeline import Candidate, review_candidates


class PipelineTests(unittest.TestCase):
    def test_well_formed_candidate_is_accepted(self):
        result = review_candidates(
            [Candidate("Build a testable prototype", "It reduces risk", ("brief",))]
        )
        self.assertTrue(result[0].accepted)
        self.assertEqual(result[0].score, 1.0)

    def test_missing_provenance_is_rejected(self):
        result = review_candidates([Candidate("An idea", "A reason")])
        self.assertFalse(result[0].accepted)
        self.assertIn("no provenance supplied", result[0].issues)

    def test_invalid_threshold_is_rejected(self):
        with self.assertRaises(ValueError):
            review_candidates([], minimum_score=2)


if __name__ == "__main__":
    unittest.main()
