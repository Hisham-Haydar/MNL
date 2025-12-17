"""Fix compute_beta_leisure_at_median and utility computation functions."""
import re

# Read file
with open('RURO_post_estimation.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes_made = 0

# 1. Fix the docstrings for compute_beta_leisure_at_median (2 occurrences)
old_docstring = '''    Compute β_l(X) at median/mode covariate values.
    
    β_l(X) = β_l0 + β_l_log_age * log(age) + β_l_log_age2 * log(age)²
             + β_l_ch0_3 * ch0_3 + β_l_ch4_6 * ch4_6 + β_l_ch7_9 * ch7_9
             + β_l_educL * educL + β_l_educH * educH
             + β_l_reg2 * reg2 + ...'''

new_docstring = '''    Compute β_l(X) at median/mode covariate values.
    
    β_l(X) = β_l0 + β_l_age_norm * age_norm + β_l_age_norm2 * age_norm²
             + β_l_n_children * n_children
             (or legacy: β_l_log_age, β_l_ch0_3, etc.)'''

count_doc = content.count(old_docstring)
print(f'Found {count_doc} docstring occurrences')
if count_doc > 0:
    content = content.replace(old_docstring, new_docstring)
    changes_made += count_doc

# 2. Fix the age/children effects block in compute_beta_leisure_at_median (2 occurrences)
old_age = '''    # Age effects
    log_age = median_shifters.get("log_age", np.log(40))
    log_age2 = median_shifters.get("log_age2", log_age ** 2)
    beta_l += group_params.get("beta_l_log_age", 0.0) * log_age
    beta_l += group_params.get("beta_l_log_age2", 0.0) * log_age2
    
    # Children effects
    beta_l += group_params.get("beta_l_ch0_3", 0.0) * median_shifters.get("children0_3", 0.0)
    beta_l += group_params.get("beta_l_ch4_6", 0.0) * median_shifters.get("children4_6", 0.0)
    beta_l += group_params.get("beta_l_ch7_9", 0.0) * median_shifters.get("children7_9", 0.0)'''

new_age = '''    # Age effects (simplified model uses normalized age)
    age_norm = median_shifters.get("age_norm", 0.0)
    age_norm2 = median_shifters.get("age_norm2", age_norm ** 2)
    beta_l += group_params.get("beta_l_age_norm", 0.0) * age_norm
    beta_l += group_params.get("beta_l_age_norm2", 0.0) * age_norm2
    
    # Legacy age effects (for backward compatibility)
    log_age = median_shifters.get("log_age", np.log(40))
    log_age2 = median_shifters.get("log_age2", log_age ** 2)
    beta_l += group_params.get("beta_l_log_age", 0.0) * log_age
    beta_l += group_params.get("beta_l_log_age2", 0.0) * log_age2
    
    # Children effects (simplified model uses n_children)
    beta_l += group_params.get("beta_l_n_children", 0.0) * median_shifters.get("n_children", 0.0)
    
    # Legacy children effects (for backward compatibility)
    beta_l += group_params.get("beta_l_ch0_3", 0.0) * median_shifters.get("children0_3", 0.0)
    beta_l += group_params.get("beta_l_ch4_6", 0.0) * median_shifters.get("children4_6", 0.0)
    beta_l += group_params.get("beta_l_ch7_9", 0.0) * median_shifters.get("children7_9", 0.0)'''

count_age = content.count(old_age)
print(f'Found {count_age} age effects block occurrences')
if count_age > 0:
    content = content.replace(old_age, new_age)
    changes_made += count_age

# 3. Fix parameter descriptions in default_desc dictionaries (2 occurrences)
old_desc = '''"beta_l0": "Base preference for leisure",
        "beta_l_log_age": "Effect of log(age) on leisure preference",
        "beta_l_log_age2": "Effect of log(age)² on leisure preference",
        "beta_l_ch0_3": "Effect of children 0-3 on leisure (females)",
        "beta_l_ch4_6": "Effect of children 4-6 on leisure",
        "beta_l_ch7_9": "Effect of children 7-9 on leisure",'''

new_desc = '''"beta_l0": "Base preference for leisure",
        "beta_l_age_norm": "Effect of normalized age on leisure preference",
        "beta_l_age_norm2": "Effect of normalized age² on leisure preference",
        "beta_l_n_children": "Effect of number of children on leisure",
        # Legacy parameters (for backward compatibility)
        "beta_l_log_age": "Effect of log(age) on leisure preference",
        "beta_l_log_age2": "Effect of log(age)² on leisure preference",
        "beta_l_ch0_3": "Effect of children 0-3 on leisure (females)",
        "beta_l_ch4_6": "Effect of children 4-6 on leisure",
        "beta_l_ch7_9": "Effect of children 7-9 on leisure",'''

count_desc = content.count(old_desc)
print(f'Found {count_desc} parameter description occurrences')
if count_desc > 0:
    content = content.replace(old_desc, new_desc)
    changes_made += count_desc

# 4. Fix CSV template example comments (2 occurrences)  
old_csv = '''        beta_l0,0.5,"Base leisure preference",-5,5
        beta_l_log_age,0.1,"Age effect on leisure",-2,2'''

new_csv = '''        beta_l0,0.5,"Base leisure preference",-5,5
        beta_l_age_norm,0.1,"Normalized age effect on leisure",-2,2'''

count_csv = content.count(old_csv)
print(f'Found {count_csv} CSV example occurrences')
if count_csv > 0:
    content = content.replace(old_csv, new_csv)
    changes_made += count_csv

# 5. Fix utility computation in obs_df section - add support for new param names
# This is the compute_choice_utilities section around line 2543
old_utility_age = '''        # Add shifters if available
        if "log_age" in obs_df.columns:
            beta_l_arr += params.get("beta_l_log_age", 0.0) * obs_df["log_age"].values
            beta_l_arr += params.get("beta_l_log_age2", 0.0) * obs_df["log_age"].values ** 2
        elif "dag" in obs_df.columns:
            log_age = np.log(np.clip(obs_df["dag"].values, 18, None))
            beta_l_arr += params.get("beta_l_log_age", 0.0) * log_age
            beta_l_arr += params.get("beta_l_log_age2", 0.0) * log_age ** 2
        
        # Children shifters
        for ch_col, param_key in [("dch0_3", "beta_l_ch0_3"), ("dch4_6", "beta_l_ch4_6"), ("dch7_9", "beta_l_ch7_9")]:
            if ch_col in obs_df.columns:
                beta_l_arr += params.get(param_key, 0.0) * obs_df[ch_col].values'''

new_utility_age = '''        # Add shifters if available
        # Simplified model uses age_norm, n_children
        if "age_norm" in obs_df.columns:
            beta_l_arr += params.get("beta_l_age_norm", 0.0) * obs_df["age_norm"].values
            beta_l_arr += params.get("beta_l_age_norm2", 0.0) * obs_df["age_norm"].values ** 2
        # Legacy: log_age
        if "log_age" in obs_df.columns:
            beta_l_arr += params.get("beta_l_log_age", 0.0) * obs_df["log_age"].values
            beta_l_arr += params.get("beta_l_log_age2", 0.0) * obs_df["log_age"].values ** 2
        elif "dag" in obs_df.columns:
            log_age = np.log(np.clip(obs_df["dag"].values, 18, None))
            beta_l_arr += params.get("beta_l_log_age", 0.0) * log_age
            beta_l_arr += params.get("beta_l_log_age2", 0.0) * log_age ** 2
        
        # Children shifters (simplified model)
        if "n_children" in obs_df.columns:
            beta_l_arr += params.get("beta_l_n_children", 0.0) * obs_df["n_children"].values
        
        # Legacy children shifters
        for ch_col, param_key in [("dch0_3", "beta_l_ch0_3"), ("dch4_6", "beta_l_ch4_6"), ("dch7_9", "beta_l_ch7_9")]:
            if ch_col in obs_df.columns:
                beta_l_arr += params.get(param_key, 0.0) * obs_df[ch_col].values'''

count_utility = content.count(old_utility_age)
print(f'Found {count_utility} utility computation occurrences')
if count_utility > 0:
    content = content.replace(old_utility_age, new_utility_age)
    changes_made += count_utility

# Write back
with open('RURO_post_estimation.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nTotal changes made: {changes_made}')
print('Done!')
