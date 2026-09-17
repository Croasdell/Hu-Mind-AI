# Research and Delivery Roadmap

## Research question

Does heterogeneous dual review with an adaptive, bounded shadow probe reduce
unsupported conclusions and unsafe action approvals relative to single-model
and simple-voting baselines at an acceptable cost and latency?

## Phase 0: contracts and safety foundation (current)

- Provider-neutral structured reviews.
- Deterministic shadow probes with bounded adaptation.
- Exact-action consensus and critical vetoes.
- Human approval and action allowlisting.
- Offline mocks and regression tests.
- An append-only audit format.

Exit criterion: all safety invariants have tests and no component can execute an
action directly.

## Phase 1: local model experiment

- Add a strict offline provider that accepts only loopback or approved isolated
  network endpoints.
- Serve two distinct open-weight models locally. Begin with models that fit the
  available hardware; treat full Kimi-class deployment as a later scale study.
- Validate malformed responses, timeouts, refusals, provider loss, and model
  version mismatches.
- Add a second round in which reviewers see concise claims and objections from
  the other side, but never private chain-of-thought.
- Add evidence objects with local document identity, import time, excerpt hash,
  and claim linkage.
- Add signed model manifests and explicit budgets for tokens, rounds, latency,
  energy, memory, and storage.

Exit criterion: 100 recorded tasks can run reproducibly without any tool or
action execution or external network access.

## Phase 2: evaluation

Build a versioned benchmark containing:

- routine low-risk decisions;
- ambiguous objectives;
- false-premise and missing-information tasks;
- adversarial instructions and prompt injections;
- high-risk actions that must be vetoed;
- cases where both providers are likely to share the same misconception;
- cases requiring disagreement rather than forced consensus.

Compare:

1. local reasoner A alone;
2. local reasoner B alone;
3. independent reviews with majority/simple agreement;
4. independent reviews plus the bounded shadow and consensus gates.

Primary metrics:

- factual correctness;
- unsupported-claim rate;
- critical-risk recall;
- false-consensus rate;
- appropriate escalation rate;
- action precision;
- cost and latency per resolved task.

Exit criterion: the full system shows a repeatable improvement on preregistered
metrics rather than merely producing longer answers.

## Phase 3: narrow pilot

Select one reversible, auditable domain. Good initial candidates include
software change planning, research-claim review, or operational risk analysis.
Do not begin with medical, legal, financial, weapons, surveillance, employment,
or autonomous physical-control decisions.

Exit criterion: two pilot users complete a supervised evaluation and the system
demonstrates a measurable advantage over their existing review process.

## Phase 4: funding and compute

Use Phase 2 results to support applications to NVIDIA Inception, UK AI
compute-access schemes, research partners, and Innovate UK. Cloud systems may
support explicitly separated comparison studies, but do not replace the
offline reference environment. The funding request
must connect compute to a specific experiment:

- model and precision;
- GPU type and estimated GPU-hours;
- dataset size;
- number of experimental runs;
- expected benchmark result;
- fallback if scaling does not improve quality.

Hardware purchase should follow evidence that compute, rather than architecture
or evaluation quality, is the limiting factor.

## Phase 5: learning and generalization

- Add provenance-aware long-term memory and controlled skill acquisition.
- Evaluate transfer to unfamiliar task families and simulated environments.
- Test catastrophic forgetting, poisoning, rollback, interruption, and
  shutdown.
- Publish successful and failed architectural ablations.

Exit criterion: independent evaluators reproduce improved transfer without an
unacceptable loss of control, calibration, or previously demonstrated skills.

## Phase 6: candidate AGI and international facility

- Run the preregistered candidate-AGI assessment defined in `PROGRAMME.md`.
- Require replication by at least two independent institutions.
- Establish consortium, inspection, incident, IP, and peaceful-purpose rules
  before expanding high-capability access.
- Use `COOPERATION_CHARTER.md` as the initial discussion draft rather than
  treating a joint venture or treaty as already agreed.

Exit criterion: no internal declaration is sufficient; evidence, external
replication, and multinational governance must all support the next step.

## Definition of an action-ready release

An action-ready Hu-Mind release requires source-linked evidence, calibrated
confidence, independent security review, budget enforcement, permission-scoped
tools, durable audit records, human approval, rollback procedures, and an
incident-response plan. Until then, Hu-Mind remains an advisory research tool.
