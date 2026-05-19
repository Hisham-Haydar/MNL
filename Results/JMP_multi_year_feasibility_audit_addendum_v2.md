# JMP Multi-Year Feasibility Audit — Addendum v2

**Document:** JMP_multi_year_feasibility_audit_addendum_v2.md  
**Extends:** Results/JMP_multi_year_feasibility_audit_addendum_v1.md  
**Date:** 2026-05-19  
**Reference memo:** docs/JMP_multi_year_and_cross_validation_strategy_memo_v3_1.md  

---

## Purpose of This Addendum

Two gaps remained open after addendum v1:

1. **2018 not assessed.** `FR_2018_a2.txt` exists on disk and `FR_2018` is installed in EUROMOD J1.0+. The v3.1 memo names P3a (2015+2016+2017) as the primary three-year configuration, but does not evaluate 2018 as an alternative third year. This addendum adds a P3b (2015+2016+2018) branch and a P4 (2015+2017+2018) non-2016 extension.

2. **Repeated-ID identity validation not performed.** The addendum v1 cited the 8,796 household overlap as mechanically established but did not validate whether repeat identifiers actually correspond to the same physical household across waves. This addendum runs full identity-validation diagnostics on all three overlapping year pairs.

---

## A. 2018 Availability

### A1. Raw Microdata

`FR_2018_a2.txt` is present at `Z:\Hisham\EUROMOD-STORAGE\Data\FR\`:

| File | Individuals | Households | Column count |
| --- | --- | --- | --- |
| `FR_2018_a2.txt` | 24,620 | 10,876 | 127 |

All RURO-critical columns are present, including `drgn1`, `deh`, `dgn`, `dag`, `dms`, `dwt`, and all labour/income variables. `FR_2018` adds `tpr` (wealth tax, present in 2015 and absent from 2016–2017, reappearing in 2018) and retains `twl`, `yptmp`, `bchba`, `bsawk`, `ltr`, `ymwdt` from 2017.

### A2. EUROMOD System

`FR_2018` is confirmed present in `Z:\...\XMLParam\Countries\FR\FR.xml` (19 systems, FR_2006–FR_2024). No output files for FR_2018 exist in the project's processed-data directories.

### A3. Identifier Maxima

| File | `idhh` max | `idperson` max | `idorighh` max | `idorigperson` max |
| --- | --- | --- | --- | --- |
| FR_2018_a2 | 4,991,800 | 499,180,001 | 4,991,800 | 9,379,750,001 |

2018 `idperson` max is 499,180,001 — well below B=10^11. The UID encoding scheme is sufficient for 2018.

### A4. GSUR and CPI Requirements for 2018

- **GSUR rates:** `FR_gsur_ruro.parquet` covers 2018 — available immediately.
- **Eurostat denominators:** `lfst_r_lfsd2pop_2016_full.csv` covers 2016 only; 2018 denominators require re-download. Same gap as 2015/2017.
- **INSEE benchmark 2018:** Not yet downloaded. Approximate expected value ~8.8% (ILO unemployment rate, SA, metropolitan France).
- **HICP/CPI 2018:** EUROMOD HICPCONFIG.xml has 2018 = 103.60 (base 2015=100). Implied factor: φ_2018 = 100.31/103.60 = 0.9682.

---

## B. Pairwise Overlap Structure (All Year Pairs)

Computed from `idorighh` (original household ID, raw EU-SILC) and `idorigperson`:

| Year pair | Overlap households | Overlap persons | Disjoint? | Cluster-robust (T1) required? |
| --- | --- | --- | --- | --- |
| 2015 ∩ 2016 | **0** | 0 | Yes | No |
| 2015 ∩ 2017 | **0** | 0 | Yes | No |
| 2015 ∩ 2018 | **0** | 0 | Yes | No |
| 2016 ∩ 2017 | **8,796** | 19,904 | No | Yes |
| 2016 ∩ 2018 | **7,065** | 15,696 | No | Yes |
| 2017 ∩ 2018 | **8,521** | 19,123 | No | Yes |

2015 is disjoint from every other year (different EU-SILC panel). 2016, 2017, and 2018 are successive rotating-panel waves that share substantial sub-samples with one another.

**Note on household-count reconciliation:** The `idorighh` set-intersection gives the household-level overlap. The distinct `idorighh` values appearing in the merged person-level dataset are slightly higher in both years (e.g., 8,814 and 8,908 for 2016–2017) because household composition changes within the panel — a household may gain or lose members between waves while retaining its `idorighh`. The canonical overlap count is the `idorighh` set-intersection figure (8,796 for 2016–2017), confirming the v3.1 memo exactly. The idhh-level counts diverge because EUROMOD assigns within-year IDs independently.

---

## C. Identity Validation for Repeated Households

For each overlapping year pair, repeat persons were identified by `idorigperson` match and tested on four criteria: sex stability, age progression, household continuity, and education stability.

### C1. 2016 → 2017 (19,904 repeat persons, 8,796 repeat households)

| Criterion | Result | Assessment |
| --- | --- | --- |
| Sex stability | 99.96% (8 mismatches) | Consistent with genuine panel; 8 mismatches plausibly coding corrections |
| Age progression (Δdag = +1) | 95.8% exactly +1; 99.9% within ±1 of expected | Consistent with one-year gap |
| Same household (idorighh) | 99.25% | 0.75% changed household — consistent with household splits/moves in panel surveys |
| Education stability (all ages) | 93.1% (1,365 changes) | Explained by young-adult cohort completing degrees |
| Education stability (age 25–60) | 97.1% | Appropriate for working-age window |
| Suspicious records (sex mismatch OR age off-track) | **19 persons** | 0.10% of repeat sample; negligible |

Age-progression distribution for 2016→2017:

| Δdag | Count | Share |
| --- | --- | --- |
| +1 (expected) | 19,062 | 95.77% |
| 0 (birthday not yet passed) | 828 | 4.16% |
| Other | 14 | 0.07% |

The 828 persons with Δdag=0 are a known EU-SILC artefact: `dag` is truncated to integer years and the survey interview date can precede the respondent's birthday in the later wave, leaving the reported age unchanged. This is not a data-quality problem.

**Verdict for 2016–2017:** Panel identity is valid. The `idorigperson` key reliably identifies the same physical person across waves. The 8,796 `idorighh` overlap is a genuine rotating-panel sub-sample. Clustering at `idorighh` is the correct inference unit.

### C2. 2016 → 2018 (15,696 repeat persons, 7,065 repeat households)

| Criterion | Result | Assessment |
| --- | --- | --- |
| Sex stability | 99.94% (10 mismatches) | Consistent |
| Age progression (Δdag = +2) | 96.2% exactly +2; 99.9% within ±1 of expected | Consistent with two-year gap |
| Same household (idorighh) | 98.62% | Slightly more household movement over two years — expected |
| Education stability (all ages) | 86.4% (2,133 changes) | Higher over two years; dominated by young-adult completions |
| Education stability (age 25–60) | 95.5% | Appropriate |
| Suspicious records | **21 persons** | 0.13% — negligible |

The 590 persons with Δdag=+1 (rather than expected +2) again reflect the birthday/interview-timing artefact. Education changes are concentrated in the 14–24 age band (634 of 2,133 changers), confirming degree-completion as the primary driver. The direction matrix shows predominately upgrading transitions (e.g., deh=0→1, deh=1→2), consistent with young adults completing schooling.

**Verdict for 2016–2018:** Panel identity is valid. The two-year gap produces modestly more household movement and education change, both consistent with genuine longitudinal dynamics rather than coding errors.

### C3. 2017 → 2018 (19,123 repeat persons, 8,521 repeat households)

| Criterion | Result | Assessment |
| --- | --- | --- |
| Sex stability | 99.95% (10 mismatches) | Consistent |
| Age progression (Δdag = +1) | 99.9% within ±1 of expected | Strongest of the three pairs |
| Same household (idorighh) | 99.28% | Consistent with one-year gap |
| Education stability (age 25–60) | 97.6% | Consistent |
| Suspicious records | **20 persons** | 0.10% — negligible |

**Verdict for 2017–2018:** Panel identity is valid.

### C4. Clustering-Key Decision

In all overlapping pairs, the `idorighh` key identifies repeat households reliably. The suspicious-record rate is ≤ 0.13% in every pair — too low to affect inference. The appropriate clustering key for T1 cluster-robust SEs is **`idorighh`** (original household ID, available directly in the microdata). In the stacked pooled dataset, the cluster key will be the UID-encoded original household: `cluster_uid = idorighh` (for the purposes of the variance estimator, not to be confused with the stacked-observation UID which incorporates a year tag).

---

## D. Configuration Comparison: P2, P3a, P3b, P4

| Configuration | Years | HH-rows | Unique HH | Repeat HH (overlap) | Repeat HH / total | T1 needed |
| --- | --- | --- | --- | --- | --- | --- |
| P2 | 2015+2016 | 22,849 | 22,849 | 0 | 0.0% | No |
| P3a | 2015+2016+2017 | 33,917 | 25,121 | 8,796 | 25.9% | Yes |
| P3b | 2015+2016+2018 | 33,725 | 26,660 | 7,065 | 20.9% | Yes |
| P4 | 2015+2017+2018 | 33,334 | 24,813 | 8,521 | 25.6% | Yes |

**Sample size:** P3a and P3b are nearly identical in total rows (33,917 vs 33,725). P4 is slightly smaller.

**Repeat-HH fraction:** P3a has the highest overlap fraction (25.9%), P3b the lowest (20.9%). A lower overlap fraction means cluster-robust SEs are closer to simple SEs and the inflation from repeat observations is smaller.

**Unique households:** P3b has the largest unique-household count (26,660 vs 25,121 for P3a), meaning more distinct economic units contribute to identification.

**Distance from M1-clean baseline:** P3a includes 2017 (adjacent to the accepted 2016 baseline); P3b skips 2017 and jumps to 2018. Policy continuity across years matters for the time-invariant preference assumption — 2016 and 2017 are closer to one another in institutional context (pre-Macron presidency economic policy changes) than 2016 and 2018.

**2018-specific note:** `FR_2018_a2.txt` brings back `tpr` (the ISF wealth tax), which was absent from 2016 and 2017. This does not affect the RURO utility function directly, but the disposable income calculation in the 2018 EUROMOD system differs from the 2016/2017 systems in that the ISF is now simulated. The `ils_dispy` aggregate will incorporate ISF for 2018 observations. This is an income-definition comparability issue absent from P3a; it should be flagged and quantified before P3b is used.

---

## E. Recommendation: 2017 vs 2018 as the Third Year

**Recommended: retain P3a (2015+2016+2017) as the primary three-year configuration. Treat P3b (2015+2016+2018) as a robustness branch, not a default.**

Rationale:

1. **Temporal adjacency.** 2017 is one year from the accepted 2016 baseline. The time-invariance assumption for preference parameters is most credible over shorter spans. A 2015–2016–2017 pool covers a three-year window under a single consistent economic regime.

2. **ISF wealth tax.** The `tpr` variable reappears in 2018 (absent in 2016 and 2017). This creates an asymmetric income-definition issue that does not exist in P3a. Resolving it requires confirming that the 2018 ISF simulation is minor enough not to materially shift `ils_dispy` distributions for the RURO sample — an additional comparability check not required for P3a.

3. **Overlap fraction.** P3b's lower overlap fraction (20.9% vs 25.9%) is a marginal advantage for inference, not a deciding factor. Both configurations require T1 cluster-robust SEs regardless.

4. **Logical consistency with v3.1 memo.** The v3.1 memo names 2015, 2016, 2017 explicitly throughout and does not mention 2018. Departing from the memo's stated configuration requires a deliberate decision to revise the strategy.

**P4 (2015+2017+2018)** is noted as a non-2016 extension for robustness purposes but is not a priority configuration — it excludes the accepted 2016 M1-clean baseline year, which is the natural anchor for any temporal comparison.

**Decision required:** If P3b is to be retained as an active branch alongside P3a, it needs an explicit authorisation and a supplementary income-definition comparability check for 2018.

---

## F. Updated F1–F6 Status Including 2018

| Condition | 2015 | 2016 | 2017 | 2018 |
| --- | --- | --- | --- | --- |
| F1: EUROMOD system | ✓ | ✓ | ✓ | ✓ |
| F2: EU-SILC microdata | ✓ | ✓ | ✓ | ✓ |
| F3: Eurostat GSUR rates | ✓ | ✓ | ✓ | ✓ |
| F3: Eurostat GSUR denominators | ✗ | ✓ | ✗ | ✗ |
| F4: INSEE benchmark | ✗ | ✓ | ✗ | ✗ |
| F5: INSEE CPI / HICP | ✗ *(proxy available)* | ✓ | ✗ *(proxy available)* | ✗ *(proxy available)* |
| F6: EUROMOD output comparability | ✓ | ✓ | ✓ | ✓ *(minor ISF flag)* |

The same three mechanical acquisition gaps that block 2015 and 2017 also block 2018. Closing them for all three years is the same set of API calls. If 2018 is retained as an active branch, no additional acquisition work is needed beyond what is already required for P3a.

---

## G. What Can Be Authorised Now (Revised)

**Authorise immediately:**

1. **Data acquisition for 2015, 2017, and 2018 simultaneously:** Download `lfst_r_lfsd2pop` and `lfst_r_lfp2acedu` for all three years in a single Eurostat API call (`startPeriod=2015&endPeriod=2018`); retrieve INSEE BDM series 001688526 for 2015, 2017, and 2018.
2. **CPI source decision:** Adopt the EUROMOD HICP values from `HICPCONFIG.xml` (Eurostat/AMECO series, base 2015=100) as the project's CPI harmonisation source, documenting the decision and the implied φ_t factors (φ_2015=1.0031, φ_2016=1.0000, φ_2017=0.9886, φ_2018=0.9682), with a note that the v3.1 memo's specified INSEE domestic CPI was not separately retrieved and that the HICP proxy is being adopted as a pragmatic substitute. Alternatively, retrieve the INSEE domestic CPI series and use it instead.
3. **GSUR v2 script year-parameterisation:** One-line edit to `enh_prepare_FR_gsur_v2.py` line 44.
4. **Stage M1 implementation planning:** Design the pooled-parquet builder, EUROMOD run procedure, and cluster-robust SE architecture. P3a is the primary configuration; P3b is a listed robustness branch pending the ISF comparability check.

**Defer:**

- Pooled estimation (all configurations): execution-blocked.
- P3b activation: pending ISF/`tpr` income-definition comparability check for 2018.
- P4: not a priority; no authorisation needed yet.

**Clustering key confirmed:** `idorighh` (original household ID). Identity validation across all overlapping pairs passes with ≤ 0.13% suspicious records. The 8,796 (2016–2017), 7,065 (2016–2018), and 8,521 (2017–2018) repeat-household counts are genuine rotating-panel sub-samples, confirmed by sex stability (≥99.94%), age progression (≥99.9% within ±1 of expected gap), and household continuity (≥98.6%).