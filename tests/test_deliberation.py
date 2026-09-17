import unittest

from humind.action_gate import ActionGate
from humind.consensus import evaluate_consensus
from humind.deliberation import DeliberationEngine
from humind.providers.base import review_from_json
from humind.providers.mock import MockReviewer
from humind.schemas import ModelReview, PeerReviewSummary, ProposedAction, Verdict
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


class ScriptedRevisionReviewer:
    def __init__(self, name, first, revised):
        self.name = name
        self.first = first
        self.revised = revised
        self.revision_inputs = []

    def review(self, objective, probe):
        return self.first

    def revise(self, objective, probe, own_position, peer_position):
        self.revision_inputs.append((own_position, peer_position))
        return self.revised


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

    def test_same_provider_identity_cannot_form_consensus(self):
        decision = evaluate_consensus(
            (approved_review("same", self.action), approved_review("same", self.action))
        )
        self.assertFalse(decision.approved)
        self.assertIn("distinct provider identities", decision.reasons[0])


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

    def test_bounded_revision_can_reach_exact_consensus(self):
        action = ProposedAction("run_experiment", "benchmark")
        left = ScriptedRevisionReviewer(
            "left",
            ModelReview("left", Verdict.REVISE, "private left rationale", confidence=0.6),
            approved_review("left", action),
        )
        right = ScriptedRevisionReviewer(
            "right",
            ModelReview(
                "right",
                Verdict.REQUEST_EVIDENCE,
                "private right rationale",
                claims=("bounded test is reversible",),
                risks=("compute cost",),
                confidence=0.6,
            ),
            approved_review("right", action),
        )
        result = DeliberationEngine(left, right).deliberate("Test revision")
        self.assertTrue(result.consensus.approved)
        self.assertEqual(len(result.review_rounds), 2)
        peer = left.revision_inputs[0][1]
        self.assertIsInstance(peer, PeerReviewSummary)
        self.assertNotIn("summary", peer.as_payload())
        self.assertNotIn("assumptions", peer.as_payload())

    def test_first_round_consensus_skips_revision(self):
        action = ProposedAction("run_experiment", "benchmark")
        left = ScriptedRevisionReviewer("left", approved_review("left", action), approved_review("left", action))
        right = ScriptedRevisionReviewer("right", approved_review("right", action), approved_review("right", action))
        result = DeliberationEngine(left, right).deliberate("Already agreed")
        self.assertEqual(len(result.review_rounds), 1)
        self.assertFalse(left.revision_inputs)

    def test_first_round_veto_is_sticky_across_revision(self):
        action = ProposedAction("run_experiment", "benchmark")
        veto = ModelReview(
            "left",
            Verdict.REJECT,
            "private veto rationale",
            critical_vetoes=("unresolved safety boundary",),
            confidence=0.9,
        )
        left = ScriptedRevisionReviewer("left", veto, approved_review("left", action))
        right = ScriptedRevisionReviewer("right", approved_review("right", action), approved_review("right", action))
        result = DeliberationEngine(left, right).deliberate("Do not erase veto")
        self.assertFalse(result.consensus.approved)
        self.assertIn("first-round critical veto", result.consensus.reasons[0])

    def test_spoofed_review_identity_is_rejected(self):
        action = ProposedAction("run_experiment", "benchmark")
        left = MockReviewer(approved_review("left", action))
        right = MockReviewer(approved_review("right", action))
        right.name = "right"
        right._review = approved_review("left", action)
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            DeliberationEngine(left, right).deliberate("identity check")


if __name__ == "__main__":
    unittest.main()
