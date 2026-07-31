# 1. Verdict

The substantive T-7 backward-error repair is correct, but the commissioned micro-recheck cannot pass because the new §1.1 register contains an inaccurate relative-change statement and the attachment changes front-matter text outside the three locations expressly permitted by the commission.

# 2. Findings

1. **Exact coefficient — PASS.** With `K = 35`, `G = 1555`, and `u = 2⁻⁵³`, v3 correctly defines
   `γ_G = G·u/(1−G·u) = 1.7263968032924165e-13` and
   `κ_BE = K·γ_G = K·G·u/(1−G·u) = 6.042388811523458e-12`.
   The displayed derivation reproduces the displayed coefficient.
2. **Certified constant — PASS.** `κ_BE_certified = 6.0424e-12` is explicitly identified as upward-rounded and exceeds the displayed exact coefficient by approximately `1.11885e-17`. T-7 applies this certified constant, not the unrounded coefficient.
3. **Cross-location consistency and tightness — FAIL IN PART.** The F5-R1 register row, §15 T-7, and §16.2 agree on the formula and certified constant. The statement that the gate remains `16.55×` tighter than the `1e-10` rank convention is correct. However, the following §1.1 paragraph reports the change from `6.0423888115224145e-12` to `6.0424e-12` as `1.8e-5` in relative terms; the relative change is approximately `1.85e-6`. The same paragraph says no gate was weakened while also correctly calling the new floor marginally more permissive. It should instead state that T-7 is minimally loosened only to implement the valid upward-rounded certification, while remaining `16.55×` tighter than the rank convention.
4. **No change outside the three locations — FAIL.** The v2–v3 comparison also changes six front-matter lines in total: title, mission cycle, target path, supersession statement, remediation authority, and commit status. These changes are metadata-only and introduce no design change, but they are outside §1.1, §15 T-7, and §16.2. The author’s §1.1 explanation cannot override the commission’s literal no-other-change condition. Passage therefore requires either byte identity outside the three locations or an explicit manager ruling admitting the version-only front-matter exception.

# 3. Whether D-2 may be frozen

No substantive D-2 defect remains: the conditional 35-dimensional estimand and boundary treatment are unaffected. Formal D-2 freeze should nevertheless wait until the §1.1 numerical statement is corrected and the manager resolves the front-matter scope exception; no model, estimand, baseline, or additional methods review is required.

MICRO-RECHECK FAIL
