# JMP Multi-Year Stage M1 — Execution Readiness Report v2

**Document:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v2.md  
**Date:** 2026-05-20  
**Supersedes:** docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md (2026-05-19)  
**Prepared by:** Pipeline execution via Claude Code  
**Authorization references:**
- `docs/JMP_GSUR_year_alignment_decision_v1.md` (Decisions 1–3)
- `docs/JMP_single_year_replication_2015_2017_authorization_v1.md`
- User authorization 2026-05-20 (FR_2016 rebuild and Stage M1 authorization update)

**Supporting reports:**
- `Results/JMP_single_year_consolidated_readiness_verdict_v1.md`
- `Results/JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md`
- `Results/JMP_single_year_FR2016_gsurY2015_rebuild_report_v1.md`
- `Results/JMP_single_year_FR2017_replication_report_v1.md`

---

## 1. Readiness verdict

**Stage M1 P3a (2015+2016+2017) provisional stacking and construction is AUTHORIZED.**

All three per-year MNL-input parquets are present in `Data/processed/fr/`, GSUR-opportunity-year aligned, and confirmed by cell-level rate verification. The Stage M1 P3a dry-run resolves all three years. The HICP deflator CSV is in place. All five Stage M1 reusable scripts execute without errors.

**Authorization scope: provisional only.** All Stage M1 outputs from this authorization must carry the label `provisional_v1_fallback_opportunity_year_aligned` in sidecar metadata and any result tables; labelled filename copies are optional because the configured Stage M1 scripts write fixed output stems. The v1 GSUR fallback (not GSURv2) was used for all three years. Final/reportable pooled estimation is not authorized by this verdict.

---

## 2. What changed since v1

v1 (2026-05-19) stated: **Stage M1 execution is NOT authorized.** The reasons were:

1. EUROMOD outputs for FR_2015 and FR_2017 not produced.
2. MNL parquets for 2015 and 2017 not produced.
3. The 2016 MNL parquet not placed in `Data/processed/fr/`.
4. GSUR opportunity-year alignment not resolved for any year.

Changes since v1, in order:

| Item | v1 status | v2 status | Resolved by |
| ---- | --------- | --------- | ----------- |
| FR_2015 EUROMOD + MNL parquet | ABSENT | **PRESENT** | 5-stage pipeline executed 2026-05-20 |
| FR_2015 GSUR year alignment | UNRESOLVED | **ALIGNED (yr=2014)** | Rebuilt with `--gsur-year 2014`; cell-verified |
| FR_2016 MNL parquet in `Data/processed/fr/` | ABSENT | **PRESENT** | Mirrored 2026-05-20 |
| FR_2016 GSUR year alignment | MISALIGNED (yr=2016 used; yr=2015 correct) | **ALIGNED (yr=2015)** | Rebuilt with `--gsur-year 2015`; cell-verified 2026-05-20 |
| FR_2017 EUROMOD + MNL parquet | ABSENT | **PRESENT** | 5-stage pipeline executed 2026-05-20 |
| FR_2017 GSUR year alignment | UNRESOLVED | **ALIGNED (yr=2016)** | Built with `--gsur-year 2016`; cell-verified |
| HICP deflator CSV | PRESENT (resolved in v1 session) | PRESENT | Option B adopted 2026-05-19 |
| Stage M1 scripts | FUNCTIONAL (v1 session) | FUNCTIONAL | Static validation v3 (2026-05-19) |
| P3a dry-run | BLOCKED (0/3 FOUND) | **READY (3/3 FOUND)** | All inputs now present |

---

## 3. Files inspected

| Document | Sections used |
| -------- | ------------- |
| `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md` | §1 NOT AUTHORIZED verdict; §14 missing inputs; §18 next-task sequence |
| `Results/JMP_single_year_consolidated_readiness_verdict_v1.md` | §3 GSUR alignment table; §9 required steps |
| `Results/JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md` | §§8–11 cell verification, row counts, sidecar |
| `Results/JMP_single_year_FR2016_gsurY2015_rebuild_report_v1.md` | §§7–11,18–19 cell verification, row counts, sidecar, dry-run |
| `Results/JMP_single_year_FR2017_replication_report_v1.md` | §§8–12 cell verification, row counts, sidecar (as corrected 2026-05-20) |
| `docs/JMP_GSUR_year_alignment_decision_v1.md` | Decision 3 (provisional dry-run under v1 fallback) |
| `docs/JMP_multi_year_stage_M1_implementation_plan_v2.md` | §5 configurations; §17 validation checks; §21 what remains blocked |
| `Results/JMP_multi_year_stage_M1_static_validation_report_v3.md` | All checks PASS (2026-05-19) |
| `config/multi_year/fr_p3a_stage_m1.yaml` | Input patterns, year list, UID scheme, blocked_configs gates |

---

## 4. Authorized input set

The provisional P3a input set consists of the following nine files, all present in `Data/processed/fr/`:

| Year | Singles parquet | Couples parquet | Sidecar | GSUR opp. yr | Aligned |
| ---- | --------------- | --------------- | ------- | ------------ | ------- |
| 2015 | `fr_2015_RURO_mnl_v1gsurY2014__singles.parquet` | `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` | `fr_2015_RURO_mnl_v1gsurY2014__mnlmeta.json` | 2014 | ✓ |
| 2016 | `fr_2016_RURO_mnl_v1gsurY2015__singles.parquet` | `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` | `fr_2016_RURO_mnl_v1gsurY2015__mnlmeta.json` | 2015 | ✓ |
| 2017 | `fr_2017_RURO_mnl_v1gsurY2016__singles.parquet` | `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` | `fr_2017_RURO_mnl_v1gsurY2016__mnlmeta.json` | 2016 | ✓ |

The M1-clean single-year operative file `fr_2016_RURO_mnl_GSURv2__` is **not** part of this input set. It remains on Z: and in its own right as the single-year structural baseline. It has been removed from `Data/processed/fr/` to prevent glob collision; the Z: originals are intact.

---

## 5. FR_2015 readiness

| Dimension | Value |
| --------- | ----- |
| EUROMOD system / dataset | FR_2014 / FR_2015_a2 (XML-confirmed) |
| GSUR opportunity year | **2014** |
| GSUR source | `FR_gsur_ruro.parquet` (v1 fallback) |
| GSUR filter applied | `--gsur-year 2014 --year 2015` |
| Cell-level verification | Row0: rate=0.061 = v1 year=2014 exactly; ≠ year=2015 (0.095) |
| Singles: rows × cols | 166,900 × 75 |
| Couples: rows × cols | 256,600 × 93 |
| Singles deciders | 1,669 |
| Couples deciders | 2,566 |
| c_scale singles | 7,565.57 |
| c_scale couples | 15,189.22 |
| Sidecar `gsur_version` | `v1_fallback_opportunity_year_aligned` |
| Sidecar `gsur_opportunity_year` | 2014 |
| Sidecar `gsur_alignment_status` | `aligned` |
| Local mirror size (singles) | 21,467,197 bytes |
| Local mirror size (couples) | 42,977,905 bytes |
| Report | `Results/JMP_single_year_FR2015_gsurY2014_rebuild_report_v1.md` |
| Readiness | **PASS** |

---

## 6. FR_2016 readiness

| Dimension | Value |
| --------- | ----- |
| EUROMOD system / dataset | FR_2015 / FR_2016 (from Z: euromodmeta) |
| GSUR opportunity year | **2015** |
| GSUR source | `FR_gsur_ruro.parquet` (v1 fallback) |
| GSUR filter applied | `--gsur-year 2015 --year 2016` |
| Cell-level verification | 8 disambiguating cells all match v1 year=2015; none match year=2014 or year=2016 |
| Prior misaligned file | `fr_2016_RURO_mnl_GSURv2__` used year=2016 rates (rate=0.153 at row0); correct is year=2015 (0.121) |
| Singles: rows × cols | 167,600 × 75 |
| Couples: rows × cols | 257,700 × 93 |
| Singles deciders | 1,676 |
| Couples deciders | 2,577 |
| c_scale singles | 7,590.29 |
| c_scale couples | 15,106.18 |
| Sidecar `gsur_version` | `v1_fallback_opportunity_year_aligned` |
| Sidecar `gsur_opportunity_year` | 2015 |
| Sidecar `gsur_alignment_status` | `aligned` |
| Local mirror size (singles) | 21,500,531 bytes |
| Local mirror size (couples) | 43,108,696 bytes |
| Report | `Results/JMP_single_year_FR2016_gsurY2015_rebuild_report_v1.md` |
| Readiness | **PASS** |

Note: The M1-clean verdict (`docs/RURO_occ_M1_clean_verdict_v1.md`, LL=−6487.5522) was estimated on `fr_2016_RURO_mnl_GSURv2__` and remains valid for that data. The `v1gsurY2015` file used here differs in GSUR rates; it is for the provisional multi-year pooled route only.

---

## 7. FR_2017 readiness

| Dimension | Value |
| --------- | ----- |
| EUROMOD system / dataset | FR_2016 / FR_2017_a2 (XML-confirmed; euromod Python package with `PYTHONNET_RUNTIME=coreclr`) |
| GSUR opportunity year | **2016** |
| GSUR source | `FR_gsur_ruro.parquet` (v1 fallback) |
| GSUR filter applied | `--gsur-year 2016 --year 2017` |
| Cell-level verification | Row0: rate=0.103 = v1 year=2016 exactly |
| Singles: rows × cols | 166,200 × 75 |
| Couples: rows × cols | 229,500 × 93 |
| Singles deciders | 1,662 |
| Couples deciders | 2,295 |
| c_scale singles | 7,584.12 |
| c_scale couples | 15,137.71 |
| Sidecar `gsur_version` | `v1_fallback_opportunity_year_aligned` |
| Sidecar `gsur_opportunity_year` | 2016 |
| Sidecar `gsur_alignment_status` | `aligned` |
| Local mirror size (singles) | 21,356,869 bytes |
| Local mirror size (couples) | 38,961,983 bytes |
| tpr non-zero (WA) | 0 / 2,364 (0.000%) |
| twl non-zero (WA) | 6 / 2,364 (0.254%) — below 1% threshold |
| Report | `Results/JMP_single_year_FR2017_replication_report_v1.md` |
| Readiness | **PASS** |

---

## 8. GSUR opportunity-year alignment

All three years now use GSUR rates keyed to the EUROMOD system year (opportunity year), not the survey data year. This is required by `docs/JMP_GSUR_year_alignment_decision_v1.md` Decision 2.

| Data year | EUROMOD system | Correct opp. year | File | GSUR year used | Aligned |
| --------- | -------------- | ----------------- | ---- | -------------- | ------- |
| 2015 | FR_2014 | 2014 | `v1gsurY2014__` | **2014** | ✓ |
| 2016 | FR_2015 | 2015 | `v1gsurY2015__` | **2015** | ✓ |
| 2017 | FR_2016 | 2016 | `v1gsurY2016__` | **2016** | ✓ |

All three sidecars carry:
- `gsur_version: v1_fallback_opportunity_year_aligned`
- `gsur_alignment_status: aligned`
- `gsur_alignment_rule: opportunity_year = euromod_system_year`
- Correct `gsur_opportunity_year` values (2014, 2015, 2016 respectively)

**GSUR source:** `FR_gsur_ruro.parquet` (v1 fallback) for all three years. GSURv2 rates exist only for 2016 in `FR_gsur_ruro_v2_stageA.parquet` and are not used in this provisional input set. The v1 fallback is accepted under Decision 3, subject to the provisional labelling requirement.

---

## 9. CPI/HICP readiness

| Item | Status |
| ---- | ------ |
| `Data/external/cpi_hicp_fr_harmonisation.csv` | **PRESENT** (written 2026-05-19) |
| Decision | Option B — EUROMOD HICP from HICPCONFIG.xml (Eurostat/AMECO, base 2015=100) |
| Decision document | `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md` |
| φ_t values | 2015: 1.0031 / 2016: 1.0000 / 2017: 0.9886 / 2018: 0.9682 |
| Maximum φ_t deviation | < 3.2% over the 2015–2018 window |
| Ready for `m1_harmonise_cpi.py` | **YES** |

This status is unchanged from v1. The HICP CSV was created in the v1 session and remains valid.

---

## 10. Identifier and raw-ID readiness

All four required Stage M1 raw-ID columns are present and non-null in all six parquets:

| Column | FR_2015 s/c | FR_2016 s/c | FR_2017 s/c |
| ------ | ----------- | ----------- | ----------- |
| `idhh` | ✓ / ✓ | ✓ / ✓ | ✓ / ✓ |
| `idperson` | ✓ / ✓ | ✓ / ✓ | ✓ / ✓ |
| `idorighh` | ✓ / ✓ | ✓ / ✓ | ✓ / ✓ |
| `idorigperson` | ✓ / ✓ | ✓ / ✓ | ✓ / ✓ |

(s = singles, c = couples)

The B = 10^11 UID scheme (`stacked_hh_uid = year_tag × B + idhh`, `stacked_person_uid = year_tag × B + idperson`) is safe for all three years: the binding constraint is `idperson` max ≈ 9.4 × 10^9 (2016) < 10^11 = B. No cross-year collision is possible (per implementation plan v2 §10).

---

## 11. Metadata sidecar readiness

All three `__mnlmeta.json` sidecars are present locally and carry all required alignment fields. Summary:

| Field | 2015 | 2016 | 2017 |
| ----- | ---- | ---- | ---- |
| `year` | 2015 | 2016 | 2017 |
| `gsur_version` | `v1_fallback_opportunity_year_aligned` | `v1_fallback_opportunity_year_aligned` | `v1_fallback_opportunity_year_aligned` |
| `gsur_opportunity_year` | 2014 | 2015 | 2016 |
| `gsur_data_year` | 2015 | 2016 | 2017 |
| `gsur_alignment_rule` | `opportunity_year = euromod_system_year` | `opportunity_year = euromod_system_year` | `opportunity_year = euromod_system_year` |
| `gsur_alignment_status` | `aligned` | `aligned` | `aligned` |
| `sample_sizes.singles_deciders` | 1,669 | 1,676 | 1,662 |
| `sample_sizes.couples_deciders` | 2,566 | 2,577 | 2,295 |
| `sample_sizes.n_draws` | 100 | 100 | 100 |

**Sidecar readiness: PASS** for all three years.

---

## 12. Stage M1 dry-run result

```
======================================================================
DRY RUN -- config=p3a  years=[2015, 2016, 2017]
Config YAML: ...\config\multi_year\fr_p3a_stage_m1.yaml
======================================================================

Inputs:
  [2015]  FOUND  ...\Data\processed\fr\fr_2015_RURO_mnl_v1gsurY2014__couples.parquet  (41.0 MB)
  [2016]  FOUND  ...\Data\processed\fr\fr_2016_RURO_mnl_v1gsurY2015__couples.parquet  (41.1 MB)
  [2017]  FOUND  ...\Data\processed\fr\fr_2017_RURO_mnl_v1gsurY2016__couples.parquet  (37.2 MB)

Planned output: ...\Data\processed\fr\pooled\fr_p3a_stacked_raw.parquet

Status: all inputs present -- ready to run without --dry-run

UID scheme (B=100,000,000,000):
  year=2015  tag=1  stacked range = [100,000,000,001 to 199,999,999,999]
  year=2016  tag=2  stacked range = [200,000,000,001 to 299,999,999,999]
  year=2017  tag=3  stacked range = [300,000,000,001 to 399,999,999,999]

Raw IDs to preserve: ['idorighh', 'idorigperson', 'idhh', 'idperson']
No parquet written (dry-run mode).
```

- 2015: **FOUND** → `fr_2015_RURO_mnl_v1gsurY2014__couples.parquet` (glob pattern 3: `*{year}*RURO*mnl*.parquet`)
- 2016: **FOUND** → `fr_2016_RURO_mnl_v1gsurY2015__couples.parquet` (glob pattern 3)
- 2017: **FOUND** → `fr_2017_RURO_mnl_v1gsurY2016__couples.parquet` (glob pattern 3)

All three years resolve through glob pattern 3 (`*{year}*RURO*mnl*.parquet`). None of the `*job*gmm*` or `*job*` patterns match because no job-model parquets are present in `Data/processed/fr/`.

Dry-run: **Status: all inputs present — ready to run without `--dry-run`.**

---

## 13. Remaining limitations

The following limitations apply to all outputs produced under this authorization. They are not blocking for provisional stacking but must be disclosed in any downstream output that cites results.

| Limitation | Detail |
| ---------- | ------ |
| **v1 GSUR fallback** | All three years use `FR_gsur_ruro.parquet` (v1), not GSURv2. v1 rates are broad-age-band aggregates. GSURv2 Stage A rates exist only for 2016. The provisional label is required until GSURv2 is extended to 2015 and 2017, or until a separate verdict explicitly accepts the v1 fallback as final. |
| **No GSURv2 for 2015 and 2017** | Requires Eurostat denominators (`lfst_r_lfsd2pop`, `lfst_r_lfp2acedu` for 2015/2017) and INSEE BDM 001688526 annual averages. These are not acquired. |
| **tpr/twl asymmetry** | 2015 carries `tpr` (property tax, 0.344% WA incidence); 2016 and 2017 carry `twl` (ISF wealth tax, ~0.29% WA incidence). All three are below the 1% escalation threshold; see `Results/JMP_multi_year_stage_M1_readiness_addendum_v2.md`. P3b (2015+2016+2018) remains hard-blocked pending `Results/M1_ISF_tpr_comparability_check_2018.md`. |
| **M1-clean single-year baseline** | The M1-clean single-year structural estimates (LL=−6487.5522, 53 parameters) used `fr_2016_RURO_mnl_GSURv2__` as operative data. The v1gsurY2015 FR_2016 file used in Stage M1 has different GSUR rates; any pooled estimation result will not be directly comparable to M1-clean on this dimension. |
| **HICP proxy deflator** | The CPI φ_t values are from EUROMOD HICPCONFIG.xml (Eurostat/AMECO), not INSEE domestic CPI. Maximum deviation < 3.2% over 2015–2018. Disclosed in `docs/JMP_multi_year_CPI_HICP_source_decision_v1.md`. |
| **No cluster-robust SE wrapper** | The pooled estimation SE wrapper for T1 cluster-robust standard errors (clustering on `idorighh`) is not yet implemented. Stage M1 constructs the `cluster_id` column; the estimation-level usage requires a separate implementation step. |
| **P3b hard-blocked** | `fr_p3b_stage_m1.yaml` `blocked_configs` gate remains active. P3b is not executable until `Results/M1_ISF_tpr_comparability_check_2018.md` concludes "proceed with p3b." |

---

## 14. What Stage M1 execution is authorized to do

Under this authorization, the following Stage M1 steps may be executed once the operator is ready:

| Step | Script | Action |
| ---- | ------ | ------ |
| 1 | `m1_stack_years.py --config p3a` | Stack the three per-year parquets; assign `year_tag`, `stacked_hh_uid`, `stacked_person_uid`; preserve raw IDs; write `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet`; create or verify a matching label sidecar |
| 2 | `m1_identity_validation.py --config p3a` | Run §13 person-identity diagnostics on stacked-raw file; write `Results/M1_identity_validation_summary.md` |
| 3 | `m1_harmonise_cpi.py --config p3a` | Read `cpi_hicp_fr_harmonisation.csv`; add `*_real` deflated columns per year; write `Data/processed/fr/pooled/fr_p3a_harmonised.parquet`; create or verify a matching label sidecar |
| 4 | `m1_add_cluster_key.py --config p3a` | Add `cluster_id = idorighh`; may be embedded in step 3 |
| 5 | `m1_validate.py --config p3a` | Run V1–V9 validation checks; write `Results/M1_*` manifests |

All five scripts are confirmed functional (static validation v3, 2026-05-19). The command sequence is in `docs/JMP_multi_year_stage_M1_implementation_plan_v2.md` §18 Gate 4.

---

## 15. What remains unauthorized

| Action | Status |
| ------ | ------ |
| Stage M1 P3a live stacking (steps 1–5 above) | **NEWLY AUTHORIZED** (provisional) |
| Stage M1 P3b stacking | **NOT AUTHORIZED** — hard-blocked gate |
| Stage M1 P4 stacking | **NOT AUTHORIZED** — hard-blocked gate |
| Stage M1 P2 stacking | Not yet addressed; may proceed after P3a completes (inputs present) |
| Pooled estimation (P3a) | **NOT AUTHORIZED** — requires cluster-robust SE wrapper and pooled estimation spec |
| Pooled estimation (P3b) | **NOT AUTHORIZED** — additionally blocked on ISF check |
| Welfare computation | **NOT AUTHORIZED** — welfare decisions and scaffolding design exist, but computation remains blocked pending an accepted empirical baseline and separate welfare implementation/audit authorization |
| Welfare scaffolding implementation | **NOT AUTHORIZED** — design is complete; implementation remains deferred until the pooled-route decision or an explicit M1-clean fallback decision |
| Canonical MNL model promotion | **NOT AUTHORIZED** — M1-clean single-year (2016) result remains canonical baseline |
| GSUR Stage B (age-specific weights) | **NOT AUTHORIZED** |
| GSURv2 extension to 2015/2017 | **NOT AUTHORIZED** here — requires Eurostat denominator acquisition |
| P3b activation | **NOT AUTHORIZED** — requires ISF comparability memo |
| FR_2018 pipeline run | **NOT AUTHORIZED** — no authorization exists for 2018 |

---

## 16. Required output labels

All outputs produced from Stage M1 stacking under this authorization must carry the following label:

**`provisional_v1_fallback_opportunity_year_aligned`**

The current Stage M1 configuration writes fixed output filenames:

- `Data/processed/fr/pooled/fr_p3a_stacked_raw.parquet`
- `Data/processed/fr/pooled/fr_p3a_harmonised.parquet`

Because those filenames do not themselves contain the provisional label, the label must appear in sidecar metadata at minimum. Labelled filename copies are allowed, but the sidecar requirement remains binding.

Required sidecar fields for each Stage M1 output:

```json
{
  "provisioning_label": "provisional_v1_fallback_opportunity_year_aligned",
  "gsur_source_status": "v1_fallback",
  "gsur_alignment_rule": "opportunity_year = euromod_system_year",
  "pooled_estimation_authorized": false,
  "welfare_computation_authorized": false
}
```

The label must also appear:
- In the first line of any result table or report that cites pooled statistics derived from this dataset.
- In any estimation results file sidecar that uses this dataset as input.

The label documents three properties simultaneously:
1. **provisional** — not final for publication; may be superseded by GSURv2 rates.
2. **v1_fallback** — GSUR rates from `FR_gsur_ruro.parquet` (v1), not GSURv2 Stage A.
3. **opportunity_year_aligned** — GSUR key = EUROMOD system year for all three years.

---

## 17. Whether pooled estimation is authorized

**Pooled estimation is NOT authorized.**

Stage M1 produces the stacked and harmonised input dataset. Two additional prerequisites for pooled estimation are not yet in place:

1. **Cluster-robust SE wrapper:** The variance estimator for T1 cluster-robust standard errors (clustering on `idorighh`) is not implemented. The `cluster_id` column will be present in the harmonised parquet after Stage M1, but the estimation engine (`enh_RURO_estimate_FR.py`) has no cluster-robust SE path.

2. **Pooled estimation specification:** No YAML or design memo specifies the multi-year pooled model. The M1-clean specification (`estimation_spec_ruro_occ_M1_clean.yaml`) was designed for single-year (2016) data. A pooled estimation spec must be written before any pooled run.

Additionally, the provisional v1 GSUR fallback means that any pooled estimation result would carry the provisional label and could not be reported as final in the JMP. Final/reportable pooled estimation requires either: (a) GSURv2 rates extended to 2015 and 2017, or (b) a separate explicit verdict accepting the v1 fallback as final with documented rationale.

---

## 18. Whether welfare computation is authorized

**Welfare computation is NOT authorized.**

This report corrects the outdated v1 wording. The welfare-measurement decisions and welfare-scaffolding design are already complete:

1. `docs/JMP_welfare_measurement_decisions_memo_v2.md`
2. `docs/JMP_welfare_scaffolding_design_memo_v2.md`

Those documents lock the welfare object, inequality/decomposition design, and scaffolding architecture. They do not authorize welfare implementation or welfare computation.

Stage M1 remains a data-construction step only. Welfare computation remains blocked until either:

1. the pooled route earns a later SA2 verdict and becomes the accepted empirical baseline; or
2. the project explicitly stops the pooled route and proceeds with M1-clean 2016 as the empirical baseline.

Even after one of those baseline decisions, welfare implementation and welfare computation require their own implementation report, audit, and authorization. Stage M1 makes no welfare progress and creates no welfare outputs.

---

## 19. PASS / FAIL verdict

| Check | Result |
| ----- | ------ |
| FR_2015 parquet present locally | **PASS** |
| FR_2015 GSUR opportunity year = 2014 (cell-verified) | **PASS** |
| FR_2015 sidecar: `v1_fallback_opportunity_year_aligned` | **PASS** |
| FR_2016 parquet present locally | **PASS** |
| FR_2016 GSUR opportunity year = 2015 (cell-verified, 8 disambiguating cells) | **PASS** |
| FR_2016 sidecar: `v1_fallback_opportunity_year_aligned` | **PASS** |
| FR_2017 parquet present locally | **PASS** |
| FR_2017 GSUR opportunity year = 2016 (cell-verified) | **PASS** |
| FR_2017 sidecar: `v1_fallback_opportunity_year_aligned` | **PASS** |
| All six parquets: zero missing `gsur` | **PASS** |
| All four raw-ID columns present in all six parquets | **PASS** |
| HICP deflator CSV present | **PASS** |
| Stage M1 scripts functional (static validation v3) | **PASS** |
| P3a dry-run: 2015 FOUND | **PASS** |
| P3a dry-run: 2016 FOUND (v1gsurY2015, not GSURv2) | **PASS** |
| P3a dry-run: 2017 FOUND | **PASS** |
| P3a dry-run status: READY | **PASS** |
| P3b gate: hard-blocked | **PASS** (correct behavior) |
| P4 gate: hard-blocked | **PASS** (correct behavior) |
| M1-clean operative files on Z: untouched | **PASS** |
| No estimation or welfare authorized | **CONFIRMED** |

**Overall PASS — Stage M1 P3a provisional stacking is authorized.**

---

## 20. Exact next task

**Run Stage M1 P3a stacking.**

```powershell
# Step 1: Stack
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\multi_year\m1_stack_years.py" `
    --config p3a

# Step 2: Identity validation
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\multi_year\m1_identity_validation.py" `
    --config p3a

# Step 3: CPI harmonisation
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\multi_year\m1_harmonise_cpi.py" `
    --config p3a

# Step 4: Cluster key
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\multi_year\m1_add_cluster_key.py" `
    --config p3a

# Step 5: Validation
& "U:\Desktop\Nizam_Hisham\MNL\.venv\Scripts\python.exe" `
    "U:\Desktop\Nizam_Hisham\MNL\scripts\multi_year\m1_validate.py" `
    --config p3a
```

**Before running step 1:** confirm `Data/processed/fr/pooled/` is empty (no stale parquet from a prior dry-run test). The stacking script will write `fr_p3a_stacked_raw.parquet` there.

**Required output label:** All outputs must carry `provisional_v1_fallback_opportunity_year_aligned` (§16). Because the configured parquet filenames are fixed, the Stage M1 execution report must create or verify at least these two sidecars:

```text
Data/processed/fr/pooled/fr_p3a_stacked_raw__stage_m1_meta.json
Data/processed/fr/pooled/fr_p3a_harmonised__stage_m1_meta.json
```

Each sidecar must contain `provisioning_label: "provisional_v1_fallback_opportunity_year_aligned"` and explicitly state that pooled estimation and welfare computation are not authorized.

**Post-execution deliverable:** Write `Results/JMP_multi_year_stage_M1_P3a_execution_report_v1.md` documenting the stacking run, validation results (V1–V9), and identity-validation diagnostics. That report is the prerequisite for any downstream pooled estimation authorization.

**What this does NOT unlock:** pooled estimation, welfare computation, canonical MNL promotion, P3b, or any modification to the M1-clean single-year specification.

---

*This report supersedes `docs/JMP_multi_year_stage_M1_execution_readiness_report_v1.md` for the purposes of Stage M1 P3a execution authorization. The v1 document remains in place as a historical record of the pre-execution readiness assessment.*
