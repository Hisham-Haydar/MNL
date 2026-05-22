# JMP NC Pilot — Stages 1–4 Build Report v1

*France RURO multi-year extension | v1 | 2026-05-22*

Document class: pilot build report. Records execution of NC pilot Stages
1–4 (pre-draw Mincer fit → pilot W1 wage draw → 30×30 product for 2016
couples → pilot parquet + metadata), under the scope amendment
`docs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md`. Hard stop before
EUROMOD. M1-clean 2016 remains active. Corrected pooled P3a track
unaffected.

---

## 1. Stage 1–4 verdict

**Stages 1–4 PASSED.** All authorized stages completed without firing
any halt condition. No production file, YAML, parquet, or row guard was
modified. The pilot couples product parquet exists at
`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet`
with 2,319,300 rows (= 2,577 couples × 900 alternatives) and its
metadata sidecar lists `n_draws_per_couple = 900`. HP2 lockstep,
HP3 chosen-row invariants, and HP9 row counts all pass. Hard stop
honoured before Stage 5 (EUROMOD).

---

## 2. Authorization scope

Authorized by `docs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md`,
which narrows `docs/JMP_NC_pilot_spec_contract_v1.md` to Stages 1–4
(pre-draw Mincer fit; pilot wage draw + proposal density;
30×30 product over 2016 couples; pilot parquet + metadata). All
spec-contract decisions carry forward unchanged: W1 baseline,
two-group comparison, `delta_occ*` calibrated, `occ_spec="fixed"`,
common sigma, `draw_male` / `draw_female` / `draw_joint`, chosen at
`draw_joint == 0`. Hard stop before EUROMOD.

Not authorized and not executed: EUROMOD, GSUR re-merge, MNL
estimation-ready stack rebuild beyond the pilot scaffold, precompute,
estimation, welfare, SA2, canonical promotion, M1-clean displacement,
any singles modification, any in-place edit to production
`enh_RURO_draws.py` / `enh_RURO_prep_mnl_basic.py` /
`prepare_pooled_estimation_ready.py` / the frozen P3a YAML.

---

## 3. Files inspected

| File | Method |
|---|---|
| `docs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md` | Full read |
| `docs/JMP_NC_pilot_spec_contract_v1.md` | Full read |
| `Results/JMP_NC_pilot_build_report_v1.md` | Full read (prior halt report) |
| `Results/JMP_nc_pilot_feasibility_audit_v1.md` | Full read (prior session) |
| `docs/JMP_next_cycle_opportunity_respecification_plan_v1.md` | Full read (prior session) |
| `Results/JMP_opportunity_block_readonly_diagnostic_v1.md` | Full read (prior session) |
| `scripts/enhanced/enh_RURO_draws.py` | Targeted Grep + ranged Read (lines 100–120, 1119–1234) |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Targeted Read (lines 880–1080) |
| `scripts/maintenance/prepare_pooled_estimation_ready.py` | Ranged Read (lines 1–80) |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` | Full read |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet` | Bounded reads (columns); full read of 2016 slice during build |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet` | Schema + row count only |
| `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__mnlmeta.json` | Full read |

---

## 4. Files created

All new files are under pilot-only paths:

| Path | Purpose |
|---|---|
| `scripts/pilot/fit_pilot_mincer.py` | Stage-1 driver: fits W1 + two-group Mincer on pooled 2015–2017 working observed wages |
| `scripts/pilot/pilot_wage_draw.py` | Stage-2 module: `draw_pilot_wages` (W1 log-normal) and `log_q_pilot_wages` (matching log-normal density) — pilot-only; production unchanged |
| `scripts/pilot/build_pilot_couples_product.py` | Stages 3–4 driver: builds the 30×30 product over 2016 couples, applies W1 wages on non-chosen alts, writes pilot parquet + metadata |
| `scripts/pilot/config/pilot_mincer_coefficients_v1.json` | Pilot Mincer coefficients (W1 + two-group, tagged with fitting set and cell counts) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet` | Pilot couples product scaffold (2,319,300 rows; W1 wages on non-chosen alts; EUROMOD-dependent income columns dropped) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__mnlmeta.json` | Pilot metadata sidecar (n_draws=900; EUROMOD/GSUR/precompute/estimation = not_run) |
| `Results/JMP_NC_pilot_stage1_4_build_report_v1.md` | This report |

`scripts/pilot/__pycache__/` was created as a side effect of running the
pilot driver; it is a transient Python cache and is not part of the
authorized output set.

---

## 5. Files modified

**None.** No file in `scripts/enhanced/`, `scripts/maintenance/`,
`Data/processed/`, or any other production path was modified by this
session. `git status --short` reports only the new untracked
`scripts/pilot/` tree (the `Results/` and `Data/pilot/` directories
either contain only this report / pilot outputs or are themselves
untracked).

Production references touched in read-only mode:

- `scripts/enhanced/enh_RURO_draws.py` — read; line references for the
  production uniform wage draw (~1196–1204) and proposal-density term
  (~1225–1234) used as quoted references in the pilot module. **Not
  modified.**
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py` — read; line references
  for the production diagonal merge (~1058–1065) used as quoted
  reference. **Not modified.**
- `scripts/maintenance/prepare_pooled_estimation_ready.py` — read; the
  hard-coded row guards (lines 70–72) **not modified**. The pilot uses
  its own driver entirely.
- `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`
  — read. **Frozen, not modified.**

---

## 6. Pilot-only path confirmation

Every write performed by this session lives under one of:

- `scripts/pilot/`
- `scripts/pilot/config/`
- `Data/pilot/nc_2016_couples/`
- `Results/JMP_NC_pilot_stage1_4_build_report_v1.md` (this report)

No write to `scripts/enhanced/`, `scripts/maintenance/`,
`scripts/enhanced/specifications/`, or `Data/processed/` was performed.
The production singles parquet `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__singles.parquet`
was read only (row count 500,700 confirmed unchanged).

---

## 7. Stage 1 W1 Mincer fit

Specification (reference `loc4 = 1`, common slopes, single common sigma):

```
log w = beta_w0 + beta_w_educL·educL + beta_w_educH·educH
      + beta_w_pexp·pexp_years + beta_w_pexp2·pexp_years2
      + delta_occ2·1[loc4=2] + delta_occ3·1[loc4=3] + delta_occ4·1[loc4=4]
      + year_2015_indicator + year_2017_indicator
      + epsilon,   epsilon ~ N(0, sigma²)
```

Fit on pooled 2015–2017 working observed (draw=0) wages, singles +
couples; `loc4 ∈ {1,2,3,4}`, `wage > 0`. n = **18,886**, k = 10,
R² = **0.2320**, `sigma = 0.3771`.

**Calibrated coefficients (W1):**

| Coefficient | Estimate | SE |
|---|---|---|
| intercept (beta_w0) | 1.9787 | 0.0257 |
| beta_w_educL | −0.0540 | 0.0098 |
| beta_w_educH | 0.2737 | 0.0086 |
| beta_w_pexp | 0.0247 | 0.0017 |
| beta_w_pexp2 | −0.000378 | 0.000040 |
| **delta_occ2** | **−0.0797** | 0.0091 |
| **delta_occ3** | **+0.0251** | 0.0106 |
| **delta_occ4** | **+0.2415** | 0.0080 |
| year_2015_indicator | −0.0254 | 0.0073 |
| year_2017_indicator | +0.0186 | 0.0073 |
| sigma (common) | 0.3771 | — |

The three `delta_occ*` quantify the W1 occupation premium relative to
loc4 = 1 (Routine-Manual). The pattern (Intel ≈ RM, NRM below RM,
NonInt well above) is consistent with the diagnostic's pooled-sample
ordering and confirms that the binding empirical separation is loc4 = 4
vs the rest.

**Status: calibrated, fixed at draw time, NOT free structural
parameters.** The pilot consumes these values at the draw stage and
does not re-estimate them at the structural stage. This is the
spec-contract §13 fallback adopted as the pilot default, removing the
double-counting risk by construction (the structural free-parameter
count stays at 55).

Full coefficient JSON: `scripts/pilot/config/pilot_mincer_coefficients_v1.json`.

---

## 8. Stage 1 two-group Mincer fit

Same baseline; replaces the three `delta_occ*` with a single
`delta_NonInt·1[loc4=4]`. Same sample (n = 18,886), k = 8, R² = 0.2277,
sigma = 0.3781.

| Coefficient | Estimate | SE |
|---|---|---|
| intercept | 1.9603 | 0.0247 |
| beta_w_educL | −0.0530 | 0.0098 |
| beta_w_educH | 0.2723 | 0.0086 |
| beta_w_pexp | 0.0246 | 0.0017 |
| beta_w_pexp2 | −0.000376 | 0.000040 |
| **delta_NonInt** | **+0.2577** | 0.0067 |
| year_2015_indicator | −0.0258 | 0.0073 |
| year_2017_indicator | +0.0183 | 0.0073 |
| sigma (common) | 0.3781 | — |

The two-group ΔR² vs W1 is −0.0043 (W1 0.2320 vs two-group 0.2277) on
two more parameters — consistent with the diagnostic's qualitative
finding that the binding wage separation is essentially "NonInt vs
rest." The two-group model is held as a documented comparison for later
Stage-9 testing; the pilot baseline draws use W1.

---

## 9. Mincer fitting set

**Set: pooled 2015–2017 with year controls, singles + couples, working
observed (draw=0) wages, `loc4 ∈ {1,2,3,4}`, `wage > 0`.**

- n_total = 18,886
- n_singles = 4,611
- n_couples_male = 7,134
- n_couples_female = 7,141

The amendment's preferred choice (pooled with year controls) was
adopted; the 2016-only fallback was not invoked. Cell counts by
(loc4, dgn, year_tag) and any thin-cell flags are persisted in the
pilot config under `fitting_set.cell_counts_loc4_dgn_year` and
`fitting_set.thin_cells_lt_50`. The pilot config sets
`thin_cell_warning = true` only if any (loc4, dgn, year_tag) cell has
n < 50; the executor should consult the config for the exact list.

Cell counts (smallest pooled-sex cells), from the config:

| loc4 | dgn | year_tag | n |
|---|---|---|---|
| 3 (Intel) | 1 (male) | 1 (2015) | 132 |
| 3 (Intel) | 1 (male) | 2 (2016) | 134 |
| 3 (Intel) | 1 (male) | 3 (2017) | 124 |
| 2 (NRM) | 1 (male) | 1 (2015) | 244 |
| 2 (NRM) | 1 (male) | 2 (2016) | 248 |

Smallest cell across all (loc4, dgn, year_tag) combinations is **124**;
above the n<50 threshold. No thin-cell warning fires.

---

## 10. Accepted-wage caveat

The Mincer fit is on **accepted (selected-on-employment) wages** —
specifically, observed draw=0 working wages with `loc4 ∈ {1,2,3,4}`
and `wage > 0`. This is a documented approximation to the pure
wage-offer distribution, which would require a selection correction
to recover from accepted data. The pilot config records the caveat
verbatim:

> "Coefficients are fit on accepted (selected-on-employment) wages …
> This is a documented approximation to the wage-offer distribution;
> offer-vs-accepted selection across loc4 is not corrected (per spec
> contract §14)."

The keep/condition decision (whether to condition wages on occupation
at all) is unaffected — sharp accepted separation is strong evidence
against an unconditional offer draw. The *form* of the conditional
draw carries the caveat, with selection-corrected offer Mincer (OFF)
listed as the next refinement if the pilot motivates it.

---

## 11. Stage 2 W1 wage draw implementation

Implemented in the pilot-only module
`scripts/pilot/pilot_wage_draw.py`:

```python
log_wage = mu + sigma * z         # z standard normal
wage     = exp(log_wage)
```

where, for each working simulated alternative,

```python
mu = beta_w0 + beta_w_educL*educL + beta_w_educH*educH
   + beta_w_pexp*pexp_years + beta_w_pexp2*pexp_years2
   + np.where(loc4 == 2, delta_occ2, 0)
   + np.where(loc4 == 3, delta_occ3, 0)
   + np.where(loc4 == 4, delta_occ4, 0)
   + np.where(year_tag == 1, year_2015_indicator, 0)
   + np.where(year_tag == 3, year_2017_indicator, 0)
```

`loc4` is the partner's **observed** occupation under `occ_spec="fixed"`
(retained); no occupation is sampled. sigma is the common scalar from
the Stage-1 fit (0.3771).

**Replaces production lines 1196–1204** of
`scripts/enhanced/enh_RURO_draws.py` (the unconditional `Uniform[w_min,
w_max]` draw), but the production file is **not modified**: the pilot
draw lives in the pilot module and is called only by the pilot driver.

---

## 12. Stage 2 proposal-density / log-prior correction

The matching log-density for the log-normal wage draw is implemented in
the same module:

```
log_q_wage = -log(wage) - 0.5*log(2π·sigma²) - (log_wage - mu)² / (2·sigma²)
```

(the standard log-normal PDF at the realised wage). This replaces the
production uniform term `-log(w_max - w_min)` at production reference
lines 1225–1234 of `enh_RURO_draws.py`, in lockstep with the wage draw.

**HP2 lockstep check.** On a 1024-row sample of male partners
(2016 couples, draw=0 with loc4 forced to a working code where the
diagonal had a non-working partner), `draw_pilot_wages` returns
`log_q_wage` equal to a fresh evaluation of `log_q_pilot_wages` at the
realised wage to within **max_abs_diff = 0.00e+00** (exact equality in
float64). HP2 passes. The build halts immediately if this check fails.

---

## 13. Draw method record

| Slot | Method actually used | Sequence | Scramble | Seed |
|---|---|---|---|---|
| Pilot wage draw, male partners | **Halton** | `scipy.stats.qmc.Halton(d=1, scramble=True, seed=20260522)` | True | 20260522 |
| Pilot wage draw, female partners | **Halton** | `scipy.stats.qmc.Halton(d=1, scramble=True, seed=20260523)` | True | 20260523 |
| Lockstep sanity check (HP2) | PCG64 (`numpy.random.default_rng(12345)`) | — | — | 12345 |

Sequence chosen per amendment §5: **Halton preferred** (less sensitive
to non-power-of-2 lengths than Sobol). PCG64 fallback was implemented
but not exercised — `scipy.stats.qmc.Halton` was available in the
project venv (scipy 1.16.2) and dropped in cleanly. Seed-and-log
discipline preserves the production convention (female draws use male
seed + 1).

Hours, state, and occupation draws are NOT regenerated in this slice
(they live downstream of EUROMOD in the production pipeline; the pilot
only touches the wage draw and the couples combine rule per amendment
§5 and §6). The pilot parquet inherits the production marginal draws
0..29 for partner state/hours/occupation, with the wage column
overwritten via W1 for non-chosen alternatives.

---

## 14. Stage 3 product construction

The diagonal index-pairing in `_reshape_couples_to_wide()` (production
reference `enh_RURO_prep_mnl_basic.py:1058–1065`) was replaced — in the
pilot driver only — by a 30×30 cross-join on `idhh` over draws 0..29.

Construction sketch (executed in
`scripts/pilot/build_pilot_couples_product.py::_build_product`):

1. Restrict the production 2016 couples parquet to `draw < 30` →
   77,310 male-side rows and 77,310 female-side rows
   (= 2,577 couples × 30 draws each).
2. Split the wide parquet into a male-side frame (`_male` columns +
   shared/household columns, `draw` renamed to `draw_male`) and a
   female-side frame (`_female` columns only, `draw` renamed to
   `draw_female`).
3. Cross-join on `idhh` (inner merge) → 2,319,300 rows per couple over
   the 900 joint alternatives.
4. Emit `draw_male ∈ {0..29}`, `draw_female ∈ {0..29}`,
   `draw_joint = 30·draw_male + draw_female ∈ {0..899}`.
5. Construct `is_chosen_male = (draw_male == 0)`,
   `is_chosen_female = (draw_female == 0)`,
   `is_chosen_joint = (draw_male == 0 AND draw_female == 0)`.

The legacy production single-integer `draw` column is **dropped** from
the pilot parquet to avoid ambiguity (downstream consumers in the
pilot must read `draw_joint`); this is recorded as part of the
downstream re-pointing surface for the next slice (§22, §26).

**Partner-dependence assumption (stated explicitly per amendment §6):**
conditional independence of the partners' opportunity draws. The
product is the correct joint sample under this assumption; the
diagonal silently imposed maximal dependence and is removed.

---

## 15. `draw_male` / `draw_female` / `draw_joint` validation

| Quantity | Value | Expected |
|---|---|---|
| Distinct `draw_male` values | 30 | 30 |
| Distinct `draw_female` values | 30 | 30 |
| Distinct `draw_joint` values | 900 | 900 |
| Range of `draw_male` | 0..29 | 0..29 |
| Range of `draw_female` | 0..29 | 0..29 |
| Range of `draw_joint` | 0..899 | 0..899 |
| `draw_joint == 30·draw_male + draw_female` | True (by construction) | True |

All cardinalities and ranges match. No HP3 violation on the join keys.

---

## 16. Chosen-row validation

| Quantity | Value |
|---|---|
| Rows with `draw_joint == 0` | **2,577** |
| Distinct couples represented in chosen rows | **2,577** |
| `is_chosen_male == is_chosen_female` on chosen rows | **True** (all 2,577) |
| Number of couples with > 1 chosen row | 0 |
| Number of couples with 0 chosen rows | 0 |

Exactly one row per couple has `draw_joint == 0`; on every such row,
`is_chosen_male` and `is_chosen_female` are both 1. **HP3 passes.**

---

## 17. Stage 4 pilot parquet output

Path:
`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet`

| Property | Value |
|---|---|
| Format | Parquet, Snappy-compressed |
| Engine | pyarrow |
| Rows | **2,319,300** |
| File size | 89,179,800 bytes (≈85.0 MiB) |
| Columns | Wide (male + female fields side by side) + `draw_male`, `draw_female`, `draw_joint`, `is_chosen_male`, `is_chosen_female`, `is_chosen_joint` + pilot `log_q_wage_male_pilot`, `log_q_wage_female_pilot` |
| Wage columns | `wage_male`, `wage_female` — drawn under W1 log-normal on non-chosen alternatives; preserved as observed on chosen rows (`draw_joint == 0`) |
| Working-alt wage draws applied | male: 2,013,180; female: 2,015,790 (loc4 ∈ {1,2,3,4} AND draw_*partner* > 0) |
| EUROMOD-dependent columns | **Dropped** (5 column prefixes: `ils_dispy`, `ils_dispy_em`, `i_`, `il_`, `tu_`). Not valid for product alternatives pre-EUROMOD. |

The pilot parquet is a **choice-set scaffold**: it has the joint
choice-set structure and the W1 wage values for every non-chosen
alternative, but it does not yet have disposable income or any
EUROMOD-dependent quantity for non-chosen alternatives. Those are the
input for Stage 5 (EUROMOD), which is **not authorized** in this slice.

---

## 18. Metadata sidecar

Path:
`Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__mnlmeta.json`

Key fields:

| Field | Value |
|---|---|
| `schema_version` | `nc_pilot_couples_product_v1` |
| `year` | 2016 |
| `country` | FR |
| `household_type` | couples_only |
| `n_couples` | 2577 |
| `n_draws_per_couple` | 900 |
| `product_size` | 30×30 |
| `row_count` | 2,319,300 |
| `wage_model` | W1 (occupation-conditioned log-normal); reference loc4 = 1 |
| `wage_sigma` | 0.3771 |
| `wage_sigma_kind` | common (single scalar) |
| `calibrated_delta_occ.status` | calibrated, fixed at draw time, NOT free structural parameters |
| `occ_spec` | fixed (partner loc4 = observed loc4 across all 900 alternatives) |
| `partner_dependence_assumption` | conditional independence |
| `singles_production_rows_unchanged` | 500700 |
| `EUROMOD_status` | not_run |
| `GSUR_status` | not_run |
| `precompute_status` | not_run |
| `estimation_status` | not_run |
| `draw_method.wage_male` | halton |
| `draw_method.wage_female` | halton |
| `draw_method.seed_male` | 20260522 |
| `draw_method.seed_female` | 20260523 |
| `draw_method.scramble` | true |
| `stage_2_lockstep_HP2.ok` | true |
| `stage_2_lockstep_HP2.max_abs_diff` | 0.0 |

The metadata also records the `income_columns_dropped` list (the
EUROMOD-dependent columns removed because they are not valid for
product alternatives) and a `downstream_draw_repointing_surface` note
identifying the change that downstream consumers will need to absorb
in the next slice.

---

## 19. Row-count validation

| Quantity | Value | Expected | Result |
|---|---|---|---|
| Pilot couples rows | **2,319,300** | 2,577 × 900 = 2,319,300 | **PASS (HP9)** |
| Distinct couples in pilot parquet | 2,577 | 2,577 | PASS |
| Chosen rows per couple (= 1) | 1 for all 2,577 | exactly 1 | PASS (HP3) |
| Singles production parquet rows | **500,700** | 500,700 unchanged | PASS (HP9) |
| Production couples parquet rows | 743,800 (unchanged, read-only) | 743,800 | PASS (HP9; production untouched) |

---

## 20. Production-safety validation

| Check | Result |
|---|---|
| `git status --short` shows only `scripts/pilot/` untracked, plus `Results/` outputs | **OK** — no production file is `M` or `??`-flagged |
| `scripts/enhanced/enh_RURO_draws.py` modification time | Unchanged (read-only access) |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` modification time | Unchanged |
| `scripts/maintenance/prepare_pooled_estimation_ready.py` modification time | Unchanged (row guards at lines 70–72 not touched) |
| `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml` modification time | Unchanged (frozen P3a YAML intact) |
| Production singles parquet rows | 500,700 (re-confirmed at run time) |
| Production couples parquet rows | 743,800 (untouched) |
| Production `__mnlmeta.json` | Unchanged |
| Corrected pooled P3a outputs under `Results/JMP_pooled_P3a_*` | Unchanged |

HP1 (production behaviour change when pilot absent) does not fire: the
production pipeline imports nothing from `scripts/pilot/` and would run
identically if `scripts/pilot/` did not exist.

---

## 21. Halt-condition status

| Halt | Condition | Status |
|---|---|---|
| **HP1** | Production script/YAML/guard change | **NOT FIRED** |
| **HP2** | Wage draw / proposal density inconsistent | **NOT FIRED** (lockstep max_abs_diff = 0.0 on 1024-row sample) |
| **HP3** | `draw_joint == 0` chosen-row violation, or `is_chosen_male ≠ is_chosen_female` | **NOT FIRED** (2,577/2,577 couples have exactly one chosen row; flags consistent) |
| **HP9** | Pilot row count ≠ 2,577 × 900 or singles drift from 500,700 | **NOT FIRED** (2,319,300 = 2,577 × 900; singles unchanged) |
| **HP-STAGE** | Any Stage 5+ action, welfare, SA2, promotion, M1-clean displacement | **NOT FIRED** (hard stop honoured) |
| HP4 / HP5 / HP6 / HP7 | Not applicable to this slice (no EUROMOD, no GSUR, no precompute, no estimation) | Not applicable |

**No halt fired.** All stages 1–4 completed.

---

## 22. What was not executed

- **Stage 5 — EUROMOD.** Not run; not authorized in this slice. The
  product alternatives have wage and joint-choice structure but no
  disposable income beyond the chosen row.
- **Stage 6 — GSURv2 re-merge.** Not run.
- **Stage 7 — full MNL estimation-ready rebuild / split-stem.** Not run
  beyond the pilot parquet + metadata of Stage 4. Singles parquet is
  not regenerated.
- **Stage 8 — precompute checks.** Not run.
- **Stage 9 — diagnostic pilot estimation.** Not run. No 400 / 900 /
  1,600 simulation-consistency builds either (the consistency-builds
  are a later slice, not authorized here).
- **Welfare, SA2, canonical promotion, M1-clean displacement.** Not
  performed; not authorized.
- **Downstream `draw_joint` re-pointing.** Identified (see §26) but not
  executed; that is the next slice.
- **W2 (occ × sex), occupation-specific sigma, free structural
  `delta_occ*`, selection-corrected offer Mincer (OFF).** All deferred.

---

## 23. Whether Stage 5 EUROMOD authorization is now ready

**No.** Stage 5 remains unauthorized. The amendment's hard stop is
explicit: "stops at Stage 4 and reports" (amendment §3, §8). Before
Stage 5 can be authorized, the executor needs an explicit
EUROMOD-runner confirmation (location, invocation, expected wall time,
output schema, target path under the pilot directory). The build
report (this document) and the pilot parquet provide the inputs
EUROMOD will consume in a later slice; what is missing is the
runner-side confirmation and a separate authorization document.

---

## 24. Whether welfare computation is authorized

**No.** Welfare is explicitly excluded from this slice (amendment §10
and §11 HP-STAGE) and from the spec contract (§25). No welfare is
computed in this session and none will be without a separate
authorizing document. Welfare requires SA2 passage on a credible
structural baseline; the pilot is a feasibility-and-design instrument,
not a verdict-grade baseline.

---

## 25. Whether M1-clean remains active

**Yes.** M1-clean 2016 (`ruro_occ_M1_clean`) remains the active JMP
baseline. Nothing in this session displaces it. The corrected pooled
P3a (`ruro_occ_P3a_pooled`) is still under post-estimation review on
its frozen 100-diagonal, unconditional-wage spec, independent of this
pilot.

---

## 26. Immediate next task

Two candidates, in order of priority:

1. **Next pilot slice — downstream `draw_joint` re-pointing audit.**
   The pilot parquet drops the legacy single-integer `draw` column.
   Downstream code that previously encoded `draw == 0` semantics for
   the couples block must be updated to read `draw_joint` (or
   equivalently `(draw_male == 0) AND (draw_female == 0)`). Re-pointing
   surface identified by Grep in `scripts/enhanced/`:

   | Site | Line | Context |
   |---|---|---|
   | `enh_RURO_draws.py` | 370 | `is_draw0 = df["draw"] == 0` (chosen-row mask in draw construction) |
   | `enh_RURO_prep_mnl_basic.py` | 1234 | `chosen_mask = df["draw"] == 0` (prep step) |
   | `enh_RURO_prep_mnl_basic.py` | 1286 | `chosen_mask = df["draw"] == 0` (second prep call site) |
   | `enh_RURO_euromod.py` | 492 | `person_max_draw[person_max_draw == 0]` (EUROMOD wrapper non-decider filter) |
   | `estimation_engine.py` | 380 | comment + observed-V extraction (draw==0 first in each group) |
   | `quick_verify.py` | 176 | verification mask `df[df["draw"] == 0]` |

   **These sites are NOT changed in this slice.** They are documented
   here as the next-slice surface. Any re-pointing should live in
   pilot-only modules or behind a pilot flag; production paths
   continue to read `draw` until a later slice authorizes the change.

2. **EUROMOD-runner confirmation.** Independent of (1) and required
   for Stage 5: confirm the EUROMOD runner's location, invocation,
   wall-time expectation, and output schema. Without this, Stage 5
   cannot start.

A dedicated next-cycle authorization document should be produced for
each before any further build action.

**Promotion debt** flagged by the pilot drivers (per spec contract §17):

- `EXPECTED_COUPLES_2016 = 2577` hard-coded in
  `scripts/pilot/build_pilot_couples_product.py` (would parameterize for
  FR_2015/2017 or other countries).
- `PRODUCT_SIZE = 30` hard-coded (would parameterize for 20×20 / 40×40
  consistency builds in the deferred later slice).
- `year_tag` mapping `{1:2015, 2:2016, 3:2017}` consumed; no general
  year-set abstraction.
- Mincer fitting set fixed (pooled 2015–2017 singles+couples) by the
  Stage-1 driver.

---

**Required final statements:**

- **Stages 1–4 PASSED.**
- **No EUROMOD was run.**
- **No GSUR merge was run.**
- **No precompute was run.**
- **No estimation was run.**
- **No welfare was computed.**
- **No SA2 was issued.**
- **M1-clean 2016 remains the active baseline.**
- **The corrected pooled P3a track is unaffected.**

---

*Status: NC pilot Stage 1–4 build report v1, produced 2026-05-22.
Authorization: `docs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md`.
Hard stop honoured before EUROMOD. M1-clean 2016 active. Frozen pooled
P3a spec and post-estimation track unaffected. Next document(s): a
downstream-re-pointing-audit authorization, and (separately) an
EUROMOD-runner authorization.*
