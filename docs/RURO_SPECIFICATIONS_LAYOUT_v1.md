# RURO Estimation Specification Layout v1

Date: 2026-05-18

## Decision

All estimation-specification YAML files are now stored in:

```text
scripts/enhanced/specifications/
```

The scope of this move is the `estimation_spec*.yaml` family. Runtime or package
configuration files outside that family, such as `configs/default.yaml`, remain
in their existing locations because they are not model specifications.

## Canonical rule

For new work, use the canonical path:

```text
scripts/enhanced/specifications/<estimation_spec_file>.yaml
```

Example:

```powershell
python scripts/enhanced/enh_RURO_estimate_FR.py `
  --spec-config "scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml"
```

## Compatibility rule

Historical commands and reports often reference the former location:

```text
scripts/enhanced/<estimation_spec_file>.yaml
```

`estimation_spec_parser.py` now resolves those legacy paths to the canonical
`specifications/` directory when the file name matches an existing estimation
specification. This keeps older command transcripts usable without keeping
duplicate YAML files in two directories.

## Documentation rule

- Active documentation should use the new canonical path.
- Historical reports, archived notes, and past command transcripts may preserve
  the path that was actually used at the time.
- New memos should cite the canonical path unless they are describing an old run
  for provenance.

## Files moved

The move covered the full `scripts/enhanced/estimation_spec*.yaml` family,
including:

- continuous RURO specs;
- job-choice specs;
- RURO occupation-specification ladder files;
- provenance-only GSURv2 spec copies.

The model contents were not changed by the relocation.
