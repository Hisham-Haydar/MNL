# FR P2a Region-Live Manager Decisions (v1)

## D-1 — Canonical engine-ready frame

The geometry/reference object is the in-memory `er_b` construction defined by
§12–§12b of `fr_singles_pipeline_v1.ipynb`:

`draws/pricing`
→ `assemble_singles`
→ independent region/urbanisation/GSUR revival
→ B-pool band overwrite
→ `er_b`

The committed adapter stem and the existing root parquets are comparison
artifacts, not automatically authoritative inputs.

The production runner must reconstruct the same `er_b` object independently,
freeze it under `region_live_v1`, and prove equality with the relevant existing
frames after canonical sorting, dtype normalization, and common-column
alignment.

## D-2 — Objective and reload tolerances

Approved:

- 4-decimal target: `|negLL − 19053.4655| < 1e-2`
- full target: `|negLL − 19053.46553160094| ≤ 1e-4`
- cold reload: `|negLL_reload − negLL_stored| ≤ 1e-6`

A materially better objective is also a stop, because it means the reference fit was not reproduced as claimed.

## D-3 — Rank and regional-block criteria

Approved with one methodological amendment:

- rank tolerance = `1e-10 × max eigenvalue`
- full free Hessian rank = `37`
- regional design-matrix rank = `10`

For the regional block, require:

- the 10-column household-level regional design matrix has rank 10;
- the raw 10×10 regional Hessian sub-block is positive definite;
- the conditional regional-information matrix, computed as the regional Schur complement against the other free parameters, has rank 10 and strictly positive minimum eigenvalue.

The proposed “regional loading share below 0.5 in each of the three smallest eigenvectors” should be reported as a warning diagnostic, not used as a hard pass/fail gate. The 0.5 cutoff is informative but too arbitrary to determine identification by itself.

## D-4 — Symmetry and condition number

Approved:

- Hessian symmetry: `max|H − H′| ≤ 1e-8 × max|H|`
- condition-number reporting:
  - `≤ 1e7` clean
  - `1e7 to 1e10` warning
  - `> 1e10` hard failure

The strict report must show the actual value and compare it with the certified pooled baseline’s approximate condition number of `1.295×10^6`.

## D-5 — Remaining tolerances

Approved:

- T1 score identity:
  - `np.allclose(sum_scores, -gradient, atol=1e-8, rtol=1e-8)`
- bound-hit epsilon:
  - `1e-5`
- gradient gate:
  - `max|gradient| < 1e-2`

The gradient gate applies to the 35 free, non-bound parameters. Optimizer `success=True` remains separately required.

## D-6 — Cluster count

Approved without requiring another manager round.

The expected T3 count shall be the exact number of unique nonmissing `idorighh` values measured in the frozen region-live sample, provided that:

- the count agrees across the source mapping and frozen stem;
- every estimation household maps to exactly one cluster;
- the count is between `1` and `1,555`;
- no cluster identifier is missing.

Persist the resolved integer in the dry-run evidence and final manifest. Do not use the pooled default of `9,657`.

## D-7 — Scope of identification

Approved:

- The production rebuild may establish real-data local identification diagnostics.
- It may not claim synthetic-recovery certification of the regional block.
- A separate synthetic-recovery gate is required before:
  - promotion of P2a to a certified structural result;
  - a claim that the regional/access block is structurally identified;
  - use of P2a as a replacement for the certified pooled baseline.

The strict rebuild report may say “real-data Hessian/rank diagnostics pass,” but not “identification certified.”

## D-8 — Package upstreaming

Deferred.

Keep the chunked score orchestration in the JMP-specific `MNL/scripts/p2a/` code for this rebuild. Do not modify `dclaborsupply-monorepo`. A later package PR can evaluate whether the primitive is genuinely reusable.
