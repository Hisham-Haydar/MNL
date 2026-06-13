# RURO Welfare F5 — Singles Measure-Family Inequality Point Estimates

Date: 2026-06-13 · spec_hash `492bcfa9c766bfcb` · theta_hash `1dd94e9cf1f35464` · weight `dwt` · cluster `idorighh` · unit monthly real-2016 EUR (FR EUROMOD ils_dispy; build earnings use WEEKS_PER_MONTH=52/12 => monthly; c_scale≈2035 ≈ mean monthly disposable income)

**POINT ESTIMATES ONLY.** Conference-reportable claims require cluster-bootstrap re-estimation CIs (not run; see Inference status). Headline = survey-weighted Gini of W1/W4/W6. W3 = validation only; W1 working-only = appendix.

## Provenance & weight join (Task 0)

- F4C parquet sha256 match: True; F4C gates pass: True
- Joined households: **5007** (==5007: True); no missing/extra/dup: True; dwt finite>0: True; within-uid constant: True; group==dgn: True
- Overall: n=5007, Σdwt=14,813,218, unique idorighh=3902
- By group: singles_female n=2764 Σdwt=7,751,144 clusters=2164; singles_male n=2243 Σdwt=7,062,074 clusters=1738
- By year_tag: 1 n=1669 Σdwt=4,912,935; 2 n=1676 Σdwt=4,867,206; 3 n=1662 Σdwt=5,033,077

## Weighted-index primitives validated (Task 1)

- Gini vs O(n²) MAD oracle: 2.22e-16; integer-weight replication: 1.11e-16; weight-scale invariance: 4.44e-16; value-scale invariance: 4.44e-16; equal-values→0: 2.22e-16; non-positive fails clearly: True. ALL ≤1e-12: **True**

## Headline survey-weighted Gini (Task 2)

| scope | measure | n | Σweight | w-mean | w-median | **w-Gini** | unw-Gini | |Δ| |
|---|---|---|---|---|---|---|---|---|
| singles_all | W1 | 5007 | 14,813,218 | 1,784 | 1,654 | **0.1648** | 0.1712 | 0.0064 |
| singles_all | W4 | 5007 | 14,813,218 | 70,143 | 59,832 | **0.3245** | 0.3245 | 0.0001 |
| singles_all | W6 | 5007 | 14,813,218 | 84,170 | 71,202 | **0.3314** | 0.3319 | 0.0004 |
| singles_male | W1 | 2243 | 7,062,074 | 1,731 | 1,593 | **0.1654** | 0.1773 | 0.0119 |
| singles_male | W4 | 2243 | 7,062,074 | 65,953 | 52,859 | **0.3573** | 0.3610 | 0.0037 |
| singles_male | W6 | 2243 | 7,062,074 | 72,467 | 58,160 | **0.3572** | 0.3608 | 0.0036 |
| singles_female | W1 | 2764 | 7,751,144 | 1,833 | 1,713 | **0.1624** | 0.1646 | 0.0022 |
| singles_female | W4 | 2764 | 7,751,144 | 73,961 | 66,443 | **0.2887** | 0.2901 | 0.0014 |
| singles_female | W6 | 2764 | 7,751,144 | 94,833 | 84,996 | **0.2899** | 0.2924 | 0.0025 |

(Unweighted Gini is a labeled sensitivity, never the headline.)

## Across-measure Gini bracket / spread (Task 3)

| scope | min Gini (measure) | max Gini (measure) | bracket | abs spread |
|---|---|---|---|---|
| singles_all | 0.1648 (W1) | 0.3314 (W6) | [0.1648, 0.3314] | 0.1666 |
| singles_male | 0.1654 (W1) | 0.3573 (W4) | [0.1654, 0.3573] | 0.1919 |
| singles_female | 0.1624 (W1) | 0.2899 (W6) | [0.1624, 0.2899] | 0.1275 |

Pre-registered across-measure normative-sensitivity result. NOT a decomposition or opportunity share.

## Secondary weighted indices (Task 4)

| scope | measure | CV² | Theil L | Atkinson ε=1 | Atkinson ε=2 |
|---|---|---|---|---|---|
| singles_all | W1 | 0.2401 | 0.0484 | 0.0472 | 0.0813 |
| singles_all | W4 | 0.5139 | 0.1890 | 0.1722 | 0.3404 |
| singles_all | W6 | 0.5290 | 0.1962 | 0.1781 | 0.3512 |
| singles_male | W1 | 0.1589 | 0.0480 | 0.0469 | 0.0818 |
| singles_male | W4 | 0.6675 | 0.2245 | 0.2011 | 0.3762 |
| singles_male | W6 | 0.6667 | 0.2241 | 0.2007 | 0.3747 |
| singles_female | W1 | 0.3043 | 0.0479 | 0.0468 | 0.0795 |
| singles_female | W4 | 0.3942 | 0.1535 | 0.1423 | 0.2944 |
| singles_female | W6 | 0.4153 | 0.1537 | 0.1424 | 0.2918 |

Appendix — W1 working-only weighted Gini: singles_all 0.1576 (n=5007); singles_male 0.1556 (n=2243); singles_female 0.1585 (n=2764)

W3 validation readout (NOT headlined): max|Ω³| = 2.93e-10 (≤1e-8: True).

## Tail & stability diagnostics (Task 5)

| scope | measure | w-p99 | w-max | top-1% wt share | Gini winsor@p99 (sens.) |
|---|---|---|---|---|---|
| singles_all | W1 | 4,034 | 40,475 | 0.0371 | 0.1526 |
| singles_all | W4 | 246,741 | 964,992 | 0.0504 | 0.3141 |
| singles_all | W6 | 296,323 | 1,368,235 | 0.0495 | 0.3217 |
| singles_male | W1 | 4,527 | 15,160 | 0.0366 | 0.1566 |
| singles_male | W4 | 272,639 | 689,380 | 0.0580 | 0.3465 |
| singles_male | W6 | 296,914 | 761,824 | 0.0579 | 0.3462 |
| singles_female | W1 | 3,835 | 40,475 | 0.0372 | 0.1486 |
| singles_female | W4 | 231,650 | 964,992 | 0.0427 | 0.2806 |
| singles_female | W6 | 295,817 | 1,368,235 | 0.0437 | 0.2809 |

Rank correlations (Spearman) among headline measures:
- singles_all: W1–W4 0.480, W1–W6 0.489, W4–W6 0.986
- singles_male: W1–W4 0.512, W1–W6 0.514, W4–W6 1.000
- singles_female: W1–W4 0.438, W1–W6 0.462, W4–W6 0.992

Winsorized results are sensitivity only and do not replace the primary unwinsorized Gini. W4/W6 are full-compensation measures with large levels (F4C caveat retained).

## Inference status (Task 6) — NO bootstrap run

- Cluster key: **idorighh**; clusters overall **3902** (by group {'singles_female': 2164, 'singles_male': 1738}); multi-pooled-year clusters 1105.
- Required: cluster-bootstrap re-estimation: resample idorighh clusters, RE-ESTIMATE theta per replicate, then recompute F4C measures; fixed-theta household resampling alone is NOT the pre-registered inference and cannot produce final headline CIs.
- Required replicates (scaffold): **200**.
- Fixed-theta household resampling alone is **not** the pre-registered inference and cannot produce final headline CIs.

## Outputs

- `C:\Users\hisham\Repo\MNL\outputs\welfare\fastlane\singles_measure_family_F5_v1.parquet` (sha256 `c9d2a3af4cd96aa53b1bc975986fd8c784eb64816d6b7d29e3ec3e8dbe5bc018`)
- `C:\Users\hisham\Repo\MNL\outputs\welfare\fastlane\singles_measure_family_F5_households_v1.parquet` (sha256 `5dce9d9d836d90101aa89771badf1742238431b6a86ad41d2f7412ac4127872f`)
- `F5_manifest_v1.json`; this report.

---

F5 POINT-ESTIMATE STATUS: valid
ACROSS-MEASURE SPREAD STATUS: valid
READY FOR F6 DESIGN MEMO: yes
CONFERENCE-REPORTABLE WITH CI: NO — cluster-bootstrap re-estimation pending