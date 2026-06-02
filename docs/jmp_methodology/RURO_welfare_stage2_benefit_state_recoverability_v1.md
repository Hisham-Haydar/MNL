# RURO Welfare — Stage Two, Increment Two-C: benefit-state recoverability inspection

**Date:** 2026-06-02
**Increment:** STAGE TWO, INCREMENT TWO-C only — **READ-ONLY** benefit-state
recoverability inspection. Decides whether exact benefit-state recovery for
redrawn-node pricing is possible through bounded joins/plumbing.
**Status:** inspection complete. **Verdict: NOT FEASIBLE through bounded
joins/plumbing.** Exact redrawn-node benefits require a **separately authorised
per-node EUROMOD pricing path, with full parity gates** — not a simple reuse or
reconstruction of stored benefit state. (This is a node-pricing implementation
decision; it is distinct from a "wholesale rebuild" of the B-pool/data pipeline.)
The parity-relevant benefit `ils_ben` is a **node-dependent EUROMOD-simulated
output** that (a) does not reconstruct from the stored standardized subtotals and
(b) varies with the labour-supply node, so it cannot be reused as frozen invariant
state.

> **No W^3 welfare finding is produced; no measure beyond W^3 is touched.** This
> increment ran **no EUROMOD simulation**, priced **no node**, computed **no
> V_i^dir**, and modified **no source or data**. It read schemas, metadata,
> documentation, and persisted artifacts, and wrote this report + a read-only
> provenance JSON. Not committed automatically.

**Evidence base.** `Data/documentation/euromod_fr_2015_2017_*` (input/output
reference, input variables, output index, standardized income concepts), the
parity report `RURO_welfare_stage2_parity_v1.md` + its JSON/CSV, the build scripts
`run_bpool_euromod_chunk.py` / `assemble_bpool_priced.py`, and the storage-level
parquets. Where local files do not expose a policy internal, it is marked
**NOT ESTABLISHED FROM REPO EVIDENCE**.

---

## 1. Benefit-state inventory (evidence-tiered)

`ils_ben` is the parity-failing component. Its standardized decomposition (from
`euromod_fr_2015_2017_standard_income_concepts.csv`, `IlsDef_fr`, evidence-direct):

```
ils_dispy = ils_origy + ils_ben − ils_sicdy − ils_tax     (identity; holds to 0 in priced data)
ils_ben   = ils_pen + ils_benmt + ils_bennt
ils_pen   = poa00 + pdi00 + psu                            (public pensions; INPUT vars)
ils_benmt = bchyc_s + bsuwd_s + bunmt_s + bchlg_s + bched_s + bchba_s + bsaoa_s
          + bdi_s + bsa00_s + bhotn_s + (tinrf_s | bsawk_s) + bchot_s + bsaot + bhoot + bed   (means-tested)
ils_bennt = bhl + bunct_s + bch00_s + bchcc_s + bchor_s + bmact_s + bpact_s                    (non means-tested)
```

| Tier | Members | Nature | Evidence |
|---|---|---|---|
| **Standardized subtotals** | `ils_ben`, `ils_pen`, `ils_benmt`, `ils_bennt`, `ils_bensim` | income-list aggregates | `standard_income_concepts.csv` |
| **Public-pension inputs** | `poa00`, `pdi00`, `psu` | raw DRD INPUT (not `_s`) | `input_variables.csv`; `ils_pen` formula |
| **Means-tested simulated** | `bchyc_s`, `bsuwd_s`, `bunmt_s`, `bchlg_s`, `bched_s`, `bchba_s`, `bsaoa_s`, `bdi_s`, `bsa00_s`, `bhotn_s`, `tinrf_s`, `bsawk_s`, `bchot_s` | EUROMOD-**simulated** (`*_s`) | income concepts CSV; the `_s` suffix = simulated output |
| **Means-tested inputs** | `bsaot`, `bhoot`, `bed`, `bsa`, `bun`, `bunmy`, `bch00` | raw DRD INPUT | `input_variables.csv` |
| **Non-means-tested simulated** | `bunct_s`, `bch00_s`, `bchcc_s`, `bchor_s`, (`bmact_s`, `bpact_s`) | EUROMOD-**simulated** | income concepts CSV |
| **EUROMOD intermediate state** | `i_bho_*` (housing: rate/rentbase/minrate/p0/pp/r0/rl), `i_bch_*`, `i_bched_*`, `i_bchlg_*`, `i_bdi_*` | simulated INTERMEDIATE (means-test machinery) | priced-parquet columns (49 sim aux + ~tu_* tax-unit head/dep) |
| **Actual policy-function internals** (eligibility thresholds, uprating, taper rates) | — | **NOT ESTABLISHED FROM REPO EVIDENCE** | the output index is wildcard-group config (`b*`/`ils_*`/`t*`), not parameter values; the reference doc states the local files prove configuration, not that any value was generated or any internal is exposed |

**What the documentation proves vs. does not.** It proves the *income-list
composition* of `ils_ben` and the *standard-output configuration* (which groups are
written). It does **not** expose the policy parameter values, taper/threshold logic,
or uprating that EUROMOD applies inside each `*_s` benefit — those live in
`FR.xml`/`IlsDef_fr` policy functions the local index files do not enumerate.

---

## 2. Where each variable exists, grain, and node-dependence

(From direct parquet-schema inspection; full per-file lists in the provenance JSON.)

| variable group | precompute-long | priced-long | engine-ready | grain | node-dependent? |
|---|---|---|---|---|---|
| `ils_dispy/origy/ben/pen/benmt/bennt/sicdy` | **present** | **present** | only `ils_origy`, `ils_pen`, `ils_sicdy` | individual × draw | `ils_ben` **YES** (varies w/ draw); `ils_origy/sicdy` invariant-to-benefit |
| pension inputs `poa00/pdi00/psu` | present | present | absent | individual (annual) | **NO** (invariant input) |
| means-tested `*_s` (`bhotn_s`, `tinrf_s`, `bsa00_s`, …) | present | present | absent | individual × draw | **YES** for housing/PPE/child (vary across draws); most others 0 in this synthetic DRD |
| non-means-tested `*_s` (`bch00_s`, `bunct_s`, …) | present | present | absent | individual × draw | **YES** (`bch00_s` varies) |
| `i_bho_*` / `i_bch_*` intermediates | present | present | absent | individual × draw | **YES** (computed for the stored draw's income) |
| `tu_*` tax-unit head/dep-child | present | present | absent | tax unit | structural (invariant to node) |
| keys | `stacked_hh_uid, draw, idperson, idhh, data_year, year_tag, ruro_decider` | + `idhh_true, idperson_true` | `stacked_hh_uid, draw, idperson, idhh` (couples: `draw_joint, idhh`) | — | — |

**Join keys back to a node:** `(stacked_hh_uid, draw)` for singles and
`(stacked_hh_uid, draw_joint)` for couples uniquely identify an alternative;
`idhh_true`/`idperson_true` (priced-long only) recover the un-stamped identity. The
parity smoke CSV (`stage2_parity_smoke_rows_diag.csv`) carries
`stacked_hh_uid, draw, idperson, stored/repriced ils_dispy`, the per-component abs
diffs, and stored `ils_ben`.

**Decisive node-dependence evidence (2016 singles, the 4 parity-failing HH).** The
simulated benefits that are nonzero for these households **vary across draws**:
`bhotn_s` (housing allowance AL), `tinrf_s` (PPE refund), `bch00_s` (universal child
benefit), `bched_s` (education grant ARS), `bchot_s` (other family). They vary
because each is means-tested against earned income, which the draw `(w,h)` changes.
Two of the four HH have all-zero simulated benefits yet **still fail parity** — their
stored `ils_ben` comes from a benefit value not equal to the stored subtotal columns
(see §below).

---

## 3. Recoverability classification (A/B/C/D/E)

| variable / component | class | reason (evidence) |
|---|---|---|
| `ils_pen` and inputs `poa00/pdi00/psu` | **A — invariant + recoverable** | raw DRD INPUT, invariant to the node; reusable for a redrawn node. |
| `ils_origy`, `ils_sicdy`, `ils_earns` | **A/B** | reproduce to **machine zero** in the parity test; recomputable from node `(w,h)` + invariant state (already shown faithful in Two-B). |
| means-tested simulated `bhotn_s`, `tinrf_s`/`bsawk_s`, `bsa00_s`, `bdi_s`, `bunmt_s`, … | **C — simulated output only** (becomes **D** for redrawn nodes) | `*_s` EUROMOD-simulated, **node-dependent** (means-tested on earned income). Stored values are valid only for the **stored** draw; reusing them for a **redrawn** node is invalid unless that component is explicitly frozen by policy decision. For a redrawn node their correct value is **NOT recoverable without re-running the benefit policy function** (= EUROMOD) ⇒ D. |
| non-means-tested simulated `bch00_s`, `bunct_s`, `bchcc_s`, … | **C → D** | same: `_s` simulated, node-dependent (`bch00_s` varies across draws). |
| `i_bho_*` / `i_bch_*` intermediate state | **C → D** | stored, but computed for the **stored** draw's income; itself node-dependent, so not invariant state reusable for a redrawn node. |
| `tu_*` tax-unit structure | **A** | invariant household roster/assessment-unit structure. |
| **the headline `ils_ben`** (what parity compares) | **D — not recoverable through bounded joins/plumbing** (requires a per-node EUROMOD pricing path) | (i) it does **NOT** reconstruct from the stored standardized subtotals — `\|ils_ben − (ils_pen+ils_benmt+ils_bennt)\|` is nonzero on **259/808** rows, up to **±724** (the subtotals are out of sync with the headline benefit in the priced file); and (ii) it is node-dependent. So it can be neither frozen (varies with node) nor summed from stored parts (subtotals disagree). |
| policy thresholds / taper / uprating internals | **E — not established** | not exposed by the local index files. |

**Why D, not B.** B (node-dependent + recoverable) would require recomputing the
benefit from redrawn node variables **plus stored invariant state, without EUROMOD**.
The means-tested benefits depend on policy functions (eligibility, taper, household
means base) that the repo does **not** expose as reconstructible formulas (tier E),
and the stored intermediates are themselves node-tied. So recomputation requires a
per-node EUROMOD benefit re-run — i.e. it falls in tier D (not recoverable through a
bounded join/plumbing, tier B). Tier D here means "a separately authorised per-node
EUROMOD pricing path is required," which is distinct from a wholesale rebuild of the
B-pool/data pipeline.

---

## 4. The year-specific benefit switch (`tinrf_s` 2015 / `bsawk_s` 2016-2017)

**Documentation (`IlsDef_fr`):** `tinrf_s` (PPE refund) is `+` in 2015 and `n/a` in
2016/2017; `bsawk_s` (activity allowance PA) is `n/a` in 2015 and `+` in 2016/2017,
inside `ils_benmt`/`ils_bensim`.

**Repo evidence — the priced files price `data_year` with a LAGGED policy system.**
`run_bpool_euromod_chunk._SYSTEM_PAIRING` maps:
`2015 → FR_2014`, `2016 → FR_2015`, `2017 → FR_2016` (policy system_code). So the
stored `*_s` columns reflect the **pricing policy system**, not the calendar year:

| data_year | policy system | `tinrf_s` present | `bsawk_s` present |
|---|---|---|---|
| 2015 | FR_2014 | **yes** | no |
| 2016 | FR_2015 | **yes** | no |
| 2017 | FR_2016 | no | **yes** |

So `bsawk_s` appears **only** in the 2017 priced files (priced with FR_2016 policy);
2015 and 2016 carry `tinrf_s`. The input variable `bsawk` (no `_s`) is present in all
years.

**Classification of the switch component:** both `tinrf_s` and `bsawk_s` are
**`*_s` SIMULATED outputs (tier C → D for redrawn nodes)** — EUROMOD-computed,
node-dependent, inside means-tested benefits. They are **not** recoverable inputs and
**cannot be reproduced for a redrawn node without re-running the policy** (the local
files do not expose the PPE/PA computation). For redrawn-node pricing they fall under
the same D verdict as the rest of `ils_benmt`. (Whether the data-year→policy lag is
intended is a build-design question, recorded here as evidence, not adjudicated.)

---

## 5. Decision question — verdict

**NOT FEASIBLE through bounded joins/plumbing.** Exact redrawn-node benefits require
a **separately authorised per-node EUROMOD pricing path, with full parity gates** —
not a simple reuse/recovery of stored benefit state, and distinct from a "wholesale
rebuild" of the B-pool/data pipeline.

- The parity-relevant `ils_ben` is a **node-dependent simulated benefit** (§2): it
  varies with `(w,h)` because the means tests bind on earned income.
- It **cannot be frozen** as invariant state (it changes with the node), and it
  **cannot be reconstructed from stored parts** (the standardized subtotals disagree
  with the headline by up to ±724 on 259/808 rows — §3).
- Recomputing it for a redrawn node requires the EUROMOD benefit policy functions,
  whose internals are **not exposed** by the repo (tier E) — so there is no bounded
  join/plumbing that yields the correct redrawn-node benefit; a per-node EUROMOD
  pricing path is required.
- This is consistent with Two-B: income and contributions reprice to machine zero;
  only benefits fail, and they fail because they are simulated node-dependent state
  that the bounded reprice cannot reproduce.

This is **not** PARTIALLY FEASIBLE in any sense that would let production W^3 proceed:
the only "partial" route is to **freeze** the benefit component at the stored value,
which is invalid for a redrawn node (the node has different earned income), so it
would bias welfare exactly on the benefit-recipient households the whole exercise is
meant to value. It is **not UNRESOLVED**: the evidence is sufficient to classify —
the blocker is node-dependent simulated benefits + unexposed policy internals, not
missing diagnostic information.

---

## 6. Minimal later-increment design (only if a per-node EUROMOD pricing path is authorised)

Because the verdict is "bounded joins/plumbing are not feasible," there is **no
bounded-join shortcut** to specify. The honest minimal design is a **separately
authorised per-node EUROMOD pricing path** (a node-pricing implementation, distinct
from a wholesale rebuild of the B-pool/data pipeline) — to be opened only under
separate authorisation:

- **Join (invariant state, tier A):** for each redrawn node, attach the household's
  invariant inputs by `(stacked_hh_uid)` / `idhh_true`: demographics (`dag, dgn, dms,
  deh`), roster/kinship (`idpartner, idfather, idmother`, `tu_*` structure), pensions
  (`poa00, pdi00, psu`), housing context (`xhc*`, `amrtn`), and non-labour income
  inputs (`yiy, ypr, ypp`).
- **Overwrite/recompute (node-dependent, tier B):** the labour-supply node variables
  `(w,h,occ,emp)` → `lhw, yivwg, yem, yem_hour` (the build's overwrite set), and the
  derived earnings the benefit means tests read.
- **Re-run through EUROMOD (tier C/D):** every `*_s` benefit and tax
  (`ils_benmt`/`ils_bennt`/`ils_pen` simulated parts, `ils_tax`) — i.e. price the
  redrawn node's full record through the build's `EuromodRunner` with the build's
  `_SYSTEM_PAIRING`/`_RAW_SCHEMA`. This is exactly the build's pricing path applied to
  redrawn nodes.
- **Freeze by design (only if a policy memo authorises it):** none recommended — any
  frozen benefit component biases benefit-recipient welfare.
- **The parity test a later implementation MUST pass first** (before any redrawn-node
  pricing is trusted): re-run the **Two-B reprice parity on EXISTING nodes through the
  new per-node EUROMOD path** and require `ils_dispy` (and, for couples, the
  household-joint summed disposable income) to reproduce the stored value to
  machine tolerance on **all** 2015/2016/2017 × singles/couples cells — including the
  benefit-recipient rows that fail today. Only an all-cells PASS unblocks pricing.

This design does not reduce the cost below a per-node EUROMOD run; it states precisely
what such a run must join, overwrite, and re-simulate, and the gate it must clear.

---

## Files

- **Report:** this file.
- **Read-only provenance:** `outputs/welfare/stage1_w3/stage2_benefit_state_inventory.json`
  (per-file benefit-column inventory, year-switch presence + policy-system mapping,
  node-dependence of the failing-HH simulated benefits, and the `ils_ben`-vs-subtotals
  reconstruction gap).

## Explicit scope statement

No W^3 welfare finding is produced and no measure beyond W^3 is touched. No EUROMOD
simulation was run, no node was priced, no V_i^dir was computed, no 2×/4× growth was
run, and no source or data was modified. Verdict: **exact benefit-state recovery for
redrawn-node pricing is NOT FEASIBLE through bounded joins/plumbing; exact pricing
requires a separately authorised per-node EUROMOD pricing path with full parity
gates** (a node-pricing implementation, not a wholesale rebuild of the B-pool/data
pipeline). Production redrawn-node pricing and production V_i^dir remain BLOCKED
pending separate authorisation of that path and an all-cells parity PASS.
