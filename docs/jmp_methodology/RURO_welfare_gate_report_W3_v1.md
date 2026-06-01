# RURO Welfare Gate Report — W^3 (Stage One)

**Date:** 2026-06-01
**Stage:** ONE only (build the welfare scaffold + run W^3 validation gates).
**Status:** **BLOCKED at reproducibility preflight — implementation NOT started.**
**Repo HEAD at report time:** `7cac2e3`.

> This report records a **hard STOP at preflight**, per the Stage One instruction:
> *"Verify `JMP_welfare_spec_v5.md` is tracked/committed. If it is untracked or
> dirty, STOP and report that implementation is blocked until the frozen authority
> is version-controlled."* No welfare source was created, no config was written, no
> estimation/welfare/decomposition/bootstrap/data-rebuild script was run, and no
> welfare numbers were computed. Nothing was committed.

---

## Blocking finding

**The frozen welfare authority `docs/jmp_methodology/JMP_welfare_spec_v5.md` is
UNTRACKED in git.** It exists on disk (35,706 bytes) but is not version-controlled
(`git status` → `?? docs/jmp_methodology/JMP_welfare_spec_v5.md`; it is **not**
gitignored). The entire Stage One build must be grounded against this memo as the
frozen authority; building against an untracked, mutable file would make the
implementation non-reproducible and the contract un-auditable (the contract
`RURO_welfare_scaffold_design_contract_v2.md` cites `JMP_welfare_spec_v5.md` as its
source of authority in ~20 places).

For contrast, every *other* authority file in the chain **is** tracked:
`JMP_welfare_spec_v1..v4.md`, `RURO_welfare_scaffold_design_contract_v1.md`,
`RURO_welfare_scaffold_design_contract_v2.md`, and
`welfare_proposal_individualisation_check.md`. v5 is the lone untracked authority.

**Resolution required before Stage One may proceed:** commit
`JMP_welfare_spec_v5.md` (and confirm it is clean/non-dirty) so the frozen authority
is version-controlled. This report does not perform that commit — fixing the
blockage is a deliberate, separately-authorised act, not something this run resolves
by guess.

---

## Preflight results

### Preflight 1 — Reproducibility

| Check | Result | Evidence |
|---|---|---|
| `JMP_welfare_spec_v5.md` tracked/committed & clean | **FAIL (BLOCKING)** | `git status --porcelain` → `?? docs/jmp_methodology/JMP_welfare_spec_v5.md` (untracked); `git check-ignore` → not ignored; file present on disk (35,706 bytes) |
| `theta_hat_realdata_901_v1.csv` exists | PASS | `scripts/bpool/specs/theta_hat_realdata_901_v1.csv` (3,423 bytes, 47 params) |
| `estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` exists | PASS | `scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml` (15,925 bytes) |
| Production 901-alt engine-ready data exists | PASS | `EUROMOD-STORAGE/new_data/fr_p3a_bpool_engine_ready__couples.parquet` (342M), `__singles.parquet` (52M), `__mnlmeta.json` (2.3K) |

**Preflight 1 verdict: FAIL (blocking).** The data inputs are all present; the sole
failure is the version-control status of the frozen authority. Because the
instruction makes this a hard STOP, the remaining preflights and all gates are
**not executed**.

### Preflight 2 — Engine parity

**NOT RUN** — gated behind Preflight 1. (Planned: inspect `build_jax_singles_ll` /
`build_jax_couples_ll` in `scripts/bpool/jax_ll_probe.py` for row-level
`V = u + log_h + log_w + log_market - log_prior` and household-logsum exposure;
add a shared component extractor / parity wrapper if not directly exposed; this
feeds Gate 0.)

### Preflight 3 — Draw-multiplier datasets

**NOT RUN** — gated behind Preflight 1. (Planned: check whether the datasets for
`core.integration.per_household_stability.draw_multipliers` exist; if absent, mark
the formal draw-growth stability sub-gate BLOCKED and compute production-resolution
ESS diagnostics only — never rebuild data or fabricate higher-draw inputs.)

---

## Gate results

All gates are **NOT RUN** (build not started; preflight STOP). Recorded here with
their contract cross-reference so the mapping is on file for the Stage One run once
the blockage is cleared.

| This report's gate | Status | Maps to contract `RURO_welfare_scaffold_design_contract_v2.md` |
|---|---|---|
| **Gate 0 — Engine parity** | NOT RUN | **Not in §6.** An implementation-parity gate added to make the contract's "one machine" guarantee (§1 — *"call the same utility and opportunity-density construction as the estimator"*) **falsifiable**. Welfare core's logsum/likelihood at `theta_hat` must match the estimator within declared tolerance (smoke + production); failure stops the run. |
| **Gate 1 — Welfare integration** (parts (i)–(ii): `V_i^IS` draw-growth stability; ESS diagnostic + max-normalised-weight + flagged-subset `V_i^dir` cross-check) | NOT RUN | **§6 gate 1**, the three-part welfare-integration gate — **parts (i) and (ii)**. |
| **Gate 4 — W^3 reference coverage** | NOT RUN | **§6 gate 1 — part (iii)** (reference-coverage / EUROMOD gate). For W^3 the laissez-faire reference is the household's own set with pay, so coverage is checked against existing `c_ij`; the `Ā/J/o` EUROMOD exposure is a later W^5/W^6 issue, **not** triggered by W^3. |
| **Gate 2 — Inversion sanity** | NOT RUN | **§6 gate 2** (inversion sanity: reference recovers zero, monotonicity, bracketing convergence per household). |
| **Gate 3 — Household-unit integrity** | NOT RUN | **§6 gate 3** (one `Omega_i` per couple from joint utility/budget; no per-capita split; type-conditional references). |

**In words:** this report's **Gate 1 parts (i)–(ii)** and **Gate 4** together
constitute contract **§6 gate 1** (the three-part welfare-integration gate), with
**Gate 4** being its **part (iii)** reference coverage. **Gate 2** = contract §6
gate 2 (inversion sanity). **Gate 3** = contract §6 gate 3 (household-unit
integrity). **Gate 0** is an implementation-parity gate **not** in §6, added to make
the contract's "one machine" guarantee in §1 falsifiable. (The Shapley-exhaustiveness
gate named in §6 is a forward requirement of the deferred decomposition contract and
is out of scope for this Stage One W^3 build.)

---

## Scope statement (carried even though no computation occurred)

Any W^3 welfare distribution or `I(Omega^3)` that *would* be computed during these
gates is an **INTERNAL validation artifact, not a welfare finding**, pending
separate Stage Two authorisation. No such artifact exists yet — the run stopped at
preflight before any welfare computation.

This Stage One scope explicitly **excludes** (not run, not implemented): decomposition,
bootstrap, gender-split robustness, stochastic dominance, intra-household
equivalisation, and `W^1/W^2/W^4/W^5/W^6` as reportable measures.

---

## Commands run (read-only preflight only)

```
git ls-files --error-unmatch docs/jmp_methodology/JMP_welfare_spec_v5.md
  → error: pathspec did not match any file(s) known to git   (UNTRACKED)
git status --porcelain docs/jmp_methodology/JMP_welfare_spec_v5.md
  → ?? docs/jmp_methodology/JMP_welfare_spec_v5.md
git check-ignore -v docs/jmp_methodology/JMP_welfare_spec_v5.md
  → (not ignored)
ls -la docs/jmp_methodology/JMP_welfare_spec_v5.md
  → present, 35,706 bytes
ls scripts/bpool/specs/theta_hat_realdata_901_v1.csv
       scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin.yaml
  → both present
ls EUROMOD-STORAGE/new_data/fr_p3a_bpool_engine_ready__{couples,singles}.parquet
       fr_p3a_bpool_engine_ready__mnlmeta.json
  → all present (342M / 52M / 2.3K)
git rev-parse --short HEAD  → 7cac2e3
```

No `.venv\Scripts\python.exe` execution occurred; no source/config files were created.

---

## Next action (for the operator, not performed here)

1. Commit `docs/jmp_methodology/JMP_welfare_spec_v5.md` so the frozen authority is
   version-controlled and clean.
2. Re-invoke the Stage One W^3 build. With Preflight 1 cleared, the run proceeds to
   Preflight 2 (engine parity inspection + Gate 0), Preflight 3 (draw-multiplier
   dataset check), then Gates 0–4 in two passes (smoke → production), producing the
   welfare source under `scripts/welfare/`, the resolved config
   `scripts/welfare/configs/welfare_stage1_w3.yaml`, and the updated version of this
   report.
