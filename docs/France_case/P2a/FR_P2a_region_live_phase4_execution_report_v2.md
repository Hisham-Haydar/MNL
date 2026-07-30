# Phase-4 execution report v2

**FINAL VERDICT: PASS**

The authorized Phase-4 rerun completed successfully. The published bundle is
`outputs/p2a_singles2016/region_live_v1/phase4_curvature_v1/complete/`.

| Item | Value |
| --- | --- |
| MNL HEAD | `fee60723ed27d6979976a3dc85b09cde3096e011` |
| Nested dclaborsupply HEAD / MNL gitlink | `27756a06ea189339aa82915ed2124628afed20eb` |
| Review-v7 SHA-256 | `cd0bb6ee5a0cbe130e65cdb211d9eb6d38ede1143e7b2431583013fd9a708d0c` |
| Phase-4 rerun exit code | `0` |
| Phase-4 status | `PHASE_4_COMPLETE` |
| Hessian evaluated | Yes |
| Hessian shape | `37 x 37` |
| Symmetry deviation / tolerance | `1.8189894035458565e-12` / `0.00023588019878151842` |
| Full Hessian minimum eigenvalue | `0.1037326963880782` |
| Full Hessian rank / tolerance | `37` / `4.2048457934380494e-06` |
| Condition number / classification | `405353.94719781954` / `clean` |
| Regional design source | `production_likelihood_loader_arrays` |
| Regional design shape / rank | `[1555, 10]` / `10` |
| Raw regional subblock minimum eigenvalue / PD | `3.3787399166319405` / Yes |
| Schur-complement rank / minimum eigenvalue | `10` / `2.255741652065068` |
| Regional loading-share warning | No |
| Post-evaluation input recheck | PASS — all 10 authenticated inputs matched pre-run and accepted hashes |
| Complete bundle SHA-256 | `5484886985aecd28e511719e42f45b85ad0e1755d1f951dbd13a79281d9665f3` |

The bundle contains the required manifest, diagnostics, console log, Hessian,
eigenvalue, regional-subblock, and Schur-complement artifacts. The optional
`hessian_free.npy` is also present.
