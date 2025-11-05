# %% packages and working directory  
import os 
import pandas as pd 
import numpy as np 
import biogeme.database as db
import biogeme.biogeme as bio 
import biogeme.models as models 
import biogeme.version as ver 
from biogeme.expressions import Beta, log,Variable, bioMultSum


# Consolidate changing directory and CPI dictionary since these don't change throughout the script
new_directory = r'C:\Users\hisham\Spain\2021 datasets'
os.chdir(new_directory)


# %%
filtered_df = pd.read_csv('SpanishData.csv')

# Rescale data
def rescale_column(df, col):
    mean = df[col].mean()
    std = df[col].std()
    df[col] = (df[col] - mean) / std
    return df

# Apply rescaling to relevant columns (example)
for col in filtered_df.select_dtypes(include=[np.float64]).columns:
    filtered_df = rescale_column(filtered_df, col)


# Ensure appropriate data types
filtered_df = filtered_df.astype({col: 'float32' for col in filtered_df.select_dtypes(include=[np.float64]).columns})

# Create the Biogeme database
database = db.Database('labour_supply', filtered_df)
globals().update(database.variables)
logy_vars = {f'logy_h{i}': Variable(f'logy_h{i}') for i in range(4)}
logl_vars = {f'logl_h{i}': Variable(f'logl_h{i}') for i in range(4)}
logy2_vars = {f'logy2_h{i}': Variable(f'logy2_h{i}') for i in range(4)}
logl2_vars = {f'logl2_h{i}': Variable(f'logl2_h{i}') for i in range(4)}
logyl_vars = {f'logyl_h{i}': Variable(f'logyl_h{i}') for i in range(4)}
choice = Variable('original_scenario')

# Define heterogeneity variables
dag = Variable('dag')
dag2 = Variable('dag2')
dgn = Variable('dgn')
dncsy = Variable('dncsy')
#%% 
# Define the parameters to be estimated with realistic boundaries
alpha = Beta('alpha', 16.77, 0, 200, 0)
beta = Beta('beta', 68.13, 0, 300, 0)
gamma_yy = Beta('gamma_yy', -0.95, -30, 0, 0)
gamma_ll = Beta('gamma_ll', -8.78, -30, 0, 0)
gamma_yl = Beta('gamma_yl', 0.104, -15, 15, 0)

# Define heterogeneity parameters for age and gender with boundaries
alpha_dag = Beta('alpha_dag', -.0407395, -10, 10, 0)
alpha_dag2 = Beta('alpha_dag2',.0008478, -1, 1, 0)
alpha_dgn = Beta('alpha_dgn', .7765613, -10, 10, 0)
alpha_dncsy = Beta('alpha_dncsy', -2.458267, -10, 10, 0)

beta_dag = Beta('beta_dag', -.1247139 , -10, 10, 0)
beta_dag2 = Beta('beta_dag2', .001434 , -1, 1, 0)
beta_dgn = Beta('beta_dgn', -.735524, -5, 0, 0)
beta_dncsy = Beta('beta_dncsy', -2.473627, -10, 0, 0)

# Create alpha and beta dictionaries for dummy variables with realistic boundaries
def create_alpha_beta_dict(levels, prefix):
    return {level: Beta(f'{prefix}_{level}', 0, -50, 50, 0) for level in levels}

deh_levels = [col for col in filtered_df.columns if 'deh_' in col]
dcz_levels = [col for col in filtered_df.columns if 'dcz_' in col]
lindi_levels = [col for col in filtered_df.columns if 'lindi_' in col]
les_levels = ['les_2', 'les_7']
amrtn_levels = [col for col in filtered_df.columns if 'amrtn_' in col]
dms_levels = [col for col in filtered_df.columns if 'dms_' in col]

alpha_deh = create_alpha_beta_dict(deh_levels, 'alpha')
beta_deh = create_alpha_beta_dict(deh_levels, 'beta')
alpha_dcz = create_alpha_beta_dict(dcz_levels, 'alpha')
beta_dcz = create_alpha_beta_dict(dcz_levels, 'beta')
alpha_lindi = create_alpha_beta_dict(lindi_levels, 'alpha')
beta_lindi = create_alpha_beta_dict(lindi_levels, 'beta')
alpha_les = create_alpha_beta_dict(les_levels, 'alpha')
beta_les = create_alpha_beta_dict(les_levels, 'beta')
alpha_amrtn = create_alpha_beta_dict(amrtn_levels, 'alpha')
beta_amrtn = create_alpha_beta_dict(amrtn_levels, 'beta')
alpha_dms = create_alpha_beta_dict(dms_levels, 'alpha')
beta_dms = create_alpha_beta_dict(dms_levels, 'beta')

# Combine all alpha and beta dictionaries
alpha_dict = {**alpha_deh, **alpha_dcz, **alpha_lindi, **alpha_les, **alpha_amrtn, **alpha_dms}
beta_dict = {**beta_deh, **beta_dcz, **beta_lindi, **beta_les, **beta_amrtn, **beta_dms}

# Precompute common terms
alpha_common_terms = alpha + alpha_dag * dag + alpha_dag2 * dag2 + alpha_dgn * dgn + alpha_dncsy * dncsy
beta_common_terms = beta + beta_dag * dag + beta_dag2 * dag2 + beta_dgn * dgn + beta_dncsy * dncsy

# Helper function to create utility
def create_utility(logy, logl, logy2, logl2, logyl, alpha_dict, beta_dict, alpha_common, beta_common):
    alpha_sum = bioMultSum([alpha_common] + [alpha_dict[level] * Variable(level) for level in alpha_dict] )
    beta_sum = bioMultSum([beta_common] + [beta_dict[level] * Variable(level) for level in beta_dict])
    return alpha_sum * logy + beta_sum * logl + gamma_yy * logy2 + gamma_ll * logl2 + gamma_yl * logyl
# %% 

# Generate the utility functions using the helper function
V = {i: create_utility(logy_vars[f'logy_h{i}'], logl_vars[f'logl_h{i}'], logy2_vars[f'logy2_h{i}'], logl2_vars[f'logl2_h{i}'], logyl_vars[f'logyl_h{i}'],
                       alpha_dict, beta_dict, alpha_common_terms, beta_common_terms) for i in range(4)}

# Define the availability of each choice (all choices are available)
av = {i: 1 for i in range(4)}

# Associate the utility functions with the choice situations
logprob = models.loglogit(V, av, choice)

# %% Create the Biogeme object
biogeme_model = bio.BIOGEME(database, logprob)
biogeme_model.modelName = 'optimized_model_with_bounds2'
biogeme_model.choice = choice

# Adjust optimization settings for better convergence
biogeme_model.algorithmParameters = {'tolerance': 1e-6, 'maxIter': 2000}

# Estimate the parameters
results = biogeme_model.estimate()

# Print the estimated parameters
print(results.getEstimatedParameters())
