> Archived on 2026-05-26 as a documentation-only correction whose substance is reabsorbed.
> Base file (kept active): `docs/France_case/execution_logs/GSURv2/JMP_GSURv2_MNL_rebuild_authorization_v1.md`.
> See `docs/France_case/cleanup/MOVE_MANIFEST_2026-05-26_round2.md`.

# JMP GSURv2 MNL-Parquet Rebuild Authorization — Correction v1

*France 2014–2015–2016 | v1 | 2026-05-20*

---

## 1. Purpose

This document records two narrow documentation corrections applied to
`docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md`. No code was
changed. No script was run. No parquet was written. The rebuild
authorization scope, the validation requirements, the halt conditions,
and all downstream prohibitions are unchanged.

| # | Issue | Action |
|---|-------|--------|
| C1 | Extra `## Required final statements` heading (21st heading, beyond the 20 required sections) | Demoted to `**Required final statements**` plain bold text under §20 |
| C2 | Three passages stated the next gate after a passing rebuild is directly "the pooled stacking re-run authorization" | Replaced with: the next gate is a strict post-rebuild verdict; if that verdict passes, it may authorize pooled stacking re-run as the following step |

---

## 2. Heading correction

**Before:** The authorization memo had 20 numbered sections (§1–§20)
followed by a 21st heading:

```
## Required final statements
```

This made `Required final statements` an unintended 21st `##`-level
section, inconsistent with the 20-section structure stated in the
memo's own introduction.

**After:** The `##` marker is removed; the block is now:

```
**Required final statements**
```

It is plain bold text under §20. The statements themselves
(rebuild authorized after O7 sign-off; pooled stacking NOT
authorized; pooled estimation NOT authorized; welfare NOT authorized;
M1-clean 2016 remains the active baseline) are unchanged.

---

## 3. Next-gate wording correction

**Before.** Three passages in the authorization described the next
gate after a passing rebuild as directly "the pooled stacking re-run
authorization":

| Location | Original text |
|----------|--------------|
| §19 R8 | "A statement that the next gate is the pooled stacking re-run authorization (separately gated) and a confirmation that the rebuild did not perform any downstream step." |
| §19 closing paragraph | "If the rebuild passes, the next gate is the pooled stacking re-run authorization." |
| §20 "What to do next" | "If the rebuild passes, the next gate is the pooled stacking re-run authorization, which is separately gated and not authorised by this rebuild." |

This wording incorrectly implied a direct two-step path from rebuild
→ pooled stacking re-run authorization, with no intervening
verification gate between the rebuild and the pooled stacking step.

**After.** All three passages are replaced with the required wording:
"the next gate is a strict post-rebuild verdict; if that verdict
passes, it may authorize pooled stacking re-run as the following
step."

| Location | Corrected text |
|----------|---------------|
| §19 R8 | "A statement that the next gate is a strict post-rebuild verdict; if that verdict passes, it may authorize pooled stacking re-run as the following step. Confirmation that the rebuild did not perform any downstream step." |
| §19 closing paragraph | "If the rebuild passes, the next gate is a strict post-rebuild verdict; if that verdict passes, it may authorize pooled stacking re-run as the following step." |
| §20 "What to do next" | "If the rebuild passes, the next gate is a strict post-rebuild verdict; if that verdict passes, it may authorize pooled stacking re-run as the following step. Pooled stacking re-run is separately gated and not authorised by this rebuild." |

The correction does not change the authorization scope. Pooled
stacking re-run was already explicitly NOT authorized by the
rebuild memo (§17 N1); the correction clarifies only the sequencing
of the next gate, inserting the post-rebuild verdict as the
required step between the rebuild and any possible pooled stacking
re-run authorization.

---

## 4. What was not changed

The following are confirmed unchanged:

- The rebuild authorization scope: GSURv2 MNL-parquet rebuild for
  FR_2015, FR_2016, and FR_2017 remains authorized under the O7
  sign-off.
- The authorized actions (A1–A7, §16): reading inputs, verifying
  schema, verifying `dgn` coding, singles merge, couples merge,
  writing output parquets with sidecars, running validation.
- The validation checks (V1–V12, §15).
- The halt conditions (H1–H10, §18).
- The v1-fallback preservation rule (§12).
- The active GSUR variable naming rule (§13).
- The sidecar metadata requirements (§14).
- The not-authorized list (§17): pooled stacking, pooled estimation,
  welfare, canonical promotion, P3b/P4, and estimation-spec changes
  all remain NOT authorized.
- The output stems (§8), input stems (§6), GSURv2 lookup inputs
  (§7), and survey-year mapping (§5).
- The merge logic for singles (§10) and couples (§11).
- All 20 numbered section headings.
- The required final statements (authorization after O7 sign-off;
  pooled stacking NOT authorized; pooled estimation NOT authorized;
  welfare NOT authorized; M1-clean 2016 remains active baseline).

No code was changed. No data was built.

---

## 5. Final authorization status

The GSURv2 MNL-parquet rebuild remains authorized under the O7
crosswalk sign-off, within the bounds specified in
`docs/JMP_GSURv2_MNL_rebuild_authorization_v1.md`.

After correction, the memo accurately states that, if the rebuild
passes, the next gate is a strict post-rebuild verdict; if that
verdict passes, it may authorize pooled stacking re-run as the
following step. The pooled stacking re-run is separately gated and
is not authorized by this rebuild authorization.

Pooled stacking is NOT authorized.
Pooled estimation is NOT authorized.
Welfare computation is NOT authorized.
M1-clean 2016 remains the active JMP baseline.
