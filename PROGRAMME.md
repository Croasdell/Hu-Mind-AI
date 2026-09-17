# Hu-Mind: Living Top-Down AGI Programme

Status: working programme, version 0.1  
Planning horizon: multi-year  
Long-term aim: produce and independently verify a working candidate for
artificial general intelligence through peaceful international cooperation.

This document is the top-down map. It is expected to change when experiments
contradict it. Lower-level designs, code, budgets, and partnerships must trace
back to this programme; the programme must in turn be revised when evidence
shows that an assumption is wrong.

## 1. Mission

Build an offline-first, auditable system that can learn and reason across
substantially different domains, recognize its uncertainty, seek evidence,
form and revise plans, and act only within explicit human authority.

The programme will study whether productive tension between heterogeneous
reasoners, bounded adversarial thought generation, verified evidence, memory,
and deterministic action governance can overcome weaknesses found in
monolithic AI systems.

The programme does not claim that Hu-Mind is AGI today. “AGI” is a research
target whose operational definition and tests must be published before any
success claim.

## 2. Non-negotiable principles

1. **Peaceful purpose.** No work whose primary purpose is weapons, coercive
   surveillance, mass manipulation, or autonomous use of force.
2. **Offline sovereignty.** The reference system must operate without external
   APIs or an internet connection after models and signed artefacts are
   provisioned.
3. **Evidence before scale.** Hardware expansion follows measured bottlenecks;
   it does not substitute for a sound architecture or evaluation.
4. **No model self-authorization.** Models may propose and review. A separate
   deterministic gate and a human authority control consequential action.
5. **Falsifiability.** Every architectural claim needs a baseline, metric,
   failure condition, and reproducible experiment.
6. **Plural oversight.** No state, company, model provider, or founder should
   be able to make an unreviewed claim of AGI or unilaterally activate a
   high-capability system.
7. **Reversible progress.** Early experiments remain sandboxed, checkpointed,
   rate-limited, and capable of rollback.
8. **Learn from failure.** Negative results, near misses, and abandoned
   hypotheses are first-class project outputs.

## 3. Operational definition of a candidate AGI

A candidate may enter independent AGI assessment only after it demonstrates
all of the following under preregistered, held-out evaluation:

- broad transfer across language, software, quantitative reasoning, research,
  planning, and unfamiliar simulated environments;
- adaptation to new task families from limited instructions or experience;
- durable memory with provenance, correction, and controlled forgetting;
- construction and revision of explicit world models;
- calibrated uncertainty and reliable requests for evidence or help;
- long-horizon planning with recovery from interruption and failed steps;
- robustness to distribution shift, deception, prompt injection, and
  adversarially selected tasks;
- bounded resource use and competitive learning/inference efficiency;
- respect for permissions, action boundaries, shutdown, and human veto;
- reproducibility by at least two independent evaluation teams.

No single benchmark score, fluent conversation, model size, self-description,
or agreement between models is sufficient evidence of AGI.

## 4. Top-level system hypothesis

```text
                         HUMAN PURPOSE AND AUTHORITY
                                   |
                                   v
                     Objective, constraints, evidence
                                   |
                                   v
                Bounded shadow / counter-hypothesis generator
                                   |
                        +----------+----------+
                        |                     |
                        v                     v
              Heterogeneous reasoner A   Heterogeneous reasoner B
                (local open weights)       (local open weights)
                        |                     |
                        +----------+----------+
                                   |
                      Claims, disagreement, evidence
                                   |
                                   v
                   Synthesis and deterministic consensus
                                   |
                        +----------+----------+
                        |                     |
                   unresolved             candidate plan
                        |                     |
               evidence / revision     policy + human gate
                                              |
                                              v
                                   sandboxed local executor
                                              |
                                              v
                                  observation and learning
                                              |
                                     versioned memory
```

This is a hypothesis, not a commitment to preserve every component. Each block
must earn its place by outperforming a simpler baseline.

## 5. Scientific hypotheses

| ID | Hypothesis | Baseline | Evidence that supports it | Evidence that kills or revises it |
|---|---|---|---|---|
| H1 | Heterogeneous review reduces critical errors | Best single model | Lower critical-error and false-approval rates | No significant gain after cost matching |
| H2 | Bounded shadow probes expose neglected failure modes | Dual review without probes | Higher risk recall without unacceptable false alarms | More noise, bias, or deadlock than useful discoveries |
| H3 | Deterministic consensus improves action precision | Model-selected action | Fewer unsafe/incorrect actions at matched task completion | Excessive refusal or no safety improvement |
| H4 | Structured, provenance-aware memory improves transfer | Stateless system | Better held-out transfer and correction retention | Contamination, false-memory persistence, or marginal benefit |
| H5 | Deliberative synthesis produces capabilities beyond voting | Majority/score voting | Better solution quality on disagreement cases | Equivalent or worse performance |
| H6 | Offline open-weight models can support the full architecture | Hosted frontier APIs used only as research comparators | Acceptable capability and efficiency inside the air gap | Required capability remains unavailable locally |

## 6. Programme workstreams

### A. Cognitive architecture

- independent proposal, criticism, synthesis, memory, and metacognition;
- explicit separation between confidence, evidence, and authority;
- multiple forms of reasoning rather than a permanent “left/right brain” claim;
- mechanisms for productive disagreement without forced consensus.

### B. Learning and memory

- episodic, semantic, procedural, and audit memory stores;
- source provenance, conflict representation, retraction, and decay;
- continual learning experiments with catastrophic-forgetting tests;
- no unrestricted self-modification.

### C. Evaluation and failure science

- preregistered benchmarks and ablations;
- red teams independent of the builders;
- hidden evaluation sets and contamination checks;
- a public failure register for hypotheses, incidents, and negative results.
- preregistered plans and tamper-evident results mapped to H1-H6;

### D. Offline systems and hardware

- reproducible signed model and software manifests;
- local inference endpoints on an isolated network;
- deterministic orchestration and sandboxed execution;
- measured GPU memory, throughput, energy, storage, and cooling needs;
- staged hardware acquisition tied to experiment gates.

### E. Safety and governance

- permission-scoped actions and human veto;
- capability and misuse evaluations before every scope expansion;
- incident response, rollback, external inspection, and whistleblowing channels;
- an international charter separating scientific access from operational
  authority.

### F. Institutions and funding

- a research consortium before a capital-intensive joint venture;
- shared facilities and contributed hardware;
- transparent background-IP and project-IP rules;
- public, philanthropic, academic, and commercial funding without exclusive
  control over safety decisions.

## 7. Stage gates

### Gate 0 — reproducible foundation

Deliverables:

- offline build manifest and threat model;
- deterministic orchestration and consensus tests;
- signed data/model inventory;
- benchmark specification and failure register.

Pass condition: a second machine reproduces the offline test results from
documented artefacts.

### Gate 1 — two local reasoners

Deliverables:

- two genuinely distinct locally hosted models;
- no runtime external-network dependency;
- independent first-round reviews;
- cost, latency, energy, and error baselines.

Pass condition: the system completes the first 100-task evaluation and fails
closed during provider loss or malformed output.

### Gate 2 — architectural falsification

Deliverables:

- all H1-H6 ablations that current hardware permits;
- false-consensus and correlated-error analysis;
- published negative results and revised architecture.

Pass condition: at least one Hu-Mind configuration beats cost-matched single
models on preregistered primary metrics and survives independent replication.

### Gate 3 — learning system

Deliverables:

- provenance-aware long-term memory;
- controlled skill acquisition in simulation;
- forgetting, poisoning, and rollback evaluations.

Pass condition: measurable transfer to unseen task families without unacceptable
regression, data leakage, or loss of control.

### Gate 4 — bounded general agent

Deliverables:

- long-horizon planning in an offline simulated world;
- resource budgets, interruption, shutdown, and recovery;
- supervised action through a narrow allowlist.

Pass condition: external red teams verify action precision, shutdown behavior,
and recovery across agreed domains.

### Gate 5 — candidate AGI assessment

Deliverables:

- preregistered cross-domain assessment against the definition in section 3;
- replication by at least two independent institutions;
- multinational safety, security, legal, and societal review;
- a decision process for continued containment, wider research access, or
  rejection of the AGI claim.

Pass condition: no internal project vote can declare success. The evidence and
independent assessments must support it.

### Gate 6 — international facility

Deliverables:

- treaty-compatible peaceful-use charter;
- shared compute facility and inspection regime;
- agreed contributions, access, IP, publication, and incident rules;
- representation for participating states, research institutions, civil
  society, and affected communities.

Pass condition: governance exists before high-capability expansion, not after.

## 8. Hardware progression

| Stage | Representative capability | Purpose |
|---|---|---|
| Bench | Two 24–32 GB GPUs, 128–256 GB RAM | Independent 20–32B-class inference and orchestration |
| Lab | 192–384 GB aggregate VRAM, 256–512 GB ECC RAM | 70B/120B inference, quantisation, adaptation, larger evaluations |
| Shared facility | 640 GB+ aggregate accelerator memory with high-bandwidth interconnect | Kimi-class mixture-of-experts research and multi-model concurrency |
| International facility | Modular multi-vendor clusters | Replication, independent partitions, safety evaluation, controlled scaling |

These are planning envelopes, not purchase authorizations. Every procurement
requires a workload model, measured bottleneck, energy/cooling plan, support
plan, and comparison with rental or partner access.

## 9. Living-plan change process

Every material change is recorded in `DECISIONS.md` with:

- the assumption or design being changed;
- evidence for and against;
- affected hypotheses and stage gates;
- safety and governance consequences;
- decision owner and reviewers;
- date for reconsideration.

Architecture evidence follows `EXPERIMENTS.md`: plans freeze their protocol,
dataset, configuration, metrics, and decision criteria before execution;
results enter a hash-chained journal and cite negative outcomes in the failure
register. Partner-held checkpoints make deletion or rewriting detectable.

The top-down programme is reviewed after each gate, major negative result,
incident, material model change, or new partner. Historical versions remain in
Git so the project cannot silently rewrite why a decision was made.

## 10. Immediate next programme increment

Completed foundations include the loopback-by-default local provider, signed
model manifests, deterministic 100-task infrastructure harness, injected
provider-failure tests, bounded critique, strict evidence packs, and the
preregistered experiment journal. These are software-foundation results, not a
passed Gate 1 or evidence of AGI.

The next increment is:

1. select two genuinely different open-weight models after licence and hardware
   review, then create their production manifests;
2. freeze real E1 and E5 capability datasets and preregister their plans;
3. deploy both model servers on an egress-denied host or isolated LAN;
4. collect correctness, false-consensus, latency, memory, energy, and failure
   data rather than buying larger hardware on estimates alone;
5. reproduce the run on a second machine under an independent operator;
6. use `CONSORTIUM_CONCEPT_NOTE.md` to recruit the first three to five research
   partners and independent journal-checkpoint holders.

## Evidence base

- Expert-system builders documented brittleness and the knowledge-acquisition
  bottleneck: [Brittleness and Bottlenecks](https://doi.org/10.1016/B978-0-444-87137-4.50029-1).
- Cyc explicitly attempted to address those limits through large-scale common
  sense representation: [Cyc project paper](https://doi.org/10.1609/aimag.v6i4.510).
- Research continues to find that scale alone does not guarantee human-level
  common sense: [systematic LLM commonsense study](https://arxiv.org/abs/2111.00607).
- ITER members agreed to share construction/operation costs and project IP:
  [ITER IP framework](https://www.iter.org/node/20687/framework-sharing-iter-intellectual-property).
- The Antarctic Treaty establishes peaceful use, scientific cooperation,
  exchange of results, and inspection as international principles:
  [Antarctic Treaty overview](https://www.ats.aq/e/antarctictreaty.html?lang=en).
