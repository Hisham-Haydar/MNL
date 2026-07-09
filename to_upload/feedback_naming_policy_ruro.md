---
name: RURO naming policy — comprehensive rename completed 2026-05-20
description: The full sweep from "Stijn-style" labels to neutral RURO terminology is complete (2026-05-20). Path renames were done 2026-05-13; content rewrites + manual fixes completed 2026-05-20. Residuals are Z: paths only.
type: feedback
originSessionId: 5ca0f80f-bd09-41ef-9fe2-55bc21b9b60e
---
The repository has been **fully renamed** from `stijn_occ` / `Stijn-style`
labels to neutral RURO terminology. Path renames were applied 2026-05-13;
content rewrites (19 files) and manual post-script fixes were completed
2026-05-20 via `scripts/maintenance/rename_stijn_to_ruro.py`. The earlier
instruction to "keep historical artefacts as provenance" was explicitly
**lifted** by the user; the rename covers all of `outputs/`, `Results/`,
`reports/`, and `docs/` (outside the safe havens listed below).

**Residual `stijn` tokens (expected, not errors):** 7 tracked files contain
`stijn` only in Z: paths pointing to the out-of-scope EUROMOD shared-storage
directory (`Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/stijn_occ/...`).
`docs/RURO_NAMING_AND_PACKAGE_SCOPE_v1.md` also intentionally lists
deprecated `Stijn-style` terms in its "Do not use" column.

**Why:** the user wants a clean, country/year/specification-agnostic
package surface with no personal labels. One centralised acknowledgement
remains in `docs/ACKNOWLEDGEMENTS.md`.

**How to apply:**

- Use `ruro_occ_M0` everywhere as the model identifier.
- Use `scripts/enhanced/estimation_spec_ruro_occ_M0.yaml`. The legacy
  `estimation_spec_stijn_occ_M0.yaml` has been **deleted** (was a
  byte-identical duplicate).
- Output paths: `outputs/{estimates,post_estimation}/fr/spec/ruro_occ/...`.
- Output prefix: `fr_2016_ruro_occ_gamspy_...`.
- Reusable validation tools: `Results/_canary_ruro_occ_M0.{py,json}` and
  `Results/_validation_ruro_occ_M0.{py,json}`.
- Prose: "continuous RURO baseline", "RURO occupation-opportunity M0",
  "proposal-component aliases", "proposal-density correction", "the R
  reference implementation", "the continuous RURO reference design".

**Safe havens (personal name preserved on purpose):**

1. `stijn/` — original R-notebook `author:` fields are legitimate
   authorship metadata.
2. `docs/archive/` — sealed historical snapshot.
3. `docs/ACKNOWLEDGEMENTS.md` — the single centralised acknowledgement.

The rename script itself (`scripts/maintenance/rename_stijn_to_ruro.py`)
is also in its own safe-haven set so re-runs cannot collapse its
replacement maps.

**Out of scope (intentional):** the EUROMOD shared-storage scenario
directory `Z:/hisham/EUROMOD-STORAGE/interim/ruro/fr/2016/stijn_occ/`
remains under its old name; two docs preserve the original Z: path
deliberately. Rename via `Rename-Item` when shared-storage hygiene is
convenient.

**Policy reference:** `docs/RURO_NAMING_AND_PACKAGE_SCOPE_v1.md`.
**Rename manifests:** `Results/rename_stijn_to_ruro_manifest_<UTC>.csv`
per invocation.
