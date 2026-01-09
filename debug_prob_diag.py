"""Debug script for probability diagnostics."""
import pandas as pd
import numpy as np
import json

# Load data and params
df = pd.read_parquet('U:/EUROMOD-STORAGE/Data/processed/fr/2016/fr_2016_RURO_mnl__singles.parquet')
with open('outputs/estimates/fr/2016/estimation_results.json') as f:
    results = json.load(f)

params = results['results']['joint']['parameters']

# Get SM params (keep full names with _sm suffix)
sm_params = {k: v for k, v in params.items() if k.endswith('_sm') or not any(k.endswith(s) for s in ['_sf', '_m', '_f'])}
print('SM params available:', list(sm_params.keys())[:10])

def bc(x, theta):
    if abs(theta) < 1e-10:
        return np.log(np.maximum(x, 1e-10))
    else:
        return (np.power(np.maximum(x, 1e-10), theta) - 1) / theta

def compute_beta_l_with_suffix(df, params, suffix='_sm'):
    """Compute full beta_l including all shifters."""
    n = len(df)
    beta_l0 = params.get(f'beta_l0{suffix}', 0.0)
    beta_l = np.full(n, beta_l0)
    
    # Check for age_norm
    age_key = f'beta_l_age_norm{suffix}'
    if age_key in params and 'age_norm' in df.columns:
        beta_l += params[age_key] * df['age_norm'].values
        
    age2_key = f'beta_l_age_norm2{suffix}'
    if age2_key in params and 'age_norm2' in df.columns:
        beta_l += params[age2_key] * df['age_norm2'].values
        
    educL_key = f'beta_l_educL{suffix}'
    if educL_key in params and 'educL' in df.columns:
        beta_l += params[educL_key] * df['educL'].values
        
    educH_key = f'beta_l_educH{suffix}'
    if educH_key in params and 'educH' in df.columns:
        beta_l += params[educH_key] * df['educH'].values
    
    return beta_l

beta_c = sm_params.get('beta_c_sm', sm_params.get('beta_c', 1.0))
theta_c = sm_params.get('theta_c_sm', sm_params.get('theta_c', 0.5))
theta_l = sm_params.get('theta_l_sm', sm_params.get('theta_l', 0.0))

print(f'Using: beta_c={beta_c:.4f}, theta_c={theta_c:.4f}, theta_l={theta_l:.4f}')

df_sm = df[df['dgn'] == 1].copy()
print(f'Columns available: {[c for c in df_sm.columns if "age" in c or "educ" in c]}')

sample_hh = df_sm['idhh'].iloc[0]
sample = df_sm[df_sm['idhh'] == sample_hh].copy()

c = sample['consumption'].values
l = sample['leisure'].values
log_q = sample['log_q_total'].values
prior = sample['prior'].values
is_chosen = sample['is_chosen'].values

# Compute beta_l with shifters
beta_l = compute_beta_l_with_suffix(sample, sm_params, '_sm')
print(f'beta_l range: {beta_l.min():.4f} to {beta_l.max():.4f}')

# Compute V correctly
V = beta_c * bc(c, theta_c) + beta_l * bc(l, theta_l) + log_q - prior
print(f'V range: {V.min():.2f} to {V.max():.2f}')

# Compute probs
V_shifted = V - V.max()
exp_V = np.exp(V_shifted)
probs = exp_V / exp_V.sum()
print(f'Probs: min={probs.min():.6f}, max={probs.max():.6f}, sum={probs.sum():.6f}')

chosen_mask = is_chosen == 1
if chosen_mask.any():
    p_chosen = probs[chosen_mask][0]
    v_chosen = V[chosen_mask][0]
    print(f'V_chosen = {v_chosen:.2f}, V_max = {V.max():.2f}, diff = {V.max() - v_chosen:.2f}')
    print(f'P(chosen) = {p_chosen:.6f}')

# Test more households
print('\n--- Testing 10 households ---')
all_p_chosen = []
for i, hh in enumerate(df_sm['idhh'].unique()[:10]):
    hh_data = df_sm[df_sm['idhh'] == hh].copy()
    c = hh_data['consumption'].values
    l = hh_data['leisure'].values
    log_q = hh_data['log_q_total'].values
    prior = hh_data['prior'].values
    
    beta_l = compute_beta_l_with_suffix(hh_data, sm_params, '_sm')
    V = beta_c * bc(c, theta_c) + beta_l * bc(l, theta_l) + log_q - prior
    V_shifted = V - V.max()
    exp_V = np.exp(V_shifted)
    probs = exp_V / exp_V.sum()
    
    chosen_mask = hh_data['is_chosen'].values == 1
    if chosen_mask.any():
        p_chosen = probs[chosen_mask][0]
        all_p_chosen.append(p_chosen)
        print(f'HH {int(hh)}: P(chosen)={p_chosen:.4f}')

print(f'\nMean P(chosen) over 10 HH: {np.mean(all_p_chosen):.4f}')
