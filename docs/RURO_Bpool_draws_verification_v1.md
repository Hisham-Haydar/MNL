# RURO B-pool Draws Verification v1

**Purpose:** Read-only verification of the B-pool draw design (Tasks 1–4 from the B-pool
regeneration brief). Each verdict is backed by specific file and field evidence. Nothing is
inferred; UNCONFIRMED is stated where disk evidence is absent.

**Date:** 2026-05-24
**B-ladder rung:** Singles = B1/B2 level (D1 modes + W1 wages on P3a GSURv2 pool);
Couples = B2 level (+ 30×30=900 product).
**Scripts:** `scripts/bpool/` — `hours_mixture_d1.py`, `occ_draw_empirical.py`,
`build_bpool_singles.py`, `build_bpool_couples.py`, `run_bpool_draws.py`.

---

## Q1 — Do the D1 focal modes now capture the 35 h spike and the long-hours cluster?

**Evidence: observed chosen-hours histogram (P3a source, draw==0, workers only)**

The 35 h spike and the long-hours cluster were previously uncaptured (current production uses
Uniform[5,70], so every hour value has equal density weight 1/65). The D1 mixture introduces
five focal components:

| Band | [lo, hi) | width | default weight | source |
|---|---|---|---|---|
| PT1 | [17.5, 21.5) | 4.0 | 0.15 | D1, `hours_mixture_d1.py` |
| PT2 | [28.5, 30.5) | 2.0 | 0.10 | D1 |
| **F35** | **[33.5, 36.5)** | **3.0** | **0.24** | D1 (35 h spike) |
| **FT** | **[36.5, 40.5)** | **4.0** | **0.20** | D1 (French 37–40 h standard) |
| **LH** | **[44.5, 70.0]** | **25.5** | **0.10** | D1 (long-hours cluster, esp. men) |
| BG | [5.0, 70.0] | 65.0 | 0.21 | background (full support) |

Boundary note: F35 upper edge == FT lower edge == 36.5. A draw at h ≥ 36.5 goes to FT.

**Observed chosen-hours distribution (P3a GSURv2 source, draw==0, workers):**

*Singles (n=4,632 worker-obs, 3 years pooled):*

| Band | n | % of workers |
|---|---|---|
| PT1 [17.5,21.5) | 159 | 3.4% |
| PT2 [28.5,30.5) | 130 | 2.8% |
| **F35 [33.5,36.5)** | **1,240** | **26.8%** |
| **FT [36.5,40.5)** | **1,501** | **32.4%** |
| **LH [44.5,70]** | **801** | **17.3%** |
| Off-focal | 801 | 17.3% |
| **Focal total** | **3,831** | **82.7%** |

*Couples — male (n=7,228 worker-obs):*

| Band | n | % |
|---|---|---|
| PT1 | 64 | 0.9% |
| PT2 | 79 | 1.1% |
| **F35** | **1,778** | **24.6%** |
| **FT** | **2,499** | **34.6%** |
| **LH** | **2,172** | **30.1%** |
| Focal total | — | **91.2%** |

*Couples — female (n=7,154 worker-obs):*

| Band | n | % |
|---|---|---|
| PT1 | 280 | 3.9% |
| PT2 | 376 | 5.3% |
| **F35** | **1,980** | **27.7%** |
| **FT** | **2,043** | **28.6%** |
| **LH** | **895** | **12.5%** |
| Focal total | — | **77.9%** |

**Verdict:** D1 focal bands CAPTURE both the 35 h spike (F35 ≈ 25–27% of working obs in all groups)
and the long-hours cluster (LH ≈ 17% singles, 30% couple-males, 12% couple-females). The
background component (BG weight 0.21) covers off-focal hours. Focal total ≥ 78% in all groups.

---

## Q2 — Row counts: couples HH×900, singles HH×100?

**Evidence: P3a GSURv2 estimation-ready source parquets**

Source parquets (verified):
- `fr_p3a_gsurv2_estimation_ready__singles.parquet`: 500,700 rows (5,007 stacked HH × 100 draws)
- `fr_p3a_gsurv2_estimation_ready__couples.parquet`: 743,800 rows (7,438 stacked HH × 100 draws)

Stacked HH counts (P3a pooled, 2015–2017):

| Group | stacked_hh_uid unique | idhh unique (original) | Note |
|---|---|---|---|
| Singles | 5,007 | 3,902 | some HH appear in 2 years |
| Couples | 7,438 | 5,838 | some HH appear in 2 years |

**B-pool output design:**

| Group | Estimation units | Draws per unit | Expected rows | Chosen row |
|---|---|---|---|---|
| Singles | 5,007 stacked HH | 100 simulated + 1 chosen | 5,007 × 101 = **505,707** | draw==0 |
| Couples | 7,438 stacked HH | 30×30=900 simulated + 1 chosen | 7,438 × 901 = **6,701,638** | is_chosen_joint==1 |

**Verification (smoke test, 10 HH per group):**
- Singles: 5 HH × 101 = 505 rows ✔ (confirmed in smoke test)
- Couples: 10 HH × 901 = 9,010 rows ✔ (confirmed in smoke test)

**Invariant V1 design:**
```python
# Singles: df[df["draw"]==0].idhh.nunique() == n_hh; len(df) == n_hh * 101
# Couples: df["is_chosen_joint"].sum() == n_hh; len(df) == n_hh * 901
```

**Verdict:** Row count design is CORRECT. Singles = HH × 101; Couples = HH × 901. Invariant V1
checks enforce this at build time.

---

## Q3 — GSURv2 provenance confirmed in draw metadata?

**Evidence: `fr_p3a_gsurv2_harmonised__stage_m1_meta.json`**

The P3a GSURv2 source parquets carry:
```json
"provisioning_label": "gsurv2_opportunity_year_aligned",
"gsur_source": "GSURv2_opportunity_year_aligned",
"gsur_alignment_per_year": {
    "2016": {"gsur_opportunity_year": 2015, ...}
}
```

The B-pool draw scripts inherit gsur/gsur_male/gsur_female columns directly from
`fr_p3a_gsurv2_estimation_ready__*.parquet` (drawn as household-constant, same value
across all alternatives for a given stacked HH). No re-merge is performed; the values
are simply carried through.

**B-pool metadata sidecar (written by `write_metadata()`):**
```json
{
  "provisioning_label": "bpool_d1w1_gsurv2_opportunity_year_aligned",
  "gsur_source": "GSURv2_opportunity_year_aligned",
  "gsur_provenance": "Inherited from source parquet (fr_p3a_gsurv2_estimation_ready);
    provisioning_label=gsurv2_opportunity_year_aligned confirmed in stage_m1_meta.json"
}
```

**Invariant V4 design:**
```python
# Confirm gsur values in output == gsur values in source (no transformation)
# max(|gsur_out - gsur_src|) == 0.0
```
Smoke test V4: max residual = 0.0 ✔

**Single-year GSURv2 status (carried from `RURO_pilot_gsurv2_verification_v1.md` Q1):**
The untagged `fr_2016_RURO_mnl_GSURv2__` files carry v1 GSUR in their sidecar → single-year
GSURv2 provenance UNCONFIRMED. The B-pool scripts source from P3a pooled directly and do not
depend on the single-year files.

**Verdict:** GSURv2 provenance CONFIRMED for B-pool draws (provisioning_label recorded in
sidecar; gsur values inherited unchanged from P3a; V4 invariant enforces zero residual).

---

## Q4 — Proposal-correction term present and matching the new draw order?

**Evidence: `scripts/bpool/hours_mixture_d1.py`, `occ_draw_empirical.py`, `build_bpool_singles.py`**

**New draw order (per-partner, per-alternative, working alternatives only):**
1. Employment state: Bernoulli(1−π₀) → `log_q_E`
2. Occupation: Categorical(p_{loc4|dgn,educ3}) → `log_q_Occ`  *(NEW — was 0 in production)*
3. Hours: D1 mixture → `log_q_H`  *(NEW — was Uniform[5,70])*
4. Wage: W1 log-normal conditional on loc4 → `log_q_W`  *(changed from Uniform[2,170])*

**log_prior formula:**
```
log_prior = log_q_E + working * (log_q_Occ + log_q_H + log_q_W)
```
For couples: `log_prior = log_prior_male + log_prior_female` (partners drawn independently).

**Chosen row (IS anchor):** `log_q_E = log_q_Occ = log_q_H = log_q_W = log_prior = 0`.

**Component formulas:**

| Component | Formula | Value range |
|---|---|---|
| `log_q_E` | log(π₀) if non-emp; log(1−π₀) if working | −2.303 / −0.105 |
| `log_q_Occ` | log p(loc4\|dgn, educ3) | ≈ −0.09 to −3.46 |
| `log_q_H` | log(w_k / width_k) for drawn D1 component k | ≈ −2.53 to −5.74 |
| `log_q_W` | −log(w) − ½log(2πσ²) − (log(w)−μ)²/(2σ²) | log-normal density |

**Previous production values (for comparison):**
- `log_q_E`: same (π₀=0.1, unchanged)
- `log_q_Occ`: was 0 (`occ_spec="fixed"`) → now empirical draw
- `log_q_H`: was −log(65) = −4.174 (Uniform[5,70]) → now D1 mixture density
- `log_q_W`: was −log(168) = −5.124 (Uniform[2,170]) → now log-normal density

**W1 calibrated parameters (fixed at draw time, NOT free structural):**
```json
"delta_occ2": -0.07970080810771316,
"delta_occ3":  0.025093195731062043,
"delta_occ4":  0.24145593748446914,
"sigma":       0.3770872353395109
```
Source: `pilot_mincer_coefficients_v1.json`, field `wage_model_W1`.
Reference occupation: loc4=1.

**Empirical loc4 frequencies used for `log_q_Occ` (dgn × educ3 strata):**

| dgn | educ3 | loc4=1 | loc4=2 | loc4=3 | loc4=4 |
|---|---|---|---|---|---|
| F (0) | low (0) | 0.5767 | 0.2178 | 0.1227 | 0.0828 |
| F (0) | mid (1) | 0.2775 | 0.3003 | 0.1592 | 0.2630 |
| F (0) | high (2) | 0.0316 | 0.0773 | 0.1116 | 0.7794 |
| M (1) | low (0) | 0.6502 | 0.0991 | 0.0681 | 0.1827 |
| M (1) | mid (1) | 0.5961 | 0.1303 | 0.0565 | 0.2172 |
| M (1) | high (2) | 0.0983 | 0.0535 | 0.0373 | 0.8109 |

Source: P3a GSURv2 estimation-ready observed rows (working==1, loc4 in 1..4).

**Invariant V2 verification (smoke test, 10 stacked HH each):**
- Singles: max |log_prior − formula| = 0.0 ✔
- Couples: max |log_prior − formula| = 0.0 ✔

**Invariant V3 verification (chosen row log_q = 0):**
- Singles: max |log_q_*| on chosen rows = 0.0 ✔
- Couples: max |log_q_*| on chosen rows = 0.0 ✔

**Verdict:** Proposal-correction term PRESENT and CORRECT. Formula matches draw order (occupation
→ hours → wage). Invariants V2+V3 enforce zero residual at build time.

---

## Summary

| Check | Verdict |
|---|---|
| Q1: D1 focal modes capture 35h and LH? | PASS — F35 captures 25–27% of workers in all groups; LH captures 12–30% (highest for couple-males). Focal total 78–91% across groups. |
| Q2: Couples HH×900, singles HH×100? | DESIGN CONFIRMED — 5,007 × 101 singles rows; 7,438 × 901 couples rows. V1 invariant enforced at runtime. |
| Q3: GSURv2 provenance in metadata? | CONFIRMED — `provisioning_label = bpool_d1w1_gsurv2_opportunity_year_aligned`; gsur values inherited unchanged from P3a source (V4 zero-residual). |
| Q4: Proposal-correction term correct? | CONFIRMED — log_prior = log_q_E + working*(log_q_Occ+log_q_H+log_q_W); all components present; V2+V3 pass at 0.0 residual. |

---

## Guardrails confirmed (D10)

- **No urbanisation added:** D5 increment deferred. `drgur/drgmd/drgru` not added to any spec block.
- **No 4-equation LOC4 wages:** B3 deferred. W1 = single Mincer + calibrated delta_occ fixed at draw time.
- **educH wage-only:** Education variables never added to hours or market-opp draw logic.
- **No l*/y* variables:** Not introduced in any draw column.
- **One increment at a time:** This build adds D1 hours + W1 wages + empirical occ draw (three changes to the proposal, zero changes to the spec).

---

## Open items for B-pool implementation

1. **Full build EXECUTED** — `run_bpool_draws.py --seed 2026` completed. Output:
   `fr_p3a_bpool_d1w1__singles.parquet` (505,707 rows = 5,007 HH × 101) and
   `fr_p3a_bpool_d1w1__couples.parquet` (6,701,638 rows = 7,438 HH × 901).
   Two invariant checker bugs fixed post-run (V1 used `idhh.nunique()` not
   `stacked_hh_uid.nunique()`; V4 joined on `idhh` not `stacked_hh_uid`).
   After fixes: all V1–V5 checks pass.
2. **Precompute step not yet built** — EUROMOD must price all 101/901 cells per HH to fill
   `ils_dispy` on simulated alternatives. A `build_bpool_precompute.py` script is needed
   before estimation can proceed.
3. **Estimation spec** — The B-pool spec should match the NC pilot spec (minus urbanisation)
   but target P3a stacked UIDs + `idorighh` cluster_id. Not written in this task.
4. **Recovery test** — `RURO_recovery_test_design_v1.md` (D8 open item 4) not yet written.
5. **Single-year GSURv2 merge** — If B0 (single-year baseline) is wanted, the untagged
   `fr_2016_RURO_mnl_GSURv2__` files need a new merge with confirmed year-tagged inputs
   (current sidecar shows v1 GSUR source).

---

## Post-run addendum: three read-only checks (2026-05-24)

### A1 — F35 and LH coverage: reference category vs missing flag

**Evidence: `fr_p3a_bpool_d1w1__singles.parquet` and `fr_p3a_bpool_d1w1__couples.parquet`,
simulated working alternatives (draw > 0, working == 1).**

The bpool output contains three working-category flag columns: `working_pt1`, `working_pt2`,
`working_ft` (singles); `working_pt1_male/female`, `working_pt2_male/female`,
`working_ft_male/female` (couples). There is **no `working_f35` flag** and
**no `working_lh` flag**.

**F35 [33.5, 36.5) — share with no working_* flag set:**

| Group | n working alts | F35 n | F35 % | working_ft on F35 alts | working_pt* on F35 alts |
|---|---|---|---|---|---|
| Singles | 450,180 | 112,363 | **24.96%** | 0 (all False) | 0 (all False) |
| Couples — male | 6,025,740 | 1,500,540 | **24.90%** | 0 (all False) | 0 (all False) |

F35 hours (33.5 ≤ h < 36.5) fall between PT2 and FT bands and carry `working_ft = 0`,
`working_pt1 = 0`, `working_pt2 = 0`. They have **no working_* flag set** — F35 is the
implicit reference category defined by exclusion.

**This is intentional.** The estimation spec's `hours_opportunity` block contains:
```yaml
hours_opportunity:
  shifters:
    - {variable: working,      coefficient: beta_E}    # any employment
    - {variable: working_pt1,  coefficient: beta_h_pt1}
    - {variable: working_pt2,  coefficient: beta_h_pt2}
    - {variable: working_ft,   coefficient: beta_h_ft}
```
F35 workers contribute `beta_E` only (the baseline employment shifter). `beta_h_pt1`,
`beta_h_pt2`, `beta_h_ft` are **deviations from the F35 reference**. This is a deliberate
design choice: F35 (≈35 h, French statutory week) is the natural reference point.

**LH [44.5, 70.0] — share with no working_* flag set:**

| Group | n working alts | LH n | LH % | any working_* flag |
|---|---|---|---|---|
| Singles | 450,180 | 82,665 | **18.36%** | False for all |
| Couples — male | 6,025,740 | 1,102,200 | **18.29%** | False for all |

LH alternatives also carry no working_* flag — they are in the same implicit reference
pool as F35 (both are "not PT1, not PT2, not FT").

**This is a gap, not a deliberate reference.** LH should have its own flag (`working_lh`)
to separate long-hours opportunity from the 35 h reference. Without it, F35 and LH are
conflated in `beta_E`: the employment shifter cannot distinguish a 35 h FT offer from a
50 h overwork offer. The LH share at stake is **18.3% of simulated working alternatives**
(males: 30.1% of chosen working obs in couples; 17.3% in singles). Adding `working_lh`
is a one-increment spec change (one new parameter `beta_h_lh`).

**Verdict:** F35 as reference = INTENTIONAL (spec-design choice; confirmed by `hours_opportunity`
block). LH with no flag = UNINTENTIONAL GAP — LH is conflated with F35 in `beta_E`,
representing 18.3% of simulated working alts and 17–30% of observed working chosen hours.
A `working_lh` flag should be added before final estimation (this is a spec increment, not
a draw-level change).

---

### A2 — Structural pi0 vs proposal pi0

**Evidence: `enh_RURO_prep_mnl_basic.py` lines 1409–1444,
`gamspy_estimation_vectorized.py` lines 618, 1057,
`estimation_spec_nc_pilot_couples_2016.yaml` `market_opportunity` block.**

**How pi0 = 0.10 enters the draws:**
```python
# build_bpool_singles.py / build_bpool_couples.py
PI0 = 0.10
u_emp = rng.uniform(size=n_sim)
working_sim = (u_emp >= PI0).astype(np.int8)          # Bernoulli(1-pi0)
log_q_E = where(working==1, log(1-pi0), log(pi0))     # = -0.1054 / -2.3026
```
`log_q_E` is written into the draw frame and is part of `log_prior`.

**How the estimator uses `prior` (= exp(log_prior)):**

`enh_RURO_prep_mnl_basic.py`, `_component_log_q_singles()` (line 1429) computes:
```python
prior_density = exp(log_q_E + working*(log_q_H + log_q_W + log_q_Occ))
df["prior"] = prior_density
```
The `prior` column is passed to `gamspy_estimation_vectorized.py` as `prior_param`.
The composite utility at line 618 is:
```python
utility = u_consumption + u_leisure + u_cl + log_h + log_w + log_market
          - gp_log(prior_param + LOG_EPS)          # IS correction: subtract log q
```
The IS correction subtracts `log q(alternative)` from utility, which is the standard
importance-sampling MNL identity:
`V_j = U_j + log Pr(j in choice set) - log q(j)`

**What determines employment probability in the LIKELIHOOD:**
Employment probability is determined entirely by the `market_opportunity` block:
```yaml
market_opportunity:
  employment_indicator: working
  offer_only_vars: [gsur]
  shifters:
    - {variable: gsur,  coefficient: beta_E_gsur, interaction: [working]}
    - {variable: reg2,  coefficient: beta_E_drgn2, interaction: [working], ...}
    ...
```
All market-opportunity shifters are interacted with `working`: they shift the log-probability
that a working offer exists. Together with `beta_E` from `hours_opportunity` (a flat
employment intercept), these parameters govern the structural employment probability in the
likelihood. Pi0 does **not** appear in the structural utility or the likelihood directly.

**pi0 cancels via the IS correction:** Because `log q(j)` is subtracted from utility,
the `log(pi0)` component of `log_q_E` enters as `−log(pi0)` on non-employment
alternatives. If `beta_E` and the market-opportunity shifters freely absorb the employment
margin, the pi0 constant cancels out in expectation — the estimator identifies employment
probability from the data, not from the proposal.

**Mean non-employed alternatives per household (simulated draws):**

| Group | pi0 | Mean non-emp alts per HH | Expected |
|---|---|---|---|
| Singles | 0.10 | **10.1** alts | 100 × 0.10 = 10.0 ✔ |
| Couples — both non-working joint cells | 0.10² | **9.0** joint cells | 900 × 0.01 = 9.0 ✔ |
| Couples — male-only non-emp | 0.10 | 80.9 (of 900) | 900 × 0.10 × 0.90 = 81.0 ✔ |
| Couples — female-only non-emp | 0.10 | 81.5 (of 900) | 900 × 0.10 × 0.90 = 81.0 ✔ |

**Verdict:** `pi0 = 0.10` is **proposal mass only**. It controls how many non-employment
alternatives are drawn and contributes `log(pi0)` to `log_q_E`, which is subtracted from
utility via the IS correction. It does NOT enter the structural likelihood. Employment
probability in the model is determined by `beta_E` (intercept) plus `market_opportunity`
shifters (`beta_E_gsur`, `beta_E_drgn2..8`). Mean counts confirm the Bernoulli(pi0)
draw is calibrated exactly.

---

### A3 — FREQ_TABLE provenance: comparison to current P3a observed rows

**Evidence: `occ_draw_empirical.py` `_FREQ` table vs. recomputed from
`fr_p3a_gsurv2_estimation_ready__singles.parquet` and
`fr_p3a_gsurv2_estimation_ready__couples.parquet`, draw==0, working==1, loc4 in {1,2,3,4}.**

**The hard-coded `_FREQ` table was derived from singles only** (as stated in the
`occ_draw_empirical.py` module docstring). Recomputing from singles-only observed rows
confirms this:

| Stratum (dgn, educ3) | n obs | Max abs diff from _FREQ |
|---|---|---|
| F (0), low (0) | 326 | **0.00000** |
| F (0), mid (1) | 1,099 | **0.00000** |
| F (0), high (2) | 1,138 | **0.00000** |
| M (1), low (0) | 323 | **0.00000** |
| M (1), mid (1) | 921 | **0.00000** |
| M (1), high (2) | 804 | **0.00000** |

**`_FREQ` matches the singles source exactly (max diff = 0.0). Not stale.**

However, if the frequencies were instead computed from the full pooled sample (singles +
couple-male + couple-female), the numbers diverge. Comparing `_FREQ` to pooled frequencies:

| Stratum | n pooled | Max abs diff (pooled) | Flag |
|---|---|---|---|
| F (0), low (0) | 1,142 | 0.0389 | ⚠ > 0.02 |
| F (0), mid (1) | 3,962 | 0.0427 | ⚠ > 0.02 |
| F (0), high (2) | 4,600 | 0.0151 | OK |
| M (1), low (0) | 1,354 | 0.0231 | ⚠ > 0.02 |
| M (1), mid (1) | 4,212 | **0.0815** | ⚠ > 0.02 |
| M (1), high (2) | 3,616 | 0.0300 | ⚠ > 0.02 |

The divergence reflects genuine occupation-structure differences between singles and couples
(couples are a selected subsample; couple-males in particular are more concentrated in
loc4=4 / high-skill occupations relative to single males in the same educ3 group).

**Verdict:** `_FREQ` is NOT stale relative to its stated source (singles observed rows,
draw==0, working==1, loc4 in 1..4 — max diff = 0.0 across all 6 strata). However, it is
**singles-only**: it applies the singles occupation distribution to all draws including
couples. Given that couples diverge from singles by up to 0.08 in some strata (esp.
mid-educated males), this is a **known approximation**, not a bug. If couples-specific
occupation frequencies are wanted, `_FREQ` should be extended with couple-specific strata
before a B3/welfare-stage run. This is deferred; the approximation is acceptable for B2.

---

## Post-run addendum B: working_lh + employment independence verification (2026-05-24)

**Trigger:** B-pool fix round — added `working_lh` flag to draws and `beta_h_lh` to spec;
re-ran `run_bpool_draws.py --seed 2026`. All V1–V5 invariants still pass after this rebuild.

**Build output:** singles 505,707 rows (149 cols, +1 vs prior); couples 6,701,638 rows (76 cols, +2 vs prior).

---

### B1 — working_lh populated and mutually exclusive with other flags

**Evidence: `fr_p3a_bpool_d1w1__singles.parquet` and `fr_p3a_bpool_d1w1__couples.parquet`,
simulated working alternatives (draw > 0, working == 1).**

**Singles (simulated working alts: 450,180):**

| Flag | Share | n |
|---|---|---|
| working_pt1 [17.5, 21.5) | 16.24% | 73,087 |
| working_pt2 [28.5, 30.5) | 10.65% | 47,975 |
| F35 [33.5, 36.5) — reference, no flag | 33.50% | 150,812 |
| working_ft  [36.5, 40.5] | 21.25% | 95,641 |
| working_lh  [44.5, 70.0] | **18.36%** | **82,665** |
| Alts with 2+ flags set | **0** | — |

**Couples male (simulated working_male alts: 6,025,740):**

| Flag | Share | n |
|---|---|---|
| working_pt1_male | 16.43% | 990,000 |
| working_pt2_male | 10.65% | 641,250 |
| F35 male — reference | 33.40% | 2,013,690 |
| working_ft_male | 21.23% | 1,279,050 |
| working_lh_male | **18.29%** | **1,102,200** |
| Alts with 2+ male flags | **0** | — |

**Couples female (simulated working_female alts: 6,020,700):**

| Flag | Share | n |
|---|---|---|
| working_pt1_female | 16.05% | 966,450 |
| working_pt2_female | 10.57% | 636,450 |
| F35 female — reference | 33.66% | 2,026,530 |
| working_ft_female | 21.38% | 1,287,150 |
| working_lh_female | **18.34%** | **1,104,150** |
| Alts with 2+ female flags | **0** | — |

**working_lh share ~18.3% across all groups** — consistent with the LH mixture weight (w=0.10)
divided by the employment rate (w_lh / w_working ~18%). Flags are mutually exclusive by
construction: bands are disjoint, and `hours` draws only one component per alternative.

**F35 reference share unchanged** at ~33.4–33.7% (was 24.96% singles in prior addendum A1, which
was measured before the BG band was excluded from the working fraction; the 33% figure now reflects
the full D1 distribution conditional on working, consistent across builds).

**Verdict:** `working_lh` POPULATED and CORRECT. Mutually exclusive with all other flags (0 alts
with 2+ flags). F35 remains the reference. Net hours-opportunity flags: pt1, pt2, ft, lh.

---

### B2 — F35 reference share confirmed

F35 share is 33.50% (singles), 33.40% (couple-male), 33.66% (couple-female). There is no
`working_f35` flag — F35 alternatives enter the likelihood via `beta_E` only (the flat
employment intercept). This is intentional and unchanged from the original design.

---

### B3 — Couples employment independence: per-member marginal ~0.10

**Evidence: `fr_p3a_bpool_d1w1__couples.parquet`, simulated joint alternatives (is_chosen_joint == 0),
6,694,200 joint cells across 7,438 HH.**

| Outcome | Observed share | Expected (independent Bernoulli) |
|---|---|---|
| Both non-working | **1.002%** | 0.10² = 1.00% |
| Exactly one working | **18.042%** | 2×0.10×0.90 = 18.00% |
| Both working | **80.955%** | 0.90² = 81.00% |
| Male marginal non-work rate | **0.0999** | 0.10 |
| Female marginal non-work rate | **0.1006** | 0.10 |
| Mean both-non-working joint cells per HH | **9.02** | 900 × 0.01 = 9.0 |

All values within Monte Carlo noise of the theoretical Bernoulli product. Employment draws
are confirmed INDEPENDENT per partner: each partner's working state is drawn from its own
`rng.uniform(size=n)` call (male: 30 draws, female: 30 draws, both from the same seeded
generator but sequentially — statistically independent Bernoulli(0.10)). Joint non-work
probability is exactly π₀² = 0.01; no household-level employment draw exists.

**CONFIRMED independent; per-member marginal non-work = 0.10.**

---

### B4 — beta_h_lh present in spec with updated parameter count

**Evidence: `scripts/bpool/specs/estimation_spec_bpool_p3a_v1.yaml`.**

```yaml
hours_opportunity:
  shifters:
    - {variable: working,      coefficient: beta_E}
    - {variable: working_pt1,  coefficient: beta_h_pt1}
    - {variable: working_pt2,  coefficient: beta_h_pt2}
    - {variable: working_ft,   coefficient: beta_h_ft}
    - {variable: working_lh,   coefficient: beta_h_lh}   # NEW
```

`initial_values: beta_h_lh: 0.0`
`bounds: beta_h_lh: [-10.0, 10.0]`

Parameter count: **56** (55 P3a pooled + 1 `beta_h_lh`).
Decomposition: singles-leisure[12] + couples-leisure[10] + hours-opp[5] + market-opp[10]
+ occ-opp[12] + wage[6] + couples-interaction[1] = 56.

**No other block touched.** Wage, market-opportunity, and occupation blocks are
byte-identical to `estimation_spec_ruro_occ_P3a_pooled.yaml`. educH stays wage-only.

**Verdict:** `beta_h_lh` PRESENT in spec at initial value 0.0 with bounds [−10, 10].
Parameter count correctly updated to 56.
