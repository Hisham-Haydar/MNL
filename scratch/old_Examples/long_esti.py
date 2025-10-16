#%% 
import numpy as np
import pandas as pd
from scipy.optimize import minimize ,approx_fprime,differential_evolution
from scipy.special import logsumexp

df = pd.read_pickle('spanishdata.pickle')

#%% 
# Utility function
def utility(params, log_y, log_l, log_y2, log_l2, logyl):
    alpha, beta, gamma_yy, gamma_ll, gamma_yl = params[:5]
    return alpha * log_y + beta * log_l + gamma_yy * log_y2 + gamma_ll * log_l2 + gamma_yl * logyl

# Individual likelihood function
def ind_likelihood(params, utilities, choices):
    log_prob_chosen = np.where(choices == 1, utilities, -np.inf)
    log_prob_chosen = log_prob_chosen[np.isfinite(log_prob_chosen)]
    if log_prob_chosen.size > 0:
        chosen_utility = log_prob_chosen[0]
        log_prob_chosen = chosen_utility - logsumexp(utilities)
        return -log_prob_chosen  # Negative log likelihood
    else:
        return 0

# Total likelihood function
def total_likelihood(params, df):
    log_y = df['logy'].values
    log_l = df['logl'].values
    log_y2 = df['logy2'].values
    log_l2 = df['logl2'].values
    logyl = df['logyl'].values
    utilities = utility(params, log_y, log_l, log_y2, log_l2, logyl)
    ids = df['idperson'].values
    choices = df['choice_made'].values
    
    unique_ids = np.unique(ids)
    total_ll = 0
    for uid in unique_ids:
        mask = ids == uid
        total_ll += ind_likelihood(params, utilities[mask], choices[mask])
    return total_ll

#%% 

# Jacobian function
def jacobian(params, df):
    epsilon = np.sqrt(np.finfo(float).eps)
    grad = approx_fprime(params, lambda p: total_likelihood(p, df), epsilon)
    return grad

# Initial guess for parameters
initial_params = [11.64077 , 56.65185, -.5632375 , -7.120488  ,-.446051  ]

# Optimization
result = minimize(fun=total_likelihood, x0=initial_params, args=(df,), method='Newton-CG', jac=jacobian)

print(f'Optimization result Translog cleaned data: {result}')

#%% 

# Initial guess for parameters
# Initial guess for parameters
initial_params = [11.64077 , 56.65185, -.5632375 , -7.120488  ,-.446051  ]

# Optimization
result = minimize(fun=total_likelihood, x0=initial_params, args=(df,), method='Newton-CG', jac=jacobian)

print(f'Optimization result Translog cleaned data: {result}')

# %%
# Utility function
def utility(params, log_y, log_l, log_y2, log_l2, logyl):
    alpha, beta, gamma_yy, gamma_ll, gamma_yl = params[:5]
    return alpha * log_y + beta * log_l + gamma_yy * log_y2 + gamma_ll * log_l2 + gamma_yl * logyl

# Individual likelihood function
def ind_likelihood(params, utilities, choices):
    log_prob_chosen = np.where(choices == 1, utilities, -np.inf)
    log_prob_chosen = log_prob_chosen[np.isfinite(log_prob_chosen)]
    if log_prob_chosen.size > 0:
        chosen_utility = log_prob_chosen[0]
        log_prob_chosen = chosen_utility - logsumexp(utilities)
        return -log_prob_chosen  # Negative log likelihood
    else:
        return 0

# Total likelihood function
def total_likelihood(params, df):
    log_y = df['logy'].values
    log_l = df['logl'].values
    log_y2 = df['logy2'].values
    log_l2 = df['logl2'].values
    logyl = df['logyl'].values
    utilities = utility(params, log_y, log_l, log_y2, log_l2, logyl)
    ids = df['idperson'].values
    choices = df['choice_made'].values
    
    unique_ids = np.unique(ids)
    total_ll = 0
    for uid in unique_ids:
        mask = ids == uid
        total_ll += ind_likelihood(params, utilities[mask], choices[mask])
    
    return total_ll

# Jacobian function
def jacobian(params, df):
    epsilon = np.sqrt(np.finfo(float).eps)
    grad = approx_fprime(params, lambda p: total_likelihood(p, df), epsilon)
    return grad

# Bounds for parameters (assuming some reasonable bounds, adjust as necessary)
bounds = [
    (0, 30),   # alpha
    (0, 100),  # beta
    (-10, 10), # gamma_yy
    (-20, 0),  # gamma_ll
    (-5, 5)    # gamma_yl
]

# Global optimization using differential evolution
result = differential_evolution(func=total_likelihood, bounds=bounds, args=(df,), strategy='best1bin', maxiter=1000, tol=1e-7)

print(f'Optimization result Translog cleaned data: {result}')

# If needed, further local optimization using the result from global optimization as initial point
local_result = minimize(fun=total_likelihood, x0=result.x, args=(df,), method='Newton-CG', jac=jacobian)

print(f'Local optimization result Translog cleaned data: {local_result}')

