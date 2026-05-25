> Archived on 2026-05-26 — region-dummy repair completed; absorbed into the corrected-region chain.
> Live chain (kept active): `docs/France_case/execution_logs/pooled_P3a/JMP_pooled_P3a_corrected_region_reestimation_authorization_v1.md` and `..._corrected_region_post_estimation_review_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP Pooled P3a — Region-Dummy Repair Authorization v1

*France FR_2015 / FR_2016 / FR_2017 | v1 | 2026-05-21*

Specification class: narrow repair authorization memo. This memo
authorises the resolution of the single data-build / precompute defect
that the region-dummy non-identification diagnostic traced as the cause
of the flat likelihood ridge in `beta_E_drgn2`–`beta_E_drgn8`. It
authorises a couples data-build fix and a precompute value-presence
guard, the regeneration and validation of the estimation-ready split
stem, and a rerun of the read-only region-dummy diagnostic. It does NOT
authorise re-estimation, the no-region design route, welfare, an SA2
verdict, canonical promotion, or any displacement of M1-clean 2016.

Reference documents:
- `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md` (the
  read-only diagnostic — cause B/DEGENERATE_OR_MISWIRED_COLUMNS)
- `docs/JMP_pooled_P3a_post_estimation_review_v1.md` (the strict
  post-estimation review that gated this diagnostic and withheld SA2)
- `Results/JMP_pooled_P3a_estimation_report_v2.md` (the pooled
  estimation whose region block is non-identified)
- `docs/JMP_pooled_P3a_estimation_execution_repair_authorization_v1.md`
  and `docs/JMP_pooled_P3a_estimation_execution_repair_clearance_v1.md`
  (the prior split-stem repair and its clearance — the build step now
  being corrected)
- `scripts/maintenance/prepare_pooled_estimation_ready.py` (the
  split-stem build script to fix under R1)
- `scripts/enhanced/estimation_utils.py` (the precompute functions to
  harden under R2)

Interpreter of record: `.venv\Scripts\python.exe`.

---

## 1. Purpose

The purpose of this memo is to authorise a narrow, well-scoped repair of
the data-build / precompute defect that the region-dummy diagnostic
identified as the cause — classified B/DEGENERATE_OR_MISWIRED_COLUMNS,
not structural redundancy — of the exact non-identification of the seven
pooled region dummies. The repair has two parts, R1 and R2, and three
downstream obligations (regenerate-and-validate, rerun the diagnostic,
rerun preflight only if needed).

The diagnostic is decisive on the failure chain. The couples split
parquet carries `reg_nuts1_2`–`reg_nuts1_8` as columns that are present
in the schema but entirely NaN (743,800 / 743,800 missing). Because
`precompute_data_couples` tests schema presence (`"reg_nuts1_2" in
df.columns`) rather than value presence, it takes the direct-column
branch, calls `fillna(0.0)`, and produces seven all-zero arrays; the
valid `drgn1` fallback (fully populated, 8 region codes, all 24
region×year cells occupied) is never reached. In the couples
market-opportunity index the region contribution is then
`beta_E_drgn_k × 0 × working = 0` for every alternative and observation,
so the joint-likelihood gradient with respect to each region dummy is
identically zero and the likelihood is exactly flat in those seven
directions. The singles submodel offers no backup: a separate
`applies_to: "household"` guard in the singles market-opportunity path
skips region dummies entirely, so region identification can only come
through the couples index. The diagnostic ruled out collinearity (the
`drgn1`-derived design has rank 9/9, condition number 3.195) and ruled
out inconclusiveness.

This memo authorises R1 (populate the couples region dummies from
`drgn1` in the data build) and R2 (harden `precompute_data_couples` to
require non-missing, non-degenerate values before taking the direct
path, else use the `drgn1` fallback), regenerates and validates the
estimation-ready split stem, and reruns the diagnostic to confirm the
region dummies are now wired and would be identified. It does not run
the solver and does not pre-judge whether the re-estimated region block
is significant — that is a later gate.

---

## 2. Current diagnostic verdict

**The diagnostic verdict is B/DEGENERATE_OR_MISWIRED_COLUMNS: a
data-build / precompute wiring defect, not structural redundancy.**

The seven couples region-dummy columns are all-NaN; the precompute
schema-presence test takes the wrong branch and zeroes them via
`fillna(0.0)`; the `drgn1` fallback is unreachable; the region dummies
receive no usable variation in the joint likelihood; the singles
`applies_to: "household"` guard removes the only alternative
identification channel. The `drgn1` column is valid and fully populated
in the couples split, and the diagnostic confirmed no structural
collinearity (rank 9/9, condition 3.195). The flat ridge observed in the
three-start estimation (Start 2 at exactly 0.000 for all seven; Starts 1
and 3 at different non-zero vectors; identical joint LL −57,280.6213) is
the empirical signature of this defect, not of redundancy.

This verdict is what distinguishes the present memo from the
no-region-design route: the region dimension is not shown to be
genuinely uninformative; it was never given a chance to inform the
likelihood because its couples input was zero.

---

## 3. Why no-region design is not authorized yet

The pooled no-region-dummy specification is **not** authorised at this
stage, and must not be adopted as a shortcut around this repair.

The strict reason is that the no-region design is only defensible if the
region dimension is genuinely uninformative — cause A
(intact-and-wired-but-collinear/redundant). The diagnostic found cause
B: the region dummies were zeroed by a build defect before they could
inform the likelihood. Dropping them now would **mask** a data bug and
silently discard a region-based opportunity dimension that M1-clean
identified cross-sectionally and that the corrected pooled data may well
identify. Canonising a region-free spec on the strength of a flat ridge
that was manufactured by an all-NaN input column would be a measurement
error, not a modelling simplification.

The correct order is: fix the data and the guard (R1, R2), regenerate
and validate, rerun the diagnostic, and only then — on the corrected
data — decide whether the region dimension is identified and
informative. If, after the repair, the region block is properly wired
and still found redundant or insignificant on a future re-estimation,
the no-region design becomes a legitimately evidenced option at that
later gate. It is premature now.

---

## 4. Root cause to repair

The root cause is a two-link defect, and both links are repaired.

**Link 1 — data build (the originating defect).** The pooled P3a
data-build step
(`scripts/maintenance/prepare_pooled_estimation_ready.py`) wrote the
couples split with `reg_nuts1_2`–`reg_nuts1_8` present as columns but
entirely NaN, while the valid region source `drgn1` was carried through
intact. The singles split was built correctly (region dummies populated,
two unique values each). The defect is couples-specific and originates
in the build, upstream of estimation.

**Link 2 — precompute guard (the defect that let it through silently).**
`estimation_utils.py:precompute_data_couples` selects the region source
by schema presence (`if "reg_nuts1_2" in df.columns`) rather than value
presence. With the columns present-but-NaN, it takes the direct branch,
applies `fillna(0.0)`, and never reaches the `elif "drgn1"` fallback.
This converted a data defect into a silent, estimable-but-flat model
instead of an error or a fallback.

R1 repairs Link 1 (so the data is self-describing and correct). R2
repairs Link 2 (so the precompute can never again silently accept
present-but-empty region columns, on this or any future build). Both are
required: R1 fixes the actual data used; R2 prevents recurrence and
makes the fallback reachable when appropriate.

---

## 5. Authorized repair R1: couples region-dummy data-build fix

**R1 — populate the couples region dummies from `drgn1` in the data
build.**

Modify the pooled data-build step (the split-stem builder
`scripts/maintenance/prepare_pooled_estimation_ready.py`, or the
upstream couples-construction step it calls) so that, for the couples
split, `reg_nuts1_2`–`reg_nuts1_8` are derived from `drgn1` whenever the
existing `reg_nuts1_*` columns are absent or entirely missing:

```python
# For the couples split, when reg_nuts1_* are absent or all-NaN:
for k in range(2, 9):
    df_couples[f"reg_nuts1_{k}"] = (df_couples["drgn1"] == k).astype(float)
```

Region 1 (Île-de-France) remains the omitted reference and is not given
a dummy, consistent with the specification. The derivation must reproduce
the region support the diagnostic documented from `drgn1`: all 24
couples region×year cells populated (minimum cell 172 households), 8
region codes, 7,438 couples household-year choice sets.

R1 is the load-bearing repair: because the singles `applies_to:
"household"` guard removes region dummies from the singles index,
region identification can come only through the correctly built couples
index. The derivation must be guarded so it fires only when the
`reg_nuts1_*` columns are missing or all-NaN, and does not overwrite
already-valid columns (so the same builder remains correct for any build
that already populates them directly).

---

## 6. Authorized repair R2: precompute value-presence guard

**R2 — harden `precompute_data_couples` to test value presence, not
schema presence.**

Modify `estimation_utils.py:precompute_data_couples` so the direct
`reg_nuts1_*` column path is taken only if at least one region-dummy
column has non-missing, non-degenerate values; otherwise fall back to
`drgn1`:

```python
# Value-presence guard, not schema-presence:
_reg_cols = [f"reg_nuts1_{k}" for k in range(2, 9)]
_reg_direct_usable = (
    all(c in df.columns for c in _reg_cols)
    and any(df[c].notna().any() for c in _reg_cols)
    and any(df[c].fillna(0).nunique() > 1 for c in _reg_cols)
)
if _reg_direct_usable:
    # direct reg_nuts1_* path
    ...
elif "drgn1" in df.columns:
    # drgn1 fallback (now reachable when direct columns are empty/degenerate)
    ...
else:
    # explicit error: no usable region source
    raise ...
```

"Non-degenerate" means at least one region column is not constant after
`fillna(0)` (i.e., not all-zero). The guard must (a) take the direct
path when the columns are genuinely populated, (b) take the `drgn1`
fallback when the direct columns are absent, all-NaN, or all-zero, and
(c) raise an explicit error if neither a usable direct column set nor
`drgn1` is available, rather than silently producing zero arrays. The
fallback path must produce the same `data.reg2`–`data.reg8` arrays that
a correct direct build would produce.

R2 makes R1 robust: even if a future build again writes empty
`reg_nuts1_*` columns, the precompute will reach the `drgn1` fallback or
error loudly, never silently zero the region block. With R1 applied, the
direct path will be valid and used; R2 is the defence-in-depth that
prevents silent recurrence.

---

## 7. Required regenerated files

The repair must regenerate and validate the estimation-ready split stem:

- `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet`
  — regenerated with `reg_nuts1_2`–`reg_nuts1_8` populated from `drgn1`
  (non-NaN, binary, summing across regions consistently with `drgn1`).
- `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet`
  — **preserved** unless validation shows it must be regenerated for
  consistency (its region dummies are already valid per the diagnostic;
  regenerate only if a schema or alignment check requires it, and
  document the reason if so).
- `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json`
  — regenerated/updated if and only if the column set or metadata
  changes; otherwise preserved. Any change documented.

The regeneration must preserve, exactly: the row counts (singles
500,700; couples 743,800; total 1,244,500), the 12,445 household-year
choice sets, the 9,657 unique `idorighh` clusters, the cluster key
(`cluster_id = idorighh`), the household-type-specific income routing
(singles `ils_dispy_real`; couples `ils_dispy_male` / `ils_dispy_female`;
couples consumption path does not read `ils_dispy_real`), and the year
indicators (`year_2015_indicator = 1[year_tag == 1]`,
`year_2017_indicator = 1[year_tag == 3]`). The repair changes only the
couples region-dummy columns (and, if strictly necessary for
consistency, the singles file and metadata).

---

## 8. Required validation checks

The repair must pass the following checks. None invokes the solver.

- **(V1) Couples region columns now valid.** In the regenerated couples
  split, `reg_nuts1_2`–`reg_nuts1_8` are non-NaN `float64`, binary
  (values in {0,1}), and not all-zero; each household-year takes exactly
  one region (the seven dummies plus the omitted region 1 partition the
  sample), reproducing the diagnostic's `drgn1` region support (all 24
  region×year cells populated; minimum cell 172).
- **(V2) `drgn1` consistency.** For every couples row,
  `reg_nuts1_k == 1` iff `drgn1 == k` (k = 2..8), and all seven are 0
  iff `drgn1 == 1`.
- **(V3) Singles unchanged (or documented).** The singles region columns
  remain valid and unchanged; if the singles file was regenerated, the
  reason is documented and its region columns still pass the V1-style
  checks.
- **(V4) Conservation.** Row counts (500,700 / 743,800 / 1,244,500),
  household-year count (12,445), and cluster count (9,657 unique
  `idorighh`) are preserved.
- **(V5) Cluster key and income routing preserved.**
  `cluster_id == idorighh` on both files; singles carry `ils_dispy_real`;
  couples carry `ils_dispy_male` / `ils_dispy_female`; the couples
  consumption path does not read `ils_dispy_real`.
- **(V6) Year indicators preserved.** `year_2015_indicator` and
  `year_2017_indicator` present and correct on both files per the
  established derivation.
- **(V7) Loader accepts regenerated stem.** `load_and_validate_mnl_data`
  accepts the regenerated split stem with `strict_validation=True`.
- **(V8) Precompute now takes the correct region path.** With R2 applied,
  `precompute_data_couples` on the regenerated couples split takes the
  direct `reg_nuts1_*` path (now value-valid) and produces non-zero,
  non-degenerate `data.reg2`–`data.reg8`; and, as a guard test, on a
  synthetic all-NaN couples input it takes the `drgn1` fallback (or
  errors if `drgn1` is also absent) rather than silently zeroing.
- **(V9) Smoke-test interface intact.** The cluster-robust SE
  `--mode smoke-test` and the estimator CLI remain callable; no
  estimation is run.

---

## 9. Required diagnostic rerun

After the repair and the V1–V9 validation, **rerun the read-only
region-dummy non-identification diagnostic** on the regenerated split
stem, saved as
`Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md`.

The rerun must, with no estimation:
- confirm the couples region columns are now populated and wired into
  the couples market-opportunity index (the `beta_E_drgn_k × reg_k ×
  working` contribution is now non-zero and varies across alternatives);
- confirm the design block remains full-rank and well-conditioned
  (region vs `gsur`, year dummies, occupation dummies) — i.e., that
  fixing the data did not introduce collinearity;
- re-classify the cause: the expected post-repair classification is that
  the region dummies are now identifiable (the cause-B defect resolved);
- explicitly note that whether the region dummies are statistically
  significant once estimated is a separate question that this read-only
  diagnostic does not and cannot answer (it requires re-estimation,
  which is not authorised here).

The diagnostic rerun is the gate that confirms the repair achieved its
purpose (region dummies now wired and identifiable) without running the
solver.

---

## 10. What is authorized

The following are authorized by this memo, and only these.

- **(A1) R1** — the couples region-dummy data-build fix: derive
  `reg_nuts1_2`–`reg_nuts1_8` from `drgn1` in the couples split when the
  existing columns are absent or all-NaN (§5).
- **(A2) R2** — the precompute value-presence guard in
  `precompute_data_couples`: take the direct path only when the region
  columns are non-missing and non-degenerate, else the `drgn1` fallback,
  else error (§6).
- **(A3) Regenerate and validate** the estimation-ready split stem,
  preserving the singles file unless validation requires otherwise (§7),
  and running checks V1–V9 (§8).
- **(A4) Rerun the read-only region-dummy diagnostic** on the
  regenerated stem and save it as v2 (§9).
- **(A5) Rerun preflight only if needed** to confirm estimator
  compatibility with the regenerated stem (for example, if the column
  set or metadata changed). If the regenerated stem is schema-compatible
  and only the couples region values changed, a full preflight rerun is
  not required; a targeted load/precompute confirmation (V7, V8)
  suffices. Any preflight rerun is saved as a versioned report.
- **(A6) Write the repair report** (§13) and the regenerated files to
  their documented paths.

---

## 11. What is not authorized

The following are NOT authorized by this memo. Each remains gated.

- **(N1) Re-estimation / running the solver.** No pooled estimation is
  run. The corrected data is prepared and validated; estimation against
  it is a separate, later gate requiring its own authorization.
- **(N2) The pooled no-region design route.** Not adopted; not designed;
  not authorised (§3).
- **(N3) Welfare computation.** Not authorised; separately gated behind
  an accepted SA2 verdict.
- **(N4) An SA2 verdict.** Not issued. The SA2 verdict remains a later
  adjudication gate; the strict post-estimation review precedes it.
- **(N5) Canonical promotion.** No output — the regenerated split stem,
  the hardened precompute, any future estimate — is promoted to
  canonical status. The regenerated stem is a corrected candidate input
  at a documented path.
- **(N6) M1-clean displacement.** M1-clean 2016 remains the active JMP
  baseline.
- **(N7) Specification modification.** The pooled YAML is not modified;
  the 55-parameter `ruro_occ_P3a_pooled` spec, including the seven region
  shifters, is unchanged. The repair is to the data and the precompute,
  not the spec.
- **(N8) Any modification beyond R1, R2, and the regeneration.** No other
  change to the estimator, the engine, the loader, or the singles build
  (unless V3 strictly requires a documented singles regeneration).

---

## 12. Halt conditions

The repair halts under the following conditions. Each halt preserves the
outputs produced up to the halt and requires diagnosis before the repair
proceeds.

- **(H1) `drgn1` not usable.** If `drgn1` in the couples split is not in
  fact valid (missing values, fewer than 8 region codes, or empty
  region×year cells) — contradicting the diagnostic — the repair halts:
  R1 cannot derive the region dummies from a defective source, and the
  cause must be re-diagnosed.
- **(H2) Region partition inconsistent.** If V1/V2 fail — if the derived
  `reg_nuts1_k` do not form a clean one-region-per-household partition
  consistent with `drgn1` — the repair halts.
- **(H3) Conservation broken.** If V4 fails — if regeneration loses or
  duplicates rows, household-years, or clusters — the repair halts.
- **(H4) Cluster key or income routing corrupted.** If V5 fails — if the
  cluster key changes, or the couples consumption path would read
  `ils_dispy_real`, or income columns are dropped or mixed — the repair
  halts.
- **(H5) Precompute still zeros the region block.** If V8 fails — if,
  after R1 and R2, `precompute_data_couples` still produces all-zero or
  degenerate `data.reg2`–`data.reg8` on the regenerated couples split —
  the repair halts: the wiring is not fixed.
- **(H6) New collinearity introduced.** If the diagnostic rerun (§9)
  finds the region-plus-related design block is no longer full-rank /
  well-conditioned after the fix, the repair halts and reports, rather
  than proceeding as if the region dimension were cleanly identified.
- **(H7) Solver, re-estimation, no-region design, welfare, SA2,
  canonical, M1-clean displacement, or spec modification attempted.** If
  the repair would do any of these, it halts: none is authorised (§11).

---

## 13. Required repair report

The repair must be recorded in a report saved as
`Results/JMP_pooled_P3a_region_dummy_repair_report_v1.md`. The report
must include:

- the repair verdict (R1 and R2 applied; whether the region dummies are
  now wired and identifiable on the regenerated data) and a one-line
  status per repair;
- the files modified (the data-build script; `estimation_utils.py`) and
  the files regenerated (the couples split; the singles split and
  metadata only if regenerated, with the reason), each with a one-line
  change summary;
- for R1: the derivation rule, the guard that fires it only when the
  existing columns are absent or all-NaN, and the resulting couples
  region support (the 24 region×year cells, reproducing the diagnostic's
  `drgn1` distribution);
- for R2: the value-presence guard logic, with explicit confirmation
  that the direct path requires non-missing and non-degenerate values,
  that the `drgn1` fallback is now reachable, and that the no-usable-
  source case errors rather than silently zeroing;
- the validation results V1–V9, each PASS/FAIL with detail, including
  the V8 demonstration that precompute now produces non-zero region
  arrays on the real data and falls back (or errors) on a synthetic
  all-NaN input;
- a pointer to the diagnostic rerun
  (`...region_dummy_nonident_diagnostic_v2.md`) and its post-repair
  classification;
- whether a preflight rerun was needed and, if so, its result;
- any halt (§12) and its diagnosis;
- a "what was not executed" section confirming: no solver run, no
  re-estimation, no welfare, no SA2, no canonical promotion, no
  no-region design adopted, no spec modification, no M1-clean
  displacement;
- the required final statements (below).

**Required final statements (to appear in the repair report):**
- R1 (couples region-dummy data-build fix) and R2 (precompute
  value-presence guard) are applied; the region dummies are now wired
  and identifiable on the regenerated data (or the repair halted, with
  the halting condition named).
- The solver was NOT run; no re-estimation was performed.
- The pooled no-region design route was NOT adopted.
- Welfare computation is NOT authorized; none was run.
- No SA2 verdict was issued; no output was promoted to canonical status.
- M1-clean 2016 remains the active JMP baseline.

---

## 14. Exact Claude Code task

Tool path: **Claude Code** (local data-build and source repair). Not the
project chat — this task modifies local files and regenerates data.

Interpreter: `.venv\Scripts\python.exe`.

Files to confirm present before starting: the couples and singles split
parquets and `__mnlmeta.json` under
`Data/processed/fr/pooled/`; the build script
`scripts/maintenance/prepare_pooled_estimation_ready.py`;
`scripts/enhanced/estimation_utils.py`; the pooled YAML; the loader
`load_and_validate_mnl_data`; the diagnostic
`Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v1.md`; and this
authorization.

Prompt to use:

> Execute the narrow region-dummy repair per
> `docs/JMP_pooled_P3a_region_dummy_repair_authorization_v1.md`. Use the
> interpreter `.venv\Scripts\python.exe`. Do NOT run the solver. Do NOT
> re-estimate. Do NOT adopt the pooled no-region design. Do NOT compute
> welfare. Do NOT issue an SA2 verdict. Do NOT promote any output to
> canonical status. Do NOT modify the pooled YAML. Do NOT replace
> M1-clean 2016 as the active baseline.
>
> R1 — Couples region-dummy data-build fix. In the pooled split-stem
> builder (`scripts/maintenance/prepare_pooled_estimation_ready.py`, or
> the upstream couples-construction step it calls), derive
> `reg_nuts1_2`–`reg_nuts1_8` for the couples split from `drgn1` whenever
> the existing `reg_nuts1_*` columns are absent or entirely NaN:
> `df_couples[f"reg_nuts1_{k}"] = (df_couples["drgn1"] == k).astype(float)`
> for k = 2..8. Guard the derivation so it does not overwrite
> already-valid columns. Region 1 stays the omitted reference.
>
> R2 — Precompute value-presence guard. In
> `scripts/enhanced/estimation_utils.py:precompute_data_couples`, replace
> the schema-presence test with a value-presence test: take the direct
> `reg_nuts1_*` path only if all seven columns are present AND at least
> one has non-missing values AND at least one is non-degenerate
> (not all-zero after fillna); else take the `drgn1` fallback (produce
> the same `data.reg2`–`data.reg8` arrays a correct direct build would);
> else raise an explicit error rather than silently zeroing.
>
> Regenerate `fr_p3a_gsurv2_estimation_ready__couples.parquet` with the
> populated region columns. Preserve the singles parquet and the
> `__mnlmeta.json` unless a schema/alignment check requires regenerating
> them — if so, document the reason. Preserve exactly: row counts
> (500,700 / 743,800 / 1,244,500), 12,445 household-years, 9,657
> `idorighh` clusters, `cluster_id = idorighh`, income routing (singles
> `ils_dispy_real`; couples `ils_dispy_male`/`ils_dispy_female`; couples
> consumption path does not read `ils_dispy_real`), and the year
> indicators.
>
> Run validation V1–V9 (none invoke the solver): couples region columns
> now valid binary non-all-zero; `reg_nuts1_k == 1` iff `drgn1 == k` and
> all zero iff `drgn1 == 1`; singles unchanged (or documented);
> conservation of rows/HH-years/clusters; cluster key and income routing
> preserved; year indicators preserved; loader accepts the regenerated
> stem with strict validation; precompute now takes the direct region
> path and yields non-zero `data.reg2`–`data.reg8` on the real data AND
> falls back/errors on a synthetic all-NaN couples input; smoke-test
> interface intact.
>
> Then rerun the read-only region-dummy non-identification diagnostic on
> the regenerated stem and save it as
> `Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md`,
> confirming the region dummies are now populated and wired into the
> couples market-opportunity index, the design block stays full-rank /
> well-conditioned, and the cause-B defect is resolved — while noting
> explicitly that statistical significance of the region dummies is a
> separate question requiring re-estimation, which is NOT authorized.
> Rerun preflight only if the column set or metadata changed; otherwise a
> targeted load/precompute confirmation suffices.
>
> HALT conditions: `drgn1` not usable; region partition inconsistent
> with `drgn1`; conservation broken; cluster key or income routing
> corrupted; precompute still zeros the region block after R1+R2; new
> collinearity introduced by the fix; any solver/re-estimation/no-region/
> welfare/SA2/canonical/M1-clean/spec action attempted.
>
> Save the repair report as
> `Results/JMP_pooled_P3a_region_dummy_repair_report_v1.md`, recording
> the repair verdict and per-repair status; files modified and
> regenerated; the R1 derivation rule and resulting region support; the
> R2 guard logic with the fallback/error behaviour; validation results
> V1–V9; a pointer to the diagnostic v2 and its post-repair
> classification; whether a preflight rerun was needed and its result;
> any halt and diagnosis; a "what was not executed" section; and the
> required final statements. Write all outputs to versioned/documented
> paths. Do NOT run the solver. Do NOT re-estimate. Do NOT compute
> welfare. Do NOT issue SA2. Do NOT promote canonically.

Output to save: the repair report at
`Results/JMP_pooled_P3a_region_dummy_repair_report_v1.md`, the diagnostic
rerun at
`Results/JMP_pooled_P3a_region_dummy_nonident_diagnostic_v2.md`, the
regenerated couples split (and any documented singles/metadata
regeneration), and the modified build script and `estimation_utils.py`.

What to do next: return the repair report and the diagnostic v2 to the
project chat. If the diagnostic v2 confirms the region dummies are now
wired and identifiable on the corrected data, the next gate is a
re-estimation authorization for the corrected pooled P3a (a separate
memo) — NOT issued here. Only after a corrected re-estimation and a fresh
strict post-estimation review can the SA2 question (including, if the
region block then proves genuinely redundant on correct data, the
no-region design option) be revisited. Welfare, SA2, canonical
promotion, and M1-clean displacement remain gated.

---

**Required final statements**

- **The narrow region-dummy repair is authorized:** R1 (populate the
  couples `reg_nuts1_2`–`reg_nuts1_8` from `drgn1` in the data build when
  the existing columns are absent or all-NaN) and R2 (harden
  `precompute_data_couples` to require non-missing, non-degenerate region
  values before the direct path, else the `drgn1` fallback, else an
  explicit error), followed by regeneration, validation V1–V9, and a
  rerun of the read-only region-dummy diagnostic.

- **The pooled no-region design route is NOT authorized** at this stage:
  the cause is a data-build defect (B), not proven structural redundancy,
  so the region dimension must be repaired and given a fair chance to
  identify before any decision to drop it.

- **The solver is NOT run and no re-estimation is authorized** by this
  memo. Re-estimation against the corrected data is a separate, later
  gate.

- **Welfare computation is NOT authorized**, and **no SA2 verdict is
  issued**; no output is promoted to canonical status.

- **M1-clean 2016 remains the active JMP baseline**, displaced only by a
  future SA2 verdict explicitly promoting an identified pooled
  specification.
