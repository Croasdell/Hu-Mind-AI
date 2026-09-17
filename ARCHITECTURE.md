# Hu-Mind Deliberation Architecture

Hu-Mind is an experimental dual-review reasoning system. It does not model
literal left and right brain hemispheres. Instead, it borrows a design metaphor
from C. G. Jung's tension of opposites: two independently produced positions are
held apart long enough for a better, third position to emerge.

The engineering claim is deliberately narrower than AGI. Hu-Mind asks whether
independent, heterogeneous reviewers plus constructive adversarial probes can
reduce unsupported conclusions and unsafe actions compared with a single model.

## Components

### 1. Objective

The user supplies an objective, constraints, and (eventually) an evidence pack.
The objective is data, not an instruction that can override Hu-Mind's policy.

### 2. Shadow probe generator

The shadow component produces one constructive counterthought per round. It
looks for hidden assumptions, contradictory evidence, affected parties, cheaper
alternatives, and plausible failure modes.

It is intentionally bounded:

- it adapts numeric challenge weights, not its own source code or instructions;
- its intensity has a fixed cap;
- its probes are questions, not facts;
- it has no tools and cannot authorize actions;
- identical objective and round inputs produce the same probe.

This is safer and more testable than generating vaguely "negative" thoughts.

### 3. Independent reviewers

Two heterogeneous, locally hosted open-weight models receive the same objective
and shadow probe. Kimi and OpenAI `gpt-oss` are research candidates, subject to
hardware feasibility and licensing review; they are not permanent architectural
requirements. In the first review round neither model sees the other's answer.
Each must return the same provider-neutral JSON contract:

- verdict;
- proposed canonical action;
- claims and assumptions;
- evidence;
- risks and critical vetoes;
- confidence.

Provider diversity may reduce correlated mistakes, but it does not guarantee
independence or truth. That is an empirical question the evaluation programme
must measure.

If the independent reviews do not agree, local providers may perform exactly
one peer-critique round. Each receives the other's structured verdict, canonical
action and fingerprint, claims, evidence, risks, vetoes, and confidence. It
does not receive the other's free-form summary, assumptions, hidden reasoning,
or model state. Reviewers are instructed to maintain disagreement when the
evidence warrants it; convergence is not itself rewarded.

### 4. Consensus gate

The deterministic gate, rather than either model, decides whether consensus
exists. Approval currently requires:

1. both reviewers explicitly approve;
2. both propose the exact same canonical action fingerprint;
3. both meet the confidence threshold;
4. both provide evidence;
5. neither raises a critical veto.

Failure produces a request for evidence or escalation. It never silently picks
one model as the winner.

Reviewer identities are checked against the configured providers in every
round. A first-round critical veto is sticky: a later model revision cannot
erase it or authorize action. Resolution requires human evidence review.

### 5. Human and action gate

Model consensus is necessary but insufficient. A consequential action also
requires explicit human approval and an allowlisted action kind. Hu-Mind emits
an authorization object; it does not presently execute anything.

### 6. Audit trail

Experiments can record structured events as JSON Lines. API keys, hidden model
reasoning, and sensitive raw prompts must not be written to the audit log.

## Deliberation sequence

```text
objective
   |
   v
bounded shadow probe
   |
   +-------------------+
   v                   v
Kimi review        OpenAI review
   |                   |
   +---------+---------+
             v
    deterministic consensus
             |
        no --+-- yes
        |         |
  one redacted    human approval
  critique round  + allowlist
        |              |
        v              v
 consensus again  authorization object
        |
 unresolved -> evidence/human escalation
```

## Threat model

Hu-Mind must assume that:

- both models can hallucinate the same answer;
- a prompt or retrieved document can attempt prompt injection;
- one provider can fail, time out, or return malformed JSON;
- apparent evidence can be irrelevant, circular, or fabricated;
- consensus can be produced through shared training-data bias;
- an approved plan can still be harmful outside its stated context.

Consequently, future evidence adapters need source verification, retrieved data
must be treated as untrusted, provider failures must fail closed, and high-risk
actions must remain outside the executable allowlist.

## Offline deployment boundary

The reference system is air-gapped. Models are downloaded, licensed, hashed,
scanned, and transferred through a controlled provisioning process, then served
through separate loopback or isolated-LAN endpoints. The orchestrator must be
able to reject any non-local endpoint when strict offline mode is enabled.

The implemented `OfflineNetworkPolicy` defaults to loopback only and rejects
public endpoints before a local provider can be constructed. Explicit isolated
hosts or IP networks can be allowlisted. This application check is defence in
depth: deployment firewall rules and physical isolation remain authoritative.

The repository currently contains Kimi and OpenAI cloud adapters for comparative
development work. They are not the production boundary and must not be enabled
inside the reference environment. The next provider layer will target local
OpenAI-compatible inference servers such as vLLM, Ollama, or llama.cpp without
hard-coding a particular runtime.

Every local model requires a manifest containing:

- model identity and exact revision;
- source and licence;
- file hashes and signature status;
- quantisation and inference runtime;
- expected memory and hardware requirements;
- evaluation status and approved roles.

The local adapter now verifies the manifest signature, artifact hashes, role,
and endpoint boundary before making inference requests. The prototype signing
scheme is HMAC-SHA256; multi-institution operation requires a later migration
to public-key or threshold signing with protected keys.

Each local request also carries an enforced inference budget. Input size and
requested output tokens are bounded before dispatch; elapsed time, reported
total tokens, structured response shape, and runtime model identity are checked
before a review can enter consensus. Missing accounting or any mismatch raises
a provider error, so no action can be approved from that round.

No runtime secrets or external provider credentials belong in the air-gapped
environment.

## What Hu-Mind is not

- It is not currently AGI or proof of general reasoning.
- It is not a psychological model or a simulation of a human brain.
- Consensus is not proof of correctness.
- The shadow probe is not an autonomous personality.
- The current action gate is authorization logic, not a general-purpose agent.
- The current cloud adapters are development comparators, not the offline
  reference deployment.
