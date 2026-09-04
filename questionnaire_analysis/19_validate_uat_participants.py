import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "mycosense_uat_raw.csv"

df = pd.read_csv(RAW_FILE)

# ------------------------------------------------------------
# Remove the two Qualtrics metadata rows
# ------------------------------------------------------------

data = df.iloc[2:].copy()

print()
print("MYCOSENSE UAT - PARTICIPANT VALIDATION")
print("=" * 100)

print()
print("Rows after removing Qualtrics metadata:")
print(len(data))

print()
print("Distribution channels:")
print(data["DistributionChannel"].value_counts(dropna=False))


# ------------------------------------------------------------
# Keep only genuine anonymous survey responses
# ------------------------------------------------------------

anonymous = data[
    data["DistributionChannel"]
    .astype(str)
    .str.lower()
    .eq("anonymous")
].copy()

print()
print("=" * 100)
print("Anonymous responses only")
print("=" * 100)

print()
print("Number of anonymous responses:")
print(len(anonymous))


# ------------------------------------------------------------
# Consent variables
# ------------------------------------------------------------

consent_items = [
    "Q12_1",
    "Q12_2",
    "Q12_3",
    "Q12_4",
    "Q12_5",
    "Q12_6",
    "Q12_7",
    "Q12_8",
    "Q12_9",
]

print()
print("Consent responses by participant:")
print()

display_cols = (
    ["ResponseId", "Progress", "Finished"]
    + consent_items
    + ["Q13"]
)

print(
    anonymous[
        display_cols
    ].to_string(index=False)
)


# ------------------------------------------------------------
# Convert consent responses to numeric
# ------------------------------------------------------------

for col in consent_items + ["Q13"]:
    anonymous[col] = pd.to_numeric(
        anonymous[col],
        errors="coerce"
    )


# ------------------------------------------------------------
# Check all nine consent statements
#
# In this Qualtrics export:
# 1 = Yes
# 2 = No
# ------------------------------------------------------------

anonymous["All_Consent_Items_Yes"] = (
    anonymous[consent_items]
    .eq(1)
    .all(axis=1)
)

anonymous["Final_Consent_Yes"] = (
    anonymous["Q13"].eq(1)
)


# ------------------------------------------------------------
# Check survey completion
# ------------------------------------------------------------

anonymous["Progress_Numeric"] = pd.to_numeric(
    anonymous["Progress"],
    errors="coerce"
)

anonymous["Finished_Numeric"] = pd.to_numeric(
    anonymous["Finished"],
    errors="coerce"
)

anonymous["Completed"] = (
    anonymous["Progress_Numeric"].eq(100)
    &
    anonymous["Finished_Numeric"].eq(1)
)


# ------------------------------------------------------------
# Check Likert completion
# ------------------------------------------------------------

likert_cols = [
    f"Q14_{i}"
    for i in range(1, 11)
]

for col in likert_cols:
    anonymous[col] = pd.to_numeric(
        anonymous[col],
        errors="coerce"
    )

anonymous["Likert_Items_Answered"] = (
    anonymous[likert_cols]
    .notna()
    .sum(axis=1)
)

anonymous["All_Likert_Answered"] = (
    anonymous["Likert_Items_Answered"]
    .eq(10)
)


# ------------------------------------------------------------
# Overall validation summary
# ------------------------------------------------------------

anonymous["Valid_UAT_Response"] = (
    anonymous["Completed"]
    &
    anonymous["All_Consent_Items_Yes"]
    &
    anonymous["Final_Consent_Yes"]
    &
    anonymous["All_Likert_Answered"]
)


print()
print("=" * 100)
print("Participant validation summary")
print("=" * 100)

summary_cols = [
    "ResponseId",
    "Completed",
    "All_Consent_Items_Yes",
    "Final_Consent_Yes",
    "Likert_Items_Answered",
    "All_Likert_Answered",
    "Q18",
    "Valid_UAT_Response",
]

print()
print(
    anonymous[
        summary_cols
    ].to_string(index=False)
)

print()
print("=" * 100)
print("Counts")
print("-" * 100)

print(
    "Anonymous survey responses       :",
    len(anonymous)
)

print(
    "Completed responses              :",
    int(anonymous["Completed"].sum())
)

print(
    "All 9 consent statements = Yes   :",
    int(anonymous["All_Consent_Items_Yes"].sum())
)

print(
    "Final consent = Yes              :",
    int(anonymous["Final_Consent_Yes"].sum())
)

print(
    "All 10 Likert items answered     :",
    int(anonymous["All_Likert_Answered"].sum())
)

print(
    "VALID UAT RESPONSES              :",
    int(anonymous["Valid_UAT_Response"].sum())
)

print()
print("=" * 100)
print("Validation complete.")
