# RURO Stijn Occ M0 — MNL Rebuild Command Plan v1

Date: 2026-05-12 (revised)

**Purpose**: Rebuild the France 2016 continuous MNL parquet files so that
`loc4` varies across working alternatives within each household, making the
12 occupation coefficients (`beta_occ_{2,3,4}_{sm,sf,cm,cf}`) identified.

**Root cause of current FAIL**: `enh_RURO_draws.py` defaults to
`occ_spec="fixed"`, which copies the household's observed occupation to every
working draw. All working alternatives of a household then share the same
occupation, so `beta_occ_k` is collinear with `beta_E`.

**Key change**: `--occ-spec empirical --occ-strata __all__`

`--occ-strata __all__` passes a single token that does not match any column in
the RURO-ready files. The draws script detects `len(strata_cols) == 0` and
falls back to a synthetic `__all__ = 1` column, collapsing all working
deciders into a single pooled stratum. This samples occupation from the
pooled empirical marginal — the M0 contract: one pooled `q_Occ`, no stratum
interactions.

**Occupation column requirement**: The MNL spec (`stijn_occ_M0`) expects
`loc4` in the final parquet. `enh_RURO_draws.py` calls `_infer_occ_col`,
which prefers `loc4` → `loc_ruro` → `loc`. **If the RURO-ready file does not
contain `loc4`, the rebuild cannot proceed as-is** — a pre-step that creates
`loc4` from `loc` (collapsing ISCO 1-digit to 4 task groups) would be
required first. Step 0 explicitly asserts `loc4` is present and fails loudly
if it is not.

---

## Notation

```powershell
$PY          = "U:/Desktop/Nizam_Hisham/MNL/.venv/Scripts/python.exe"
$DATA        = "Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016"
$EM          = "Z:/hisham/EUROMOD-STORAGE/EUROMOD_RELEASES_J1.0+/EUROMOD_RELEASES_J1.0+"
$RAW         = "Z:/hisham/EUROMOD-STORAGE/Data/raw"
$SCEN        = "Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/stijn_occ/scenarios"
$SCEN_RED    = "Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/stijn_occ/scenarios_reduced"
$GSUR        = "U:/Desktop/Nizam_Hisham/MNL/Data/external/FR_gsur_ruro.parquet"
$PROJ        = "U:/Desktop/Nizam_Hisham/MNL"
```

Use a dedicated scenario directory (`stijn_occ/scenarios`) so this rebuild
does not overwrite the `combined_draws_em.parquet` used by the existing job
model or current continuous MNL.

---

## Step 0 — Pre-flight canary (read-only, ~30 s)

Confirm the RURO-ready inputs exist and identify which occupation column will
be used by the draws script (`loc4` preferred, then `loc_ruro`, then `loc`).

```powershell
& $PY -c @'
import pandas as pd, sys

for name, path in [
    ("singles", r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready.parquet"),
    ("couples", r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/couples_RURO_ready.parquet"),
]:
    df = pd.read_parquet(path)
    required = ["loc4", "dgn", "lhw", "yivwg"]
    missing = [c for c in required if c not in df.columns]
    print(f"\n{name}: {len(df)} rows")
    print(f"  Missing required cols: {missing}")
    if missing:
        print(f"  STOP: required columns missing — cannot proceed")
        sys.exit(1)
    # Working filter: lhw > 0 (positive contracted hours), not lma flag
    working_mask = df["lhw"] > 0
    vc = df.loc[working_mask, "loc4"].value_counts().sort_index()
    n_uniq = vc.shape[0]
    print(f"  loc4 distribution (lhw > 0): {vc.to_dict()}")
    print(f"  Distinct loc4 values in working subsample: {n_uniq}  (need >= 3)")
    if n_uniq < 3:
        print(f"  WARNING: only {n_uniq} distinct loc4 value(s) — empirical sampling may not create variation")
'@
```

**Pass criteria**:

- Both files load without error.
- `loc4` is present (not `loc_ruro` or `loc`). If absent, a pre-step creating `loc4` from `loc` is required before anything else.
- At least 3 distinct `loc4` values among `lhw > 0` rows (positive contracted hours — the correct working filter; `lma` can include non-employment alternatives where `loc4 = -1`).

---

## Step 1 — Rebuild draws with pooled occupation sampling

Before running, optionally back up the existing draw files if they are still
needed by other pipelines:

```powershell
Rename-Item "$DATA/singles_RURO_ready_RURO_draws.parquet" `
            "$DATA/singles_RURO_ready_RURO_draws__pre_stijn_occ.parquet"
Rename-Item "$DATA/couples_RURO_ready_RURO_draws.parquet" `
            "$DATA/couples_RURO_ready_RURO_draws__pre_stijn_occ.parquet"
```

Run draws:

```powershell
& $PY "$PROJ/scripts/enhanced/enh_RURO_draws.py" `
  --singles-path "$DATA/singles_RURO_ready.parquet" `
  --couples-path "$DATA/couples_RURO_ready.parquet" `
  --n-draws 99 `
  --wage-spec vw `
  --occ-spec empirical `
  --occ-strata __all__ `
  --occ-min-cell 30 `
  --h-min 5.0 `
  --h-max 70.0 `
  --w-min 2.0 `
  --w-max 170.0 `
  --rng-seed 17
```

**Output files**:

| File | Location |
| --- | --- |
| `singles_RURO_ready_RURO_draws.parquet` | `$DATA/` |
| `singles_RURO_ready_RURO_draws__drawsmeta.json` | `$DATA/` |
| `couples_RURO_ready_RURO_draws.parquet` | `$DATA/` |
| `couples_RURO_ready_RURO_draws__drawsmeta.json` | `$DATA/` |

New column added by `--occ-spec empirical`: `log_q_occ` (log-proposal
density for the drawn occupation on working alternatives; zero for
non-work alternatives and for draw=0 non-workers).

### C1 — Post-draw canary (run before EUROMOD, ~30 s)

Replace `OCC_COL` below with the column reported by Step 0:

```powershell
& $PY -c @'
import pandas as pd

df = pd.read_parquet(r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws.parquet")
print("loc4 present:", "loc4" in df.columns)
print("log_q_occ present:", "log_q_occ" in df.columns)
# Simulated working draws only: draw >= 1 AND hours > 0 (lhw > 0)
# lma is not used — non-employment draws also have lma=1 but loc4=-1
sim = df[df["draw"] >= 1]
working_sim = sim[sim["lhw"] > 0] if "lhw" in sim.columns else sim[sim["hours"] > 0]
if "loc4" in df.columns and "idhh_true" in df.columns:
    med = working_sim.groupby("idhh_true")["loc4"].nunique().median()
    print(f"Median distinct loc4 per household in simulated working draws (lhw > 0): {med}")
    print("(expect >= 2; if 1, --occ-spec empirical did not take effect)")
'@
```

**Pass criteria**: `loc4` and `log_q_occ` both present; median distinct
`loc4` per household in simulated working draws ≥ 2. If median = 1, do not
proceed.

### C2 — Drawsmeta occ_spec check (~5 s)

```powershell
& $PY -c @'
import json
with open(r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/singles_RURO_ready_RURO_draws__drawsmeta.json") as f:
    m = json.load(f)
dp = m.get("distributional_params", {})
print("occ_spec :", dp.get("occ_spec"))
print("occ_strata:", dp.get("occ_strata"))
print("n_draws  :", m.get("n_draws"))
print("seed     :", m.get("seed"))
'@
```

**Pass criteria**: `occ_spec: empirical`, `occ_strata: ['__all__']`.
If `occ_spec: fixed`, the draw file was not rebuilt — re-run Step 1.

---

## Step 2 — EUROMOD simulation on rebuilt draws

```powershell
& $PY "$PROJ/scripts/enhanced/enh_RURO_euromod.py" `
  --singles-draws "$DATA/singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "$DATA/couples_RURO_ready_RURO_draws.parquet" `
  --microdata-template "$RAW/FR_2016.txt" `
  --euromod-system FR_2015 `
  --euromod-dataset FR_2016 `
  --euromod-root "$EM" `
  --scenario-dir "$SCEN"
```

**Output files**:

| File | Location |
| --- | --- |
| `combined_draws_em.parquet` | `$SCEN/` |

EUROMOD reads and writes income/tax-benefit variables only. The `loc4` column
is carried through unchanged in the draws file and re-joined downstream in
MNL prep.

---

## Step 2b — Column reduction (optional, between EUROMOD and MNL prep)

`reduce_mnl_columns.py` processes **`combined_draws_em.parquet`** — the
EUROMOD output — and writes a trimmed version with ~100 essential columns
instead of 900+. Run this step **after EUROMOD and before MNL prep** to
reduce memory usage and speed up Step 3.

Dry run first to see what will be dropped:

```powershell
& $PY "$PROJ/scripts/enhanced/reduce_mnl_columns.py" `
  --input-dir  "$SCEN" `
  --output-dir "$SCEN_RED" `
  --spec-dir   "$PROJ/scripts/enhanced" `
  --dry-run --verbose
```

If the dry run looks correct, apply:

```powershell
& $PY "$PROJ/scripts/enhanced/reduce_mnl_columns.py" `
  --input-dir  "$SCEN" `
  --output-dir "$SCEN_RED" `
  --spec-dir   "$PROJ/scripts/enhanced" `
  --verbose
```

**Output file**: `$SCEN_RED/combined_draws_em.parquet`

If Step 2b is run, use `$SCEN_RED` in the `--euromod-combined` argument of
Step 3. If Step 2b is skipped, use `$SCEN` instead (see Step 3 command).

---

## Step 3 — Rebuild MNL parquet files

If Step 2b was run (recommended):

```powershell
& $PY "$PROJ/scripts/enhanced/enh_RURO_prep_mnl_basic.py" `
  --singles-draws "$DATA/singles_RURO_ready_RURO_draws.parquet" `
  --couples-draws "$DATA/couples_RURO_ready_RURO_draws.parquet" `
  --euromod-combined "$SCEN_RED/combined_draws_em.parquet" `
  --out-base "$DATA/fr_2016_RURO_mnl" `
  --wage-spec vw `
  --year 2016 `
  --gsur-file "$GSUR" `
  --drawsmeta "$DATA/singles_RURO_ready_RURO_draws__drawsmeta.json"
```

If Step 2b was skipped, replace `$SCEN_RED` with `$SCEN`.

**Key flags**:

- `--drawsmeta`: reads the sidecar from Step 1, syncing `pi0_m`, `pi0_f`,
  `h_min/max`, `w_min/max`, `wage_spec`, and `occ_spec` so MNL prep
  computes priors that exactly match the draw distribution.
- No `--no-column-filter`: the default column filter is active. MNL prep
  computes the frozen Stijn aliases (`log_q_E`, `log_q_H`, `log_q_W`,
  `log_q_Occ`) from the raw draw-layer components (`log_q_state`,
  `log_q_hours`, `log_q_wage`, `log_q_occ`) and keeps only the aliases in
  the final parquet — the raw layer columns are dropped. Also kept: `loc4`.
  Forbidden columns dropped: `lindi`, `industry`, `nace`, `log_q_job`,
  `log_q_total`, `log_q_state`, `job_id`, `type_id`, `hours_bin`, `wage_bin`.

**Output files** (overwrite warning — these replace the existing MNL
parquets used by the current continuous pipeline):

| File | Location |
| --- | --- |
| `fr_2016_RURO_mnl__singles.parquet` | `$DATA/` |
| `fr_2016_RURO_mnl__couples.parquet` | `$DATA/` |

The job-model files (`fr_2016_RURO_mnl_job_gmm`) are in a separate directory
and are not affected.

### C3 — Post-MNL Gate-A canary: occupation variation (~60 s)

```powershell
& $PY -c @'
import pandas as pd

SINGLES = r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet"
COUPLES = r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet"

# --- Singles ---
s = pd.read_parquet(SINGLES)
w = s[s["working"] == 1]
med = w.groupby("idhh")["loc4"].nunique().median() if "loc4" in s.columns else "loc4 MISSING"
print(f"Singles: median distinct loc4 per idhh in working alts = {med}  (expect >= 3)")
for col in ["log_q_E", "log_q_H", "log_q_W", "log_q_Occ", "log_prior"]:
    print(f"  {col}: {col in s.columns}")

# --- Couples male ---
c = pd.read_parquet(COUPLES)
for partner in ["male", "female"]:
    wc = c[c[f"working_{partner}"] == 1] if f"working_{partner}" in c.columns else c
    loc_col = f"loc4_{partner}"
    med = wc.groupby("idhh")[loc_col].nunique().median() if loc_col in c.columns else f"{loc_col} MISSING"
    print(f"\nCouples {partner}: median distinct {loc_col} per idhh in working alts = {med}  (expect >= 3)")
    for col in [f"log_q_E_{partner}", f"log_q_H_{partner}", f"log_q_W_{partner}", f"log_q_Occ_{partner}"]:
        print(f"  {col}: {col in c.columns}")
'@
```

**Pass criteria**:

- Singles: median distinct `loc4` per `idhh` ≥ 3.
- Couples male: median distinct `loc4_male` per `idhh` ≥ 3.
- Couples female: median distinct `loc4_female` per `idhh` ≥ 3.
- All Stijn alias columns present for singles (`log_q_E/H/W/Occ`) and for
  each partner (`log_q_E_male`, `log_q_H_male`, `log_q_W_male`,
  `log_q_Occ_male`, and the `_female` equivalents).

If any median = 1.0, the draws rebuild did not produce occupation variation.
Check C2 first; if drawsmeta shows `occ_spec: fixed` re-run from Step 1.

### C4 — Post-MNL canary: prior consistency (~30 s)

```powershell
& $PY -c @'
import pandas as pd, numpy as np

SINGLES = r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet"
COUPLES = r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__couples.parquet"

# --- Singles: log_prior = log_q_E + working*(log_q_H + log_q_W + log_q_Occ) ---
s = pd.read_parquet(SINGLES)
w = (s["working"] == 1).astype(float)
recon = s["log_q_E"] + w * (s["log_q_H"] + s["log_q_W"] + s["log_q_Occ"])
diff = (s["log_prior"] - recon).abs()
print(f"Singles  max |log_prior - recon|: {diff.max():.6e}  (expect < 1e-9)")
print(f"         rows with |diff| > 1e-6: {(diff > 1e-6).sum()}")

# --- Couples: log_prior = male_component + female_component ---
# male:   log_q_E_male + working_male*(log_q_H_male + log_q_W_male + log_q_Occ_male)
# female: log_q_E_female + working_female*(log_q_H_female + log_q_W_female + log_q_Occ_female)
c = pd.read_parquet(COUPLES)
wm = (c["working_male"] == 1).astype(float)
wf = (c["working_female"] == 1).astype(float)
recon_c = (
    c["log_q_E_male"]   + wm * (c["log_q_H_male"]   + c["log_q_W_male"]   + c["log_q_Occ_male"])
  + c["log_q_E_female"] + wf * (c["log_q_H_female"] + c["log_q_W_female"] + c["log_q_Occ_female"])
)
diff_c = (c["log_prior"] - recon_c).abs()
print(f"Couples  max |log_prior - recon|: {diff_c.max():.6e}  (expect < 1e-9)")
print(f"         rows with |diff| > 1e-6: {(diff_c > 1e-6).sum()}")
'@
```

**Pass criteria**: max absolute difference < 1e-9 for both singles and couples.
Any larger discrepancy indicates a prior-computation mismatch in MNL prep.

---

## Step 4 — Summary of expected output files

| Step | File | Location |
| --- | --- | --- |
| 1 | `singles_RURO_ready_RURO_draws.parquet` | `$DATA/` |
| 1 | `singles_RURO_ready_RURO_draws__drawsmeta.json` | `$DATA/` |
| 1 | `couples_RURO_ready_RURO_draws.parquet` | `$DATA/` |
| 1 | `couples_RURO_ready_RURO_draws__drawsmeta.json` | `$DATA/` |
| 2 | `combined_draws_em.parquet` | `$SCEN/` |
| 2b | `combined_draws_em.parquet` (reduced) | `$SCEN_RED/` |
| 3 | `fr_2016_RURO_mnl__singles.parquet` | `$DATA/` |
| 3 | `fr_2016_RURO_mnl__couples.parquet` | `$DATA/` |

---

## Step 5 — Estimated runtime and risk

| Step | Estimated wall time | Risk |
| --- | --- | --- |
| 0 — pre-flight canary | ~30 s | None |
| 1 — draws | ~5–15 min (99 draws × ~30 k singles + ~12 k couples) | Low; fully vectorised |
| C1/C2 — post-draw canaries | ~30 s | None |
| 2 — EUROMOD | **30–90 min** | High: .NET startup + 100 × FR_2016 scenarios; needs EUROMOD DLLs |
| 2b — column reduction | ~2–5 min | Low |
| 3 — MNL prep | ~10–20 min | Medium: join and column compute at n_hh × 100 rows |
| C3/C4 — post-MNL canaries | ~60 s | None |

**EUROMOD risk notes**:

- Requires `.NET CoreCLR` and the release at `$EM`. Verify the path exists before submitting.
- If EUROMOD fails mid-run, scenario files in `$SCEN` may be partial. Delete `$SCEN` entirely and retry from Step 2.
- Memory: 99 draws × ~42 k individuals ≈ 8–16 GB RAM.

**Overwrite risk**: Steps 1 and 3 overwrite files shared with the existing
continuous pipeline. Any estimation reading `fr_2016_RURO_mnl__singles.parquet`
will use the new occupation-varying data after Step 3.

---

## Step 6 — Canary ladder summary

Run in order; stop on the first failure before proceeding.

| Check | When | Expect |
| --- | --- | --- |
| C0 — pre-flight | Before Step 1 | Both RURO-ready files load; occ col found; ≥ 3 distinct values in working subsample |
| C1 — post-draw | After Step 1, before Step 2 | `log_q_occ` present; median distinct occ per household ≥ 2 in simulated working draws |
| C2 — drawsmeta | After Step 1, before Step 2 | `occ_spec: empirical`, `occ_strata: ['__all__']` |
| C3 — Gate-A | After Step 3 | Median distinct `loc4` (and `loc4_male`/`loc4_female`) per household ≥ 3; all Stijn aliases present |
| C4 — prior | After Step 3 | Max \|log_prior − reconstructed\| < 1e-9 |

---

## Appendix — Estimation command (after rebuild only)

Do not run until all canaries (C0–C4) pass.

```powershell
& $PY "$PROJ/scripts/enhanced/enh_RURO_estimate_FR.py" `
  --mnl-base "$DATA/fr_2016_RURO_mnl" `
  --output-dir "U:/Desktop/Nizam_Hisham/MNL/outputs/estimates/fr/spec/stijn_occ/gamspy" `
  --group joint `
  --solver gamspy-conopt `
  --vectorized `
  --spec-config "scripts/enhanced/estimation_spec_stijn_occ_M0.yaml" `
  --auto-timestamp `
  --verbose
```

Do not warm-start from a job-choice run (default is no warm-start).

---

## What this plan does NOT cover

- Rebuilding `singles_RURO_ready.parquet` / `couples_RURO_ready.parquet`
  (assumed current).
- Rebuilding the GSUR file (assumed current at `$GSUR`).
- Post-estimation occupation panels (observed vs predicted `loc4`
  distributions) — pending addition to `RURO_post_estimation_styled.py`.
- Cross-engine (NumPy vs GAMSPy) consistency diagnostics.
