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
The controlled Gate-3 memory boundary is specified in [MEMORY.md](MEMORY.md).
The draft transfer, conflict, and poisoning experiment is in
[H4_PROTOCOL.md](H4_PROTOCOL.md).
Current partnership and funding approaches are recorded in
[OUTREACH.md](OUTREACH.md).

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

## Repository guide

```text
humind/          orchestration, providers, evidence, memory, and safety gates
tests/           deterministic regression and failure-path tests
ARCHITECTURE.md  system boundaries and threat model
PROGRAMME.md     staged research and funding programme
EXPERIMENTS.md   falsifiable hypotheses and result process
ROADMAP.md       implementation and evaluation gates
```

Supporting documents cover the capability dataset, offline deployment,
hardware evidence, controlled memory, cooperation model, and programme decision
history. They are research plans rather than claims of demonstrated AGI.

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
- event-sourced memory with provenance, conflicts, correction, retraction, and decay;
- opt-in deterministic retrieval that treats recalled content as untrusted data;
- a human approval and action-allowlist gate;
- Kimi and OpenAI API adapters that are inactive until configured;
- a manifest-verified local provider that rejects non-allowlisted endpoints;
- offline mocks, audit support, and regression tests.

The available development setup is now split across two machines: a lightweight
laptop for orchestration and an offline-capable SIMBA server reported to contain
an RTX 2080 Ti, 32 GB RAM, and an AMD Ryzen 5 CPU. The server specification and
exact CPU model must be re-verified when it is next powered on. SIMBAX may help
write bounded components, but its patches remain subject to tests, independent
review, and human approval.

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

## Next milestones

- Measure the SIMBA server and add exact token, throughput, VRAM, RAM, energy,
  and temperature telemetry.
- Harden SIMBAX project-context exclusions before it handles Hu-Mind source.
- Connect two distinct local models through verified manifests.
- Reproduce the deployment under an egress-deny firewall on a second machine.
- Freeze an independently authored capability dataset and blinded labels.
- Run the preregistered single-model and dual-review comparisons.
- Measure correctness, false consensus, risk recall, latency, energy, and memory.
- Execute the H4 transfer and poisoning protocol with real local models.
- Run a narrow supervised pilot before considering tool execution.

The next major evidence milestone is the first live, reproducible dual-review
experiment through the existing consensus and human-approval boundaries.

The development strategy is hybrid: use local SIMBAX inference for bounded,
high-volume implementation work and reserve stronger external models for
architecture, difficult failures, security review, and final verification.

## Project status

Hu-Mind AI is an independent research prototype. It is not AGI, is not suitable
for consequential autonomous decisions, and currently has no tool-execution
authority. Contributions should preserve those boundaries and distinguish
implemented controls from proposed experiments.

## License

No licence file is currently included. Until one is added, normal copyright
restrictions apply.
