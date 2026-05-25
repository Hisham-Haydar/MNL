# RURO occupation-opportunity M0a-clean — Implementation Report v1

Date: 2026-05-13

Implements the `ruro_occ_M0a_clean` specification described in section 8(e)
of `Results/RURO_occ_M0a_simplification_plan_v1.md`: replace the
equality-constraint pool used in `ruro_occ_M0a` (`theta_c_sm − theta_c_sf =
0` as a hard `param_diff`) with a true renamed shared parameter
`theta_c_singles`. The likelihood landscape is identical, but the
parameter vector is shorter by one (47 vs 48) and the unconstrained
Hessian no longer carries a rank-deficient direction along the equality
constraint — the post-estimation correlation panel will stop reporting
`|corr| > 1` in the `(beta_c_*, theta_c_*)` block.

All four validation gates A–D pass (see §6 below). No estimation was run.

## 1. Files changed

| File | Change |
| --- | --- |
| `scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml` | **NEW**. M0a-clean YAML; differs from `estimation_spec_ruro_occ_M0a.yaml` by 5 entries (see §3). |
| `scripts/enhanced/estimation_spec_parser.py` | **MODIFIED**. Narrow patch: new field on `EstimationSpec`, new YAML key, new helper method, suppression of per-singles `theta_c_*` emission when the shared name is set, single shared emission in its place. |
| `scripts/enhanced/estimation_engine.py` | **MODIFIED**. Two singles-side call sites in `_compute_utility_singles` and `_compute_utility_derivatives_singles` now consult `spec.theta_c_param_name(group)` instead of building the suffixed name directly. |
| `scripts/enhanced/gamspy_estimation_vectorized.py` | **MODIFIED**. Two sites (singles utility, couples-household utility) route through the same helper for symmetry. |
| `scripts/enhanced/gamspy_estimation.py` | **MODIFIED**. Five sites (singles utility + couples utility + per-group gradient sites) route through the same helper. The literal `'theta_c'` string is replaced by the helper-resolved base name. |
| `Results/_M0a_clean_spec_check.py` | **NEW**. Re-runnable validation harness; gates A–D. |
| `docs/France_case/P3a/execution_logs/single_year_baseline/M0a-clean/RURO_occ_M0a_clean_implementation_report_v1.md` | **NEW**. This report. |

No other files were touched. MNL data, draw scripts, EUROMOD scripts,
post-estimation script, and the job-choice branch are all unchanged.

## 2. Why Route A (renamed shared parameter)

Route A — `theta_c_singles` as a distinct, neutrally-named parameter — was
implemented as required. Three reasons made it the right choice over the
abandoned Route B fallback (reuse `theta_c_sm` and drop `theta_c_sf`):

1. **Semantic clarity**: the new name documents the intent. Future readers
   see `theta_c_singles` and immediately understand that it is shared
   between sm and sf. Reusing `theta_c_sm` for both groups would be
   misleading and risk hidden engine assumptions (e.g. someone later
   reading code that "uses theta_c_sm" would not realise it is also the sf
   curvature).
2. **Backward compatibility**: the parser change is gated on the presence
   of `utility.consumption.singles_box_cox_exponent`. Old specs without
   this key produce exactly the legacy `theta_c_sm`/`theta_c_sf` split, as
   verified by Gate B on `estimation_spec_ruro_occ_M0.yaml` (still 52
   parameters with both gendered theta_c names).
3. **Engine surface**: only the singles call sites need to consult a
   helper. The couples paths route through the same helper for symmetry
   but the helper returns the legacy `theta_c` for them — no behaviour
   change.

## 3. Exact YAML changes vs the equality-constraint M0a

Five differences relative to `scripts/enhanced/estimation_spec_ruro_occ_M0a.yaml`:

| Section | Change |
| --- | --- |
| `specification.name` | `ruro_occ_M0a` → `ruro_occ_M0a_clean`; description rewritten. |
| `utility.consumption` | Added `singles_box_cox_exponent: "theta_c_singles"`. Existing `box_cox_exponent: "theta_c"` (couples) is unchanged. |
| `optimization.expression_constraints.constraints` | **Removed** the `theta_c_singles_pool` `param_diff` entry. The two `mul_cou_*_positive` constraints are preserved verbatim. |
| `initial_values` | Removed `theta_c_sm: -1.0` and `theta_c_sf: -1.0`. Added `theta_c_singles: -1.0`. |
| `optimization.bounds` | Removed `theta_c_sm: [-8.0, 0.95]` and `theta_c_sf: [-8.0, 0.95]`. Added `theta_c_singles: [-8.0, 0.95]`. |

All hours / wage / market / occupation opportunity blocks; the four
`beta_l_educH_*` removals from M0a; the prior / proposal correction
machinery; and the two `mul_cou_*_positive` constraints are byte-identical
to the equality-constraint M0a YAML.

Couples consumption: `theta_c` (shared `cm`/`cf`) is **unchanged**. The
singles pool does **not** extend to couples — that would be a different
identification claim and is not part of the M0a-clean repair.

## 4. Parser changes

All edits in `scripts/enhanced/estimation_spec_parser.py`:

| Location | Change |
| --- | --- |
| `EstimationSpec` dataclass (around L91–95) | Added field `utility_consumption_theta_singles_shared: Optional[str] = None`. Default `None` preserves legacy behaviour. |
| `EstimationSpec` methods (immediately after `is_ac2013`, L168+) | Added method `theta_c_param_name(group)`. Returns `utility_consumption_theta_singles_shared` for singles groups when set; the legacy gender-suffixed name for singles groups otherwise; the bare `utility_consumption_theta` (e.g. `theta_c`) for couples groups. Recognises group aliases (`sm`, `sf`, `m`, `f`, `singles_male`, `singles_female`, `couples_household`, `couples`, `couples_male`, `couples_female`). |
| `parse_specification` consumption-config parsing (L409–434) | Reads `consumption_config.get("singles_box_cox_exponent")`. Rejects with a clear `ValueError` if the user enables both `singles_box_cox_exponent` and `pool_across_groups` (mutually exclusive — the latter would already fold singles and couples). Logs an info line when active. |
| `parse_specification` call to `_build_parameter_list` (L704 area) | Passes `singles_shared_consumption_theta=utility_consumption_theta_singles_shared`. |
| `parse_specification` `EstimationSpec(...)` constructor (L788 area) | Passes `utility_consumption_theta_singles_shared=utility_consumption_theta_singles_shared`. |
| `_build_parameter_list` signature (L1208 area) | Added kwarg `singles_shared_consumption_theta: Optional[str] = None`. |
| `_build_parameter_list` singles-male block (L1199 area) | Per-singles `theta_c_sm` emission is now suppressed when `singles_shared_consumption_theta` is set. |
| `_build_parameter_list` singles-female block (L1220 area) | Same suppression for `theta_c_sf`. |
| `_build_parameter_list` after both singles blocks (new lines after the singles-female append) | Emits the single shared name once when set, gated on `box_cox` utility form and `not pool_consumption`. |

Mutual exclusivity is enforced at parse time: `singles_box_cox_exponent`
and `pool_across_groups` cannot both be set.

## 5. Engine changes

The five engine call sites that previously built `theta_c_{sm,sf}` (or
hard-coded `'theta_c'`) now route through `spec.theta_c_param_name(group)`.
The helper returns the right name in every case; the surrounding code is
otherwise unchanged.

| File | Function / context | Lines (approximate) | Edit |
| --- | --- | --- | --- |
| `estimation_engine.py` | `_compute_utility_singles` | 459–466 | Resolve `theta_c_name` via `spec.theta_c_param_name(singles_group)` instead of suffix construction; add `singles_group = "singles_male" if data.is_male else "singles_female"`. |
| `estimation_engine.py` | `_compute_utility_derivatives_singles` | 882–888 | Same change; `theta_c_name` is reused at the derivative site L962. |
| `gamspy_estimation_vectorized.py` | `_build_utility_singles_vectorized` (singles utility) | 381–384 | Resolve `theta_c_base` via `spec.theta_c_param_name(group)`, then pass to existing `get_param_name`. |
| `gamspy_estimation_vectorized.py` | `_build_utility_couples_vectorized` (household utility) | 714–720 | Symmetric: helper returns the legacy `theta_c` for `couples_household`. No behaviour change. |
| `gamspy_estimation.py` | Couples-household utility (L905–916), singles-male utility (L605 area), singles-female utility (L1795 area), couples derivative (L1985 area), and singles derivative sites | five sites | Each `get_param_name('theta_c', <group>, …)` becomes `get_param_name(spec.theta_c_param_name(<group>) or 'theta_c', <group>, …)`. The legacy literal `'theta_c'` survives only as the `or` fallback for safety. |

Couples-side call sites in `estimation_engine.py` (`_compute_utility_couples`
L1343–1354, `_compute_utility_derivatives_couples` L1774–1783 and L1982–1984)
use `params[spec.utility_consumption_theta]` **directly without a suffix** —
they were already correct for couples and need no change.

## 6. Validation gate results

All gates pass. Full output from
`U:/Desktop/Nizam_Hisham/MNL/.venv/Scripts/python.exe Results/_M0a_clean_spec_check.py`:

### Gate A — M0a-clean parse

```text
n_estimated_params = 47
educH residuals: []
  PASS: spec.name == 'ruro_occ_M0a_clean'
  PASS: len(spec.all_param_names) == 47
  PASS: 'theta_c_singles' in spec.all_param_names
  PASS: 'theta_c_sm' NOT in spec.all_param_names
  PASS: 'theta_c_sf' NOT in spec.all_param_names
  PASS: no beta_l_educH_* in spec.all_param_names
  PASS: no param_diff constraint links theta_c_* to theta_c_*
  PASS: mul_cou_m_positive and mul_cou_f_positive constraints present
  PASS: spec.utility_consumption_theta_singles_shared == 'theta_c_singles'
```

### Gate B — M0 backward compatibility

```text
n_estimated_params = 52
  PASS: spec.name == 'ruro_occ_M0'
  PASS: len(spec.all_param_names) == 52
  PASS: 'theta_c_sm' in M0 params
  PASS: 'theta_c_sf' in M0 params
  PASS: 'theta_c_singles' NOT in M0 params
  PASS: M0 singles_box_cox_exponent is None
  PASS: M0 hours_opportunity coefs unchanged
  PASS: M0 wage_opportunity mean_shifter coefs unchanged
```

### Gate C — engine resolver routing

```text
  PASS: M0a-clean: theta_c_param_name('singles_male') == 'theta_c_singles'
  PASS: M0a-clean: theta_c_param_name('singles_female') == 'theta_c_singles'
  PASS: M0a-clean: theta_c_param_name('sm') == 'theta_c_singles'
  PASS: M0a-clean: theta_c_param_name('sf') == 'theta_c_singles'
  PASS: M0a-clean: theta_c_param_name('couples_household') == 'theta_c'
  PASS: M0a-clean: theta_c_param_name('couples_male') == 'theta_c'
  PASS: M0a-clean: theta_c_param_name('couples_female') == 'theta_c'
  PASS: M0a-clean: 'theta_c_sf' resolves to nothing the engine would request
  PASS: M0 legacy: theta_c_param_name('singles_male') == 'theta_c_sm'
  PASS: M0 legacy: theta_c_param_name('singles_female') == 'theta_c_sf'
  PASS: M0 legacy: theta_c_param_name('couples_household') == 'theta_c'
```

Note carried in the gate output: invoking the engine forward pass requires
a GAMSPy container or a `PrecomputedData*` object; that is outside the
read-only check. With the parameter vector correct (Gate A) and the
resolver behaviour correct (Gate C), the engine code paths will request
the right names.

### Gate D — `py_compile` on touched files

```text
  PASS: py_compile scripts\enhanced\estimation_spec_parser.py
  PASS: py_compile scripts\enhanced\estimation_engine.py
  PASS: py_compile scripts\enhanced\gamspy_estimation_vectorized.py
  PASS: py_compile scripts\enhanced\gamspy_estimation.py
  PASS: py_compile Results\_M0a_clean_spec_check.py
```

Overall verdict: **PASS**.

## 7. Note on the previous M0a (equality-constraint) run

The completed estimation run under
`outputs/estimates/fr/spec/ruro_occ/gamspy/estimation_spec_ruro_occ_M0a/run_*/`
(the version using `param_diff theta_c_sm − theta_c_sf = 0`) is **preserved
as provenance** and should NOT be cited as the M0a baseline. Its 10
reported parameter correlations with `|corr| > 1` in the `(beta_c_*,
theta_c_*)` block are a constraint-handling artefact: the optimizer
respected the equality but the post-estimation script computed the Hessian
of the unconstrained 48-dimensional problem (which is by construction
rank-deficient along the equality direction). M0a-clean removes the
rank-deficient direction by construction; the post-estimation correlation
panel will be PSD and interpretable.

## 8. User commands for the next estimation

Pre-flight (optional, < 1 minute): re-run the validation suite to confirm
no drift.

```powershell
$PY = "U:/Desktop/Nizam_Hisham/MNL/.venv/Scripts/python.exe"
& $PY Results/_M0a_clean_spec_check.py
& $PY Results/_validation_ruro_occ_M0.py
```

Estimation:

```powershell
& $PY scripts/enhanced/enh_RURO_estimate_FR.py `
  --mnl-base "\\aff300msh.cifs.myliser.lu\ComputeShare\Hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/ruro_occ/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml" `
  --auto-timestamp `
  --verbose
```

Per the M0a plan, three starts are required (defaults, defaults + small
Gaussian perturbation, random within bounds) to clear the multistart proxy
for Gate B5. Use `--warm-start none` (the default) and a different
`--rng-seed` for each invocation.

Post-estimation:

```powershell
& $PY scripts/enhanced/RURO_post_estimation_styled.py `
  --results-json "<LATEST_M0a_clean_RUN>/estimation_results.json" `
  --mnl-base "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/post_estimation/fr/spec/ruro_occ/gamspy" `
  --prefix "fr_2016_ruro_occ_gamspy_M0a_clean_" `
  --spec-config "scripts/enhanced/estimation_spec_ruro_occ_M0a_clean.yaml" `
  --auto-timestamp `
  --compute-se
```

## 9. Risks before re-estimation

1. **AC2013 path is untouched.** The shared-singles logic is bypassed when
   `model_version == "AC2013"` because that branch reads parameter names
   directly from the YAML `initial_values`. M0a-clean is a `regular`
   `model_family`, so this risk does not bite for the active spec, but
   anyone porting the change to an AC2013 spec would need a separate edit.
   Audited and left intentionally.
2. **`gamspy_estimation.py` literal `'theta_c'` strings.** Five sites
   previously hard-coded the literal as the base name passed to
   `get_param_name`. They now resolve via the helper, but if a future
   spec sets `utility.consumption.box_cox_exponent` to something other
   than `theta_c`, the `or 'theta_c'` fallback I added would mis-route in
   the edge case where `spec.utility_consumption_theta` is `None`. That
   case means "log utility" and the code path is already gated by
   `if spec.utility_consumption_theta:` above the resolver call, so the
   fallback is unreachable; documented here so a future refactor that
   removes the outer `if` does not introduce a regression.
3. **EstimationSpec accessors used by the post-estimation script.** The
   post-estimation script generates a parameter table from the spec.
   The new `theta_c_singles` is in `spec.all_param_names`, so it appears
   in the table; the classifier (`_classify_param_via_blocks`) maps it to
   `preference` via name match (`theta_c` substring). The existing
   "Top-N initial-vs-final movers" computation will work normally.
4. **`expression_constraints` consistency.** The two retained
   `mul_cou_*_positive` constraints reference `consumption` and
   `leisure_{male,female}` evaluations at fixed points; they do not depend
   on the singles-shared theta and are evaluated at couples-household
   parameters only. Unaffected.
5. **Other audited but unchanged hits.** `grep -n "theta_c"` across the
   four touched engine files surfaced only the call sites covered above.
   The post-estimation script (`RURO_post_estimation_styled.py`) reads
   `theta_c` indirectly via the parameter dictionary and treats it as a
   generic preference parameter — no code-path edits needed there.
6. **No estimation was run.** Per instructions. The user runs estimation
   from the commands in §8.
