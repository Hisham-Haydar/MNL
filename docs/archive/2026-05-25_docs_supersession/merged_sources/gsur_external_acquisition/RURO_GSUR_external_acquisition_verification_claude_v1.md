> Merged into `docs/France_case/consolidated/RURO_GSUR_external_acquisition_consolidated_v1.md` on 2026-05-25. See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md`.

# Adversarial verification of external data sources (O1, O2, O9) for the RURO GSUR build

## 1. Verification verdict

**Partially ready.** Two of the three proposed source paths (O2 denominator and O9 benchmark) are essentially correct at the file-identification level, but each carries one substantive correction that must be incorporated before coding. The O1 crosswalk path is **not implementation-ready**: the proposed Eurostat NUTS2013→NUTS2016 file is genuine and official, but it is insufficient on its own — three additional, only partially documented, mappings are needed to reach the level of EUROMOD's `drgn1` (INSEE old two-digit regions), and the existence and granularity of an "old-region" variable in the GSUR/SILC source for France 2016 is itself in doubt.

Two factual claims embedded in the acquisition report are wrong and have been corrected below: (i) the NUTS-2 level for France was **not** realigned to the 13 new régions in NUTS 2021 (it still reflects the 22 former régions in NUTS 2021 and NUTS 2024); (ii) Eurostat's `FR` geo code in unemployment series **includes the four overseas departments (Guadeloupe, Martinique, Guyane, Réunion)** for reference year 2016 — it is *France hors Mayotte*, not France métropolitaine.

## 2. Confirmed claims from the acquisition report

The acquisition report is correct on the following:

- **Eurostat publishes `NUTS2013-NUTS2016.xlsx`** as the official inter-version correspondence, hosted on the Eurostat "History of NUTS" page (`https://ec.europa.eu/eurostat/web/nuts/history`; direct file: `https://ec.europa.eu/eurostat/documents/345175/629341/NUTS2013-NUTS2016.xlsx`).
- **Commission Regulation (EU) 2016/2066 of 21 November 2016** is the legal instrument that updated NUTS to the 2016 version, CELEX `32016R2066` (`https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R2066`). It amended Regulation (EC) No 1059/2003 and applied to data transmissions from 1 January 2018.
- **Loi n° 2015-29 of 16 January 2015** restructured metropolitan France from 22 to 13 régions, effective 1 January 2016 (`https://www.legifrance.gouv.fr/loda/id/JORFTEXT000030109622`).
- The **`lfst_r_lfp2acedu`** dataset exists on the Eurostat databrowser with title *"Economically active population by sex, age, educational attainment level and NUTS 2 regions (1 000)"* and is a **stock series in thousand persons** with the four required dimensions (NUTS 2 × sex × age × ISCED11). For the denominator concept "labour-force stock by region × sex × age × education for France 2016", this is the correct single Eurostat table.
- **`une_rt_a`** ("Unemployment by sex and age – annual data") and **`tps00203`** ("Total unemployment rate") both exist on the Eurostat databrowser, both derive from EU-LFS, and `tps00203` is a curated single-cell extract of the `une_rt_a` family (age 15-74, both sexes, % of active population).

## 3. Claims that are unsupported, unsafe, or need qualification

Four claims in the acquisition report are wrong or need qualification:

- *"The NUTS 2 French level was realigned to the new régions in NUTS 2021."* **Wrong.** Per the INSEE definition page `c2112` (`https://www.insee.fr/fr/metadonnees/definition/c2112`) and the Eurostat NUTS overview, the NUTS-2 level for France still reflects the **22 former metropolitan régions** (plus 5 DOM = 27 NUTS-2 units) in NUTS 2016, NUTS 2021, and NUTS 2024. Only NUTS 1 was changed to host the 13 new régions (replacing the ZEAT). The NUTS-2 codes were **renamed** under the new letter scheme (e.g. FR21 Champagne-Ardenne → FRF2; FR42 Alsace → FRF1; FR43 Franche-Comté → FRC2), but the underlying 22-region geography is unchanged.
- *"lfst_r_lfu3pers gives unemployment stocks by … duration of unemployment."* **Wrong.** `lfst_r_lfu3pers` is "Unemployment by sex, age, educational attainment level and NUTS 2 region" — it has no duration dimension. Duration of unemployment at the regional level lives in `lfst_r_lfu2ltu` (long-term unemployment, 12 months+).
- *"Eurostat `FR` covers France métropolitaine."* **Wrong for 2016.** From reference year 2014 onward, Eurostat's `FR` geo code in LFS-derived unemployment series **includes Guadeloupe, Martinique, Guyane, Réunion** (Mayotte added only from 2024). Eurostat's own ESMS for the LFS series and INSEE's "A new Labour Force Survey in 2021" both state this explicitly. The 2016 value 10.1% under `FR` is *France hors Mayotte*, not métropole.
- *"EUROMOD drgn1 for France uses INSEE 2-digit old-region codes (11, 21, …, 94 + 01–04)."* **Plausible but unverified.** The publicly available EUROMOD France country report (Bouvard, 2019, Y10_CR_FR_Final.pdf on `euromod-web.jrc.ec.europa.eu`) does **not** publish the codebook for `drgn1` (it documents policies, not variable codes). EUROMOD's convention is to take the region from EU-SILC `DB040`, which in the anonymised UDB is at **NUTS 1** for most countries, not at the 22-region INSEE level. The claim therefore cannot be confirmed from official public documentation and must be checked against the EUROMOD data dictionary distributed with the model, or directly with the JRC EUROMOD team.

The author attribution "Paola De Agostini and colleagues" for the France country report is also incorrect for the FR_2016/FR_2017 vintage: the relevant report is Bouvard (AMSE) and Trannoy.

## 4. O1 crosswalk verification

The `NUTS2013-NUTS2016.xlsx` file is the canonical Eurostat correspondence between the two NUTS vintages and is appropriate for the *NUTS↔NUTS* part of the work. **It is, however, far from sufficient for the project's actual need**, which is to map an EUROMOD `drgn1` value (asserted to be a 1980s-vintage INSEE region code) back into a stable post-reform region identifier.

The full chain that must be built is:

1. EUROMOD `drgn1` → INSEE 2-digit region code (NOT documented in any public EUROMOD source).
2. INSEE 2-digit old-region code → NUTS 2013 NUTS-2 code (no single canonical published INSEE table; must be reconstructed by region name from the COG 2015 file `https://www.insee.fr/fr/information/2560698` joined to the Eurostat NUTS-2 list).
3. NUTS 2013 NUTS-2 code → NUTS 2016 NUTS-2 code (this is what `NUTS2013-NUTS2016.xlsx` provides — a pure recoding because the underlying 22-region geometry is preserved).
4. NUTS 2016 NUTS-2 code → NUTS 2016 NUTS-1 code (i.e. the 13 new régions, by simple aggregation; the parent NUTS-1 code is the first three characters of the NUTS-2 code, e.g. FRF1, FRF2, FRF3 → FRF Grand Est).

Steps 1, 2 and 4 are **not** delivered by the Eurostat file. The acquisition report's framing — "we use `NUTS2013-NUTS2016.xlsx` to bridge the reform" — collapses a four-step chain into one and conceals two genuinely missing crosswalks.

For step 4, the INSEE definition page `c2112` is the authoritative documentation that the 13 new régions sit at NUTS 1, that ZEAT lost their NUTS-1 role in 2016, and that NUTS 2 was *not* restructured. For the legal underpinning, Reg. 2016/2066 (CELEX `32016R2066`) and Loi 2015-29 are correctly identified.

**Status: the proposed file is genuine and useful, but the acquisition report under-specifies the crosswalk pipeline. The build cannot proceed on the Eurostat file alone.**

## 5. O1 remaining risk: old region to EUROMOD drgn1

This is the single largest unresolved risk in the O1 chain. Specifically:

- The public EUROMOD France country report does not contain a codebook for `drgn1`. The asserted coding (INSEE 11=Île-de-France, 21=Champagne-Ardenne, …, 94=Corse, 01–04 for DOM) matches the long-standing INSEE pre-2016 region codes verified against the COG 2015 file (`https://www.insee.fr/fr/information/2560698`), but **whether EUROMOD's FR input dataset for 2016/2017 actually exposes this two-digit variable rather than the EU-SILC anonymised NUTS-1 code is undocumented in any officially accessible source**.
- The DOM list in the acquisition report is incomplete: it omits Mayotte (INSEE code 06, NUTS FRY5), which became a DOM in 2011. For SILC France 2016 this is generally irrelevant (Mayotte is excluded from EU-LFS until 2024 and was not in EU-SILC France 2016), but it should be explicit.
- The INSEE↔NUTS correspondence required for step 2 of §4 is **not** published by INSEE as a single official crosswalk table. The widely circulated CSV on `data.gouv.fr` ("nomenclature-code-des-nouvelles-regions-2016") is user-contributed and its own metadata redirects users back to the INSEE COG. The mapping is therefore reconstructible from COG 2015 + Eurostat NUTS 2013 list joined on region name, but **no canonical, machine-readable INSEE↔NUTS-2 table exists on official portals**. The acquisition report must either (a) deliver a hand-built crosswalk and document the join keys (region name, normalised), or (b) drop the request for old-region granularity.

**Action required:** request from the user (i) the actual EUROMOD France data dictionary (`drgn1` codelist) or a value-frequency dump of `drgn1` from the FR_2016/FR_2017 input dataset, and (ii) confirmation of whether DOM are present in the model's France input file at all.

## 6. O1 remaining risk: GSUR workbook geography

EU-SILC's User Database (the only public/scientific-use vehicle for SILC France microdata) **anonymises `DB040` (region of residence) down to NUTS 1**. This is documented in the Eurostat EU-SILC ESMS (`https://ec.europa.eu/eurostat/cache/metadata/en/ilc_sieusilc.htm`) and in the EU-SILC User Guide (Doc065, e.g. `https://ec.europa.eu/eurostat/documents/203647/16195750/2021_Doc65_EUSILC_User_Guide.pdf`).

If the GSUR workbook is built from EU-SILC UDB and not from a national restricted-access version of the SILC France ("EU-SILC France SRCV CASD" / INSEE Centre d'accès sécurisé aux données), then **the maximum regional detail in the workbook is NUTS 1**. Under NUTS 2016 that is the 13 new régions (plus FRY for the DOM); under NUTS 2013 it would be the 9 ZEAT (plus DOM grouping). In either case, **the workbook does not, and cannot, contain a 22-region identifier** of the kind needed to populate the asserted EUROMOD `drgn1` code list.

If the workbook exposes only 13 new régions, the `NUTS2013-NUTS2016.xlsx` crosswalk is **structurally incapable** of recovering the 22 old régions — the mapping is many-to-one in that direction, not one-to-many. The build pipeline must therefore be reformulated to operate at the lowest common geography (NUTS 1 = 13 new régions + DOM), with a corresponding redefinition of `drgn1` upstream in the EUROMOD input.

**This is a blocking issue.** Before any coding, the user must establish (a) whether the GSUR/SILC source has 22-region detail or NUTS-1 detail, and (b) whether EUROMOD `drgn1` matches that granularity. If the answer is NUTS 1, item O1 reduces to a one-line mapping table (13 régions ↔ 13 NUTS-1 codes), and the Eurostat NUTS2013-NUTS2016 file is not needed at all for France 2016.

## 7. O2 denominator verification

`lfst_r_lfp2acedu` is **verified and appropriate** as the primary denominator source. Eurostat databrowser URL: `https://ec.europa.eu/eurostat/databrowser/view/lfst_r_lfp2acedu/default/table`. The dataset is annual, in thousand persons (`THS_PER`, a stock), with dimensions `geo` (NUTS 2), `sex`, `age` (standard LFS bands), `isced11` (ED0-2 / ED3_4 / ED5-8 from 2014 onward), and `time`. France 2016 is in coverage, indexed under NUTS 2016 region codes.

Two facts must be made explicit in the build documentation:

- The "p2" suffix in `lfst_r_lfp*` codes denotes **NUTS-2 regional level**, not "participation rate". The rate counterpart is `lfst_r_lfp2actrt`. The acquisition report's gloss ("p2 = participation, stock") is wrong on the meaning of the prefix even though it correctly identifies the dataset as a stock.
- ISCED-2011 applies to France from reference year 2014; the 2016 cells are pure ISCED-2011 and are not directly comparable cell-by-cell to pre-2014 ISCED-97 cells.

If the project's denominator concept is "all resident persons" rather than the labour force, the correct table is `lfst_r_lfsd2pop` ("Population in private households by educational attainment level and NUTS 2 region", `https://ec.europa.eu/eurostat/databrowser/view/lfst_r_lfsd2pop/default/table`), which Eurostat itself pairs with `lfst_r_lfp2acedu` in its Statistics Explained chapter on regional labour-market education.

## 8. O2 fallback hierarchy

A revised, defensible hierarchy:

1. **Primary, labour-force denominator:** `lfst_r_lfp2acedu` (stock, NUTS 2 × sex × age × ISCED11). Verified.
2. **Primary, population denominator (if you want to include the inactive):** `lfst_r_lfsd2pop` (stock, same grid). Verified.
3. **Decomposition cross-checks:** `lfst_r_lfe2eedu` (employed stock, same grid) and `lfst_r_lfu3pers` (unemployed stock, same grid) should satisfy approximately `lfp2acedu ≈ lfe2eedu + lfu3pers` cell-by-cell, modulo sampling error and confidentiality suppression. This identity is a useful internal audit.
4. **Rate cross-checks (not denominators):** `lfst_r_lfu3rt` (unemployment rate, %) and `lfst_r_lfp2actrt` (participation rate, %). Useful for sanity but not for cell counts.
5. **`lfst_r_lfp2act`:** labour-force stock by NUTS 2 with **sex × age only** — usable only when the ISCED breakdown is suppressed. Not a substitute for `lfst_r_lfp2acedu`.
6. **`lfst_r_lfpop`:** **does not exist** as a queryable dataset code; it is a folder label in the Eurostat navigation tree. Remove from any reference list.

The acquisition report's fallback list contains one false hypothesis (the duration dimension in `lfst_r_lfu3pers`) and should be revised accordingly.

## 9. O2 cell-level checks required after download

For each downloaded extract, the following must be checked before any cell count is used in the MNL denominator:

The first essential check is that the **France 2016 cells under the required `geo × sex × age × isced11` cross-tab are non-empty and not flagged** with Eurostat's standard quality codes — `:` (not available), `c` (confidential), `u` (low reliability), or `e` (estimated). The Eurostat regional LFS ESMS (`https://ec.europa.eu/eurostat/cache/metadata/en/reg_lmk_esms.htm`) is explicit that sample-reliability rules drive suppression at fine cross-classifications. For the smaller French NUTS-2 units — Corse (FRM0) and the DOM (FRY1–FRY4) — suppression at the four-dimensional cross-tab is the rule rather than the exception. The MNL specification must either aggregate these strata or impute them.

Second, the **age bands** must be checked against the EUROMOD/SILC age categories used in the user's MNL. Eurostat's standard LFS bands include Y15-24, Y25-49, Y25-54, Y50-64, Y15-64 and Y15-74; not all bands are stored at the full ISCED-by-region cross-tab. Third, **`isced11`** is the only education classification available for 2016 and is the only one consistent with the EUROMOD/SILC `pl040`-family education coding for that wave. Fourth, the **unit** must be confirmed (`THS_PER` = thousand persons in the stock tables; multiply by 1000 before computing shares). Fifth, the **geo** dimension for the 2016 reference year uses **NUTS 2016 codes** in the current databrowser dissemination — the old NUTS 2013 22-region codes (FR10, FR21, …) are not the disseminated geometry, so any join to EUROMOD must use NUTS 2016 NUTS-2 letter codes (FR10, FRB0, FRC1, …, FRM0) and not the pre-reform numerics.

## 10. O9 benchmark verification

Both proposed codes are verified. `une_rt_a` ("Unemployment by sex and age – annual data") and `tps00203` ("Total unemployment rate") exist on the Eurostat databrowser at `https://ec.europa.eu/eurostat/databrowser/view/une_rt_a/default/table` and `https://ec.europa.eu/eurostat/databrowser/view/tps00203/default/table` respectively. `tps00203` is the curated main-table extract at age 15-74, both sexes, percent of the active population, drawn from the same EU-LFS-derived series as `une_rt_a`. Annual averages are calculated as the mean of the four quarterly LFS estimates (per the Eurostat LFS ESMS).

For France in 2016, both series report **10.1%** at `sex=T, age=Y15-74, unit=PC_ACT`. This is confirmed against INSEE's *Tableaux de l'économie française*, édition 2017, which cites the same figure with a Eurostat extraction date of 7 September 2017 (`https://www.insee.fr/fr/statistiques/3303389?sommaire=3353488`).

The critical correction the acquisition report needs to absorb concerns the **geographic perimeter encoded by `geo=FR`**. For reference year 2016, Eurostat `FR` covers **metropolitan France plus the four overseas departments Guadeloupe, Martinique, Guyane and Réunion** (i.e. *France hors Mayotte*). Mayotte was added to the EU-LFS continuous series only from 2024. This is documented in the Eurostat LFS ESMS and explicitly stated in the INSEE methodological note "A new Labour Force Survey in 2021". The acquisition report's implicit assumption that `FR` = France métropolitaine is wrong and would generate a perimeter mismatch with any métropole-only sample.

## 11. Benchmark geography decision

The benchmark to use is dictated by the perimeter of the analytic sample, not by convenience of source:

- If the project's EUROMOD France input is **France métropolitaine only** (the historical default for EU-SILC France 2016 — to be confirmed against the EU-SILC France quality report), the correct 2016 benchmark is **INSEE BDM series `001688526`** (*Taux de chômage au sens du BIT — Ensemble — France métropolitaine — CVS*, `https://www.insee.fr/fr/statistiques/serie/001688526`), with a 2016 annual average of approximately **9.7%**. Using Eurostat `tps00203` (10.1%) against a métropole sample would overstate the benchmark by roughly 0.4 percentage points purely through the inclusion of higher-unemployment DOM in the denominator.
- If the project's sample is **France hors Mayotte** (métropole + 4 DOM), Eurostat `une_rt_a`/`tps00203` at `FR` = 10.1% is appropriate, and is identical to INSEE BDM series `001688527` (*France hors Mayotte*, `https://www.insee.fr/fr/statistiques/serie/001688527`).
- France entière (including Mayotte) is not a relevant 2016 perimeter: Mayotte was outside the continuous LFS and outside EU-SILC France in 2016.

The decision therefore reduces to a **single question about the EUROMOD/SILC sample perimeter** that the user must answer before fixing the benchmark.

## 12. Files/tables that should be downloaded

The minimal, verified set required to proceed is:

- **`NUTS2013-NUTS2016.xlsx`** from `https://ec.europa.eu/eurostat/documents/345175/629341/NUTS2013-NUTS2016.xlsx` (Eurostat). For step 3 of the O1 chain only.
- **INSEE COG 2015** region file from `https://www.insee.fr/fr/information/2560698` and **COG 2016** region file from `https://www.insee.fr/fr/information/2114819` (INSEE). Required to reconstruct the INSEE-2-digit ↔ NUTS-2 mapping by region name, and the 22→13 region aggregation.
- **`lfst_r_lfp2acedu`** France 2016 extract from `https://ec.europa.eu/eurostat/databrowser/view/lfst_r_lfp2acedu/default/table` (Eurostat). Labour-force stock denominator.
- **`une_rt_a`** France 2016 extract from `https://ec.europa.eu/eurostat/databrowser/view/une_rt_a/default/table` (Eurostat), **conditional on the sample being France hors Mayotte**; otherwise **INSEE BDM series `001688526`** from `https://www.insee.fr/fr/statistiques/serie/001688526` for a métropole sample.

For legal/documentary traceability (not data inputs), retain the URLs for Reg. 2016/2066 (`https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R2066`), Loi 2015-29 (`https://www.legifrance.gouv.fr/loda/id/JORFTEXT000030109622`), the INSEE NUTS definition `c2112` (`https://www.insee.fr/fr/metadonnees/definition/c2112`), and the EU-SILC ESMS (`https://ec.europa.eu/eurostat/cache/metadata/en/ilc_sieusilc.htm`).

## 13. Files/tables that are optional

`lfst_r_lfsd2pop` is required only if the denominator concept is the resident population rather than the labour force. `lfst_r_lfe2eedu` and `lfst_r_lfu3pers` are useful as internal cross-checks via the active = employed + unemployed identity but are not denominator inputs. `lfst_r_lfu3rt` and `lfst_r_lfp2actrt` are rate series and have no role as denominators. `tps00203` is redundant with `une_rt_a` and need not be downloaded separately. The INSEE BDM series `001688527` (France hors Mayotte) duplicates Eurostat `une_rt_a` `FR` and is needed only for INSEE-source provenance documentation. The COG hub page (`https://www.insee.fr/fr/information/2560452`) is informational rather than a data input.

## 14. Final decision: implementation-ready, partially ready, or not ready

**Partially ready.** O2 (denominator) is implementation-ready once the documentation corrects the "u3 = duration" error and the "p2 = participation" gloss. O9 (benchmark) is implementation-ready once the perimeter question is settled — and the answer dictates which of two series to pull. **O1 (crosswalk) is not implementation-ready**: the proposed Eurostat file is correct but only covers one of the four steps that the actual project pipeline requires, and two of the missing steps depend on facts that are not documented in any publicly accessible official source (the `drgn1` codelist and the maximum geographic granularity of the GSUR/SILC source for France 2016).

## 15. Corrections needed before coding

The acquisition report must be revised on the following points before any data are pulled:

- Replace the single-step framing of the regional crosswalk with the explicit four-step chain in §4, and identify which of the three non-Eurostat steps the project will satisfy and how. The Eurostat `NUTS2013-NUTS2016.xlsx` file alone is insufficient.
- Correct the claim that NUTS-2 was realigned to the 13 new French régions in NUTS 2021. NUTS-2 still maps to the 22 former régions in NUTS 2016, 2021 and 2024; only NUTS-1 holds the 13 new régions. Cite INSEE `c2112`.
- Establish, and document in the rebuild specification, whether the GSUR/SILC source for France 2016 exposes 22-region detail or only NUTS-1 (13 régions). If the source is EU-SILC UDB, the answer is NUTS-1 and the whole 22-region pipeline collapses to a one-line aggregation.
- Obtain the EUROMOD France data dictionary (or a value-frequency dump of `drgn1` for FR_2016/FR_2017) to confirm — or refute — the asserted INSEE-2-digit coding. The current claim is not verifiable from the publicly accessible country report.
- Add Mayotte (INSEE code 06, NUTS FRY5) to the DOM list, with an explicit note that it is excluded from EU-LFS 2016 and from EU-SILC France 2016.
- Correct the gloss on `lfst_r_lfp2acedu`: the "p2" suffix denotes NUTS-2 level, not participation; the dataset is a stock in thousand persons. Correct the gloss on `lfst_r_lfu3pers`: it has no duration dimension; regional duration sits in `lfst_r_lfu2ltu`. Remove any reference to `lfst_r_lfpop` as a dataset code.
- State that under `geo=FR` Eurostat reports *France hors Mayotte* (métropole + 4 DOM) for 2016, not France métropolitaine, and pin the benchmark choice to the EUROMOD/SILC sample perimeter (INSEE `001688526` ≈ 9.7% for métropole; Eurostat `une_rt_a` `FR` = INSEE `001688527` = 10.1% for hors Mayotte).
- Correct the EUROMOD France country-report author attribution: the FR_2016/FR_2017-vintage report is Bouvard & Trannoy (AMSE), not De Agostini.