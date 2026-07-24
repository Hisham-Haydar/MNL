#!/usr/bin/env python
"""FR P2a region-live — fresh-process reload verifier.

Two modes (plan v2 s17, s24; decisions v2 D-2):

  --mode pre-estimation   (default) Pre-estimation reload check for the Phase 1-2
      dry-run era: in a FRESH process, rebuild the objective from the frozen
      region_live_v1 stem + the stored region-live theta (root
      theta_p2a_singles_2016_v1.csv 'trial' column) through the dclaborsupply
      package APIs, and verify the G-19 anchors (JAX within 1e-4 of the full
      target; NumPy/JAX within 1e-6). This is NOT the strict post-estimation
      cold-reload gate. Writes nothing unless --write-json is given (the path
      must resolve inside region_live_v1/).

  --mode cold-reload      Phase-7 strict cold-reload gate (MANAGER-GATED; must
      NOT be invoked before Phases 3-6 exist). Verifies provenance hashes,
      parameter ordering, and the D-2 anchors against region_live_v1/theta.csv
      + estimation_results.json, then writes cold_reload_verification.json.
      The script refuses to run this mode while the estimation artifacts are
      absent.

No optimizer is imported in either mode. No EUROMOD. No draw generation.
Exit codes: 0 pass, 2 check failed / refused, 3 unexpected error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import numpy as np
import pandas as pd
import yaml

MNL_ROOT = Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _py(o: Any):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON-serializable: {type(o)}")


def _environment() -> Dict[str, str]:
    import jax
    return {"python": sys.version.split()[0], "jax": jax.__version__,
            "numpy": np.__version__, "pandas": pd.__version__,
            "platform": platform.platform(),
            "utc": datetime.now(timezone.utc).isoformat()}


def _build_objective(cfg: Dict[str, Any], out_root: Path):
    """Load spec + frozen stem through package APIs; return (spec, names, dm, df, tot, np_eval)."""
    from dclaborsupply import EstimationSpec
    from dclaborsupply.data.loader import load_singles
    from dclaborsupply.likelihood.engine_jax import build_jax_singles_ll
    from dclaborsupply.likelihood.index import compute_index
    import jax
    import jax.numpy as jnp

    spec = EstimationSpec.from_yaml(str(MNL_ROOT / cfg["certified_spec"]["yaml"]))
    names = list(spec.all_param_names)
    stem = cfg["run"]["frozen_stem_name"]
    p_parquet = out_root / f"{stem}__singles.parquet"
    p_meta = out_root / f"{stem}__mnlmeta.json"
    if not (p_parquet.is_file() and p_meta.is_file()):
        raise FileNotFoundError(
            f"frozen stem not found under {out_root} — run Phase 1 first")
    er = pd.read_parquet(p_parquet)
    meta = json.loads(p_meta.read_text(encoding="utf-8"))
    dm = load_singles(er[pd.to_numeric(er["dgn"]) == 1].reset_index(drop=True),
                      spec, is_male=True, metadata=meta)
    df_ = load_singles(er[pd.to_numeric(er["dgn"]) == 0].reset_index(drop=True),
                       spec, is_male=False, metadata=meta)
    nm, _ = build_jax_singles_ll(dm, spec, is_male=True)
    nf, _ = build_jax_singles_ll(df_, spec, is_male=False)
    tot = jax.jit(lambda t: nm(t) + nf(t))

    def jax_eval(theta: np.ndarray) -> float:
        return float(tot(jnp.asarray(theta)))

    def np_eval(theta: np.ndarray) -> float:
        return float(compute_index(spec, (dm, df_, None), theta,
                                   ruro=True, backend="numpy"))

    return spec, names, jax_eval, np_eval, {"stem_parquet_sha256": _sha256(p_parquet),
                                            "stem_mnlmeta_sha256": _sha256(p_meta)}


def _mode_pre_estimation(cfg: Dict[str, Any], out_root: Path,
                         write_json: Optional[Path]) -> int:
    g = cfg["gates"]
    st = cfg["stored_region_live_theta"]
    res: Dict[str, Any] = {"mode": "pre-estimation",
                           "note": ("pre-estimation reload check for the Phase 1-2 "
                                    "dry-run; NOT the Phase-7 strict cold-reload gate"),
                           "environment": _environment()}
    t0 = time.time()
    spec, names, jax_eval, np_eval, hashes = _build_objective(cfg, out_root)
    res.update(hashes)

    tab = pd.read_csv(MNL_ROOT / st["v1_csv"]).set_index("param")
    res["theta_source"] = st["v1_csv"]
    res["ordering_ok"] = (list(tab.index) == names)
    theta = tab[st["value_column"]].astype(float).reindex(names).to_numpy()

    res["negll_jax"] = jax_eval(theta)
    res["negll_numpy"] = np_eval(theta)
    res["abs_dev_full"] = abs(res["negll_jax"] - float(cfg["targets"]["negll_full"]))
    res["abs_dev_4dp"] = abs(res["negll_jax"] - float(cfg["targets"]["negll_4dp"]))
    res["backend_abs_dev"] = abs(res["negll_jax"] - res["negll_numpy"])
    res["full_ok"] = res["abs_dev_full"] <= float(g["g19_theta_eval_tol_full"])
    res["anchor_ok"] = res["abs_dev_4dp"] < float(g["g19_anchor_tol_4dp"])
    res["backend_ok"] = res["backend_abs_dev"] <= float(g["g19_backend_agreement_tol"])
    res["ok"] = bool(res["ordering_ok"] and res["full_ok"] and res["anchor_ok"]
                     and res["backend_ok"])
    res["wall_seconds"] = round(time.time() - t0, 1)

    print(json.dumps(res, indent=2, default=_py))
    if write_json is not None:
        wj = write_json.resolve()
        if out_root.resolve() != wj and out_root.resolve() not in wj.parents:
            print("REFUSED: --write-json must resolve inside region_live_v1/",
                  file=sys.stderr)
            return 2
        wj.parent.mkdir(parents=True, exist_ok=True)
        wj.write_text(json.dumps(res, indent=2, default=_py), encoding="utf-8")
    return 0 if res["ok"] else 2


def _mode_cold_reload(cfg: Dict[str, Any], out_root: Path) -> int:
    """Phase-7 strict gate (G-17, D-2). MANAGER-GATED — refuses until Phase 3+ artifacts exist."""
    g = cfg["gates"]
    theta_csv = out_root / "theta.csv"
    results_json = out_root / "estimation_results.json"
    prov_json = out_root / "provenance.json"
    if not (theta_csv.is_file() and results_json.is_file()):
        print("REFUSED: cold-reload mode is the Phase-7 gate; region_live_v1/theta.csv "
              "and estimation_results.json do not exist (Phases 3-8 are manager-gated "
              "and have not run).", file=sys.stderr)
        return 2

    res: Dict[str, Any] = {"mode": "cold-reload", "environment": _environment()}
    t0 = time.time()

    # hash re-verification against provenance
    res["hash_checks"] = {}
    if prov_json.is_file():
        prov = json.loads(prov_json.read_text(encoding="utf-8"))
        for name, sha in (prov.get("output_hashes") or {}).items():
            p = out_root / name
            if p.is_file():
                res["hash_checks"][name] = {"expected": sha, "actual": _sha256(p),
                                            "ok": _sha256(p) == sha}
    res["hashes_ok"] = all(v["ok"] for v in res["hash_checks"].values()) \
        if res["hash_checks"] else False

    spec, names, jax_eval, np_eval, hashes = _build_objective(cfg, out_root)
    res.update(hashes)
    tab = pd.read_csv(theta_csv).set_index("param")
    res["ordering_ok"] = (list(tab.index) == names)
    theta = tab["value"].astype(float).reindex(names).to_numpy()
    stored = json.loads(results_json.read_text(encoding="utf-8"))
    negll_stored = -float(stored["results"]["joint"]["final_ll"])

    res["negll_reload"] = jax_eval(theta)
    res["negll_numpy"] = np_eval(theta)
    res["negll_stored"] = negll_stored
    res["abs_dev_stored"] = abs(res["negll_reload"] - negll_stored)
    res["abs_dev_4dp"] = abs(res["negll_reload"] - float(cfg["targets"]["negll_4dp"]))
    res["backend_abs_dev"] = abs(res["negll_reload"] - res["negll_numpy"])
    res["anchor_ok"] = res["abs_dev_4dp"] < float(g["g17_cold_reload"]["anchor_4dp"])
    res["stored_ok"] = res["abs_dev_stored"] <= float(g["g17_cold_reload"]["vs_stored"])
    res["backend_ok"] = res["backend_abs_dev"] <= float(g["g19_backend_agreement_tol"])
    res["ok"] = bool(res["hashes_ok"] and res["ordering_ok"] and res["anchor_ok"]
                     and res["stored_ok"] and res["backend_ok"])
    res["wall_seconds"] = round(time.time() - t0, 1)

    out = out_root / "cold_reload_verification.json"
    out.write_text(json.dumps(res, indent=2, default=_py), encoding="utf-8")
    print(json.dumps(res, indent=2, default=_py))
    return 0 if res["ok"] else 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--mode", choices=["pre-estimation", "cold-reload"],
                    default="pre-estimation")
    ap.add_argument("--write-json", default=None,
                    help="pre-estimation mode: optional JSON output path "
                         "(must resolve inside region_live_v1/)")
    args = ap.parse_args(argv)

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    out_root = Path(args.out) if args.out else (MNL_ROOT / cfg["run"]["output_root"])
    try:
        if args.mode == "pre-estimation":
            return _mode_pre_estimation(cfg, out_root,
                                        Path(args.write_json) if args.write_json else None)
        return _mode_cold_reload(cfg, out_root)
    except FileNotFoundError as e:
        print(f"CHECK FAILED: {e}", file=sys.stderr)
        return 2
    except Exception:
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
