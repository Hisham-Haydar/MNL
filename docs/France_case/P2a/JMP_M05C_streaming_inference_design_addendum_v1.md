# JMP-M05C Streaming Inference Design Addendum v1

**Applies to:** accepted Phase-5 inference design v4  
**Purpose:** replace the household-score persistence/custody architecture  
**Status:** Binding for JMP-M05C

## 1. Unchanged statistical target

The accepted inferential target remains:

- 1,555 household contributions;
- 37 free scores;
- 35 interior parameters for conditional covariance;
- accepted Phase-4 Hessian bread;
- unweighted household meat;
- correction `1555/1520`;
- active-bound and fixed-pin treatment;
- H0-A/B/C/G regional/access tests;
- accepted T/W numerical tolerances except where this addendum explicitly
  replaces an artifact/custody gate.

## 2. Revised score-computation contract

Scores must be computed in canonical stable `idhh` order in bounded transient
batches.

For each batch `b`, compute a float64 score matrix `S_b` with 37 columns and
immediately update:

\[
g_{37} \leftarrow g_{37} + \sum_{i\in b}s_i,
\]

\[
M_{37} \leftarrow M_{37} + S_b^\top S_b,
\]

\[
M_{35} \leftarrow M_{35} + S_{b,I}^\top S_{b,I},
\]

where `I` is the accepted ordered 35-interior selector.

Also update one global SHA-256 digest over the canonical byte stream:

`idhh canonical encoding || 37 float64 little-endian score values`

for all 1,555 households in order.

After updating the accumulators and digest, the batch score array must be
released. The implementation must never concatenate or persist the full
`1555×37` matrix.

## 3. Persisted score evidence

Persist only:

1. `score_aggregate_summary.json`
   - household count;
   - dimension;
   - canonical-order fingerprint;
   - global score-stream SHA-256;
   - aggregate score vector;
   - scalar norm/moment diagnostics;
   - batch size actually used;
   - dtype and byte-order contract.
2. `score_sum_free37.csv`
3. `meat_free37.npy` and `.csv`
4. `meat_interior35.npy` and `.csv`
5. covariance, correlation, standard-error, regional-test, diagnostics,
   manifest, and console artifacts required by the accepted design.

Do not persist:

- row-level scores;
- household identifiers paired with scores;
- row-level score digests;
- temporary score batches.

## 4. Fresh-process reproduction

The reproduction process reruns the same streaming computation from the
accepted sources and compares:

- global score-stream SHA-256;
- aggregate 37-score sum;
- `M_37`;
- `M_35`;
- canonical-order fingerprint;
- household count;
- actual batch size and numerical environment.

Use the accepted mixed exact/allclose rules specified by design v4.

No second score file is created.

## 5. Score-identity gate

Retain:

\[
\sum_i s_i=-\nabla \mathrm{negLL}.
\]

Use:

`np.allclose(sum_scores, -gradient, atol=1e-8, rtol=1e-8)`.

The identity is checked from the streamed aggregate vector.

## 6. Revised artifact/custody gate

The former household-score custody gate is replaced by:

### T-23S — No row-level score persistence

Pass only if:

- the output member set contains no row-level score artifact;
- no restricted-store member is created;
- no temporary batch remains after success or failure;
- static and behavioral tests show no code path writes a 2D household-score
  array;
- output allowlists contain only aggregate artifacts;
- failure finalization truthfully reports whether any temporary batch existed
  in memory, without attempting to serialize it.

This is an artifact-persistence gate, not an application-surface-count gate.

## 7. Revised reproduction gate

The prior duplicate-score-artifact form of T-12 is superseded by:

### T-12S — Fresh-process aggregate reproduction

A fresh process must reproduce:

- score-stream digest;
- score sum;
- 37×37 meat;
- 35×35 meat;
- order fingerprint;
- household count.

No row-level score artifact may be written.

## 8. Transaction contract

Use the normal MNL attempt transaction:

- unique staging directory;
- aggregate artifacts only;
- closed allowlisted member set;
- hashes and manifest;
- atomic publication to the dry-run attempt status;
- STOPPED preservation on failure;
- no `complete/` until later authorization.

No external restricted-store transaction is used.

## 9. Implementation surface

The implementation may use private helpers and the accepted generic derivative
primitive.

The review criterion is not the number of import-callable score-capable
functions. The criterion is:

1. the production runner uses the accepted likelihood route;
2. no production path persists row-level scores;
3. the final and failed output member sets are allowlisted and aggregate-only;
4. integration tests execute the actual production evaluator rather than a
   replacement fixture.

## 10. Disclosure and replication

Aggregate meat/covariance objects and the single global score-stream digest are
treated as non-row-level derived outputs subject to ordinary disclosure review.

No household-level score retention or special ACL is part of JMP-M05C.

## 11. Design precedence

Where design v4 conflicts with this addendum on:

- authoritative score `.npy`;
- row-level score CSV;
- restricted custody;
- T-12 duplicate artifact;
- T-23 custody fields;
- single full-score application surface;

this addendum controls.

All other design-v4 provisions remain binding.
