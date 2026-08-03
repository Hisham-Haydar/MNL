# FR P2a — JMP-M05C Increment B independent review — v2

## 1. Review-B-v2 verdict

**FINAL VERDICT: REJECT**

The six named review-v1 examples now reproduce as claimed, all twelve updated
PROOFS pass, and the numerical core is unchanged. The bounded refix is still not
complete. T-22 lets a caller replace the supposedly authenticated expected-name
set; the serializers perform their empty-grade refusal only after writing the
target; and the JSON summary's unrestricted `extra` mapping can persist a
temporary 5-by-37 score block and overwrite the payload's grade. These are
remaining gate-authentication, R-37a, and no-row-persistence defects. With both
remediation budgets spent, any one requires rejection.

## 2. Scope and exact state

This was an independent read-only Review B v2. I ran tests and PowerShell/Python
proofs, created no repository output artifact, made no source edit or commit,
and did not run the full population. The only reviewer-owned file is this
review.

Starting and pre-review-file state:

- MNL HEAD: `92e299de6313bad0b0421c0db3dd268fdbcfdb59`.
- Nested gitlink and nested HEAD:
  `27756a06ea189339aa82915ed2124628afed20eb`; nested worktree clean.
- Phase-3 `attempts/`: 70 subdirectories before and after all tests.
- Untracked paths: exactly the five declared source, test, report, review-v1,
  and refix-report paths. After this file was written, this review is the sole
  addition.
- Increment-B implementation SHA-256:
  `506e9dc5574563a2ba233a87f25c025e6a54f4c372a5835517b3e89d691447e9`.
- Increment-B tests SHA-256:
  `f5a4bbf89b5a75fab8739b5955869a392db1342b4121c9bfd1ff0dae464c468b`.
- Report-v1 SHA-256:
  `3e9e69cf20321c889c2ec0284d3d3cc55e825c3a64615f8fc877ce46272c76b0`.
- Review-v1 SHA-256:
  `822b0fbc91ab6f906bca2dd49931bbbd27f9ee4bfa25f87db4cbd95a06b3a3af`.
- Refix-report SHA-256:
  `638c5f2788b8fac1285f12174ce4803b214b8c74c235be39ae052987d5f6dd27`.

The three committed Increment-A files
`scripts/p2a/p2a_phase5_score_stream.py`,
`tests/p2a/test_p2a_phase5_score_stream.py`, and
`tests/p2a/conftest.py` have an empty diff against HEAD.

## 3. Fix-by-fix findings

1. **T-5 theta-byte authentication — PASS for the required fix.**
   `accepted_theta_sha256` reads the Phase-3 JSON theta, converts it to a
   contiguous float64 vector, and hashes its bytes. The recomputed hash is
   `c024b89386c502003f9d4abb927b048dfab42c0bafe48d9a69d9fcb330f0580d`;
   the matching four-arm T-5 passes. Flipping exactly one byte and reloading
   through the real helper produced
   `faac56766f021952313be856f1171f486532fdbc74c0801de1d86ffdb3e11b85`;
   T-5 failed only `theta_bytes_match`, while bread, Phase-3 bundle, and Phase-4
   bundle arms remained true. The theta argument is required and keyword-only.

2. **T-22 exact active names — FAIL, partial fix.** Empty, missing, extra, and
   wrong-name mappings all fail with `active_names_ok=False`,
   `threshold_ok=False`, and `ratios={}`; the exact certified pair passes. But
   `gate_T22_numerical_kkt` exposes `active_names` as a caller-controlled
   argument. The direct call
   `gate_T22_numerical_kkt({'forged_active': 1.0}, 1e-4,
   active_names=('forged_active',))` returns `passed=True` and reports
   `required_names=['forged_active']`. Therefore the gate does not invariably
   authenticate against `ACTIVE_BOUND_NAMES`.

3. **Authoritative table gradients — PASS.** `build_parameter_table` requires
   `AcceptedGradients`, keys its free vector by the authenticated name sequence,
   and uses those values for free-coordinate gradients and active multipliers.
   `beta_w_educH` renders exactly `0.00010992597206183063`. Replacing every CSV
   gradient with `12345.6789` left the complete 47-by-13 frame identical and
   changed only the declared comparison diagnostic, reproducing `test_H9`.

4. **`inference_grade` propagation — FAIL, partial fix.** On successful paths,
   `subset-diagnostic` appears on `RegionalTests.inference_grade`, its
   diagnostics, its metadata, and regional-table attrs; it also appears on
   `ParameterTable`, its metadata, and frame attrs. All three successful
   serializer calls returned `ArtifactRecord` objects and `as_dict()` payloads
   carrying that grade, without changing the regional or parameter-table column
   schemas. However, `_record` validates a nonempty grade only after each writer
   has created its file. Direct empty-grade calls to `write_matrix`,
   `write_table`, and `write_score_aggregate_summary` each raised `IB-REFUSE`
   while leaving the target present. The summary's `extra` mapping can also
   overwrite its payload `inference_grade` independently of the record. R-37a's
   requirement that a covariance-derived artifact cannot be serialized
   unlabelled is therefore not met.

5. **Serializer refusal contracts — FAIL, partial fix.** The review-v1
   `np.zeros((5, 35))` probe and a numeric DataFrame containing `NaN` now both
   raise `SerializerRefusal` with code `IB-REFUSE`; matrix/table member shape,
   type, row-count, and parameter-column contracts are present. But the JSON
   contract checks only `kind='json'`. Supplying
   `extra={'temporary_scores_free37': np.zeros((5,37)).tolist()}` to
   `write_score_aggregate_summary` persisted the complete 5-by-37 block. The
   same mapping could overwrite the grade with an empty string while the
   returned record still said `subset-diagnostic`. The persistence surface is
   thus not closed by construction.

6. **Corrected PROOF-1 and PROOF-11 — PASS.** Before creation of this review,
   PROOF-1 printed exactly the five expected untracked paths and the exact clean
   nested state. PROOF-11 printed `NONE` for both generated Phase-5 artifact
   files and Phase-5 output directories. Both corrected expected outputs are
   true as printed.

Static inspection found no tracked design, package, or architecture edit; no
certified tolerance or arithmetic constant changed; the 13-column parameter
schema and 16-name aggregate artifact set remain fixed; and no runner,
transaction, manifest writer, or full-population execution path was added.
Nevertheless, the unrestricted JSON `extra` content path prevents the required
no-full-score/persistence conclusion.

## 4. Proofs executed

Refix report §10 supersedes report v1 §6. I executed all twelve commands
verbatim from `C:\Users\hisham\Repo\MNL` with the specified virtual-environment
interpreter.

| Proof | Observed | Result |
| --- | --- | --- |
| PROOF-1 | Exact HEADs, five expected untracked paths, exact gitlink, clean nested tree | PASS |
| PROOF-2 | Phase-3 `2cf23764…`; Phase-4 `54848869…`; bread `e9ca080e…`; theta `c024b893…` | PASS |
| PROOF-3 | `85 passed in 5.56s` | PASS |
| PROOF-4 | `76 passed, 9 deselected in 1.36s` | PASS |
| PROOF-5 | `9 passed, 76 deselected in 5.38s` | PASS |
| PROOF-6 | `12 passed, 73 deselected in 0.44s` | PASS |
| PROOF-7 | `6 passed, 79 deselected in 1.14s` | PASS |
| PROOF-8 | `19 passed, 66 deselected in 1.18s` | PASS for shipped cases; direct JSON/ordering probes above fail the stronger contract |
| PROOF-9 | `20 passed, 65 deselected in 1.15s` | PASS |
| PROOF-10 | `222 passed, 1 deselected in 94.60s`; test 29 deselected | PASS |
| PROOF-11 | Generated files `NONE`; output directories `NONE` | PASS |
| PROOF-12 | Every printed scalar and requested defect check reproduced | PASS |

The green suite does not cover the residuals. `test_I12` never overrides
`active_names`; `test_J15` does not assert that the target remains absent after
an empty-grade refusal; and `test_J9` does not exercise `extra`.

## 5. Regression

The review-v1 §5 numerical results are unchanged:

| Quantity | Reproduced value |
| --- | ---: |
| raw bread asymmetry | `1.8189894035458565e-12` |
| bread minimum eigenvalue | `0.10373269638807983` |
| bread condition number | `405353.9471978127` |
| meat asymmetry | `0.0` |
| meat minimum eigenvalue | `2.0597024553162405e-13` |
| correction | `1.0230263157894737` |
| solve-vs-pinv deviation | `1.9602097722781764e-12` |
| `max(abs(H_II @ V_model - I))` | `1.2038803846172754e-14` |
| T-19 maximum ratio | `0.0003819780309704067` |
| robust covariance minimum eigenvalue | `-9.474781170961761e-20` |
| regional robust minimum eigenvalue | `1.7170023605273287e-06` |
| W-1 robust/model ratio range | `0.06105116993643892` to `0.4261454847830435` |
| meat numerical rank | `34` |
| W-5 score-sum infinity norm | `22.52139019527921` |

The authoritative interior maximum remains
`0.00010992597206183063` at `beta_w_educH`; active multipliers remain
`0.8445544161794221` and `1.4682021491125388`, with ratios `7682.9` and
`13356.3`. This confirms that the refix did not alter covariance arithmetic.

The dedicated committed Increment-A suite is green: `76 passed in 70.35s`.
The guarded full suite is also green as reported above. The committed
Increment-A files remain unmodified, the nested tree remains clean, no generated
Phase-5 output exists, and the Phase-3 attempt count remains 70.

## 6. Manager-ruling completion

**R-37a — NOT COMPLETE.** The grade is present on the requested derived
containers, table attrs, metadata, and successful serializer records without a
schema change. Yet empty-grade calls write before refusing, and JSON `extra` can
replace the payload grade. Unlabelled or inconsistently labelled subset output
can therefore be persisted.

**R-37b — COMPLETE.** The authoritative
`phase4_diagnostics.json -> gradient_free` vector is required for table
construction and is the sole arithmetic source. The poisoned-CSV invariance and
the full-precision `beta_w_educH` value reproduce.

## 7. Residual defects

1. T-22's expected active-name set is caller-overridable, so a forged name set
   can satisfy the gate.
2. All three serializers validate a nonempty `inference_grade` after writing;
   `IB-REFUSE` does not leave the destination untouched.
3. `write_score_aggregate_summary(extra=...)` accepts arbitrary content, can
   persist a prohibited temporary score block, and can overwrite protected
   payload fields including `inference_grade`.

These are required-contract defects, not optional hardening. The authorized
single bounded refix has not fully closed review-v1 fixes 2, 4, and 5.

## 8. Whether Increment C may begin

Increment C may not begin. The remediation and conversion budgets are both
spent, and the remaining required fixes force return to the Goal 1 Manager for
the prescribed higher-level disposition. No commit, ledger update, runner,
transaction, dry run, or Increment-C work is authorized by this review.
