# France_case/NC_pilot/ — couples 30×30=900 alternatives pilot

The NC pilot is the alternative track that builds the couples choice set as the **product** of male and female opportunity draws (30 × 30 = 900 alternatives per couple) rather than the index-paired diagonal (100 alternatives) used in earlier specs. Singles continue with 100 draws (ideally 99 + 1 observed, equivalent in expectation).

NC pilot is **active** alongside P3a; the two are concurrent tracks per `_shared/governance/RURO_spec_redesign_decisions_v2.md` §D-SCOPE. M1-clean 2016 (the single-year P3a baseline) remains the active JMP baseline until SA2 verdict.

## What changed vs job_model

- The archived `job_model/` track defined a choice as a discrete (occupation, hours, wage) combination
- NC builds the choice as a **draw-based product** of male × female opportunity draws, priced through EUROMOD per draw
- Both partners are deciders in every run (Strategy C′ as of stage5 v2)

## Subfolders

- **`design/`** — design memos and spec contracts:
  - `JMP_NC_pilot_spec_contract_v1.md`
  - `JMP_NC_pilot_vectorized_estimator_design_contract_v1.md`
  - `JMP_NC_pilot_optimizer_multistart_design_memo_v1.md`
  - `JMP_NC_pilot_beta_l0_m_specification_review_v1.md`

- **`execution_logs/`** — dated run reports, amendments, verdicts (17 files covering optimizer chain, diagnostic chain, precompute chain, stage 1-5 amendments)

## Cross-track references

- `RURO_pilot_gsurv2_verification_v1.md` (in `../P3a/consolidated/`) verifies both the GSURv2 MNL merge and the NC pilot spec structure
- `_shared/governance/RURO_spec_redesign_decisions_v2.md` governs both NC and P3a

## Sibling tracks

- [`../P3a/`](../P3a/) — active 3-year stacked estimation
- [`../job_model/`](../job_model/) — archived
- [`../_shared/`](../_shared/) — cross-track material
