
import pandas as pd
from pathlib import Path

# Input Excel file and output text file paths

excel_path = Path("Data/DRD_FR_2021_c2.xls")
output_path = Path("outputs/DRD_FR_2021_c2_export.txt")

try:
    with open(output_path, "w", encoding="utf-8") as f:
        x = pd.read_excel(excel_path, sheet_name=None, dtype=str)
        for name, df in x.items():
            df = df.fillna("")
            f.write(f"=== Sheet: {name} ===\n")
            df.to_csv(f, sep="\t", index=False, lineterminator="\n")
            f.write("\n")
    print(f"Saved to {output_path}")
except Exception as e:
    print(f"Error: {e}")
