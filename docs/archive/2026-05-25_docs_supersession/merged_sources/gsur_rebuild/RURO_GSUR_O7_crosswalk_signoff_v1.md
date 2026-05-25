> Merged into `docs/France_case/consolidated/RURO_GSUR_rebuild_consolidated_v1.md` on 2026-05-25. See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-25.md`.

# RURO GSUR O7 Crosswalk Sign-off v1

Date: 2026-05-17

I approve O7 crosswalk sign-off for Stage A versioned GSURv2 MNL rebuild.

The approved crosswalk is:
Data/external/fr_drgn1_to_nuts2_crosswalk.csv

The approved lookup file is:
Data/external/FR_gsur_ruro_v2_stageA.parquet

The approved merge key is:
(drgn1, educ3, sex)

This approval is only for writing versioned GSURv2 MNL parquets.
It does not authorize overwriting canonical MNL files.
It does not authorize estimation until the MNL rebuild validation passes.
It does not authorize age-specific GSUR Stage B.
It does not authorize welfare computation.
