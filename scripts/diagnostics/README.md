# Diagnostics Scripts

This folder is for manual checks, comparisons, and investigation scripts.

Rules:

- Diagnostics can read project data and outputs.
- Diagnostics should not be required for the normal pipeline to run.
- If a diagnostic becomes a repeatable automated test, move it to `tests/`.
- If a diagnostic becomes part of the production pipeline, promote it into the relevant active pipeline folder and document it in `docs/PIPELINE_ENTRYPOINTS.md`.

