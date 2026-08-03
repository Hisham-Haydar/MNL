# MISSION JMP-M05C — Minimal Streaming Inference Implementation

**Programme:** Goal 1 — Empirical JMP  
**Manager:** Goal 1 Manager — Empirical JMP  
**Mission status:** Authorized through one audited dry run  
**Production real run:** Not authorized

## 1. Objective

Implement the accepted Phase-5 inference design using transient streamed
household scores and persisted aggregate sufficient statistics only.

The mission replaces the paused JMP-M05B execution architecture. It does not
change the statistical estimand.

## 2. Authoritative design

Read and obey:

- accepted Phase-5 inference design v4;
- `JMP_M05C_streaming_inference_design_addendum_v1.md`;
- accepted source-verification report and parameter map;
- accepted Phase-3 and Phase-4 manager records and bundles;
- `JMP_M05B_pause_and_M05C_redesign_decision_v1.md`.

The addendum prevails only on score persistence, custody, reproduction, T-12S,
T-23S, transaction, and application-surface review.

## 3. Starting-state requirement

Before implementation:

1. archive the rejected JMP-M05B working set outside Git;
2. commit its review/report evidence only;
3. remove the rejected source changes from the main working tree;
4. salvage and separately commit the Phase-4 test-42 correction;
5. require clean MNL and nested repositories;
6. record exact starting revisions.

Do not copy rejected implementation source into JMP-M05C.

## 4. Implementation strategy

Use one fresh Claude Code Opus session.

Implement in three increments.

### Increment A — Streaming score reducer

Deliver:

- canonical household iterator/order;
- bounded batch score computation using the accepted per-group likelihood;
- aggregate score vector;
- 37×37 and 35×35 meat accumulation;
- global canonical score-stream digest;
- no row-level persistence;
- actual production-path integration test on a bounded subset;
- deterministic synthetic tests.

Independent Codex review A is required before Increment B.

### Increment B — Covariance and inference objects

Deliver:

- accepted bread loading and authentication;
- model-based and corrected robust covariance;
- active-bound and fixed-pin reporting;
- regional H0-A/B/C/G tests;
- numerical gates and diagnostics;
- aggregate artifact serializers.

Independent Codex review B is required before Increment C.

### Increment C — Runner, transactions, and reproduction

Deliver:

- dry-run-only runner;
- immutable aggregate-only attempt transaction;
- T-12S fresh-process aggregate reproduction;
- T-23S no-row-persistence gate;
- manifest and provenance;
- STOPPED behavior;
- no `complete/`;
- full no-row-persistence integration tests.

Final integrated Codex review C is required before commit and dry run.

## 5. Reviewer-runnable proof rule

Every implementation claim must be demonstrated through:

- an actual production-path test;
- a bounded deterministic fixture where full data are unnecessary;
- exact command lines;
- expected outputs;
- failure tests.

Integration tests may patch expensive data size or input fixtures, but may not
replace the production evaluator, score reducer, covariance builder, or runner
orchestration being claimed.

A green test produced by replacing the subject under review is invalid.

## 6. Review and remediation budget

For each increment:

- reviewer verdict: `APPROVE`, `APPROVE AFTER FIXES`, or `REJECT`;
- one narrow remediation is permitted for `APPROVE AFTER FIXES`;
- `REJECT` is an E2 halt;
- no next increment starts without approval.

The final integrated review must return `APPROVE` before commit or dry run.

## 7. Package boundary

`dclaborsupply-monorepo` is read-only.

Reuse its accepted likelihood and generic derivatives. Do not modify package
source.

A required package change is an E2 halt and separate PKG mission.

## 8. Required aggregate artifacts

At minimum:

- `score_aggregate_summary.json`
- `score_sum_free37.csv`
- `meat_free37.npy`
- `meat_free37.csv`
- `meat_interior35.npy`
- `meat_interior35.csv`
- model covariance/correlation
- robust covariance/correlation
- standard-error table
- regional covariance and Wald-test outputs
- `phase5_diagnostics.json`
- `phase5_manifest.json`
- `phase5_console.log`

No row-level score artifact is permitted.

## 9. Dry-run authorization

After final review APPROVE and exact-state commit:

- run exactly one full 1,555-household dry run;
- write only an aggregate-only attempt under `attempts/`;
- do not create `complete/`;
- audit all gates and artifacts;
- return to the deputy programme director for production-run authorization.

## 10. Non-scope

Do not:

- run the production real execution;
- create accepted paper-facing inference claims;
- run synthetic recovery;
- run welfare or decomposition;
- modify notebooks;
- run EUROMOD;
- add couples or pooled years;
- persist household scores;
- use the restricted score store;
- revive the capability-security architecture.

## 11. Halt conditions

Stop on:

- accepted-source or bundle mismatch;
- score-identity failure;
- fresh-process digest/meat mismatch;
- any row-level score persistence;
- production evaluator replaced in an integration test;
- package modification requirement;
- review REJECT;
- unrelated dirty worktree;
- attempt to create `complete/`.

## 12. Final return packet

Return after the audited dry run:

- mission ledger;
- increment A/B/C implementation reports;
- reviews A/B/C;
- exact implementation commit;
- dry-run console, diagnostics, manifest, and aggregate artifacts;
- T-1 through T-23S gate table;
- proof no row-level score artifact exists;
- Goal 1 dry-run acceptance memo;
- recommendation on one production execution.
