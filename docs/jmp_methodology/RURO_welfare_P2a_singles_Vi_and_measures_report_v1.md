# RURO Welfare P2a — V_i^IS + W-measure family (singles 2016)

Date: 2026-07-12 · spec_hash `492bcfa9c766bfcb` · theta_hash `7dbf035a5769146a` · stem `fr_p2a_singles2016_welfare` · S=101/HH · n=1555

Produced by `scripts/welfare/run_p2a_singles_welfare.py` on the NEW P2a baseline. No re-estimation; θ is a fixed input (results.joint.parameters).

## What was run

1. Staging (`stage_p2a_singles_welfare.py`): `stacked_hh_uid=idhh` (invert harmonise_bpool_engine_ready.py:130), `year_tag=2` (harmonise:20,131; single 2016 wave), canonical θ CSV from results JSON.
2. V_i^IS = engine logsum `lse` (estimation_engine.py:380); normalized `V_actual = V_i^IS − log(101)` (run_f4c…py:196-199).
3. W1/W3/W4/W6 verbatim from F4C Tasks 2-4; inequality from F5 primitives.

## Deviation from F4C literals (and why)

- **Actual target source.** F4C reads V_i^IS from the external F3-reconciled `singles_ViIS_dualstem_v1.parquet` (run_f4c…py:159-160). P2a has no such file — P3-1 PRODUCES V_i^IS — so `V_target = engine lse` directly. Consequence: the W3 zero-recovery identity is EXACT (not merely ≈ F4A).
- **Couples path.** `build_data_objects` always loads couples (jrt:271); P2a is singles-only, so the runner calls the singles primitives directly (jrt:189,274-279), no couples artifact written.
- **No S=101/N=5007 hard guard.** F4C asserts N=5007 (run_f4c…py:188); P2a has 1,555 HH, so the runner checks `n==expect_n_hh` (1,555) and `alts==S_i` (101) instead.

## Headline numbers

| measure | median ω (EUR) | p05 | p95 | weighted Gini (pooled) |
|---|---:|---:|---:|---:|
| W1 | 1345 | 846 | 2298 | 0.1757 |
| W4 | 8505 | 3742 | 17712 | 0.2610 |
| W6 | 9409 | 3983 | 19725 | 0.2664 |

W3 (own-set laissez-faire transfer) is the identity readout: median 1.29e-12 EUR, |max| 2.40e-10 EUR ≈ 0.

## Inequality battery (pooled, dwt-weighted, headline)

| measure | Gini | CV² | Theil-L | Atkinson(0.5) | Atkinson(1) | Atkinson(2) |
|---|---:|---:|---:|---:|---:|---:|
| W1 | 0.1757 | 0.1350 | 0.0534 | 0.0269 | 0.0520 | 0.1015 |
| W4 | 0.2610 | 0.2569 | 0.1148 | 0.0554 | 0.1085 | 0.2133 |
| W6 | 0.2664 | 0.2627 | 0.1195 | 0.0573 | 0.1127 | 0.2222 |

## Verification (deliverable 4)

- V_i finite for all 1555 HH: **True**
- reconstructed-logsum vs engine lse parity < 1e-9: **True**
- W finite counts: {'W1': 1555, 'W4': 1555, 'W6': 1555}
- pooled Gini(W) ∈ (0,1): {'W1': True, 'W4': True, 'W6': True}
- W3 zero-recovery identity holds: **True** — F4C: 'Subtracting log(S) from BOTH actual and own-set reference leaves the root unchanged => W3 numerically identical' (run_f4c…py:512-513); welfare_core.py:44-46 'Phi_i(0)=0 the W^3 reference-recovers-zero sanity check'. Here V_target==engine lse so R_shift(0)==lse exactly => W3 omega == 0.

**ALL_PASS: True**

## Outputs

- viis: `C:\Users\hisham\MNL\EUROMOD-STORAGE\outputs\welfare\p2a_singles2016\singles_ViIS_p2a_v1.parquet`
- measures: `C:\Users\hisham\MNL\EUROMOD-STORAGE\outputs\welfare\p2a_singles2016\singles_measures_p2a_v1.parquet`
- inequality: `C:\Users\hisham\MNL\EUROMOD-STORAGE\outputs\welfare\p2a_singles2016\inequality_p2a_v1.json`
- report: `C:\Users\hisham\Repo\MNL\docs\jmp_methodology\RURO_welfare_P2a_singles_Vi_and_measures_report_v1.md`

No existing script/config modified; no commit.