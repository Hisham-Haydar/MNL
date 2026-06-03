# RURO Rebuild — Stage Three, Increment Three-A: pin and validate the reproducible staged baseline

**Date:** 2026-06-03
**Increment:** STAGE THREE, INCREMENT THREE-A only — pin the rebuild configuration from
evidence and validate the Two-N staged rebuild as a reproducible CANDIDATE baseline with a
non-bypassable determinism gate.
**Status:** complete. **VERDICT: VALIDATED REPRODUCIBLE CANDIDATE BASELINE = TRUE.** All four
required gates pass: Task 1 coverage ✓, Task 2 determinism ✓, Task 3 component coherence ✓,
Task 4 criterion recorded ✓.

The Two-N staged rebuild reproduces itself **exactly** (a second independent EUROMOD run of a
singles chunk and a benefit-heavy couples chunk matches the staged output to machine zero on
every headline, every simulated component, every key, and row order), is **internally
coherent** at full scale (0 identity violations across all six year × mode cells), and its
rebuild configuration is now **pinned from build-code + runtime evidence**. The baseline is
therefore a sound foundation for a *separately authorised* controlled re-estimation — but it
is **NOT canonical**, and this increment performs no re-estimation, no welfare, and no swap.

> **No re-estimation; no `V_i^dir`; no redrawn-node pricing; no promotion of any staged
> baseline to canonical; no production parquet swapped, overwritten, moved, or deleted;
> nothing beyond `W^3`.** The determinism re-run wrote only to a clearly-marked scratch
> directory (neither production nor the Two-N staging baseline). Not committed automatically.

---

## Task 0 — pinned rebuild configuration (FROM EVIDENCE)

The pinned config (`outputs/welfare/stage1_w3/stage3a_pinned_rebuild_config.json`) is generated
by **reading the build worker's constants and the runtime path/EUROMOD resolver** — nothing is
hardcoded in the validator. Recovered facts:

| field | value (from evidence) |
|---|---|
| EUROMOD release dir | `…/EUROMOD-STORAGE/Euromod_model/EUROMOD_RELEASES_J2.0+` |
| `euromod` package version | `0.2.17` |
| pythonnet runtime | `coreclr` |
| system pairing | data 2015 → `FR_2014`; 2016 → `FR_2015`; 2017 → `FR_2016` (one system per data year) |
| dataset names | 2015 → `FR_2015_a2`; 2016 → `FR_2016_a3`; 2017 → `FR_2017_a2` |
| CPI `phi_y` | 2015 = 1.0031; 2016 = 1.0000; 2017 = 0.9886 |
| per-year input schema | 2015: 122 cols; 2016: 124 cols; 2017: 128 cols (full lists in the JSON) |
| ID stamping | singles `id*1000+draw`; couples `id*10000+draw`; `*_true` preserves originals |
| staging path (Two-N) | `…/EUROMOD-STORAGE/new_data/staging_twoN` |
| production chunk manifest | 21 chunks (singles 1/yr `[0,101)`; couples 6/yr bands of 150 over `[0,900)`) with stored row counts |
| estimation base year | estimator wages **2016-real**; `c_scale = mean(consumption)`; post-EUROMOD `ils_dispy_real = ils_dispy × phi_y` (CPI per **data** year) |
| all-component write-back | patched (writes every `sim_df` column not in `_RAW_SCHEMA[year]`, Two-M) |
| certified estimate reference | `joint_pooled_v1_bll0_tlmpin`, **47 free params**, clustered SE present, cluster key `idorighh` |

**Recorded as `NOT ESTABLISHED FROM REPO EVIDENCE` (not guessed):**

- the **exact internal EUROMOD model version** — the `euromod` API exposes the release-dir
  name (`EUROMOD_RELEASES_J2.0+`) and package version (`0.2.17`) but not an exact model
  build/version string;
- the **assessment-unit / tax-unit definition** — this lives inside the EUROMOD FR model
  (internal TUDef resolution), not in repo config. Only runtime TUDef *counts* are observable,
  and the chunk worker does not persist a TUDef count (completion markers carry `tudef=None`).

The two-deflation architecture is preserved by construction (the build feeds EUROMOD **nominal**
earnings; the 2016-real deflation is estimator-facing only; the `phi_y` CPI is applied **after**
EUROMOD) — this is the pinned-config record of it, not a change to it.

---

## Task 1 — staged-baseline coverage (PASS)

Read against the pinned production chunk manifest:

- **21 / 21 chunks present**, each with a completion marker `.done.json`.
- **All staged row counts match the manifest exactly** (e.g. 2017 singles c0 = 238,764;
  2017 couples c5 = 1,131,900; 2015 couples c0 = 1,276,554).
- **Staged data are distinct from production paths.** Staging is `…/new_data/staging_twoN/`
  (chunk files `…__c{N}.parquet`); the production assembled priced files
  (`…__{mode}.parquet`, no `__c`) live directly in `…/new_data/`. Different directory,
  non-colliding names; no production assembled priced parquet is reachable for overwrite in
  staging. (This check mirrors the Two-N `_resolve_staging_or_refuse` safety rule: unsafe only
  if staging *is* the `new_data/` root, *is* the `chunks/` dir, or is *inside* `chunks/` — a
  separate subdirectory of `new_data/` is the intended, safe layout.)
- **Production parquet untouched** — the six assembled priced files are all dated 2025-05-26
  (a read-only mtime/size snapshot is recorded in the provenance JSON); none was written.

`task1_coverage.ok = TRUE`.

---

## Task 2 — determinism gate (PASS — the decisive gate)

A deterministic subset was **re-run from scratch** through the **patched all-component
write-back worker under the pinned config**, to a **separate scratch directory**
(`…/new_data/scratch_three_a_determinism`, neither production nor Two-N staging), and compared
column-for-column against the existing Two-N staged output.

**Subset** (≥1 singles, ≥1 couples, ≥1 benefit-heavy): 2017 was the worst Two-N cell for
means-tested divergence (singles 4.3 %, couples 8.4 %), so the benefit-heavy chunk is a 2017
couples band.

| chunk | role | rows (staged == rerun) | row order | headline cols checked / bad | component `ils_*`/`*_s` cols checked / bad | PASS |
|---|---|---|---|---|---|---|
| 2017 singles c0 | singles | 238,764 == 238,764 | identical | 6 / **0** | 133 / **0** | ✓ |
| 2017 couples c5 | couples / benefit-heavy | 1,131,900 == 1,131,900 | identical | 6 / **0** | 133 / **0** | ✓ |

The comparison covers `ils_dispy`, `ils_origy`, `ils_ben`, `ils_tax`, `ils_sicdy`,
`ils_dispy_real`, **all 133 available `ils_*` / `*_s` simulated component columns**, and the
full row-key set (`stacked_hh_uid`, `draw`/`draw_joint`/`draw_male`/`draw_female`,
`idperson_true`) in positional order. **Max abs difference = 0 above tolerance (1e-6) on every
column; row order is byte-identical.**

`task2_determinism_gate.ok = TRUE`. The staged baseline **reproduces itself exactly** — it is a
valid controlled-re-estimation foundation (a baseline that did not reproduce itself could not
be). This is the gate that the increment requires not to be bypassable; it ran a genuine second
EUROMOD execution, not a re-read of the staged files.

---

## Task 3 — component-coherence gate on the FULL staged baseline (PASS)

On the full Two-N staged baseline (all 21 chunks, decider rows), per year × mode:

| cell | `ils_ben` identity violations | `ils_dispy` identity violations | `ils_ben` varies across draws | `ils_benmt` varies across draws |
|---|---|---|---|---|
| 2015 singles | 0 | 0 | 97.0 % | 97.0 % |
| 2015 couples | 0 | 0 | 98.5 % | 97.0 % |
| 2016 singles | 0 | 0 | 96.8 % | 96.8 % |
| 2016 couples | 0 | 0 | 98.6 % | 97.3 % |
| 2017 singles | 0 | 0 | 94.5 % | 94.4 % |
| 2017 couples | 0 | 0 | 96.0 % | 93.7 % |

`ils_ben = ils_pen + ils_benmt + ils_bennt` and `ils_dispy = ils_origy − ils_tax − ils_sicdy +
ils_ben` both hold with **0 violations** in every cell (the stale stored data violated these on
58–59 % singles / 32–40 % couples), and the simulated components are **draw-specific** (≈ 94–99 %
of households). The Two-L/Two-M staleness bug is confirmed fixed on the full staged baseline.

`task3_component_coherence_full.ok = TRUE`.

---

## Task 4 — pre-registered controlled re-estimation verdict criterion (RECORDED)

Written into the provenance JSON **before** any re-estimation is run. The criterion (verbatim
intent):

- **Re-estimate** the certified spec (`joint_pooled_v1_bll0_tlmpin`, 47 free params, `theta_l_m`
  pinned −0.8, `beta_ll` fixed 0) on the reproducible rebuilt baseline, **initialised from the
  certified `theta_hat`** (`scripts/bpool/specs/theta_hat_realdata_901_v1.csv`).
- **Compare every parameter against certified `theta_hat`, parameter-by-parameter.**
- **Judge movement against the clustered standard error** (`se_clustered`, cluster key
  `idorighh`): within ~the clustered-SE band ⇒ immaterial; well outside ⇒ material.
- **Focus on the decomposition-relevant blocks:** ability/wage (`beta_w0`, `beta_w_educL`,
  `beta_w_educH`, `beta_w_pexp`, `beta_w_pexp2`, `sigma`); opportunity/access (`beta_E`,
  `beta_h_*`, `beta_E_gsur`, `beta_E_drg*`, `beta_E_y*`, `beta_E_drgur/drgmd`, `beta_occ_*`);
  preference (`beta_l0_*`, `beta_l_age*`, `beta_l_nkids_*`, `theta_l_*`, `theta_c_singles`).
- **Re-run the synthetic-recovery standard** on the new reproducible baseline (PD Hessian at
  production scale + recovery within tolerance), as for the certified gate.
- **No welfare promotion** (`V_i^dir`, redrawn-node pricing, `W^3` promotion, anything beyond
  `W^3`) until the estimate decision is settled.

**Decision rule (pre-registered):** if all decomposition-relevant blocks are within
clustered-SE tolerance AND the synthetic-recovery standard passes, the irreproducibility is
immaterial and the certified estimate stands **with a caveat** (Two-O Option A); otherwise the
reproducible baseline replaces the old one and its re-estimate becomes certified (Two-O Option
B). **This increment does NOT run the re-estimation.**

---

## Task 5 — readiness statement

| condition | result |
|---|---|
| Task 1 coverage PASS | ✓ |
| Task 2 determinism PASS | ✓ |
| Task 3 component coherence PASS | ✓ |
| Task 4 criterion recorded | ✓ |
| pinned configuration evidence complete | ✓ |

**`validated_reproducible_candidate_baseline = TRUE`.**

Explicitly:

- **The baseline is NOT canonical.** It is a validated *reproducible candidate* only.
- **Production is NOT swapped** (the six assembled priced files are unchanged, dated
  2025-05-26).
- **Controlled re-estimation is a SEPARATE authorisation** — not performed here.
- **No welfare computation is authorised** by this increment.

The next decision is the Two-O dispositive test (controlled re-estimation on this reproducible
baseline, compared against certified `theta_hat` / clustered SEs / synthetic-recovery standard),
which requires separate supervisor authorisation.

---

## Files

- **Validation source:** `scripts/welfare/run_stage3a_pinned_baseline_validation.py`
  (Tasks 0–5; reads build-code constants, emits pinned config, coverage, determinism gate,
  full-scale coherence, criterion, readiness). Config-driven; no hardcoded country/year/spec
  constants.
- **Pinned rebuild config:** `outputs/welfare/stage1_w3/stage3a_pinned_rebuild_config.json`.
- **Provenance JSON:** `outputs/welfare/stage1_w3/stage3a_pinned_baseline_validation.json`
  (all five tasks + readiness).
- **Scratch determinism output:**
  `…/EUROMOD-STORAGE/new_data/scratch_three_a_determinism/` (2 re-run chunks; clearly NOT
  production and NOT the Two-N staging baseline; not committed).
- **Two-N staged baseline (validated here, unchanged):**
  `…/EUROMOD-STORAGE/new_data/staging_twoN/` (21 chunks + 21 markers).

## Explicit scope statement

No re-estimation; no `V_i^dir`; no redrawn-node pricing; no promotion of any staged baseline to
canonical; no production parquet swapped, overwritten, moved, or deleted; nothing beyond `W^3`.
The determinism re-run output went to a scratch directory only. The controlled re-estimation is
a separate authorisation and was NOT performed.
