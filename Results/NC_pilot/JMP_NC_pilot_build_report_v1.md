# JMP NC Pilot — Build Report v1 (pre-execution halt)

*France RURO multi-year extension | v1 | 2026-05-22*

Document class: pilot build report. This report records that the build
authorized by `docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md` was **halted before
any build action** at the pre-execution check, on the user's direction.
**No file in the repository has been modified by this session except this
report.** No Mincer fit was performed. No draws were generated. No
parquet was rebuilt. No EUROMOD was run. No GSURv2 merge was re-computed.
No MNL rebuild was performed. No precompute was run. No estimation was
run. No welfare was computed. No SA2 was issued. M1-clean 2016 remains
the active JMP baseline. The corrected pooled P3a track is unaffected
and continues independently on its frozen 100-diagonal, unconditional-
wage spec.

---

## 1. Scope and authorization provenance

**Authorizing document:** `docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md`
(JMP NC Pilot — Spec Contract v1, dated 2026-05-22). The contract
authorizes the 2016-couples-only pilot scope of §4, gated by the halt
conditions of §26.

**Pilot scope per contract §4:**
- Population: couples only.
- Year: FR_2016 only (n = 2,577 couples, audit-confirmed).
- Choice set: 30 × 30 = 900 joint alternatives per couple
  (couples rows = 2,319,300).
- Wage: W1 (occupation intercepts, reference loc4 = 1) baseline;
  two-group (`1[loc4=4]`) comparison.
- `occ_spec = "fixed"` retained; single common sigma.
- Draw method: Halton preferred, Sobol acceptable, PCG64 documented
  fallback.
- Simulation-consistency points: 400 / 900 / 1,600.
- `delta_occ*` **calibrated** (pre-draw Mincer step, fixed at draw
  time), **not** free structural parameters. Free-parameter count stays
  at 55.

**Inputs read for this session (no modification):**
- `docs/France_case/NC_pilot/design/JMP_NC_pilot_spec_contract_v1.md` (full read).
- `Results/NC_pilot/JMP_nc_pilot_feasibility_audit_v1.md` (full read, in prior
  session).
- `docs/France_case/P3a/design/JMP_next_cycle_opportunity_respecification_plan_v1.md` (full
  read, in prior session).
- `scripts/enhanced/enh_RURO_draws.py` (targeted Grep + ranged Read in
  prior session).
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py` (targeted Read of the
  couples reshape function in prior session).
- `scripts/maintenance/prepare_pooled_estimation_ready.py` (ranged Read
  in prior session).
- `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`
  (full read in prior session).
- `Data/processed/fr/pooled/fr_p3a_gsurv2_estimation_ready__couples.parquet`
  (bounded column read of `idhh`/`draw`/`year_tag` in prior session,
  not in this session).

No write operation other than this report.

---

## 2. Halt event

**Halt point:** before Stage 1 of the §28 build prompt (pre-draw Mincer
fit). The build was halted at the pre-execution scope check.

**Halt mechanism:** the assistant raised a pre-execution scope concern
covering five points (Stage 6 EUROMOD runner-availability unknown;
Stage 9 estimation time/scope; Stage 1–4 multiple unconfirmed design
choices; HP8 risk if autonomous escalation; the contract's "feasibility-
and-design instrument" framing) and offered the user four options:

A. Stage 1 only (Mincer fit on observed draw=0 working wages).
B. Scaffolding only (driver/config/--pilot mode; no data writes).
C. Halt and write report up to here.
D. Stages 1–4 in one go (Mincer + draws + 900-product parquet; stop
   before EUROMOD).

**User selection:** **Option C — Halt and write report up to here.**

This report is the artefact required by spec contract §26 (final
paragraph): *"Any halt → stop, write the build report up to the halt,
await a contract amendment. Do not silently fix and continue."*

---

## 3. Reasoning for the halt

The halt is **not** a §26 HP1–HP9 *technical* halt (no production guard
was edited, no proposal-density inconsistency was created, no
`draw_joint == 0` violation was produced — because no build action was
taken). It is a **pre-execution scope halt** rooted in the contract's
own language and structure:

1. **EUROMOD runner is an external dependency.** Spec contract §19
   names "2,577 couples × 900 = 2,319,300 EUROMOD evaluations" as the
   binding data-build cost. The contract does not specify the EUROMOD
   runner location, invocation, expected wall time, or output schema.
   Stages 6 of the §28 prompt assumes a callable EUROMOD step exists in
   the project; this session has not verified it. Launching EUROMOD
   without that verification is an action whose blast radius is large
   (multi-hour-to-day wall time, intermediate file footprint, potential
   external resource contention).

2. **The contract is a "feasibility-and-design instrument" (§3).** The
   pilot's first objective per §23 is to *measure* the EUROMOD and
   precompute and gradient cost. Treating the §28 build prompt as a
   single-shot autonomous job pushes against this framing: the contract
   wants discrete, checkpointed stages, not one large opaque run.

3. **Multiple Stage 1–4 design choices are open in the contract:**
   - Halton vs Sobol vs PCG64 fallback (contract §16 says
     "if implementable", a judgment call without a single forced
     choice).
   - Pooled 2015–2017 Mincer vs 2016-only fallback (contract §15
     specifies pooled "if available at fit time", which is a runtime
     check on the data, not a pre-decided path).
   - Pilot output directory layout (contract names neither a directory
     nor a file scheme; the assistant would have to invent one).
   - The `--pilot` flag wiring vs separate driver (contract §17 offers
     either with "preferred" not "required" guidance).

   These are not technical blockers — they are decisions the executor
   must make, and the user's selection of Option C indicates that
   making them autonomously is not the intent.

4. **HP8 (any attempt to … run beyond couples-2016 scope).** Even an
   intermediate write that escalates outside the narrow scope (for
   example, modifying a production script in place rather than a pilot
   driver) is the failure mode HP8 protects against. The cleanest way
   to preserve HP8 invariants until an executor with EUROMOD-runner
   confirmation is engaged is to do no writes.

The user's choice (Option C) accepts the assistant's reading: the build
needs an EUROMOD-runner confirmation and an explicit Stage-1-vs-full-
pipeline scope decision before proceeding. This report documents that
state.

---

## 4. Data-prep changes made

**None.** No file in the repository has been modified by this session
except this report. No pilot driver was created, no `--pilot` mode was
added to `prepare_pooled_estimation_ready.py`, no pilot config was
written, and no edits were made to:

- `scripts/enhanced/enh_RURO_draws.py` (unchanged).
- `scripts/enhanced/enh_RURO_prep_mnl_basic.py` (unchanged).
- `scripts/maintenance/prepare_pooled_estimation_ready.py` (unchanged,
  production guards intact at lines 70–72).
- `scripts/enhanced/specifications/estimation_spec_ruro_occ_P3a_pooled.yaml`
  (unchanged, frozen 100-diagonal unconditional-wage spec preserved).

No downstream `draw_joint` re-pointing audit was performed (because no
joint key was constructed).

---

## 5. Pre-draw Mincer fit

**Not run.** No coefficients were fit. No pilot config was written. No
accepted-wage caveat is recorded in code; the caveat remains documented
only in the spec contract §14 and the design memo.

---

## 6. Draw-method record

**Not run.** No marginal draws were regenerated. No sequence / seed /
scramble was selected or recorded for the pilot. The existing draws
(produced by the P3a pipeline under PCG64 with seed-and-log discipline)
remain in place and unmodified.

---

## 7. EUROMOD run

**Not run.** Zero EUROMOD evaluations were performed in this session.
The 2,577 × 900 = 2,319,300 evaluation surface named in spec contract
§19 was not entered.

---

## 8. GSUR re-merge

**Not run.** GSUR centring was not re-computed. The existing P3a-centred
GSUR values remain in place and were not consulted for the pilot.

---

## 9. MNL rebuild

**Not run.** No couples wide-format parquet was rebuilt. No
`__mnlmeta.json` was produced with `n_draws=900` for couples. The
production estimation-ready parquets and metadata are unchanged.

**Production invariants confirmed unchanged** (status quo from prior
session reads, not re-verified in this session):

- Singles parquet: 500,700 rows (per `__mnlmeta.json`).
- Couples parquet: 743,800 rows (diagonal, 100 alternatives per
  couple-year, per `__mnlmeta.json`).
- `n_draws`: 100 per individual.
- Cluster key: `cluster_id` from `idorighh`.
- R1 region repair applied 2026-05-21 (per `__mnlmeta.json`).

These are unchanged because nothing was written.

---

## 10. Precompute checks

**Not run.** No precompute on a pilot parquet was attempted (because no
pilot parquet exists).

---

## 11. Pilot validation checks

**Not run.** The §23 validation checks all presuppose at minimum a
completed pilot data build and at least one diagnostic estimation; this
session reached neither. The seven required checks remain pending:

- Pipeline end-to-end confirmation — pending.
- Wage-occupation separate-identification check — pending.
- W1 vs two-group comparison — pending.
- 400 / 900 / 1,600 simulation-consistency — pending.
- Computational budget — pending.
- Draw-method record — pending.
- Accepted-wage caveat statement (the *check* — the rationale is
  recorded in §14 of the contract).

---

## 12. Halt-condition status

| Halt | Status |
|---|---|
| HP1 — production behaviour change when pilot absent | Not fired. Production scripts unchanged. |
| HP2 — proposal-density not updated with wage draw | Not applicable. No draw replacement attempted. |
| HP3 — `draw_joint == 0` chosen-row invariant | Not applicable. No joint key constructed. |
| HP4 — couples disposable income all-NaN | Not applicable. No EUROMOD run. |
| HP5 — GSUR centring inherited from P3a | Not applicable. No GSUR re-merge attempted. |
| HP6 — region columns all-NaN, R1 not re-applied | Not applicable. No rebuild attempted. |
| HP7 — separate-identification failure with free `delta_occ*` | Not applicable. No estimation attempted; `delta_occ*` are calibrated by contract design. |
| HP8 — welfare / SA2 / promotion / M1-clean displacement / out-of-scope run | Not fired. No such action attempted. |
| HP9 — pilot row count or singles row count drift | Not applicable. No write performed. |

**No HP1–HP9 has fired.** The halt is a pre-execution scope halt
recorded in §2–§3 of this report, distinct from a technical halt.

---

## 13. Promotion-debt list

**Not applicable to this session.** Because no pilot code was written,
no hard-coded France / P3a / 2016 / 900 constants were introduced. The
spec contract §17's promotion-debt accounting target (the build-time
list of hard-coded constants that would need parameterisation before
the pilot code is promoted to the reusable package) remains to be
populated when the build is executed.

---

## 14. State of the repository at halt

- Working tree, before this report write: clean (per the resumed-session
  status check).
- Working tree, after this report write: one new file
  (`Results/NC_pilot/JMP_NC_pilot_build_report_v1.md`).
- Branch: `main` (per environment context).
- No commit was created by this session.
- No production script, YAML, or data artefact was modified.
- The corrected pooled P3a estimation artefacts under `Results/` remain
  unmodified.

---

## 15. What is needed to resume

To resume the §28 build under the existing contract, the executor (or a
future session under the user's direction) needs explicit confirmation
on the following, ideally in a short amendment-style direction note:

1. **EUROMOD runner status.** Where is the EUROMOD invocation point in
   this codebase (or external)? What is the expected wall time per
   alternative? What output schema (file? database? parquet?) does it
   produce, and where will the pilot's outputs land? Without this, Stage
   6 cannot start.
2. **Pilot output directory.** Confirm a pilot-scoped path. A
   reasonable default the executor can adopt: `Data/pilot/nc_2016_couples/`
   for parquet/metadata and `scripts/pilot/` for driver/config code, but
   the user should confirm or override before any write.
3. **Mincer fitting set choice at runtime.** Pooled 2015–2017 with year
   controls is the contract's preferred choice (§15); confirm that the
   working observed (draw=0) sample at pooled level is accessible at
   fit time. The diagnostic confirmed this is the case from the
   estimation-ready singles parquet (4,611 working singles) plus the
   draw=0 working couples partners (≈7,134 male, ≈7,141 female,
   covering 2015–2017), but the pooled-vs-2016-only switch is a
   runtime decision the executor will need to take.
4. **Halton / Sobol / PCG64 choice.** Contract §16 prefers Halton if
   cleanly droppable into the four `rng.uniform` call sites in
   `enh_RURO_draws.py` (state, hours, wage, occupation choice). The
   executor must commit to one of {Halton, Sobol, PCG64 fallback} and
   record the choice; the contract does not pre-decide.
5. **Staged vs single-shot execution.** Confirm whether the build
   should be executed in checkpointed stages (Stage 1 → review → Stage
   2 → review → ...) with assistant pause points between stages, or as
   one autonomous run with the report written only at the end / on
   halt. Option C in §2 of this report effectively pre-selects
   "staged" by stopping before Stage 1.

A contract amendment is not strictly required if the user simply
provides these five confirmations in a follow-up message; the contract
itself authorizes the build scope.

---

## 16. Required final statements

- **M1-clean 2016 remains active.**
- **Corrected pooled P3a track is unaffected.**
- **No welfare was computed.**
- **No SA2 was issued.**
- **No canonical promotion was performed.**
- **Pilot scope only.**

---

*Status: pilot build report v1, written at a pre-execution scope halt
under spec contract §26's "stop and report" discipline. No build action
was taken. The report exists so the next session has an explicit record
of the halt point, the reasoning, and the five confirmations needed to
resume. No HP1–HP9 fired. Frozen pooled P3a spec and post-estimation
track unaffected.*
