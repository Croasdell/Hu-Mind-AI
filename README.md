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
trust generated text. “Unfiltered” is not a quality guarantee: Hu-Mind keeps
review, provenance, and human approval for consequential actions.

## Initial layout

```text
humind/
  __init__.py       package version
  pipeline.py       candidate and review data structures
tests/              deterministic tests
```

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

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

## Scope and originality

This repository will use public model weights and documented interfaces. It
does not reverse-engineer, reproduce, or redistribute Venice.ai proprietary
code, prompts, data, or hosted-service internals. Check each model's license
before commercial deployment.

## Roadmap

- Add Mistral-compatible creative-model adapter.
- Add a local logic/reviewer adapter with structured outputs.
- Add evidence and citation tracking.
- Add evaluation sets for factuality, usefulness, and refusal/safety behavior.
- Add optional tool execution only behind explicit user approval and sandboxing.
