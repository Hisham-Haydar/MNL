# FR P2a Region-Live Manager Decisions (v2)

## Status

- **v2 is canonical for implementation.** Every production script, run-config, gate table, and
  implementation prompt must trace to this document, not to v1.
- **v1** (`FR_P2a_region_live_manager_decisions_v1.md`) is retained unchanged as the **historical
  pre-notebook-integration decision record**. Where v1 and v2 differ (only D-1), v2 governs.
- The **formal 47-parameter pooled baseline is unchanged**: `joint_pooled_v1_bll0_tlmpin`
  (France 2015–2017 pooled; JAX; singles 101 / couples 901; negLL 238504.6360973987;
  synthetic-recovery certified; real-data Hessian positive definite; clustered on `idorighh`).
- **P2a region-live remains provisional** (target negLL 19053.4655): not accepted, not safe for
  inference, manuscript results, or certified welfare, pending the production rebuild and strict
  diagnostics. The theta pointer in `p2a_fit_provenance.json` remains UNRESOLVED.

## D-1 — Canonical engine-ready frame (BINDING CLARIFICATION — replaces v1 D-1)

The production runner must independently reconstruct the notebook's in-memory `er_b` object, but
**Phase 1 must not rerun EUROMOD or regenerate proposal draws.**

The reconstruction boundary is:

frozen already-priced P2a draw artifacts
→ `assemble_singles`
→ independently reconstruct `drgn1/drgur/drgmd/drgru/gsur`
→ apply B-pool band overwrite
→ `er_b`
→ freeze under `region_live_v1/`

The existing engine-ready frames are **comparison artifacts only** and must not be copied as the
new canonical object.

The authoritative sources are split by role:

1. **Geometry, draws, proposal densities and already-computed EUROMOD outcomes:** use the frozen
   upstream priced-draw artifacts actually consumed by §§12–12b of `fr_singles_pipeline_v1.ipynb`.
   As identified from the executed notebook (reconciliation report §5), these are:
   - **EUROMOD pricing cache** (already-computed outcomes, read by §10 cell `ec=22`, resumable /
     `SKIP_PRICING`): `MNL/fr_singles_pricing_p2a/priced_{00000,00200,00400,00600,00800,01000,
     01200,01400}.parquet` — 8 git-tracked chunks, 225,836 rows, all 1,555 households, columns
     `idhh, idperson, source_idhh, source_idorighh, source_idperson, ruro_decider, dgn, draw,
     ils_dispy, bsa00_s`.
   - **Draw geometry + proposal densities** (`draws_p2a`: per-(idhh, draw) hours, wage, loc4,
     working, band flags, `log_prior`/`log_q_*`): consumed by §12 via `feat2`/`alt2` but **not
     persisted by the notebook** — it exists only in-memory (§9, seed 2026). A frozen geometry
     artifact must be produced during **notebook stabilization** (by `fr_singles_pipeline_v2.ipynb`)
     and hashed before Phase 1 may start. Phase 1 consumes only the frozen artifact; it never
     re-draws.
2. **Region and urbanisation:** reconstruct from `EUROMOD-STORAGE/Data/FR/FR_2016_a3.txt`
   (`drgn1`; `drgur/drgmd/drgru` from EU-SILC `db100`).
3. **GSUR:** reconstruct from `EUROMOD-STORAGE/Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`
   using the documented keys `(drgn1, educ3, sex)` (opportunity-year 2015 for the 2016 wave).

If the frozen upstream priced-draw inputs cannot be identified unambiguously or are unavailable,
the plan verdict is BLOCKED. An engine-ready parquet must never be substituted for them.

A later separate gate may test end-to-end draw-generation and EUROMOD-pricing reproducibility.
That is outside this rebuild.

## D-2 — Objective and reload tolerances (carried from v1, ratified)

- 4-decimal target: `|negLL − 19053.4655| < 1e-2`
- full target: `|negLL − 19053.46553160094| ≤ 1e-4`
- cold reload: `|negLL_reload − negLL_stored| ≤ 1e-6`

A materially better objective is also a stop, because it means the reference fit was not reproduced as claimed.

## D-3 — Rank and regional-block criteria (carried from v1, ratified with amendment)

- rank tolerance = `1e-10 × max eigenvalue`
- full free Hessian rank = `37`
- regional design-matrix rank = `10`

For the regional block, require:

- the 10-column household-level regional design matrix has rank 10;
- the raw 10×10 regional Hessian sub-block is positive definite;
- the conditional regional-information matrix, computed as the regional Schur complement against
  the other free parameters, has rank 10 and strictly positive minimum eigenvalue.

The "regional loading share below 0.5 in each of the three smallest eigenvectors" is reported as a
**warning diagnostic, not a hard pass/fail gate**. The 0.5 cutoff is informative but too arbitrary
to determine identification by itself.

## D-4 — Symmetry and condition number (carried from v1, ratified)

- Hessian symmetry: `max|H − H′| ≤ 1e-8 × max|H|`
- condition-number reporting (three-tier):
  - `≤ 1e7` clean
  - `1e7 to 1e10` warning
  - `> 1e10` hard failure

The strict report must show the actual value and compare it with the certified pooled baseline's
approximate condition number of `1.295×10^6`.

## D-5 — Remaining tolerances (carried from v1, ratified in full)

- T1 score identity: `np.allclose(sum_scores, -gradient, atol=1e-8, rtol=1e-8)`
- bound-hit epsilon: `1e-5`
- gradient gate: `max|gradient| < 1e-2` on the **35 free, non-bound parameters**
- optimizer `success=True` is separately required.

No further manager round is needed on any of these values.

## D-6 — Cluster count (carried from v1, ratified in full)

The expected T3 count is resolved **automatically** as the exact number of unique nonmissing
`idorighh` values measured in the frozen region-live sample, provided that:

- the count agrees across the source mapping and frozen stem;
- every estimation household maps to exactly one cluster;
- the count is between `1` and `1,555`;
- no cluster identifier is missing.

Persist the resolved integer in the dry-run evidence and final manifest. Do **not** use the pooled
default of `9,657`. **This decision does not wait for another manager round** — the measured value
is self-ratifying under the four conditions above.

## D-7 — Scope of identification (carried from v1, ratified in full)

- The production rebuild may establish real-data local identification diagnostics.
- It may not claim synthetic-recovery certification of the regional block.
- **Synthetic recovery is mandatory** before:
  - promotion of P2a to a certified structural result;
  - a claim that the regional/access block is structurally identified;
  - use of P2a as a replacement for the certified pooled baseline.

The strict rebuild report may say "real-data Hessian/rank diagnostics pass," but not
"identification certified."

## D-8 — Package upstreaming (carried from v1, ratified)

Deferred.

Keep the chunked score orchestration in the JMP-specific `MNL/scripts/p2a/` code for this rebuild.
Do not modify `dclaborsupply-monorepo`. A later package PR can evaluate whether the primitive is
genuinely reusable.
