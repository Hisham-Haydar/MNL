# RURO Naming And Package Scope v1

## Purpose

The package-facing terminology should describe the model as RURO, not as a
person-specific style. Earlier development files used `stijn_occ` as a working
label because the continuous branch was compared against an existing RURO
reference implementation. That label should not be treated as the name of the
method.

Personal acknowledgements are centralized in:

```text
docs/ACKNOWLEDGEMENTS.md
```

## Preferred Terms

| Avoid in package-facing text | Use instead |
| --- | --- |
| Stijn-style baseline | continuous RURO baseline |
| Stijn occupation M0 | RURO occupation-opportunity M0 |
| Stijn proposal aliases | proposal-component aliases |
| Stijn prior correction | proposal-density correction |
| Stijn log_q aliases | layered proposal components |
| Stijn-style enhanced branch | enhanced continuous RURO branch |

## Active Specification Name

New runs should use:

```text
scripts/enhanced/estimation_spec_ruro_occ_M0.yaml
```

The older file

```text
scripts/enhanced/estimation_spec_stijn_occ_M0.yaml
```

is retained only as a compatibility/provenance artifact for completed runs and
older documentation.

## Method Description For Papers

Use wording like:

```text
We estimate preferences in a Random Utility Random Opportunity (RURO)
framework. Alternatives are sampled over employment, hours, wages, and
occupation. The systematic choice index adds preference utility and additive
opportunity components, then subtracts the log proposal density exactly once.
Occupation enters the opportunity block and not the direct utility function.
```

This describes the model object without tying it to a person-specific label.

## Archival References

References to older comparison material, historical notes, and completed run
folders may still contain `stijn` in filenames. Do not rewrite those blindly:
they are provenance labels, not the package API.
