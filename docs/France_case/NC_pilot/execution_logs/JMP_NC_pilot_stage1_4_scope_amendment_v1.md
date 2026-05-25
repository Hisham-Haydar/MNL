# JMP NC Pilot — Stage 1–4 Scope Amendment v1

*France RURO multi-year extension | v1 | 2026-05-22*

**Document category: scope amendment to `docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md`.**
This amendment narrows the authorized build to **Stages 1–4 only** (pre-draw
Mincer fit → pilot wage draw → 30×30 product → pilot couples parquet +
metadata), stopping **before EUROMOD**. It changes the *execution scope*, not
the *specification*: every decision in the spec contract (W1 baseline,
two-group comparison, `delta_occ*` calibrated, `occ_spec="fixed"`, common
sigma, `draw_male`/`draw_female`/`draw_joint` convention, chosen row at
`draw_joint==0`) is carried forward unchanged. M1-clean 2016 remains active.
The corrected pooled P3a track is unaffected.

---

## 1. Purpose

To authorize a checkpointed first build slice — Stages 1–4 of spec contract
§28 — that produces the pilot's wage model, regenerated draws, and the
900-alternative couples choice set **without** touching EUROMOD, GSUR, the
MNL estimation-ready stack, precompute, or estimation. This slice builds
everything that is *upstream* of EUROMOD so the expensive EUROMOD step (and
the design choices around it) can be reviewed before it is launched.

The slice resolves, by pre-deciding them here, the four open runtime choices
the build report (`Results/JMP_NC_pilot_build_report_v1.md` §15) flagged as
needed-to-resume for Stages 1–4 (Mincer set, draw method, output paths,
staged execution). The fifth (EUROMOD runner status) is deferred — it is
precisely what this slice stops short of.

---

## 2. Why the original build halted

The original §28 prompt bundled Stages 1–9 — Mincer fit, draws, product
parquet, MNL rebuild, EUROMOD (2,319,300 evaluations), GSUR re-merge,
precompute, and a diagnostic estimation — into one autonomous run. The build
report records a **pre-execution scope halt** (Option C), on four grounds:
(a) the EUROMOD runner's location, invocation, wall time, and output schema
were unverified, and launching it is a large-blast-radius action; (b) the
contract frames the pilot as a checkpointed feasibility instrument, not a
single opaque job; (c) several Stage 1–4 choices were left as executor
judgment (Halton vs Sobol vs PCG64; pooled vs 2016-only Mincer; output paths;
`--pilot` flag vs separate driver); (d) preserving HP8 invariants until
EUROMOD is confirmed argued for doing no writes. No HP1–HP9 technical halt
fired; the working tree is clean except the report. This amendment responds
by authorizing only the upstream, reviewable, cheap slice.

---

## 3. Corrected scope

**Authorized:** Stages 1–4 (this amendment, §4–§7), under the safeguards of
§8 and the halt conditions of §11.

**Hard stop:** the build halts after Stage 4 and writes its report. It does
**not** begin Stage 5 (EUROMOD) or anything downstream.

Stage-by-stage:

| Stage | Action | Authorized here |
|---|---|---|
| 1 | W1 + two-group Mincer fit (pre-draw) | **Yes** |
| 2 | Pilot W1 wage draw + matching proposal density | **Yes** |
| 3 | 30×30 product alternatives for 2016 couples | **Yes** |
| 4 | Pilot couples parquet (900 alts) + metadata | **Yes** |
| 5 | EUROMOD | **No — hard stop before** |
| 6 | GSUR re-merge | No |
| 7 | MNL estimation-ready rebuild / split-stem | No (beyond the pilot parquet + metadata of Stage 4) |
| 8 | Precompute checks | No |
| 9 | Diagnostic estimation | No |

All Stage 1–4 outputs are written to **pilot-only paths** (§8); no production
P3a file, YAML, data parquet, or row guard is touched.

---

## 4. Stage 1 authorization

**Authorized: fit the W1 and two-group Mincer models (pre-draw step).**

- **Sample:** working observed (draw=0) alternatives, `loc4 ∈ {1,2,3,4}`,
  `wage > 0`, singles + couples.
- **Year set (pre-decided, resolving build-report §15.3):** **pooled
  2015–2017 with year controls.** The build report confirmed the pooled
  working sample is accessible at fit time (≈4,611 working singles plus
  ≈7,134 male / ≈7,141 female working couples partners spanning 2015–2017).
  Pooled is the contract's §15 preferred choice; use it. The 2016-only
  fallback is invoked **only** if the pooled working sample proves
  inaccessible at runtime, in which case the build flags thin-cell risk
  (e.g. Intel-Male n≈104 in singles) in the report.
- **W1 model:**
  `log w = beta_w0 + beta_w_educL·educL + beta_w_educH·educH + beta_w_pexp·pexp_years + beta_w_pexp2·pexp_years2 + delta_occ2·1[loc4=2] + delta_occ3·1[loc4=3] + delta_occ4·1[loc4=4] + ε`,
  reference `loc4=1`, common slopes, single common `sigma`.
- **Two-group model:** identical but with a single `delta_NonInt·1[loc4=4]`.
- **Output:** a pilot config file holding both coefficient sets, **tagged with
  fitting set** (years = 2015–2017 pooled, population = working singles +
  couples, n per cell), written to the pilot config path (§8). These are
  **calibrated** inputs to the draw stage, not free structural parameters.
- **Accepted-wage caveat:** the report must state the fit is on accepted
  (selected-on-employment) wages, a documented approximation to the offer
  distribution (contract §14).

---

## 5. Stage 2 authorization

**Authorized: build the pilot-only W1 wage draw and its matching
proposal-density / log-prior path.**

- In the **pilot draw path only** (not the production `enh_RURO_draws.py`
  in place — see §8), replace the unconditional `Uniform[w_min,w_max]` wage
  draw (production reference lines ~1196–1204) with sampling log w from
  `Normal(X_i β + δ_{loc4_i}, σ²)` and exponentiating, where `loc4_i` is the
  person's occupation (= observed occupation under `occ_spec="fixed"`, which
  is retained).
- **Matching proposal density (HP2 — hard requirement):** replace the uniform
  term `-log(w_max − w_min)` (production reference lines ~1225–1234) with the
  log-normal density evaluated at the drawn wage, **in lockstep**. The wage
  draw and its `log_q_wage` term must be changed together; a mismatch breaks
  the importance-sampling correction.
- **Draw method (pre-decided, resolving build-report §15.4):** **Halton**
  (`scipy.stats.qmc.Halton`, scrambled, seeded) for the couples product draws
  if it drops cleanly into the wage/hours/state call sites; **PCG64 documented
  fallback** otherwise. Sobol is not used in the pilot (30 and 900 are not
  powers of two; Halton is the lower-friction low-discrepancy choice). Record
  sequence + seed + scramble in the report. Preserve the existing seed-and-log
  discipline (couples seed = singles seed + 1).
- Marginal draws **are regenerated** in the pilot path (forced by the wage
  change), per contract §5/§18.
- Build both wage variants' draw inputs (W1 and two-group) so Stage 3/4 can
  carry both, or build W1 first and two-group as a parallel variant — either
  is acceptable provided both are produced as pilot artifacts.

---

## 6. Stage 3 authorization

**Authorized: construct the 30×30 product alternatives for 2016 couples.**

- In the **pilot reshape path only**, replace the diagonal inner-merge on
  `["idhh","draw"]` (production reference `_reshape_couples_to_wide()` lines
  ~1058–1065) with a cross-join on `idhh` over the first 30 male and first 30
  female marginal draws → 900 joint alternatives per couple.
- **Emit all three draw identifiers:** `draw_male ∈ {0..29}`,
  `draw_female ∈ {0..29}`, `draw_joint = 30·draw_male + draw_female ∈ {0..899}`.
- **Chosen row:** `draw_male==0 AND draw_female==0` ⇔ `draw_joint==0`.
- **Invariants:** exactly one male and one female record per `(idhh, draw_joint)`;
  `is_chosen_male == is_chosen_female`; **exactly one** `draw_joint==0` row per
  couple.
- **Partner-dependence assumption:** conditional independence (the product is
  the correct joint sample); stated explicitly in the build, per contract §5.
- Scope is **2016 couples only**. Singles are not touched. (Stages 1–4 produce
  the 900-alt block; the 400/900/1,600 consistency builds of contract §23 are
  a *later* slice, not authorized here.)

---

## 7. Stage 4 authorization

**Authorized: write the pilot couples parquet and its metadata.**

- Write the 900-alternative wide-format couples parquet to the **pilot data
  path** (§8). Do **not** write singles (unchanged; not part of this slice)
  and do **not** produce the full estimation-ready split-stem stack.
- Write a **pilot `__mnlmeta.json`** with couples `n_draws = 900`. (Singles
  metadata is not regenerated in this slice.)
- **Row-count verification (HP9):** couples rows must equal
  **2,577 × 900 = 2,319,300**. Halt if not.
- **Chosen-row verification (HP3):** exactly one `draw_joint==0` per couple;
  `is_chosen_male==is_chosen_female`. Halt if not.
- No EUROMOD income, no GSUR centring, no region-array precompute is performed
  on this parquet — those are downstream stages. The parquet at this stage is
  the choice-set scaffold with regenerated draws and W1 wage values, awaiting
  EUROMOD disposable income in a later slice.

---

## 8. Required safeguards

- **Pilot-only code/config/data paths.** Suggested defaults (executor may
  confirm/override): pilot code under `scripts/pilot/`, pilot config under
  `scripts/pilot/config/`, pilot data + metadata under
  `Data/pilot/nc_2016_couples/`. Resolves build-report §15.2.
- **No in-place edits to production.** `enh_RURO_draws.py`,
  `enh_RURO_prep_mnl_basic.py`, `prepare_pooled_estimation_ready.py`, and the
  P3a YAML are **read-only references**. The pilot wage draw (§5) and product
  reshape (§6) live in pilot copies/modules, not patched production functions.
- **Production row guards untouched** (`prepare_pooled_estimation_ready.py`
  lines 70–72): not edited; the pilot uses its own driver/expected counts
  (separate-driver option of contract §17). Resolves build-report §15.5 as
  "staged, separate driver."
- **Staged execution (pre-decided, resolving build-report §15.5):** this slice
  *is* the staging — it stops at Stage 4 and reports. No autonomous
  continuation into Stage 5.
- **HP2 lockstep** between wage draw and proposal density (§5).
- **Country/year/spec-agnostic where feasible** (contract §17): parameterize
  country, year set, product size (the 30 and the joint-key multiplier),
  reference occupation, fitting set; flag any hard-coded
  France/P3a/2016/900/30 constant as promotion debt in the report.

---

## 9. Required outputs

1. Pilot Mincer coefficient config (W1 + two-group, tagged with fitting set).
2. Pilot draw artifacts (regenerated marginals with W1 wage values; draw-method
   record).
3. Pilot 900-alternative couples parquet (2016) at the pilot data path.
4. Pilot `__mnlmeta.json` (couples `n_draws=900`).
5. **Build report:** `Results/JMP_NC_pilot_stage1_4_build_report_v1.md` (§12),
   including the row-count and chosen-row verifications, draw-method record,
   accepted-wage caveat, promotion-debt list, and the downstream `draw_joint`
   re-pointing surface *identified* (not yet changed — that is a later slice).

---

## 10. What is not authorized

- EUROMOD (Stage 5) and everything downstream.
- GSUR re-merge; MNL estimation-ready rebuild beyond the Stage-4 pilot parquet
  + metadata; precompute; estimation; welfare; SA2; canonical promotion;
  M1-clean displacement.
- Singles rebuild or singles re-draw.
- The 400/1,600 consistency builds (later slice).
- Free structural estimation of `delta_occ*` (calibrated only).
- Any in-place edit to production scripts, the P3a YAML, or the production row
  guards.
- Any write to production data/estimation directories.

---

## 11. Halt conditions

Stages 1–4 inherit the spec-contract halts that can fire upstream of EUROMOD,
plus the slice boundary:

| Halt | Condition |
|---|---|
| **HP1** | Any production script/YAML/guard changes (in-place edit leaked). |
| **HP2** | Wage draw changed without the matching proposal-density term (importance-sampling inconsistency). |
| **HP3** | `draw_joint==0` does not select exactly one chosen row per couple, or `is_chosen_male ≠ is_chosen_female`. |
| **HP9** | Couples pilot rows ≠ 2,577 × 900 = 2,319,300, or any singles artifact is modified. |
| **HP-STAGE** | Any attempt to begin Stage 5 (EUROMOD) or beyond, compute welfare, issue SA2, promote, or displace M1-clean. |

HP4 (disposable-income), HP5 (GSUR centring), HP6 (region all-NaN), HP7
(free-`delta_occ*` identification) are **not applicable** to this slice (no
EUROMOD, no GSUR, no region precompute, no estimation; `delta_occ*` calibrated
by design). Any fired halt → stop, write the report up to the halt, await
direction. Do not work around.

---

## 12. Required report

`Results/JMP_NC_pilot_stage1_4_build_report_v1.md`, covering: scope and
authorization provenance (this amendment); Stage 1 (Mincer coefficients,
fitting set, accepted-wage caveat, thin-cell flag if 2016-only fallback used);
Stage 2 (wage-draw path, proposal-density lockstep confirmation, draw method +
seed + scramble); Stage 3 (product construction, draw_male/female/joint,
invariants); Stage 4 (pilot parquet path, row-count = 2,319,300 verification,
chosen-row verification, pilot metadata n_draws=900); pilot output paths used;
downstream `draw_joint` re-pointing surface identified for the next slice;
promotion-debt list; halt-condition status; and required final statements
(EUROMOD not run; M1-clean active; P3a unaffected; no welfare/SA2/promotion;
Stages 1–4 only).

---

## 13. Exact Claude Code task

Use **Claude Code (Sonnet)**, local. Pilot paths only; stop after Stage 4.

```text
Work locally in my RURO/MNL codebase. PILOT BUILD — STAGES 1–4 ONLY,
2016 couples only. Authorized by docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md
(narrows docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md to Stages 1–4; HARD STOP
before EUROMOD).

HARD CONSTRAINTS (halt and report if any would be violated):
- STOP after Stage 4. Do NOT run EUROMOD, GSUR re-merge, MNL estimation-ready
  rebuild beyond the pilot parquet+metadata, precompute, or estimation.
- Do NOT edit production in place: enh_RURO_draws.py,
  enh_RURO_prep_mnl_basic.py, prepare_pooled_estimation_ready.py, and the
  P3a YAML are READ-ONLY references. Put the pilot wage draw and product
  reshape in PILOT modules/copies under scripts/pilot/.
- Do NOT touch production row guards (prepare_pooled_estimation_ready.py
  lines 70-72). Use a pilot driver/config with pilot-specific counts.
- Pilot paths only: code scripts/pilot/, config scripts/pilot/config/,
  data+metadata Data/pilot/nc_2016_couples/ (confirm or override, but no
  production path writes).
- delta_occ* are CALIBRATED (Stage-1 Mincer, fixed at draw time), NOT free.
- Do NOT compute welfare, issue SA2, promote anything, or displace M1-clean.
- Singles are NOT touched.

Read first (confirm, don't assume):
- docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md
- docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md
- Results/JMP_nc_pilot_feasibility_audit_v1.md
- scripts/enhanced/enh_RURO_draws.py
- scripts/enhanced/enh_RURO_prep_mnl_basic.py
- scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml

STAGE 1 — Mincer fit (pre-draw):
- Sample: working observed (draw=0) alternatives, loc4 in {1,2,3,4}, wage>0,
  singles + couples, POOLED 2015-2017 with year controls. If the pooled
  working sample is not accessible at fit time, fall back to 2016-only and
  FLAG thin cells in the report.
- Fit W1: log w = beta_w0 + beta_w_educL*educL + beta_w_educH*educH
  + beta_w_pexp*pexp_years + beta_w_pexp2*pexp_years2
  + delta_occ2*1[loc4=2] + delta_occ3*1[loc4=3] + delta_occ4*1[loc4=4],
  ref loc4=1, common slopes, single common sigma.
- Fit two-group: same with single delta_NonInt*1[loc4=4].
- Write both coefficient sets to a pilot config, TAGGED with fitting set
  (years, population, n per cell). Record the accepted-wage caveat.

STAGE 2 — Pilot wage draw + proposal density (pilot path only):
- Replace Uniform[w_min,w_max] (prod ref ~1196-1204) with
  Normal(Xb + delta_loc4, sigma^2) log-wage draw, then EXPONENTIATE;
  loc4 = observed occupation (occ_spec=fixed retained).
- Replace the uniform proposal term -log(w_max-w_min) (prod ref ~1225-1234)
  with the matching log-normal density IN LOCKSTEP (HP2).
- Draw method: Halton (scipy.stats.qmc.Halton, scrambled, seeded) if it drops
  cleanly into the wage/hours/state call sites; else documented PCG64
  fallback. NOT Sobol. Record sequence+seed+scramble. Keep couples seed =
  singles seed + 1.
- Regenerate marginals in the pilot path (forced by the wage change).
- Produce draw inputs for BOTH W1 and two-group as pilot artifacts.

STAGE 3 — 30x30 product (2016 couples):
- Replace diagonal inner-merge on ["idhh","draw"] (prod ref ~1058-1065) with
  a cross-join on idhh over draws 0..29 each -> 900 joint alts/couple.
- Emit draw_male in 0..29, draw_female in 0..29,
  draw_joint = 30*draw_male + draw_female in 0..899.
- Chosen row = (draw_male==0 AND draw_female==0) == (draw_joint==0).
- Invariants: one male + one female per (idhh, draw_joint);
  is_chosen_male==is_chosen_female; exactly one draw_joint==0 per couple.
- Conditional-independence assumption stated. 2016 couples only.

STAGE 4 — Pilot parquet + metadata:
- Write the 900-alt wide couples parquet to Data/pilot/nc_2016_couples/.
- Write a pilot __mnlmeta.json with couples n_draws=900.
- VERIFY couples rows == 2,577 * 900 == 2,319,300 (HP9; halt if not).
- VERIFY exactly one draw_joint==0 per couple and
  is_chosen_male==is_chosen_female (HP3; halt if not).
- Do NOT add EUROMOD income, GSUR centring, or region precompute.

THEN STOP. Do not begin Stage 5.

Also GREP for downstream code that relies on a single-integer "draw" column
(==0 semantics) and LIST the re-pointing surface in the report — do NOT
change those sites in this slice.

Halt conditions: HP1, HP2, HP3, HP9, HP-STAGE (see amendment section 11).
If any fires, STOP, write the report to that point, await direction.

Write ONE report: Results/JMP_NC_pilot_stage1_4_build_report_v1.md, with the
contents required by amendment section 12. End with required final statements
(EUROMOD not run; M1-clean active; P3a unaffected; no welfare/SA2/promotion;
Stages 1-4 only).
```

Save the report as: `Results/JMP_NC_pilot_stage1_4_build_report_v1.md`

---

**Required final statements:**

- **This amendment authorizes Stages 1–4 only**, with a hard stop before
  EUROMOD. It changes execution scope, not the specification.
- **All spec-contract decisions carry forward unchanged** (W1 baseline,
  two-group comparison, calibrated `delta_occ*`, `occ_spec="fixed"`, common
  sigma, `draw_male`/`draw_female`/`draw_joint`, chosen at `draw_joint==0`).
- **Four resume confirmations are pre-decided here:** Mincer set = pooled
  2015–2017 with year controls (2016-only fallback flagged); draw method =
  Halton (PCG64 fallback), not Sobol; pilot paths = `scripts/pilot/` +
  `Data/pilot/nc_2016_couples/`; execution = staged (stop at Stage 4). The
  fifth (EUROMOD runner status) is deferred — it is what this slice stops
  before.
- **No production file, YAML, data parquet, or row guard is modified.**
- **M1-clean 2016 remains active; the corrected pooled P3a track is
  unaffected; no welfare, no SA2, no promotion.**

---

*Status: scope amendment v1 to the NC pilot spec contract. Authorizes Stages
1–4 (upstream of EUROMOD) under pilot-only paths and the §11 halts. Executes
nothing itself. Next document: the Stage 1–4 build report (§12). EUROMOD and
all downstream stages remain unauthorized.*
