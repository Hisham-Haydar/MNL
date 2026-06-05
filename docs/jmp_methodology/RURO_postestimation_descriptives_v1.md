# RURO Post-estimation descriptives — Stage Five, Increment Five-A

**Date:** 2026-06-04
**Increment:** STAGE FIVE, INCREMENT FIVE-A only — descriptive statistics, opportunity-set
readout, certified-estimate diagnostics, and a self-contained post-estimation HTML, all from the
**certified** baseline `joint_pooled_v1_bll0_tlmpin`.
**Status:** complete. **READ-ONLY at certified `theta_hat`. This is descriptive / estimator
diagnostics — NOT a welfare result.**

> **No re-estimation; no `V_i^dir`; no pricing; no `W^3` or any welfare measure / reportable
> inequality number; no specification change; no production swap; no canonical promotion.** All
> outputs are written under `outputs/` and `docs/`; the certified theta, engine-ready data, and
> staged/production artifacts are untouched. The full companion is the HTML report
> `RURO_postestimation_descriptives_v1.html`. Not committed automatically.

**Inputs (certified, from `welfare.baseline`):** theta `theta_hat_realdata_901_v1.csv` (47 free
params); spec `estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml`; engine-ready stem
`fr_p3a_bpool_engine_ready` (singles 101 alts, couples 901). Population: **12,445 households**
(singles_male 2,243 + singles_female 2,764 + couples 7,438).

---

## Task 1 — estimate summary and SE asymmetry (descriptive)

All 47 free parameters tabulated by block (full table in the HTML), each with value, Hessian SE,
clustered SE, t = value/`se_clustered`, |t|>1.96 significance, and bound/fixed status (the fixed
`theta_l_m = −0.8` and removed `beta_ll = 0` are appended as pinned rows). **The documented SE
asymmetry holds — the opportunity/access block is tight, the preference/leisure blocks are
wide:**

| block | role | median clustered SE | significant (|t|>1.96) |
|---|---|---|---|
| wage (`beta_w*`, `sigma`) | ability/wage | **0.012** | 6 |
| occupation (`beta_occ_*`) | opportunity/access | **0.047** | 5 |
| market + hours (`beta_E*`, `beta_h_*`) | opportunity/access | **0.124** | 9 |
| singles leisure | preference | **0.387** | 6 |
| couples leisure | preference | **0.394** | 3 |

The wage/opportunity/access SEs are **~3–30× tighter** than the preference/leisure SEs — the
"opportunity is sharply identified, preferences/leisure are weakly curved" feature carried from
the certified recovery gate. Figure: `stage5a_task1_se_asymmetry.png`.

---

## Task 2 — pure opportunity-set readout (g_hat only)

For each household, the **pure opportunity density** at certified θ is the opportunity block
`g_block = log_h + log_w + log_market` per alternative (it **excludes** utility `u` AND the
proposal `−log_prior`; verified as the exact residual `g_block = V_full − u + log_prior` to
machine precision, ~1e-15). Per-household weights and summaries (formulas stated):

- `p_g(j) = softmax(g_block)_j`;  opportunity entropy `H = −Σ_j p_g(j) log p_g(j)`;
- effective opportunity count `= exp(H)`;  ESS-style count `= 1 / Σ_j p_g(j)²`;  max weight;
- support size 101 (singles) / 901 (couples).

**Singles and couples reported separately (NOT pooled).** Median effective opportunity count:

| group | support | median opp. effective count | median opp. ESS count |
|---|---|---|---|
| singles_male | 101 | 12.8 | (parquet) |
| singles_female | 101 | 13.9 | (parquet) |
| couples | 901 | 17.7 | (parquet) |

So the typical household's opportunity mass concentrates on ≈ 13–18 effective alternatives out of
its 101 / 901 support. Per-household series → `outputs/opportunity_diagnostics_certified_v1.parquet`
(one row per HH). Figure: `stage5a_task2_opportunity_effcount.png`.

---

## Task 3 — utility-weighted attractiveness diagnostic (NOT opportunity-set size)

Separately, the **choice-attractiveness / likelihood-weighted** distribution uses the full
certified `V = u + log ĝ − log π`: `p_V(j) = softmax(V_full)_j`, with the same entropy /
effective-count / max-weight summaries. **This is labelled an attractiveness diagnostic, NOT pure
opportunity-set size.**

| group | median attractiveness effective count | median (attractiveness ÷ opportunity) ratio |
|---|---|---|
| singles_male | 38.8 | **2.98** |
| singles_female | 36.6 | **2.59** |
| couples | 167.3 | **9.07** |

The attractiveness effective count is **larger** than the pure-opportunity count (ratio > 1
everywhere) — at the certified preferences, the household's *attractive* mass spreads across more
alternatives than the raw opportunity density alone, most strongly for couples (901-alt support,
ratio ≈ 9). Figure: `stage5a_task3_attractiveness_vs_opportunity.png`.

---

## Task 4 — opportunity heterogeneity by location / education / local variables

Pure-opportunity and utility-weighted effective counts cross-tabbed by region (`drgn1`/`reg*`),
education (`educ3`), gender/mode, and local-condition variables (`gsur`, `drgur`, `drgmd`), read
from the HH-constant engine-ready covariates (chosen row per HH). Figure:
`stage5a_task4_heterogeneity_region.png`; full cross-tabs in the HTML.

**Absent variable (reported, not imputed):** `couples:gsur` — the couples engine-ready `gsur`
join is missing/NaN at the chosen row, so couples GSUR heterogeneity is omitted (not imputed or
merged). All other covariates (region, `educ3`/`educ3_male`/`educ3_female`, `drgur`, `drgmd`,
singles `gsur`) are present.

---

## Task 5 — wage / hours / LOC4 opportunity structure (plain statement)

**What the certified baseline implements for LOC4 (stated plainly): ONE log-wage density with
occupation MEAN shifts and a COMMON sigma — NOT four distinct densities.** From the spec:
`wage_opportunity` is a single log-normal with mean shifters
(`beta_w0, beta_w_educL, beta_w_educH, beta_w_pexp, beta_w_pexp2`) and **one** variance parameter
`sigma`; occupation enters *separately* (the opportunity/access block, `beta_occ_2/3/4_{m,f}`) as
a **mean shift** on `loc4`. So LOC4 acts purely as a mean shift on the single shared log-wage
density with common σ.

The implied LOC4-conditional wage densities are plotted as **four curves sharing σ with means
shifted by `beta_occ_*`** (`stage5a_task5_loc4_wage_densities.png`) so the one-density-vs-four
question is visible. Hours/employment/occupation opportunity summaries (hours-band offsets
`beta_h_pt1/pt2/ft/lh`) are plotted at the certified support
(`stage5a_task5_hours_offsets.png`). **No spec change.**

---

## Task 6 — ESS distributions (estimator diagnostics, not welfare)

Importance-sampling `ESS_i = 1 / Σ_j ω_ij²` from the certified likelihood machinery, plotted
**separately** for singles_male / singles_female / couples (and by year/mode in the HTML).
**Labelled estimator diagnostics, NOT welfare results.** Figure: `stage5a_task6_ess.png`.

---

## Task 7 — post-estimation HTML

`docs/jmp_methodology/RURO_postestimation_descriptives_v1.html` — self-contained (base64-embedded
PNGs) — embeds the estimate/SE tables, the SE-asymmetry figure, the pure opportunity-set-size
distributions, the utility-weighted attractiveness diagnostics, the by-region / by-education /
local-condition plots, the wage-by-LOC4 and hours figures, and the ESS distributions. **Every
figure caption carries "descriptive at certified theta; not welfare; not re-estimation."**

---

## Files

- **Driver:** `scripts/diagnostics/run_stage5a_postestimation_descriptives.py` (read-only; reuses
  the certified `welfare_core._build_V_extractor` + ESS machinery; the pure-opportunity block is
  the exact residual `V_full − u + log_prior`). Ruff-clean; config-driven; `--n-hh 0` = all HH.
- **HTML:** `docs/jmp_methodology/RURO_postestimation_descriptives_v1.html`.
- **Figures:** `outputs/figures/stage5a_*.png` (7).
- **Per-household opportunity diagnostics:** `outputs/opportunity_diagnostics_certified_v1.parquet`
  (12,445 rows; opportunity + attractiveness entropy / effective count / ESS count / max weight,
  by group).
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage5a_postestimation_descriptives.json`
  (per-task summaries, scope flags, absent-variable list, g_block construction).
- **Unchanged:** certified theta, engine-ready data, staged reference, production priced files.

## Explicit scope statement

Read-only at certified `theta_hat`. No re-estimation; no `V_i^dir`; no welfare; no `W^3`; no
measure / reportable inequality number; no pricing; no spec change; no production swap; no
canonical promotion. Absent variables are reported (`couples:gsur`), not imputed. This is a
descriptive / estimator-diagnostic increment, not a welfare result.
