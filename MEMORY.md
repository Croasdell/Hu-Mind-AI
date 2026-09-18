# Controlled Memory and Learning Boundary

Status: Gate-3 foundation implemented; no claim of continual learning or improved
general intelligence.

Hu-Mind's first durable memory is an event-sourced research component for H4.
It is designed to test whether provenance-aware memory improves transfer and
correction retention without allowing silent self-modification or false-memory
amplification.

## Memory classes

- **Episodic:** a sourced observation about a particular run or event.
- **Semantic:** a sourced proposition intended to persist across tasks.
- **Procedural:** a sourced description of a procedure. It is data, never an
  executable permission or tool invocation.
- **Audit:** sourced governance and correction metadata.

Episodic and audit events may be logged automatically because they do not alter
the system's authority or learned operating rules. Semantic and procedural
writes require explicit human approval. Corrections and retractions always
require human approval. Each event records whether it came from human authority
or system observation, and reconstruction rejects semantic/procedural writes,
corrections, or retractions without the required authority marker. This marker
is auditable but is not yet a cryptographic human signature; consortium identity
and threshold-signature integration remain future work.

## Provenance and identity

Every memory contains:

- a type and stable subject;
- its content and confidence;
- one or more evidence IDs from an available local evidence pack;
- the exact evidence-pack fingerprint;
- timezone-qualified creation and optional expiry times;
- an optional explicit link to the memory it supersedes.

The memory identity hashes those fields. Unknown evidence packs and invented
evidence IDs are rejected. This establishes traceability, not truth: poisoned or
misleading source material can still produce a well-provenanced false memory.

## No silent overwrite

Memory events enter the same hash-chained journal used for experiment records.
Correction appends a new entry linked to the old identity; it does not edit or
delete the old bytes. Retraction appends a sourced retraction event. The active
view hides superseded, retracted, expired, and not-yet-created entries while the
historical journal retains them.

Two active entries with the same type and subject but different content are
returned together and the subject is marked conflicted. Retrieval never selects
one merely because it is newer or more confident.

## Decay and controlled forgetting

Recall calculates effective confidence from an explicit `as_of` time and
configured half-life. Decay changes ranking, not history. Expiry removes an
entry from the active view but not the journal. Restoring or replacing knowledge
requires another authorized event, preventing accidental resurrection through
an implicit database update.

## Separation from action

The memory ledger has no tools, executor, provider credentials, or action gate.
A procedural memory cannot grant permission, expand the action allowlist, or
satisfy human approval. Local reviewers can now receive an opt-in, deterministic
retrieval context when a retriever and explicit `as_of` time are configured.
Only active semantic and episodic entries are eligible. Retrieval is bounded by
item and character budgets, includes every active variant of a selected conflict
or none of them, and labels the JSON payload as untrusted data. The exact payload
is fingerprinted in provider telemetry. It remains subject to evidence,
consensus, policy, and human gates; its text is never interpreted as an
instruction by the orchestration layer.

## H4 falsification programme

The actual H4 experiment must compare a stateless configuration against this
memory layer on held-out task families. The draft protocol is
[H4_PROTOCOL.md](H4_PROTOCOL.md). It must preregister:

- transfer accuracy after controlled experiences;
- retention of a human-approved correction;
- catastrophic forgetting on previously passed tasks;
- recovery after retraction and rollback;
- poisoning success rate from adversarial but validly imported evidence;
- conflict detection and inappropriate conflict resolution;
- retrieval precision, latency, token cost, and storage growth;
- unauthorized semantic/procedural write attempts.

The memory hypothesis is contradicted if transfer gains are marginal, corrections
do not persist, poisoning or stale retrieval materially increases errors, or
operational cost exceeds the registered benefit. In that case the component is
revised or removed; a sophisticated memory mechanism does not earn a permanent
place merely because it resembles human cognition.

## Still missing before Gate 3

- encrypted storage and key lifecycle design;
- source-quality and cross-source independence scores;
- quotas, retention schedules, and denial-of-storage controls;
- a frozen H4 dataset and stateless baseline;
- poisoning, rollback, interruption, and catastrophic-forgetting runs;
- independent replication.
