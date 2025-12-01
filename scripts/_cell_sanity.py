import pandas as pd

singles_long = pd.read_parquet(r"U:\EUROMOD-STORAGE\Data\processed\fr\2021\singles_RURO_ready_RURO_draws.parquet")
couples_long = pd.read_parquet(r"U:\EUROMOD-STORAGE\Data\processed\fr\2021\couples_RURO_ready_RURO_draws.parquet")

for name, df in [("singles", singles_long), ("couples", couples_long)]:
    print(f"\n=== {name} ===")
    print(df[["idperson","draw","is_chosen"]].groupby("idperson").agg(
        n_alts = ("draw","size"),
        chosen_sum = ("is_chosen","sum"),
        draw_min = ("draw","min"),
        draw_max = ("draw","max"),
    ).describe())
    print("\nHours, wage, loc (first few rows):")
    print(df[["draw","hours","wage","loc"]].head())
