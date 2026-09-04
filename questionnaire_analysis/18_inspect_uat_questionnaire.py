import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "mycosense_uat_raw.csv"

df = pd.read_csv(RAW_FILE)

print()
print("MYCOSENSE UAT QUESTIONNAIRE - RAW DATA INSPECTION")
print("=" * 90)

print()
print("Dataset shape:")
print(df.shape)

print()
print("Column names:")
for i, col in enumerate(df.columns, start=1):
    print(f"{i:02d}. {col}")

print()
print("First 8 rows:")
print(df.head(8).to_string())

print()
print("Response type / status values:")
for col in ["Status", "Finished", "Progress", "DistributionChannel"]:
    if col in df.columns:
        print()
        print(f"{col}:")
        print(df[col].value_counts(dropna=False))

print()
print("Possible Qualtrics metadata rows:")
print(df.iloc[:3].to_string())

print()
print("Consent and eligibility fields:")
for col in ["Q12", "Q13"]:
    if col in df.columns:
        print()
        print(f"{col}:")
        print(df[col].value_counts(dropna=False))

print()
print("Likert questions detected:")
likert_cols = [
    col for col in df.columns
    if col.startswith("Q14_")
]
print(likert_cols)

print()
print("Open-text questions detected:")
open_cols = [
    col for col in df.columns
    if col.startswith("Q16_")
]
print(open_cols)

print()
print("Overall suitability question:")
if "Q18" in df.columns:
    print(df["Q18"].value_counts(dropna=False))

print()
print("=" * 90)
print("Inspection complete.")
