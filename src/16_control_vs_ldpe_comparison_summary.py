import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 66: Explicit Control vs LDPE Comparison Summary
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
TABLE_DIR = BASE_DIR / "outputs" / "tables"

MASTER_FILE = TABLE_DIR / "master_results_table.csv"
OUTPUT_FILE = TABLE_DIR / "control_vs_ldpe_comparison_summary.csv"

master = pd.read_csv(MASTER_FILE)


def get_result(evidence_type, comparison, metric):

    subset = master[
        master["Evidence Type"].eq(evidence_type)
        &
        master["Comparison / Session"].eq(comparison)
        &
        master["Metric"].eq(metric)
    ]

    if len(subset) != 1:
        raise ValueError(
            f"Expected one result for "
            f"{evidence_type} | {comparison} | {metric}. "
            f"Found {len(subset)}."
        )

    return subset.iloc[0]["Result"]


# ------------------------------------------------------------
# Matched 24 August direct comparison
# ------------------------------------------------------------

temperature = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Temperature",
)

humidity = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Humidity",
)

soil = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Soil Moisture",
)

ph = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "pH",
)

electrical = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Electrical Activity",
)


rows = [
    {
        "Variable": "Temperature",
        "Control – No Plastic": temperature.split(";")[0].strip(),
        "LDPE – Plastic Exposed": temperature.split(";")[1].strip(),
        "Comparative Result": ";".join(
            temperature.split(";")[2:]
        ).strip(),
    },

    {
        "Variable": "Humidity",
        "Control – No Plastic": humidity.split(";")[0].strip(),
        "LDPE – Plastic Exposed": humidity.split(";")[1].strip(),
        "Comparative Result": ";".join(
            humidity.split(";")[2:]
        ).strip(),
    },

    {
        "Variable": "Soil Moisture",
        "Control – No Plastic": soil.split(";")[0].strip(),
        "LDPE – Plastic Exposed": soil.split(";")[1].strip(),
        "Comparative Result": ";".join(
            soil.split(";")[2:]
        ).strip(),
    },

    {
        "Variable": "pH",
        "Control – No Plastic": ph.split(";")[0].strip(),
        "LDPE – Plastic Exposed": ph.split(";")[1].strip(),
        "Comparative Result": ";".join(
            ph.split(";")[2:]
        ).strip(),
    },

    {
        "Variable": "Electrical Activity",
        "Control – No Plastic": electrical.split(";")[0].strip(),
        "LDPE – Plastic Exposed": electrical.split(";")[1].strip(),
        "Comparative Result": ";".join(
            electrical.split(";")[2:]
        ).strip(),
    },
]


comparison = pd.DataFrame(rows)

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print()
print("Control – No Plastic vs LDPE – Plastic Exposed")
print("=" * 100)

print()
print(
    comparison.to_string(
        index=False
    )
)

print()
print("=" * 100)

print("Validation checks")
print("-" * 100)

print(
    "Control label correct              :",
    "Control – No Plastic"
    in comparison.columns
)

print(
    "LDPE label correct                 :",
    "LDPE – Plastic Exposed"
    in comparison.columns
)

print(
    "Five variables compared            :",
    len(comparison) == 5
)

print(
    "Electrical comparison included     :",
    comparison["Variable"]
    .eq("Electrical Activity")
    .any()
)

print(
    "Soil comparison included           :",
    comparison["Variable"]
    .eq("Soil Moisture")
    .any()
)

print(
    "No missing comparison values       :",
    comparison.notna().all().all()
)

print()
print("Comparison summary saved to:")
print(f"  {OUTPUT_FILE}")

