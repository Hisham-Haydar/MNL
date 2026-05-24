"""Bisect the LL discrepancy between NumPy prototype and CONOPT oracle."""
import sys, json, math, pickle
import numpy as np
sys.path.insert(0, 'scripts/enhanced')

with open('Data/pilot/nc_2016_couples/precomputed/fr_pilot_nc_2016_couples_precomputed_loc.pkl','rb') as f:
    pc = pickle.load(f)
with open('Results/pilot/nc_2016_couples/diagnostic_rerun_v1/start_1_warm_P3a/estimation_result.json') as f:
    r1 = json.load(f)
p = r1['parameters']

N, J = pc.n_groups, pc.n_obs // pc.n_groups
EPS = 1e-12
ORACLE = -16527.14218317334

def R(a): return a.reshape(N, J)
def bc(x, theta):
    log_x = np.log(np.maximum(x, EPS))
    if abs(theta) < 1e-10: return log_x
    return (np.exp(theta * log_x) - 1.0) / theta
def ll(u):
    chosen = R(pc.actual_choice)
    u_max = u.max(axis=1, keepdims=True)
    log_d = np.log(np.exp(u - u_max).sum(axis=1)) + u_max.squeeze()
    return float(((chosen * u).sum(axis=1) - log_d).sum())

consumption = R(pc.consumption); leisure_m = R(pc.leisure_male); leisure_f = R(pc.leisure_female)
prior = R(pc.prior); working_m = R(pc.working_male); working_f = R(pc.working_female)
log_wage_m = R(pc.log_wage_male); log_wage_f = R(pc.log_wage_female)
age_m = R(pc.age_norm_male); age2_m = R(pc.age_norm2_male)
age_f = R(pc.age_norm_female); age2_f = R(pc.age_norm2_female)
n_kids = R(pc.n_children)
gsur_m = R(pc.gsur_male); gsur_f = R(pc.gsur_female)
reg2=R(pc.reg2); reg3=R(pc.reg3); reg4=R(pc.reg4)
reg5=R(pc.reg5); reg6=R(pc.reg6); reg7=R(pc.reg7); reg8=R(pc.reg8)
loc4_2_m=R(pc.loc4_2_male); loc4_3_m=R(pc.loc4_3_male); loc4_4_m=R(pc.loc4_4_male)
loc4_2_f=R(pc.loc4_2_female); loc4_3_f=R(pc.loc4_3_female); loc4_4_f=R(pc.loc4_4_female)
educL_m=R(pc.educL_male); educH_m=R(pc.educH_male); pexp_m=R(pc.pexp_years_male); pexp2_m=R(pc.pexp_years2_male)
educL_f=R(pc.educL_female); educH_f=R(pc.educH_female); pexp_f=R(pc.pexp_years_female); pexp2_f=R(pc.pexp_years2_female)
wpt1_m=R(pc.working_pt1_male); wpt2_m=R(pc.working_pt2_male); wft_m=R(pc.working_ft_male)
wpt1_f=R(pc.working_pt1_female); wpt2_f=R(pc.working_pt2_female); wft_f=R(pc.working_ft_female)

bc_c   = np.log(consumption + EPS)
bc_l_m = bc(leisure_m, p['theta_l_m'])
bc_l_f = bc(leisure_f, p['theta_l_f'])
coeff_l_m = p['beta_l0_m'] + p['beta_l_age_m']*age_m + p['beta_l_age2_m']*age2_m
coeff_l_f = (p['beta_l0_f'] + p['beta_l_age_f']*age_f + p['beta_l_age2_f']*age2_f
             + p['beta_l_nkids_f']*n_kids)
u_pref = p['beta_c']*bc_c + coeff_l_m*bc_l_m + coeff_l_f*bc_l_f + p['beta_ll']*bc_l_m*bc_l_f

log_h_m = (p['beta_E']*working_m + p['beta_h_pt1']*wpt1_m*working_m
         + p['beta_h_pt2']*wpt2_m*working_m + p['beta_h_ft']*wft_m*working_m)
log_h_f = (p['beta_E']*working_f + p['beta_h_pt1']*wpt1_f*working_f
         + p['beta_h_pt2']*wpt2_f*working_f + p['beta_h_ft']*wft_f*working_f)

sigma = p['sigma']
mu_m = p['beta_w0'] + p['beta_w_educL']*educL_m + p['beta_w_educH']*educH_m + p['beta_w_pexp']*pexp_m + p['beta_w_pexp2']*pexp2_m
mu_f = p['beta_w0'] + p['beta_w_educL']*educL_f + p['beta_w_educH']*educH_f + p['beta_w_pexp']*pexp_f + p['beta_w_pexp2']*pexp2_f
log_w_m = working_m*(-0.5*(log_wage_m-mu_m)**2/(sigma**2+EPS) - np.log(sigma+EPS) - 0.5*math.log(2*math.pi) - log_wage_m)
log_w_f = working_f*(-0.5*(log_wage_f-mu_f)**2/(sigma**2+EPS) - np.log(sigma+EPS) - 0.5*math.log(2*math.pi) - log_wage_f)

log_market = p['beta_E_gsur']*gsur_m*working_m*10.0 + p['beta_E_gsur']*gsur_f*working_f*10.0
w_hh = working_m + working_f
for coef, reg in [('beta_E_drgn2',reg2),('beta_E_drgn3',reg3),('beta_E_drgn4',reg4),
                  ('beta_E_drgn5',reg5),('beta_E_drgn6',reg6),('beta_E_drgn7',reg7),('beta_E_drgn8',reg8)]:
    log_market = log_market + p[coef]*reg*w_hh
log_market = (log_market
            + p['beta_occ_2_cm']*loc4_2_m*working_m + p['beta_occ_3_cm']*loc4_3_m*working_m
            + p['beta_occ_4_cm']*loc4_4_m*working_m + p['beta_occ_2_cf']*loc4_2_f*working_f
            + p['beta_occ_3_cf']*loc4_3_f*working_f + p['beta_occ_4_cf']*loc4_4_f*working_f)

prior_sum = prior.sum(axis=1, keepdims=True) + EPS
center    = (prior * log_market).sum(axis=1, keepdims=True) / prior_sum
log_market_c = log_market - center
log_prior = np.log(prior + EPS)

utility = u_pref + log_h_m + log_h_f + log_w_m + log_w_f + log_market_c - log_prior

print(f"Full LL = {ll(utility):.8f}  delta = {ll(utility)-ORACLE:+.6f}")
print()

# Bisect
print("--- Bisection ---")
tests = [
    ("No -log_prior",         u_pref + log_h_m + log_h_f + log_w_m + log_w_f + log_market_c),
    ("No centering",          u_pref + log_h_m + log_h_f + log_w_m + log_w_f + log_market - log_prior),
    ("No hours",              u_pref + log_w_m + log_w_f + log_market_c - log_prior),
    ("No wage",               u_pref + log_h_m + log_h_f + log_market_c - log_prior),
    ("No market",             u_pref + log_h_m + log_h_f + log_w_m + log_w_f - log_prior),
    ("Pref+prior only",       u_pref - log_prior),
]
for name, u in tests:
    v = ll(u)
    print(f"  {name:30s}: LL={v:.6f}  delta={v-ORACLE:+.6f}")

print()
# Key question: is the centering truly proposal-weighted?
# GAMSPy: denom = Sum(j_alias, prior[i,k]) + EPS
#          center = Sum(j_alias, prior[i,k] * log_market[i,k]) / denom
# Our numpy: prior.sum(axis=1) + EPS as denom -> sum of prior across all J alternatives
# prior sum per group mean is 0.093352 (not 1!) since prior = proposal/N draw weights
# Check if centering denom should be sum(prior) or 1.0
print(f"prior sum per group mean: {prior.sum(axis=1).mean():.6f}")
print(f"prior sum per group range: {prior.sum(axis=1).min():.6f} .. {prior.sum(axis=1).max():.6f}")
print()

# GAMSPy centering: exactly as coded, using sum of prior as denom
# Our implementation matches. Let me check if uniform centering changes anything:
center_uniform = log_market.mean(axis=1, keepdims=True)
log_market_c_uniform = log_market - center_uniform
u_uniform_center = u_pref + log_h_m + log_h_f + log_w_m + log_w_f + log_market_c_uniform - log_prior
print(f"  Uniform centering:             LL={ll(u_uniform_center):.6f}  delta={ll(u_uniform_center)-ORACLE:+.6f}")

# What if we DON'T add EPS to denominator in centering?
prior_sum2 = prior.sum(axis=1, keepdims=True)
center2    = (prior * log_market).sum(axis=1, keepdims=True) / prior_sum2
u_noEPS = u_pref + log_h_m + log_h_f + log_w_m + log_w_f + (log_market - center2) - log_prior
print(f"  Centering no-EPS in denom:     LL={ll(u_noEPS):.6f}  delta={ll(u_noEPS)-ORACLE:+.6f}")

# What if hours_opportunity has NO interaction with working?
# (var_param_m is NOT multiplied by working_m again, just used as-is)
log_h_m_raw = p['beta_E']*working_m + p['beta_h_pt1']*wpt1_m + p['beta_h_pt2']*wpt2_m + p['beta_h_ft']*wft_m
log_h_f_raw = p['beta_E']*working_f + p['beta_h_pt1']*wpt1_f + p['beta_h_pt2']*wpt2_f + p['beta_h_ft']*wft_f
u_rawH = u_pref + log_h_m_raw + log_h_f_raw + log_w_m + log_w_f + log_market_c - log_prior
print(f"  Hours no working*working mult: LL={ll(u_rawH):.6f}  delta={ll(u_rawH)-ORACLE:+.6f}")

# Sanity: what are wpt1_m, wpt2_m, wft_m values?
print()
print(f"working_m mean: {working_m.mean():.4f}")
print(f"wpt1_m mean: {wpt1_m.mean():.4f}")
print(f"wpt2_m mean: {wpt2_m.mean():.4f}")
print(f"wft_m mean: {wft_m.mean():.4f}")
print(f"wpt1_m*working_m == wpt1_m? {np.allclose(wpt1_m*working_m, wpt1_m)}")
print()

# The GSUR scale: spec says scale=10.0 -> var_param = gsur * 10.0
# The GSUR interaction: interaction=['working']
# So: beta_E_gsur * (gsur * 10.0) * working_m  [for male]
# BUT: applies_to='both' -> both male and female add their own terms
# My impl: beta_E_gsur * gsur_m * working_m * 10 + beta_E_gsur * gsur_f * working_f * 10
# Check: is gsur_male the same array for both male and female, or truly gender-specific?
print(f"gsur_male mean: {gsur_m.mean():.4f}, gsur_female mean: {gsur_f.mean():.4f}")
print(f"gsur_male == gsur_female: {np.allclose(gsur_m, gsur_f)}")

# What if gsur is household-level (same for both) and should be used once, not twice?
log_market_gsur1 = (p['beta_E_gsur']*gsur_m*(working_m+working_f)*10.0)  # household-level, once
w_hh2 = working_m + working_f
lm2 = log_market_gsur1.copy()
for coef, reg in [('beta_E_drgn2',reg2),('beta_E_drgn3',reg3),('beta_E_drgn4',reg4),
                  ('beta_E_drgn5',reg5),('beta_E_drgn6',reg6),('beta_E_drgn7',reg7),('beta_E_drgn8',reg8)]:
    lm2 = lm2 + p[coef]*reg*w_hh2
lm2 = (lm2 + p['beta_occ_2_cm']*loc4_2_m*working_m + p['beta_occ_3_cm']*loc4_3_m*working_m
      + p['beta_occ_4_cm']*loc4_4_m*working_m + p['beta_occ_2_cf']*loc4_2_f*working_f
      + p['beta_occ_3_cf']*loc4_3_f*working_f + p['beta_occ_4_cf']*loc4_4_f*working_f)
center_lm2 = (prior * lm2).sum(axis=1, keepdims=True) / prior_sum
u_gsur1 = u_pref + log_h_m + log_h_f + log_w_m + log_w_f + (lm2 - center_lm2) - log_prior
print(f"  GSUR once (household-level):   LL={ll(u_gsur1):.6f}  delta={ll(u_gsur1)-ORACLE:+.6f}")
