# JMP NC Pilot — `draw_joint` Re-Pointing Audit v1

*France RURO multi-year extension | v1 | 2026-05-22*

Document class: read-only audit. No code modified, no data modified,
no EUROMOD run, no GSUR merge, no precompute, no estimation, no
welfare, no SA2. M1-clean 2016 remains the active baseline. Corrected
pooled P3a track unaffected.

---

## 1. Audit verdict

**Strategy A (pilot-only compatibility alias in the EUROMOD-input
exporter) is sufficient for Stage 5 but NOT sufficient on its own for
Stages 7–9.** Stage 5 (EUROMOD) operates on the *long-format individual
draws file*, not on the wide product parquet, so the `draw_joint` change
does not reach the EUROMOD wrapper directly — the wrapper still wants
individual `(idperson, draw)` keys on a per-partner basis. The pilot
should therefore export EUROMOD inputs from the *marginal* per-partner
draw frames (which already use the legacy scalar `draw`), not from the
wide product parquet. The wide product parquet is consumed only
downstream of EUROMOD (precompute + estimation + post-estimation), and
*those* sites need re-pointing — but they are not Stage 5 sites.

A separate finding raises the bar: **`estimation_engine.py:380`
assumes the chosen alternative is `V[group_starts[g]]`** (first row in
each group). On the current pilot parquet, the chosen row
(`draw_joint == 0`) is at position 0 of its (idhh) group in only
175 of 2,577 couples (median position ≈465). This is a hard
precondition for any estimation run on the pilot parquet and must be
fixed (either by re-sorting the parquet so `draw_joint == 0` is first
in each group, or by re-pointing the engine to read from a `chosen_idx`
array per group). It is **not** a Stage-5 blocker — but it IS a hard
blocker for any post-EUROMOD estimation. The build report already
named this as a later-slice item; this audit pinpoints it as a hard
prerequisite.

Recommended Stage-5 approach: **B'** — a constrained version of
strategy A. EUROMOD inputs are exported from the long-format marginal
draws (legacy `draw` semantics preserved), the wide product parquet is
not consumed by EUROMOD at all, and the post-EUROMOD merge writes
disposable income onto the product parquet by joining
`(idperson_male, draw_male)` and `(idperson_female, draw_female)`. The
chosen-position fix and the precompute / estimation / post-estimation
re-pointing then become a *separate* later slice prior to Stage 8/9 —
not a precondition for EUROMOD itself.

---

## 2. Authorization scope

This audit is read-only. Authorized by §26 of the build report
(`Results/NC_pilot/JMP_NC_pilot_stage1_4_build_report_v1.md`) which names the
re-pointing audit as the immediate next task. Outside scope: any code
or data modification, EUROMOD execution, GSUR re-merge, precompute,
estimation, welfare, SA2, canonical promotion, M1-clean displacement.

---

## 3. Files inspected

| File | Method |
|---|---|
| `Results/NC_pilot/JMP_NC_pilot_stage1_4_build_report_v1.md` | Full read (prior turn) |
| `docs/France_case/NC_pilot/execution_logs/JMP_NC_pilot_stage1_4_scope_amendment_v1.md` | Full read (prior turn) |
| `docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md` | Full read (prior turn) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product.parquet` | Schema + bounded column reads (`idhh`, `draw_male`, `draw_female`, `draw_joint`, `is_chosen_*`, `year_tag`) |
| `Data/pilot/nc_2016_couples/fr_pilot_nc_2016_couples_product__mnlmeta.json` | Full read |
| `scripts/pilot/build_pilot_couples_product.py` | Full read |
| `scripts/pilot/pilot_wage_draw.py` | Full read |
| `scripts/pilot/config/pilot_mincer_coefficients_v1.json` | Full read |
| `scripts/enhanced/enh_RURO_draws.py` | Targeted Grep + ranged Read around line 370 and surrounding context |
| `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | Ranged Read of `_normalize_singles()` (1220–1269) and `_normalize_couples_wide()` (1272–1310) |
| `scripts/enhanced/enh_RURO_euromod.py` | Ranged Read of decider/non-decider section (470–530) |
| `scripts/enhanced/estimation_engine.py` | Ranged Read around line 380 (V_obs extraction) |
| `scripts/enhanced/estimation_utils.py` | Ranged Read of group-builder for singles (730–810) and couples (1108–1185); + Grep of `is_chosen` / `group_starts` |
| `scripts/enhanced/RURO_post_estimation_styled.py` | Grep of `is_chosen` and `chosen_col` usage (≈20 sites at lines 3148, 3292, 3456, 3500, 3593, 3628, 4753, 4927, 4989, 5250, 5318, 5507, 5539, 6120, 6154) |
| `scripts/enhanced/quick_verify.py` | Grep + context at line 176 |

---

## 4. Pilot draw convention

Confirmed from the pilot parquet itself (`pyarrow` schema + bounded
column read; no full materialization beyond join-key columns):

| Property | Value |
|---|---|
| Scalar `draw` column present? | **No** (verified `'draw' in schema.names == False`) |
| `draw_male` present, range 0..29 | Yes |
| `draw_female` present, range 0..29 | Yes |
| `draw_joint` present, range 0..899 | Yes |
| `draw_joint == 30·draw_male + draw_female` holds for all 2,319,300 rows | **Yes** (boolean check confirmed) |
| `is_chosen_male` (marginal, =1 when `draw_male==0`) present | Yes |
| `is_chosen_female` (marginal, =1 when `draw_female==0`) present | Yes |
| `is_chosen_joint` (=1 when `draw_male==0 AND draw_female==0`) present | Yes |
| Legacy `is_chosen` or `chosen` column present | **No** |
| Rows with `draw_joint == 0` (joint chosen) | 2,577 — one per couple |
| `is_chosen_male == 1 == is_chosen_female == 1 == is_chosen_joint == 1` on chosen row | True for all 2,577 |
| `is_chosen_male == 1` on **non**-chosen rows | 74,733 rows (where `draw_male==0` but `draw_female>0`) — these are NOT the joint-chosen row |
| `is_chosen_female == 1` on **non**-chosen rows | 74,733 rows (where `draw_female==0` but `draw_male>0`) — these are NOT the joint-chosen row |

**Critical asymmetry:** in the pilot parquet, `is_chosen_male` and
`is_chosen_female` carry **marginal** chosen semantics (one of the two
draws equals 0), not joint. Only `is_chosen_joint` (and equivalently
`draw_joint == 0`) marks the actual chosen alternative for the
likelihood. Any downstream code that ports legacy `is_chosen == 1`
semantics by reading `is_chosen_male` or `is_chosen_female` would
produce **30 chosen rows per couple instead of 1**, which is wrong by
construction.

---

## 5. Legacy draw-dependent sites found

Exhaustive list across `scripts/enhanced/` and `scripts/maintenance/`
of sites that consume the legacy single-integer `draw` column or the
legacy `is_chosen` column:

| # | File | Line | Pattern | Context |
|---|---|---|---|---|
| 1 | `scripts/enhanced/enh_RURO_draws.py` | 370 | `is_draw0 = df["draw"] == 0` | `_validate_baseline_compliance()` — verifies that draw=0 rows of deciders match observed baseline labor inputs. Operates on the long-format per-person draws file, BEFORE couples reshape. |
| 2 | `scripts/enhanced/enh_RURO_euromod.py` | 490 | `person_max_draw = draws_df.groupby(id_col)["draw"].max()` | Fallback decider/non-decider inference: a person is a decider if at least one of their draws has `draw > 0`. Operates on long-format draws file. |
| 3 | `scripts/enhanced/enh_RURO_euromod.py` | 492 | `nondecider_ids = set(person_max_draw[person_max_draw == 0].index)` | Same — non-deciders have only `draw == 0`. Long format. |
| 4 | `scripts/enhanced/enh_RURO_euromod.py` | 517 | `nd_copy["draw"] = d` | Replicates non-deciders across all `draws_df["draw"]` values 0..N. Long format. |
| 5 | `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | 1234 | `chosen_mask = df["draw"] == 0` | Fallback in `_normalize_singles()` (singles wide) — runs *only* if `"is_chosen"` is absent. Primary path uses `is_chosen == 1`. |
| 6 | `scripts/enhanced/enh_RURO_prep_mnl_basic.py` | 1286 | `chosen_mask = df["draw"] == 0` | Fallback in `_normalize_couples_wide()` — same fallback structure. Primary path uses `is_chosen == 1`. |
| 7 | `scripts/enhanced/estimation_engine.py` | 380 | comment: "Extract V for observed choices (draw==0, which is first in each group)" + `V_obs = np.array([V[start] for start in data.group_starts])` | **Implicit chosen-row assumption** — does NOT read `draw` or `is_chosen` columns; assumes the chosen row is at `group_starts[g]` (first row of each contiguous (idhh, year_tag) group). |
| 8 | `scripts/enhanced/quick_verify.py` | 176 | `df[df["draw"] == 0]` | Verification helper; computes baseline household sizes from the chosen alternative. Standalone script, used post-build for sanity checks. |
| 9–13 | `scripts/enhanced/estimation_utils.py` | 780, 1156 | `chosen_col = "is_chosen" if "is_chosen" in df.columns else ("chosen" if "chosen" in df.columns else None)` | Singles and couples group-builders — primary chosen-row identification. If both `is_chosen` and `chosen` are absent, falls through to hours-match or max-prior. The pilot parquet has neither. |
| 14+ | `scripts/enhanced/RURO_post_estimation_styled.py` | 3148, 3292, 3456, 3500, 3593, 3628, 4753, 4927, 4989, 5250, 5318, 5507, 5539, 6120, 6154 | `chosen_col = 'is_chosen' if 'is_chosen' in df.columns else 'chosen'` | Post-estimation diagnostics — ≈15 separate sites all using the same `is_chosen`-or-`chosen` priority chain. The pilot parquet has neither column. |

**Group-by-stage classification:**

- **Stage 5 (EUROMOD wrapper):** sites 1–4 (long-format draws file).
- **Stage 7 (MNL prep / split-stem):** sites 5–6 (wide-format singles
  and couples — secondary path only).
- **Stage 7 / Stage 8 (precompute):** sites 9–13.
- **Stage 9 (estimation):** site 7 — and this is the *implicit* one
  that does not appear in any grep for `draw == 0` directly.
- **Post-estimation:** site 14+ (≈15 sites).
- **Standalone verification:** site 8.

---

## 6. EUROMOD wrapper dependency

`scripts/enhanced/enh_RURO_euromod.py` consumes the **long-format
per-person draws file** (`draws_df`), not the wide product parquet.
The relevant section (lines 470–530) does two things:

1. **Decider inference.** If an explicit `is_decider` column is present
   on the draws file (preferred), use it. Otherwise (fallback), infer
   that anyone with `max(draw) > 0` is a decider and anyone whose only
   draw is `draw == 0` is a non-decider. The `person_max_draw == 0`
   filter at line 492 is the fallback's non-decider mask.

2. **Replication of non-deciders across draws.** Lines 510–524: for
   each draw value `d` in `all_draws`, copy the non-decider baseline
   rows and set `draw = d`. This ensures EUROMOD can compute
   household-level outcomes when one partner is a non-decider.

**Implication for the pilot.** EUROMOD never sees `draw_joint`. It
sees per-partner draws keyed by `(idperson, draw)`. For the pilot:

- The male side of the couples product (30 draws) is logically a
  per-male long-format file: `(idperson_male, draw_male)` with
  `draw_male ∈ {0..29}`.
- The female side is `(idperson_female, draw_female)` with
  `draw_female ∈ {0..29}`.
- These are exactly the inputs EUROMOD already understands — they look
  like the existing long-format draws file, just with 30 draws per
  person instead of 100.

The wrapper's `person_max_draw == 0` and `draw == d` logic both work
unchanged on these inputs, *provided* the EUROMOD input exporter feeds
the long-format marginal frames (not the wide product parquet). The
EUROMOD wrapper does **not** need to be re-pointed for the pilot.

What does need to be built (next slice, not now): a pilot EUROMOD
input exporter that constructs the two long-format per-partner draws
frames from the pilot product parquet (or, more efficiently, from the
intermediate marginal draws produced upstream of the reshape).

**There is one subtle risk** to flag: the `_compute_id_multiplier()`
call at line 481 of `enh_RURO_euromod.py` uses `max_draw` to construct
EUROMOD-internal person IDs that are unique across draws. With 30
draws per person instead of 100, the multiplier shrinks, and any
downstream code that depends on the original multiplier (e.g.
post-EUROMOD identifier round-tripping) needs verification. This is a
configuration concern, not a `draw_joint` concern, but it is in the
same "Stage-5 surface" envelope.

---

## 7. MNL-prep dependency

Sites 5 and 6 in `_normalize_singles()` and `_normalize_couples_wide()`
(lines 1230–1236 and 1282–1288) are **fallback** chosen-row
identification: they consult `df["draw"] == 0` only when neither
`is_chosen` nor `chosen` is present.

The pilot parquet has neither, so these fallbacks would fire — except
that the *primary* path (the `is_chosen` branch) is the one
`estimation_utils.py` actually uses for the precompute. In `_normalize_*`
the fallback path would silently treat **0 rows** as chosen (because
there is no `draw` column either), reaching the `raise KeyError` at
lines 1236 and 1288. This is a clean failure mode: the MNL-prep
normalizer would *halt* on the pilot parquet rather than silently
produce wrong scaling. That is the desirable behaviour.

**Implication:** the pilot parquet cannot be passed through the
production `_normalize_singles` / `_normalize_couples_wide` functions
unchanged — they will raise. The pilot's choice-set scaffold has not
yet been normalized (consumption / leisure columns from EUROMOD are
absent), so normalization is not yet applicable in any case. Both
points argue for the same conclusion: the pilot parquet is a
pre-normalisation, pre-EUROMOD scaffold and the production
normalization functions should not be invoked on it.

---

## 8. Precompute dependency

The precompute builders (`precompute_data_singles` at
`estimation_utils.py:558` and `precompute_data_couples` at
`estimation_utils.py:902`) consume the *normalised, estimation-ready*
wide parquet (post-EUROMOD, post-GSUR, post-normalization). They use
two pieces of structure that interact with the pilot's draw
convention:

1. **Group boundaries** (`group_starts`, `group_ends`) derived from
   contiguous `(idhh, year_tag)` runs (singles) or `(idhh, year_tag)`
   runs (couples). This is *structurally compatible* with the pilot
   parquet (sorted by `idhh`; year_tag constant for 2016) — but the
   group size would be 900, not 100.

2. **Chosen-row identification** at lines 780 and 1156:
   ```python
   chosen_col = "is_chosen" if "is_chosen" in df.columns else (
                "chosen" if "chosen" in df.columns else None)
   ```
   Neither `is_chosen` nor `chosen` exists on the pilot parquet, so
   `chosen_col` is `None`. The code then falls through to:

   - `hours_observed` match (singles) / `hours_male_observed` and
     `hours_female_observed` match (couples) — these are *not* columns
     on the pilot parquet either; and
   - max-prior fallback (`np.argmax(group_priors)`) — chooses the
     prior maximiser per group, which is **not** the observed couple
     alternative.

   Without re-pointing, the precompute would silently identify the
   wrong row as chosen for all 2,577 couples, with no error. **This is
   the most dangerous downstream failure mode** the audit identifies.

**Required for Stage 7 (precompute):** either add a synthetic
`is_chosen = is_chosen_joint` column to the pilot parquet at the
EUROMOD/GSUR-merge slice, OR re-point the precompute to read
`is_chosen_joint` directly when available.

---

## 9. Estimation dependency

Site 7 — `estimation_engine.py:380`. The comment says it all:

> # Extract V for observed choices (draw==0, which is first in each group)
> `V_obs = np.array([V[start] for start in data.group_starts])`

The engine assumes the **chosen alternative is the first row of each
group** (i.e. at `group_starts[g]`). It does **not** read any column;
the assumption is baked into the row order coming out of the
precompute.

**Empirical finding on the pilot parquet** (read-only check; in-memory
groupby on `idhh`; no parquet modification):

| Property | Value |
|---|---|
| Couples groups (one per idhh, 2016 only) | 2,577 |
| Median within-group position of `draw_joint == 0` | **465** |
| Min / max position | 0 / 899 |
| Couples with `draw_joint == 0` at position 0 in their group | **175** (6.8%) |

The cross-join in `_build_product` emits rows ordered by
`(draw_male, draw_female)` within each `idhh`, and `idhh` is sorted in
the source parquet — but within each `idhh` the chosen row sits at
position `30·k + m` where `(k, m)` is the original within-source
ordering of the male and female `draw==0` rows. It is essentially
*never* at position 0 of the cross-join block.

**Implication.** Even if precompute correctly identifies
`is_chosen_joint == 1`, the *engine* will silently read
`V[group_starts[g]]` and treat the wrong alternative as the observed
choice. The log-likelihood will be wrong; gradients will be wrong;
identification will collapse. This is a hard precondition for any
estimation run on the pilot parquet.

Two fixes are possible (audit only — do not implement):

A. **Re-sort the pilot parquet** so `draw_joint == 0` is at position
   0 of each (idhh) group. Within-group order otherwise free. This
   keeps the engine unchanged.

B. **Re-point the engine** to read a `chosen_idx` array per group
   (carried in the precompute output), instead of assuming position 0.
   More invasive; touches a hot path in the LSE / gradient computation.

Strategy A is lower-impact for the pilot and aligned with the build
report's "pilot-only modules" principle.

---

## 10. Post-estimation dependency

`RURO_post_estimation_styled.py` has ≈15 sites (lines 3148, 3292,
3456, 3500, 3593, 3628, 4753, 4927, 4989, 5250, 5318, 5507, 5539,
6120, 6154) all using the same priority chain:

```python
chosen_col = 'is_chosen' if 'is_chosen' in df.columns else 'chosen'
```

None falls through to `draw == 0`. On the pilot parquet (neither
column present) the `chosen_col` would receive `'chosen'` (the
fallback string), and a `df[chosen_col]` access would raise
`KeyError('chosen')`. This is also a clean fail (raise), not a silent
miscalculation.

These sites only matter at Stage 9 (post-estimation diagnostics), and
they share the same fix as §8: the pilot parquet should carry a
synthetic `is_chosen` column (defined as `is_chosen_joint`) when it
reaches post-EUROMOD slices, so the rest of the production code path
sees the conventional column it expects without re-pointing.

---

## 11. Verification dependency

`scripts/enhanced/quick_verify.py:176` consumes
`df[df["draw"] == 0]` for baseline-household-size verification. This
is a standalone post-build sanity script (not part of the production
estimation pipeline). It would `KeyError("draw")` on the pilot
parquet. No action required for Stage 5; if `quick_verify.py` is ever
run on a pilot parquet, it would need a pilot variant. Low priority.

---

## 12. Which sites must be changed before Stage 5

**None of the sites in §5 are blockers for Stage 5 (EUROMOD).**

The EUROMOD wrapper (sites 1–4) operates on long-format per-person
draws (`(idperson, draw)`), not on the wide product parquet. The pilot
must export EUROMOD inputs from per-partner marginal draws, but those
inputs use the legacy scalar `draw` semantics (draw ∈ {0..29}). No
code change in `enh_RURO_euromod.py` or `enh_RURO_draws.py` is
required to run EUROMOD on the pilot.

What IS needed before Stage 5 (and is itself out of audit scope):

- A pilot EUROMOD **input exporter** that produces the two long-format
  per-partner draws frames (male and female), drawing from the
  regenerated marginals with W1 wages applied — *not* from the wide
  product parquet, which is a downstream artefact.
- Or equivalently: re-use the production
  `_compute_id_multiplier()` path with 30 draws and verify the
  EUROMOD-internal person-ID arithmetic is consistent.

Neither requires a `draw_joint` re-pointing in production code.

---

## 13. Which sites can wait until after EUROMOD

All sites except the EUROMOD wrapper can wait, but they split into
two tiers:

**Tier 1 — must fix before precompute (Stage 8) or estimation
(Stage 9):**

- Site 7 — `estimation_engine.py:380` chosen-row position. **Strategy
  A (re-sort parquet so `draw_joint==0` is first in each group) is
  the recommended pilot-only fix.**
- Sites 9–13 — `estimation_utils.py` chosen-column identification.
  Recommended pilot-only fix: add a synthetic `is_chosen` column to
  the post-EUROMOD pilot parquet defined as `is_chosen_joint`. No
  code change required if the alias is added at the data layer.
- Sites 5–6 — `enh_RURO_prep_mnl_basic.py` normalization. These
  functions are not called on the pilot parquet directly in the
  current plan, but if the pilot routes through a normalisation step,
  the same `is_chosen` alias resolves it.

**Tier 2 — must fix before post-estimation (Stage 9 diagnostics):**

- Sites 14+ — `RURO_post_estimation_styled.py` ≈15 sites. All resolved
  by the same `is_chosen` alias.

**Tier 3 — convenience / verification only:**

- Site 8 — `quick_verify.py`. Not on the critical path.
- Site 1 — `enh_RURO_draws.py:370` — only relevant when regenerating
  marginals; the pilot has already regenerated marginals via
  `scripts/pilot/pilot_wage_draw.py` and is_decider columns flow
  through the long-format draws file, so this baseline-compliance
  check works on long-format inputs as before.

---

## 14. Recommended pilot-only compatibility strategy

**Recommended: hybrid A + alias.** Concretely:

1. **EUROMOD input slice** (next authorized slice — Stage 5 surface).
   Export per-partner long-format draws frames (male + female), each
   with the legacy scalar `draw` column. EUROMOD wrapper consumes
   these *unchanged*. No `draw_joint` enters EUROMOD.

2. **Post-EUROMOD merge slice.** After EUROMOD produces disposable
   incomes per `(idperson, draw)` pair, join those incomes onto the
   wide pilot product parquet using two separate merges:
   - `(idperson_male, draw_male)` → `ils_dispy_male`
   - `(idperson_female, draw_female)` → `ils_dispy_female`
   Add a synthetic column `is_chosen = is_chosen_joint` at this step.
   Re-sort the wide parquet so `draw_joint == 0` is the first row of
   each (idhh, year_tag) group. **These two data-layer adjustments
   resolve the position-0 invariant (site 7) and the `chosen_col`
   priority chain (sites 9–13, 14+) with zero code change in
   production scripts.**

3. **GSUR re-merge** consumes the post-EUROMOD wide parquet (still no
   `draw` column needed; GSUR centering uses the choice-set
   structure, not the draw index).

4. **Precompute and estimation** run with the production code
   unchanged on the now-aliased pilot parquet.

5. **Post-estimation** runs with the production code unchanged.

This strategy minimises production-code touch points and keeps all
re-pointing on the data side. Production scripts continue to look for
the legacy `is_chosen` column they already expect; the pilot synthesises
that column from the joint-chosen flag.

The recommendation is a constrained version of audit-option A (pilot
compatibility alias) combined with the *parquet re-sort* operation
that the position-0 engine assumption requires.

---

## 15. Whether to add a pilot legacy-draw alias

**Do not add a scalar `draw = draw_joint` alias to the pilot parquet.**
Rationale:

- The only production consumers of a scalar `draw` column on the
  *wide* parquet are the two fallback paths in
  `enh_RURO_prep_mnl_basic.py` (sites 5–6), both of which assume
  `draw == 0` means the chosen alternative. With 900 alternatives
  indexed 0..899, this assumption is correct (`draw_joint == 0` IS
  the chosen alternative) — but only if the alias **equals
  `draw_joint`**, not the male or female partner draw. If a future
  consumer reads the alias and expects values in 0..99, they will see
  values in 0..899 and have no warning.
- Aliasing `draw` to `draw_joint` papers over the fact that the draw
  semantics have changed. The build report's intention (recorded in
  the metadata sidecar's `downstream_draw_repointing_surface` note)
  is to make the change visible to downstream consumers. Silent
  aliasing defeats that.

What *is* recommended (per §14): alias `is_chosen` to
`is_chosen_joint`, because `is_chosen` carries unambiguous semantics
(0/1, one chosen per group) that the joint flag honours exactly.

---

## 16. Whether to re-point directly to `draw_joint`

**Direct re-pointing of production code to `draw_joint` is not
recommended for the pilot.** Two reasons:

1. The build report and the scope amendment both require pilot-only
   code paths; in-place edits to `scripts/enhanced/` violate that
   principle and risk HP1.
2. Production scripts continue to serve the corrected pooled P3a
   track on the legacy diagonal parquet. Editing them to understand
   `draw_joint` (even via conditional branches) introduces a code
   path that diverges from the verified production behaviour and
   needs its own validation — for *zero* benefit if Strategy A + data
   aliases already resolves the consumption sites.

If at some later slice the NC pilot graduates into the production
specification (a separate, distant decision), the re-pointing can be
made permanent in production code at that point — driven by a spec
contract that authorises modification of the production scripts.

---

## 17. Halt conditions for Stage 5

Halt the next-slice (Stage 5) build if any of the following are
violated:

- **HE1** Production `scripts/enhanced/` files are modified in place.
  EUROMOD wrapper consumes long-format inputs unchanged; pilot code
  exports those inputs from pilot modules only.
- **HE2** EUROMOD inputs are exported from the wide product parquet
  rather than from the per-partner marginal draws. (Symptom: EUROMOD
  is presented with `draw_joint` semantics it does not understand.)
- **HE3** The wide product parquet receives EUROMOD outputs without
  the post-EUROMOD merge re-sorting `draw_joint == 0` to position 0
  in each (idhh, year_tag) group **and** synthesising an
  `is_chosen = is_chosen_joint` column. This is the precondition for
  Stage 7/8/9 to run on the production code unchanged.
- **HE4** EUROMOD throughput or output-schema assumptions change in
  any way that affects downstream income routing. Surface the change
  and stop — do not silently absorb it.
- **HE5** Any singles parquet is touched in Stage 5. Pilot scope is
  couples-only; singles disposable income is already computed in
  production.
- **HE6** Any attempt to run welfare, SA2, promotion, or M1-clean
  displacement at Stage 5.
- **HE7** EUROMOD `_compute_id_multiplier` overflows or collides for
  the 30-draws-per-person pilot configuration.

These are additions to the existing HP1–HP9 from the spec contract
and the slice amendment. They are not a replacement.

---

## 18. What was not executed

- No code modified.
- No data modified.
- No EUROMOD run. (Explicitly: **no EUROMOD was run.**)
- No GSUR merge run.
- No precompute run.
- No estimation run.
- No welfare computed.
- No SA2 issued.
- No promotion.
- No production file touched (read-only access only).
- No singles parquet touched.

Two transient temp files (`pilot_audit_check.py`,
`pilot_order_check.py`) were created under `%LOCALAPPDATA%\Temp` to
run bounded read-only parquet checks; both were deleted after use.

---

## 19. Recommended next task

**Next slice: Stage 5 EUROMOD input-export design + EUROMOD run
(2016 couples only, 2,319,300 alternatives).** Specifically:

1. Author a separate authorization document — call it
   `docs/archive/2026-05-26_round2_chain_compression/strategy_v1_superseded/JMP_NC_pilot_stage5_euromod_amendment_v1.md` — that:
   - confirms EUROMOD runner location, invocation, output schema, and
     wall-time expectation;
   - specifies the per-partner long-format export from the pilot
     marginals;
   - states HE1–HE7 (this audit §17) as the Stage-5 halt conditions;
   - encodes the post-EUROMOD merge + re-sort + `is_chosen` alias
     operation as part of Stage 5's data-layer output, so Stages 7–9
     run on the production code unchanged.
2. **Independently** (and before Stage 8 / 9), produce the pilot
   precompute and estimation scaffold to consume the post-EUROMOD
   pilot parquet with the data-layer adjustments above. No production
   code change should be required if §14 is followed.
3. Do not invoke `scripts/enhanced/quick_verify.py` against the
   pilot parquet without a pilot variant; either skip it for the
   pilot or write `scripts/pilot/quick_verify_pilot.py`. Low priority.

---

*Status: read-only audit of `draw_joint` re-pointing surface for the
NC pilot. Produced 2026-05-22. No EUROMOD was run; no code or data
modified; M1-clean 2016 remains active; corrected pooled P3a track
unaffected. Next document: Stage 5 EUROMOD amendment, per §19.*
