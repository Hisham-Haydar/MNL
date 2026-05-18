# Estimation Specifications

This directory is the canonical home for RURO estimation-specification YAML files.

- Scope: `estimation_spec*.yaml`
- Runtime configs such as `configs/default.yaml` stay outside this directory.
- New estimation specifications should be created here.
- Use paths such as:

```powershell
--spec-config "scripts/enhanced/specifications/estimation_spec_ruro_occ_M0c_b2_GSURv2.yaml"
```

For compatibility, the parser still resolves historical paths such as
`scripts/enhanced/estimation_spec_ruro_occ_M0c_b2.yaml` when a canonical file
with the same name exists in this directory. Historical reports can therefore
retain the path that was used at the time without breaking reproducibility.
