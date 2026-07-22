# FR 2016 Singles RURO — P2a Rebuild Master Record

> **Two vintages — read first (updated 2026-07-22).** Neither P2a fit is the certified pooled baseline (`joint_pooled_v1_bll0_tlmpin`, negLL 238504.6360973987), and neither is accepted.
> 1. **Region-dead — negLL 19071.6562 — DIAGNOSTIC / SUPERSEDED.** Original fit with region/urbanisation/GSUR **zero-stubbed at engine-ready assembly** (a wiring bug). The `2026-07-12`-dated post-estimation artifacts in this folder (SEs `p2a_se_clustered.csv`, solver diagnostics, `p2a_singles2016_params.csv`, PNGs) describe **this** vintage and are retained as labelled history.
> 2. **Region-live — target negLL 19053.4655 — PROVISIONAL, awaiting production rebuild.** A data-wiring repair revived region/urbanisation/GSUR (`drgn1, drgur, drgmd, drgru, gsur`); same spec/bounds/start/JAX engine (`beta_E` −4.31→−0.75). Only the results JSON, `_v2` engine-ready parquet and mnlmeta were regenerated (`2026-07-13`); a region-live Hessian/eigenvalues, gradient, cluster-robust SE and post-estimation report **do not exist**. **Not accepted; not safe for inference, manuscript results, or certified welfare.** See `dclaborsupply-monorepo/docs/validation/FR_P2a_region_live_promotion_readiness_v1.md`.

## Region-live fit (provisional — negLL 19053.4655)

Sample: 1,555 single households (20-60), FR_2016_a3, certified B-pool draws (101 alts/HH).
negLL fit **19053.4655** (37 free / 10 pinned / 2 at-bound; occupation block ESTIMATED, not pinned). Prior region-dead vintage: negLL 19071.6562.
## What changed vs the trial (negLL 4106.6042; occ pinned; uniform proposals)
1. Draws design: certified B-pool (D1 hours mixture, W1 occ-conditional wages, empirical occ, pi0=0.10, seed 2026).
2. Band convention: bpool (11342/7391/7541 rows reflagged vs assembled; negLL 19071.6562 vs 19130.4360).
3. Occupation block FREE and identified; region/urbanisation/gsur revived from zero-stubs (negLL 19071.6562 -> 19053.4655; beta_E absorbed the regional variation).
4. theta_c_singles = 0.0935.
## Verdict artifacts (outputs/p2a_singles2016/)
- P2a-6 inline report: the hours-distribution figure is the rebuild verdict (target: the 33.5-36.5 band recovering toward the observed ~25%).
- P2a-7 SEs: p2a_se_clustered.csv (sandwich, analytic scores, cluster=idorighh; occupation-block SEs included).
- results JSON + *_llm_summary_*.md + PNGs in the same folder.
## Provenance
Region-live: `theta_p2a_singles_2016_v1.csv` and `theta_p2a_singles_2016_v2.csv` (numerically identical region-live theta, differ only in float precision) | `p2a_fit_provenance.json` (records negLL 19053.4655; its `theta_csv` pointer is retained as `v1` — see note there; engine-ready is `_v2`) | `fr_singles_engine_ready_p2a_bpool_v2.parquet` (region revived). Region-dead history used `fr_singles_engine_ready_p2a_bpool.parquet`.
