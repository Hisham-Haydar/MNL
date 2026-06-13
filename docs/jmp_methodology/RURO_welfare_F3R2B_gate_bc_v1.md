# F3-R2B: Dispositive Joint-Batch Gate B/A/C (yem-fix run)

## Fix applied

Root cause of F3-R2A `CONSTRUCTION_MISMATCH`: arithmetic path mismatch in `yem`.

| Path | Formula | Result |
|------|---------|--------|
| Task 2 (`_overwrite_choice_vars`) | `yem = reg_h*w*wpm + ot_h*w*wpm` | reference |
| Task 3 (F3-R2A joint loop) | `yem = (reg_h+ot_h)*w*wpm` | differs by 1-2 ULP |
| Task 3 (F3-R2B joint loop) | `yem00=reg_h*w*wpm; yemxp=ot_h*w*wpm; yem=yem00+yemxp` | **FIXED** |

`a*c + b*c ≠ (a+b)*c` in IEEE 754 — observed difference was 4.5e-13 to 9.1e-13 (~1-2 ULP for yem ≈ 2000 EUR/month). Not a real construction mismatch.

## Gate results

| Gate | Verdict |
|------|---------|
| B — byte-identity of anchor em_input | PASS |
| A — EUROMOD determinism (repeat primary, tol 1e-6) | PASS |
| C — joint vs target-only sim output (all cols, tol 1e-6) | FAIL |

**Overall verdict: NOT_LICENSED**

## Conclusions

```
READY FOR F4: yes
FROZEN FULL-V S=100 GATE: fail
UTILITY-ONLY B2 ANCHOR GATE: fail
JOINT BATCHING METHOD: not licensed
BATCH-CONTEXT DEPENDENCE: proven
FULL SINGLES V_i^dir AT S=100 AUTHORIZED: no
```
