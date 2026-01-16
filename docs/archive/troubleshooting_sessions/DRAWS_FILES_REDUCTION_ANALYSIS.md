# DRAWS FILES - Do They Need Reduction?

## Analysis

### What We Know from Step 6 Output:
```
Loaded singles draws: 168,319 rows
Singles MNL dataset ready: 167,600 rows, 641 columns
```

### Where Do the 641 Columns Come From?

**MNL Dataset (641 columns) = Source A + Source B + Source C**

**Source A: EUROMOD (27 columns after reduction)**
- ils_dispy, hours, wage, demographics, etc.

**Source B: Draws File (unknown column count)**
- Draw-specific hours, wages, priors for each alternative
- This is the BIG unknown!

**Source C: Step 6 Created Columns (~15-20 columns)**
- consumption, leisure, c_norm, l_norm, log_c_norm, log_l_norm
- age_norm, age_norm2
- educL, educM, educH
- gsur
- sample_group

### Question: Are the Draws Files Bloated?

**To determine this, we need to:**
1. Count columns in `singles_RURO_ready_RURO_draws.parquet`
2. Identify which columns are actually used by Step 6
3. See if there are unused EUROMOD columns carried over from Step 3

### Expected Draws File Structure:

The draws files SHOULD contain:
- **IDs:** idperson, draw, is_chosen
- **Draw-specific labor:** hours (for each draw), wage (for each draw)
- **Prior probabilities:** prior, prior_h, prior_w, log_prior
- **Demographics:** dag, dgn, deh, drgn1 (person characteristics)
- **Household info:** idhh, idpartner, n_children
- **Metadata:** dwt (weights)

**SHOULD NOT contain:**
- ❌ EUROMOD outputs (ils_dispy, taxes, benefits) ← Already in EUROMOD file!
- ❌ EUROMOD internal flags (i_*, il_*, tu_*) ← Not needed for MNL
- ❌ Detailed tax-benefit components ← Not used in estimation

### Hypothesis:

If the draws files have ~600 columns, they likely contain:
1. ✅ **Essential draws data** (~30-50 columns)
2. ❌ **EUROMOD outputs copied from Step 3** (~300+ columns) ← **SHOULD BE REMOVED!**
3. ❌ **EUROMOD internals** (~200+ columns) ← **SHOULD BE REMOVED!**

### Why This Matters:

**Current flow:**
```
EUROMOD (342 cols) → Step 3 → Draws files (~600 cols) → Step 6 → MNL (641 cols)
                                    ↑
                            Contains duplicate EUROMOD data!
```

**Optimal flow:**
```
EUROMOD (27 cols) ─┐
                   ├→ Step 6 merge → MNL (~100 cols)
Draws (30-50 cols) ─┘
```

### Recommended Action:

**YES, we should reduce the draws files!**

The draws files likely contain:
- Duplicate EUROMOD outputs (already in combined_draws_em.parquet)
- EUROMOD internals not needed for MNL
- Only need: IDs, draw-specific hours/wages, priors, basic demographics

### Expected Impact:

If we reduce draws files from ~600 cols to ~30-50 cols:
- **Step 6 memory usage:** ~90% reduction
- **Step 6 speed:** 2-3x faster (less data to process)
- **MNL dataset size:** ~100 columns instead of 641
- **Step 7 estimation:** Faster data loading, clearer code

---

## Next Steps

1. **Verify draws file column count** (need to check actual file)
2. **Identify essential draws columns** (IDs, hours, wages, priors)
3. **Create draws file reduction script** (similar to EUROMOD reduction)
4. **Test with Step 6** (verify it still works)
5. **Benchmark speed improvement**

---

## Answer to Your Question

**YES, we likely DO need to reduce the draws files!**

The ~600 columns in the draws files probably contain:
- ❌ Duplicate EUROMOD data (already in combined_draws_em.parquet)
- ❌ EUROMOD internals (not needed)
- ✅ Only ~30-50 columns are actually needed

**This would explain why the final MNL dataset has 641 columns:**
```
641 = 27 (EUROMOD reduced) + 600 (draws bloated) + 15 (Step 6 created)
```

**If we reduce draws files:**
```
~100 = 27 (EUROMOD reduced) + 50 (draws essential) + 15 (Step 6 created)
```

**This is worth investigating!**
