# Offline Reference Deployment

Status: implementation guide for Gate 1; not yet a record of a completed
air-gapped deployment.

## Security boundary

An air gap is a property of the whole deployment, not a Python option. The
reference system requires all of the following:

1. a physically isolated host or isolated research LAN with no route to the
   public internet;
2. host firewall rules that deny egress by default;
3. model servers bound to loopback or an explicitly approved isolated subnet;
4. controlled removable-media import, malware scanning, hashing, and a
   two-person approval record;
5. verified model manifests before a provider is constructed;
6. no cloud credentials on the isolated machines;
7. exported audit results reviewed before they leave the boundary.

`OfflineNetworkPolicy` is defence in depth against configuration errors. It
does not create an air gap and is not a substitute for physical isolation or
firewall enforcement.

## Provisioning sequence

On a connected staging machine:

- obtain the model from its recorded source and pin an exact revision;
- review the licence and intended role;
- scan every transferred file;
- record a SHA-256 digest for every artifact;
- populate the manifest fields defined in `humind/manifest.py`;
- sign the canonical manifest through the controlled provisioning process;
- copy the bundle to approved media and record custody.

Inside the isolated boundary:

- rescan the media and compare custody records;
- verify the manifest signature and every artifact hash;
- copy artifacts into a read-only model store;
- start each model server under a separate low-privilege account;
- configure distinct reviewer names and approved roles;
- prove internet egress is unavailable before running Hu-Mind;
- retain the manifest digest with every experiment report.

The prototype currently uses HMAC-SHA256 manifest signatures so the entire
verification path works with the Python standard library. This authenticates a
bundle within one controlled organisation, but distributes a shared secret.
Before multi-institution provisioning, replace it with public-key or threshold
signatures and hardware-backed keys.

## Local provider boundary

`LocalReviewer` speaks the common OpenAI-compatible chat-completions protocol,
so a locally deployed vLLM, llama.cpp, or other compatible server can be used
without changing consensus logic. Its constructor fails unless:

- the endpoint is loopback or explicitly allowed by the offline network policy;
- the manifest signature is valid;
- every listed artifact hash matches;
- the requested reviewer role is approved by the manifest.

No model process receives action tools. It returns a structured review to the
deterministic consensus layer.

## Gate-1 evidence checklist

- [ ] Two distinct open-weight models and exact revisions selected.
- [ ] Licences reviewed and recorded.
- [ ] Signed production manifests created with all artifact hashes.
- [ ] Egress-deny firewall configuration independently checked.
- [ ] Two model servers run on loopback or the isolated LAN.
- [x] Provider loss, timeout, malformed output, token overrun, and runtime model
  mismatch fail closed in injected regression tests.
- [ ] The real-model 100-task dataset is preregistered and frozen.
- [ ] Single-model and dual-model reports include latency, memory, energy, and errors.
- [ ] A second machine reproduces the results.

The built-in `--benchmark-smoke` command checks only the 100-task orchestration
and reporting path. Its deterministic reviewers know the expected answers. Its
score is therefore not evidence about model capability, safety, or AGI.
