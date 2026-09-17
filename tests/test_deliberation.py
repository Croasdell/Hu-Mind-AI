import unittest

from humind.action_gate import ActionGate
from humind.consensus import evaluate_consensus
from humind.deliberation import DeliberationEngine
from humind.providers.base import review_from_json
from humind.providers.mock import MockReviewer
from humind.schemas import ModelReview, ProposedAction, Verdict
from humind.shadow import ShadowProbeGenerator
from humind.terminal import run_dual_demo


def approved_review(provider: str, action: ProposedAction) -> ModelReview:
    return ModelReview(
        provider=provider,
        verdict=Verdict.APPROVE,
        summary="Bounded experiment is supported.",
        action=action,
        evidence=("benchmark specification",),
        risks=("time cost",),
        confidence=0.85,
    )


class ConsensusTests(unittest.TestCase):
    def setUp(self):
        self.action = ProposedAction(
            "run_experiment",
            "dual-review-benchmark",
            (("dataset", "fixtures/v1"),),
        )

    def test_matching_independent_approvals_reach_consensus(self):
        decision = evaluate_consensus(
            (approved_review("kimi", self.action), approved_review("openai", self.action))
        )
        self.assertTrue(decision.approved)
        self.assertEqual(decision.action.fingerprint, self.action.fingerprint)

    def test_different_actions_are_escalated(self):
        other = ProposedAction("run_experiment", "different-benchmark")
        decision = evaluate_consensus(
            (approved_review("kimi", self.action), approved_review("openai", other))
        )
        self.assertFalse(decision.approved)
        self.assertIn("reviewers proposed different actions", decision.reasons)

    def test_veto_blocks_consensus(self):
        blocked = ModelReview(
            provider="kimi",
            verdict=Verdict.APPROVE,
            summary="Approval contains a veto and must not pass.",
            action=self.action,
            evidence=("benchmark",),
            critical_vetoes=("private data has no consent record",),
            confidence=0.9,
        )
        decision = evaluate_consensus((blocked, approved_review("openai", self.action)))
        self.assertFalse(decision.approved)

    def test_human_and_allowlist_gate_are_both_required(self):
        decision = evaluate_consensus(
            (approved_review("kimi", self.action), approved_review("openai", self.action))
        )
        gate = ActionGate({"run_experiment"})
        self.assertFalse(gate.authorize(decision, human_approved=False).allowed)
        self.assertTrue(gate.authorize(decision, human_approved=True).allowed)


class ShadowAndEngineTests(unittest.TestCase):
    def test_shadow_probe_is_deterministic_and_bounded(self):
        generator = ShadowProbeGenerator()
        first = generator.generate("Evaluate a new reasoning system", round_number=1)
        second = generator.generate("Evaluate a new reasoning system", round_number=1)
        self.assertEqual(first, second)
        self.assertLessEqual(first.intensity, generator.profile.intensity_cap)

    def test_engine_keeps_reviewers_independent_and_adapts_profile(self):
        action = ProposedAction("run_experiment", "benchmark")
        left = MockReviewer(approved_review("kimi", action))
        right = MockReviewer(
            ModelReview(
                provider="openai",
                verdict=Verdict.REVISE,
                summary="More evidence is required.",
                action=action,
                confidence=0.6,
            )
        )
        engine = DeliberationEngine(left, right)
        before = engine.shadow.profile.contradiction
        result = engine.deliberate("Test the architecture")
        self.assertFalse(result.consensus.approved)
        self.assertGreater(engine.shadow.profile.contradiction, before)

    def test_provider_json_contract_is_validated(self):
        review = review_from_json(
            "openai",
            '{"verdict":"approve","summary":"ok","action":{"kind":"run_experiment",'
            '"target":"benchmark","parameters":{"dataset":"v1"}},"evidence":["spec"],'
            '"confidence":0.8}',
        )
        self.assertEqual(review.verdict, Verdict.APPROVE)
        self.assertEqual(review.action.parameters, (("dataset", "v1"),))

    def test_offline_demo_keeps_execution_blocked(self):
        output = run_dual_demo("Evaluate a safe experiment")
        self.assertIn("Consensus: approved", output)
        self.assertIn("Execution authorized: False", output)
        self.assertIn("human approval remains required", output)


if __name__ == "__main__":
    unittest.main()
