# RURO Welfare F3-R2A Repair + Dispositive Joint-Batch Diagnosis v1

## Overview

- spec_hash: `492bcfa9c766bfcb`
- theta_hash: `1dd94e9cf1f35464`
- Total elapsed: 120.9s

## Task 1 — Metadata Repair

- Gate-3b verdict (frozen): **FAIL**
- Gate-3b high-ESS median |delta_common|: 0.7319804266785854
- F4 readiness: **YES**
- F4 basis: Dual-stem V_i^IS production gate-0 certified (singles+couples PASS). Joint-batch parity is NOT an F4 dependency: F4 uses V_i^IS as the primary integrator. Omega readiness is out of scope for this repair.
- Omega readiness: OUT_OF_SCOPE
- F3-R2 provisional verdict: NOT_LICENSED

## Task 2 — Durable Anchor Evidence (v3)

- Utility-only B2 anchor gate: **fail**
- Sim output cols captured: 272

| Anchor | UID | V_i^IS | ESS | V_dir_util | delta_common | B2 pass |
| --- | --- | --- | --- | --- | --- | --- |
| primary | 200001593700 | 11.496632 | 40.5 | 4.1188 | 1.2262 | no |
| top_ess_sm_2016 | 200003504101 | 10.321668 | 45.1 | 1.9648 | -1.3039 | no |
| top_ess_sf_2016 | 200003672000 | 11.394785 | 41.4 | 2.8398 | -0.9495 | no |

## Task 3 — Dispositive Joint-Batch Diagnosis

- N HHs in joint batch: 1676
- N nodes per HH: 100
- Base seed: 20260604
- EUROMOD: FR_2015 / FR_2016_a3

- **Gate B (byte-identity of em_input rows): FAIL**
- **Gate A (EUROMOD determinism): NOT RUN**
- **Gate C (output comparison): NOT RUN**

- **Verdict: CONSTRUCTION_MISMATCH**
- Batch-context dependence: **unresolved**
- Joint batching method: **unresolved**

## Conclusions

READY FOR F4: yes
FROZEN FULL-V S=100 GATE: fail
UTILITY-ONLY B2 ANCHOR GATE: fail
JOINT BATCHING METHOD: unresolved
BATCH-CONTEXT DEPENDENCE: unresolved
FULL SINGLES V_i^dir AT S=100 AUTHORIZED: no
