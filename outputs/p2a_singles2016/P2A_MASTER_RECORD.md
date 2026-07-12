# FR 2016 Singles RURO — P2a Rebuild Master Record
Sample: 1,555 single households (20-60), FR_2016_a3, certified B-pool draws (101 alts/HH).
negLL fit **19071.6562** (37 free / 10 pinned / 2 at-bound; occupation block ESTIMATED, not pinned).
## What changed vs the trial (negLL 4106.6042; occ pinned; uniform proposals)
1. Draws design: certified B-pool (D1 hours mixture, W1 occ-conditional wages, empirical occ, pi0=0.10, seed 2026).
2. Band convention: bpool (11342/7391/7541 rows reflagged vs assembled; negLL 19071.6562 vs 19130.4360).
3. Occupation block now FREE and identified (P2a-4 ridge probe nonzero; trial was -0.0002).
4. theta_c_singles = 0.0943.
## Verdict artifacts (outputs/p2a_singles2016/)
- P2a-6 inline report: the hours-distribution figure is the rebuild verdict (target: the 33.5-36.5 band recovering toward the observed ~25%).
- P2a-7 SEs: p2a_se_clustered.csv (sandwich, analytic scores, cluster=idorighh; occupation-block SEs included).
- results JSON + *_llm_summary_*.md + PNGs in the same folder.
## Provenance
theta_p2a_singles_2016_v1.csv | p2a_fit_provenance.json | fr_singles_engine_ready_p2a_bpool.parquet
