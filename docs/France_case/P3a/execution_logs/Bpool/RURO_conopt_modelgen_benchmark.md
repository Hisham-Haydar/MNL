# CONOPT model-generation benchmark — results

**Params:** 49  **Alt rows:** 180,900  **Couples alts/HH:** 401  **Years:** 2015,2016,2017
**HH:** sm=300 sf=300 cou=300

All configs solve the IDENTICAL likelihood; `ll_match` confirms no economic change (LL equal to reference within 1e-6).

## Timing table

| Config | link | thr | wall (s) | modelgen (s) | solve (s) | iters | LL match |
|---|---|---:|---:|---:|---:|---:|---|
| ref.baseline_fresh | memory | 8 | 431.9 | 404.5 | 26.6 | 13 | True |
| C.frozen_warm1 | memory | 8 | 27.1 | 0.0 | 26.7 | 13 | True |
| C.frozen_warm2 | memory | 8 | 27.1 | 0.0 | 26.7 | 13 | True |
| C.frozen_cold | memory | 8 | 42.3 | 0.0 | 41.9 | 21 | True |

## Frozen model (model instance) — did generation collapse?

Freeze generates the model instance ONCE; subsequent solves modify variable .l/.lo/.up and re-solve. If `modelgen` drops to ~0 on frozen_warm2 / frozen_cold, generation is skipped -> 4x solves pay generation once. LL match confirms no economic change.

| Solve | wall (s) | modelgen (s) | solve (s) | iters | LL match |
|---|---:|---:|---:|---:|---|
| C.frozen_warm1 | 27.1 | 0.0 | 26.7 | 13 | True |
| C.frozen_warm2 | 27.1 | 0.0 | 26.7 | 13 | True |
| C.frozen_cold | 42.3 | 0.0 | 41.9 | 21 | True |

**Generation collapse on re-solve: NO** (solve1 modelgen=0.0s -> solve2 modelgen=0.0s).

## One-time build-phase breakdown (Python expression build)

| Phase | seconds |
|---|---:|
| container_create | 0.06 |
| param_vars | 1.55 |
| ll_expr_build | 3.03 |
| model_create | 0.04 |
