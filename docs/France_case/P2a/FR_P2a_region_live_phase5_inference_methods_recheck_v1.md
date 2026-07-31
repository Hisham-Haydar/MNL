# 1. Recheck verdict

One narrow numerical residual remains under Fix 5. Fixes 1–4 and 6–7 pass, the consequential edits C-a–C-e are entailed, and no model, estimand, or baseline change has been introduced.

# 2. Scope

This was the commissioned targeted recheck only. It examined the sections identified in the v2 §1.1 revision register against the seven required fixes in the methods review §17 and the acceptance checklist in §18. Previously approved matters were not reopened. The conditional 35-dimensional estimand, restricted bread, 35-column meat, and prohibition on symmetric Wald inference for the two active upper-bound coordinates remain unchanged.

# 3. Fix-by-fix findings (F1–F7, C-a–C-e)

- **F1 — PASS.** §§11.2, 11.5 and 19 confine the Loewner result to model-based inverse-information objects, make T-22 sample numerical KKT evidence only, remove every known-direction uncertainty claim, and state a coherent two-tier later-method trigger. §§19–20 contain no robust-covariance ordering claim.
- **F2 — PASS.** §§10.3–10.6 define `K = 35` as the local restricted dimension/rank and present `c = 1555/1520` transparently as a pre-registered HC1/CR1-style regression analogue, not an exact nonlinear M-estimation correction.
- **F3 — PASS.** §13.4 gives conformant objects `E_R ∈ ℝ^{10×35}`, `V_RR ∈ ℝ^{10×10}`, `A ∈ ℝ^{q×10}`, `r ∈ ℝ^q`, and the equivalent `R ∈ ℝ^{q×35}` form; it names every restriction row and §17.2 separates `p_model` from `p_robust`.
- **F4 — PASS.** §§11.3, 12.2 and 17.2–17.3 provide one consistent 13-column schema with `bound_value`, `bound_side`, `grad_negll`, and `multiplier`; there is no stray `flag` column; all five inferential fields are literal `NA` for active-bound and pinned rows.
- **F5 — RESIDUAL.** T-4 has the correct signed sum, T-9 equals the `1e-10` rank convention, W-4 uses the robust 95% interval and triggers on equality, and the T-19/T-22/W-4 tiers were preserved. T-7's stated backward-error derivation is not exact; see §4.
- **F6 — PASS.** The changed sections consistently describe H0-B as the common NUTS-1 intercept component, keep the ten-coordinate block distinct from the full opportunity mechanism and decomposition, and make future clustering degeneracy conditional on the future primitive contribution and repeated-unit structure.
- **F7 — PASS.** §§17.1 and 18.5 require durable, access-controlled, immutable restricted custody of authoritative bytes, with locator, hash, size, shape, layout, row/column fingerprints, disclosure class, and named retention responsibility; T-23 gates the route-specific record.
- **C-a — PASS.** The §§20.1–20.2 edits are direct claim-register consequences of F1 and F6.
- **C-b — PASS.** The §22 status and open-item updates are procedural consequences of remediation and introduce no new substantive decision.
- **C-c — PASS.** §1 and §1.1 supply the required v2 state and traceable revision register. Each register row points to the sections implementing its stated change; the sole implementation residual is the F5 exactness issue below.
- **C-d — PASS.** The front-matter changes only record version and review state.
- **C-e — PASS.** §23 updates only the process position and next handoff. C-a–C-e are entailed consequences, not scope growth.

# 4. Residuals

1. **T-7 backward-error coefficient (§15; §16.2).** The memo defines the standard dot-product factor as `γ_G = G·u/(1−G·u)` and then invokes a factor `K` for the eigenvalue perturbation, but sets `κ_BE = K·G·u`. Under that stated derivation the coefficient is instead `K·γ_G = K·G·u/(1−G·u) ≈ 6.042388811523458e-12`, not `6.0423888115224145e-12`. Replace the coefficient and displayed derivation consistently in T-7 and §16.2, using a value rounded upward, or supply another valid backward-error derivation for the retained coefficient. This is a narrow numerical-definition repair; it does not change the gate tier, model, estimand, or baseline.

# 5. Whether D-2 may be frozen and immediate next action

D-2 is substantively clear: its conditional-35 estimand and boundary treatment pass this recheck, and no boundary-aware alternative is required for the limited conditional claims. Formal freeze should nevertheless wait for the single T-7 correction and a micro-recheck limited to that coefficient in §15 and §16.2. No other remediation is required.

RECHECK FAIL — RESIDUALS
