# RURO Welfare F3-R2 Reconciliation + Joint-Batch Parity Report v1

## Overview

- spec_hash: `492bcfa9c766bfcb`
- theta_hash: `1dd94e9cf1f35464`
- Total elapsed: 247.2s

## Task 0 — Audit

- n_singles: 5007 (expect 5007)
- n_couples: 7438 (expect 7438)
- Anchor 200001593700 V_i^IS diff: 0.00e+00 (≤1e-9: True)
- Gate-0 all OK: True
- Gate-3b verdict (frozen): unknown

## Task 1 — Dual-Stem Parquets

- Singles rows: 5007  Couples rows: 7438
- Singles staged negll sum: 63900.9972
- Singles V_i^IS delta (staged−cert) median: 0.000736 nats
- Output: `outputs/welfare/fastlane/singles_ViIS_dualstem_v1.parquet`
- Output: `outputs/welfare/fastlane/couples_ViIS_dualstem_v1.parquet`

## Task 2 — Anchor Pricing

- `primary` (uid=200001593700): status=OK, n_nodes=100
- `top_ess_sm_2016` (uid=200003504101): status=OK, n_nodes=100
- `top_ess_sf_2016` (uid=200003672000): status=OK, n_nodes=100

## Task 3 — Joint-Batch Parity Gate

- Year: 2016 (year_tag=2)
- N HHs in joint batch: 1676
- N nodes per HH: 100
- Base seed: 20260604
- EUROMOD system: FR_2015 / FR_2016_a3
- Overall max abs diff: 3.10e+02  tol: 1e-06
- **Verdict: NOT_LICENSED**

### Anchor parity by column

| Anchor | UID | max_abs | pass |
| --- | --- | --- | --- |
| primary | 200001593700 | 1.27e+02 | False |
| top_ess_sm_2016 | 200003504101 | 1.59e+02 | False |
| top_ess_sf_2016 | 200003672000 | 3.10e+02 | False |

## Task 4 — Decisions

1. V_obs_staged + negll_contribution_staged produced: **True**
2. Anchor pricing: {'primary': 'OK', 'top_ess_sm_2016': 'OK', 'top_ess_sf_2016': 'OK'}
3. Joint-batch parity: **NOT_LICENSED** (max_abs=3.10e+02)
4. F4 authorized: **False** — F4 NOT authorized pending parity resolution.
5. Ω(W^3) ready: **False** — Omega(W^3) NOT authorized until joint-batch parity resolves.
