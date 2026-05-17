# RURO GSUR v2 Stage A MNL Rebuild Report v1

Date: 2026-05-17
Run timestamp: 2026-05-17T20:05:56Z
Script: `scripts/enhanced/enh_RURO_mnl_rebuild_GSURv2_stageA.py`
Prompt: `Prompts/RURO_GSUR_v2_stageA_MNL_rebuild_prompt_corrected_v2.md`
Authorisation: `docs/RURO_GSUR_O7_crosswalk_signoff_v1.md`

---

## 1. Overall verdict

| Item | Value |
|---|---|
| **Overall result** | **PASS** |
| Hard checks failed | 0 |
| M12-diag (hard) | **PASS** |
| Re-estimation authorized | YES — all hard checks PASS |

---

## 2. Input files (canonical, read-only)

| File | Rows | Size | mtime (before task) |
|---|---|---|---|
| `fr_2016_RURO_mnl__singles.parquet` | 167,600 | 21,500,551 bytes | 2026-05-13T10:38:21Z |
| `fr_2016_RURO_mnl__couples.parquet` | 257,700 | 43,108,822 bytes | 2026-05-13T10:38:22Z |
| `Data/external/FR_gsur_ruro_v2_stageA.parquet` | 54 | — | — |

---

## 3. Output files (versioned)

| File | Rows | Size | mtime (after task) |
|---|---|---|---|
| `fr_2016_RURO_mnl_GSURv2__singles.parquet` | 167,600 | 21,510,188 bytes | 2026-05-17T22:05:57Z |
| `fr_2016_RURO_mnl_GSURv2__couples.parquet` | 257,700 | 43,130,386 bytes | 2026-05-17T22:05:59Z |

---

## 4. M1 — Value-identical non-GSUR columns

| Item | Singles | Couples |
|---|---|---|
| Columns checked | 74 | 91 |
| Columns failed | 0 | 0 |
| Failed cols | [] | [] |
| **Result** | **PASS** | **PASS** |

---

## 5. M2 — GSUR column schema

**Singles** — missing columns: `[]` → **PASS**

**Couples** — missing columns: `[]` → **PASS**

---

## 6. M3 — No NaN in gsur

| Item | Singles | Couples |
|---|---|---|
| NaN count (singles gsur) | 0 | — |
| NaN count (couples gsur_male) | — | 0 |
| NaN count (couples gsur_female) | — | 0 |
| **Result** | **PASS** | **PASS** |

---

## 7. M4 — Île-de-France parity (hard pass/fail, tolerance 0.001)

This check confirms that the rebuilt `gsur` column in the versioned parquet
equals the validated Stage A lookup value for drgn1=1 households.

**Singles — per (educ3, sex) cell:**

| educ3 | sex | parquet gsur | lookup gsur | diff |
|---|---|---|---|---|
| 0 | F | 0.153000 | 0.153000 | 0.000000 |
| 0 | M | 0.164000 | 0.164000 | 0.000000 |
| 1 | F | 0.103000 | 0.103000 | 0.000000 |
| 1 | M | 0.110000 | 0.110000 | 0.000000 |
| 2 | F | 0.058000 | 0.058000 | 0.000000 |
| 2 | M | 0.056000 | 0.056000 | 0.000000 |

max |diff| = 0.000000 → **PASS**

**Couples** — max |diff| male = 0.000000,
female = 0.000000 → **PASS**

---

## 8. M4-diag — v1→v2 correction magnitude by drgn1 (diagnostic)

Large differences expected for low-educ (educ3=0) and high-educ (educ3=2) cells
because v1 `gsur` was not education-stratified.

Overall mean |diff| (singles): 0.0166
Overall max |diff| (singles): 0.1060

Result: DOCUMENTED (not pass/fail)

---

## 9. M5 — Age-band assignment

| Item | Singles | Couples |
|---|---|---|
| dag==65 rows | 200 | (see below) |
| dag==65 with wrong label | 0 | — |
| dag<65 rows | 167400 | (see below) |
| dag<65 with wrong label | 0 | — |
| **Result** | **PASS** | **PASS** |

Couples detail (partners): {'male': {'n_age65': 0, 'n_wrong_label_age65': 0, 'n_age_lt65': 257700, 'n_wrong_label_lt65': 0}, 'female': {'n_age65': 0, 'n_wrong_label_age65': 0, 'n_age_lt65': 257700, 'n_wrong_label_lt65': 0}}

---

## 10. M6 — Partner-specific consistency (couples, documented)

| Item | Value |
|---|---|
| Active rows | 257,700 |
| Rows with gsur_male == gsur_female | 0 |
| Fraction identical | 0.0% |
| Note | Expected ~15%; if 100% merge applied identical values to both partners |

Result: DOCUMENTED

---

## 11. M7 — Row count preservation

| Parquet | Expected rows | Actual rows | Expected HH | Actual HH | Result |
|---|---|---|---|---|---|
| Singles | 167,600 | 167,600 | 1,676 | 1,676 | **PASS** |
| Couples | 257,700 | 257,700 | 2,577 | 2,577 | **PASS** |

---

## 12. M8 — Forensic record preservation

`gsur_legacy_misaligned` must equal the actual v1 canonical `gsur` value (column-wise).

**Singles:**
- value_identical = True
- max_abs_diff = 0.0
- **Result: **PASS****

**Couples (male):**
- value_identical = True
- max_abs_diff = 0.0

**Couples (female):**
- value_identical = True
- max_abs_diff = 0.0

**Result couples: **PASS****

---

## 13. M9 — Cross-stage load compatibility

| Item | Singles | Couples |
|---|---|---|
| Readable by pd.read_parquet | Yes | Yes |
| gsur dtype | {'gsur': 'float64'} | {'gsur_male': 'float64', 'gsur_female': 'float64'} |
| gsur is numeric float | True | True |
| **Result** | **PASS** | **PASS** |

---

## 14. M10 — Versioned path / canonical untouched

| Item | Value |
|---|---|
| canonical singles mtime before | 2026-05-13T10:38:21Z |
| canonical singles mtime after | 2026-05-13T10:38:21Z |
| canonical singles unchanged | True |
| canonical couples mtime before | 2026-05-13T10:38:22Z |
| canonical couples mtime after | 2026-05-13T10:38:22Z |
| canonical couples unchanged | True |
| versioned singles exists | True |
| versioned couples exists | True |
| **Result** | **PASS** |

---

## 15. M11-diag — GSUR distribution by demographic cell

### Singles (drgn1 × dgn × educ3)

| drgn1 | dgn | educ3 | n | mean gsur v2 | mean gsur v1 | mean diff | max|diff| |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 0 | 2400 | 0.1530 | 0.1530 | +0.0000 | 0.0000 |
| 1 | 0 | 1 | 5500 | 0.1030 | 0.1030 | -0.0000 | 0.0000 |
| 1 | 0 | 2 | 8000 | 0.0580 | 0.0580 | +0.0000 | 0.0000 |
| 1 | 1 | 0 | 1600 | 0.1640 | 0.1640 | +0.0000 | 0.0000 |
| 1 | 1 | 1 | 2700 | 0.1100 | 0.1100 | +0.0000 | 0.0000 |
| 1 | 1 | 2 | 6900 | 0.0560 | 0.0560 | +0.0000 | 0.0000 |
| 2 | 0 | 0 | 1700 | 0.1487 | 0.1250 | +0.0237 | 0.0237 |
| 2 | 0 | 1 | 5900 | 0.1107 | 0.1310 | -0.0203 | 0.0203 |
| 2 | 0 | 2 | 5600 | 0.0561 | 0.0480 | +0.0081 | 0.0081 |
| 2 | 1 | 0 | 2800 | 0.1680 | 0.1590 | +0.0090 | 0.0090 |
| 2 | 1 | 1 | 7400 | 0.1011 | 0.0990 | +0.0021 | 0.0021 |
| 2 | 1 | 2 | 3500 | 0.0565 | 0.0480 | +0.0085 | 0.0085 |
| 3 | 0 | 0 | 1100 | 0.2300 | 0.1240 | +0.1060 | 0.1060 |
| 3 | 0 | 1 | 3100 | 0.1330 | 0.0770 | +0.0560 | 0.0560 |
| 3 | 0 | 2 | 3900 | 0.0700 | 0.0560 | +0.0140 | 0.0140 |
| 3 | 1 | 0 | 1000 | 0.2340 | 0.1720 | +0.0620 | 0.0620 |
| 3 | 1 | 1 | 1600 | 0.1350 | 0.0890 | +0.0460 | 0.0460 |
| 3 | 1 | 2 | 1900 | 0.0670 | 0.0500 | +0.0170 | 0.0170 |
| 4 | 0 | 0 | 900 | 0.1829 | 0.1590 | +0.0239 | 0.0239 |
| 4 | 0 | 1 | 3900 | 0.0898 | 0.1050 | -0.0152 | 0.0152 |
| 4 | 0 | 2 | 3300 | 0.0622 | 0.0530 | +0.0092 | 0.0092 |
| 4 | 1 | 0 | 1300 | 0.1983 | 0.1630 | +0.0353 | 0.0353 |
| 4 | 1 | 1 | 2700 | 0.1162 | 0.1050 | +0.0112 | 0.0112 |
| 4 | 1 | 2 | 2400 | 0.0551 | 0.0490 | +0.0061 | 0.0061 |
| 5 | 0 | 0 | 1600 | 0.1636 | 0.2000 | -0.0364 | 0.0364 |
| 5 | 0 | 1 | 7800 | 0.0906 | 0.1300 | -0.0394 | 0.0394 |
| 5 | 0 | 2 | 5300 | 0.0574 | 0.0680 | -0.0106 | 0.0106 |
| 5 | 1 | 0 | 2800 | 0.1842 | 0.2100 | -0.0258 | 0.0258 |
| 5 | 1 | 1 | 8400 | 0.0761 | 0.1250 | -0.0489 | 0.0489 |
| 5 | 1 | 2 | 3800 | 0.0470 | 0.0680 | -0.0210 | 0.0210 |
| 6 | 0 | 0 | 1300 | 0.1647 | 0.1890 | -0.0243 | 0.0243 |
| 6 | 0 | 1 | 4000 | 0.0891 | 0.0950 | -0.0059 | 0.0059 |
| 6 | 0 | 2 | 4400 | 0.0618 | 0.0660 | -0.0042 | 0.0042 |
| 6 | 1 | 0 | 1200 | 0.1604 | 0.2000 | -0.0396 | 0.0396 |
| 6 | 1 | 1 | 4700 | 0.0863 | 0.1200 | -0.0337 | 0.0337 |
| 6 | 1 | 2 | 3400 | 0.0602 | 0.0620 | -0.0018 | 0.0018 |
| 7 | 0 | 0 | 1500 | 0.1393 | 0.1740 | -0.0347 | 0.0347 |
| 7 | 0 | 1 | 4400 | 0.0817 | 0.0860 | -0.0043 | 0.0043 |
| 7 | 0 | 2 | 4600 | 0.0478 | 0.0520 | -0.0042 | 0.0042 |
| 7 | 1 | 0 | 1100 | 0.1507 | 0.2020 | -0.0513 | 0.0513 |
| 7 | 1 | 1 | 4300 | 0.0690 | 0.0740 | -0.0050 | 0.0050 |
| 7 | 1 | 2 | 3800 | 0.0518 | 0.0520 | -0.0002 | 0.0002 |
| 8 | 0 | 0 | 1800 | 0.1570 | 0.1490 | +0.0080 | 0.0080 |
| 8 | 0 | 1 | 5000 | 0.1280 | 0.0980 | +0.0300 | 0.0300 |
| 8 | 0 | 2 | 4000 | 0.0626 | 0.0700 | -0.0074 | 0.0074 |
| 8 | 1 | 0 | 1500 | 0.1713 | 0.1650 | +0.0063 | 0.0063 |
| 8 | 1 | 1 | 2700 | 0.1130 | 0.0800 | +0.0330 | 0.0330 |
| 8 | 1 | 2 | 3100 | 0.0610 | 0.0400 | +0.0210 | 0.0210 |

### Couples male (drgn1 × educ3_male)

| drgn1 | educ3_male | n | mean gsur v2 | mean gsur v1 | mean diff | max|diff| |
|---|---|---|---|---|---|---|
| 1 | 0 | 4900 | 0.1640 | 0.1640 | +0.0000 | 0.0000 |
| 1 | 1 | 13100 | 0.1100 | 0.1100 | +0.0000 | 0.0000 |
| 1 | 2 | 20300 | 0.0560 | 0.0560 | +0.0000 | 0.0000 |
| 2 | 0 | 6300 | 0.1680 | 0.1590 | +0.0090 | 0.0090 |
| 2 | 1 | 24000 | 0.1011 | 0.0990 | +0.0021 | 0.0021 |
| 2 | 2 | 14300 | 0.0565 | 0.0480 | +0.0085 | 0.0085 |
| 3 | 0 | 2400 | 0.2340 | 0.1720 | +0.0620 | 0.0620 |
| 3 | 1 | 8500 | 0.1350 | 0.0890 | +0.0460 | 0.0460 |
| 3 | 2 | 8200 | 0.0670 | 0.0500 | +0.0170 | 0.0170 |
| 4 | 0 | 3100 | 0.1983 | 0.1630 | +0.0353 | 0.0353 |
| 4 | 1 | 10800 | 0.1162 | 0.1050 | +0.0112 | 0.0112 |
| 4 | 2 | 8800 | 0.0551 | 0.0490 | +0.0061 | 0.0061 |
| 5 | 0 | 6100 | 0.1842 | 0.2100 | -0.0258 | 0.0258 |
| 5 | 1 | 26200 | 0.0761 | 0.1250 | -0.0489 | 0.0489 |
| 5 | 2 | 16100 | 0.0470 | 0.0680 | -0.0210 | 0.0210 |
| 6 | 0 | 4000 | 0.1604 | 0.2000 | -0.0396 | 0.0396 |
| 6 | 1 | 13400 | 0.0863 | 0.1200 | -0.0337 | 0.0337 |
| 6 | 2 | 11800 | 0.0602 | 0.0620 | -0.0018 | 0.0018 |
| 7 | 0 | 5700 | 0.1507 | 0.2020 | -0.0513 | 0.0513 |
| 7 | 1 | 13100 | 0.0690 | 0.0740 | -0.0050 | 0.0050 |
| 7 | 2 | 11700 | 0.0518 | 0.0520 | -0.0002 | 0.0002 |
| 8 | 0 | 4400 | 0.1713 | 0.1650 | +0.0063 | 0.0063 |
| 8 | 1 | 11000 | 0.1130 | 0.0800 | +0.0330 | 0.0330 |
| 8 | 2 | 9500 | 0.0610 | 0.0400 | +0.0210 | 0.0210 |

### Couples female (drgn1 × educ3_female)

| drgn1 | educ3_female | n | mean gsur v2 | mean gsur v1 | mean diff | max|diff| |
|---|---|---|---|---|---|---|
| 1 | 0 | 4800 | 0.1530 | 0.1530 | +0.0000 | 0.0000 |
| 1 | 1 | 11400 | 0.1030 | 0.1030 | -0.0000 | 0.0000 |
| 1 | 2 | 22100 | 0.0580 | 0.0580 | +0.0000 | 0.0000 |
| 2 | 0 | 5900 | 0.1487 | 0.1250 | +0.0237 | 0.0237 |
| 2 | 1 | 19700 | 0.1107 | 0.1310 | -0.0203 | 0.0203 |
| 2 | 2 | 19000 | 0.0561 | 0.0480 | +0.0081 | 0.0081 |
| 3 | 0 | 1600 | 0.2300 | 0.1240 | +0.1060 | 0.1060 |
| 3 | 1 | 8100 | 0.1330 | 0.0770 | +0.0560 | 0.0560 |
| 3 | 2 | 9400 | 0.0700 | 0.0560 | +0.0140 | 0.0140 |
| 4 | 0 | 2400 | 0.1829 | 0.1590 | +0.0239 | 0.0239 |
| 4 | 1 | 10100 | 0.0898 | 0.1050 | -0.0152 | 0.0152 |
| 4 | 2 | 10200 | 0.0622 | 0.0530 | +0.0092 | 0.0092 |
| 5 | 0 | 5800 | 0.1636 | 0.2000 | -0.0364 | 0.0364 |
| 5 | 1 | 22200 | 0.0906 | 0.1300 | -0.0394 | 0.0394 |
| 5 | 2 | 20400 | 0.0574 | 0.0680 | -0.0106 | 0.0106 |
| 6 | 0 | 3400 | 0.1647 | 0.1890 | -0.0243 | 0.0243 |
| 6 | 1 | 11800 | 0.0891 | 0.0950 | -0.0059 | 0.0059 |
| 6 | 2 | 14000 | 0.0618 | 0.0660 | -0.0042 | 0.0042 |
| 7 | 0 | 3400 | 0.1393 | 0.1740 | -0.0347 | 0.0347 |
| 7 | 1 | 11900 | 0.0817 | 0.0860 | -0.0043 | 0.0043 |
| 7 | 2 | 15200 | 0.0478 | 0.0520 | -0.0042 | 0.0042 |
| 8 | 0 | 3500 | 0.1570 | 0.1490 | +0.0080 | 0.0080 |
| 8 | 1 | 8300 | 0.1280 | 0.0980 | +0.0300 | 0.0300 |
| 8 | 2 | 13100 | 0.0626 | 0.0700 | -0.0074 | 0.0074 |

Result: DOCUMENTED

---

## 16. M12-diag — Household-level constancy (HARD check)

**Singles** (households where column varies within idhh):

{'gsur': 0, 'gsur_legacy_misaligned': 0, 'gsur_weighting_source': 0, 'gsur_age_band_used': 0}

**Couples** (households where column varies within idhh):

{'gsur_male': 0, 'gsur_female': 0, 'gsur_male_legacy_misaligned': 0, 'gsur_female_legacy_misaligned': 0, 'gsur_male_weighting_source': 0, 'gsur_female_weighting_source': 0, 'gsur_male_age_band_used': 0, 'gsur_female_age_band_used': 0}

**Result: **PASS**** (zero variation expected; any non-zero = merge bug)

---

## 17. Stage A estimation readiness

All hard checks M1–M10 and M12-diag: **PASS**

**Stage A re-estimation against the versioned GSURv2 parquets is authorized per spec §14.**

Canonical promotion remains deferred (requires Stage A verdict SA-STANDS/SA-REVISION and separate O10 approval).
Stage B age-specific GSUR and welfare computation remain deferred.
