# RURO certified baseline — canonical styled post-estimation report (pointer + provenance)

**Date:** 2026-06-05
**Increment:** STAGE FIVE-A2 — complete the canonical styled post-estimation reporting layer for
the certified baseline.
**Status:** complete. **Post-estimation reporting only — READ-ONLY. No re-estimation, no welfare
pricing, no `V_i^dir`, no `W^3` promotion, no production/staged-pricing changes.**

This memo points to the external styled-report artifacts and records how they were produced.
**There are two distinct HTML reports; keep them in separate lanes:**

| | repo HTML | external HTML |
|---|---|---|
| file | `docs/jmp_methodology/RURO_postestimation_descriptives_v1.html` | `…/EUROMOD-STORAGE/outputs/post_estimation/realdata_joint_901_tlmpin_certified/joint/…/joint_post_estimation_report_*.html` (+ `joint_enhanced_*`) |
| nature | **bespoke descriptive dashboard** (Stage Five-A) — pure opportunity readout, utility-weighted attractiveness, ESS, SE asymmetry, LOC4 wage-density clarification | **canonical styled post-estimation report** (`RURO_post_estimation_styled.py`) — participation/hours fit, wage/hours distributions, MUC/MUL, indifference contours, elasticities, inference + Hessian diagnostics |
| label | descriptive at certified θ; not welfare; not re-estimation | canonical styled post-estimation report |

---

## Certified styled report — how it was produced (read-only)

**Inputs (certified baseline, all pre-existing):**

- spec: `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` (47 free params;
  `theta_l_m` pinned −0.8; `beta_ll` fixed 0)
- theta + SEs: `scripts/bpool/specs/theta_hat_realdata_901_v1.csv`
  (`value, se_hessian, se_clustered`)
- baseline doc: `docs/France_case/P3a/execution_logs/Bpool/RURO_realdata_2016_2017_joint_901_v1.md`
- engine-ready: `fr_p3a_bpool_engine_ready` (singles 101, couples 901)

**Step 1 — certified joint `estimation_results.json`** (Five-A) via
`scripts/bpool/step4_emit_results_json.py --joint-mode` → emits one results JSON carrying the
full joint 47-param vector + the certified Hessian + clustered SEs. (No estimation.)

**Step 2 — base styled report** (Five-A): `scripts/enhanced/RURO_post_estimation_styled.py` on
that results JSON (the certified SEs are embedded, so **no** `--compute-se`). Produced the full
per-group HTML + ~25 plots/tables (fit, wage/hours distributions, MUC/MUL, contours,
elasticities, inference, diagnostics bundle).

**Step 3 — cluster-robust-SE artifact** (Five-A2, read-only): `scripts/diagnostics/run_stage5a2_cluster_se_artifact.py`
**assembles** the `cluster_robust_se_artifacts` JSON the enhanced layer needs (the schema in
`docs/reporting/RURO_post_estimation_styled_general_reporting_enhancement_v1.md` §6) **from the
existing certified artifacts** — the certified theta/SE vectors + the certified Hessian/cluster
facts parsed from the baseline doc's embedded JSON. **The sandwich is NOT recomputed**; the
certified clustered SEs are taken as-is. Values: `n_free` = **47**; `PE6_true_hessian` condition
number **1.295e6** (not near-singular, < 1e12); **T3** 9,657 clusters (idorighh); **T4**
SE-positivity passes on the free block (0 nonpositive); **T5** clustered/Hessian ratio median
**1.23**, max **2.08** (>1 as expected with the 2016–2017 repeat-HH clustering). Written to
`…/realdata_joint_901_tlmpin_certified/joint/certified_cluster_robust_se.json`.

**Fixed/pinned parameters in the styled table.** The certified identified block is **47 free
parameters**; `theta_l_m` is pinned (−0.8) and `beta_ll` is removed (= 0). `step4_emit_results_json.py`
injects the pinned `theta_l_m` into the results JSON so the spec-driven V-function is complete, so
it also appears as a row in the styled inference table. To avoid displaying it as a free parameter
with a misleading flag, the cluster-SE artifact appends `theta_l_m` **explicitly as a NON-FREE row**
(`free_mask = False`, NaN SEs, `n_free = 47`, `n_displayed = 48`, `pinned_params = ["theta_l_m"]`),
so the reporter marks it outside the identified block. **In all cases: the styled table may display
fixed parameters from the full spec, but the enhanced free-block diagnostics and the PE6/T3/T4/T5
gates apply only to the 47-parameter identified block.**

**Step 4 — enhanced styled report** (Five-A2): re-ran `RURO_post_estimation_styled.py` with
`--cluster-se-json certified_cluster_robust_se.json --cluster-col idorighh`, which activates the
extended diagnostics (inference table with robust t/p, Hessian/T3-T5/PE6 section, reproducibility
metadata) and writes `joint_enhanced_extended_diagnostics.{md,json}` alongside the styled HTML.

---

## Artifacts genuinely UNAVAILABLE (reported, not fabricated)

The certified estimate was produced by the **JAX backend** (constrained two-stage optimizer),
**not GAMS/CONOPT**. Therefore the CONOPT/GAMS-specific solver artifacts do **not exist** and
were **not** supplied to the enhanced reporter; the reporter renders them as
*"Not available in supplied solver artifacts"*, which is the correct, honest state:

- `--solver-log` (plain-text GAMS/CONOPT log) — **unavailable** (no CONOPT run).
- `--listing-file` (GAMS `.lst`; RGmax, RTOL/FTOL, equations/variables/nonzeros, active bounds)
  — **unavailable** (no GAMS listing; the certified two-start convergence + PD-Hessian evidence
  lives in `RURO_jax_recovery_gate_tlmpin_901_v1.md` and the certified baseline doc).
- `--gradient-diagnostics` (Python central-difference score at convergence) — **not run** here:
  it would recompute the likelihood gradient, and this increment stays strictly read-only on the
  estimate (the certified stationarity evidence is the recovery-gate's max|grad| + PD Hessian).
- `--comparison-results-json` — not used (no second run to compare).

The JAX-backend convergence + identification evidence the CONOPT fields would otherwise carry is
already certified upstream: PD Hessian (min_eig **+0.459**, cond **1.295e6**), two-start
agreement, and the 901 Check-5 re-gate (min_eig +1.706).

---

## Report classification

This is the **"canonical styled post-estimation report, base + enhanced (cluster-SE) layer"** —
**not** the full general-reporting enhancement with CONOPT solver/listing/RGmax sections (those
require a GAMS run that does not exist for the JAX-backend certified baseline). The cluster-SE /
Hessian / T3-T5 / PE6 / inference-table / reproducibility sections **are** populated; the
GAMS/CONOPT solver-diagnostics and Python-gradient sections are reported as unavailable / not
run.

---

## Files

- **Assembler (repo):** `scripts/diagnostics/run_stage5a2_cluster_se_artifact.py` (read-only;
  builds the cluster-SE artifact from existing certified artifacts). Ruff-clean.
- **This memo (repo):** the pointer + provenance.
- **Provenance JSON (repo):** `outputs/welfare/stage1_w3/stage5a2_styled_enhanced.json`.
- **External styled outputs** (canonical reports location, outside the repo, under
  `…/EUROMOD-STORAGE/outputs/post_estimation/realdata_joint_901_tlmpin_certified/joint/`):
  `estimation_results.json`, `certified_cluster_robust_se.json`, the base styled HTML
  (`joint_post_estimation_report_*.html`), the enhanced styled HTML + extended-diagnostics
  (`joint_enhanced_*`), and the ~25 plot PNGs / CSVs / diagnostics JSONs.
- **Unchanged:** certified theta, engine-ready data, staged reference, production priced files.

## Explicit scope statement

Post-estimation reporting only. Read-only. No re-estimation; no sandwich recompute; no welfare
pricing; no `V_i^dir`; no `W^3` promotion; no production/staged-pricing changes; no spec change;
no canonical promotion. CONOPT solver artifacts are reported as unavailable (JAX backend), not
fabricated.
