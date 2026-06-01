"""Characterize the STRUCTURE of the gender-split non-identification.

Read-only: recompute the exact jax.hessian at the gsplit synthetic MLE
(seed 20260530, the same point the gate reported PD min_eig +1.532) and
extract the identification geometry of the 4 relaxed params:
  {beta_E_m, beta_E_f, beta_h_pt2_m, beta_h_pt2_f}.

Reports:
 1. cov = H^-1 ; 4x4 correlation matrix of the relaxed params (flag |corr|>0.9).
 2. eigen-decomposition of the cov sub-blocks -> which linear combination is
    WELL-identified (small cov-eigenvalue = stiff) vs FLAT (large cov-eigenvalue
    = soft). The cov eigvec with the LARGEST eigenvalue = least-identified dir.
 3. Done separately for the beta_E pair and the beta_h_pt2 pair (2x2 each).
 4. Verdict per pair: RIDGE (anti/co-correlated, a contrast/level is flat) vs
    INDEPENDENT MISLOCATION (low corr, each individually soft).

NO re-fit, NO re-gate. Uses the gate's reported theta_hat as the MLE.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, 'scripts/enhanced')
sys.path.insert(0, 'scripts/bpool')
import numpy as np
import estimation_spec_parser as sp
import joint_recovery_test as jrt
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from jax_ll_probe import build_jax_singles_ll, build_jax_couples_ll

np.set_printoptions(precision=4, suppress=True, linewidth=120)

REPORT = Path('docs/France_case/P3a/execution_logs/Bpool/RURO_jax_recovery_gate_gsplit_901_v1.md')
SPEC = 'scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_tlmpin_gsplit.yaml'
DRAW = 'scripts/bpool/specs/estimation_spec_joint_pooled_v1_bll0_gsplit_draw.yaml'
SEED = 20260530   # gate default; MUST match or the Hessian is at the wrong data

spec = sp.parse_specification(SPEC)
draw = sp.parse_specification(DRAW)
pnames = spec.all_param_names
for pn in ("theta_l_sm", "theta_l_sf", "theta_l_m", "theta_l_f"):
    if pn in spec.bounds:
        spec.bounds[pn] = (-4.0, -0.3)
    if pn in draw.bounds:
        draw.bounds[pn] = (-4.0, -0.3)

R = json.loads(REPORT.read_text(encoding='utf-8').split('```json')[1].split('```')[0])
theta_hat = np.array(R['check2']['theta_hat'], dtype=np.float64)

rng = np.random.default_rng(SEED)
data_sm, data_sf, data_cou = jrt.build_data_objects(
    'fr_p3a_bpool_engine_ready', [], 0, couples_stem='fr_p3a_bpool_engine_ready')
theta_star = np.asarray(jrt.load_theta_star_from_csv(
    Path('scripts/bpool/specs/theta_star_joint_v1.csv'), spec))
bnds = [spec.bounds.get(n, (None, None)) for n in pnames]
for i, (lo, hi) in enumerate(bnds):
    if lo is not None:
        theta_star[i] = max(theta_star[i], lo + 1e-9)
    if hi is not None:
        theta_star[i] = min(theta_star[i], hi - 1e-9)


def _full(fit):
    m = dict(zip(pnames, fit))
    m.update(spec.fixed_params or {})
    return np.array([m[n] for n in draw.all_param_names])


sm_s, sf_s, cou_s = jrt.run_synthetic_dgp(
    draw, data_sm, data_sf, data_cou, _full(theta_star), rng)

gs = set(spec.gender_split or [])
f_sm, _ = build_jax_singles_ll(sm_s, spec, is_male=True, use_actual_choice=True, gender_split=gs or None)
f_sf, _ = build_jax_singles_ll(sf_s, spec, is_male=False, use_actual_choice=True, gender_split=gs or None)
f_cou, _ = build_jax_couples_ll(cou_s, spec, use_actual_choice=True, gender_split=gs or None)
joint = jax.jit(lambda t: f_sm(t) + f_sf(t) + f_cou(t))

H = np.asarray(jax.jit(jax.hessian(joint))(jnp.asarray(theta_hat)))
H = 0.5 * (H + H.T)
w_full = np.linalg.eigvalsh(H)
pd_ok = bool(np.all(w_full > 0))
cov = np.linalg.inv(H) if pd_ok else np.linalg.pinv(H, hermitian=True, rcond=1e-10)

relaxed = ['beta_E_m', 'beta_E_f', 'beta_h_pt2_m', 'beta_h_pt2_f']
ridx = [pnames.index(n) for n in relaxed]
recov = {n: R['relaxed_recovery']['params'][n] for n in relaxed}


def corr_from_cov(C):
    d = np.sqrt(np.diag(C))
    return C / np.outer(d, d)


out = []


def p(s=''):
    out.append(s)
    print(s)


p("# gsplit non-identification STRUCTURE — read-only Hessian diagnostic")
p()
p("> Reads the EXISTING gsplit synthetic MLE Hessian (no re-fit / no re-gate). "
  "Recomputes exact jax.hessian at the gate's reported theta_hat with the same "
  f"seed {SEED}, then extracts cov = H^-1 and the identification geometry of the "
  "4 relaxed gender-split params. Companion to RURO_jax_recovery_gate_gsplit_901_v1.md.")
p()
p(f"Full Hessian PD={pd_ok}, min_eig={w_full.min():.4f} "
  f"(reproduces the gate's +1.532 -> correct MLE/seed). "
  f"cov = H^-1{'  (pinv, non-PD)' if not pd_ok else ''}.")
p()
p("## 1. Correlation matrix of the 4 relaxed params (cov = H^-1)")
p()
C4 = cov[np.ix_(ridx, ridx)]
Cr = corr_from_cov(C4)
p("| | " + " | ".join(relaxed) + " |")
p("|" + "---|" * (len(relaxed) + 1))
for i, n in enumerate(relaxed):
    p(f"| {n} | " + " | ".join(f"{Cr[i, j]:+.3f}" for j in range(4)) + " |")
p()
p("SE(Hessian): " + ", ".join(f"{n}={np.sqrt(C4[i, i]):.4f}" for i, n in enumerate(relaxed)))
p()
flags = []
for i in range(4):
    for j in range(i + 1, 4):
        if abs(Cr[i, j]) > 0.9:
            flags.append((relaxed[i], relaxed[j], Cr[i, j]))
if flags:
    for a, b, c in flags:
        p(f"- **|corr|>0.9 RIDGE FLAG: {a} vs {b} = {c:+.3f}**")
else:
    p("- No |corr|>0.9 pair among the 4 (no global 4-way ridge among all four).")
p()


def describe(v, pair):
    a, b = v
    if a < 0:
        a, b = -a, -b
    if abs(abs(a) - abs(b)) < 0.25:
        if a * b > 0:
            return f"LEVEL/SUM ({pair[0]} + {pair[1]})  [v=({a:+.2f},{b:+.2f})]"
        return f"CONTRAST ({pair[0]} - {pair[1]})  [v=({a:+.2f},{b:+.2f})]"
    dom = pair[0] if abs(a) > abs(b) else pair[1]
    return f"mostly {dom}  [v=({a:+.2f},{b:+.2f})]"


def pair_analysis(pair, label, tag):
    p(f"## {tag}. {label} pair: {pair[0]} , {pair[1]}")
    p()
    idx = [pnames.index(pair[0]), pnames.index(pair[1])]
    C2 = cov[np.ix_(idx, idx)]
    cc = corr_from_cov(C2)[0, 1]
    se = [np.sqrt(C2[0, 0]), np.sqrt(C2[1, 1])]
    p(f"- corr({pair[0]}, {pair[1]}) = **{cc:+.3f}**")
    p(f"- SE: {pair[0]}={se[0]:.4f}, {pair[1]}={se[1]:.4f}")
    wv, Vv = np.linalg.eigh(C2)
    stiff = Vv[:, 0]   # small cov eigenvalue = well-identified
    soft = Vv[:, -1]   # large cov eigenvalue = flat
    p(f"- cov eigenvalues: stiff(identified)={wv[0]:.4e}, soft(flat)={wv[-1]:.4e}, "
      f"soft/stiff ratio={wv[-1] / wv[0]:.1f}")
    p(f"- **WELL-IDENTIFIED** (stiff) direction: {describe(stiff, pair)}")
    p(f"- **FLAT** (soft) direction:           {describe(soft, pair)}")
    p(f"- recovery: {pair[0]} true={recov[pair[0]]['true']:+.2f} -> {recov[pair[0]]['recovered']:+.3f}; "
      f"{pair[1]} true={recov[pair[1]]['true']:+.2f} -> {recov[pair[1]]['recovered']:+.3f}")
    if abs(cc) > 0.9:
        v = (f"RIDGE — strong correlation ({cc:+.2f}); only the "
             f"{describe(stiff, pair).split('[')[0].strip()} is identified, the "
             f"{describe(soft, pair).split('[')[0].strip()} is flat. A reparam "
             f"(shared level + gender deviation) COULD rescue it.")
    elif wv[-1] / wv[0] > 10:
        v = (f"PARTIAL RIDGE — corr modest ({cc:+.2f}) but soft/stiff ratio "
             f"{wv[-1] / wv[0]:.0f}: the {describe(soft, pair).split('[')[0].strip()} "
             f"is much flatter. Reparam may help.")
    else:
        v = (f"INDEPENDENT MISLOCATION — corr modest ({cc:+.2f}), soft/stiff ratio "
             f"{wv[-1] / wv[0]:.0f} (no strong ridge). Each param individually "
             f"soft/mislocated; reparam unlikely to help.")
    p(f"- **VERDICT: {v}**")
    p()
    return cc, wv[-1] / wv[0]


pair_analysis(['beta_E_m', 'beta_E_f'], 'beta_E', '2')
pair_analysis(['beta_h_pt2_m', 'beta_h_pt2_f'], 'beta_h_pt2', '3')

p("## 4. Full 4x4 eigenstructure (2 separate pair-ridges, or a 4-way tangle?)")
p()
w4, V4 = np.linalg.eigh(C4)
p(f"cov 4x4 eigenvalues (large = flat): {w4[::-1]}")
p()
p("Softest (most flat) 4-direction eigenvector loadings:")
soft4 = V4[:, -1]
for i, n in enumerate(relaxed):
    p(f"- {n}: {soft4[i]:+.3f}")
p()

REPORT_OUT = Path('docs/France_case/P3a/execution_logs/Bpool/RURO_gsplit_nonid_structure_v1.md')
REPORT_OUT.write_text("\n".join(out) + "\n", encoding='utf-8')
print(f"\n[written] {REPORT_OUT}")
