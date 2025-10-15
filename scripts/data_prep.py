#!/usr/bin/env python
# @Date    : 2025-10-08 16:14:38
# @Author  : Hisham Haydar (Hisham.Haydar@liser.lu)
# @Link    : https://hisham-haydar.github.io/
# @Version : 1.0.0

# %% Bootstrap (Interactive Window friendly paths and helpers)
import os
import sys
from pathlib import Path
import euromod as em
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    SCRIPT_DIR = Path(__file__).resolve().parent
except NameError:
    # Fallback when running cells interactively without __file__
    SCRIPT_DIR = Path.cwd() / "scripts"

PROJECT_ROOT = (SCRIPT_DIR / "..").resolve()
os.chdir(PROJECT_ROOT)

SCRATCH_DIR = PROJECT_ROOT / "scratch"
if SCRATCH_DIR.exists():
    sys.path.insert(0, str(SCRATCH_DIR))

try:
    from scratch.my_functions import (
        apply_abnormal_filter,
        compute_wage_recon,
        correct_labor_status,
        apply_filtering_pipeline,
        apply_other_members_filter,
        check_data_quality,
        create_income_columns,
        create_stats_entry,
        export_gender_split_data,
        export_household_data,
        get_head_counts,
        identify_extreme_households,
        log_filtering_step,
        process_couples_data,
        process_singles_data,
        setup_logging,
        validate_household_integrity,
        validate_required_columns,
    )  # type: ignore
except ImportError as e:
    raise ImportError(
        "Missing helpers 'create_income_columns' and 'get_head_counts' in scratch/my_functions.py."
    ) from e

# Canonical project paths
DATA_ROOT = PROJECT_ROOT / "Data"
RAW_DIR = (DATA_ROOT / "raw") if (DATA_ROOT / "raw").exists() else DATA_ROOT
PROCESSED_DIR = DATA_ROOT / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = PROJECT_ROOT / "EUROMOD_RELEASES_J1.0+" / "EUROMOD_RELEASES_J1.0+"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "prep"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR = OUTPUTS_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Configuration parameters
CONFIG = {
    "age_range": (16, 65),
    "replacement_income_cap": 100,
    "allowed_les": [3, 5, 7],
    "extreme_wage_diff": 500,
    "wage_bounds": (2, 170),
    "hour_bounds": (5, 79),
    "target_system": "DE_2014",
    "target_dataset": "DE_2015_a1",
    "export_format": "parquet",
    "plot_bins": 40,
}

PLOT_VARIABLES = {
    "lhw": {"label": "Weekly hours worked (lhw)", "discrete": False},
    "yivwg": {"label": "Gross wage (yivwg)", "discrete": False},
    "ils_disp": {"label": "Disposable income (ils_disp)", "discrete": False},
    "yem": {"label": "Employment income (yem)", "discrete": False},
    "les": {"label": "Labour status code (les)", "discrete": True},
    "loc": {"label": "Occupation class (loc)", "discrete": True},
    "lindi": {"label": "Industry class (lindi)", "discrete": True},
    "dag": {"label": "Age (dag)", "discrete": False},
    "dehde": {"label": "Highest education (dehde)", "discrete": True},
    "num_children_total": {"label": "Number of children", "discrete": True},
}


def _plot_distribution(series: pd.Series, title: str, output_path: Path, *, discrete: bool, bins: int) -> None:
    """Persist a histogram or bar plot for the provided series."""
    clean = series.dropna()
    if clean.empty:
        print(f"Skipping '{series.name}' for '{title}': no data after filtering")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    if discrete or (pd.api.types.is_integer_dtype(clean) and clean.nunique() <= bins / 2):
        counts = clean.value_counts().sort_index()
        ax.bar(counts.index.astype(str), counts.values, color="#4C72B0") # type: ignore
        ax.set_ylabel("Count")
    else:
        ax.hist(clean, bins=bins, color="#4C72B0", edgecolor="white")
        ax.set_ylabel("Frequency")

    ax.set_title(title)
    ax.set_xlabel(title.split(" – ")[0])
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def _generate_group_plots(df: pd.DataFrame, *, group_name: str, prefix: str, bins: int) -> dict[str, Path]:
    """Create plots for ``df`` and return a mapping from variable to saved path."""
    saved_paths: dict[str, Path] = {}
    for column, info in PLOT_VARIABLES.items():
        if column not in df.columns:
            print(f"Skipping '{column}' for '{group_name}': column missing")
            continue
        output_path = PLOTS_DIR / f"{prefix}_{column}.png"
        title = f"{info['label']} – {group_name}"
        _plot_distribution(df[column], title, output_path, discrete=info["discrete"], bins=bins)
        saved_paths[column] = output_path
    return saved_paths


def _generate_gender_plots(df: pd.DataFrame, *, base_group: str, prefix: str, bins: int) -> dict[str, dict[str, Path]]:
    """Produce plots for the whole sample and gender-specific subsets."""
    results: dict[str, dict[str, Path]] = {}
    results["overall"] = _generate_group_plots(df, group_name=base_group, prefix=f"{prefix}_overall", bins=bins)

    for gender_code, gender_label in [(0, "female"), (1, "male")]:
        subset = df[df["dgn"].astype(float) == gender_code]
        if subset.empty:
            print(f"No records for {base_group} – {gender_label}, skipping plots")
            continue
        results[gender_label] = _generate_group_plots(
            subset,
            group_name=f"{base_group} ({gender_label})",
            prefix=f"{prefix}_{gender_label}",
            bins=bins,
        )
    return results


setup_logging("INFO")


# %% Directories and Data import
def _first_existing(*paths: Path) -> Path:
    """Return the first path that exists, or the last candidate if none exist."""
    for p in paths:
        if p.exists():
            return p
    return paths[-1]


data_file = _first_existing(
    RAW_DIR / "DE_2015_a1.txt",
    DATA_ROOT / "DE_2015_a1.txt",
    RAW_DIR / "DE_2021_b1.txt",
    DATA_ROOT / "DE_2021_b1.txt",
)
df = pd.read_csv(data_file, sep="\t")
mod = em.Model(str(MODEL_DIR))
TARGET_SYSTEM = CONFIG["target_system"]
TARGET_DATASET = CONFIG["target_dataset"]

country = mod["DE"]
try:
    system = country[TARGET_SYSTEM]
except KeyError:
    if hasattr(country, "systems"):
        raw_systems = country.systems  # type: ignore[attr-defined]
        systems_iter = raw_systems.values() if hasattr(raw_systems, "values") else raw_systems
    else:
        systems_iter = country.values() if hasattr(country, "values") else country  # type: ignore[attr-defined]
    system = next(iter(systems_iter))

dataset = None
if hasattr(system, "datasets"):
    try:
        dataset = system.datasets[TARGET_DATASET]
    except (KeyError, AttributeError):
        dataset = None

if dataset is None:
    candidates = [
        ds
        for ds in getattr(system, "bestmatch_datasets", [])
        if getattr(ds, "name", "") == TARGET_DATASET
    ]
    dataset = candidates[0] if candidates else system.bestmatch_datasets[0]

system_name = getattr(system, "name", TARGET_SYSTEM)
dataset_name = getattr(dataset, "name", TARGET_DATASET)
print(f"Running EUROMOD system {system_name} with dataset {dataset_name}")

sim = system.run(df, dataset.name)
df_sim = sim.outputs[0]
print("raw df info (memory_usage='deep'):")
df.info(memory_usage="deep")  # type: ignore[arg-type]


# %% Head of Households
df_sim["hh_IsHead"] = (df_sim["tu_hh_de_HeadID"] == df_sim["idperson"]).astype(int)
is_single_head = df_sim.groupby("idhh")["hh_IsHead"].sum().eq(1)
print(f"Number of households with a single head: {is_single_head.sum()}")
multi_head_count = df_sim.groupby("idhh")["hh_IsHead"].sum().gt(1).sum()
print(f"Number of households with multiple heads: {multi_head_count}")
print(f"Number of unique households in the dataset: {df_sim['idhh'].nunique()}")


print("Columns and info before creation of aggregates:")
df_sim.info(memory_usage="deep")
df_sim1 = create_income_columns(df_sim)
print("Columns and info after creation of aggregates:")
df_sim1.info(memory_usage="deep")


start_var = "tu_family2_de_HeadID"
end_var = "income_total_overall"
sim1_cols = [col.strip() for col in df_sim1.columns.tolist()]
try:
    start_index = sim1_cols.index(start_var)
    end_index = sim1_cols.index(end_var)
except ValueError as err:
    raise ValueError("One or both boundary columns were not found in df_sim1.") from err

required_columns = sim1_cols[start_index : end_index + 1]
print("Required columns in df_sim1 to keep:", required_columns)

if "idperson" not in df.columns or "idperson" not in df_sim1.columns:
    raise ValueError("idperson is not present in both DataFrames!")

final_df_sim1 = df.merge(
    df_sim1[["idperson"] + required_columns],
    on="idperson",
    how="left",
)

print("Final merged frame shape:", final_df_sim1.shape)

REQUIRED_COLUMNS = ["idperson", "idhh", "dag", "dgn", "les", "yem", "lhw", "yivwg"]
validate_required_columns(final_df_sim1, REQUIRED_COLUMNS)

if not validate_household_integrity(final_df_sim1):
    print("Warning: Household integrity issues detected!")

quality_issues = check_data_quality(final_df_sim1)
if quality_issues:
    print(f"Data quality issues detected: {quality_issues}")


final_df_sim1["les_orig"] = final_df_sim1["les"]
final_df_sim1 = correct_labor_status(final_df_sim1, emp_threshold=0)

chg = final_df_sim1["les_enforced"] != final_df_sim1["les_orig"]
print("Reclassified away from employee (3→≠3):", int(((final_df_sim1["les_orig"] == 3) & chg).sum()))
print("Total status changes:", int(chg.sum()))
print(
    pd.crosstab(
        final_df_sim1["les_orig"],
        final_df_sim1["les_enforced"],
        rownames=["les_orig"],
        colnames=["les_enforced"],
    )
)


final_df_sim1 = compute_wage_recon(final_df_sim1)
WPM = 52 / 12
yem_from_hours = final_df_sim1["w_emp_strict"] * final_df_sim1["lhw"] * WPM
m_div12 = np.isclose(final_df_sim1["yem"], yem_from_hours / 12, rtol=0.05, atol=5)
m_liwmy = np.isclose(
    final_df_sim1["yem"],
    yem_from_hours * (final_df_sim1["liwmy"].clip(lower=0, upper=12).fillna(0) / 12),
    rtol=0.10,
    atol=5,
)
valid_emp = final_df_sim1["les_enforced"].eq(3) & final_df_sim1["lhw"].ge(10)

final_df_sim1["flag_periodicity"] = valid_emp & (m_div12 | m_liwmy)
final_df_sim1["yem_corrected"] = np.where(
    final_df_sim1["flag_periodicity"], yem_from_hours, final_df_sim1["yem"]
)

final_df_sim1["wage_final"] = final_df_sim1["w_emp_strict"]
final_df_sim1["yem2_final"] = np.where(valid_emp, final_df_sim1["wage_final"] * final_df_sim1["lhw"] * WPM, np.nan)
final_df_sim1["diff_yem_final"] = np.where(
    valid_emp, final_df_sim1["yem2_final"] - final_df_sim1["yem_corrected"], np.nan
)

CONFIG["extreme_diff_column"] = "diff_yem_final"

households_to_remove = identify_extreme_households(
    final_df_sim1.loc[~final_df_sim1["flag_periodicity"].fillna(False)],
    CONFIG,
)
print("Households to remove:", households_to_remove)

count_extreme_negative = (final_df_sim1["diff_yem_final"] <= -500).sum()
extreme_positive = final_df_sim1.loc[
    (final_df_sim1["diff_yem_final"] >= CONFIG["extreme_wage_diff"])
    & (~final_df_sim1["flag_periodicity"].fillna(False))
]
print("Count of records with unresolved diff_yem >= 500:", len(extreme_positive))
print(
    extreme_positive[
        [
            "yem_corrected",
            "yem2_final",
            "yds",
            "yse",
            "diff_yem_final",
            "lhw",
            "yivwg",
            "wage_final",
            "les_orig",
            "les_enforced",
            "les_suggested",
            "lindi",
            "loc",
            "lse",
        ]
    ].describe()
)


ep = final_df_sim1.loc[
    (final_df_sim1["diff_yem_final"] >= CONFIG["extreme_wage_diff"])
    & (~final_df_sim1["flag_periodicity"].fillna(False))
].copy()
prop_yem_zero = (ep["yem_corrected"] == 0).mean()
print("Share with yem_corrected == 0 in ep:", round(prop_yem_zero, 3))
print(ep["yem_corrected"].describe())
eq_rate = np.isclose(ep["wage_final"], ep["yivwg"], rtol=1e-6, atol=1e-6).mean()
print("Share with wage_final ≈ yivwg:", round(eq_rate, 3))
print(ep[["wage_final", "yivwg"]].describe())
median_recon = ep["wage_final"].median() * ep["lhw"].median() * (52 / 12)
print(
    "Medians — yem2_final, diff_yem_final, recon:",
    ep["yem2_final"].median(),
    ep["diff_yem_final"].median(),
    median_recon,
)
print(ep["lhw"].describe())

hp_left = pd.to_numeric(final_df_sim1["hh_IsHead"], errors="coerce").fillna(0).eq(1)
hp_right = pd.to_numeric(final_df_sim1["tu_hh_de_IsPartner"], errors="coerce").fillna(0).eq(1)
is_head_partner = hp_left | hp_right
share_hp_in_ep = is_head_partner.loc[ep.index].mean()
print("Share head/partner within ep:", round(share_hp_in_ep, 3))
counts_hp = is_head_partner.loc[ep.index].value_counts().rename({True: "head/partner", False: "other"})
print("Counts in ep by role:\n", counts_hp)

print(
    final_df_sim1["liwmy"].describe(),
    (final_df_sim1["liwmy"] > 12).sum(),
    final_df_sim1["liwmy"].unique()[:20],
)
print(final_df_sim1[["liwmy", "liwftmy", "liwptmy"]].head(10))


ready_allowed_les = final_df_sim1["les_enforced"].isin(CONFIG["allowed_les"])
ready_age = final_df_sim1["dag"].between(*CONFIG["age_range"])
ready_hours = final_df_sim1["lhw"].between(*CONFIG["hour_bounds"])
ready_wage = final_df_sim1["wage_final"].between(*CONFIG["wage_bounds"]) | final_df_sim1["wage_final"].isna()
ready_no_unresolved_extreme = ~final_df_sim1["idhh"].isin(households_to_remove)

final_df_sim1["keep_for_analysis"] = (
    ready_allowed_les & ready_age & ready_hours & ready_wage & ready_no_unresolved_extreme
)


child_bands = {
    "num_children_0_3": final_df_sim1["dag"].gt(0) & final_df_sim1["dag"].le(3),
    "num_children_3_6": final_df_sim1["dag"].gt(3) & final_df_sim1["dag"].le(6),
    "num_children_6_11": final_df_sim1["dag"].gt(6) & final_df_sim1["dag"].le(11),
    "num_children_11_17": final_df_sim1["dag"].gt(11) & final_df_sim1["dag"].le(17),
}
child_flags = pd.DataFrame(child_bands, index=final_df_sim1.index)
parent_links = pd.concat(
    [
        child_flags,
        final_df_sim1[["idfather", "idmother"]],
    ],
    axis=1,
)
parent_links = parent_links.melt(
    id_vars=list(child_bands.keys()),
    value_vars=["idfather", "idmother"],
    var_name="parent_role",
    value_name="parent_id",
)
valid_parent = parent_links["parent_id"].notna() & parent_links["parent_id"].ne(0)
parent_counts = (
    parent_links.loc[valid_parent]
    .groupby("parent_id")[list(child_bands.keys())]
    .sum()
)
parent_counts["num_children_total"] = parent_counts.sum(axis=1)
parent_counts = parent_counts[
    [
        "num_children_total",
        "num_children_0_3",
        "num_children_3_6",
        "num_children_6_11",
        "num_children_11_17",
    ]
]
final_df_sim1 = final_df_sim1.merge(
    parent_counts,
    how="left",
    left_on="idperson",
    right_index=True,
)
child_cols = parent_counts.columns.tolist()
final_df_sim1[child_cols] = final_df_sim1[child_cols].fillna(0).astype(int)

prep_path = PROCESSED_DIR / "DE_2015_a1_prepared_master.csv"
final_df_sim1.to_csv(prep_path, index=False)
print("Saved prepared master to:", prep_path)


final_df_sim1["les"] = final_df_sim1["les_enforced"]

print("\n=== Couples filtering pipeline ===")
df_couples = process_couples_data(final_df_sim1)
couples_initial = df_couples["idhh"].nunique()
print(f"Couples baseline households: {couples_initial}")

couples_stats_records: list[dict] = []
total, female, male = get_head_counts(df_couples)
couples_stats_records.append(
    create_stats_entry(
        "Baseline",
        "Initial couples households",
        total,
        female,
        male,
        couples_initial,
    )
)

couples_filtered, couples_pipeline_stats = apply_filtering_pipeline(
    df_couples,
    role_filters=[
        ("hh_IsHead", "Head"),
        ("tu_hh_de_IsPartner", "Partner"),
    ],
    household_type="couples",
    initial_count=couples_initial,
    config=CONFIG,
)
couples_stats_records.extend(couples_pipeline_stats)

before_other = couples_filtered["idhh"].nunique()
couples_no_other = apply_other_members_filter(couples_filtered, CONFIG)
after_other = couples_no_other["idhh"].nunique()
log_filtering_step("Other Household Members", before_other, after_other)
total, female, male = get_head_counts(couples_no_other)
couples_stats_records.append(
    create_stats_entry(
        "Other Household Members",
        "Drop households with ineligible other members",
        total,
        female,
        male,
        couples_initial,
    )
)

before_abnormal = couples_no_other["idhh"].nunique()
couples_final = apply_abnormal_filter(couples_no_other, households_to_remove, CONFIG)
after_abnormal = couples_final["idhh"].nunique()
log_filtering_step("Wage & Labor Time", before_abnormal, after_abnormal)
total, female, male = get_head_counts(couples_final)
couples_stats_records.append(
    create_stats_entry(
        "Wage & Labor Time",
        "Drop households with les==3 and abnormal wage or hours",
        total,
        female,
        male,
        couples_initial,
    )
)

couples_stats_df = pd.DataFrame(couples_stats_records)[
    ["Step", "Description", "Total Households", "Female Heads", "Male Heads", "% Remaining"]
]
couples_exports = export_household_data(
    df=couples_final,
    stats_df=couples_stats_df,
    output_prefix="couples_filtering",
    output_dir=OUTPUTS_DIR,
    processed_dir=PROCESSED_DIR,
    export_format=CONFIG.get("export_format", "parquet"),
)
print("Couples outputs:", couples_exports)


print("\n=== Singles filtering pipeline ===")
df_singles = process_singles_data(final_df_sim1)
singles_initial = df_singles["idhh"].nunique()
print(f"Singles baseline households: {singles_initial}")

singles_stats_records: list[dict] = []
total, female, male = get_head_counts(df_singles)
singles_stats_records.append(
    create_stats_entry(
        "Baseline",
        "Initial singles households",
        total,
        female,
        male,
        singles_initial,
    )
)

singles_filtered, singles_pipeline_stats = apply_filtering_pipeline(
    df_singles,
    role_filters=[("hh_IsHead", "Head")],
    household_type="singles",
    initial_count=singles_initial,
    config=CONFIG,
)
singles_stats_records.extend(singles_pipeline_stats)

before_other = singles_filtered["idhh"].nunique()
singles_no_other = apply_other_members_filter(singles_filtered, CONFIG)
after_other = singles_no_other["idhh"].nunique()
log_filtering_step("Other Household Members (Singles)", before_other, after_other)
total, female, male = get_head_counts(singles_no_other)
singles_stats_records.append(
    create_stats_entry(
        "Other Household Members",
        "Drop households with ineligible other members",
        total,
        female,
        male,
        singles_initial,
    )
)

before_abnormal = singles_no_other["idhh"].nunique()
singles_final = apply_abnormal_filter(singles_no_other, households_to_remove, CONFIG)
after_abnormal = singles_final["idhh"].nunique()
log_filtering_step("Wage & Labor Time (Singles)", before_abnormal, after_abnormal)
total, female, male = get_head_counts(singles_final)
singles_stats_records.append(
    create_stats_entry(
        "Wage & Labor Time",
        "Drop singles with les==3 and abnormal wage or hours",
        total,
        female,
        male,
        singles_initial,
    )
)

singles_stats_df = pd.DataFrame(singles_stats_records)[
    ["Step", "Description", "Total Households", "Female Heads", "Male Heads", "% Remaining"]
]
singles_exports = export_household_data(
    df=singles_final,
    stats_df=singles_stats_df,
    output_prefix="singles_filtering",
    output_dir=OUTPUTS_DIR,
    processed_dir=PROCESSED_DIR,
    export_format=CONFIG.get("export_format", "parquet"),
)
print("Singles outputs:", singles_exports)

gender_exports = export_gender_split_data(
    singles_final,
    output_prefix="singles_final_filtered",
    processed_dir=PROCESSED_DIR,
    export_pickle=False,
    export_format=CONFIG.get("export_format", "parquet"),
)
print("Singles gender-split exports:", gender_exports)


plot_bins = int(CONFIG.get("plot_bins", 40))

singles_heads = singles_final[singles_final["hh_IsHead"] == 1]
singles_plot_paths = _generate_gender_plots(
    singles_heads,
    base_group="Singles Heads",
    prefix="singles_heads",
    bins=plot_bins,
)
print("Singles head plots saved:", singles_plot_paths)

couples_heads = couples_final[couples_final["hh_IsHead"] == 1]
couples_head_plot_paths = _generate_gender_plots(
    couples_heads,
    base_group="Couples Heads",
    prefix="couples_heads",
    bins=plot_bins,
)
print("Couples head plots saved:", couples_head_plot_paths)

couples_partners = couples_final[couples_final["tu_hh_de_IsPartner"] == 1]
couples_partner_plot_paths = _generate_gender_plots(
    couples_partners,
    base_group="Couples Partners",
    prefix="couples_partners",
    bins=plot_bins,
)
print("Couples partner plots saved:", couples_partner_plot_paths)
#%% 
