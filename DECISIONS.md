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
