# RURO Welfare F5-R — Cross-Section Scope Reconciliation

Date: 2026-06-13 · spec_hash `492bcfa9c766bfcb` · theta_hash `1dd94e9cf1f35464` · reuses frozen F5 households (recomputation only).

Inequality recomputation only; no F6/decomposition/bootstrap/estimation/EUROMOD/commit. F5 calculations are valid; the PRIMARY cross-section label is a governance decision, left UNRATIFIED here.

## 1. Governance conflict

- **Decisions memo v2 §13**: Under a POOLED specification the PRIMARY baseline welfare distribution is option (b): the 2016 distribution computed from the pooled theta-hat but evaluated on the 2016 cross-section (l.584-586). Secondary sensitivities: (a) pooled across all years, (c) reweighted-2016. the certified baseline joint_pooled_v1_bll0_tlmpin IS a pooled specification, so the §13 pooled-case rule governs the primary scope. → primary = **2016 cross-section (year_tag==2)**.
- **Roadmap v1**: conference population = single-adult households in France 2015-2017 (l.14); status = planning memo, supersedes nothing, pre-registers framing (l.3). frames the narrative population but does NOT supersede the §13 primary-scope rule; it is a presentational/narrative framing, not a governance amendment.
- **Reconciliation**: the existing F5 pooled results remain VALID CALCULATIONS but cannot be silently labeled PRIMARY; under §13 the primary is the 2016 cross-section and pooled is sensitivity (a).
- Terminology: pooled sample = **5007 household-year observations**; original households/clusters = **3902 idorighh**; year_tag 1=2015, 2=2016, 3=2017; year obs counts {1: 1669, 2: 1676, 3: 1662}.
- 5007 household-year observations come from 3902 distinct original households (idorighh); households present in multiple years appear as multiple pooled observations.

## 2. Inequality by scope (weighted Gini, singles_all)

| scope | status | n | W1 | W4 | W6 | min→max | spread |
|---|---|---|---|---|---|---|---|
| primary_candidate_2016 | PRIMARY (UNRATIFIED) | 1676 | 0.1734 | 0.3288 | 0.3371 | W1→W6 | 0.1637 |
| pooled_sensitivity_2015_2017 | sensitivity | 5007 | 0.1648 | 0.3245 | 0.3314 | W1→W6 | 0.1666 |
| year_2015 | sensitivity | 1669 | 0.1573 | 0.3225 | 0.3270 | W1→W6 | 0.1697 |
| year_2016 | sensitivity | 1676 | 0.1734 | 0.3288 | 0.3371 | W1→W6 | 0.1637 |
| year_2017 | sensitivity | 1662 | 0.1625 | 0.3166 | 0.3245 | W1→W6 | 0.1619 |

By group (weighted Gini W1 / W4 / W6):

| scope | group | W1 | W4 | W6 | spread |
|---|---|---|---|---|---|
| primary_candidate_2016 | singles_all | 0.1734 | 0.3288 | 0.3371 | 0.1637 |
| primary_candidate_2016 | singles_male | 0.1665 | 0.3588 | 0.3590 | 0.1925 |
| primary_candidate_2016 | singles_female | 0.1768 | 0.2937 | 0.2957 | 0.1189 |
| pooled_sensitivity_2015_2017 | singles_all | 0.1648 | 0.3245 | 0.3314 | 0.1666 |
| pooled_sensitivity_2015_2017 | singles_male | 0.1654 | 0.3573 | 0.3572 | 0.1919 |
| pooled_sensitivity_2015_2017 | singles_female | 0.1624 | 0.2887 | 0.2899 | 0.1275 |
| year_2015 | singles_all | 0.1573 | 0.3225 | 0.3270 | 0.1697 |
| year_2015 | singles_male | 0.1638 | 0.3735 | 0.3733 | 0.2097 |
| year_2015 | singles_female | 0.1500 | 0.2688 | 0.2694 | 0.1195 |
| year_2016 | singles_all | 0.1734 | 0.3288 | 0.3371 | 0.1637 |
| year_2016 | singles_male | 0.1665 | 0.3588 | 0.3590 | 0.1925 |
| year_2016 | singles_female | 0.1768 | 0.2937 | 0.2957 | 0.1189 |
| year_2017 | singles_all | 0.1625 | 0.3166 | 0.3245 | 0.1619 |
| year_2017 | singles_male | 0.1649 | 0.3363 | 0.3360 | 0.1714 |
| year_2017 | singles_female | 0.1585 | 0.2926 | 0.2935 | 0.1350 |

Secondary indices, distribution summaries, and tail shares per scope×group×measure are in the F5R parquet.

## 3. Stability comparison (2016 vs pooled / other years)

- min-Gini measure is **W1 in every scope×group**: True.
- Full-compensation (W4/W6) Gini **exceeds W1 in every scope×group**: True.
- 2016-vs-other weighted-Gini differences (singles_all):

| measure | 2016 | pooled | Δ pooled | 2015 | Δ2015 | 2017 | Δ2017 |
|---|---|---|---|---|---|---|---|
| W1 | 0.1734 | 0.1648 | -0.0086 | 0.1573 | -0.0161 | 0.1625 | -0.0109 |
| W4 | 0.3288 | 0.3245 | -0.0043 | 0.3225 | -0.0063 | 0.3166 | -0.0122 |
| W6 | 0.3371 | 0.3314 | -0.0057 | 0.3270 | -0.0101 | 0.3245 | -0.0127 |

- Repeated original households: the pooled scope contains repeated original households (3,902 idorighh across 5,007 household-year obs); persistent households are counted once per year, so the pooled cross-section is NOT an independent-household distribution. This affects (i) the effective sample / weighting interpretation and (ii) any inference (handled by the idorighh cluster-bootstrap), but does NOT change the point-estimate calculations. The single-year 2016 scope avoids the repeated-household double-representation.

## 4. Recommendation (NOT ratified)

**Recommended: Option A.** RETAIN the decisions-memo §13 rule: 2016 cross-section (year_tag==2) PRIMARY, pooled 2015-2017 as the pre-registered sensitivity (a). Rationale: §13 is the standing ratified rule for the pooled-specification case (which the certified joint_pooled baseline is); the roadmap's 2015-2017 framing explicitly supersedes nothing and is a narrative/presentational frame served by REPORTING pooled alongside; and the 2016 single-year scope avoids the repeated-original-household double-representation present in the pooled cross-section. The qualitative conclusion (full-compensation inequality exceeds W1) and the min/max bracket measures are STABLE across 2016, pooled, and each year, so the choice is about labeling/primary-scope governance, not about which numbers are computed.

**Alternative B**: AMEND governance explicitly: pooled 2015-2017 PRIMARY, 2016 sensitivity. This requires an EXPLICIT supersession of decisions-memo §13 (the roadmap cannot do this implicitly), plus a decision on how repeated original households are represented in the primary pooled cross-section (count-per-year vs collapse-to-household vs reweight).

**Required operator sign-off**: explicit choice: (A) confirm 2016-primary per §13 [pooled = sensitivity], OR (B) ratify an explicit amendment of §13 to pooled-2015-2017-primary [2016 = sensitivity] together with the repeated-household representation rule. Until signed, PRIMARY CROSS-SECTION remains UNRATIFIED and F6 must not start.

## Outputs

- `C:\Users\hisham\Repo\MNL\outputs\welfare\fastlane\singles_measure_family_F5R_crosssection_v1.parquet` (sha256 `21a96b36d089854c1ed928fcfc2cb0afc7bde8aee53121191d6db60d2c1f35cd`)
- `F5R_crosssection_manifest_v1.json`; this report.

---

F5 CALCULATION STATUS: valid
PRIMARY CROSS-SECTION STATUS: UNRATIFIED
READY FOR F6 DESIGN MEMO: NO
REQUIRED NEXT INPUT: explicit 2016-primary or pooled-primary ratification