# FR-P2a Region-Live Phase-5 Result Acceptance v1

**Mission:** JMP-M05C — Minimal Streaming Inference Implementation
**Decision-maker:** ChatGPT JMP Deputy Programme Director (`JMP_M05C_deputy_phase5_acceptance_v1.md`, 2026-08-03)
**Goal-1 audit:** `JMP_M05C_goal_manager_dryrun_acceptance_v1.md` — READY FOR DEPUTY REAL-RUN DECISION
**Date:** 2026-08-03

## 1. Acceptance verdict

`PHASE-5 FULL-SAMPLE INFERENCE ACCEPTED`

The single authorized full-population aggregate-only dry run is accepted as
the canonical Phase-5 inference result for the region-live P2a singles-2016
programme. A second numerical "production real run" is not authorized: it
would repeat the identical full-sample computation without adding scientific
information. The accepted attempt is canonical by acceptance and evidence
promotion, not by recomputation. No `complete/` directory has been created or
copied for Phase 5, and none will be — the existing immutable attempt
directory under `attempts/` is the canonical artifact set.

## 2. Canonical execution anchor

MNL HEAD at accepted execution:

```
bd7e3af2a0056b43f3fb8b50b858f358ed7a8825
```

Revision chain: `ffd060f7` (M05B closeout / test-42 salvage) → `b5169293`
(streaming addendum) → `92e299de` (Increment A) → `c2cf6a36` (Increment B +
proportionality records) → `bd7e3af2` (Increment C certified, dry run
authorized).

Nested `dclaborsupply-monorepo` revision and gitlink:

```
27756a06ea189339aa82915ed2124628afed20eb
```

## 3. Canonical attempt path

```
outputs/p2a_singles2016/region_live_v1/phase5_inference_v1/attempts/20260803T133122Z_14772_817e8deb503d408fa73b8b53d598c0db_dryrun_PHASE_5_DRY_RUN_COMPLETE/
```

Status: `PHASE_5_DRY_RUN_COMPLETE`. `creates_complete: false`. Mode:
`dry-run-only`. `real_run_supported: false`.

## 4. Accepted bundle and member hashes

Bundle SHA-256 (manifest-excluded hash-of-hashes over the 18 non-manifest
members, `"\n".join(f"{name}:{sha256(name)}")` sorted by name, then SHA-256 of
that string, per `_bundle_sha256` in `scripts/p2a/run_p2a_phase5_inference.py`):

```
d08947ce015f2b2a922c6d5591ebe600c53016922b3a1158d90f125cd2195232
```

This bundle hash has been independently recomputed against the files on disk
and matches exactly.

19-member allowlist (all present on disk, all SHA-256 verified against
`phase5_manifest.json.artifact_hashes`, no leftovers, no non-allowlisted
member):

| Member | SHA-256 |
|---|---|
| meat_free37.csv | `548be0a6c122ef636931e53f7818296929fab2ee6060b2a2eba8781ccc49b02c` |
| meat_free37.npy | `4bac680485d6e651165666c80ee1929ae4a6efc4f41c7d4a35d9b981426b4d94` |
| meat_interior35.csv | `b2a1f2144745a55423695523c3d2e8f2837a0bb9d65756f6a222ed562af3cfed` |
| meat_interior35.npy | `3551b319ead355619577e58725e1071ae400c6964ef9510c2a029a81753e0e89` |
| phase5_console.log | `7111aa441f38ad2b9648fa920cda414c7b155f546ddacda27a45681ddc4e31b9` |
| phase5_correlation_model.csv | `d9d0d2eb4616693297021bb2b17aba1dbb49e752f057302dc02da2a0d0bd461a` |
| phase5_correlation_robust.csv | `b0c857c8a9432031996f8d2ee5fb51943e649cfc52417dcfd44e3bbcaa7af652` |
| phase5_covariance_model.csv | `2e72678a6b7392f53794add0d20ff089bf2f0c5c8819f8327877c97a81e2ed73` |
| phase5_covariance_model.npy | `04952ba16eb1032a315000f2fd5593de7faa37f8bd571a01c1c8181e0c185632` |
| phase5_covariance_robust.csv | `c43710b4f5452ba10e569f44bab4b2853c4b21c9c09bbbf3510f153cbe3b094c` |
| phase5_covariance_robust.npy | `0b4e2a509b718ad67d337784df7c38cb4e1edcec9514b78a1f73edf3aff6a80b` |
| phase5_diagnostics.json | `943d8532dc0c4825b435b65fefa677d8ecca6018c924e9663e9024a34c60c34f` |
| phase5_manifest.json | (self-referential — excluded from the bundle hash; content-addressed via git) |
| phase5_parameter_table.csv | `6727692a8614c8a8cf01c0d5d98a75bc737d026e6c297c73b6f4826172deebb2` |
| phase5_regional_covariance.csv | `3cba5b4389073d41022cc9e3a43afc6a3a826f2e139ec18a09d554e795db4111` |
| phase5_regional_tests.csv | `47dae8014ec2c536cb3cf79e27a61f50af4871f3c0303d3be1737fb9f735b584` |
| phase5_standard_errors.csv | `da92759879c7e451a5b1ff488a48e13ec7e6dd98b793ebf7caa9313b420f3fbb` |
| score_aggregate_summary.json | `b3533fa4d52ee504d89b8b0d3d7e6e7fc217815aa91cd2388b43d9130108cf08` |
| score_sum_free37.csv | `b76ff964ec40561a625f660657258c5effe97ce12bd47c6bda618f952f48cc19` |

Accepted upstream bundles bound into this result (verified against gate T-5):

- Phase-3 bundle: `2cf237648743f59bd742b12feceaea67c5fd377b26faf4fb6fad6f452f86864b`
- Phase-4 bundle: `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3`
- Accepted theta-byte hash: `c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d`
- Bread (Phase-4 Hessian) hash: `e9ca080ecc7e40e43881b9422af0095f23ad2bfef3e84648d2031a33eb9e4061`

## 5. Statistical gates

`gating_failures: []`. All gating-tier checks in `phase5_diagnostics.json`
passed (`passed: true`): T-5 (bread/theta/bundle provenance), T-6 (bread
integrity, PD, rank 37), T-7 (meat validity, PSD), T-8 (solve stability),
T-9 (covariance validity, V_model PD / V_robust PSD), T-10 (finite-sample
correction), T-14 (regional V_RR PD rank 10), T-17 (parameter-order
fingerprint), T-18 (valid correlations), T-19 (conditional-35 stationarity),
T-22 (numerical KKT activity, sample-level), T-1/T-4 (full-population score
identity), T-12S (fresh-process bitwise reproduction), T-23S (aggregate-only
member set, no leftovers).

Key figures:

- Full-population score identity: `max_abs_dev = 1.4566126083082054e-13`
  against the `1e-8` gate (`n_households = 1555`).
- T-12S fresh-process reproduction: parent digest = child digest =
  `7f71a532ff66a1e882f4a085ca78e14a9788e6c98cff8c04957b9df4c3ff4a80`; all
  exact keys matched; meat/score max-abs deviations exactly `0.0`; frozen
  tuple `ad_mode=jacfwd`, `batch_size=128`, `idhh_encoding=int64_le`.
- Finite-sample correction: `G/(G-K) = 1555/1520 = 1.0230263157894737`
  (`G=1555`, `N=1555`, `K=35`).
- 35-dimensional conditional robust covariance: `V_robust` PSD, all 35
  diagonals strictly positive and finite; regional `V_RR` PD, rank 10.

Warning-tier (non-gating, never determines the verdict): W-1 (SE ratio),
W-2 (eigenspectrum), W-3 (effective rank), W-4 (near-boundary containment,
see §8), W-5 (centring diagnostic) — all recorded; only W-4 flagged.

## 6. Reproduction

To reproduce the T-12S fresh-process check from a clean interpreter, re-run
the aggregate streaming reducer against the accepted sources bound in
`phase5_manifest.json.accepted_binding` (MNL HEAD `bd7e3af2...`, nested
`27756a06...`, Phase-3/Phase-4 bundle hashes, config SHA-256
`08be1cf6a7be0ff64a6417aef8e979003f5fa4f48f826b4d202ffd50c1f161d9`, spec
SHA-256 `492bcfa9c766bfcb5d8536f5e920cc0b00ffa600b7b89db60b250365f331f211`) and
confirm the child `score_stream_sha256` equals the parent digest
`7f71a532ff66a1e882f4a085ca78e14a9788e6c98cff8c04957b9df4c3ff4a80` without
creating a second score file. To reproduce the bundle hash, recompute
`_bundle_sha256` (`scripts/p2a/run_p2a_phase5_inference.py`) over the 18
non-manifest members of the accepted attempt directory and confirm it equals
`d08947ce015f2b2a922c6d5591ebe600c53016922b3a1158d90f125cd2195232`. No new
Phase-5 numerical run is authorized or required to close JMP-M05C.

## 7. Aggregate-only disclosure

The accepted workflow retains no household-level score matrix, no
household-level score hashes, and no temporary score batch
(`transient_batch_existed_in_memory_only: false`,
`transient_batch_serialized: false`). Gate T-23S confirms the member set is
allowlist-closed and aggregate-only: `no_row_level_score_member: true`,
`no_row_level_2d_array: true`, `no_restricted_store_member: true`,
`no_temporary_batch_remains: true`, `leftovers: []`. No row-level artifact
carries a household identifier; `idhh_encoding` fields describe byte
encoding convention only, not stored identifiers. The special
restricted-score retention and ACL question is closed as moot for Phase 5:
no restricted score store exists or is referenced, and all published
artifacts are non-disclosive aggregates. Ordinary disclosure review still
applies before any public replication release.

## 8. W-4 caveat

W-4 (near-boundary containment on the robust 95% interval) flagged two
coordinates:

- `beta_l0_sm`: robust 95% interval `[-0.123099..., 9.683896...]` against
  bounds `[0.05, 50.0]` — touches the lower bound.
- `beta_w_pexp2`: robust 95% interval `[-0.101443..., 0.075392...]` against
  bounds `[-0.1, 0.1]` — touches the lower bound.

Per the deputy ruling, S-10 Tier 1 applies now:

1. carry both names into the Phase-5 interpretation memo and inference
   appendix;
2. state that their symmetric robust 95% intervals are near the parameter
   boundary and should be interpreted cautiously;
3. do not treat this warning as evidence against the accepted model or as a
   reason to re-estimate Phase 3;
4. in M07/M08, record whether each coordinate materially loads on the
   welfare or decomposition functional and include one targeted local
   sensitivity.

S-10 Tier 2 is not triggered now. It becomes mandatory only if the paper
makes direct inference on a boundary coordinate, the welfare/decomposition
functional loads materially on one of the flagged coordinates, or an
unconditional active-set claim is proposed. This warning is non-gating
(`tier: warning`) and does not affect the acceptance verdict.

## 9. Active-bound interpretation

Gate T-22 (sample-level, not a population claim) confirms the numerical KKT
activity multiplier mapping carries exactly the two authenticated
active-bound names, each with multiplier ≥ 100× the interior max
|grad negLL| (`interior_max_abs_grad = 1.0992597206183063e-04`):

- `beta_l_age2_sm`: multiplier `0.8445544161794221` (ratio `7682.94`)
- `beta_l_age2_sf`: multiplier `1.4682021491125388` (ratio `13356.28`)

These two parameters are pinned/active at their bound in the accepted
47-parameter specification; the reported 35-dimensional interior covariance
and standard errors are conditional on this active set. This is a
sample-level KKT statement, not a claim about population-level bound
activity.

## 10. Regional/access interpretation

Gate T-14 confirms the regional test covariance `V_RR` is PD, rank 10, with
degrees of freedom `[10, 7, 2, 1]` for hypotheses H0-A/B/C/G; both model and
robust forms are computed and finite. The regional/access block reported
here (`phase5_regional_covariance.csv`, `phase5_regional_tests.csv`) is
distinct from the complete opportunity mechanism: it exercises the
conditional 35-dimensional interior parameter set under the active-bound
pinning described in §9, and should not be read as an unconditional
statement about the full opportunity/access structure. The weakest
eigendirection of `V_RR` has eigenvalue `0.018139225240310614` (W-2,
warning-tier, reporting only).

## 11. Evidence commit

This acceptance pointer is committed to MNL together with the exact
19-member accepted attempt as a single evidence commit
(`results(p2a): accept full-sample Phase-5 inference`). The commit does not
alter, recompute, or duplicate any numerical artifact; it promotes the
existing immutable `attempts/...PHASE_5_DRY_RUN_COMPLETE/` directory to
canonical status by documentation and version control alone. No `complete/`
directory is created.

## 12. Downstream use

The Phase-5 inference objects in the accepted attempt are reportable as
accepted empirical results for M07/M08 and subsequent manuscript work,
subject to: the W-4 caveat (§8); the distinction between the regional/access
block and the complete opportunity mechanism (§10); the conditional
35-dimensional active-set interpretation (§9); and ordinary manuscript
review. No second Phase-5 numerical run is required or authorized before
downstream use.
