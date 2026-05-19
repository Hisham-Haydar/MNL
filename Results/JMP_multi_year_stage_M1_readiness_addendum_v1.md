# JMP Multi-Year Stage M1 — Readiness Addendum

**Document:** Results/JMP_multi_year_stage_M1_readiness_addendum_v1.md
**Date:** 2026-05-19
**Addendum to:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md
**Reason:** User review identified two points requiring tighter treatment before the readiness package is accepted as clean.

---

## Issue 1 — HICP adoption is provisional, not a permanent replacement of INSEE CPI

### Clarification

The execution readiness report correctly records that `Data/external/cpi_hicp_fr_harmonisation.csv` was written with EUROMOD HICP φ_t values (Option B), and that the decision memo (`docs/JMP_multi_year_CPI_HICP_source_decision_v1.md`) labels this provisional. This addendum makes the provisional status explicit at the package level.

### Status

**Execution-ready, not final.**

The HICP CSV was created to unblock Stage M1 from a CPI-file perspective. The φ_t values are:

| Year | φ_t |
| --- | --- |
| 2015 | 1.0031 |
| 2016 | 1.0000 |
| 2017 | 0.9886 |
| 2018 | 0.9682 (P3b only) |

Maximum deviation across 2015–2017 window: 0.0031 (0.31%) between 2015 and 2016. All three φ_t values are within 1.2% of 1.0.

### What provisional means

- The HICP CSV **may be used** to run Stage M1 harmonisation. There is no methodological barrier to doing so.
- If the INSEE IPC (all-items, metropolitan France, annual average) is later retrieved and any φ_t differs from the HICP value by more than 0.5 percentage points, the CSV must be rewritten and all harmonised parquets must be rebuilt from the stacked raw parquets.
- Given the small magnitude of φ_t (maximum 3.2% deviation over 2015–2018), the probability of a material difference is low. The JMP paper must include the disclosure note in `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md §1`.
- The HICP decision does **not** require re-authorisation before Stage M1 execution. It is already authorised by this package.

### Condition to make it final

Retrieve INSEE IPC (BDM series accessible at data.gouv.fr or the INSEE API). If retrieved: compare row-by-row with HICP φ_t; if max difference < 0.5 pp, replace the `notes` column in the CSV with "INSEE IPC confirmed consistent with HICP; adoption permanent"; if difference ≥ 0.5 pp on any year, rewrite φ_t values and rebuild harmonised parquets.

---

## Issue 2 — 2015 `tpr` and `twl`: income-definition asymmetry in P3a

### Background: what the implementation plan says

The implementation plan v2 §16 states that "`tpr` is present in FR_2015 and FR_2018 but absent from FR_2016 and FR_2017 (ISF was replaced by IFI in 2018...)." It also says the ISF/`tpr` comparability check "is a prerequisite for P3b execution but not for P3a."

The user correctly flagged that P3a includes 2015, and that if 2015 has `tpr` non-zero while 2016/2017 do not, there is an income-definition asymmetry in P3a too — not only in P3b.

### Empirical findings (inspected 2026-05-19)

**Variable nomenclature clarification (from EUROMOD ILS definitions):**

The EUROMOD standard income concepts file (`Data/documentation/euromod_fr_2015_2017_standard_income_concepts.csv`) establishes:

- `tpr` = **"Property taxes"** (e.g. taxe foncière / taxe d'habitation precursor). Enters `ils_tax` in FR_2015, FR_2016, and FR_2017.
- `twl` = **"Wealth tax (ISF)"** — the actual ISF variable. Also enters `ils_tax` in all three years.

The implementation plan §16 uses "`tpr`" loosely as shorthand for "wealth/property tax variable." The precise variable for the ISF wealth tax is `twl`, not `tpr`. This distinction matters for the asymmetry assessment.

**Raw input file inspection:**

| Year | `tpr` in raw input file | `twl` in raw input file |
| --- | --- | --- |
| FR_2015_a2.txt | **YES** — 108 non-zero rows out of 26,558 (0.41% of all; 0.34% of working-age 18–64) | Not checked (twl is EUROMOD-simulated output, not a raw EU-SILC input) |
| FR_2016_a3.txt | **NO** — column absent | — |
| FR_2017_a2.txt | **NO** — column absent | — |

`tpr` in FR_2015 is an **observed EU-SILC input** (raw property tax paid, from French tax records), not a EUROMOD simulation. EUROMOD reads it and passes it through to `ils_tax` and `ils_dispy`.

In FR_2016 and FR_2017, there is no `tpr` raw input column. The 2016 MNL parquet (`fr_2016_RURO_mnl_job_gmm__singles.parquet`) has `tpr` with all-zeros (335,200 rows, 0 non-zero) — consistent with EUROMOD outputting zero property tax for 2016.

**Scale of the 2015 tpr effect:**

For working-age individuals (dag 18–64) in FR_2015:
- 53 out of 15,414 working-age rows have `tpr > 0` (0.344%)
- Mean monthly `tpr` for affected rows: €550.59 (annual: ~€6,607)
- Max monthly `tpr`: €3,675.58 (annual: ~€44,100)
- Median monthly `tpr` for affected rows: €416.67 (annual: ~€5,000)

`tpr` enters `ils_tax` with a positive sign (increases taxes), which reduces `ils_dispy`:

`ils_dispy = ils_origy + benefits − ils_tax`

For the 53 affected working-age rows, `tpr` reduces annual `ils_dispy` by a mean of ~€6,607.

### Assessment: is this a material P3a asymmetry?

**The asymmetry exists but is likely negligible in the P3a context for the following reasons:**

1. **Incidence is 0.34% of working-age sample.** Fewer than 1 in 300 working-age individuals are affected. In any RURO estimation sample of ~10,000–15,000 person-rows, approximately 34–51 rows would carry non-zero `tpr`. These are effectively statistical noise in the pooled regression.

2. **The RURO sample further restricts to employees and unemployed (les codes 1, 3, 5).** Among the 53 working-age rows with `tpr > 0`, the les distribution shows codes 3, 4, 2, 9, 5, 8, 7. Code 3 (employee) dominates, but the RURO sample restriction and the draw expansion will further dilute these observations.

3. **tpr is a property tax, not an employment-income tax.** It affects `ils_dispy` but not `ils_earns` or the wage distribution. The RURO utility function is driven primarily by wage and employment status; a small reduction in `ils_dispy` for 0.34% of observations is unlikely to shift estimated preference parameters measurably.

4. **The asymmetry is structurally different from the P3b/2018 ISF issue.** The concern for P3b §16 was that the EUROMOD-simulated ISF in 2018 (`twl`) affects `ils_dispy` for a non-trivial share of the RURO sample, creating a systematic income-concept asymmetry between 2018 and 2016/2017. For 2015, the property tax (`tpr`) is an observed EU-SILC input affecting 0.34% of working-age rows — structurally much less concerning.

5. **tpr appears in the ILS definition for 2016 and 2017 as well.** The `ils_tax` definition includes `tpr` in all three years (FR_2015, FR_2016, FR_2017). In 2016 and 2017 it is zero for all rows because the raw input file does not contain the column. This is symmetric treatment: all years have `tpr` in the `ils_tax` aggregate, but only 2015 has non-zero values. There is no evidence that EUROMOD treats the 2015 property tax conceptually differently from 2016/2017.

### Does P3a require an analogue to the P3b ISF check?

**No — but the 2015 `tpr` asymmetry should be documented and the affected rows flagged in the harmonised parquet.**

Recommended action (not blocking for Stage M1 execution):

1. After EUROMOD is run for FR_2015 and the MNL parquet is produced: confirm the share of RURO-sample rows with `tpr > 0`. If it exceeds 1% (well above the 0.34% seen in raw data), escalate to a formal comparability check.
2. Add `tpr` to the metadata sidecar (`mnlmeta.json`) as a flagged variable when non-zero.
3. In the final M1 validation report, report the count and percentage of observations with `tpr > 0` per year, as a data quality annotation — not a blocking check.
4. The JMP draft should note: "The 2015 year in the P3a panel includes 0.3–0.4% of working-age observations with non-zero property tax (`tpr`) entered as an observed EU-SILC input; the corresponding values are zero in 2016 and 2017. This creates a minor income-definition asymmetry that is negligible given the incidence rate."

### Conclusion on the tpr/P3a question

**P3a does not require an analogue to the P3b ISF check.** The asymmetry is real, small (0.34% incidence), structurally distinct from the 2018 ISF simulation issue, and documentable at validation time rather than as a gate. The "Stage M1 execution is NOT authorized" verdict from the execution readiness report is unchanged and is driven by the absent EUROMOD outputs and MNL parquets — not by the `tpr` issue.

**The implementation plan §16 footnote should be corrected** to clarify that `tpr` = property tax (not ISF wealth tax = `twl`) and that 2015 `tpr` is an observed input at 0.34% incidence, not a EUROMOD simulation.

---

## Issue 3 — 2016 MNL input: copy locally vs. update YAML

### The choice

The 2016 MNL parquet exists at:
`Z:\hisham\EUROMOD-STORAGE\Data\processed\fr\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet`

The M1 config `input_parquet_dir: Data/processed/fr` resolves to the repo-local path. There are two ways to make m1_stack_years.py find it:

**Option L — Copy locally:**
```powershell
Copy-Item "Z:\...\2016\fr_2016_RURO_mnl_job_gmm__singles.parquet" "Data\processed\fr\"
Copy-Item "Z:\...\2016\fr_2016_RURO_mnl_job_gmm__mnlmeta.json"    "Data\processed\fr\"
```

**Option Z — Point YAML at Z: path:**
Change `input_parquet_dir: Data/processed/fr` to `input_parquet_dir: Z:/hisham/EUROMOD-STORAGE/Data/processed/fr` in all four config YAMLs.

### Recommendation: **Option L (copy locally)**

| Criterion | Option L (copy) | Option Z (YAML → Z:) |
| --- | --- | --- |
| Repo portability | **Good** — repo self-contained | **Bad** — breaks on any machine without Z: mapped |
| Reproducibility | Good — local files are versioned | Poor — Z: path is institutional; content may change |
| Disk space | Costs ~250 MB per year (singles parquet) | None |
| Consistency across 2015/2016/2017 | All three years in same local dir | All three on Z: (acceptable if Z: always accessible) |
| git tracking | Parquets in `.gitignore`; sidecar JSON can be tracked | Neither tracked |
| Stage M1 output | Pooled output stays in repo-local `Data/processed/fr/pooled/` | Same |

**Option L is preferred.** The Z: drive is institutional shared storage; its availability cannot be guaranteed from all execution environments. The local `Data/processed/fr/` directory is the intended home for per-year MNL inputs, consistent with the Stage M1 YAML design. Parquet files should be `.gitignore`'d (large binaries) but their existence in the local directory is required for script execution.

**This recommendation applies to all three years.** When 2015 and 2017 MNL parquets are produced (after EUROMOD runs), they should be placed in `Data/processed/fr/` alongside the 2016 file. The Z: originals remain as the authoritative storage copy.

---

## Summary

| Issue | Status | Blocking? |
| --- | --- | --- |
| HICP provisional adoption | Execution-ready; INSEE IPC retrieval deferred | Not blocking |
| 2015 `tpr` asymmetry in P3a | Negligible (0.34% incidence); document at validation; no analogue ISF check needed | Not blocking |
| 2016 MNL local copy vs. YAML | Copy to `Data/processed/fr/` recommended (Option L) | Not blocking (either option works) |

**Final readiness classification: NOT AUTHORIZED — unchanged.**

The readiness package is now clean. No gate has been removed. Stage M1 execution remains blocked on EUROMOD outputs for FR_2015/FR_2017 and MNL parquets for all three years (including 2016 placement). The two caveats raised in the user review are resolved by clarification and empirical analysis, not by code changes or new gates.