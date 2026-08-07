# FR P2a — JMP-M08 Reprice-Parity Production-Path Review v1

**Review role:** independent production-path review; the single bounded M08 review.  
**Repository:** `C:\Users\hisham\Repo\MNL` at MNL HEAD `520441a653f04196bf1e92e3658a478b4feb3718`; nested `dclaborsupply-monorepo` HEAD `27756a06ea189339aa82915ed2124628afed20eb`.  
**Reviewed verdict:** `PARITY_PASS_FULL`.  
**Overall verdict:** **REJECT — the recorded numerical result may be genuine, but `PARITY_PASS_FULL` is not earned by this gate/evidence packet.** T1, T2, T3, T5, and T6 are accepted. T4 is rejected because the comparison fails open on non-finite repriced values. T7 is rejected because the report does not meet its manifest/chunk trace and attribution-only requirements. These are certification findings; this review does not assert that a finite stored-versus-repriced value actually differs.

No EUROMOD execution was performed. Static execution of the real comparison function was sufficient to falsify T4, and the permitted one-chunk rerun could not establish absence of masked values over all eight historical chunks. All other reviewer proofs were read-only, in-memory commands. This memo is the only file created by the review.

## Verdict register

| Threat | Verdict | Classification on rejection |
|---|---|---|
| T1 Artifact binding | **ACCEPT** | — |
| T2 Subject integrity / no fixture replacement | **ACCEPT** | — |
| T3 Geometry-equivalence claim | **ACCEPT** | — |
| T4 Comparison soundness | **REJECT** | **Implementation defect that blocks scientific certification; not affirmative evidence of a scientific mismatch.** |
| T5 Shim inertness | **ACCEPT** | — |
| T6 Transaction integrity | **ACCEPT** | — |
| T7 Claim-to-evidence | **REJECT** | **Disclosure/evidence-integrity defect, including a scientific causal overclaim.** |

## T1 — ARTIFACT BINDING: ACCEPT

The executed gate config points to the committed production config and the exact `frozen_inputs.pricing_cache` node, without copying any SHA-256 values (`scripts/welfare/configs/welfare_m08_p2a_parity_v1.yaml:26-33`). The committed source declares the eight-chunk grid, 225,836 rows, 1,555 households, ten columns, and all eight pins (`scripts/p2a/configs/p2a_regionlive_rebuild_v1.yaml:89-104`). Git showed that config and all eight cache parquets are tracked and that the config is byte-clean against the index.

`verify_pricing_cache_pins` loads the selected node from that source, iterates every declared pin, hashes the corresponding parquet, and raises `HP-PIN` immediately on absence or mismatch (`scripts/welfare/m08_p2a_parity.py:67-99`). It then checks declared total rows and unique households (`scripts/welfare/m08_p2a_parity.py:100-127`). The runner completes this binding before reconstruction or any call to `reprice_chunk` (`scripts/welfare/run_m08_p2a_parity_gate.py:137-145`, `146-187`). Thus the comparisons in the reviewed execution cannot precede full pin verification.

The full manifest records the committed source/path, all eight expected/observed digest equalities, and the declared/observed shape equality (`outputs/p2a_singles2016/region_live_v1/welfare_m08_v1/attempts/20260805T180301Z_638408_ca402c3a3d9a412ea0d76914c07697f7_parity_PARITY_PASS_FULL/gate_manifest.json:13-127`). Independent hashing reproduced all eight declared SHA-256 values. Independent parquet reads reproduced 225,836 rows, 1,555 households, the eight declared offsets, the exact ten-column order, and zero duplicate or null join keys.

The cache directory remains named in the gate config rather than taken from the production node (`scripts/welfare/configs/welfare_m08_p2a_parity_v1.yaml:30-32`; `scripts/welfare/m08_p2a_parity.py:76-91`). This does not falsify the reviewed binding: every compared file had to be byte-identical to the committed pin, and the executed config digest is recorded. No duplicated or mutable pin value exists in the gate config.

## T2 — SUBJECT INTEGRITY / NO FIXTURE-REPLACEMENT: ACCEPT

The reconstructed namespace executes notebook code cells 2 through 34 only, with pricing/export guards forced off and the notebook development output redirected under staging (`scripts/welfare/m08_p2a_parity.py:189-259`). The production notebook reads the raw FR input (`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb:116-117`), constructs `draws_p2a` and its true identifiers (`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb:986-987`), creates the full-entitlement baseline and production earnings policy/runner (`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb:1188-1205`), and does not reach the cache-loading/pricing loop in cell 35 during reconstruction.

The repriced alternative frame is a copy of reconstructed `draws_p2a`, with only provenance aliases added (`scripts/welfare/m08_p2a_parity.py:323-328`). `reprice_chunk` selects the reconstructed alternatives and baseline by the chunk household set and passes them to the reconstructed `runner_full.price` with the production country/system/dataset and `draw` key (`scripts/welfare/m08_p2a_parity.py:331-356`). The underlying production runner rebuilds each isolated household from baseline, applies the earnings policy only to the alternative's decider, and sends the resulting frame to the real connector (`dclaborsupply-monorepo/packages/dclaborsupply_app/src/dclaborsupply_app/euromod/runner.py:145-166`, `226-242`, `286-309`).

The stored parquet is read into the separate `stored` frame (`scripts/welfare/m08_p2a_parity.py:345-347`) and is used only after the pricing result exists, for key/order checks and the comparison merge (`scripts/welfare/m08_p2a_parity.py:358-403`). Neither `stored` nor any column derived from it is an argument to `runner_full.price`. The frozen geometry parquet is likewise read only by the post-reconstruction geometry verifier (`scripts/welfare/m08_p2a_parity.py:262-317`), not as a source of repriced values. This is genuine connector/EUROMOD execution, not fixture replacement or comparison of the artifact to itself.

## T3 — GEOMETRY-EQUIVALENCE CLAIM: ACCEPT

The production notebook defines `single_idhh`, the full baseline, the production runner, `hh_all = sorted(single_idhh)`, and `CHUNK = 200` (`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb:1188-1205`). Its production loop copies `draws_p2a`, sets the source/decider identifiers, iterates the sorted household list in 200-household slices, and makes one `runner_full.price` call with `alt_key_cols=['draw']` (`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb:1233-1253`). The gate reproduces the same aliases and one-call-per-offset selection (`scripts/welfare/m08_p2a_parity.py:323-355`; `scripts/welfare/run_m08_p2a_parity_gate.py:168-201`). The production runner creates one isolated synthetic household for every `(source_idhh, draw)` group and restores every baseline member before applying only that group's staged hours/wage (`dclaborsupply-monorepo/packages/dclaborsupply_app/src/dclaborsupply_app/euromod/runner.py:145-180`, `196-264`). No cache value participates in that staging.

The full manifest records a rebuilt 157,055-row/1,555-household geometry and zero difference on all eight compared pricing-relevant columns (`.../20260805T180301Z_638408_ca402c3a3d9a412ea0d76914c07697f7_parity_PARITY_PASS_FULL/gate_manifest.json:178-205`). It records requested grid equal to the complete committed grid (`gate_manifest.json:207-228`). Each full chunk records 200 households and 20,200 alternatives, the last 155 and 15,655, and every chunk records `row_order_identical_to_stored: true` (`gate_manifest.json:230-629`). Independent cache inspection confirmed that each chunk's household set is exactly `sorted(all 1,555 source_idhh)[offset:offset+200]`.

The code records row-order identity as evidence rather than making it a separate halt (`scripts/welfare/m08_p2a_parity.py:372-376`). For the reviewed run this does not falsify the geometry claim: the recorded value is true in all eight chunks, while duplicate and row-set mismatches are hard stops (`scripts/welfare/m08_p2a_parity.py:361-370`). On a parity run, the alternatives are the already staged nodes; no counterfactual replacement occurs. The claimed Option-B degeneration onto the production batch is therefore supported for this run only.

## T4 — COMPARISON SOUNDNESS: REJECT

### Evidence that does work

The join keys are exactly `(source_idhh, draw, source_idperson)` in the gate config (`scripts/welfare/configs/welfare_m08_p2a_parity_v1.yaml:61-76`). The library rejects duplicate keys, asserts full key-set equality, performs a one-to-one inner merge, and checks that its length equals the stored frame (`scripts/welfare/m08_p2a_parity.py:361-389`). There is no row filter, clipping operation, or deduplication. Independent cache inspection found 225,836 rows, zero duplicate keys, zero null key cells, and finite stored `ils_dispy`/`bsa00_s` on every row. The full manifest records eight chunks, 225,836 rows, a `1e-6` tolerance, zero rows above tolerance, and no failing chunk (`...PARITY_PASS_FULL/gate_manifest.json:632-645`).

For ordinary finite differences, absolute difference and capture operate as described: `d = abs(repriced - stored)`, the gate mask is `d > tol`, and captured rows include the keys, stored/repriced gate and witness values, component values, and accumulator witnesses (`scripts/welfare/m08_p2a_parity.py:391-414`). A read-only in-memory call to the real `reprice_chunk` with one finite `2e-6` gate difference returned `FAIL`, `n_rows_above_tol = 1`, and a one-row capture with all advertised fields. The runner persists per-chunk and aggregate failing CSVs when that frame is nonempty (`scripts/welfare/run_m08_p2a_parity_gate.py:185-201`, `232-234`).

### Minimal falsifying observation

Both sides are converted with `pd.to_numeric(..., errors='coerce')`; `np.nanmax`/`np.nanmedian` summarize the resulting difference; and `d > tol` builds the only gate mask (`scripts/welfare/m08_p2a_parity.py:393-403`). No `isfinite`/null assertion occurs before the mask. Consequently a nonnumeric or `NaN` repriced value becomes `NaN`, for which `NaN > 1e-6` is false. It is neither counted nor captured.

A read-only in-memory execution of the actual function with a finite stored value `10.0` and a repriced `NaN` on the same unique key returned:

```text
status=PASS
n_rows_above_tol=0
max_abs_diff=nan
failing_rows_is_none=True
```

This directly falsifies the required rule “PASS iff zero rows above tolerance with no NaN masking.” Although the pinned stored side is finite, neither the manifest nor chunk JSON records a repriced non-finite count, so the historical eight-chunk packet cannot exclude this condition. The chunk status then becomes `PASS` whenever the masked count is zero and there are no hard errors (`scripts/welfare/m08_p2a_parity.py:416-434`), and the runner's overall verdict simply requires every such chunk status to be `PASS` (`scripts/welfare/run_m08_p2a_parity_gate.py:203-228`). Therefore the all-row equality claim is not certified by the recorded aggregates.

**Classification:** implementation-only as an observed defect, with a scientific-certification consequence. It does not demonstrate a substantive finite-value mismatch; it demonstrates that the gate/evidence cannot prove their absence across all 225,836 repriced rows.

## T5 — SHIM INERTNESS: ACCEPT

The post-halt change seeds `display` and `get_ipython` lambdas returning `None` in the reconstruction namespace (`scripts/welfare/m08_p2a_parity.py:211-219`). Within reconstructed cells 2–34 the notebook has exactly two `display(...)` calls, both expression statements whose return values are unused (`dclaborsupply-monorepo/notebooks/fr_singles_pipeline_v2.ipynb:599`, `602`); there is no `get_ipython` call in that span. An AST read confirmed neither call is assigned, tested, returned, or used as a branch condition. The only surrounding condition is whether there are unknown-worker rows; it does not depend on `display` (`fr_singles_pipeline_v2.ipynb:592-602`).

The nested repository's worktree hash-object for the notebook is `1a06c99b61b6dd5d5707bf71ccc6e8e876063f02`, exactly equal to its index blob, and `git diff`/status for the file are empty. The production notebook is byte-untouched. The shims are presentation-only in the executed span.

## T6 — TRANSACTION INTEGRITY: ACCEPT

`GateTransaction` creates an exclusive lock, then the attempts/staging directories and a unique staging directory (`scripts/welfare/run_m08_p2a_parity_gate.py:45-73`). `finish` uses `os.replace(staging, attempts/destination)` and `release` removes the lock (`scripts/welfare/run_m08_p2a_parity_gate.py:75-84`); the runner invokes finish and release in `finally` (`scripts/welfare/run_m08_p2a_parity_gate.py:262-265`). There is no `complete/` path in the implementation. Read-only filesystem checks found `attempts/` and an empty `.staging/`, no lock, and no `complete/`.

All three manifests have the same config digest `029d5e...` and runner digest `1eea3c...`. The stopped attempt records library `bde41a...` and the `cell-21` undefined-`display` halt (`.../20260805T175912Z_104548_c376a2bfd6b44912b60146ecc9a04f58_parity_STOPPED_HP_RECON/gate_manifest.json:8-10`, `163-166`). Smoke and full record library `d79d05...`; smoke requests offset 0 and compares 29,492 rows (`.../20260805T175932Z_733948_1ce508a6e0504acb94c901ef3751a011_parity_PARITY_PASS_SMOKE/gate_manifest.json:8-10`, `208-221`, `277-290`). Full requests the complete grid and compares the declared 225,836 rows (`...PARITY_PASS_FULL/gate_manifest.json:8-10`, `207-228`, `632-647`). Current file hashes independently reproduce the config, runner, and post-shim library digests.

The library difference is exactly the shim change. In memory, removing the four explanatory shim-comment lines at current `scripts/welfare/m08_p2a_parity.py:211-214` and replacing the namespace block at lines 215–219 with the former single line

```python
ns: Dict[str, Any] = {"__name__": "__m08_parity_reconstruction__"}
```

reproduces the stopped attempt's SHA-256 exactly: `bde41a0718093855ec310e1725633df5532d50c44def056a2b041389823d82c7`. No other byte difference is needed.

The stopped packet has zero chunk JSONs, smoke has one, and full has eight. Every chunk JSON is value-identical to its corresponding manifest `chunk_results` entry. Full per-chunk rows are 29,492; 29,593; 27,775; 30,704; 28,583; 28,078; 28,482; and 23,129, summing to 225,836; every recorded row-order flag is true and every recorded hard-error list is empty (`...PARITY_PASS_FULL/gate_manifest.json:230-629`). The three attempt names, attempt IDs, halt/run modes, grids, and counts are internally consistent.

## T7 — CLAIM-TO-EVIDENCE: REJECT

The central per-chunk and aggregate table values do trace correctly to the full manifest/chunk JSONs: row counts, household/alternative counts, elapsed seconds, row-order flags, zero differences, hard errors, grid/full-run status, total EUROMOD time, and start/finish timestamps are represented in `...PARITY_PASS_FULL/gate_manifest.json:230-647`. The stated limitation is present and accurate: the report says the result licenses stored-node reproducibility only, does not license joint-batch redrawing, and retains target-only geometry for counterfactual pricing (`docs/France_case/P2a/FR_P2a_m08_parity_gate_report_v1.md:319-326`, `355-360`).

The threat nevertheless fails on three minimal observations:

1. **Numerical claims without manifest/chunk trace.** The report claims 182 of 200 chunk-0 households (91.0%) and 23.7% of rows are RSA-positive (`FR_P2a_m08_parity_gate_report_v1.md:194-197`, repeated at `292-295`). The chunk JSON contains only batch sizes, timing/errors, available columns, and difference summaries (`...PARITY_PASS_FULL/chunk_priced_00000.json:1-50`); neither it nor the manifest contains RSA-positive household or row counts. Independent reading of the pinned cache does reproduce 182/200 and 6,993/29,492 = 23.7115%, so this is a traceability failure rather than a numerical contradiction. It still falsifies “every numerical claim traces to a manifest or chunk JSON.” Historical residual counts/amounts and build times at report lines 306–317 likewise do not originate in this gate packet.
2. **Code-lineage statement is internally inaccurate.** The report presents library `d79d05...` as the gate identity “recorded in every attempt manifest” (`FR_P2a_m08_parity_gate_report_v1.md:95-98`), while the stopped manifest records `bde41a...` (`...STOPPED_HP_RECON/gate_manifest.json:8-10`). The later provenance correctly describes the shim change (`FR_P2a_m08_parity_gate_report_v1.md:377-384`), but the earlier all-attempt identity statement remains false. The report also calls notebook cells 2–34 “the loop that wrote the cache” (`FR_P2a_m08_parity_gate_report_v1.md:111-113`); the actual cache loop is cell 35, visible at notebook lines 1233–1253. The gate reconstructs cells 2–34 and separately reimplements that loop's pricing call.
3. **The FR.xml timing explanation is framed as causation, not attribution.** The report says three facts “explain the difference,” that another task “traced the ... residual precisely” to system drift, and that the cause “is now identified as build vintage against a changed EUROMOD system” (`FR_P2a_m08_parity_gate_report_v1.md:310-315`, `328-333`). Those are proven-cause formulations. The current manifest establishes only the current XML/DataConfig sizes and mtimes (`...PARITY_PASS_FULL/gate_manifest.json:149-159`); timing supports attribution but does not by itself prove that the intervening XML content change caused the absent P3a residual. This violates the frozen attribution-only requirement.

There is a further disclosure overstatement tied to T4: the report calls the result “bit-for-bit” equality (`FR_P2a_m08_parity_gate_report_v1.md:269-276`). The implementation computes float64 numerical absolute differences after coercion; it performs no bitwise comparison (`scripts/welfare/m08_p2a_parity.py:393-403`), and its non-finite masking prevents the packet from establishing equality on every repriced row. The manifest supports recorded finite summary values of `0.0`; it does not support the stronger bit-for-bit claim.

**Classification:** disclosure/evidence-integrity rejection with a scientific-attribution overclaim. The reproducibility-versus-joint-batching limitation itself is accepted.

## Overall certification decision

**REJECT `PARITY_PASS_FULL` as an earned certification verdict.** Artifact authenticity, no-fixture production-path execution, parity geometry, shim inertness, and attempt transaction/lineage are supported. The decisive comparison can return `PASS` while a joined repriced gate value is `NaN`, and the historical packet contains no evidence field capable of excluding that condition across all rows. Separately, the gate report fails the required numerical trace and attribution-only disclosure standard. This conclusion is limited to the seven frozen threats and makes no finding on code style, general security, or any other stage.
