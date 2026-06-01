# gsplit non-identification STRUCTURE — read-only Hessian diagnostic

> Reads the EXISTING gsplit synthetic MLE Hessian (no re-fit / no re-gate). Recomputes exact jax.hessian at the gate's reported theta_hat with the same seed 20260530, then extracts cov = H^-1 and the identification geometry of the 4 relaxed gender-split params. Companion to RURO_jax_recovery_gate_gsplit_901_v1.md.

Full Hessian PD=True, min_eig=1.5319 (reproduces the gate's +1.532 -> correct MLE/seed). cov = H^-1.

## 1. Correlation matrix of the 4 relaxed params (cov = H^-1)

| | beta_E_m | beta_E_f | beta_h_pt2_m | beta_h_pt2_f |
|---|---|---|---|---|
| beta_E_m | +1.000 | +0.880 | -0.016 | -0.002 |
| beta_E_f | +0.880 | +1.000 | +0.002 | -0.011 |
| beta_h_pt2_m | -0.016 | +0.002 | +1.000 | +0.012 |
| beta_h_pt2_f | -0.002 | -0.011 | +0.012 | +1.000 |

SE(Hessian): beta_E_m=0.2279, beta_E_f=0.2231, beta_h_pt2_m=0.0640, beta_h_pt2_f=0.0630

- No |corr|>0.9 pair among the 4 (no global 4-way ridge among all four).

## 2. beta_E pair: beta_E_m , beta_E_f

- corr(beta_E_m, beta_E_f) = **+0.880**
- SE: beta_E_m=0.2279, beta_E_f=0.2231
- cov eigenvalues: stiff(identified)=6.1180e-03, soft(flat)=9.5606e-02, soft/stiff ratio=15.6
- **WELL-IDENTIFIED** (stiff) direction: CONTRAST (beta_E_m - beta_E_f)  [v=(+0.70,-0.72)]
- **FLAT** (soft) direction:           LEVEL/SUM (beta_E_m + beta_E_f)  [v=(+0.72,+0.70)]
- recovery: beta_E_m true=-0.36 -> -0.213; beta_E_f true=-1.00 -> -0.212
- **VERDICT: PARTIAL RIDGE — corr modest (+0.88) but soft/stiff ratio 16: the LEVEL/SUM (beta_E_m + beta_E_f) is much flatter. Reparam may help.**

## 3. beta_h_pt2 pair: beta_h_pt2_m , beta_h_pt2_f

- corr(beta_h_pt2_m, beta_h_pt2_f) = **+0.012**
- SE: beta_h_pt2_m=0.0640, beta_h_pt2_f=0.0630
- cov eigenvalues: stiff(identified)=3.9476e-03, soft(flat)=4.1147e-03, soft/stiff ratio=1.0
- **WELL-IDENTIFIED** (stiff) direction: mostly beta_h_pt2_f  [v=(+0.30,-0.95)]
- **FLAT** (soft) direction:           mostly beta_h_pt2_m  [v=(+0.95,+0.30)]
- recovery: beta_h_pt2_m true=-1.19 -> +0.039; beta_h_pt2_f true=+0.37 -> -0.114
- **VERDICT: INDEPENDENT MISLOCATION — corr modest (+0.01), soft/stiff ratio 1 (no strong ridge). Each param individually soft/mislocated; reparam unlikely to help.**

## 4. Full 4x4 eigenstructure (2 separate pair-ridges, or a 4-way tangle?)

cov 4x4 eigenvalues (large = flat): [0.0956 0.0061 0.0041 0.0039]

Softest (most flat) 4-direction eigenvector loadings:
- beta_E_m: -0.716
- beta_E_f: -0.699
- beta_h_pt2_m: +0.002
- beta_h_pt2_f: +0.001

The single flattest 4-direction is **almost purely the beta_E level** (beta_E_m + beta_E_f,
loadings ~0.71/0.70; pt2 loadings ~0). The pt2 pair does NOT mix with the beta_E pair —
the 4x4 block is effectively **two independent 2x2 problems**, with different structures.

---

## Synthesis — the two pairs fail DIFFERENTLY (one reparable, one not)

**The 4-way block is two independent 2x2 problems** (cross-pair |corr| < 0.02). So
each pair is diagnosed on its own, and they give OPPOSITE structures:

### beta_E pair = PARTIAL RIDGE (level flat, contrast stiffer) — reparam *might* help, but is not the binding problem

- corr(beta_E_m, beta_E_f) = **+0.880**, soft/stiff ratio **16**.
- **Identified (stiff) direction: the gender CONTRAST (beta_E_m − beta_E_f).**
  **Flat (soft) direction: the LEVEL (beta_E_m + beta_E_f).**
- Both recovered to ≈ −0.21 (beta_E_m −0.213, beta_E_f −0.212) — the optimizer pinned
  their *difference* near 0 and let their shared *level* drift. True level
  (−0.36 + −1.00)/2 = **−0.68**; recovered level ≈ **−0.21** → the flat level slid ~0.47.
  (And the true contrast +0.64 also did not recover — it landed ≈0 — so this is a ridge
  in the LEVEL plus a smaller contrast bias, not a clean "only-contrast-known" case.)
- **Caveat: beta_E is already heavily parameterized.** beta_E (the employment level)
  shares the choice set with 12 market-opportunity beta_E_* shifters + the year/region
  structure. The beta_E level is the direction most confounded with those. This is why
  beta_E_m alone "recovered OK" (0.65 SE) in the gate but the *split level* is flat: the
  split adds a second free level on top of an already level-saturated block.
- **Reparam verdict: a shared-E-level + gender-deviation reparam COULD identify the
  contrast, but the contrast itself is only modestly stiff (ratio 16, not >100) and is
  also mislocated here. Reparam is plausible but NOT clearly sufficient.**

### beta_h_pt2 pair = INDEPENDENT MISLOCATION (no ridge) — reparam CANNOT help

- corr(beta_h_pt2_m, beta_h_pt2_f) = **+0.012** (≈0), soft/stiff ratio **1.0** (no ridge).
- Each pt2 coefficient is individually well-curved (SE 0.063–0.064, among the *stiffest*
  in the model) yet each lands far from truth: beta_h_pt2_m true −1.19 → +0.039
  (wrong sign), beta_h_pt2_f true +0.37 → −0.114.
- There is **no linear combination** (no sum, no contrast) that rescues this: the cov
  ellipse is essentially circular (eigenvalues 3.95e-3 vs 4.11e-3, ratio 1.0). Both axes
  are equally (mis)identified. **A shared-level + deviation reparam buys nothing** — it
  just rotates a circle.
- This is the **binding** non-identification. The pt2 hours band [28.5, 30.5] is narrow
  and sparsely populated; splitting its coefficient by gender asks the synthetic data to
  place two separate values where it cannot reliably place even their combination at the
  truth. The large LR statistic (206.6) reflects an in-sample *fit* gain from the extra
  freedom, not the data's ability to *locate* the two coefficients.

### Overall verdict

| Pair | corr | soft/stiff | structure | flat direction | reparam can help? |
|---|---|---|---|---|---|
| beta_E (m,f) | +0.88 | 16 | **partial ridge** | level (m+f) | maybe (contrast only) |
| beta_h_pt2 (m,f) | +0.01 | 1.0 | **independent mislocation** | both equally | **no** |

**The gender split fails for TWO different reasons, and the dominant one (pt2) is NOT
reparameterizable.** A shared-level+deviation reparam might recover the beta_E *contrast*,
but the beta_h_pt2 split — which carried the largest LR signal (206.6) and the headline
"opposite signs" economic story — is independently mislocated with no rescuing combination.

**Implication for the paper:** the 47-param spec (joint_pooled_v1_bll0_tlmpin) remains the
certified baseline. If a later decomposition shows the split matters, the realistic options
are (a) split ONLY beta_E with a level+deviation reparam and re-gate the *contrast*, keeping
beta_h_pt2 pooled; or (b) accept that beta_h_pt2 cannot be gender-split at this
sample/resolution and report the pooled coefficient with the LR result as an in-sample
caveat — NOT as identified gendered estimates. Splitting beta_h_pt2 by gender is not
supportable as a structural (recoverable) parameter at 901.

