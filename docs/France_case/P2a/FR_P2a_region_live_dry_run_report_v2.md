# FR P2a Region-Live — Phase 1–2 Dry-Run Report — v2

Date: 2026-07-24. Executor: production runner `scripts/p2a/run_p2a_regionlive_rebuild.py`
(**unchanged code, unchanged thresholds** — no patch was applied for this run). Governed by
`FR_P2a_region_live_manager_decisions_v2.md` (canonical),
`FR_P2a_region_live_production_rebuild_plan_v2.md`, and the notebook-integration addendum.
Supersedes `FR_P2a_region_live_dry_run_report_v1.md` (the attempt-0 G-0 STOP, preserved — §2).

No estimation, no optimizer call, no EUROMOD, no draw generation, no notebook execution or
modification, no inference, no post-estimation, no welfare. The certified spec and every theta
file are untouched. Nothing was committed.

Commands executed (from the MNL repo root):

```
python scripts/p2a/run_p2a_regionlive_rebuild.py
  --config scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
  --phase 2 --out outputs/p2a_singles2016/region_live_v1 --dry-run
# EXIT CODE: 0   -> manifest status DRY_RUN_PHASES_1_2_COMPLETE (wall ~11 s)

python scripts/p2a/verify_p2a_regionlive_reload.py
  --config scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml
  --out outputs/p2a_singles2016/region_live_v1 --mode pre-estimation
  --write-json outputs/p2a_singles2016/region_live_v1/pre_estimation_reload_verification.json
# EXIT CODE: 0   (fresh process; cold-reload mode NOT invoked — Phase-7 remains manager-gated)
```

## 1. Dry-run verdict

**PASS.**

Every pre-registered Phase 1–2 gate passed with no warnings: G-0 frozen inputs, the full G-18
data-wiring battery, and G-19 objective reproduction. Headline results: the independently
reconstructed engine-ready frame `er_b` serializes **byte-identically** to the three pre-existing
region-live frames (§7), and the stored region-live theta reproduces the target objective
**exactly** — JAX negLL 19053.46553160094, absolute deviation from the full-precision target
**0.0**, NumPy/JAX agreement 3.64e-12 (§19–20), confirmed again in a fresh process (§21).

## 2. Attempt-0 preservation

The attempt-0 STOPPED evidence (2026-07-24 morning run that correctly halted at G-0) was copied,
unmodified, to `outputs/p2a_singles2016/region_live_v1/audit_attempt_0_g0_stop/`:
`data_wiring_validation.json` (9,442 B), `provenance.json` (2,589 B), `rebuild_manifest.json`
(2,108 B — `status: STOPPED, stop: {code: S-1, gate: G-0}`). The `inputs/` directory was not
moved or modified.

## 3. Files created

Written by this run, all inside `region_live_v1/` (plus this report):

| File | Content |
|---|---|
| `audit_attempt_0_g0_stop/` (3 files) | preserved attempt-0 STOPPED evidence |
| `region_map_p2a_singles2016.parquet` (28,875 B) | Phase-1 idhh → {drgn1, drgur, drgmd, drgru, gsur} source mapping (+ idorighh, educ3, sex) |
| `data_wiring_validation.json` (13,455 B) | full G-0 + G-18 evidence, every block `ok: true` |
| `fr_p2a_singles2016_regionlive__singles.parquet` (23,114,466 B) | **frozen canonical stem (er_b)** |
| `fr_p2a_singles2016_regionlive__mnlmeta.json` (534 B) | stem metadata (scales, cluster key, prior convention) |
| `dry_run_report.json` (8,706 B) | Phase-2 binding/liveness/cluster/objective evidence, `ok: true` |
| `pre_estimation_reload_verification.json` (913 B) | fresh-process reload evidence, `ok: true` |
| `provenance.json`, `rebuild_manifest.json` | updated provenance + `DRY_RUN_PHASES_1_2_COMPLETE` manifest |
| `docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v2.md` | this report |

No file outside `region_live_v1/` (and this report) was written; no code or config was modified.

## 4. Authoritative inputs

All hash-verified against the config registry (G-0, PASS): raw `FR_2016_a3.txt`
(`da3eed57…`), gsur lookup `FR_gsur_ruro_v2_stageA_y2015.parquet` (`f51ad630…`), certified spec
YAML (`492bcfa9…`, **unchanged**), certified warm-start theta (`c72e92b1…`), stored region-live
thetas v1 (`930ef3aa…`) / v2 (`9c8d7ee7…`), the three comparison frames and adapter mnlmeta.

## 5. Frozen geometry contract

**PASS (pre-run check + G-0, independently).**
`inputs/fr_p2a_draws_geometry__singles.parquet` (8,316,412 B): SHA-256
**`5bcf0e5409ef74c57f6de24efdfd24d0075132dc3138ddb57a22740b916cf235`** — exactly the mandated
value; the meta json declares the same hash. Contract: 157,055 rows; 1,555 households; exactly
101 alternatives per household (min = max = 101); seed 2026; all 33 required columns present;
full 162-column freeze (`n_columns: 162` — the complete in-memory `draws_p2a` set);
`status: frozen_production_input`, `produced_by: notebooks/fr_singles_pipeline_v2.ipynb`;
draw-0 chosen contract (one per household, `is_chosen==1`, `log_prior==0`) verified.

## 6. Frozen priced-draw inputs

**PASS.** All 8 pricing-cache chunks `fr_singles_pricing_p2a/priced_{00000..01400}.parquet`
hash-match the registry; concatenated contract: 225,836 rows, 1,555 unique `source_idhh`, exact
10-column set. Read-only; no EUROMOD call occurred.

## 7. Existing-frame reconciliation

**PASS — strongest possible form.** The three pre-existing region-live frames are byte-identical
to each other (all `8bf083ce…`), and the **independently reconstructed** `er_b` — rebuilt from
frozen priced draws + frozen geometry + raw-source revival, never reading any engine-ready frame —
matched them on **all 194 common columns with zero differing columns** (max abs diff 0 under the
1e-9 gate; no column present in one side only; 157,055 rows). The frozen stem parquet even
**serializes to the identical byte stream** (`8bf083ce…` — §23). Five-column idempotence
(re-applying the source mapping to the reference frames reproduces them unchanged) also passed.
Normalization scales gated equal to the committed adapter meta: `c_scale 1911.108057855561`,
`l_scale 10.0`.

## 8. Household mapping validation

**PASS.** Funnel reproduced the checkpoint exactly (households: baseline 10,003 → age 5,793 →
education 5,557 → retirement 4,973 → LES 4,010 → other-members 3,887 → hours/wage 3,830;
mutations: 25 capped, 6 to-inactive, 407 non-employment hours zeroed). Singles sample: 1,555
households / 2,236 persons. Mapping: 1,555 rows, unique `idhh`, no missing values. Take-up
determinism: seed 20162016, revealed rates nw 0.548 / w 0.265 (== expected), shares 0.542/0.292.

## 9. Region support

**PASS.** `drgn1 ∈ {1..8}`, all 8 regions present, counts exactly
{1: 245, 2: 254, 3: 122, 4: 135, 5: 279, 6: 175, 7: 182, 8: 163} — at the source mapping and at
the revived engine-ready frame.

## 10. Urbanisation validation

**PASS.** `drgur + drgmd + drgru == 1` for every household, each component binary, at both the
mapping and the revived frame (loader-level one-hot re-verified in §16).

## 11. GSUR validation

**PASS.** Lookup: 48 valid rows, 100% match on `(drgn1, educ3, sex)`. Household-level `gsur` in
[0.0532, 0.2250], mean 0.09450886, 47 unique values, non-constant; within-household constancy
across all 101 alternatives; no cross-household leakage (engine rows equal the mapping row for
their `idhh` exactly).

## 12. Choice-geometry invariance

**PASS.** Geometry 157,055 = 1,555 × 101 with draw-0 chosen-first contract; assembled `er_p2a`
(157,055 × 194), exactly 1,555 chosen; draw-0 unknown-occupation mode imputation exactly **7 rows
→ loc4 = 4** (== checkpoint); band-overwrite comparison counts exactly
{pt1: 11,342, pt2: 7,391, ft: 7,541, lh: 0} (== checkpoint); bpool flags zero on all non-working
rows; final `er_b` shape 157,055 × 194.

## 13. Proposal-density invariance

**PASS.** `prior > 0` everywhere; canonical-prior identity and the Wave-0.1 composition
`log_prior = log_q_E + working·(log_q_H + log_q_W + log_q_Occ)` enforced by
`assemble_singles._validate_wave01` (rtol 0 / atol 1e-9) on the assembled frame; loader-level
`max|log(prior) − log_prior| = 0.0` for both genders. No draw path exists in the runner (S-0
guard verified at startup and at exit).

## 14. Frozen engine-ready stem

**PASS.** `fr_p2a_singles2016_regionlive__singles.parquet` + `__mnlmeta.json` frozen under
`region_live_v1/` (produced_by `scripts/p2a/run_p2a_regionlive_rebuild.py`; normalization
`c_scale 1911.108057855561`, `l_scale 10.0`, `n_chosen 1555`; cluster key
`cluster_id ← source_idorighh`; prior convention recorded). This stem — not any pre-existing
frame — is what Phase 2 loaded and every later phase will read.

## 15. Specification and pin binding

**PASS.** Certified YAML hash unchanged (`492bcfa9…`); 47 `spec.all_param_names` matching the
order of both stored theta CSVs; spec-level `fixed_params == {theta_l_m: −0.8}`; **10 run-level
pins** applied by bounds-clamping at the certified warm-start values (indices 10–17, 31–32:
couples leisure block + year dummies; e.g. `beta_l0_m` pinned at 1e-06, `beta_E_y2015` at
−0.2546064112); **37 free parameters** with explicit per-parameter bounds recorded in
`dry_run_report.json`; occupation block free. Warm-start equality: vs v2 `certified` column
**max abs 0.0**; vs v1 (rounded storage) 4.55e-07 ≤ 5e-07. Stored-theta cross-check: `trial`
v1 vs v2 **max abs 0.0**. Theta SHA-256 `5f3722dc…` — matching the theta hash recorded by the
P2a welfare run manifest, closing that provenance loop.

## 16. JAX loader liveness

**PASS (both genders).** Loader arrays nonzero and **array-equal to the frozen columns**:
region dummies (sm means reg2..reg8: 0.1807, 0.0616, 0.0812, 0.1975, 0.1218, 0.1232, 0.0952;
sf: 0.1486, 0.0927, 0.0916, 0.1641, 0.1046, 0.1118, 0.1130 — the readiness doc's "reg2 mean
0.181" is confirmed as the singles-male split), gsur (sm mean 0.0980, sf 0.0915), urbanisation
one-hot, prior strictly positive, `log_prior` consistency dev 0.0. Split: 714 sm households
(72,114 rows) + 841 sf (84,941 rows) = 1,555.

## 17. Wage and occupation route

**PASS (runtime-asserted this run).** Structural `wage_spec == "vw"`; `wage_loc_groups` absent —
**neither `loc_empirical` nor `vw_occupation` is active structurally**; occupation enters
`log_market` only as the six `loc4_{2,3,4} × {male,female}` access shifters folded into
`market_opportunity_shifters` (enumerated in `dry_run_report.json`); proposal-side occupation
conditioning is data-carried through `prior`/`log_prior` from the frozen geometry.

## 18. Proposal-correction checks

**PASS.** `prior` positive and equal to the canonical clip-exp of `log_prior` (dev 0.0 at loader
level, both genders); proposal-weighted within-choice-set centering active
(`market_opportunity_center_within_choice_set: true`, `center_weights: "proposal"`); the
validated engine applies the correction once (`V = u + log_h + log_w + log_market − log_prior`),
witnessed numerically by the 3.64e-12 cross-backend agreement (§20).

## 19. JAX objective reproduction

**PASS — exact.** JAX negLL at the stored region-live theta = **19053.46553160094**;
`|negLL − 19053.46553160094| = 0.0` (gate ≤ 1e-4); `|negLL − 19053.4655| = 3.16e-05`
(gate < 1e-2). Evaluation 0.8 s (post-jit). No optimizer was called anywhere (G-19 mandate;
`scipy.optimize` on the prohibited-module list, verified absent).

## 20. NumPy/JAX agreement

**PASS.** NumPy reference backend (`compute_index(..., backend="numpy")`) = 19053.465531600945;
`|JAX − NumPy| = 3.64e-12` (gate ≤ 1e-6). Two independent engine implementations land on the
same objective to sub-nanounit precision.

## 21. Fresh-process pre-estimation reload

**PASS.** `verify_p2a_regionlive_reload.py --mode pre-estimation` in a brand-new process:
ordering ok; JAX negLL 19053.46553160094 with `abs_dev_full = 0.0`; NumPy 19053.465531600945,
backend dev 3.64e-12; frozen-stem hashes recorded (parquet `8bf083ce…`, mnlmeta `05be4030…`);
wall 2.6 s. Written to `pre_estimation_reload_verification.json`. This is the pre-estimation
reload check only — the **Phase-7 strict cold-reload gate was not invoked** (manager-gated).

## 22. Resolved cluster count

**Resolved T3 count = 1,555** (D-6, self-ratifying: unique nonmissing `idorighh` in the frozen
stem = 1,555; mapping↔stem consistency ok; exactly one cluster id per household; within bounds
[1, 1,555]; no missing ids; pooled default 9,657 never used). Persisted in `dry_run_report.json`
and the manifest. One household per cluster in this single-wave singles sample.

## 23. Hashes and provenance

`provenance.json` records all 18 verified input hashes (incl. geometry `5bcf0e54…`) and the
output hashes: `region_map_p2a_singles2016.parquet` and — notably — the frozen stem
`fr_p2a_singles2016_regionlive__singles.parquet` = **`8bf083ce3be17f8c74af894bc3748718cbb0a991
eb9a411db7188e806d1e9f0d`**, byte-identical to all three pre-existing region-live frames: the
reconstruction is exact to the serialized byte. Manifest self-hashes: config `68d152e7…`, runner
script `be11294b…` (identical to the attempt-0 values — **no code or threshold was changed
between the STOPPED attempt and this PASS**). Git heads at run time: MNL `928d11b` (dirty:
run outputs + pending addendum/prompt edits), monorepo `27756a0` (clean). Environment: Python
3.12.2, jax 0.10.1, numpy 2.3.5, pandas 2.3.3, Windows Server 2022.

## 24. Stop-condition status

No stop condition triggered. S-0 prohibited-operation guards verified at startup and exit (no
EUROMOD, no draw modules, no `scipy.optimize` loaded; all writes inside `region_live_v1/`);
S-1/G-0 passed; G-18 passed in full; S-8 no mid-run hash change; S-9/G-19 passed. Manifest:
`DRY_RUN_PHASES_1_2_COMPLETE` — the dry-run stops after Phase 2 **by design** (plan v2 §24
step 4).

## 25. Git diff summary

MNL `git status --short` (nothing committed):

```
 M Prompts/Phase_1_2_only.md                     (operator's prompt file — not touched by this run)
 M dclaborsupply-monorepo                        (gitlink: monorepo at 27756a0, clean)
 M docs/.../FR_P2a_region_live_notebook_integration_addendum_v1.md   (+58/−3, prior task, pending commit)
 M outputs/.../region_live_v1/data_wiring_validation.json   (+168 — attempt-0 STOP → full PASS evidence)
 M outputs/.../region_live_v1/provenance.json               (+12 — output hashes added)
 M outputs/.../region_live_v1/rebuild_manifest.json         (+43 — STOPPED → DRY_RUN_PHASES_1_2_COMPLETE)
?? outputs/.../region_live_v1/audit_attempt_0_g0_stop/
?? outputs/.../region_live_v1/dry_run_report.json
?? outputs/.../region_live_v1/fr_p2a_singles2016_regionlive__{singles.parquet,mnlmeta.json}
?? outputs/.../region_live_v1/inputs/                       (operator's geometry freeze)
?? outputs/.../region_live_v1/pre_estimation_reload_verification.json
?? outputs/.../region_live_v1/region_map_p2a_singles2016.parquet
?? docs/France_case/P2a/FR_P2a_region_live_dry_run_report_v2.md   (this report)
```

`dclaborsupply-monorepo`: clean (both notebooks untouched by this run). No script, config,
spec, or theta file modified — `git diff` on `scripts/` and `scripts/bpool/specs/` is empty.

## 26. Whether Phase 3 may run

**Technically unblocked; procedurally manager-gated — so: not yet.** Every Phase-3 precondition
this dry-run can establish is now established (frozen stem, exact objective reproduction on both
backends, verified binding, resolved cluster count, S-0 guards). Per plan v2 §24 step 4 and
decisions v2, Phases 3–8 run **only after the manager reviews this dry-run evidence**, and the
runner itself refuses `--phase > 2`. No estimation was or will be started without that review.

## 27. Immediate next action

Submit this report plus the evidence bundle (`data_wiring_validation.json`,
`dry_run_report.json`, `pre_estimation_reload_verification.json`, `rebuild_manifest.json`,
attempt-0 folder) to the manager for the Phase-3 authorization decision. On approval, the next
execution is Phase 3 (estimation, §11 of plan v2) through the same runner with the ratified
G-1/G-2/G-3/G-15/G-16 gates, followed by the Phase 4–8 battery — each phase manager-gated as
planned. A commit of the Phase 1–2 artifact set (§3 list + the addendum amendment) is ready to
be made whenever the operator approves; nothing has been committed by this run.

**FINAL VERDICT: PASS** (all Phase 1–2 gates green; no warnings; no code, threshold, spec, or
theta modified; nothing committed).
