#%% 
import numpy as np
import pandas as pd
from scipy.optimize import minimize,fsolve, approx_fprime
from scipy.special import logsumexp
from scipy import stats
from scipy.stats import ttest_ind

#%% 
# Load the data
df = pd.read_pickle('longSpan.pickle')
df[['idperson', 'scenario','original_scenario']].head()

df['dag'] = (df['dag'] - df['dag'].mean()) / df['dag'].std()
df['dag2'] = df['dag2'] / 1000

df.info()
#%% 
## mapping
scenario_mapping = {'h0': 0, 'h1': 1, 'h2': 2, 'h3': 3}

df['original_scenario'] = df['original_scenario'].map(scenario_mapping)
df['scenario'] = df['scenario'].map(scenario_mapping)

#%% 

df = df.drop(columns=['consum', 'lhw_h0', 'lhw_h1', 'lhw_h2', 'lhw_h3','normalized_age','normalized_dncsy'])
df.info()
#%% 
# Convert dummy variable columns to uint8
uint8_columns = ['dgn', 'deh_1', 'deh_0', 'deh_3', 'deh_2', 'deh_4',
                 'dcz_2', 'dcz_3', 'lindi_0', 'lindi_1', 'lindi_3', 'lindi_4',
                 'lindi_5', 'lindi_6', 'lindi_7', 'lindi_8', 'lindi_9',
                 'lindi_10', 'lindi_11', 'lindi_12', 'les_2', 'les_7', 'amrtn_2',
                 'amrtn_3', 'amrtn_4', 'amrtn_6', 'dms_3', 'dms_4', 'dms_5','scenario'
                 ,'original_scenario','drgru','choice_made','leisure','lhw_scenario']

df[uint8_columns] = df[uint8_columns].astype('uint8')
# Changing all int64 columns to int8
df = df.astype({col: 'float32' for col in df.select_dtypes(include='float64').columns})
df.info()
#%% 
df[['idperson', 'scenario','original_scenario','lhw_scenario','choice_made', 'hyds','leisure']].head()
# %%
df.to_pickle('spanishdata.pickle')
