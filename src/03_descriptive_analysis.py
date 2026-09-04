from pathlib import Path
import pandas as pd
import numpy as np


# ------------------------------------------------------------
# MycoSense Descriptive Analysis
# Step 48: Processed Dataset Validation and Initial Summary
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CONTROL_FILE = (
    PROCESSED_DIR /
    "mycosense_control_analysis_ready.csv"
)

LDPE_FILE = (
    PROCESSED_DIR /
    "mycosense_ldpe_analysis_ready.csv"
)


# ------------------------------------------------------------
# Load processed datasets
# ------------------------------------------------------------

control = pd.read_csv(CONTROL_FILE)
ldpe = pd.read_csv(LDPE_FILE)


# Convert timestamps back to datetime after reading CSV.
control["Timestamp UTC"] = pd.to_datetime(
    control["Timestamp UTC"],
    errors="coerce",
    utc=True
)

ldpe["Timestamp UTC"] = pd.to_datetime(
    ldpe["Timestamp UTC"],
    errors="coerce",
    utc=True
)


# ------------------------------------------------------------
# Dataset Validation
# ------------------------------------------------------------

print()
print("Processed Dataset Validation")
print("-" * 50)

print()
print("Dataset dimensions:")
print(
    f"  Control : "
    f"{control.shape[0]} rows x "
    f"{control.shape[1]} columns"
)

print(
    f"  LDPE    : "
    f"{ldpe.shape[0]} rows x "
    f"{ldpe.shape[1]} columns"
)


print()
print("Condition labels:")

print(
    "  Control :",
    control["Condition"]
    .value_counts(dropna=False)
    .to_dict()
)

print(
    "  LDPE    :",
    ldpe["Condition"]
    .value_counts(dropna=False)
    .to_dict()
)


print()
print("Timestamp validation:")

print(
    f"  Control invalid timestamps : "
    f"{control['Timestamp UTC'].isna().sum()}"
)

print(
    f"  LDPE invalid timestamps    : "
    f"{ldpe['Timestamp UTC'].isna().sum()}"
)

print(
    f"  Control chronological      : "
    f"{control['Timestamp UTC'].is_monotonic_increasing}"
)

print(
    f"  LDPE chronological         : "
    f"{ldpe['Timestamp UTC'].is_monotonic_increasing}"
)


# ------------------------------------------------------------
# Confirm that original values remain preserved
# while invalid analysis values are masked.
# ------------------------------------------------------------

print()
print("Original-versus-analysis preservation check")
print("-" * 50)

variable_pairs = [
    (
        "Temperature",
        "Temperature (C)",
        "Temperature Analysis (C)",
        "Temperature Valid"
    ),
    (
        "Humidity",
        "Humidity (%)",
        "Humidity Analysis (%)",
        "Humidity Valid"
    ),
    (
        "Soil moisture",
        "Soil Moisture (%)",
        "Soil Moisture Analysis (%)",
        "Soil Valid"
    ),
    (
        "pH",
        "pH",
        "pH Analysis",
        "pH Valid"
    ),
    (
        "Electrical",
        "Electrical Activity (mV)",
        "Electrical Analysis (mV)",
        "Electrical Valid"
    )
]


def preservation_check(df, label):

    print()
    print(f"{label}:")

    for (
        variable,
        original_column,
        analysis_column,
        validity_column
    ) in variable_pairs:

        original_present = int(
            df[original_column]
            .notna()
            .sum()
        )

        analysis_present = int(
            df[analysis_column]
            .notna()
            .sum()
        )

        invalid_but_original_preserved = int(
            (
                (~df[validity_column])
                &
                df[original_column].notna()
            ).sum()
        )

        valid_but_analysis_missing = int(
            (
                df[validity_column]
                &
                df[analysis_column].isna()
            ).sum()
        )

        print()
        print(f"  {variable}")
        print(
            f"    Original non-missing       : "
            f"{original_present}"
        )
        print(
            f"    Analysis non-missing       : "
            f"{analysis_present}"
        )
        print(
            f"    Preserved but not analysed : "
            f"{invalid_but_original_preserved}"
        )
        print(
            f"    ERROR valid-but-masked     : "
            f"{valid_but_analysis_missing}"
        )


preservation_check(
    control,
    "Control"
)

preservation_check(
    ldpe,
    "LDPE"
)


# ------------------------------------------------------------
# Initial Robust Descriptive Statistics
#
# These are descriptive summaries of repeated observations.
# They must NOT be interpreted as independent biological
# replicates.
# ------------------------------------------------------------

print()
print("Initial Robust Descriptive Statistics")
print("-" * 50)


analysis_variables = [
    (
        "Temperature (C)",
        "Temperature Analysis (C)"
    ),
    (
        "Humidity (%)",
        "Humidity Analysis (%)"
    ),
    (
        "Soil Moisture (%)",
        "Soil Moisture Analysis (%)"
    ),
    (
        "pH",
        "pH Analysis"
    ),
    (
        "Electrical Activity (mV)",
        "Electrical Analysis (mV)"
    )
]


def robust_summary(series):

    clean = series.dropna()

    if clean.empty:

        return {
            "n": 0,
            "mean": np.nan,
            "sd": np.nan,
            "median": np.nan,
            "q1": np.nan,
            "q3": np.nan,
            "iqr": np.nan,
            "min": np.nan,
            "max": np.nan
        }

    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)

    return {
        "n": len(clean),
        "mean": clean.mean(),
        "sd": clean.std(ddof=1),
        "median": clean.median(),
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "min": clean.min(),
        "max": clean.max()
    }


summary_rows = []

for condition, dataset in [
    ("Control", control),
    ("LDPE", ldpe)
]:

    for variable_name, column in analysis_variables:

        stats = robust_summary(
            dataset[column]
        )

        summary_rows.append(
            {
                "Condition": condition,
                "Variable": variable_name,
                **stats
            }
        )


summary_df = pd.DataFrame(
    summary_rows
)


for _, row in summary_df.iterrows():

    print()
    print(
        f"{row['Condition']} | "
        f"{row['Variable']}"
    )

    print(
        f"  n      : {int(row['n'])}"
    )

    print(
        f"  Mean   : {row['mean']:.3f}"
    )

    print(
        f"  SD     : {row['sd']:.3f}"
    )

    print(
        f"  Median : {row['median']:.3f}"
    )

    print(
        f"  Q1     : {row['q1']:.3f}"
    )

    print(
        f"  Q3     : {row['q3']:.3f}"
    )

    print(
        f"  IQR    : {row['iqr']:.3f}"
    )

    print(
        f"  Min    : {row['min']:.3f}"
    )

    print(
        f"  Max    : {row['max']:.3f}"
    )


# ------------------------------------------------------------
# Save the descriptive-statistics table
# ------------------------------------------------------------

TABLES_DIR = (
    PROJECT_ROOT /
    "outputs" /
    "tables"
)

TABLES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

summary_output = (
    TABLES_DIR /
    "initial_robust_descriptive_statistics.csv"
)

summary_df.to_csv(
    summary_output,
    index=False
)


print()
print("Summary table created:")
print(f"  {summary_output}")

# ------------------------------------------------------------
# Step 49: Remaining LDPE Very-Low Soil Assessment
# ------------------------------------------------------------

print()
print("LDPE Remaining Very-Low Soil Assessment")
print("-" * 50)


# ------------------------------------------------------------
# Select LDPE records where the soil measurement is currently
# considered analytically valid but remains unusually low.
#
# <= 5% is used here ONLY as a diagnostic inspection threshold.
# It is NOT a cleaning rule.
# ------------------------------------------------------------

ldpe_low_soil = ldpe[
    ldpe["Soil Valid"]
    &
    ldpe["Soil Moisture Analysis (%)"].notna()
    &
    ldpe["Soil Moisture Analysis (%)"].le(5)
].copy()


print()
print(
    "Currently valid LDPE soil readings <= 5% : "
    f"{len(ldpe_low_soil)}"
)


if not ldpe_low_soil.empty:

    print()
    print("Date distribution:")

    low_soil_dates = (
        ldpe_low_soil["Timestamp UTC"]
        .dt.date
        .value_counts()
        .sort_index()
    )

    for date, count in low_soil_dates.items():

        print(
            f"  {date} : {count} records"
        )


    print()
    print("Chronological records:")

    display_columns = [
        "ID",
        "Timestamp UTC",
        "Soil Moisture (%)",
        "Soil Moisture Analysis (%)",
        "Electrical Activity (mV)",
        "Electrical Analysis (mV)",
        "Temperature (C)",
        "Humidity (%)",
        "Device ID"
    ]

    display = ldpe_low_soil[
        display_columns
    ].copy()

    display["Time UTC"] = (
        display["Timestamp UTC"]
        .dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        .str[:-3]
    )

    display = display[
        [
            "ID",
            "Time UTC",
            "Soil Moisture (%)",
            "Soil Moisture Analysis (%)",
            "Electrical Activity (mV)",
            "Electrical Analysis (mV)",
            "Temperature (C)",
            "Humidity (%)",
            "Device ID"
        ]
    ]

    print(
        display.to_string(
            index=False
        )
    )


    # --------------------------------------------------------
    # Summarise the low-soil records.
    # --------------------------------------------------------

    print()
    print("Low-soil summary:")

    print(
        f"  Minimum soil       : "
        f"{ldpe_low_soil['Soil Moisture Analysis (%)'].min():.3f}%"
    )

    print(
        f"  Median soil        : "
        f"{ldpe_low_soil['Soil Moisture Analysis (%)'].median():.3f}%"
    )

    print(
        f"  Maximum soil       : "
        f"{ldpe_low_soil['Soil Moisture Analysis (%)'].max():.3f}%"
    )

    electrical_available = (
        ldpe_low_soil[
            "Electrical Activity (mV)"
        ]
        .dropna()
    )

    if not electrical_available.empty:

        print(
            f"  Electrical minimum : "
            f"{electrical_available.min():.3f} mV"
        )

        print(
            f"  Electrical median  : "
            f"{electrical_available.median():.3f} mV"
        )

        print(
            f"  Electrical maximum : "
            f"{electrical_available.max():.3f} mV"
        )


# ------------------------------------------------------------
# Inspect ALL LDPE 25 August records that were NOT classified
# as the combined extreme fault state.
#
# This helps determine whether the remaining soil values are
# isolated measurements or brief returns between fault states.
# ------------------------------------------------------------

print()
print("LDPE 25 August Non-Fault-Candidate Soil Assessment")
print("-" * 50)

ldpe_aug25 = ldpe[
    ldpe["Timestamp UTC"].dt.date.eq(
        pd.Timestamp("2026-08-25").date()
    )
].copy()


ldpe_aug25_non_extreme = ldpe_aug25[
    ~(
        ldpe_aug25["Soil Moisture (%)"].le(1)
        &
        ldpe_aug25[
            "Electrical Activity (mV)"
        ].abs().ge(1000)
    )
].copy()


print()
print(
    "25 August total records                 : "
    f"{len(ldpe_aug25)}"
)

print(
    "25 August records outside combined fault: "
    f"{len(ldpe_aug25_non_extreme)}"
)


print()
print("Remaining measurement combinations:")


print(
    ldpe_aug25_non_extreme[
        [
            "ID",
            "Timestamp UTC",
            "Soil Moisture (%)",
            "Electrical Activity (mV)",
            "Soil Valid",
            "Electrical Valid"
        ]
    ]
    .sort_values("Timestamp UTC")
    .to_string(index=False)
)

