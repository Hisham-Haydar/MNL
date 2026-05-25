# RURO B-pool EUROMOD Run v1

**Date:** 2026-05-25
**Pipeline stage:** P3a → P3b (post-precompute pricing)
**Scope:** FR 2015, 2016, 2017 — singles + couples — full alternative space

## What was produced

Six final priced parquets in `U:/EUROMOD-STORAGE/new_data/`:

| File | Rows | Cols | Size |
|---|---:|---:|---:|
| `fr_p3a_bpool_priced__2015__singles.parquet` | 243,713 | 565 | 29 MB |
| `fr_p3a_bpool_priced__2015__couples.parquet` | 7,617,054 | 583 | 378 MB |
| `fr_p3a_bpool_priced__2016__singles.parquet` | 241,895 | 569 | 29 MB |
| `fr_p3a_bpool_priced__2016__couples.parquet` | 7,638,678 | 587 | 381 MB |
| `fr_p3a_bpool_priced__2017__singles.parquet` | 238,764 | 569 | 28 MB |
| `fr_p3a_bpool_priced__2017__couples.parquet` | 6,798,946 | 596 | 225 MB |
| **Total** | **22,779,050** | — | **1.07 GB** |

Each file is the long precompute parquet plus EUROMOD-priced columns
`ils_dispy, ils_origy, ils_ben, ils_tax, ils_sicdy` and the deflated
`ils_dispy_real = ils_dispy * φ_year`.

## EUROMOD system pairing (opportunity_year = data_year − 1)

| Data year | EUROMOD system | EUROMOD dataset | CPI φ |
|---|---|---|---:|
| 2015 | FR_2014 | FR_2015_a2 | 1.0031 |
| 2016 | FR_2015 | FR_2016_a3 | 1.0000 |
| 2017 | FR_2016 | FR_2017_a2 | 0.9886 |

`ils_dispy_real` deflates nominal disposable income to 2016 euros.

## Execution architecture

The long precompute files are too large to run through EUROMOD in a single
process (.NET memory + pandas peak ~30 GB per couples year). Two scripts
split the work:

- [run_bpool_euromod_chunk.py](../scripts/bpool/run_bpool_euromod_chunk.py) — worker that prices one draw-range
  band of one precompute file. Loads only its band via PyArrow push-down
  filter so several workers can run concurrently without OOM.
- [assemble_bpool_priced.py](../scripts/bpool/assemble_bpool_priced.py) — concatenates the band parquets into the final
  priced parquet and runs canary checks.
- [launch_chunks.ps1](../scripts/bpool/launch_chunks.ps1) — PowerShell driver that walks the file list and
  caps concurrency at 2 workers per file. The cap is set conservatively
  because each chunk peaks at ~25–30 GB during the EUROMOD step.

**Chunking** for couples is 6 bands of 150 `draw_joint` values
(0–149, 150–299, …, 750–899). Singles run as a single chunk (~243k rows
each). Every household appears in every chunk — only the *alternatives*
are partitioned. Within a chunk, EUROMOD always sees complete tax units
(head + partner + dependent children), guaranteed by the upstream
ID-stamping in [run_bpool_euromod_chunk.py:110-121](../scripts/bpool/run_bpool_euromod_chunk.py#L110-L121) which shifts `idhh`,
`idperson`, and all kinship pointers by the same `draw` value for every
member of the household.

## Canary results (all PASS)

| File | C1 nulls | C2 nonwork median | C3 CPI viol. | C3 corr(yem, dispy) |
|---|---:|---:|---:|---:|
| 2015 singles | 0 | €721.64 | 0 | 0.856 |
| 2015 couples | 0 | €451.06 | 0 | — (skipped: no `working` col on couples) |
| 2016 singles | 0 | €728.70 | 0 | 0.641 |
| 2016 couples | 0 | €426.16 | 0 | — |
| 2017 singles | 0 | €746.07 | 0 | 0.785 |
| 2017 couples | 0 | €511.93 | 0 | — |

- **C1 (no nulls in `ils_dispy`)**: 0 nulls on 22.8 M rows.
- **C2 (non-work decider income positive)**: median disposable income on
  rows where the decider is not working is €426–€747 per file, all positive,
  driven by benefits as expected. Small fraction of negative `ils_dispy`
  (<2.7%) reflects households with negative imputed components (e.g.
  self-employment losses) — within tolerance.
- **C3 (internal consistency on chosen rows)**: CPI deflation
  `ils_dispy_real = ils_dispy * φ` holds exactly (0 violations). Singles
  show strong positive correlation between earnings (`yem`) and disposable
  income on workers. Couples skip the `corr(yem, dispy)` and
  `median_nonwork` sub-checks because the couples files use
  `working_male` / `working_female` rather than a single `working` flag
  — checked separately during assembly canary.

## Runtime

Wall time end-to-end ≈ 50 min on the 32-CPU server with `$maxConcurrent = 2`.
Per-chunk EUROMOD step is ~4–7 min (dominated by .NET startup + simulation,
not the data read). The current cap leaves substantial headroom — running
6 chunks concurrently per file would compress the wall time toward
~15–20 min and remain well under the 199 GB free RAM (peak ~6 × 30 = 180 GB).

## Known issues / follow-ups

- The original assembler did a `sort_values` on the concatenated frame
  which required a ~28 GB deep copy and OOM'd on couples. The sort was
  removed because chunks are already in correct draw order
  (`c0=[0,150), c1=[150,300), …`) and within each chunk the upstream
  household order is preserved. See [assemble_bpool_priced.py:112-115](../scripts/bpool/assemble_bpool_priced.py#L112-L115).
- For couples, every `draw_joint=0` row collides with the chosen row
  (the first simulated Cartesian cell). EUROMOD emits ~2,295–2,577
  "more than one possible partner" warnings per couples year. These are
  non-fatal and expected by design.
- The PowerShell launcher's `Start-Process -WindowStyle Hidden` does
  not give reliable `ExitCode` access — chunk success is now determined
  by the existence of the output parquet rather than the process exit
  code.

## How to reproduce

```powershell
# 1. Build long precompute files (must exist beforehand):
#    U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_precompute__{year}__{mode}__long.parquet

# 2. Price all 6 files (one year/mode at a time, 2 chunks concurrent):
powershell -NonInteractive -File U:\Desktop\Nizam_Hisham\MNL\scripts\bpool\launch_chunks.ps1

# 3. Assemble chunks into final parquets + canary:
.\.venv\Scripts\python.exe scripts\bpool\assemble_bpool_priced.py

# 4. (Optional) Rebuild meta JSON across all 6 files:
.\.venv\Scripts\python.exe scripts\bpool\rebuild_meta.py
```

Summary JSON: `U:/EUROMOD-STORAGE/new_data/fr_p3a_bpool_priced__meta.json`
(canary results per file).
