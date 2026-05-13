"""One-shot validation of rebuilt M0_stijn_occ MNL parquets.

Read-only. Produces a JSON blob the report references.
"""
import json
import os
import datetime
import numpy as np
import pandas as pd

BASE = r"Z:/hisham/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl"
SINGLES_PATH = BASE + "__singles.parquet"
COUPLES_PATH = BASE + "__couples.parquet"
MNLMETA_PATH = BASE + "__mnlmeta.json"

out = {}

# ---- File existence + metadata
for label, path in [("singles", SINGLES_PATH), ("couples", COUPLES_PATH), ("mnlmeta", MNLMETA_PATH)]:
    st = os.stat(path) if os.path.exists(path) else None
    out.setdefault("files", {})[label] = {
        "path": path,
        "exists": st is not None,
        "size_bytes": st.st_size if st else None,
        "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat() if st else None,
    }

s = pd.read_parquet(SINGLES_PATH)
c = pd.read_parquet(COUPLES_PATH)
mnlmeta = json.load(open(MNLMETA_PATH)) if os.path.exists(MNLMETA_PATH) else None

# ---- Sample structure
def _structure(df, label, work_col, hours_col):
    out_struct = {
        "rows": int(len(df)),
        "n_columns": int(len(df.columns)),
        "n_households": int(df["idhh"].nunique()) if "idhh" in df.columns else None,
    }
    alts = df.groupby("idhh").size()
    out_struct["alt_per_hh_min"] = int(alts.min())
    out_struct["alt_per_hh_median"] = float(alts.median())
    out_struct["alt_per_hh_max"] = int(alts.max())
    out_struct["alt_per_hh_distinct_values"] = sorted(alts.unique().tolist())
    chosen_col = "is_chosen" if "is_chosen" in df.columns else ("chosen" if "chosen" in df.columns else None)
    out_struct["chosen_col_used"] = chosen_col
    if chosen_col:
        per_hh_chosen = df.groupby("idhh")[chosen_col].sum()
        out_struct["chosen_per_hh_min"] = int(per_hh_chosen.min())
        out_struct["chosen_per_hh_max"] = int(per_hh_chosen.max())
        out_struct["n_hh_with_chosen_eq_1"] = int((per_hh_chosen == 1).sum())
        out_struct["n_hh_with_chosen_ne_1"] = int((per_hh_chosen != 1).sum())
    return out_struct

out["structure_singles"] = _structure(s, "singles", "working", "hours")
out["structure_couples"] = _structure(c, "couples", "working_male", "hours_male")

# ---- Required M0 columns
REQ_S = ["loc4", "working", "log_q_E", "log_q_H", "log_q_W", "log_q_Occ", "prior", "log_prior", "idhh"]
DUMMY_S = ["loc4_2", "loc4_3", "loc4_4"]
REQ_C = [
    "loc4_male", "loc4_female", "working_male", "working_female",
    "log_q_E_male", "log_q_H_male", "log_q_W_male", "log_q_Occ_male",
    "log_q_E_female", "log_q_H_female", "log_q_W_female", "log_q_Occ_female",
    "prior", "log_prior", "idhh",
]
DUMMY_C = [
    "loc4_2_male", "loc4_3_male", "loc4_4_male",
    "loc4_2_female", "loc4_3_female", "loc4_4_female",
]
out["required_singles_missing"] = [c0 for c0 in REQ_S if c0 not in s.columns]
out["required_couples_missing"] = [c0 for c0 in REQ_C if c0 not in c.columns]
out["dummies_singles_present"] = [c0 for c0 in DUMMY_S if c0 in s.columns]
out["dummies_singles_absent"] = [c0 for c0 in DUMMY_S if c0 not in s.columns]
out["dummies_couples_present"] = [c0 for c0 in DUMMY_C if c0 in c.columns]
out["dummies_couples_absent"] = [c0 for c0 in DUMMY_C if c0 not in c.columns]

# ---- Occupation variation
def _occ_variation(df, loc_col, work_col, label):
    rep = {}
    if loc_col not in df.columns:
        return {"missing": True}
    w = df[df[work_col] == 1] if work_col in df.columns else df
    nu = w.groupby("idhh")[loc_col].nunique()
    rep["n_households_with_working"] = int(len(nu))
    rep["median_distinct_loc4"] = float(nu.median())
    rep["mean_distinct_loc4"] = float(nu.mean())
    rep["max_distinct_loc4"] = int(nu.max())
    rep["min_distinct_loc4"] = int(nu.min())
    rep["pct_hh_eq_1"] = float((nu == 1).mean())
    rep["distribution_of_distinct_counts"] = {int(k): int(v) for k, v in nu.value_counts().sort_index().to_dict().items()}
    rep["loc4_value_counts_overall"] = {int(k): int(v) for k, v in df[loc_col].value_counts().sort_index().to_dict().items()}
    rep["loc4_value_counts_working"] = {int(k): int(v) for k, v in w[loc_col].value_counts().sort_index().to_dict().items()}
    return rep

out["occupation_variation_singles"] = _occ_variation(s, "loc4", "working", "singles")
out["occupation_variation_couples_male"] = _occ_variation(c, "loc4_male", "working_male", "couples_male")
out["occupation_variation_couples_female"] = _occ_variation(c, "loc4_female", "working_female", "couples_female")

# ---- Prior invariants
def _prior_invariants_singles(df):
    rep = {}
    p = df["prior"].to_numpy()
    lp = df["log_prior"].to_numpy()
    rep["n_rows"] = int(len(p))
    rep["min_prior"] = float(p.min())
    rep["n_prior_le_0"] = int((p <= 0).sum())
    rep["n_prior_nan"] = int(np.isnan(p).sum())
    mask = (p > 0) & np.isfinite(p) & np.isfinite(lp)
    diff = np.abs(np.log(p[mask]) - lp[mask])
    rep["max_abs_log_diff"] = float(diff.max())
    rep["n_rows_log_diff_gt_1e_8"] = int((diff > 1e-8).sum())
    w = (df["working"] == 1).astype(float).to_numpy()
    recon = (df["log_q_E"].to_numpy()
             + w * (df["log_q_H"].to_numpy() + df["log_q_W"].to_numpy() + df["log_q_Occ"].to_numpy()))
    rec_diff = np.abs(df["log_prior"].to_numpy() - recon)
    rep["max_abs_reconstruction"] = float(rec_diff.max())
    rep["n_rows_reconstruction_gt_1e_8"] = int((rec_diff > 1e-8).sum())
    return rep

def _prior_invariants_couples(df):
    rep = {}
    p = df["prior"].to_numpy()
    lp = df["log_prior"].to_numpy()
    rep["n_rows"] = int(len(p))
    rep["min_prior"] = float(p.min())
    rep["n_prior_le_0"] = int((p <= 0).sum())
    rep["n_prior_nan"] = int(np.isnan(p).sum())
    mask = (p > 0) & np.isfinite(p) & np.isfinite(lp)
    diff = np.abs(np.log(p[mask]) - lp[mask])
    rep["max_abs_log_diff"] = float(diff.max())
    rep["n_rows_log_diff_gt_1e_8"] = int((diff > 1e-8).sum())
    wm = (df["working_male"] == 1).astype(float).to_numpy()
    wf = (df["working_female"] == 1).astype(float).to_numpy()
    recon = (
        df["log_q_E_male"].to_numpy()
        + wm * (df["log_q_H_male"].to_numpy() + df["log_q_W_male"].to_numpy() + df["log_q_Occ_male"].to_numpy())
        + df["log_q_E_female"].to_numpy()
        + wf * (df["log_q_H_female"].to_numpy() + df["log_q_W_female"].to_numpy() + df["log_q_Occ_female"].to_numpy())
    )
    rec_diff = np.abs(df["log_prior"].to_numpy() - recon)
    rep["max_abs_reconstruction"] = float(rec_diff.max())
    rep["n_rows_reconstruction_gt_1e_8"] = int((rec_diff > 1e-8).sum())
    return rep

out["prior_singles"] = _prior_invariants_singles(s)
out["prior_couples"] = _prior_invariants_couples(c)

# ---- Non-work gating
def _nonwork_gate(df, work_col, occ_col, loc_col):
    rep = {}
    nw = df[df[work_col] == 0] if work_col in df.columns else df
    rep["n_nonwork_rows"] = int(len(nw))
    if occ_col in df.columns:
        v = nw[occ_col].to_numpy()
        rep["log_q_Occ_nonwork_max_abs"] = float(np.abs(v).max() if len(v) else 0.0)
        rep["log_q_Occ_nonwork_n_nonzero"] = int((v != 0).sum())
    if loc_col in df.columns:
        rep["loc4_unique_values_nonwork"] = sorted(nw[loc_col].unique().astype(int).tolist())[:10]
    return rep

out["nonwork_singles"] = _nonwork_gate(s, "working", "log_q_Occ", "loc4")
out["nonwork_couples_male"] = _nonwork_gate(c, "working_male", "log_q_Occ_male", "loc4_male")
out["nonwork_couples_female"] = _nonwork_gate(c, "working_female", "log_q_Occ_female", "loc4_female")

# ---- Forbidden columns
FORBIDDEN = ["lindi", "industry", "nace", "job_id", "type_id", "log_q_job", "log_q_total", "log_q_state"]
def _forbidden(df):
    return [c for c in FORBIDDEN if c in df.columns or any(col == c for col in df.columns)]
out["forbidden_singles"] = _forbidden(s)
out["forbidden_couples"] = _forbidden(c)
# Also check suffixed variants for couples
extra_couples = [col for col in c.columns if any(col.startswith(f + "_male") or col.startswith(f + "_female") or col == f for f in FORBIDDEN)]
out["forbidden_couples_with_suffix"] = sorted(set(extra_couples))

with open(r"U:/Desktop/Nizam_Hisham/MNL/Results/_validation_stijn_occ_M0.json", "w") as f:
    json.dump(out, f, indent=2, default=str)
print("Saved validation JSON.")
print(json.dumps({k: v for k, v in out.items() if k in
    ("required_singles_missing", "required_couples_missing",
     "dummies_singles_present", "dummies_couples_present",
     "forbidden_singles", "forbidden_couples")},
    indent=2))
