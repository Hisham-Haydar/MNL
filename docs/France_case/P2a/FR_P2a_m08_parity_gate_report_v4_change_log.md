# FR P2a — M08 Parity Gate Report v3 → v4 Change Log

**Scope:** final E2 closure, authorized by
`Job_Market_paper/docs/Missions/JMP_M08_final_E2_literature_and_decomposition_architecture_ruling_v1.md`
§2 (Deputy Programme Director, 2026-08-07), applying exactly the remedy in ruling
§2.2. Report v3 (`docs/France_case/P2a/FR_P2a_m08_parity_gate_report_v3.md`) is
unedited and remains immutable history. No code, config, manifest, chunk JSON,
attempt directory, gate statistic, tolerance, or verdict was changed to produce
report v4. No EUROMOD execution was performed. Nothing was committed.

Attempt of record (unchanged):
`20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL`,
at
`outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL/`.

---

## Change 1 — §0 residual E2-2 pairwise inference removed (ruling §2.2)

**Location:** report v3, `## 0. Supersession note`, the paragraph beginning "**The
v1 verdict `PARITY_PASS_FULL` is withdrawn as a certification.**"

**Exact old text (report v3, lines 84–90):**

> **The v1 verdict `PARITY_PASS_FULL` is withdrawn as a certification.** It is
> replaced by the verdict of the new attempt in §4, earned under the tightened
> standard. The review was explicit that its T4 rejection was *"an implementation
> defect that blocks scientific certification; not affirmative evidence of a
> scientific mismatch"* (review memo, verdict register, T4 row) — and the new run
> bears that out: the numbers are unchanged, but they are now certified rather than
> asserted.

**Exact new text (report v4, §0), verbatim per ruling §2.2:**

> **The v1 verdict `PARITY_PASS_FULL` is withdrawn as a certification.** It is
> replaced by the verdict of the new attempt in §4, earned under the tightened
> standard. The review classified its T4 rejection as an implementation defect that
> blocked scientific certification rather than affirmative evidence of a finite
> scientific mismatch.

**What was deleted and why.** The first sentence of the pair ("The review was
explicit that its T4 rejection was …") is retained in substance — as the ruling's
replacement sentence — but the second clause, joined by the em-dash ("— and the
new run bears that out: the numbers are unchanged, but they are now certified
rather than asserted"), is deleted in full. Per ruling §2.1, that clause made a
pairwise inference between the old (withdrawn) attempt and the new attempt of
record — asserting that the new run's numbers match the old run's numbers — which
is outside the new attempt's own packet and conflicts with the report-wide rule
that prior attempts provide lineage only, not numerical corroboration. The
replacement sentence keeps the reviewer's classification of the T4 finding
(implementation defect, not evidence of a scientific mismatch) and drops every
word that referenced the new run's relationship to a prior run's numbers.

**No new citation required.** The replacement sentence contains no numerical
value and cites no manifest or chunk-JSON field; it restates, in the ruling's
exact words, the review memo's own classification of its T4 finding — the same
classification report v3 already quoted (review memo, verdict register, T4 row).
No traceability gap is introduced.

---

## Change 2 — supersession and change declaration (ruling §2.2)

**Location:** report v4 only; new section titled "Report v4 status — E2 final
closure", inserted after the title/metadata block and before the (unchanged)
"Report v3 status — E2 documentary correction" section that report v3 carries
about report v2.

**Nature of change:** addition, not a replacement of existing v3 text. No text of
report v3 was removed to make room for it.

**New text added (report v4):** states, per ruling §2.2, that (a) report v4
supersedes report v3; (b) report v3 remains immutable history; (c) the only
substantive change is removal of the residual E2-2 pairwise inference in §0
(Change 1 above); (d) the attempt of record, the gate code, the gate packet,
every certified statistic, the `1.0e-6` EUR tolerance, and the `PASS` verdict are
unchanged from report v3; (e) no execution occurred to produce this report. Full
text is reproduced in report v4 in the section named above.

**Ancillary bookkeeping (not a substantive change):** the document title line was
updated from "Report v3 (UNCOMMITTED)" to "Report v4 (UNCOMMITTED)" to match the
new filename; this is the only other textual difference from report v3's title
block, and the "(UNCOMMITTED)" tag, the Mission/Authority/Scope-discipline/
Produced-against lines, and all commit hashes are otherwise identical to report
v3.

**Mechanical cross-reference repair.** None required beyond the title-line
bookkeeping above. Every other reference to `v1`, `v2`, or `v3` filenames,
rulings, or section numbers already present in report v3's text (the "Report v3
status" section's own reference to `FR_P2a_m08_parity_gate_report_v2.md` and to
`FR_P2a_m08_parity_gate_report_v3_change_log.md`; the `§0` cross-references at
report v3 lines 418 and 638; every `v1`-lineage reference in §§0–9) is a
historically accurate statement about an earlier transition and remains true,
unedited, inside report v4; none of them describes report v4 itself, so none
required repair.

---

## Diff summary — confirming no other substantive change

Report v4 was produced by taking the full text of report v3 and applying exactly:

1. Title line: `v3` → `v4` (bookkeeping only, §"Ancillary bookkeeping" above).
2. One inserted section ("Report v4 status — E2 final closure") stating the
   ruling §2.2 supersession declaration — an addition, no v3 text removed.
3. One sentence replacement inside the existing `## 0. Supersession note`
   paragraph (Change 1): the pairwise-inference clause is deleted and replaced
   with the ruling's exact substitute sentence.

Everything else — the metadata block; the entire "Report v3 status — E2
documentary correction" section; the remainder of `## 0. Supersession note`
(both the sentence preceding the edited one and everything following it);
§§1–9; and the explicit scope statement — is reproduced character-for-character
from report v3. In particular, unchanged and verified identical to report v3:

- the attempt-of-record id and directory;
- every cell of the §3 execution-record table, §4.1 per-chunk table, §4.2
  finiteness table, and §4.3 aggregate table (all values and all citations);
- the `1.0e-6` EUR tolerance, the `ils_dispy` gate column, the `bsa00_s` witness
  column, and `witness_nonfiniteness_gates: false`;
- the `PASS` verdict and all five items of the §4.4 verdict basis, including
  item 5 ("The certification verdict rests solely on the attempt of record and
  its eight chunk JSONs. Earlier attempts are retained as code-lineage and
  procedural history only and do not provide numerical support for this
  verdict.");
- the §5 code-lineage table and digest values;
- the §6 non-packet context (fenced **NOT GATE-PACKET EVIDENCE**, unchanged);
- the §7 findings register (T4 and T7 disposition tables);
- the §8 limitations;
- the §9 provenance tables and file-hash listing;
- the explicit scope statement and its final line.

**Full-text scan for residual pairwise or numerical-corroboration language.**
Every occurrence of "pairwise", "bears that out", "numbers are unchanged",
"certified rather than asserted", and "corroborat" in report v4 was checked
after the edit. Two occurrences remain, both inside the unedited, historical
"Report v3 status" section, both describing — accurately — that the earlier
(v2→v3) correction already removed a *different* pairwise-determinism clause
from §4.4 and that no prior attempt is cited anywhere as pairwise-equality
evidence; neither is itself a pairwise inference. No statement anywhere in
report v4 uses a prior attempt as numerical support or pairwise corroboration
for the attempt of record.

No code file, config file, manifest, chunk JSON, or attempt directory was read,
written, hashed, or otherwise touched to produce report v4. No EUROMOD execution
occurred. No gate statistic, tolerance, comparator behavior, or verdict changed.
This correction is confined to ruling §2.2.
