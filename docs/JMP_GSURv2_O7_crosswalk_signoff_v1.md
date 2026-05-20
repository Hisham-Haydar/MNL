# JMP GSURv2 O7 Crosswalk Sign-Off v1

I approve O7 crosswalk sign-off for the GSURv2 MNL-parquet rebuild.

The approved crosswalk is:

`Data/external/fr_drgn1_to_nuts2_crosswalk.csv`

The approved GSURv2 lookup files are:

`Data/external/FR_gsur_ruro_v2_stageA_y2014.parquet`  
`Data/external/FR_gsur_ruro_v2_stageA_y2015.parquet`  
`Data/external/FR_gsur_ruro_v2_stageA_y2016.parquet`

The approved conceptual merge key is:

`(drgn1, educ3, sex)`

The actual MNL schema is:

Singles:
- `drgn1`
- `educ3`
- `dgn`
- `gsur`

Couples:
- `drgn1`
- `educ3_male`
- `educ3_female`
- `gsur_male`
- `gsur_female`

Approved survey-year / opportunity-year mapping:

- FR_2015 uses GSURv2 opportunity year 2014.
- FR_2016 uses GSURv2 opportunity year 2015.
- FR_2017 uses GSURv2 opportunity year 2016.

For singles, the rebuild must map GSURv2 `sex` to the observed MNL `dgn` coding after verifying the coding convention.

For couples, the rebuild must use partner-specific merges:
- male partner: `(drgn1, educ3_male, sex = male)`
- female partner: `(drgn1, educ3_female, sex = female)`

This approval authorizes only the crosswalk and merge-key sign-off required before the GSURv2 MNL-parquet rebuild authorization.

This approval does not authorize:
- MNL parquet rebuild by itself;
- pooled Stage M1 stacking re-run;
- pooled estimation;
- welfare implementation or welfare computation;
- canonical promotion;
- P3b or P4;
- replacement of M1-clean 2016 as the active JMP baseline.

M1-clean 2016 remains the active JMP baseline until a later SA2 verdict explicitly promotes a fina