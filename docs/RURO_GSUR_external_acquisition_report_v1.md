# RURO_GSUR_external_acquisition_report_v1

## Acquisition verdict and readiness

**1. Executive verdict**

The acquisition problem is largely resolvable from official sources, but at two different layers. For **O1**, there is no official Eurostat/INSEE source that names EUROMOD’s `drgn1` directly, because `drgn1` is not an official territorial classification; however, there *are* official sources that map **modern French NUTS geography to the pre-reform French regional geography** that EUROMOD 2016 ultimately relies on. The strongest implementation-authoritative official source is Eurostat’s frozen historical correspondence file **`NUTS2013-NUTS2016.xlsx`**, backed legally by **Commission Regulation (EU) No 1319/2013** for the old NUTS 2013 classification and **Commission Regulation (EU) 2016/2066** for the NUTS 2016 revision. For **O2**, the preferred denominator problem is essentially solved at **NUTS 2**: Eurostat provides a verified dataset, **`lfst_r_lfp2acedu`**, for the labour force by educational attainment and NUTS 2 region, and official listings indicate that it is cross-classified by sex, age, and education. For **O9**, an official national benchmark is available from Eurostat’s annual unemployment series (`une_rt_a`, or the derived headline table `tps00203`) and is corroborated by INSEE’s 2016 labour-market publication, both pointing to **10.1%** for France in 2016, subject to a final geography-concept match. citeturn1view2turn33search0turn34search1turn35search0turn40search1turn41search1turn15search2turn47view0turn32search5turn30view0

The key practical implication is that **external-asset acquisition may now be authorized**, because the official-source path for O1, O2, and O9 has been identified. However, I do **not** recommend authorizing the numerical rebuild itself until the files listed below are actually downloaded and frozen in your project, and until one final manual confirmation is made on the GSUR workbook’s regional coding: if the rebuild can proceed at **modern NUTS 2**, the official crosswalk and denominator path is strong; if the workbook has only **collapsed short modern codes** left, the official sources alone do not recreate a direct `drgn1` lookup without going back to finer geography. citeturn1view2turn16view0turn38search1

**16. Final implementation readiness status**

My final status is therefore: **acquisition-ready, but not yet execution-ready**. In other words, O1, O2, and O9 are now sufficiently resolved to justify downloading and archiving the official external assets, writing the validation-source documentation, and fixing the benchmark concept. Full implementation should remain blocked until the downloaded assets are committed and the GSUR regional variable is matched to the official NUTS vintage at the intended level of geography. citeturn1view2turn38search1turn47view0

## Search record

**2. Sources searched**

The search covered the user-preferred primary domains first. On the French official side, I searched **INSEE** pages for the Code officiel géographique, historical commune membership tables, and territorial-reform documentation; on **data.gouv.fr**, I checked whether an official maintained correspondence resource existed, but the visible item on “new region codes 2016” explicitly points users back to the INSEE COG and is not the best authoritative implementation source. On the EU side, I searched **Eurostat** pages for the NUTS history and correspondence-table resources, Eurostat catalogue and databrowser entries for the relevant regional labour-force datasets, and Eurostat metadata for unemployment concepts; I also checked **EUR-Lex** for the legal regulations fixing the NUTS 2013 and NUTS 2016 classifications. citeturn19view0turn19view2turn39search2turn1view2turn16view0turn13view0turn38search1turn40search1turn41search1turn47view0

## Crosswalk acquisition

**3. O1 crosswalk: candidate sources**

There are three serious official-source candidates for O1.

The first, and strongest, candidate is Eurostat’s **historical NUTS correspondence file `NUTS2013-NUTS2016.xlsx`**, linked from the Eurostat “History of NUTS” page. Eurostat’s history page explicitly lists the NUTS revision periods and links the 2013–2016 correspondence workbook, and search-result snippets from that workbook confirm that it contains **France-specific recoding rows** such as **FR24 → FRB0**, **FR26 → FRC1**, **FR43 → FRC2**, **FR42 → FRF1**, **FR21 → FRF2**, and **FR25 → FRD1**. That is exactly the kind of frozen official crosswalk needed to relate pre-reform French regional codes to post-reform NUTS codes without inventing a mapping. citeturn1view2turn33search0turn34search1turn35search0

The second candidate is the pair of **EUR-Lex legal acts** that bookend the two relevant vintages: **Commission Regulation (EU) No 1319/2013**, which sets the NUTS 2013 classification, and **Commission Regulation (EU) 2016/2066**, which amends the NUTS annexes for the 2016 revision. These regulations provide the legal classification framework, but they are not by themselves as convenient operationally as the Eurostat correspondence workbook, because they list official classifications rather than a ready-made historical row-by-row passage table. They are best treated as legal support, not as the primary implementation file. citeturn40search1turn41search1

The third candidate is the France-specific **INSEE territorial reference material**: the COG department files for 2015 and 2016, and the broader “table d’appartenance géographique des communes” for 2015 and 2016. INSEE’s pages show that the territorial reform took effect on **1 January 2016**, that metropolitan France moved from **22 regions to 13**, and that each department belongs to **one and only one** region. These sources are excellent for France-specific verification and for any department-based sanity checks, but they are not a direct substitute for the Eurostat NUTS historical crosswalk because they use French administrative codes rather than the Eurostat NUTS codes used in GSUR and EUROMOD workflows. citeturn42view0turn19view1turn19view2turn22view0turn25view0

**4. O1 crosswalk: recommended authoritative source**

The recommended implementation-authoritative source for O1 is **Eurostat’s frozen historical correspondence workbook `NUTS2013-NUTS2016.xlsx`**. It is the best single official artifact because it is designed precisely to connect one NUTS vintage to another and is referenced from Eurostat’s own NUTS-history page. It should be treated as the **authoritative crosswalk source for the official part of the mapping**, while the EUR-Lex regulations serve as the legal basis and INSEE files serve as France-specific verification. citeturn1view2turn33search0turn40search1turn41search1

A crucial qualification is that **no official source will map directly to EUROMOD `drgn1`**, because `drgn1` is not an official Eurostat or INSEE territorial system. The official source can take you from **modern NUTS** to **pre-reform French region/NUTS codes**. The **final step** from old official regions to `drgn1` must still come from the EUROMOD France 2016 documentation already in your project. In other words, the official acquisition problem is solvable, but the last grouping step remains a model-documentation step, not an official-statistics step. That distinction should be stated explicitly in the validation memo. citeturn16view0turn40search1turn41search1

**5. O1 crosswalk: exact files/tables to download**

The exact Eurostat crosswalk file to download is **`NUTS2013-NUTS2016.xlsx`**, the workbook linked from Eurostat’s “History of NUTS” page for the 2013–2016 transition. The exact INSEE France-specific support files to download are **`depts2015-txt.zip`** and **`depts2016-txt.zip`**, which are the 2015 and 2016 department files from the COG pages. If you want a commune-level fallback or a stronger territory-membership audit trail, the exact INSEE files are **`table-appartenance-geo-communes-15.zip`** and **`table-appartenance-geo-communes-16.zip`**. If you also want the plain region-code lists for documentation, INSEE exposes **`reg2015-txt.zip`** and **`reg2016-txt.zip`**. citeturn1view2turn24view0turn26view0turn20view0turn20view1turn26view2turn27view0

**6. O1 crosswalk: implementation caveats**

The first caveat is conceptual: **do not describe the final output as an “official `drgn1` crosswalk.”** What is official is the **NUTS/COG passage**; the `drgn1` part is EUROMOD-specific. The validation report should say exactly that. citeturn16view0turn40search1turn41search1

The second caveat is temporal. Eurostat’s NUTS history page makes clear that NUTS vintages change over time, and current disseminated data may be organized under later NUTS vintages even for earlier reference years. That is why the frozen historical file is safer than relying only on a current live browser view. citeturn1view2

The third caveat is geographic. INSEE’s territorial documentation states that the 2016 reform changed the metropolitan region contours and that each department belongs to one region only. This makes the INSEE department files valuable for validation, but if your GSUR workbook now retains only **short modern region codes** rather than the underlying NUTS 2 detail, official sources cannot magically recover lost within-region heterogeneity. In that case, implementation remains blocked until the underlying geography is recovered from the fuller GSUR source. citeturn42view0turn22view0turn25view0

## Denominator acquisition

**7. O2 denominators: candidate sources**

The primary official denominator source is Eurostat’s **`lfst_r_lfp2acedu`** dataset, labelled “Labour force by educational attainment level and NUTS 2 region.” Official Eurostat search results and catalogue material identify it as the regional labour-force table to use, and supporting official catalogue excerpts describe it as **economically active population by sex, age, educational attainment level and NUTS 2 regions**. This is the closest match to your preferred denominator concept. citeturn15search2turn12search4turn14view3

The main official backup pair is **`lfst_r_lfu3pers`** for unemployed persons and **`lfst_r_lfu3rt`** for unemployment rates, both regional LFS datasets on Eurostat. These are verified to exist on Eurostat and are the natural fallback pair if labour-force counts have gaps, because they permit an implied labour-force calculation when the numerator and rate concepts align. I did not complete a cell-by-cell extraction in this report, so I recommend treating them as **verified existing backup datasets**, not as the primary weighting source. citeturn15search0turn15search1turn14view1turn14view2

The official population fallback at the same regional level is **`lfst_r_lfsd2pop`**, which Eurostat labels as “Population in private households by educational attainment level and NUTS 2 region.” Official Eurostat snippets show that this dataset includes a sex dimension and an age dimension in the browser, making it the strongest published population-count alternative if labour-force denominators are unavailable or unreliable in some cells. citeturn45search1turn45search4turn45search6

A secondary cross-check source is **`lfst_r_lfe2eedu`**, the regional employment table by educational attainment. It is useful as a cross-check or reconstruction aid, but not necessary if `lfst_r_lfp2acedu` is populated and usable. citeturn37search0turn14view1

**8. O2 denominators: exact dataset codes / tables to check**

For the preferred weighting route, check these Eurostat dataset codes first:

`lfst_r_lfp2acedu` — **verified on Eurostat**; this is the first dataset to inspect for labour-force denominators by NUTS 2 × sex × age × education. citeturn15search2turn12search4

`lfst_r_lfu3pers` — **verified on Eurostat as an existing dataset**; use as backup for unemployed counts. citeturn15search0turn14view1

`lfst_r_lfu3rt` — **verified on Eurostat as an existing dataset**; use as backup for unemployment rates. citeturn15search1turn14view2

`lfst_r_lfsd2pop` — **verified on Eurostat**; strongest population fallback at NUTS 2. citeturn45search1turn45search4

`lfst_r_lfp2act` — **verified on Eurostat**; use only if you need labour force by NUTS 2 × sex × age without education. citeturn10search0turn14view3

`lfst_r_lfe2eedu` — **verified on Eurostat as existing**, useful as an employment cross-check. citeturn37search0

**9. O2 denominators: whether labour-force denominators are available**

At the level that matters most for a defensible rebuild — **NUTS 2** — the answer is **yes**. Eurostat’s regional labour-market metadata states that the source down to NUTS level 2 is the **EU Labour Force Survey**, and the verified `lfst_r_lfp2acedu` dataset is the official labour-force-count source that most closely matches your target denominator concept. On that basis, O2 is substantially resolved **if the rebuild is done at NUTS 2**. citeturn38search1turn15search2turn12search4

What I did **not** verify in this report is a full live extraction for every France-2016 GSUR cell and every exact age-band label used in your workbook. So the right wording is: **labour-force denominators are officially available in principle and very likely in practice for the needed NUTS 2 cross-classification, but the final confirmation should be made at download/extraction time.** Because the preferred direct count exists, you should not design the pipeline around inferred denominators unless the download reveals missing or suppressed cells. citeturn15search2turn38search1

**10. O2 denominators: fallback weighting rule if exact denominators are unavailable**

The defensible fallback rule is hierarchical.

First fallback: if a small number of `lfst_r_lfp2acedu` cells are missing, infer the labour force as **unemployed persons divided by unemployment rate**, using the matching `lfst_r_lfu3pers` and `lfst_r_lfu3rt` cell. This should be flagged as an inferred denominator, because it inherits rounding from both the numerator and the rate. citeturn15search0turn15search1

Second fallback: if the labour-force cell is missing and the unemployed/rate pair is not usable, use **`lfst_r_lfsd2pop`** as the same-cell population denominator and record that the weighting source is population rather than labour force. This is a defensible approximation because it still respects region × age × education × sex structure at NUTS 2, but it should be explicitly labelled approximate in the validation report. citeturn45search1turn45search4

Third fallback: only if the education-specific cell cannot be supported, use **`lfst_r_lfp2act`** as a region × sex × age labour-force denominator and allocate education shares using the best available published population composition. This is materially weaker and should be used only as a last resort. citeturn10search0turn45search1

The limitations that must be recorded are straightforward: Eurostat regional counts are disseminated in **thousand persons**, so small-cell rounding matters; some regional LFS cells may be missing or flagged for reliability reasons; current disseminated geography may reflect later NUTS vintages; and this report verified the strongest **NUTS 2** route, not a full **NUTS 3** denominator pipeline. citeturn38search1turn45search4turn1view2

## National benchmark acquisition

**11. O9 national benchmark: candidate sources**

The best official benchmark candidates are Eurostat’s annual national unemployment tables and INSEE’s annual labour-market publications.

On the Eurostat side, the relevant official sources are **`une_rt_a`** (“Unemployment by sex and age — annual data”) and the derived headline table **`tps00203`** (“Total unemployment rate”). Eurostat’s unemployment metadata page states the concept clearly: the unemployment rate is the **annual average percentage of the labour force aged 15–74**, based on the **EU-LFS** and following **ILO** definitions; the same metadata also notes that **France includes the Overseas departments and regions (DROM)**. Eurostat browser snippets for the annual table show **France = 10.1** for 2016. citeturn47view0turn32search0turn32search2turn32search5

On the INSEE side, the strongest candidate is **“Activité, emploi et chômage en 2016”**, which states directly that the unemployment rate in France in 2016 was **10.1%**. INSEE’s long-series “L’essentiel sur le chômage” also reports **2016 = 10.1** for the aggregate series, while the 2018 “Chômage” tables specify that the 2016 field is **France hors Mayotte**, population in households, persons active, age 15+. These INSEE sources are excellent corroboration and may be preferable if your rebuilt geography or field does not match Eurostat’s France total including DROM. citeturn30view0turn30view1turn48search5turn48search7

**12. O9 national benchmark: recommended benchmark**

The recommended benchmark is:

**Eurostat annual unemployment rate for France in 2016: 10.1%, from `une_rt_a` (or the derived headline table `tps00203`), concept = annual average unemployment rate, % of labour force aged 15–74, EU-LFS / ILO-based.** Use this value **only if** your rebuilt national aggregation is intended to match the Eurostat national concept and geography. citeturn47view0turn32search2turn32search5

If your rebuilt GSUR lookup is instead closer to an **INSEE France hors Mayotte / household-population / 15+** concept, or if your geographic coverage ends up excluding some DROM components present in Eurostat’s France total, then cite an INSEE benchmark instead. In that case, the closest corroborating official value is also **10.1% for 2016**, but the field note must be copied exactly from the INSEE publication so that the benchmark concept is not overstated. citeturn30view0turn48search5turn48search7

## Download package and validation citations

**13. Data assets to download**

The minimum external asset package I would download and archive in the repo is the following.

From Eurostat: **`NUTS2013-NUTS2016.xlsx`**; the regional LFS tables **`lfst_r_lfp2acedu`**, **`lfst_r_lfu3pers`**, **`lfst_r_lfu3rt`**, **`lfst_r_lfsd2pop`**, and **`lfst_r_lfp2act`**; and the national benchmark table **`une_rt_a`** or **`tps00203`**. citeturn1view2turn15search2turn15search0turn15search1turn45search4turn10search0turn32search0turn32search5

From EUR-Lex: **Commission Regulation (EU) No 1319/2013** and **Commission Regulation (EU) 2016/2066**. citeturn40search1turn41search1

From INSEE: **`depts2015-txt.zip`**, **`depts2016-txt.zip`**, and, if you want the stronger France-specific territorial audit trail, **`table-appartenance-geo-communes-15.zip`** and **`table-appartenance-geo-communes-16.zip`**. Optionally archive **`reg2015-txt.zip`** and **`reg2016-txt.zip`** as compact documentation files. citeturn26view0turn24view0turn20view1turn20view0turn26view2turn27view0

**14. Citations to record in the validation report**

The validation report should record citations in a frozen, file-specific way, not merely “Eurostat website” or “INSEE website.”

For O1, the core citation should name **Eurostat, History of NUTS, historical correspondence file `NUTS2013-NUTS2016.xlsx`**, supplemented by the two EUR-Lex regulations fixing the old and new NUTS classifications. If you use the France-specific department join as a validation layer, also cite **INSEE, Code officiel géographique au 1er janvier 2015, `depts2015-txt.zip`** and **INSEE, Code officiel géographique au 1er janvier 2016, `depts2016-txt.zip`**. citeturn1view2turn40search1turn41search1turn26view0turn24view0

For O2, cite the exact Eurostat table codes used as denominator sources: **`lfst_r_lfp2acedu`** as the preferred labour-force denominator, with **`lfst_r_lfu3pers`**, **`lfst_r_lfu3rt`**, **`lfst_r_lfsd2pop`**, and **`lfst_r_lfp2act`** only if they are actually used in fallback paths. The validation report should explicitly state which denominator type was used in each cell family. citeturn15search2turn15search0turn15search1turn45search4turn10search0

For O9, cite either **Eurostat `une_rt_a` / `tps00203`** with the annual 2016 France concept, or the chosen **INSEE** publication if you deliberately match an INSEE field concept. If you cite the Eurostat benchmark, the validation report should also mention the Eurostat metadata definition that it is an **annual average unemployment rate, % of labour force aged 15–74, EU-LFS/ILO-based**, and that France includes DROM. citeturn47view0turn32search0turn32search5turn30view0

## Remaining limits

**15. Remaining unresolved issues**

The main unresolved issue is not source acquisition anymore; it is **source alignment**. The official sources solve the geography passage from modern official regional coding to pre-reform official coding, but they do **not** solve the last passage from old official regions to EUROMOD `drgn1`; that still has to come from the EUROMOD France documentation already in your project. citeturn16view0turn40search1turn41search1

A second unresolved issue is the **actual GSUR regional vintage and level** preserved in the workbook you will rebuild from. If that source still preserves recoverable **modern NUTS 2** detail, the official-source path identified here is strong. If it has already been collapsed to coarser modern region codes, this report does not authorize back-solving that lost structure from public aggregates alone. citeturn1view2turn38search1

A third unresolved issue is **benchmark geography choice**. Eurostat’s France unemployment concept includes **DROM**, whereas INSEE publications may use **France**, **France hors Mayotte**, or **France métropolitaine** depending on the table. The validation memo must lock that choice before numeric comparison. citeturn47view0turn48search5turn48search7

A fourth and smaller limitation is that this report verified the existence and relevance of the main Eurostat denominator datasets, but it did **not** perform a full live extraction of every 2016 France cell. That final extraction check belongs in the acquisition/archiving step, not in this report. citeturn15search2turn45search4