# FR P2a — JMP-M05C Increment B independent review — v1

## 1. Review-B verdict

**FINAL VERDICT: REJECT**

The numerical covariance core is sound on the bounded first-64 production path:
the authenticated and symmetrised bread, conditional-35 covariance, CR0 object,
finite-sample correction, regional selectors, and published T-22 anchors all
reproduce. The increment nevertheless fails review because six required fixes
remain. They are not one narrow remediation: T-5 is incomplete; T-22 can pass
vacuously; the parameter-table path violates the authoritative-gradient ruling;
subset-derived inferential objects lose `inference_grade`; the serializers admit
prohibited temporary score content; and two claimed PROOFS do not reproduce their
expected output.

## 2. Scope and exact state

This was an independent read-only review of the uncommitted Increment B at:

- MNL HEAD `92e299de6313bad0b0421c0db3dd268fdbcfdb59`;
- nested `dclaborsupply-monorepo` HEAD
  `27756a06ea189339aa82915ed2124628afed20eb`, clean;
- Phase-3 `attempts/`: 70 subdirectories before and after review;
- implementation SHA-256
  `218859e91073cfb4d325ec9da5870700fec49c6232d9d6fdb3094672938d98a3`;
- test SHA-256
  `90633103d0540bd04796025a18cb2b1f04a628a401d0e4d548fc4a58a5a5be75`;
- implementation-report SHA-256
  `3e9e69cf20321c889c2ec0284d3d3cc55e825c3a64615f8fc877ce46272c76b0`.

The initial untracked set was exactly the declared three Increment-B files. No
tracked file was modified, the nested worktree remained clean, and the committed
Increment-A module, tests, and conftest had an empty diff. After this review was
created, the only additional untracked path was this review. No commit, runner,
transaction, restricted-store access, or full-population run was performed.

Binding material checked: design v4 §§8, 10, 12 (including §12.4), 13–16 and
§17.3; streaming addendum §§1, 3, and 5; mission charter §§4-B and 5; the
committed parameter map; `phase4_diagnostics.json`; and the committed Increment-A
module.

## 3. Proofs executed

All twelve commands under the report's PROOFS heading were executed verbatim in
PowerShell with `\.\.venv\Scripts\python.exe` as printed. No proof created a
repository artifact. Results:

| Proof | Observed result | Review result |
| --- | --- | --- |
| PROOF-1 | Correct HEADs and clean nested tree; status also printed the required untracked implementation report | **FAIL**: the report's expected block omits its own untracked report path, so expected output does not reproduce |
| PROOF-2 | Phase-3 `2cf23764…`, Phase-4 `54848869…`, bread `e9ca080e…` | PASS |
| PROOF-3 | `59 passed in 5.57s` | PASS |
| PROOF-4 | `50 passed, 9 deselected in 1.26s` | PASS |
| PROOF-5 | `9 passed, 50 deselected in 5.13s` | PASS |
| PROOF-6 | `11 passed, 48 deselected in 0.71s` | PASS; the advertised bread rejection tests ran |
| PROOF-7 | `14 passed, 45 deselected in 1.13s` | PASS; the advertised table rejection tests ran |
| PROOF-8 | `9 passed, 50 deselected in 0.45s` | PASS for the shipped cases, but the adversarial gap in §6 remains |
| PROOF-9 | `9 passed, 50 deselected in 1.11s` | PASS |
| PROOF-10 | `196 passed, 1 deselected in 93.50s` | PASS; test 29 was deselected as required |
| PROOF-11 | Printed three committed files: `phase5_full_score_surface_inventory_v1.json`, `phase5_parameter_map_v1.csv`, and `phase5_source_inventory_v1.json` | **FAIL**: expected `NONE` is false because the scanner matches committed design/input artifacts |
| PROOF-12 | Reproduced every printed scalar, coordinate, rounded activity ratio, and `subset-diagnostic` label | PASS |

Thus the test suites are green, but the report's stronger claim that every
command and expected output reproduces is false. PROOF-11 also cannot establish
its stated no-artifact conclusion with its present predicate.

## 4. Design conformance

Conforming portions:

- `load_bread` hashes `hessian_free.npy` to `e9ca080e…`, checks raw asymmetry
  against `2.3588019878151842e-4`, symmetrises as `(H + H.T)/2`, and constructs
  `H_II` by authenticated interior names. There is no Hessian recomputation.
- Model covariance uses Cholesky factorisation/solve. Static inspection found no
  `np.linalg.inv`; the sole `np.linalg.pinv` occurrence is the T-8 reference.
- The robust object is `c * B @ M @ B`, with `c = 1555/1520`; the separate
  `V_robust_cr0` makes CR0 exactly recoverable.
- The parameter-table frame has exactly 47 rows and the design's 13 columns.
  Active-bound and pinned rows carry literal `NA` in the five inferential fields.
  The mandatory footnote's rendered wording is present in full.
- `E_R` and all H0-A/B/C/G selectors are constructed by authenticated names.
  Model and robust Wald results have separate `p_model` and `p_robust` fields.
- The certified constants inspected, including T-7's `6.0424e-12`, are
  unaltered. The production tests use the committed Increment-A reducer and the
  real Increment-B covariance builder; no subject-under-test substitution made
  the production family green.

Nonconforming gate surface:

1. Design-v4 T-5 includes the accepted theta-byte hash `c024b893…`.
   `gate_T5_bread_provenance` checks only bread, Phase-3 bundle, and Phase-4
   bundle hashes. Its observed/bar keys contain no theta hash.
2. T-22 is not a complete check of the two authenticated active coordinates.
   `gate_T22_numerical_kkt({}, 1e-4)` returns passed, as does a dictionary whose
   only key is `wrong_name`. The function must require exactly
   `beta_l_age2_sm` and `beta_l_age2_sf`, reject missing/extra names, and then
   apply the certified factor.

These defects contradict the report's claim that every applicable T/W gate is a
complete checkable implementation of the frozen statement.

## 5. Numerical results

The streamed first-64 aggregate reproduces the report and stays within the
applicable design bars:

| Quantity | Observed | Bar / interpretation |
| --- | ---: | --- |
| raw bread asymmetry | `1.8189894035458565e-12` | `<= 2.3588019878151842e-4` |
| bread minimum eigenvalue | `0.10373269638807983` | Phase-4 anchor `0.1037326963880782`, rtol `1e-10` |
| bread condition number | `405353.9471978127` | Phase-4 anchor `405353.94719781954`, rtol `1e-10` |
| meat raw asymmetry | `0.0` | T-7 pass |
| meat minimum eigenvalue | `2.0597024553162405e-13` | floor `-1.42580003805006e-08` |
| correction | `1.0230263157894737` | exactly `1555/1520` |
| solve-vs-pinv deviation | `1.9602097722781764e-12` | `<= 1e-8` |
| `max(abs(H_II @ V_model - I))` | `1.2038803846172754e-14` | solve residual |
| T-19 worst ratio | `0.0003819780309704067` | `<= 0.05` |
| robust covariance minimum eigenvalue | `-9.474781170961761e-20` | T-9 PSD floor passed |
| regional robust minimum eigenvalue | `1.7170023605273287e-06` | T-14 PD/rank 10 passed |
| W-1 robust/model ratio range | `0.06105116993643892` to `0.4261454847830435` | warning, expected at subset scale |
| meat numerical rank | `34` | subset diagnostic only |
| W-5 score-sum infinity norm | `22.52139019527921` | subset diagnostic only |

T-22 read the authoritative JSON and reproduced the accepted interior maximum
bit-for-bit as `1.0992597206183063e-4` at `beta_w_educH`. The active multipliers
were exactly `0.8445544161794221` and `1.4682021491125388`; the published ratios
round to `7682.9` and `13356.3`.

The report itself makes no regional or precision inferential claim from the
64-household prefix. Its scale-free/structural/whole-sample separation is
substantively correct. The object-propagation defect below nevertheless leaves
unlabelled subset Wald and parameter-table outputs available to serializers.

## 6. Serializer and no-persistence probes

Positive evidence:

- A deliberately mislabelled `float64` array of shape `(1555, 1)` was refused
  with `IB-REFUSE`, proving the leading-dimension household-scale rule is active.
- The shipped 5-by-37 score-block and identifier-paired-frame failure tests pass.
- Static inspection found writes only in the three serializer functions; no
  Phase-5 output was added to the repository, and the final git state contained
  only the declared untracked source, test, report, and review.

Adversarial failures:

- `assert_aggregate_payload(np.zeros((5, 35)), "temporary_interior_scores")`
  was accepted. This is a temporary row-level interior-score batch prohibited by
  addendum §3. Because `write_table` accepts any DataFrame under any allowed
  table member, the closed filename set does not repair the shape gap.
- A numeric DataFrame containing `NaN` was accepted, contrary to the report's
  claim that non-finite content is refused. The ndarray branch checks finiteness;
  the DataFrame branch does not.

The serializers therefore do not yet refuse row-level content by construction.
They need member-specific type/shape schemas (including 35-column score-block
rejection where distinguishable) and a numeric-finiteness check for DataFrames.

## 7. Manager rulings

**R-37a.** `inference_grade` is accepted as implementation metadata, not a new
design gate or altered tolerance. It must propagate into Increment C and the
dry-run manifest. The present implementation is incomplete: a first-64
covariance says `subset-diagnostic`, and W-1/W-4/W-5 echo it, but
`RegionalTests.diagnostics`, the regional table, and `ParameterTable` carry no
grade. Consequently subset Wald statistics/p-values and precision rows can be
serialized without the label. Preserve the exact 13-column parameter schema and
carry the grade as enclosing-object/manifest metadata.

**R-37b.** `phase4_diagnostics.json -> gradient_free` is the sole authoritative
gradient. The CSV `grad_free_negll` column may be a rendering or cross-check
only and must never feed arithmetic. `load_accepted_gradients` and T-19/T-22
follow this ruling, but `build_parameter_table` does not: it reads the CSV for
all free gradients and computes active multipliers as `-g`. At
`beta_w_educH`, the table renders `0.0001099259720618` while the authoritative
value is `0.00010992597206183063`. The active CSV values happen to round-trip
exactly, but source authority cannot depend on that accident.

## 8. Residual defects

1. T-5 omits the accepted theta-byte hash required by design v4 §15.
2. T-22 passes with an empty or wrong-name multiplier mapping.
3. The table builder uses CSV gradient values and derives multipliers from them,
   violating R-37b and the report's “never the CSV for gradient values” claim.
4. `inference_grade` does not propagate to regional and parameter-table objects,
   so the subset-diagnostic label is not everywhere on first-64 outputs.
5. Serializer shape/finite checks admit a 5-by-35 temporary score block and a
   non-finite DataFrame.
6. PROOF-1 and PROOF-11 expected outputs are false as printed.

The green test suite does not cover these cases. In particular, G8 proves that a
JSON loader exists but does not prove that all downstream gradient consumers use
it; K7 checks only W-1 and W-4 propagation; J1/J2 omit a 35-column temporary
score block; and no gate test supplies an empty or forged T-22 mapping.

## 9. Required fixes

1. Add theta-byte authentication to T-5 and test both a match and a one-byte
   mismatch.
2. Make T-22 validate the exact two authenticated active names before applying
   the `100x` threshold; add empty, missing, extra, and wrong-name failures.
3. Pass `AcceptedGradients` into the table builder, project by authenticated
   names, and use those JSON values for `grad_negll` and multipliers. Treat the
   CSV column only as an explicit non-authoritative comparison.
4. Propagate `inference_grade` through all covariance-derived containers and
   serializer/manifest metadata without changing the fixed 13-column table.
5. Enforce member-specific serializer type/shape contracts and numeric
   finiteness for DataFrames; add mislabelled 5-by-35 and non-finite-frame tests.
6. Correct the report's PROOF-1 expected state and narrow PROOF-11 to generated
   Phase-5 output locations/names so its expected `NONE` is true and checkable.

## 10. Whether Increment C may begin

Increment C may not begin. The charter permits only one narrow remediation for
an approval-after-fixes path; this review identifies six independent fixes,
including design-gate and no-row-persistence defects. Apply the fixes under a
new bounded Increment-B remediation and obtain a fresh independent Review B
before any runner, transaction, reproduction work, commit, or dry run.
