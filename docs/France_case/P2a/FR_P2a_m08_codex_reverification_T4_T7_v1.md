# FR P2a — JMP-M08 T4/T7 Narrow Re-verification v1

**Role:** narrow re-verification of the prior review's two REJECT findings only.  
**Prior review:** `docs/France_case/P2a/FR_P2a_m08_codex_production_path_review_v1.md`.  
**Attempt of record:** `20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL`.  
**Attempt directory:** `outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL/`.  
**Repository:** MNL HEAD `520441a653f04196bf1e92e3658a478b4feb3718`; nested `dclaborsupply-monorepo` HEAD `27756a06ea189339aa82915ed2124628afed20eb`.  
**Overall verdict: REJECT.** R1, R2, and R4 are accepted. R3 is rejected because report v2 retains two numerical claims in sections it declares new-attempt-only even though those claims do not trace to the new attempt's manifest or chunk JSONs. This is the same T7 numerical claim-to-evidence category rejected before, not a new threat category. The tightened comparator is sound against the prior T4 falsifier, and the new attempt's numerical `PASS` is earned.

T1, T2, T3, T5, and T6 remain **ACCEPTED** and were not reopened. No EUROMOD execution was performed. Code, configs, data, and existing outputs were read-only. The actual `reprice_chunk` function was exercised with a file-free, in-memory stub and a temporary monkeypatch of `pd.read_parquet`; no probe file was created. This memo is the only repository file created.

For compact file:line citations below, bare `FR_P2a_*.md` names resolve under `docs/France_case/P2a/`, and bare `gate_manifest.json` / `chunk_priced_*.json` names resolve under the exact attempt directory stated above.

## Verdict register

| Item | Verdict | Finding |
|---|---|---|
| R1 — T4 cure | **ACCEPT** | Either-side gate non-finiteness now becomes `+inf`, necessarily fails and is captured; per-side accounting, non-masking summaries, row-count assertions, and closed chunk/aggregate verdict rules are present. The original `NaN` falsifier now returns `FAIL`. |
| R2 — T4 witness delta | **ACCEPT** | Witness non-finiteness is evidence-additive only. It enlarges the capture mask, not the gate mask; `witness_nonfiniteness_gates` is persisted `false`. |
| R3 — T7 cure | **REJECT** | The central packet figures, non-packet fences, lineage table, notebook correction, attribution caveat, and float64 wording are correct. However, report v2's packet-only §§3–4 still contain an unpersisted projected-runtime claim and a three-execution/`0.0` determinism claim that depends on prior attempts, not the new packet. |
| R4 — earned verdict | **ACCEPT** | Independent recomputation from the eight new chunk JSONs gives 225,836/225,836 rows, max gate difference 0.0, zero above tolerance, zero gate non-finites, zero hard errors, and 8/8 passing chunks. |

## R1 — T4 comparison soundness: ACCEPT

The prior T4 rejection was specific: coercion could create `NaN`; `NaN > tol` was false; `np.nanmax`/`np.nanmedian` hid the value; neither packet nor verdict recorded or excluded it; and the runner inherited the open chunk status (`FR_P2a_m08_codex_production_path_review_v1.md:48-71`). Every element is cured.

### Code proof

1. `_numeric_side` separately processes one stored or repriced series and persists `n_raw_null`, `n_noncoercible`, `n_nan`, `n_inf`, and `n_nonfinite` (`scripts/welfare/m08_p2a_parity.py:351-371`). The comparison calls it separately on both sides of every gate and witness column (`scripts/welfare/m08_p2a_parity.py:457-460`) and stores both side dictionaries in that column's summary (`scripts/welfare/m08_p2a_parity.py:468-480`). Thus the evidence is per chunk, per column, and per side.
2. Either-side non-finiteness forms `bad = s_bad | r_bad` and forces `d = np.inf`; it cannot leave a masked `NaN` (`scripts/welfare/m08_p2a_parity.py:457-466`). The summaries use ordinary `np.max` and `np.median`, not the former NaN-skipping functions; the finite-only maximum is separately labelled (`scripts/welfare/m08_p2a_parity.py:467-472`). The other `np.nanmax` in this library is in the already accepted T3 frozen-geometry check, not this T4 comparator (`scripts/welfare/m08_p2a_parity.py:317-333`).
3. Only gate-column `d > tol` enters `fail_mask`; gate non-finiteness also enters its explicit mask (`scripts/welfare/m08_p2a_parity.py:482-489`). Because a non-finite gate row has `d = inf`, it necessarily enters `fail_mask`. Capture is `fail_mask | any_nonfinite_mask`, and persisted rows carry `fails_gate`, `nonfinite_gate_column`, and per-column `nonfinite_<col>` flags (`scripts/welfare/m08_p2a_parity.py:491-506`).
4. `n_rows_compared` is asserted equal to `stored_rows` before any statistic and persisted in the chunk result (`scripts/welfare/m08_p2a_parity.py:437-451`, `:508-511`, `:529-541`). The runner independently sums both quantities and halts on disagreement (`scripts/welfare/run_m08_p2a_parity_gate.py:217-225`).
5. A chunk passes only when `n_fail == 0`, `n_gate_nonfinite == 0`, and `hard_errors` is empty (`scripts/welfare/m08_p2a_parity.py:412`, `:551-553`). The runner recomputes aggregate above-tolerance and gate-finiteness totals (`scripts/welfare/run_m08_p2a_parity_gate.py:217-250`) and requires every chunk status plus zero aggregate tolerance and non-finite counts (`scripts/welfare/run_m08_p2a_parity_gate.py:266-270`). The runner does not separately sum hard-error list lengths, but `all(r["status"] == "PASS")` makes absence of hard errors a necessary aggregate condition because the chunk formula cannot produce `PASS` with a hard error. There is no aggregate `PASS` pathway around that condition.

The new packet exercises the persisted schema: `chunk_priced_00000.json:3-22` records compared/stored equality and chunk finiteness rollups; `:58-108` records both side taxonomies for `ils_dispy` and `bsa00_s`; and `:110-111` records zero gate failures and `PASS`. The same fields occur in all eight chunk JSONs.

### Reproduction of the prior falsifier

A file-free in-memory call to the real fixed `reprice_chunk`, using the same unique key with stored `ils_dispy = 10.0` and repriced `ils_dispy = NaN`, returned:

```text
status=FAIL
n_rows_above_tol=1
max_abs_diff=inf
gate non-finite stored/repriced=0/1
n_rows_nonfinite_gate=1
n_rows_captured=1
fails_gate=True
nonfinite_gate_column=True
nonfinite_ils_dispy=True
```

Supplemental calls gave the same closed result for a stored-side `NaN` and a repriced `+inf`: each returned `FAIL`, one row above tolerance, `max_abs_diff=inf`, and a flagged captured row. The original falsifying observation is therefore inverted on the fixed library.

## R2 — non-finite witness rows: ACCEPT

The delta is evidence-additive only.

- `fail_mask` is updated only inside `if c in gate_cols` (`scripts/welfare/m08_p2a_parity.py:482-485`). A witness non-finite contributes to `any_nonfinite_mask`, which is used only to enlarge `capture_mask` (`scripts/welfare/m08_p2a_parity.py:482`, `:491-494`).
- The capture distinguishes gate failures from witness-only evidence with `fails_gate` and `nonfinite_gate_column`, while retaining the per-column flag (`scripts/welfare/m08_p2a_parity.py:497-506`). Per-chunk and combined failing-row CSV persistence is at `scripts/welfare/run_m08_p2a_parity_gate.py:192-215`, `:276-278`.
- `witness_nonfiniteness_gates: False` is persisted per chunk and aggregate (`scripts/welfare/m08_p2a_parity.py:508-527`; `scripts/welfare/run_m08_p2a_parity_gate.py:251-253`). Neither the chunk status nor aggregate verdict reads witness counts (`scripts/welfare/m08_p2a_parity.py:551-553`; `scripts/welfare/run_m08_p2a_parity_gate.py:266-270`).

An in-memory witness-only probe—finite and equal `ils_dispy`, repriced `bsa00_s = NaN`—returned `PASS`, zero gate rows above tolerance, one captured row, `fails_gate=False`, `nonfinite_gate_column=False`, `nonfinite_bsa00_s=True`, and repriced witness `n_nonfinite=1`. Conversely, the gate-`NaN` probe above failed and was captured. Witness capture neither contaminates the gate mask nor creates a route by which a gate failure can be masked.

## R3 — T7 claim-to-evidence: REJECT

Most individual corrections are accurate, but the numerical-trace finding is not completely cured.

### Correct new-packet claims — independent spot checks

All paths in this table are under the new attempt directory
`outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/20260806T062050Z_339096_ffa19dbeb2a340babf918b3acdaa9f74_parity_PARITY_PASS_FULL/`.

| Report-v2 claim | Report evidence | New-packet evidence | Independent result |
|---|---|---|---|
| Aggregate rows are 225,836 and compared equals stored | `FR_P2a_m08_parity_gate_report_v2.md:295-297`, `:325-333` | `gate_manifest.json:1133-1135`; per-chunk counts in the eight JSONs at `:3`, `:31` | The eight counts sum to 225,836 on both measures; every pair is equal. |
| Gate maximum absolute difference is 0.0 | report `:300`, `:328-329` | `gate_manifest.json:1137-1139`; each chunk JSON `:59-67` | Recomputed maximum is 0.0. |
| Gate rows above `1e-6` are zero | report `:299-301`, `:328-329` | `gate_manifest.json:1137-1139`; each chunk JSON `:60-64` | Recomputed sum is zero. |
| Gate finiteness totals are stored/repriced/either-side `0/0/0` | report `:302-306`, `:325-331` | `gate_manifest.json:1140-1144`; each chunk JSON `:14-20`, with side taxonomies at `:68-105` | All five taxonomy counts are zero for both columns, both sides, all chunks. |
| Witness finiteness totals are stored/repriced `0/0` | report `:307-311` | `gate_manifest.json:1145-1153`; each chunk JSON `:17-22`, `:93-105` | Recomputed totals are `0/0`; the non-gating flag is false in all chunks and aggregate. |
| EUROMOD hard errors are zero | report `:244-257`, `:332` | every chunk JSON `:34`; `gate_manifest.json:1148` has no failing chunk | All eight lists are empty. |
| Total EUROMOD seconds are 1138.1 | report `:223`, `:313` | `gate_manifest.json:1149`; each chunk JSON `:33-34` | `148.7+146.7+145.2+147.8+144.6+146.5+145.7+112.9 = 1138.1`. |

The standalone chunk JSONs are value-identical to the manifest's eight `chunk_results` entries (`gate_manifest.json:231-1127`). Other checked report values also match: the attempt timestamps (`gate_manifest.json:6`, `:1157`), artifact rows/households (`:42-45`), reconstruction (`:163-205`), and requested full grid (`:208-229`).

### Other required T7 corrections that are accurate

1. **Non-packet fencing and sources.** Section 6 is explicitly headed **NOT GATE-PACKET EVIDENCE** and says none of its background supports the verdict (`FR_P2a_m08_parity_gate_report_v2.md:423-428`). Its RSA subsection identifies the pinned `priced_00000.parquet` as the source and labels the figures non-gate output (`:430-448`). Independent parquet inspection reproduced 182/200 RSA-positive households and 6,993/29,492 rows = 23.7115%. Its historical-residual table supplies a source for every figure and marks packet membership (`:450-462`): the cited audit records 184.6123 EUR, 3,460 rows, and 372 households at `docs/jmp_methodology/RURO_welfare_F6PRICEB0_geometry_audit_v1.md:15`, `:142-148`; 185.5400 EUR for `ils_ben` at `:143`; and the chunk creation time at `:58`, `:159`. The diagnosis memo records 3,460/169,276 = 2.04% and EUR 185.54 at `docs/France_case/P2a/FR_P2a_m08_parity_diagnosis_memo_v1.md:217`, `:235`. The P2a-cache source is explicitly filesystem mtimes of `fr_singles_pricing_p2a/priced_*.parquet` (report `:459`), independently observed from `2026-07-12T10:46:32Z` through `11:03:10Z`.
2. **Four-attempt digest lineage.** The table and full values at report `:365-404` exactly match fields `config_sha256`, `runner_sha256`, and `library_sha256` at lines `8-10` of each of the four attempt manifests: attempt 1 has library `bde41a0718093855ec310e1725633df5532d50c44def056a2b041389823d82c7`; attempts 2 and 3 have `d79d05ae326276506bc950449af737da35042cac4d16e733963c1ae1b9856547`; attempt 4 has `441b416d164827eab6b0822b2f6dfbda9d3de639aac61ddbdc0f144ac3181046`. Attempts 1–3 record runner `1eea3cc7583811170426c12e2a44058d9145dac52eceb202c7f10ecda31423d8`; attempt 4 records `69571a671492ec37151ca322003a4c551c6b218996949ea47e11b74a1a0b6467`; all four record config `029d5ee618576c9a91cc2374500e3d632912c52d637a1b4268c1db4796979e81`. Independent SHA-256 hashing of the current config/library/runner reproduced the attempt-4 values byte-for-byte.
3. **Cell 34/cell 35 correction.** Report `:406-419` is accurate. Notebook cell 34 defines the earnings policy, `baseline_full`, `runner_full`, `hh_all`, and `CHUNK = 200` (`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb:1178-1205`). Cell 35 copies `draws_p2a`, adds identifiers, slices `hh_all` by `CHUNK`, and calls `runner_full.price(..., alt_key_cols=['draw'])` (`:1233-1253`). The report correctly distinguishes reconstructing cells 2–34 from separately reimplementing cell 35's pricing call.
4. **FR.xml attribution and explicit non-causation.** Report `:464-494` withdraws the old causal language, identifies the current manifest's limited size/mtime evidence, calls the chronology co-occurrence, says causation is not established, lists the missing controlled comparison, and characterises system drift only as a leading candidate. The stated current file sizes/mtimes match `gate_manifest.json:150-160`.
5. **No bit-for-bit overclaim.** Report `:335-341` replaces that phrase with float64 numerical comparison at absolute tolerance `1.0e-6`, proven finiteness on both sides, and observed maximum 0.0; it expressly says no bitwise comparison occurred. The disposition is repeated at report `:546`.

### Decisive residual T7 finding

Report v2 promises that §§3–4 contain gate results only, with every value traceable to a named field of the new attempt (`FR_P2a_m08_parity_gate_report_v2.md:54-66`, repeated at `:216-217`). Two claims break that promise:

1. Section 3 says, **“Projected and realised runtime was ~19 minutes”** (`FR_P2a_m08_parity_gate_report_v2.md:230-232`). The packet supports realised duration—start `2026-08-06T06:20:50Z`, finish `06:40:10Z`, and 1138.1 EUROMOD seconds (`gate_manifest.json:6`, `:1149`, `:1157`)—but no manifest or chunk field records a projection, runtime-guard estimate, or manager cost decision. The projected half of the numerical claim has no new-packet trace.
2. Section 4 says the verdict rests on **three** independent executions—attempts 2, 3, and 4—“each returning `0.0` against the same stored chunk, hence `0.0` against each other” (`FR_P2a_m08_parity_gate_report_v2.md:343`, `:358-361`). Attempt 4's manifest/chunks cannot establish results of attempts 2 and 3. The cited §5 contains their digest lineage and outcome labels, not their numerical comparison fields (`:365-404`). The relevant `0.0` fields actually reside in the two prior-context files at `outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/20260805T175932Z_733948_1ce508a6e0504acb94c901ef3751a011_parity_PARITY_PASS_SMOKE/chunk_priced_00000.json:36-49` and `outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/20260805T180301Z_638408_ca402c3a3d9a412ea0d76914c07697f7_parity_PARITY_PASS_FULL/chunk_priced_00000.json:36-49`, not in the new attempt. Moreover, those historical files are from the comparator whose missing finiteness evidence caused the prior T4 rejection, so their summaries cannot certify the stronger pairwise-output conclusion.

Both observations are instances of the prior T7 finding **“numerical claims without manifest/chunk trace”** (`FR_P2a_m08_codex_production_path_review_v1.md:99-105`). They do not introduce a new threat category. Because R3 requires every numerical claim to trace to the new attempt, R3 is **REJECT** even though the required central spot checks and all other named T7 corrections pass.

## R4 — new-attempt verdict recomputation: ACCEPT

The eight standalone chunk JSONs give:

| Chunk | `n_rows_compared` | `stored_rows` |
|---|---:|---:|
| `priced_00000` | 29,492 | 29,492 |
| `priced_00200` | 29,593 | 29,593 |
| `priced_00400` | 27,775 | 27,775 |
| `priced_00600` | 30,704 | 30,704 |
| `priced_00800` | 28,583 | 28,583 |
| `priced_01000` | 28,078 | 28,078 |
| `priced_01200` | 28,482 | 28,482 |
| `priced_01400` | 23,129 | 23,129 |
| **Total** | **225,836** | **225,836** |

For each named file, the compared/stored values are at lines `3` and `31`; lines `14-16` give zero stored, repriced, and either-side gate non-finites; line `34` gives an empty hard-error list; line `60` gives gate maximum `0.0`; line `63` gives zero gate rows above tolerance; and line `111` gives `status: PASS`. Independent aggregation therefore yields:

```text
chunks on full grid                 8 / 8
rows compared / stored             225836 / 225836
max abs diff, ils_dispy             0.0
rows above 1e-6                     0
gate non-finite stored/repriced     0 / 0
rows with gate non-finite           0
EUROMOD hard errors                 0
passing chunks                      8 / 8
independent verdict                 PASS
```

These values match the persisted aggregate at `gate_manifest.json:1129-1154`, including row equality (`:1133-1135`), tolerance/max/count (`:1137-1139`), finiteness (`:1140-1147`), no failing chunks (`:1148`), and verdict `PASS` (`:1154`). The gate's certified verdict is earned under the tightened standard on the new attempt's own evidence.

## Overall decision

**REJECT the conversion as a complete T4/T7 certification packet.** T4 is cured, the witness delta is evidence-additive, and the new attempt earns its numerical `PASS`. The sole blocking category is the still-incomplete T7 numerical claim-to-evidence cure in report v2. This is a disclosure/evidence-integrity rejection only; it is not evidence of a finite scientific mismatch and does not reopen any accepted threat.
