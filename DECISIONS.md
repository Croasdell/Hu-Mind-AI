# Programme Decision Log

This log records material changes to the living top-down programme. Entries are
append-only; later decisions may supersede but do not erase earlier reasoning.

## D-0001 — Adopt an offline-first reference system

- **Status:** accepted
- **Decision:** External APIs may be used as explicitly labelled research
  comparators during development, but the reference Hu-Mind system must run
  entirely inside a closed environment using locally held weights.
- **Reason:** privacy, operational sovereignty, reproducibility, containment,
  and the intended hardware research programme.
- **Consequences:** provider endpoints must support localhost; model artefacts
  need hashes and licences; evaluation must include network-isolation tests.
- **Reconsider when:** a requirement cannot be evaluated locally or the offline
  assumption prevents an essential independent comparison.

## D-0002 — Treat Jung and brain-hemisphere language as metaphor

- **Status:** accepted
- **Decision:** “Shadow,” “opposites,” and “left/right” may name experimental
  roles, but will not be presented as a literal model of neuroscience or human
  psychology.
- **Reason:** the metaphor is useful for generating architectural hypotheses,
  but components must be retained only through empirical results.
- **Consequences:** documentation distinguishes inspiration from scientific
  evidence; evaluations include ablations that remove the metaphor-specific
  component.
- **Reconsider when:** never as a factual neuroscience claim; component names
  may change if they confuse partners or evaluators.

## D-0003 — Make international cooperation a programme workstream

- **Status:** accepted
- **Decision:** Develop a consortium and joint-facility path inspired by shared
  science projects and peaceful international research agreements.
- **Reason:** credible AGI research may require compute, evaluation diversity,
  legitimacy, and oversight beyond one organization.
- **Consequences:** create transparent contribution, IP, inspection, incident,
  and decision rules before pursuing a capital-intensive joint venture.
- **Reconsider when:** partner feedback or legal review identifies a more viable
  institutional structure.

## D-0004 — Enforce the offline provider boundary in code

- **Status:** accepted for the Gate-1 prototype
- **Decision:** Local model providers default to loopback-only endpoints and
  require a valid HMAC-SHA256 manifest plus matching artifact hashes and an
  approved role before use. Host firewall and physical isolation remain
  mandatory because an application allowlist cannot prove an air gap.
- **Evidence:** provider construction and tamper cases are covered by regression
  tests; a 100-task deterministic run verifies the measurement path.
- **Limit:** HMAC distributes a shared secret and is not the final consortium
  trust model. Migrate to public-key or threshold signatures before
  multi-institution provisioning.
- **Affected hypotheses/gates:** H6, Gate 0, Gate 1.
- **Reconsider when:** the first external research partner joins or a production
  provisioning appliance is selected.

## D-0005 — Treat missing runtime evidence as provider failure

- **Status:** accepted for Gate 1
- **Decision:** A local response is inadmissible unless it identifies the exact
  manifest-approved model, reports total token use, stays within input/output/
  total-token and elapsed-time budgets, and passes the structured review
  contract.
- **Reason:** an answer cannot safely enter consensus when its model identity or
  resource use is unknown, even if its prose appears plausible.
- **Evidence:** injected tests cover provider loss, malformed JSON, missing
  accounting, wrong model identity, and budget overruns.
- **Affected hypotheses/gates:** H1, H3, H6, Gate 1.
- **Reconsider when:** a chosen local runtime cannot provide trustworthy usage
  accounting; any relaxation then requires an independent server-side meter.

## D-0006 — Permit one redacted peer-critique round

- **Status:** accepted as a falsifiable experiment
- **Decision:** Preserve independent first reviews. If they disagree and both
  providers support revision, permit exactly one round containing structured
  positions but no free-form summaries, assumptions, private reasoning, or
  model state. Reapply deterministic consensus afterward.
- **Safety constraints:** provider identity is checked every round; unresolved
  disagreement blocks action; a first-round critical veto remains sticky and
  requires human evidence review.
- **Reason:** a bounded exchange may produce synthesis while limiting conformity,
  unbounded debate, and accidental chain-of-thought transfer.
- **Affected hypotheses/gates:** H1, H2, H3, H5, Gate 1, Gate 2.
- **Falsification condition:** remove or redesign the round if cost-matched
  evaluation shows greater false consensus, worse calibration, or no material
  benefit over independent review and simple voting.

## D-0007 — Make local evidence claim-linked and content-addressed

- **Status:** accepted for strict evidence experiments
- **Decision:** Import evidence inside the offline boundary, hash the exact
  document bytes and selected excerpt, fingerprint each pack, and require every
  model citation to link a declared claim to a known evidence ID and hash.
- **Reason:** free-form evidence strings allow fabricated provenance to satisfy
  a superficial consensus check.
- **Limit:** integrity is not truth. Hashes do not establish source quality,
  relevance, independence, consent, or completeness.
- **Affected hypotheses/gates:** H1, H3, H4, Gate 1, Gate 2, Gate 3.
- **Falsification condition:** revise the representation if claim-link checking
  does not reduce unsupported-claim and false-consensus rates under blinded
  evaluation, or if its operational cost outweighs the measured benefit.

## D-0008 — Preregister experiments in a tamper-evident journal

- **Status:** accepted for programme evidence
- **Decision:** Freeze protocol, dataset, configuration, metrics, and decision
  criteria before a run. Record plans and results in a hash-chained journal;
  require contradictory and aborted outcomes to cite a failure record; publish
  authenticated head checkpoints to independent partners.
- **Reason:** the living plan must respond to evidence without permitting
  hindsight criteria, suppressed negative results, or silent history changes.
- **Limit:** a local hash chain cannot detect deletion of its tail without an
  externally retained checkpoint. Prototype HMAC checkpoints are not the final
  multinational trust mechanism.
- **Affected hypotheses/gates:** H1-H6, Gates 0-6.
- **Reconsider when:** consortium key custody is designed; migrate to threshold
  signatures and multiple independently operated archives.

## D-0009 — Separate capability evaluation from infrastructure smoke tests

- **Status:** accepted for E1/E5
- **Decision:** Keep the deterministic 100-task smoke suite as plumbing evidence
  only. Require a separate 100-task, uniquely authored, independently
  adjudicated, held-out JSONL artifact for capability experiments, and score all
  baselines against its exact registered bytes.
- **Reason:** repeated known-answer templates can verify orchestration but would
  produce a meaningless capability score and invite benchmark overclaiming.
- **Controls:** minimum coverage across ten failure categories; consistent gold
  actions; hidden escalation/risk labels; identical dataset hash across single,
  simple-agreement, exact-consensus, and peer-revision configurations.
- **Limit:** lexical risk recall and fixed gold actions need blinded human review;
  training-data contamination cannot be excluded by schema validation.
- **Affected hypotheses/gates:** H1, H2, H3, H5, Gate 1, Gate 2.
