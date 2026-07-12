# FR 2016 Singles RURO Trial — Master Record
Sample: 1,555 single households (20-60), FR_2016_a3, priced FR_2015. negLL warm 4220.5238 -> fit **4106.6042** (31 free, 16 pinned, 2 at-bound).
## Frozen decisions
1. Working-alt benefit zeroing: components bind (bunct/bunmt/bsa zeroed; bsaot kept state-independent; input bsa00 inert). Probe-verified.
2. Take-up: bsa00yn_a=1 pricing (deterministic); household-trait mask, revealed-first (rates nw 0.548 / w 0.265), seeded Bernoulli 20162016. Rows adjusted 15,798.
3. pexp_years: liwwh/12 primary -> dew -> dey, cap dag-15, /20 rescale (certified enh_RURO_prep + harmonise). age_norm /10.
4. Occ block pinned at certified: unidentified under occ_spec='fixed' (ridge probe -0.0002; all 17,738 non-worker working draws imputed loc4=4).
5. beta_l_age2_sm/sf at certified bound 1.0 (widening->3.0 ran to bound for 2.28 nats; near-flat direction; MUC/MUL PASS at 1.0).
## Diagnostics verdicts
- MUC/MUL: 0% negative both sexes (threshold 5%) — PASS. Display quirk: MUC header theta_c=0.5 default; true theta_c_singles=-0.0771.
- Wage fit: predicted~observed densities coincide (both sexes).
- Hours fit: 35h reference-band spike missed (25%->7%); low-hour bands overshot; male 0-hours 13.9% obs vs 7.8% pred. Cause: uniform hours proposal cannot form reference-band atom. -> P2 rebuild driver #2 (with occ sampling #1).
- SEs: see trial_se_clustered.csv (sandwich, analytic scores, cluster=idorighh; single-wave ~HC-robust).
## Artifacts
theta_trial_singles_2016_v3_final.csv | trial_fit_provenance.json | fr_singles_engine_ready_v5.parquet |
outputs/trial_singles2016/ (results JSON, inline report (HTML discarded by design), *_llm_summary_*.md, trial_se_clustered.csv, occ_wage_separation_diagnostic.md)
## Open for P2
Draws rebuild: peaked hours proposal (certified log_q_H atoms) + occupation-sampled dimension (+ conditional wages per Box-24 verdict); pooled 2015-17; couples; year effects unpin; LR pooling tests.

## Post-closure addenda
- Box-24 verdict: SEPARATED (eta^2 F=0.213, M=0.128) -> occupation-conditional wage draws adopted for P2.
- SE gates: T1 3.1e-13; H_free min eig 0.1246 (PD on identified block); T5 ratio med 1.115 / max 2.887.
- Interpretive notes: theta_c_singles weakly identified (t=-1.11, robust/Hessian ratio 2.89;
  indistinguishable from log utility -- pooling expected to tighten). beta_E_drgur/drgmd
  collapsed to ~0 from certified -0.53/-0.67: urbanization opportunity effect not found in
  singles-2016 alone (gsur strongly present instead, t=-4.15). Both are P2 hypotheses.
