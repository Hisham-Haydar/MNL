# RURO B-pool Precompute Gate v1

**Purpose:** Read-only gate before EUROMOD precompute. Verifies that the alternative-expanded
individual-level long file fed to EUROMOD will be a strict superset of the original EUROMOD input
schema. Defines pass/fail criteria and schema requirements for `build_bpool_precompute.py`.

**Date:** 2026-05-24
**Status:** BUILT AND GATE PASSED — 2026-05-26.
`build_bpool_precompute.py` written and executed. All 6 per-year long files produced.
All 54 gate checks (9 × 6 files) PASS. Files are EUROMOD-ready.

**Verdict: GATE PASSED — all checks PASS. Long files cleared for EUROMOD run.**

**Change nothing. Report only.**

---

## 1. Raw EUROMOD input column sets

The P3a pool uses three raw EUROMOD input files located in `U:/EUROMOD-STORAGE/Data/FR/`:

| File | Columns | Notes |
|---|---|---|
| `FR_2015_a2.txt` | **122** | Tab-separated, header row |
| `FR_2016_a3.txt` | **124** | Adds `dmb`, `twl`, `yptmp` vs 2015 |
| `FR_2017_a2.txt` | **128** | Adds `bchba`, `bsawk`, `ltr`, `ymwdt`, `yptmp`, `twl`, `dmb` vs 2015 |

**Union across all three years: 129 unique column names.**
**Intersection (common to all three): 121 columns.**

Cross-year differences (not bugs — each year uses its own EUROMOD system):

| Column | Present in | Absent from | Nature |
|---|---|---|---|
| `tpr` | 2015 | 2016, 2017 | Tax/transfer item dropped in later system versions |
| `dmb` | 2016, 2017 | 2015 | Social policy instrument added from 2016 |
| `twl` | 2016, 2017 | 2015 | Work–life balance benefit introduced 2016 |
| `yptmp` | 2016, 2017 | 2015 | Temporary employment income component |
| `bchba` | 2017 only | 2015, 2016 | Child benefit variant 2017+ |
| `bsawk` | 2017 only | 2015, 2016 | Short-time work benefit 2017+ |
| `ltr` | 2017 only | 2015, 2016 | Labour transition indicator |
| `ymwdt` | 2017 only | 2015, 2016 | Monthly income item 2017+ |

**Policy:** The precompute long file must contain all columns required by each year's
EUROMOD system. The file is year-tagged (`data_year` / `year_tag`); EUROMOD will be run
per year using the year-appropriate system. Missing columns for a given year = HARD STOP.

### Complete union column list (129 columns — all must be present in long file per year)

```
aca  aco  afc  amrrm  amrtn  ate
bch00  bchba  bchcc  bched  bchlg  bchot  bchyc
bdi  bed  bfa  bhl  bho  bhoot  bhotn
bsa  bsa00  bsaoa  bsaot  bsawk  bsuwd
bun  bunct  bunmt  bunmy
dag  dct  dcu  dcz  ddi  ddt  dec  decde  deh  dehde  dew  dey  dgn  dmb  dms  dncsy
drg01  drgmd  drgn1  drgn2  drgru  drgur
dsu00  dsu01  dsu02  dwt
e20ps_o  e20pslw_o  e20psmd_o  e20pspo_o
idfather  idhh  idmother  idorighh  idorigperson  idpartner  idperson
kfb  kfbcc  kfbmy  kivho
lcs  les  lfs  lhw  lhw_f  lindi  liwftmy  liwmy  liwmy_f  liwptmy  liwwh  liwwh_f
loc  lowas  lpemy  lse  ltr  lunmy  lunmy_f
pdi  pdi00  pdimy  poa  poa00  poamy  psu  psumy
tad  tis  tpr  tscer  twl
xhc  xhcmomi  xhcot  xhcrt  xmp  xpp
yds  ydses_o  yem  yem00  yem_f  yem_hour  yemmy  yempv  yemxp  yivwg  yiy  ymwdt
yot  ypp  ypr  ypt  yptmp  yse  yse_f  ysemy
```

Year-conditional presence requirements:
- `tpr`: required for 2015 only; set to 0 for 2016/2017 if system expects it absent
- `dmb`, `twl`, `yptmp`: required for 2016 and 2017; set to 0 for 2015
- `bchba`, `bsawk`, `ltr`, `ymwdt`: required for 2017; set to 0 for 2015/2016

---

## 2. Individual-level layout requirement

### 2a. What the processed parquets look like (the authoritative reference)

The three processed full-output parquets (`fr_2015.parquet`, `fr_2016.parquet`,
`fr_2017.parquet`) are the post-EUROMOD individual-level files. Row counts:

| File | Rows | Unique idhh | Unique idperson | Note |
|---|---|---|---|---|
| `fr_2015.parquet` | **10,867** | 4,235 | 10,867 | All individuals incl. children, non-deciders |
| `fr_2016.parquet` | **10,873** | 4,253 | 10,873 | Same |
| `fr_2017.parquet` | **9,910** | 3,957 | 9,910 | Same |

Each row = one individual (`idperson` is unique). Households are groups of rows sharing
the same `idhh`. Children and non-deciders are present — the household roster is complete.

### 2b. What the precompute long file must look like

The alternative-expanded long file must be:

```
rows = Σ_households (n_individuals_in_hh × n_alternatives_for_hh)
```

where:
- `n_alternatives_for_hh` = **101** for singles HH (1 chosen + 100 simulated)
  and **901** for couples HH (1 chosen + 900 joint simulated)
- Every individual in the household — decider(s), children, non-decider adults —
  must appear in every alternative row
- `idhh` and `idperson` must be intact and correctly identify HH membership across alternatives
- A draw index column (`draw`, `draw_joint`, or equivalent) must distinguish alternatives

**Crucially:** EUROMOD taxes/benefits are computed at the household level. The full household
roster must be replicated across all alternatives, not just the decider row. Tax units,
child benefit eligibility, and means-tested transfers all depend on other household members'
income — if a non-decider row is missing, the household-level tax computation will be wrong.

---

## 3. Superset assertion: required column checks

The precompute long file (call it `fr_p3a_bpool_precompute__long.parquet`) MUST contain
every column from the raw EUROMOD input for the relevant year. The checks to run:

### 3a. Hard-stop missing columns (any of these = HALT)

For each year subset of the long file, assert that every raw input column is present:

```python
# Pseudocode for gate check
for year, raw_cols in [(2015, h2015), (2016, h2016), (2017, h2017)]:
    year_rows = long_df[long_df["data_year"] == year]
    long_cols = set(year_rows.columns)
    missing = set(raw_cols) - long_cols
    if missing:
        raise HardStop(f"MISSING from {year}: {missing}")
```

### 3b. Dtype consistency

For every raw input column present in both, dtype must be compatible (numeric → numeric;
categorical → same). EUROMOD is strict about input types — float64 is safe for all numeric
EUROMOD variables.

### 3c. Known dtype requirements from raw files

All raw input variables in `FR_20XX_a2/3.txt` are numeric (tab-separated floats/ints with
no string values except the header). The processed parquets confirm:
- `idhh`, `idperson`, `idmother`, `idfather`, `idpartner`, `idorighh`, `idorigperson`: `float64`
- All benefit/tax/income variables: `float64`
- All status/indicator dummies: `float64` (0.0/1.0)

---

## 4. Individual-level layout: detailed requirements

### 4a. Household roster completeness

For each alternative `k` of household `h`:
- Every individual `i ∈ h` must have a row with `idhh == h`, `idperson == i`, `draw == k`
- Children (identified by `idfather`/`idmother` links or age) must be present
- Non-decider adults must be present with **observed** hours/earnings (see §5)

### 4b. idhh / idperson integrity

- `idhh` must match the original household ID — EUROMOD uses `idhh` to group tax units
- `idperson` must be unique within `(idhh, draw)` — one row per person per alternative
- `idorighh` must be preserved for cluster-robust SE (= original cross-wave HH ID)

### 4c. Grouping check

For each alternative `k`, group by `(idhh, draw)`. The set of `idperson` values in that
group must equal exactly the set of `idperson` values in the observed alternative (draw==0
or is_chosen==1). No individual may appear, disappear, or be duplicated across alternatives.

---

## 5. Decider repricing only — non-decider invariance

### 5a. Who is a decider

In the bpool draw design:
- **Singles:** the single RURO decider individual (`ruro_decider == 1`)
- **Couples:** both partners (`hh_IsHead == 1` or `hh_IsPartner == 1`, both `ruro_decider == 1`)

### 5b. What varies across alternatives (decider only)

For the decider, the following columns take draw-specific values:

| Column | Source |
|---|---|
| `lhw` | drawn hours (= `hours` from bpool draw) |
| `lhw_f` | same (EUROMOD uses `lhw_f` as the annual hours variant) |
| `liwwh` | weekly hours (= drawn hours; EUROMOD may use weekly or annual) |
| `yem` | annual employment earnings computed from `wage × lhw × scale` |
| `yem_f` | same (female/annual variant) |
| `yem00` | primary employment income (EUROMOD label for main earnings) |
| `yemmy` | monthly earnings (= `yem / 12`) |
| `yempv` | earnings used for social contributions base |

All other decider columns hold their observed values (demographics, region, family status,
non-labour income — these do not vary across alternatives).

### 5c. What must NOT vary (non-deciders)

For every non-decider individual in the household:
- **All** columns must hold their observed values across all alternatives
- Specifically: `lhw`, `yem`, `yem00`, `yemmy` must equal the observed values
- Violation = incorrect tax computation (spouse's earnings affect means-tested benefits)

### 5d. Gate check pseudocode

```python
non_deciders = long_df[long_df["ruro_decider"] != 1]
for col in ["lhw", "yem", "yem00", "yemmy"]:
    # Each non-decider's col value must be constant across draw indices
    cv = non_deciders.groupby(["idhh", "idperson", "data_year"])[col].nunique()
    assert (cv == 1).all(), f"Non-decider {col} varies across draws — BUG"

deciders = long_df[long_df["ruro_decider"] == 1]
for col in ["lhw", "yem"]:
    n_unique_per_hh = deciders.groupby(["idhh", "data_year"])[col].nunique()
    # Each decider should have (n_alternatives) distinct values if hours truly vary
    assert (n_unique_per_hh > 1).all(), f"Decider {col} does not vary — draw not applied"
```

---

## 6. Extra (alternative/draw) columns — allowed additions

The precompute long file will contain extra columns beyond the raw EUROMOD input. These are
**not** a problem; EUROMOD ignores unknown columns if the runner is configured correctly.
Allowed extras (to be present in the long file for bookkeeping):

| Extra column | Purpose |
|---|---|
| `draw` | Alternative index (0 = chosen/observed; 1..N = simulated) |
| `draw_joint` | Joint draw index for couples (0..899) |
| `draw_male` | Male marginal draw index (couples) |
| `draw_female` | Female marginal draw index (couples) |
| `stacked_hh_uid` | Unique estimation unit (year × household) |
| `year_tag` | Numeric year tag (1=2015, 2=2016, 3=2017) |
| `is_chosen` / `is_chosen_joint` | Flags chosen row |
| `hours` / `hours_male` / `hours_female` | bpool-drawn hours (sourced to `lhw`) |
| `wage` / `wage_male` / `wage_female` | bpool-drawn wage |
| `loc4` / `loc4_male` / `loc4_female` | Drawn occupation category |
| `working` / `working_male` / `working_female` | Employment state |
| `log_q_*` | Proposal density components (for IS correction) |
| `log_prior` | Joint proposal log-density |

These extras ride alongside the required EUROMOD input columns and do not interfere with
EUROMOD's pricing computation.

---

## 7. Summary: gate criteria

**Run date: 2026-05-26. Script: `scripts/bpool/build_bpool_precompute.py`.**

### Per-year input-role table (pre-write inspection result)

| Variable | FR_2015_a2 (122 cols) | FR_2016_a3 (124 cols) | FR_2017_a2 (128 cols) | Role |
|---|---|---|---|---|
| `yem` | INPUT | INPUT | INPUT | Total monthly employment earnings |
| `yem00` | INPUT | INPUT | INPUT | Regular-hours component (≤35h) |
| `yemxp` | INPUT | INPUT | INPUT | Overtime component (>35h) |

No year-specific adjustments needed. Canonical earnings formula applied identically to all years.

`WEEKS_PER_MONTH = 52.0/12.0` confirmed at line 82 of `enh_RURO_euromod.py`. `yem` is monthly.
Not touched: `lhw_f`, `liwwh`, `liwwh_f`, `yem_f`, `yempv`.

### Output files produced

| File | Rows | Cols |
|---|---|---|
| `fr_p3a_bpool_precompute__2015__singles__long.parquet` | 243,713 | 562 |
| `fr_p3a_bpool_precompute__2015__couples__long.parquet` | 7,617,054 | 580 |
| `fr_p3a_bpool_precompute__2016__singles__long.parquet` | 241,895 | 566 |
| `fr_p3a_bpool_precompute__2016__couples__long.parquet` | 7,638,678 | 584 |
| `fr_p3a_bpool_precompute__2017__singles__long.parquet` | 238,764 | 575 |
| `fr_p3a_bpool_precompute__2017__couples__long.parquet` | 6,798,946 | 593 |

Total: **22,778,050 rows** across all years and modes. Sidecar: `fr_p3a_bpool_precompute__meta.json`.

Earnings formula (verbatim from `enh_RURO_euromod.py` §11, lines 725–768):
```
WEEKS_PER_MONTH = 52.0 / 12.0 ;  FRANCE_STANDARD_HOURS = 35.0
yem00 = min(lhw, 35)   × yivwg × WEEKS_PER_MONTH   [deciders only]
yemxp = max(lhw−35, 0) × yivwg × WEEKS_PER_MONTH   [deciders only]
yem   = yem00 + yemxp                                [identity asserted, max residual = 0.0]
non-working alt: yem00=yemxp=yem=0; yivwg preserved
yemmy=12 / lunmy=0 for working deciders (full-year employment, per §12)
```

### Gate check results (all 54 checks PASS)

| Check | 2015 S | 2015 C | 2016 S | 2016 C | 2017 S | 2017 C |
|---|---|---|---|---|---|---|
| G1 superset (all raw cols present) | PASS | PASS | PASS | PASS | PASS | PASS |
| G2 unique person per alternative | PASS | PASS | PASS | PASS | PASS | PASS |
| G3 full HH roster in every alternative | PASS | PASS | PASS | PASS | PASS | PASS |
| G4 non-decider lhw/yem/yem00/yemxp constant | PASS | PASS | PASS | PASS | PASS | PASS |
| G5 decider lhw varies across draws | PASS | PASS | PASS | PASS | PASS | PASS |
| G6 yem == yem00+yemxp (max resid=0.0) | PASS | PASS | PASS | PASS | PASS | PASS |
| G7 idmother intact | PASS | PASS | PASS | PASS | PASS | PASS |
| G7 idfather intact | PASS | PASS | PASS | PASS | PASS | PASS |
| G7 idpartner intact | PASS | PASS | PASS | PASS | PASS | PASS |

**Overall verdict: GATE PASSED — long files are EUROMOD-ready.**

---

## 8. What was built (completed 2026-05-26)

`scripts/bpool/build_bpool_precompute.py` — vectorized join design:

1. Reads bpool singles (505,707 rows) + couples (6,701,638 rows) from `U:/EUROMOD-STORAGE/new_data/`.
2. For each year, merges all bpool draw rows with the full HH roster (`fr_20YY.parquet`) on `idhh`
   via a single vectorized join — no Python-level row iteration.
3. Applies canonical earnings block (`_apply_earnings`) to decider rows only using `np.where`.
   Also sets `yemmy=12`/`lunmy=0` for working deciders (full-year employment, per §12).
4. Emits per-year long files (not a union): 2015=122 raw cols, 2016=124, 2017=128, plus extras.
5. Runs G1–G7 gate checks inline; hard-stops on G1 (missing raw column).

**Actual output sizes:**
- Singles: 724,372 rows total (243,713 + 241,895 + 238,764) across 2015–2017
- Couples: 22,053,678 rows total (7,617,054 + 7,638,678 + 6,798,946) across 2015–2017
- Grand total: **22,778,050 rows**

Output location: `U:/EUROMOD-STORAGE/new_data/` (6 parquets + 1 meta JSON).

**Next step: run EUROMOD per year** using each year's own system against the corresponding
per-year long file to fill `ils_dispy` on all simulated alternatives.
