#%% 
import pandas as pd    


df = pd.read_parquet(r'U:\EUROMOD-STORAGE\Data\processed\fr\2016\singles_RURO_ready.parquet', engine='pyarrow')
print(df.head())
#%% 
df_s = df.copy()

# show selected work-related columns
cols = ["lhw", "working", "working_pt1", "working_pt2", "working_ft"]
print("Work-related columns head:")
print(df_s[cols].head())

# check education dummies
edu_cols = ["deh", "educL", "educH"]
print("\nEducation indicators (unique rows sorted by deh):")
print(df_s[edu_cols].drop_duplicates().sort_values("deh"))

# region shares by reg_nuts1_ dummies
print("\nRegion dummy means (shares by region):")
print(df_s.filter(like="reg_nuts1_").mean())

# potential experience summary
pe_cols = ["dag", "deh", "pexp_years", "pexp"]
print("\nPotential experience describe:")
print(df_s[pe_cols].describe())

#%% 
df_s['check'] = df_s['pexp_years'] - (df_s['dag'] - df_s['dey'] - 6)
print("\nCheck potential experience calculation (should be 0):")
print(df_s['check'].value_counts())

df_s[["dag", "deh", "pexp_years",'check']].sample(10)

# %%
