# FR P2a — M08 Parity Gate Report v4 Acceptance Note

**Programme:** Goal 1 — Empirical JMP. **Mission:** JMP-M08, contract §1–§2
(parity correction + gate), Stage B step 3.
**Issued by:** Goal 1 Manager, as the acceptance note required by the Deputy
Programme Director's binding disposition at
`Job_Market_paper/docs/Missions/JMP_M08_final_E2_literature_and_decomposition_architecture_ruling_v1.md`
§2.3 ("On ACCEPT: v4 becomes the parity report of record; create one acceptance
note; freeze the parity axis; proceed without deputy contact").
**Date:** 2026-08-07.
**Produced against:** MNL `520441a653f04196bf1e92e3658a478b4feb3718` (pre-commit);
nested `dclaborsupply-monorepo` `27756a06ea189339aa82915ed2124628afed20eb` (clean,
untouched).
**Execution:** none. No code, config, manifest, chunk JSON, attempt directory,
gate statistic, tolerance, or verdict was created, read for modification, or
changed to produce this note. No EUROMOD execution occurred. No welfare number,
measure, or estimate was computed.

---

## 1. The final narrow verification returned ACCEPT

The final verification required by ruling §2.3 — one fresh GPT-5.6 Codex
read-only review, restricted to exactly the four listed items, with no code
review, gate rerun, EUROMOD execution, architecture review, or new requirement
permitted — returned **VERDICT: ACCEPT** on all four items:

| # | Item as specified in ruling §2.3 | Verdict |
|---|---|:--:|
| 1 | The pairwise-inference clause is gone from `FR_P2a_m08_parity_gate_report_v4.md` §0 | **ACCEPT** |
| 2 | No statement elsewhere in report v4 says prior attempts numerically corroborate the attempt of record | **ACCEPT** |
| 3 | Prior attempts are lineage/history only | **ACCEPT** |
| 4 | No extra substantive or numerical change exists from report v3 to report v4 | **ACCEPT** |

The reviewed remedy is the one ruling §2.2 authorized and no more: the §0
sentence carrying the old-versus-new pairwise inference ("… and the new run bears
that out: the numbers are unchanged, but they are now certified rather than
asserted") is deleted and replaced with the ruling's exact substitute sentence;
one v4 supersession declaration is added; the title line is updated for version
bookkeeping. Change accounting is at
`FR_P2a_m08_parity_gate_report_v4_change_log.md`, which also records the
post-edit full-text scan for residual pairwise / numerical-corroboration
language and confirms the two remaining occurrences are inside the unedited
historical "Report v3 status" section and are not themselves pairwise
inferences.

Under ruling §2.3 this ACCEPT is terminal for the E2 axis: the REJECT branch
(return to the deputy, no further self-authorized correction) is not engaged.

## 2. Report of record and retained history

**`docs/France_case/P2a/FR_P2a_m08_parity_gate_report_v4.md` is the parity-gate
REPORT OF RECORD.** It supersedes report v3, which supersedes v2, which
supersedes v1.

The following are retained on disk as **immutable history** — unedited, not
superseded away, not deleted, and committed alongside the report of record so
the full correction lineage remains auditable:

| Artifact | Status |
|---|---|
| `FR_P2a_m08_parity_gate_report_v1.md` | superseded; certification withdrawn; retained unedited |
| `FR_P2a_m08_parity_gate_report_v2.md` | superseded; retained unedited |
| `FR_P2a_m08_parity_gate_report_v3.md` | superseded; retained unedited |
| `FR_P2a_m08_parity_gate_report_v3_change_log.md` | retained |
| `FR_P2a_m08_parity_gate_report_v4_change_log.md` | retained |
| `FR_P2a_m08_codex_production_path_review_v1.md` | retained (review memo, overall REJECT) |
| `FR_P2a_m08_codex_reverification_T4_T7_v1.md` | retained (review memo, overall REJECT) |
| `FR_P2a_m08_parity_diagnosis_memo_v1.md` | retained (Route 6 → Route 1 diagnosis under R-60) |
| all four attempt directories under `outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/` | retained; attempts 1–3 untouched by the certified run and retaining their original modification times |

No superseded report is to be edited, and no attempt directory is to be
modified, pruned, or promoted. `complete/` was never created.

## 3. Certified result of record

The certified result is the verdict of attempt

```
20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL
```

published under
`outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/`, containing
`gate_manifest.json`, eight `chunk_priced_*.json`, and `reconstruction_log.txt`.

| Certified fact | Value | Source |
|---|---|---|
| Chunks | **8 / 8**, `is_full_run: true` | `gate_manifest.json → aggregate.chunks_run`, `→ aggregate.chunks_on_grid`, `→ aggregate.is_full_run` |
| Rows compared | **225,836**, asserted equal to stored rows (chunk-wise and in aggregate) | `→ aggregate.rows_compared`, `→ aggregate.rows_compared_from_chunks`, `→ aggregate.rows_compared_equals_stored_rows` |
| Gate column / tolerance | `ils_dispy` at `1e-06` EUR (frozen, contract D10) | `→ aggregate.gate_column`, `→ aggregate.tol_eur` |
| Max abs diff, gate | **0.0**; rows above tolerance **0** | `→ aggregate.ils_dispy_max_abs_diff`, `→ aggregate.rows_above_tol` |
| Non-finite, gate column | **0** stored / **0** repriced; `all_gate_values_finite_both_sides: true` | `→ aggregate.gate_nonfinite_stored`, `→ aggregate.gate_nonfinite_repriced`, `→ aggregate.all_gate_values_finite_both_sides` |
| Witness column `bsa00_s` | max abs diff **0.0**, rows above tol **0**, non-finite **0** / **0**; `witness_nonfiniteness_gates: false` | `→ aggregate.bsa00_s_max_abs_diff`, `→ aggregate.bsa00_s_rows_above_tol`, `→ aggregate.bsa00_s_nonfinite_stored`, `→ aggregate.bsa00_s_nonfinite_repriced`, `→ aggregate.witness_nonfiniteness_gates` |
| EUROMOD hard errors | **zero** on every chunk (`euromod_hard_errors: []`); `chunks_failing: []` | `chunk_priced_*.json → euromod_hard_errors`; `gate_manifest.json → aggregate.chunks_failing` |
| **Verdict** | **`PASS`** | `→ aggregate.verdict` |

Characterisation, carried forward exactly as report v4 §4.4 states it: this is
equality of `float64` values at absolute tolerance `1.0e-6` EUR, every compared
value proven finite on both sides after coercion, observed maximum difference
identically `0.0`. **It is not a bitwise comparison and no bit-for-bit claim is
made.** The certification rests solely on the attempt of record and its eight
chunk JSONs; earlier attempts supply code lineage and procedural history only.

The limitations at report v4 §8 are accepted unweakened and travel with this
acceptance: the pinned cache persists only `ils_dispy` and `bsa00_s` as priced
outputs, so no stored-versus-repriced difference exists for `ils_origy`,
`ils_sicdy`, `ils_tax`, or `ils_ben`; a PASS licenses reproducibility of the M08
baseline's own consumption through the production path at production geometry
and nothing about pricing redrawn nodes; and the gate covers the FR-2016 singles
P2a cell only.

## 4. The parity axis is FROZEN

Effective on this note:

1. **No further parity work is authorized within M08** — no re-run, no
   additional chunk, no re-execution of the gate, no widening of the compared
   column set, no new attempt directory.
2. **No further parity review is authorized within M08.** The review sequence is
   closed; T1–T7 and R1–R4 are all disposed of, and the four §2.3 items are
   ACCEPTed. No new review may reopen an accepted threat.
3. **No further parity correction is authorized within M08.** Reports v1–v4 and
   both change logs are final as written. Ruling §2.3's REJECT branch is not
   engaged, so no self-authorized correction remains available.
4. **Joint batching remains unlicensed.** F3-R2B's proof of batch-context
   dependence stands. Any Stage-D node pricing — indeed any redrawn-node pricing
   anywhere downstream — uses **target-only D-BEN Option B geometry**, with the
   counterfactual on the target household alone. The PASS certified here is not
   a licence for joint-batch redrawing; target-only and full-chunk geometry
   coincide in a parity run *only* because the target node is the stored node.
5. The P3a b-pool failure recorded at report v4 §6.2/§6.3 remains **open** and
   outside this freeze. Its leading explanation (build vintage against a changed
   EUROMOD system) is attribution, not demonstrated causation, and no P3a work is
   authorized by this note.

Anything that would reopen the parity axis is a matter for the deputy under
ruling §5's return rule, not for manager authority.

## 5. Review lineage

Production-path review (`FR_P2a_m08_codex_production_path_review_v1.md`; overall
REJECT — T1, T2, T3, T5, T6 ACCEPT, T4 comparison-soundness REJECT for failing
open on non-finite values, T7 claim-to-evidence REJECT, both classified as
implementation/disclosure defects blocking certification rather than affirmative
evidence of a scientific mismatch) → rule-3 conversion (comparator fixed so
either-side non-finiteness becomes `+inf` and necessarily fails and is captured,
per-side finiteness accounting persisted, rows-compared asserted against stored
rows, certified full re-run as attempt
`20260806T062050Z_339096_…_parity_PARITY_PASS_FULL`, issued as report v2) →
narrow re-verification (`FR_P2a_m08_codex_reverification_T4_T7_v1.md`; R1 T4 cure
ACCEPT, R2 T4 witness delta ACCEPT, **R3 T7 cure REJECT** for two packet-only
numerical claims not tracing to the new attempt, R4 earned verdict ACCEPT on
independent recomputation from the eight new chunk JSONs) → deputy E2 ruling
(`JMP_M08_E2_parity_report_v3_documentary_correction_ruling_v1.md`) → report v3
(the two authorized documentary corrections: realised-elapsed-time statement
replacing projected runtime, and the ruling's substitute sentence replacing the
three-execution pairwise determinism claim) → final E2-2 residual (report v3 §0
still carried a pairwise inference between the withdrawn and the certified
attempt) → deputy final ruling
(`JMP_M08_final_E2_literature_and_decomposition_architecture_ruling_v1.md` §2) →
report v4 (that clause deleted and replaced verbatim; supersession declaration
added; nothing else substantive) → **ACCEPT** on all four §2.3 items, recorded
here.

---

## Explicit scope statement

France 2016 singles P2a cell only. This note records an acceptance and a freeze;
it authorizes no computation. No production pricing code changed. No redrawn
node. No counterfactual covariate. No welfare number, no measure, no `V_i^dir`,
no re-estimation. No couples, no pooled years, no other cell. No stored
consumption value modified, replaced, or regenerated. No EUROMOD execution.

**Authorised by this note: nothing beyond the record of the acceptance and the
freeze of the parity axis.**
