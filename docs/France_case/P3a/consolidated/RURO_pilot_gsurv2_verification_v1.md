# RURO Pilot GSURv2 Verification v1

**Purpose:** Read-only verification answers to four questions about the GSURv2
MNL-parquet merge and the NC pilot spec structure. Each verdict is backed by a
specific file and field. Nothing is inferred; UNCONFIRMED is stated where disk
evidence is absent.

---

## Q1 — Has the GSURv2 MNL-parquet merge actually executed?

**Evidence checked:**

1. **GSURv2-versioned files exist on disk:**
   - `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__singles.parquet`
   - `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__couples.parquet`
   - `Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl_GSURv2__mnlmeta.json`

   Files exist. But their sidecar content is decisive.

2. **GSURv2 mnlmeta sidecar (`fr_2016_RURO_mnl_GSURv2__mnlmeta.json`) fields:**
   - `"timestamp": "2026-05-13T08:38:20.951652Z"` — identical to the canonical
     `fr_2016_RURO_mnl__mnlmeta.json` timestamp.
   - `"gsur_file": "U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet"` —
     this is the **v1 GSUR file**, not a GSURv2 file. Same field value as the
     canonical sidecar. No `gsur_source`, `provisioning_label`, or
     `opportunity_year` field is present in either file.
   - The two mnlmeta files are **byte-for-byte identical** in all non-column
     fields. The `fr_2016_RURO_mnl_GSURv2__` prefix appears to be a file-naming
     artefact; the sidecar does not confirm a distinct GSURv2 merge was run.

3. **P3a pooled file — GSURv2 confirmed:**
   - `Data/processed/fr/pooled/fr_p3a_gsurv2_harmonised__stage_m1_meta.json`:
     - `"provisioning_label": "gsurv2_opportunity_year_aligned"` ✓
     - `"gsur_source": "GSURv2_opportunity_year_aligned"` ✓
     - Input stems for 2016: `fr_2016_RURO_mnl_GSURv2_y2015__singles/couples.parquet`
       with SHA-256 hashes recorded.
   - SHA-256 entries confirm those per-year GSURv2 files (with `_y2015_` tag)
     were consumed. These files are **distinct** from the untagged
     `fr_2016_RURO_mnl_GSURv2__` files (no year-suffix). The year-tagged
     `_y2015_` files are not listed in the `fr/2016/` directory listing above,
     suggesting they may reside elsewhere or were since renamed.
   - `Data/processed/fr/pooled/fr_p3a_provisional_v1fallback_harmonised__stage_m1_meta.json`:
     - `"provisioning_label": "provisional_v1_fallback_opportunity_year_aligned"` —
       this is the **old** (v1-fallback) pooled file, now superseded.

**Verdict:** GSURv2 MNL merge = **EXECUTED for the P3a pooled dataset**
(`fr_p3a_gsurv2_harmonised.parquet`, provisioning_label =
`gsurv2_opportunity_year_aligned`). The untagged single-year files
`fr_2016_RURO_mnl_GSURv2__{singles,couples}.parquet` carry a v1 GSUR source in
their sidecar — their GSURv2 provenance is UNCONFIRMED from the sidecar alone.

---

## Q2 — Which opportunity-side variables does the NC pilot spec carry?

**File:** `scripts/pilot/specs/estimation_spec_nc_pilot_couples_2016.yaml`

**Market opportunity (`market_opportunity`) shifters (lines 84–115):**

| Coefficient | Variable | Notes |
| --- | --- | --- |
| `beta_E_gsur` | `gsur` | Present. `variable_scales: gsur: 10.0` (line 82). |
| `beta_E_drgn2` | `reg2` | Present (line 89). |
| `beta_E_drgn3` | `reg3` | Present (line 94). |
| `beta_E_drgn4` | `reg4` | Present (line 98). |
| `beta_E_drgn5` | `reg5` | Present (line 102). |
| `beta_E_drgn6` | `reg6` | Present (line 106). |
| `beta_E_drgn7` | `reg7` | Present (line 110). |
| `beta_E_drgn8` | `reg8` | Present (line 114). |

**Urbanisation trio (`drgur` / `drgmd` / `drgru`):** Not present anywhere in the
spec YAML. No coefficient for any urbanisation variable appears in
`market_opportunity`, `hours_opportunity`, `wage_opportunity`, or
`occupation_opportunity`. The variables are present in the pre-drop MNL data
(confirmed by `fr_2016_RURO_mnl__mnlmeta.json` column list lines 62–64:
`drgur`, `drgmd`, `drgru`) but they are not referenced by the pilot spec.

**Verdict:** Urbanisation in pilot spec = **IN-DATA-NOT-IN-SPEC**

---

## Q3 — Is educH confirmed OUT of the hours/employment-opportunity layer?

**File:** `scripts/pilot/specs/estimation_spec_nc_pilot_couples_2016.yaml`

**`hours_opportunity` block (lines 47–55):** contains only four shifters —
`working` → `beta_E`, `working_pt1` → `beta_h_pt1`, `working_pt2` →
`beta_h_pt2`, `working_ft` → `beta_h_ft`. No `educH` or any education variable
appears.

**`market_opportunity` block (lines 74–116):** contains `gsur` and `reg2`–`reg8`
only. No `educH`.

**`wage_opportunity` block (lines 58–72):** lists `educL` → `beta_w_educL` and
`educH` → `beta_w_educH` (line 66). `educH` appears **only** here.

The parameter count comment at line 152–163 confirms: Wage layer lists
`beta_w_educH` among its 6 parameters; hours/market opportunity lists no education
terms.

**Verdict:** educH out of hours-opp = **CONFIRMED** (present in wage layer only,
absent from hours and market opportunity layers per spec definition).

---

## Q4 — Does the pilot wage layer use occupation-conditional (LOC4) wages?

**File 1:** `scripts/pilot/specs/estimation_spec_nc_pilot_couples_2016.yaml`,
line 21:

```yaml
wage_spec: "vw"
```

**File 2:** `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__mnlmeta.json`,
line 21:

```json
"wage_model": "W1 (occupation-conditioned log-normal); reference loc4 = 1"
```

Lines 24–29 of the same file record four occupation-specific delta coefficients
(calibrated/fixed at draw time, not free parameters):

```json
"calibrated_delta_occ": {
    "delta_occ2": -0.07970...,
    "delta_occ3":  0.02509...,
    "delta_occ4":  0.24145...,
    "status": "calibrated, fixed at draw time, NOT free structural parameters"
}
```

The `vw` wage spec in the spec YAML has a single mean-equation (one intercept
`beta_w0` + education + experience terms). The LOC4 occupation differentials
(`delta_occ2/3/4`) are **baked into the wage draws** at the proposal/draw stage
(W1), not estimated as separate regression equations per occupation. This is one
Mincer equation with occupation-conditional mean shifts absorbed into the draw,
not four separate LOC4 equations estimated independently.

The `occupation_opportunity` block (lines 118–145) carries `beta_occ_2/3/4`
for couples-male and couples-female — these are **opportunity-availability mass**
parameters (the probability that job type k is offered), not wage-equation
parameters.

**Verdict:** Wage structure = **occupation-conditional (W1)** — single Mincer
equation with LOC4-conditional mean shifts (`delta_occ2/3/4`) fixed at draw
time; one variance parameter `sigma` common across occupations.

---

## Summary

| Question | Verdict |
| --- | --- |
| Q1: GSURv2 MNL merge executed? | EXECUTED for P3a pooled file (`gsurv2_opportunity_year_aligned`); single-year `fr_2016_RURO_mnl_GSURv2__` files carry v1 GSUR in their sidecar — those files' GSURv2 status is UNCONFIRMED. |
| Q2: Urbanisation in pilot spec? | IN-DATA-NOT-IN-SPEC (`drgur`/`drgmd`/`drgru` present in data columns, absent from all spec blocks) |
| Q3: educH out of hours-opp? | CONFIRMED (absent from `hours_opportunity` and `market_opportunity` blocks; present only in `wage_opportunity`) |
| Q4: Wage structure? | occupation-conditional (W1) — one Mincer equation, `delta_occ2/3/4` fixed at draw time, single `sigma` |