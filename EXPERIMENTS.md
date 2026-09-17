# Experiment and Falsification Programme

Status: protocol map; individual plans are not preregistered until their
dataset, configuration, and protocol hashes are frozen.

The purpose of this programme is to make architecture changes traceable to
results. An attractive demonstration does not count as evidence unless it was
run against a registered baseline, metric, success condition, and failure
condition.

## Planned experiment families

| ID | Hypothesis | Comparison | Primary measures | Supporting result | Contradictory result |
|---|---|---|---|---|---|
| E1 | H1 | Best local model alone vs two heterogeneous local reviewers at matched token/energy budgets | Critical-error rate, unsupported-claim rate, false approvals | Material reduction survives repeated seeds and held-out tasks | No improvement, or benefit disappears after cost matching |
| E2 | H2 | Dual review with vs without bounded shadow probes | Critical-risk recall, false-alarm rate, resolution latency | More critical risks found without unacceptable false alarms | Added probes create noise, distress framing, deadlock, or no recall gain |
| E3 | H3 | Model-selected action vs deterministic exact-action consensus | Action precision, unsafe approvals, appropriate refusals | Fewer unsafe/incorrect approvals at matched task completion | No safety gain or refusal cost exceeds preregistered limit |
| E4 | H4 | Stateless system vs provenance-aware memory | Held-out transfer, correction retention, contamination, forgetting | Transfer and correction improve without unacceptable regression | False memories, poisoning, or maintenance cost outweigh benefit |
| E5 | H5 | Independent review, simple vote, and one redacted critique round | Solution quality, false consensus, calibration, compute/latency | Critique improves quality without increasing false consensus | Conformity rises, or performance is equivalent after cost matching |
| E6 | H6 | Offline open-weight system vs separately run hosted comparator | Capability, latency, energy, reproducibility, privacy boundary | Required task envelope is achieved inside the air gap | A required capability remains unavailable or uneconomic locally |

## Required preregistration fields

Before a run, `ExperimentPlan` fixes:

- one or more programme hypothesis IDs;
- the baseline;
- primary metrics;
- numerical or otherwise decidable success and failure criteria;
- hashes of the protocol, frozen dataset, and complete configuration;
- a timezone-qualified registration time.

Changing one of those fields creates a new plan identity. It does not amend the
old plan.

The E1/E5 dataset and automated scorer follow `CAPABILITY_DATASET.md`. The
repository contains the validator and comparison harness, not a secretly
finished benchmark: independent authors and adjudicators must create the real
held-out cases before their hash is registered.

## Required result fields

Every `ExperimentResult` identifies:

- its preregistered plan and unique run;
- measured finite metrics and outcome (`supports`, `contradicts`,
  `inconclusive`, or `aborted`);
- result artifacts, both model manifests, and any evidence-pack fingerprint;
- start and completion times;
- reproduction status and a bounded conclusion;
- a failure-register ID for contradictory or aborted runs.

Results cannot be added before their plan or silently replaced under an
existing run ID.

## Tamper-evident record

Plans and results enter a sequence-numbered JSONL journal. Every record hashes
its canonical content and the previous record, so changing history breaks the
chain and blocks further appends. Hash chains cannot detect deletion from the
end by themselves. The journal therefore supports authenticated head
checkpoints containing its record count and head hash.

During single-organisation prototyping, checkpoints use HMAC-SHA256. For the
international programme, replace that shared secret with threshold/public-key
signatures and publish checkpoints to independent partner archives. A valid
local journal without a matching external checkpoint is not complete evidence.

## Decision loop

```text
freeze protocol/data/config
            |
            v
register plan in audit chain
            |
            v
run without changing primary criteria
            |
            v
record all outcomes, including aborted and negative runs
            |
            +---- contradicts/aborted ----> create failure record
            |                                  |
            v                                  v
independent reproduction              revise architecture/plan
            |                                  |
            +------------------+---------------+
                               v
                 retain Git history and new test
```

No result automatically changes the programme. The relevant decision entry
must cite the plan ID, run IDs, journal checkpoint, reproduction status, and
reason the evidence warrants retaining, revising, or removing a component.
