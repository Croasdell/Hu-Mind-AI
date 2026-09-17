# Evidence-Gated Offline Hardware Plan

Status: procurement framework, not a purchase authorization or vendor quote.  
Last specification review: 2026-09-17.

## Current host observation

The present development machine exposes Intel HD Graphics 620 integrated
graphics, approximately 7.6 GiB system RAM, and no `nvidia-smi` device. It can
run orchestration, fixtures, dataset validation, and audit tests, but it is not
a credible host for the two-model Gate-1 experiment.

This observation is local machine state, not a permanent project assumption.
It must be remeasured on every proposed evaluation node.

## Procurement rule

Do not choose cards from parameter counts or marketing throughput alone. Freeze
the two model revisions and runtime first, then measure or demonstrate:

- resident weights plus KV cache and runtime overhead at the selected precision;
- each model running separately and both running at the required concurrency;
- prompt, completion, and total tokens;
- provider latency and end-to-end task latency;
- peak accelerator and host memory;
- wall energy for the complete frozen evaluation;
- thermal throttling, sustained power, acoustic/cooling limits, and recovery;
- driver/runtime compatibility, ECC requirement, warranty, and support;
- reproducibility on a second node.

The system now captures provider token counts and latency and can attach measured
energy and peak-memory readings to the same capability report. A report with
partial telemetry is marked by its telemetry-coverage rate and cannot support a
cost-matched claim.

## Current NVIDIA capacity ladder

| Candidate class | Official memory | Official board power / TDP | Appropriate decision question |
|---|---:|---:|---|
| GeForce RTX 5090 | 32 GB GDDR7 | 575 W; NVIDIA lists 1000 W required system power for its reference configuration | Can each selected small/quantized model fit wholly on one consumer card, and are lack of ECC and workstation support acceptable for the bench? |
| L40S | 48 GB GDDR6 | Verify in the selected certified server | Does a supported inference server and 48 GB per model materially reduce deployment risk? |
| RTX PRO 6000 Blackwell | 96 GB GDDR7 ECC | 600 W workstation edition; 300 W Max-Q | Does 96 GB per card allow each reasoner to remain isolated without model sharding, and is professional support worth the cost? |
| H200 | 141 GB HBM3e | Up to 700 W SXM or 600 W NVL | Have measured workloads justified a data-centre node, high-bandwidth interconnect, and its power/cooling/support burden? |

Official sources: [RTX 5090 specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/),
[RTX PRO 6000 family specifications](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/),
[L40S description](https://docs.nvidia.com/vgpu/sizing/virtual-workstation/latest/gpus-vws.html),
and [H200 specifications](https://www.nvidia.com/en-gb/data-center/h200/).

Memory capacities are not additive in every runtime. Two 32 GB cards do not
automatically behave like one 64 GB card, and Hu-Mind's preferred Gate-1 layout
places one distinct reasoner on each card. Any sharded-model proposal must prove
runtime support, interconnect behavior, latency, and failure isolation.

## Staged acquisition decision

### Stage A — borrowed or rented measurement

Use partner, university, vendor, or short-term hosted hardware only as a
provisioning and sizing environment. Keep this study separate from the final
air-gapped result. Run the exact model revision, quantization, context, batch,
and server intended for the offline node.

Exit evidence:

- both signed model manifests;
- peak memory and sustained throughput for each model;
- simultaneous dual-review and revision-round measurements;
- estimated evaluation energy and runtime;
- evidence that the smallest candidate class has adequate safety margin.

### Stage B — offline Gate-1 bench

Acquire or receive in-kind the smallest supported node that passes Stage A with
at least a documented memory margin and acceptable thermals. It must include
enough host RAM and storage for both model artifacts, immutable copies,
evaluation data, logs, and rollback—not merely the GPUs.

Exit evidence:

- egress-deny and removable-media controls independently checked;
- E1/E5 run completed with full telemetry coverage;
- provider failure and shutdown drills repeated on the real runtimes;
- authenticated experiment checkpoint held outside the node.

### Stage C — replicated partner node

A second institution reconstructs the node from signed manifests and repeats
the registered run. Differences in hardware are useful if configuration and
precision changes are separately registered.

### Stage D — shared facility

Consider professional or data-centre accelerators only when the journal shows
that model fit, throughput, reliability, or scale—not dataset quality or a weak
architecture—is the binding constraint. The facility proposal must include
power, cooling, fire safety, spares, secure operations, lifecycle replacement,
and independent partitions for replication.

## Funding package generated by the evidence

An NVIDIA, public-compute, university, philanthropic, or government request
should contain:

1. the signed model manifests and licences;
2. registered E1/E5 plan IDs and dataset hash;
3. measured memory, tokens/second, energy, and completion-time tables;
4. the exact number and class of accelerators requested, with alternatives;
5. the scientific result enabled by the hardware;
6. offline security, peaceful-use, publication, and incident commitments;
7. partner contributions and independent replication plan;
8. the fallback if more compute does not improve the preregistered metrics.

This turns “we need a lot of hardware for AGI” into an auditable request for a
specific falsifiable experiment. Quotes, availability, export controls, and
electricity costs are time- and location-dependent and must be refreshed when
procurement authority exists.
