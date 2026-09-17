# Hu-Mind AI

Hu-Mind AI is an original, local-first dual-process assistant: a creative
engine proposes possibilities, then a logic engine checks them for accuracy,
clarity, feasibility, and risk before they are accepted.

The long-term research aim is a working, independently evaluated candidate AGI.
The living top-down plan is [PROGRAMME.md](PROGRAMME.md). It connects the
technical architecture to stage gates, historical failure lessons, offline
hardware, funding, and a possible international cooperative research facility.
See also [FAILURE_LESSONS.md](FAILURE_LESSONS.md),
[COOPERATION_CHARTER.md](COOPERATION_CHARTER.md), and
[DECISIONS.md](DECISIONS.md). The air-gapped deployment boundary and its
remaining evidence checklist are in [OFFLINE_DEPLOYMENT.md](OFFLINE_DEPLOYMENT.md).
The preregistered falsification matrix and tamper-evident result process are in
[EXPERIMENTS.md](EXPERIMENTS.md).
The initial partner invitation is [CONSORTIUM_CONCEPT_NOTE.md](CONSORTIUM_CONCEPT_NOTE.md).
The strict E1/E5 dataset and scoring protocol is [CAPABILITY_DATASET.md](CAPABILITY_DATASET.md).
Hardware selection and funding evidence are governed by [HARDWARE_PLAN.md](HARDWARE_PLAN.md).

The name means **Human Mind AI**. The design is inspired by complementary
creative and analytical thinking—not by copying any proprietary service.

## Design

```text
User brief
   |
   v
Creative engine  ->  candidate ideas / hypotheses / alternatives
   |
   v
Logic engine     ->  evidence, contradictions, feasibility, risk, score
   |
   v
Human decision   ->  accepted ideas, revisions, or rejection
```

The creative side may be configured with an open-weight Mistral-family model.
The logic side should remain independently testable and should not blindly
trust generated text. “Unfiltered” is not a quality guarantee: Hu-Mind keeps
review, provenance, and human approval for consequential actions.

## Initial layout

```text
humind/
  __init__.py       package version
  __main__.py       python -m humind entry point
  pipeline.py       candidate and review data structures
  terminal.py       splash screen and interactive loop
tests/              deterministic regression tests
pyproject.toml      package metadata and humind command
```

## Current status

The terminal loop is working locally with a deterministic placeholder creative
engine. The repository now also contains the provider-independent foundation
for a Kimi/OpenAI dual-review experiment:

- a bounded adaptive shadow-probe generator;
- structured, independent model reviews;
- exact-action consensus with confidence, evidence, and veto checks;
- one bounded redacted peer-critique round when initial reviews disagree;
- content-addressed local evidence packs with strict claim-link verification;
- hash-chained experiment plans/results with independently anchorable heads;
- a strict 100-task capability-dataset validator and shared single/dual scoring;
- provider-attached token/latency telemetry plus external energy/memory fields;
- a human approval and action-allowlist gate;
- Kimi and OpenAI API adapters that are inactive until configured;
- a manifest-verified local provider that rejects non-allowlisted endpoints;
- offline mocks, audit support, and regression tests.

Hu-Mind does not currently edit files, execute shell commands, or publish
actions. Read [ARCHITECTURE.md](ARCHITECTURE.md) for the design and threat model,
and [ROADMAP.md](ROADMAP.md) for the research, evaluation, pilot, and funding
programme.

## Terminal prototype

Launch the yin-yang-inspired thought loop:

```bash
python3 -m humind "build a useful PHP product"
# or, after installing the package:
humind
```

The creative stage proposes several thoughts. The logic stage marks each
`ACT`, `KEEP`, or `REJECT`. The current generator is deliberately a small
deterministic stub; a Mistral adapter can replace it later without changing
the review contract.

### Decision meanings

- `ACT` — the proposal has a rationale and provenance and is ready for an
  explicitly approved next step.
- `KEEP` — the proposal is interesting but needs evidence, a clearer rationale,
  or revision before action.
- `REJECT` — the proposal is empty or fails a basic validity gate.

The terminal loop does not execute tools, change files, or publish anything.
That boundary stays in place when model adapters are added.

For a local editable install:

```bash
python3 -m pip install -e .
humind "design a small PHP product"
```

Use `--no-colour` when sending output to logs or automated tests.

### Interactive slash commands

When `humind` is started without a brief, the prompt supports:

```text
/help       show available commands
/review     repeat the latest thought review
/history    list briefs explored in this session
/exit       leave Hu-Mind
```

Each candidate now carries structured fields for rationale, assumptions,
evidence needed, risks, proposed action, confidence, and provenance. Reviews
also expose separate usefulness, clarity, provenance, and confidence scores so
future model adapters can be evaluated instead of trusted blindly.

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

No credentials are needed for the offline test suite. Live provider experiments
will read API credentials from the environment and must use explicit model
identifiers. Never commit API keys or experimental audit data.

Preview the dual-review architecture without making API calls:

```bash
python3 -m humind --dual-demo "evaluate a reasoning architecture"
```

The demonstration deliberately reaches model consensus but leaves execution
blocked because human approval has not been supplied.

Validate the fixed 100-task orchestration and report path:

```bash
python3 -m humind --benchmark-smoke
```

This is a known-answer infrastructure test, clearly marked
`"infrastructure_only": true`; its score must not be reported as model or AGI
performance. Gate 1 still requires two real local models, a frozen capability
dataset, physical/network isolation, failure tests, and independent
reproduction.

## Scope and originality

This repository will use public model weights and documented interfaces. It
does not reverse-engineer, reproduce, or redistribute Venice.ai proprietary
code, prompts, data, or hosted-service internals. Check each model's license
before commercial deployment.

## Roadmap

- Connect two distinct local models through verified manifests.
- Reproduce the deployment under an egress-deny firewall on a second machine.
- Add a bounded second critique-and-revision round.
- Add claim-linked evidence and citation verification.
- Build the 100-task evaluation set and single-model baselines.
- Measure correctness, false consensus, risk recall, cost, and latency.
- Run a narrow supervised pilot before considering tool execution.

The next build should run the first live dual-review experiment through the
existing deterministic consensus and human-approval boundaries.
