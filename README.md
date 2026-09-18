# Hu-Mind AI

Hu-Mind AI is an original, local-first dual-process assistant: a creative
engine proposes possibilities, then a logic engine checks them for accuracy,
clarity, feasibility, and risk before they are accepted.

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
trust generated text. "Unfiltered" is not a quality guarantee: Hu-Mind keeps
review, provenance, and human approval for consequential actions.

## Architecture

```text
humind/
  __init__.py         package version and exports
  __main__.py         python -m humind entry point
  pipeline.py         candidate and review data structures, baseline gate
  terminal.py         splash screen, interactive loop, dual-demo, benchmark
  consensus.py        deterministic consensus rules (models cannot waive)
  deliberation.py     independent review orchestration, revision round
  evidence.py         content-addressed evidence packs, claim-link verification
  audit.py            hash-chained JSONL audit journal, HMAC checkpoints
  memory.py           event-sourced ledger with decay, conflicts, retraction
  shadow.py           bounded adaptive counterthought generator
  offline.py          fail-closed endpoint policy for air-gapped deployment
  manifest.py         signed model manifests with artifact hashes
  action_gate.py      human + allowlist gate between consensus and execution
  schemas.py          shared provider-neutral contracts (Verdict, Action, etc.)
  benchmark.py        100-task deterministic infrastructure benchmark
  evaluation.py       structured evaluation against frozen datasets
  experiments.py      preregistered experiment plans with audit logging
  providers/          reviewer adapters (mock, local, OpenAI, Kimi)
    base.py           ReviewerProvider protocol, JSON contract validation
    mock.py           deterministic fixture reviewer for tests/demos
    local.py          verified local OpenAI-compatible server adapter
    http.py           bounded HTTP client with offline boundary enforcement
    openai.py         OpenAI Responses API adapter (dev comparator)
    kimi.py           Moonshot Kimi adapter (dev comparator)
tests/                75 deterministic regression tests
pyproject.toml        package metadata and humind command
```

## Current status

The terminal loop is working locally with a deterministic placeholder
creative engine. The full dual-review architecture is implemented offline:

- **Independent dual review** with deterministic consensus rules
- **Bounded adaptive shadow probes** that surface neglected constraints
- **Content-addressed evidence packs** with claim-link and excerpt-hash verification
- **Hash-chained JSONL audit journal** with HMAC-SHA256 checkpoints
- **Event-sourced memory ledger** with exponential decay, conflict visibility, and human-authority retractions
- **Fail-closed offline network policy** (loopback + explicit allowlist only)
- **Signed model manifests** with artifact hash verification
- **Human + allowlist action gate** (consensus necessary but insufficient)
- **Hardened HTTP provider** — call-time endpoint validation, redirect boundary checks, response size caps, timeout sanity checks

No external model is downloaded or called by default. Cloud adapters (OpenAI,
Kimi) exist as development comparators only. Hu-Mind does not currently edit
files, execute shell commands, or publish actions.

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

### Offline dual-review demonstration

Run the full dual-review architecture without network calls or credentials:

```bash
python3 -m humind --dual-demo "Evaluate a safe experiment"
```

This uses mock reviewers to exercise: shadow probe generation, independent
reviews, deterministic consensus, action fingerprinting, and the human/allowlist
gate. Execution remains blocked without human approval.

### Infrastructure benchmark

Run the 100-task deterministic benchmark suite:

```bash
python3 -m humind --benchmark-smoke
```

This produces a machine-readable JSON report with `correct`, `task_count`,
and `infrastructure_only` fields for CI/CD integration.

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

All 75 tests are deterministic and run without network access.

## Safety boundaries

The project enforces several safety boundaries by design:

1. **Offline deployment boundary** — The `OfflineNetworkPolicy` is fail-closed.
   Empty allowlists mean loopback only. Every HTTP call re-validates the
   endpoint and every redirect target against this policy.

2. **Evidence verification** — Reviews must link claims to content-addressed
   evidence items. Excerpt hashes are verified; tampered or unknown evidence
   blocks consensus.

3. **Consensus necessary but insufficient** — Even with dual independent
   approval, execution requires explicit human approval and an allowlisted
   action kind.

4. **Model-generated JSON cannot forge telemetry** — Provider responses are
   parsed into structured `InferenceTelemetry` with token accounting, model
   identity, latency, and evidence/memory context hashes. Mismatches fail
   closed.

5. **Retrieved content is untrusted** — Memory and evidence passed to models
   are marked `untrusted-data-no-action-authority`. The prompt instructions
   forbid following commands found inside.

6. **No tool execution** — The action allowlist currently contains only
   non-consequential kinds (e.g., `run_experiment`). High-risk actions remain
   outside the executable set.

7. **Audit integrity** — Hash-chained JSONL records commit to the complete
   preceding history. Tampering is detected on read and blocks further appends.
   HMAC-SHA256 checkpoints provide external anchoring.

## Scope and originality

This repository uses public model weights and documented interfaces. It
does not reverse-engineer, reproduce, or redistribute Venice.ai proprietary
code, prompts, data, or hosted-service internals. Check each model's license
before commercial deployment.

## Roadmap

- Add Mistral-compatible creative-model adapter.
- Add a local logic/reviewer adapter with structured outputs.
- Add evidence and citation tracking.
- Add evaluation sets for factuality, usefulness, and refusal/safety behavior.
- Add optional tool execution only behind explicit user approval and sandboxing.

The next build should connect the creative adapter first, then run it through
the existing independent review gate and evaluation tests.