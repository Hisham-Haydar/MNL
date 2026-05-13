# RURO occupation-opportunity M0a — Implementation Report v1

Date: 2026-05-13

Implements the identification-repair specification described in
`Results/RURO_occ_M0a_simplification_plan_v1.md` exactly as written, with
one explicit deviation noted in §3 (the fallback equality-constraint route
for the pooled singles curvature). No estimation was run.

## 1. Files changed

| File | Change |
| --- | --- |
| `scripts/enhanced/estimation_spec_ruro_occ_M0a.yaml` | **NEW**. The M0a specification; created by copying `estimation_spec_ruro_occ_M0.yaml` and applying the changes in §2 below. |
| `docs/RURO_occ_M0a_implementation_report_v1.md` | **NEW**. This report. |

No other files were modified. The parser, estimation engine, post-estimation
pipeline, MNL data, draw scripts, EUROMOD scripts, and the job-choice branch
are all untouched.

## 2. Exact YAML changes (M0 → M0a)

All changes are confined to `estimation_spec_ruro_occ_M0a.yaml`.

### 2.1 `specification:` block

```yaml
specification:
  name: "ruro_occ_M0a"                     # was "ruro_occ_M0"
  description: "M0a identification repair: theta_c pooled across singles via hard equality; beta_l_educH removed from utility leisure"
  wage_spec: "vw"                          # unchanged
  model_family: "regular"                  # unchanged
```

### 2.2 `utility.leisure.shifters:` — remove the `educH` entry

The four-shifter list becomes three:

```yaml
shifters:
  - variable: "age_norm"
    coefficient: "beta_l_age"
  - variable: "age_norm2"
    coefficient: "beta_l_age2"
  - variable: "n_children"
    coefficient: "beta_l_nkids"
    gender_specific: true
  # REMOVED at M0a: educH shifter
```

This drops four estimated parameters that the parser had been generating
from this entry (`beta_l_educH_sm`, `beta_l_educH_sf`, `beta_l_educH_m`,
`beta_l_educH_f`).

### 2.3 `initial_values:` — drop the four removed parameters

```yaml
# Lines removed (M0 → M0a):
#   beta_l_educH_sm: 0.0
#   beta_l_educH_sf: 0.0
#   beta_l_educH_m:  0.0
#   beta_l_educH_f:  0.0
```

`theta_c_sm` and `theta_c_sf` are KEPT in `initial_values:` (both at `-1.0`).
A comment notes that `theta_c_sf` is pinned to `theta_c_sm` by the hard
equality constraint added in §2.5.

### 2.4 `optimization.bounds:` — drop the four removed parameters

```yaml
# Lines removed (M0 → M0a):
#   beta_l_educH_sm: [-8.0, 5.0]
#   beta_l_educH_sf: [-8.0, 5.0]
#   beta_l_educH_m:  [-8.0, 5.0]
#   beta_l_educH_f:  [-8.0, 5.0]
```

`theta_c_sm` and `theta_c_sf` bounds (`[-8.0, 0.95]`) are KEPT.

### 2.5 `optimization.expression_constraints.constraints:` — add the hard pool

```yaml
- name: theta_c_singles_pool
  expression: param_diff
  group: global
  lhs_param: theta_c_sm
  rhs_param: theta_c_sf
  lower: 0.0
  upper: 0.0
  mode: hard
```

This encodes `theta_c_sm − theta_c_sf = 0` as a hard equality. The two
pre-existing soft `mul_cou_*_positive` constraints are preserved verbatim.

### 2.6 Everything else: byte-identical to M0

The following blocks were copied unmodified:

- `utility.consumption` (Box-Cox over `beta_c`, `theta_c` with bounds
  `[-8.0, 0.95]`)
- `utility.leisure.intercept` / `box_cox_exponent` / `box_cox_bounds`
- `hours_opportunity` (`beta_E`, `beta_h_pt1`, `beta_h_pt2`, `beta_h_ft`)
- `wage_opportunity` (full Mincer mean, `sigma`)
- `market_opportunity` (`beta_E_gsur`, `beta_E_educH`)
- `occupation_opportunity` (all 12 `beta_occ_{2,3,4}_{sm,sf,cm,cf}` shifters,
  reference category `loc4 = 1`)
- `couples: {}` (no `beta_cl`/`beta_ll` interactions)
- `optimization.method` (`L-BFGS-B`), `analytical_gradient`, `max_iterations`,
  `tolerance`, `gradient_tolerance`, `disp`, `iprint`
- All retained bounds (Box-Cox `theta`s for every group, all `beta_c`/`beta_l0`
  scales, retained leisure shifters, all opportunity bounds)
- `gradient_verification: {enabled: false}`

## 3. Was parser support changed?

**No.** The parser (`scripts/enhanced/estimation_spec_parser.py`) was not
modified.

The plan permits two routes for pooling `theta_c` across singles:

1. **Shared-parameter route** — rename `theta_c_sm`/`theta_c_sf` to a single
   `theta_c_singles` and teach both the parser and the estimation engine to
   use one parameter for both `sm` and `sf` likelihood blocks.
2. **Hard equality-constraint fallback** — keep both `theta_c_sm` and
   `theta_c_sf` as separate parameter names in the parameter vector and add
   a hard `lhs - rhs = 0` constraint linking them.

Route 1 requires coordinated edits to:

- `_build_parameter_list` in the parser (currently constructs
  `theta_c_sm`/`theta_c_sf` unconditionally for the singles groups
  when `pool_consumption == False`).
- The estimation engine, which reads `theta_c_sm` and `theta_c_sf`
  directly via `params.get('theta_c_sm', ...)` / `params.get('theta_c_sf', ...)`
  during the per-group Box-Cox transform. Every such call site would need
  to be redirected to a new `theta_c_singles` source when the shared-singles
  flag is set, in both `gamspy_estimation_vectorized.py` and
  `estimation_engine.py`.

Route 2 is supported out of the box: the parser already accepts
`expression: param_diff` with `lhs_param`/`rhs_param`/`lower`/`upper`/`mode`
(see `_parse_expression_constraints`, parser line ≈ 741). No code beyond
the YAML needs to change.

Per the plan ("If parser modification is too large a scope at this step,
an equivalent alternative is to keep two names `θ_c_sm` and `θ_c_sf` but
link them via an equality constraint"), **Route 2 was chosen**. The plan
explicitly notes that the hard equality constraint yields exactly the same
likelihood landscape as the renamed-shared-parameter approach.

## 4. Shared parameter or equality constraint?

**Equality constraint (hard, `lower = upper = 0`).** Specifically:

```yaml
- name: theta_c_singles_pool
  expression: param_diff
  group: global
  lhs_param: theta_c_sm
  rhs_param: theta_c_sf
  lower: 0.0
  upper: 0.0
  mode: hard
```

The parser confirms this is parsed correctly (verified by
`parse_specification` returning an `expression_constraints` entry with
`mode='hard'`, `lhs_param='theta_c_sm'`, `rhs_param='theta_c_sf'`,
`lower=0.0`, `upper=0.0`).

## 5. Final parameter count

| Count | Description |
| --- | --- |
| **48** | Reported parameters (`len(spec.all_param_names)`) |
| **47** | Effective degrees of freedom after the hard equality constraint |
| 52 → 48 | Net of removing 4 `beta_l_educH_*` parameters (the equality constraint does not remove a name from the vector; it pins one) |
| 48 → 47 | Effective: the hard equality reduces the free DoF by one |

Verified by `parse_specification`:

```text
spec.name             = ruro_occ_M0a
spec.wage_spec        = vw
spec.model_family     = regular
n_estimated_params    = 48
beta_l_educH_* absent : True
theta_c_sm in params  : True
theta_c_sf in params  : True
theta_c in params (cou): True
Expression constraints: theta_c_singles_pool | param_diff | hard | theta_c_sm - theta_c_sf | lower=0.0 upper=0.0
```

If the shared-parameter route is taken in a future revision (after the
required parser + engine edits), the reported count would drop to 47 and
the equality constraint can be removed. The current spec is operationally
equivalent.

## 6. What was deliberately left unchanged

Per §10 of `RURO_occ_M0a_simplification_plan_v1.md` and the user's
instruction:

- `hours_opportunity` block (all 4 shifters: `working`, `working_pt1`,
  `working_pt2`, `working_ft`).
- `wage_opportunity` block (all 5 Mincer mean shifters + `sigma`).
- `market_opportunity` block (`beta_E_gsur`, `beta_E_educH`,
  centring, scaling).
- `occupation_opportunity` block (all 12 `beta_occ_*` shifters,
  reference `loc4 = 1`, `applies_to` routing to `sm/sf/cm/cf`).
- Prior / proposal-density correction machinery (no YAML touches; the
  correction lives in the engine and is unchanged).
- MNL parquet files
  (`Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__{singles,couples}.parquet`)
  and the `__mnlmeta.json` sidecar.
- `enh_RURO_draws.py` (no rebuild needed; M0a is a spec-side change only).
- `enh_RURO_euromod.py` (same reason).
- `enh_RURO_prep_mnl_basic.py` (same reason).
- The job-choice branch under `scripts/Job_model/` (untouched as required).
- Couples consumption block — `beta_c` and `theta_c` remain shared `cm/cf`,
  not pooled with singles `theta_c_singles`.
- All starting values for retained parameters are identical to M0.

## 7. How to run the model

Pre-estimation sanity check (recommended, takes < 1 min): re-run the
existing data validation script to confirm the rebuilt MNL files are still
intact.

```powershell
$PY = "U:/Desktop/Nizam_Hisham/MNL/.venv/Scripts/python.exe"
& $PY Results/_validation_ruro_occ_M0.py
```

All 8 categories should PASS (no data has changed since 2026-05-13).

Estimation command:

```powershell
& $PY scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0a.yaml" `
  --warm-start none `
  --auto-timestamp `
  --verbose
```

Notes on the command:

- `--warm-start none` is **mandatory**. The M0 optimum was on the wrong
  side of an indefinite Hessian; starting from M0 θ̂ would re-enter that
  region.
- The M0a plan §9 requires three starts (defaults, defaults + small
  Gaussian perturbation, random within bounds) to confirm Gate B5. Re-run
  the command above with different `--rng-seed` or manually edited
  initial values for the second and third starts.

Post-estimation:

```powershell
& $PY scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0a/run_<TS>/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/ruro_occ/gamspy" `
  --prefix "fr_2016_ruro_occ_gamspy_M0a_" `
  --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0a.yaml" `
  --auto-timestamp `
  --compute-se
```

The low-token Markdown summary will be auto-written to
`reports/fr_2016_ruro_occ_gamspy_M0a_llm_summary_<TS>.md`.

## 8. Risks before estimation

These are the items that could cause M0a to fail Gate B even though Gate A
has already passed (spec parses correctly with 48 reported parameters,
47 effective).

1. **Hard equality enforcement at the solver level.** The parser accepts
   `mode: hard`, but the underlying solver path needs to honour it. If the
   solver treats it as a stiff soft penalty rather than a true constraint,
   the Hessian would still be 48×48 with two near-collinear rows for
   `theta_c_sm` and `theta_c_sf`, which could leave a tiny negative
   eigenvalue and fail Gate B2. Mitigation: inspect the converged Hessian
   eigenvalues and the reported `theta_c_sm − theta_c_sf` residual after
   the run; if `|residual| > 1e-6`, the constraint was not honoured and
   the shared-parameter route (parser + engine edits) is required.
2. **Participation pathology persists.** §6 of the plan explicitly notes
   that M0a does not attempt to fix predicted participation = 1.0000. If
   the M0 pattern remains, that is expected and is to be addressed by the
   parallel participation diagnostic (`V_nonwork` vs `V_work` at converged
   θ̂), not by further YAML changes.
3. **Cross-engine consistency.** Gate B6 requires the vectorized and
   non-vectorized engines to agree to `1e-6` per observation on `joint_ll`
   at the M0a converged θ̂. The M0 run did not exercise the
   non-vectorized path; if there is latent disagreement, M0a will surface
   it.
4. **Multistart agreement.** Gate B5 (proxy) requires `max-Δ` on key
   parameters under 5% across three starts. The plan calls this out as
   a precondition for graduating M0a from "diagnostic only" to baseline.
5. **`beta_c` separation may still fail.** Removing the leisure educH
   shifter and pooling `theta_c` across singles is the **minimum**
   pool consistent with the M0 identification evidence. If
   `corr(beta_c_sm, beta_c_sf)` is still > 0.95 in M0a, the contingency is
   M0b: pool `beta_c_singles = beta_c_sm = beta_c_sf`. M0a does not
   pre-emptively apply that.
6. **No rebuild was done.** This is intentional. The MNL data has not
   changed since 2026-05-13; the rebuilt parquets, drawsmeta, EUROMOD
   scenario, and validation report all still apply. If anyone has touched
   `Z:/hisham/EUROMOD-STORAGE/...` between rebuild and M0a estimation,
   re-run the validation script before estimating.
7. **Reported vs effective parameter count.** Output reports (e.g. the
   low-token Markdown summary) will say 48 parameters. The 47-DoF figure
   only matters when computing AIC/BIC correction terms; the existing
   post-estimation report uses the reported count, so AIC/BIC are by
   convention slightly conservative for M0a (one extra penalty term that
   does not buy an extra degree of freedom). This is cosmetic and does
   not affect Gate B.

The plan calls explicitly for these checks; they are restated here so the
estimation step has the full pre-flight context.
