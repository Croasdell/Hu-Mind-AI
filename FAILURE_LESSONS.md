# Failure-Learning Register

The purpose of this register is not to dismiss earlier AI work as “failed.”
Many programmes produced foundational science. The purpose is to identify where
a stated route to broad intelligence did not meet its strongest expectations,
then turn that result into a Hu-Mind test.

## Historical lessons

| Approach | What it contributed | Limitation to test rather than repeat | Hu-Mind response | Required falsification test |
|---|---|---|---|---|
| Hand-built expert systems | Explicit rules, explanations, useful narrow-domain systems | Brittleness outside anticipated cases and expensive knowledge acquisition | Combine learned models with explicit evidence and deterministic gates | Distribution-shift suite; measure degradation and maintenance cost |
| Large hand-authored commonsense knowledge bases such as Cyc | Ontologies, contexts, default reasoning, durable symbolic knowledge | Enormous manual encoding burden; difficult coverage and inference control | Acquire knowledge through multiple routes, retain provenance, and measure marginal value | Cost per corrected/usable fact; held-out commonsense transfer; inference latency |
| Pure end-to-end statistical pattern learning | Powerful learning from data and broad representation | Spurious correlations, weak causal grounding, opaque provenance, unreliable out-of-distribution behavior | Evidence objects, counter-hypotheses, causal/simulation tasks, independent review | Counterfactual, causal, and distribution-shift evaluations |
| Scaling a single model | Strong general-purpose capability and simple engineering | Correlated errors remain invisible; fluency can mask unsupported claims | Heterogeneous reviewers and disagreement analysis | Cost-matched single-model versus dual-review ablation |
| Majority vote and self-consistency | Reduces some sampling errors | Repeated or correlated opinions are not independent evidence | Exact claim/action comparison plus source verification | False-consensus set where all samples share the same misconception |
| Static benchmark optimization | Comparable progress signals | Contamination, gaming, saturation, and weak real-world transfer | Hidden dynamic tasks, preregistration, and independent replication | Canary contamination tests and post-freeze task families |
| Unbounded autonomous agents | Demonstrates long-horizon tool use | Compounding errors, prompt injection, uncontrolled side effects, and unclear accountability | Offline sandbox, budgets, allowlists, human veto, rollback | Interruption, shutdown, injection, and action-precision tests |
| Anthropomorphic cognitive metaphors | Inspires modular designs and interpretable roles | Metaphor can be mistaken for neuroscience or evidence | Treat Jungian and hemispheric language as design metaphors only | Remove or replace the metaphor; retain components only if metrics improve |

## Project failure record template

Every abandoned or materially revised hypothesis gets an entry:

```text
ID:
Date:
Hypothesis:
Expected result:
Observed result:
Reproduction status:
Root-cause confidence:
What was learned:
Architecture or plan change:
New test preventing recurrence:
Open questions:
```

## Initial open failure risks

1. Both reviewers may share training data and produce correlated errors.
2. Shadow probes may increase verbosity or anxiety language without improving
   decisions.
3. Consensus may create deadlock or excessive deference to human operators.
4. Evidence fields may contain fabricated or circular references.
5. Offline models may be too weak for the proposed division of labour.
6. Memory may amplify errors faster than it accumulates useful knowledge.
7. Hardware availability may distort research toward models that fit rather
   than hypotheses that matter.
8. International governance may become symbolic while operational control
   remains concentrated.

Each risk must be converted into an owned experiment or governance control
before the relevant programme gate can pass.

