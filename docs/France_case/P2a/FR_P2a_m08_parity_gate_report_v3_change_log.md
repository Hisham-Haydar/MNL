# FR P2a — M08 Parity Gate Report v2 → v3 Change Log

**Scope:** documentary correction only, authorized by
`Job_Market_paper/docs/Missions/JMP_M08_E2_parity_report_v3_documentary_correction_ruling_v1.md`
(Deputy Programme Director, 2026-08-06), applying exactly the two corrections in
ruling §§3.1–3.2 and the supersession declaration in ruling §3.3. Report v2
(`docs/France_case/P2a/FR_P2a_m08_parity_gate_report_v2.md`) is unedited and
remains immutable history. No code, config, manifest, chunk JSON, attempt
directory, gate statistic, tolerance, or verdict was changed to produce report v3.
No EUROMOD execution was performed. Nothing was committed.

Attempt of record (unchanged):
`20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL`,
at
`outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL/`.

---

## Change 1 — §3 runtime statement (ruling §3.1)

**Location:** report v2, §3 "Certified full re-run — execution record", the
paragraph immediately following the execution-record table.

**Exact old text (report v2, lines 230–232):**

> **Runtime guard:** not triggered. Projected and realised runtime was ~19 minutes
> for the complete grid; no chunk was sampled, truncated, or deferred, and no
> manager decision on cost was required.

**Exact new text (report v3, §3):**

> Realised elapsed time for the complete grid was 19 minutes 20 seconds; no chunk
> was sampled, truncated, or deferred (`started_utc` `2026-08-06T06:20:50Z` →
> `finished_utc` `2026-08-06T06:40:10Z`; requested chunks
> `[0,200,400,600,800,1000,1200,1400]` equal the full chunk grid, `is_full_run: true`,
> eight of eight chunks run — `gate_manifest.json → started_utc`,
> `→ finished_utc`, `→ run.requested_chunks`, `→ run.chunk_grid`,
> `→ run.is_full_run`, `→ aggregate.chunks_run`, `→ aggregate.chunks_on_grid`).

**What was deleted and why.** "Projected … runtime was ~19 minutes" is a
projected-runtime statement with no field in the attempt-of-record manifest
recording a projection; "Runtime guard: not triggered" is a runtime-guard-estimate
statement; "no manager decision on cost was required" is an ex-ante cost-decision
statement. All three are outside the packet of the new attempt and are deleted
per ruling §3.1, not relocated.

**Source manifest field for every retained numerical value:**

| Value in new text | Source field | Verified value |
|---|---|---|
| `19 minutes 20 seconds` (elapsed time) | `gate_manifest.json → started_utc`, `→ finished_utc` | `started_utc = 2026-08-06T06:20:50Z`; `finished_utc = 2026-08-06T06:40:10Z`; difference = 19 min 20 s |
| `2026-08-06T06:20:50Z` | `gate_manifest.json → started_utc` | confirmed by direct read of the attempt manifest |
| `2026-08-06T06:40:10Z` | `gate_manifest.json → finished_utc` | confirmed by direct read of the attempt manifest |
| `[0,200,400,600,800,1000,1200,1400]` (requested chunks / full grid) | `gate_manifest.json → run.requested_chunks`, `→ run.chunk_grid` | both fields equal `[0, 200, 400, 600, 800, 1000, 1200, 1400]` |
| `is_full_run: true` | `gate_manifest.json → run.is_full_run` | `true` |
| `eight of eight chunks run` | `gate_manifest.json → aggregate.chunks_run`, `→ aggregate.chunks_on_grid` | `chunks_run = 8`, `chunks_on_grid = 8` |

These are the same started_utc/finished_utc and requested-grid/full-run values
already cited in the unmodified §3 table rows "Started / finished (UTC)" and
"Grid requested"; the new paragraph adds the `aggregate.chunks_run` /
`aggregate.chunks_on_grid` citation for the "eight-chunk result" the ruling
requires and does not introduce any value not already present in the packet.

---

## Change 2 — §4.4 determinism statement, fifth support item (ruling §3.2)

**Location:** report v2, §4.4 "Verdict", the numbered list of what the verdict
rests on, item 5.

**Exact old text (report v2, lines 358–361):**

> 5. **Determinism** — `priced_00000` has now been priced in three independent
>    EUROMOD executions (attempt 2 smoke, attempt 3 full, attempt 4 full; §5 — attempt
>    1 halted before pricing), each returning `0.0` against the same stored chunk,
>    hence `0.0` against each other.

**Exact new text (report v3, §4.4, item 5), verbatim per ruling §3.2:**

> 5. The certification verdict rests solely on the attempt of record and its eight
>    chunk JSONs. Earlier attempts are retained as code-lineage and procedural
>    history only and do not provide numerical support for this verdict.

**What was deleted and why.** The old item cited attempts 2 and 3 (the
pre-T4-fix comparator) as pairwise `0.0`-equality/determinism evidence for the
certified verdict. Per ruling §3.2 this is deleted because the `0.0` fields it
relies on reside in attempts 2 and 3's own `chunk_priced_00000.json`, not in the
attempt-of-record's packet, and those historical attempts ran under the
comparator whose missing finiteness evidence caused the original T4 rejection.

**Source field for the retained numerical value:** "eight chunk JSONs" —
`gate_manifest.json → aggregate.chunks_run` = 8 (the same field cited in Change 1
and in the unmodified §4.3 aggregate table row `chunks_run / chunks_on_grid`).

**§5 status (ruling §3.2, historical-table clause).** Report v2 §5 is headed
"Code lineage across all attempts" and its table (attempt id, `config_sha256`,
`library_sha256`, `runner_sha256`, outcome) contains no parity statistic and makes
no pairwise-equality or numerical-support claim. It already meets the ruling's
"clearly labelled lineage/history" requirement and is carried into report v3
**unchanged**, character-for-character. The §9 provenance table (attempt id →
outcome label) is likewise unchanged and is lineage-only. Neither table, nor any
other location in report v3, cites a prior attempt as numerical support or
pairwise-equality evidence — this was confirmed by re-checking every occurrence of
"attempt 2", "attempt 3", "smoke", "determinism", and "0.0 against" in the full
document text; the deleted item above was the only such occurrence.

---

## Change 3 — supersession and change declaration (ruling §3.3)

**Location:** report v3 only; new section titled "Report v3 status — E2
documentary correction", inserted after the title/metadata block and before the
(unchanged) "§0. Supersession note" that report v2 carries about v1.

**Nature of change:** addition, not a replacement of existing v2 text. No text of
report v2 was removed to make room for it.

**New text added (report v3):** states, per ruling §3.3, that (a) report v3
supersedes report v2; (b) report v2 remains immutable history; (c) only the two
E2 corrections in Changes 1–2 above were made; (d) the attempt of record, packet,
gate code, comparator, `1.0e-6` EUR tolerance, every certified statistic, and the
`PASS` verdict are unchanged from report v2. Full text is reproduced in report v3
in the section named above.

**Ancillary bookkeeping (not a substantive change):** the document title line was
updated from "Report v2 (UNCOMMITTED)" to "Report v3 (UNCOMMITTED)" to match the
new filename; this is the only other textual difference from report v2's title
block, and the "(UNCOMMITTED)" tag, the Mission/Authority/Scope-discipline/
Produced-against lines, and all commit hashes are otherwise identical to report
v2.

---

## Diff summary — confirming no other substantive change

Report v3 was produced by taking the full text of report v2 and applying exactly:

1. Title line: `v2` → `v3` (bookkeeping only, §"Ancillary bookkeeping" above).
2. One inserted section ("Report v3 status — E2 documentary correction") stating
   the ruling §3.3 supersession declaration — an addition, no v2 text removed.
3. One paragraph replacement in §3 (Change 1, runtime statement).
4. One list-item replacement in §4.4 (Change 2, determinism statement).

Everything else — §§0–2, the §3 execution-record table, all of §4.1–4.3, items
1–4 of §4.4, §§5–9, and the explicit scope statement — is reproduced
character-for-character from report v2. In particular, unchanged and verified
identical to report v2:

- the attempt-of-record id and directory;
- every cell of the §3 execution-record table, §4.1 per-chunk table, §4.2
  finiteness table, and §4.3 aggregate table (all values and all citations);
- the `1.0e-6` EUR tolerance, the `ils_dispy` gate column, the `bsa00_s` witness
  column, and `witness_nonfiniteness_gates: false`;
- the `PASS` verdict and items 1–4 of the §4.4 verdict basis;
- the §5 code-lineage table and digest values (`config_sha256`,
  `library_sha256`, `runner_sha256` for all four attempts);
- the §6 non-packet context (fenced **NOT GATE-PACKET EVIDENCE**, unchanged);
- the §7 findings register (T4 and T7 disposition tables);
- the §8 limitations;
- the §9 provenance tables and file-hash listing;
- the explicit scope statement and its final line.

No code file, config file, manifest, chunk JSON, or attempt directory was read,
written, hashed, or otherwise touched to produce report v3 beyond the read-only
citation checks recorded in Changes 1–2 above. No EUROMOD execution occurred. No
gate statistic, tolerance, comparator behavior, or verdict changed. This
correction is confined to ruling §§3.1–3.3.
