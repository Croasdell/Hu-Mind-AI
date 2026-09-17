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

## Phase 1: live model experiment

- Connect one Kimi model and one OpenAI model through environment configuration.
- Validate malformed responses, timeouts, refusals, and rate limits.
- Add a second round in which reviewers see concise claims and objections from
  the other side, but never private chain-of-thought.
- Add evidence objects with source URI, retrieval time, excerpt hash, and claim
  linkage.
- Add explicit budgets for requests, tokens, rounds, latency, and spending.

Exit criterion: 100 recorded tasks can run reproducibly without any tool or
action execution.

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

1. Kimi alone;
2. OpenAI alone;
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

Use Phase 2 results to support applications to NVIDIA Inception, cloud-credit
programmes, UK AI compute-access schemes, and Innovate UK. The funding request
must connect compute to a specific experiment:

- model and precision;
- GPU type and estimated GPU-hours;
- dataset size;
- number of experimental runs;
- expected benchmark result;
- fallback if scaling does not improve quality.

Hardware purchase should follow evidence that compute, rather than architecture
or evaluation quality, is the limiting factor.

## Definition of an action-ready release

An action-ready Hu-Mind release requires source-linked evidence, calibrated
confidence, independent security review, budget enforcement, permission-scoped
tools, durable audit records, human approval, rollback procedures, and an
incident-response plan. Until then, Hu-Mind remains an advisory research tool.

