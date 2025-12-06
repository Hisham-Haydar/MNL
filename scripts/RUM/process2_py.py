#%%
import pandas as pd 

# # Compute observed hourly wage for workers (using 52 weeks per year and 12 months per year)
# df.loc[df["work"] == 1, "hourly_wage"] = df.loc[df["work"] == 1, "yem"] / (
#     df.loc[df["work"] == 1, "lhw"] * (52 / 12)
# )
# # %%
# # =================================================
# # Section 2: Selection Equation and IMR Computation
# # =================================================
# # Define selection variables based on DRD details.
# selection_vars = ["dag", "dgn", "dec", "dms", "ddi", "les"]

# # Remove any selection variable with little or no variation.
# constant_vars = [var for var in selection_vars if df[var].nunique() <= 1]
# if constant_vars:
#     print("Removing constant selection variables:", constant_vars)
#     selection_vars = [var for var in selection_vars if var not in constant_vars]

# # Build design matrix and estimate the Probit model.
# X_sel = sm.add_constant(df[selection_vars])
# probit_model = sm.Probit(df["work"], X_sel)
# probit_res = probit_model.fit(disp=False)
# print("Selection Equation (Probit) Results:")
# print(probit_res.summary())

# # Compute linear predictor and then the inverse Mills ratio (IMR).
# xb = np.dot(X_sel, probit_res.params)
# df["IMR"] = np.where(
#     df["work"] == 1, norm.pdf(xb) / norm.cdf(xb), -norm.pdf(xb) / (1 - norm.cdf(xb))
# )

# # =================================================
# # Section 3: Enhanced Heckman Wage Equation (OLS)
# # =================================================
# # Work on the working sample where wages are observed.
# df_workers = df[df["work"] == 1].copy()

# # Create log-experience variable.
# df_workers["ln_experience"] = np.log(df_workers["liwwh"] + 1)

# # Create additional features: quadratic term for age and interaction between education and gender.
# df_workers["dag2"] = df_workers["dag"] ** 2
# df_workers["dey_dgn"] = df_workers["dey"] * df_workers["dgn"]

# # Define enhanced wage predictors.
# wage_vars_enh = ["dag", "dag2", "dgn", "dey", "dey_dgn", "ln_experience", "lcs"]

# # Create dummy variables for occupation ('loc') and industry ('lindi').
# loc_dummies = pd.get_dummies(df_workers["loc"], prefix="loc", drop_first=True)
# lindi_dummies = pd.get_dummies(df_workers["lindi"], prefix="lindi", drop_first=True)

# # Assemble the enhanced wage regression matrix.
# X_wage_enh = df_workers[wage_vars_enh].copy()
# X_wage_enh = sm.add_constant(X_wage_enh)
# X_wage_enh = pd.concat(
#     [X_wage_enh, loc_dummies, lindi_dummies, df_workers["IMR"]], axis=1
# )
# X_wage_enh = X_wage_enh.astype(float)
# y_wage_enh = pd.to_numeric(df_workers["hourly_wage"], errors="coerce").astype(float)

# # Estimate the enhanced Heckman wage equation using OLS.
# ols_model = sm.OLS(y_wage_enh, X_wage_enh).fit()
# print("Enhanced Heckman Wage Equation (OLS) Results:")
# print(ols_model.summary())

# # =================================================
# # Section 4: ML Wage Regression with Hyperparameter Tuning (Gradient Boosting)
# # =================================================
# param_grid = {
#     "n_estimators": [100, 200, 300],
#     "learning_rate": [0.01, 0.05, 0.1],
#     "max_depth": [3, 4, 5],
#     "min_samples_split": [2, 5],
#     "min_samples_leaf": [1, 3],
# }
# gbr = GradientBoostingRegressor(random_state=42)
# grid_search = GridSearchCV(
#     gbr, param_grid, cv=5, scoring="neg_mean_squared_error", n_jobs=-1, verbose=1
# )
# grid_search.fit(X_wage_enh, y_wage_enh)
# best_gbr = grid_search.best_estimator_
# print("Best GBR Parameters:", grid_search.best_params_)

# # Evaluate training performance on working sample for ML model.
# train_preds_ml = best_gbr.predict(X_wage_enh)
# rmse_train_ml = np.sqrt(mean_squared_error(y_wage_enh, train_preds_ml))
# print("GBR Model Training RMSE:", rmse_train_ml)
# # %%
# # =================================================
# # Section 5: Model Comparison on the Working Sample
# # =================================================
# # --- Comparison Code: Evaluate Model Performance on the Working Sample ---
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error
# import numpy as np
# import pandas as pd

# # Split the working sample into train and test sets (70/30 split)
# X_train, X_test, y_train, y_test = train_test_split(
#     X_wage_enh, y_wage_enh, test_size=0.3, random_state=42
# )

# # Refit the OLS model on the training set.
# ols_model_cv = sm.OLS(y_train, X_train).fit()
# preds_ols_cv = ols_model_cv.predict(X_test)
# rmse_ols_cv = np.sqrt(mean_squared_error(y_test, preds_ols_cv))
# print("Enhanced Heckman (OLS) Model - Test RMSE:", rmse_ols_cv)

# # Get predictions from the tuned ML model on the test set.
# preds_ml_cv = best_gbr.predict(X_test)
# rmse_ml_cv = np.sqrt(mean_squared_error(y_test, preds_ml_cv))
# print("Tuned GBR Model - Test RMSE:", rmse_ml_cv)

# if rmse_ml_cv < rmse_ols_cv:
#     print("The ML model performs better on the working sample (lower RMSE).")
# else:
#     print(
#         "The Enhanced Heckman (OLS) model performs better on the working sample (lower RMSE)."
#     )

# # ----- Now, compare predictions against the reference wage 'yivwg' on the working sample -----
# # Convert the reference wage to numeric.
# df_workers["yivwg_numeric"] = pd.to_numeric(df_workers["yivwg"], errors="coerce")

# # IMPORTANT: Limit the reference wage to the test set using the same indices as X_test.
# rmse_yivwg_cv = np.sqrt(
#     mean_squared_error(y_test, df_workers.loc[X_test.index, "yivwg_numeric"])
# )
# print("Reference Wage (yivwg) - Test RMSE:", rmse_yivwg_cv)

# if rmse_yivwg_cv < rmse_ml_cv:
#     print("The yivwg reference performs better on the test sample (lower RMSE).")
# else:
#     print(
#         "The ML model performs better on the test sample compared to yivwg (lower RMSE)."
#     )

# # =================================================
# # Section 6: Compare Predictions Against Reference Wage 'yivwg'
# # =================================================

# preds_ols_yivwg = ols_model.predict(X_wage_enh)
# preds_ml_yivwg = best_gbr.predict(X_wage_enh)
# rmse_ols_yivwg = np.sqrt(
#     mean_squared_error(df_workers["yivwg_numeric"], preds_ols_yivwg)
# )
# rmse_ml_yivwg = np.sqrt(mean_squared_error(df_workers["yivwg_numeric"], preds_ml_yivwg))
# print(
#     "Reference Wage (yivwg) vs. Enhanced Heckman (OLS) Prediction RMSE:", rmse_ols_yivwg
# )
# print("Reference Wage (yivwg) vs. Tuned ML (GBR) Prediction RMSE:", rmse_ml_yivwg)
# if rmse_ml_yivwg < rmse_ols_yivwg:
#     print("The ML model's predictions are closer to the reference wage (yivwg).")
# else:
#     print(
#         "The Enhanced Heckman (OLS) model's predictions are closer to the reference wage (yivwg)."
#     )


# # %%

# # =================================================
# # Section 7: Predict Counterfactual Wages for Non-Workers
# # =================================================
# df_nonwork = df[df["work"] == 0].copy()
# X_sel_nonwork = sm.add_constant(df_nonwork[selection_vars])
# xb_nonwork = np.dot(X_sel_nonwork, probit_res.params)
# df_nonwork["IMR"] = -norm.pdf(xb_nonwork) / (1 - norm.cdf(xb_nonwork))
# df_nonwork["ln_experience"] = np.log(df_nonwork["liwwh"].fillna(0) + 1)
# df_nonwork["dag2"] = df_nonwork["dag"] ** 2
# df_nonwork["dey_dgn"] = df_nonwork["dey"] * df_nonwork["dgn"]
# X_wage_non = df_nonwork[wage_vars_enh].copy()
# X_wage_non = sm.add_constant(X_wage_non)
# # Create and align dummies for non-workers.
# loc_dummies_non = pd.get_dummies(df_nonwork["loc"], prefix="loc", drop_first=True)
# lindi_dummies_non = pd.get_dummies(df_nonwork["lindi"], prefix="lindi", drop_first=True)
# loc_dummies_non = loc_dummies_non.reindex(columns=loc_dummies.columns, fill_value=0)
# lindi_dummies_non = lindi_dummies_non.reindex(
#     columns=lindi_dummies.columns, fill_value=0
# )
# X_wage_non = pd.concat(
#     [X_wage_non, loc_dummies_non, lindi_dummies_non, df_nonwork["IMR"]], axis=1
# )
# X_wage_non = X_wage_non.astype(float)
# df_nonwork["predicted_hourly_wage_OLS"] = ols_model.predict(X_wage_non)
# df_nonwork["predicted_hourly_wage_ML"] = best_gbr.predict(X_wage_non)
# print("\nFirst 10 Predicted Hourly Wages for Non-Workers (Enhanced Heckman OLS):")
# print(df_nonwork[["predicted_hourly_wage_OLS"]].head(10))
# print("\nFirst 10 Predicted Hourly Wages for Non-Workers (ML Model):")
# print(df_nonwork[["predicted_hourly_wage_ML"]].head(10))

# # =================================================
# # Section 8: Save Consolidated Results
# # =================================================
# df.loc[df["work"] == 0, "predicted_hourly_wage_OLS"] = df_nonwork[
#     "predicted_hourly_wage_OLS"
# ]
# df.loc[df["work"] == 0, "predicted_hourly_wage_ML"] = df_nonwork[
#     "predicted_hourly_wage_ML"
# ]

# # %%
# rmse_yivwg_calculated = np.sqrt(
#     mean_squared_error(
#         pd.to_numeric(df_workers["yivwg"], errors="coerce"), df_workers["hourly_wage"]
#     )
# )
# rmse_yivwg_calculated
# # %%
# df.to_csv("consolidated_wage_predictions.csv", index=False)
# print("\nResults saved to 'consolidated_wage_predictions.csv'")


# %%Creation of Couples
# Create and process couples data
df_couples = process_couples_data(final_df_sim1)

# Use df_couples as the independent dataset from now on
print(f"Number of households in couples : {df_couples['idhh'].nunique()}")
print(f"opposite sex couples : {df_couples['idhh'].nunique()}")


#%% 


# %% Filtration - Streamlined Filtering on couple households

# -------------------------------
# Baseline: df_couples (the starting point)
# -------------------------------
stats = []
initial_households = df_couples["idhh"].nunique()
total, female, male = get_head_counts(df_couples)
stats.append(create_stats_entry(
    "Baseline", "Initial households", total, female, male, initial_households
))

# Apply filtering pipeline for heads and partners
role_filters = [
    ("hh_IsHead", "Head"),
    ("tu_hh_de_IsPartner", "Partner")
]

df_after_basic_filters, basic_stats = apply_filtering_pipeline(
    df_couples, role_filters, "couples", initial_households, CONFIG
)
stats.extend(basic_stats)

# Apply other household members filter
before_count = df_after_basic_filters["idhh"].nunique()
df_after_members_filter = apply_other_members_filter(df_after_basic_filters, CONFIG)
after_count = df_after_members_filter["idhh"].nunique()

total_p_new, female_p_new, male_p_new = get_head_counts(df_after_members_filter)
stats.append(create_stats_entry(
    "Other Household Members Filter", 
    "Drop households based on other members' conditions",
    total_p_new, female_p_new, male_p_new, initial_households
))
log_filtering_step("Other Household Members Filter", before_count, after_count)

# Apply abnormal wage & labor time filter
before_count = df_after_members_filter["idhh"].nunique()
df_final_filtered = apply_abnormal_filter(df_after_members_filter, households_to_remove, CONFIG)
after_count = df_final_filtered["idhh"].nunique()

total_ab, female_ab, male_ab = get_head_counts(df_final_filtered)
stats.append(create_stats_entry(
    "Wage & Labor Time Filter (Abnormal)",
    "Drop households with les==3 and abnormal wage or lhw",
    total_ab, female_ab, male_ab, initial_households
))
log_filtering_step("Wage & Labor Time Filter", before_count, after_count)

# -------------------------------
# Export couples results
# -------------------------------
stats_df = pd.DataFrame(stats)
print("\nStepwise Filtering Summary for Couples (Head & Partner):")
print(stats_df)

# Export using unified function
couples_exports = export_household_data(
    df_final_filtered, stats_df, "couples", OUTPUTS_DIR, PROCESSED_DIR
)
print("\nCouples data exported to:")
for export_type, path in couples_exports.items():
    print(f"  {export_type}: {path}")

# %%SINGLES
# Create and process singles data
df_singles = process_singles_data(final_df_sim1)
print("Unique households in singles:", df_singles["idhh"].nunique())

# %% Filtration - Streamlined Filtering on single households

# -------------------------------
# Baseline: df_singles (the starting point)
# -------------------------------
stats_singles = []
initial_households = df_singles["idhh"].nunique()
total, female, male = get_head_counts(df_singles)
stats_singles.append(create_stats_entry(
    "Baseline (Singles)", "Initial singles households", total, female, male, initial_households
))

# Apply filtering pipeline for heads only
role_filters = [("hh_IsHead", "Head")]

df_after_basic_filters_singles, basic_stats_singles = apply_filtering_pipeline(
    df_singles, role_filters, "singles", initial_households, CONFIG
)
stats_singles.extend(basic_stats_singles)

# Apply other household members filter
before_count = df_after_basic_filters_singles["idhh"].nunique()
df_after_members_filter_singles = apply_other_members_filter(df_after_basic_filters_singles, CONFIG)
after_count = df_after_members_filter_singles["idhh"].nunique()

total_new, female_new, male_new = get_head_counts(df_after_members_filter_singles)
stats_singles.append(create_stats_entry(
    "Other Household Members Filter (Singles)",
    "Drop households based on other members' conditions",
    total_new, female_new, male_new, initial_households
))
log_filtering_step("Other Household Members Filter (Singles)", before_count, after_count)

# Apply abnormal wage & labor time filter
before_count = df_after_members_filter_singles["idhh"].nunique()
df_final_filtered_singles = apply_abnormal_filter(df_after_members_filter_singles, households_to_remove, CONFIG)
after_count = df_final_filtered_singles["idhh"].nunique()

total_ab, female_ab, male_ab = get_head_counts(df_final_filtered_singles)
stats_singles.append(create_stats_entry(
    "Wage & Labor Time Filter (Abnormal, Singles)",
    "Drop singles households with les==3 and abnormal wage or lhw",
    total_ab, female_ab, male_ab, initial_households
))
log_filtering_step("Wage & Labor Time Filter (Singles)", before_count, after_count)

# -------------------------------
# Export singles results
# -------------------------------
stats_singles_df = pd.DataFrame(stats_singles)
print("\nStepwise Filtering Summary for Singles:")
print(stats_singles_df)

# Export using unified function
singles_exports = export_household_data(
    df_final_filtered_singles, stats_singles_df, "singles", OUTPUTS_DIR, PROCESSED_DIR
)
print("\nSingles data exported to:")
for export_type, path in singles_exports.items():
    print(f"  {export_type}: {path}")

# Export gender-split data
gender_exports = export_gender_split_data(
    df_final_filtered_singles, "singles_final_filtered", PROCESSED_DIR
)
print("\nGender-split singles data exported:")
for gender, paths in gender_exports.items():
    for export_type, path in paths.items():
        if export_type != "data":  # Don't print data object details
            print(f"  {gender} {export_type}: {path}")

# Extract gender data for further processing
female_singles = gender_exports["female"]["data"]
male_singles = gender_exports["male"]["data"]

# %%
# Check for overlapping idperson and idhh

# Extract the sets from each dataset
couples_idperson = set(df_final_filtered["idperson"])
females_idperson = set(female_singles["idperson"])
males_idperson = set(male_singles["idperson"])

couples_idhh = set(df_final_filtered["idhh"])
females_idhh = set(female_singles["idhh"])
males_idhh = set(male_singles["idhh"])

# Check overlaps for idperson
overlap_idperson_fm = females_idperson.intersection(males_idperson)
overlap_idperson_cf = couples_idperson.intersection(females_idperson)
overlap_idperson_cm = couples_idperson.intersection(males_idperson)

# Check overlaps for idhh
overlap_idhh_fm = females_idhh.intersection(males_idhh)
overlap_idhh_cf = couples_idhh.intersection(females_idhh)
overlap_idhh_cm = couples_idhh.intersection(males_idhh)

print("Overlap idperson between female_singles and male_singles:", overlap_idperson_fm)
print("Overlap idhh between female_singles and male_singles:", overlap_idhh_fm)
print("Overlap idperson between couples and female_singles:", overlap_idperson_cf)
print("Overlap idhh between couples and female_singles:", overlap_idhh_cf)
print("Overlap idperson between couples and male_singles:", overlap_idperson_cm)
print("Overlap idhh between couples and male_singles:", overlap_idhh_cm)

# If there is no overlap at all, pile the datasets together
if not (
    overlap_idperson_fm
    or overlap_idperson_cf
    or overlap_idperson_cm
    or overlap_idhh_fm
    or overlap_idhh_cf
    or overlap_idhh_cm
):
    df_filtered_piled = pd.concat(
        [df_final_filtered, female_singles, male_singles], axis=0
    )
    print(
        "No overlapping IDs found. Combined dataset has",
        df_filtered_piled["idhh"].nunique(),
        "unique households and",
        df_filtered_piled["idperson"].nunique(),
        "unique persons.",
    )

    # Export the combined dataset
    piled_export_path = PROCESSED_DIR / "filtered_piled.csv"
    df_filtered_piled.to_csv(piled_export_path, index=False)
    print(f"Combined filtered dataset exported to {piled_export_path}")
else:
    print(
        "Overlapping IDs were found between the datasets. Please review before combining."
    )
# %% End

