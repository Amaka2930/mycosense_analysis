from pathlib import Path
import pandas as pd
import numpy as np


# ------------------------------------------------------------
# MycoSense Analysis-Ready Dataset Preparation
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CONTROL_FILE = RAW_DIR / "mycosense-control-2026-08-25.csv"
LDPE_FILE = RAW_DIR / "mycosense-ldpe_exposed-2026-08-25.csv"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# Load raw data
# ------------------------------------------------------------

control = pd.read_csv(CONTROL_FILE)
ldpe = pd.read_csv(LDPE_FILE)


def prepare_dataset(df, condition):

    data = df.copy()

    # --------------------------------------------------------
    # Timestamp preparation
    # --------------------------------------------------------

    data["Timestamp UTC"] = pd.to_datetime(
        data["Created At"],
        errors="coerce",
        utc=True
    )

    data = (
        data
        .sort_values("Timestamp UTC")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Biological record flag
    #
    # E2E records are software/system tests rather than
    # biological experimental observations.
    # --------------------------------------------------------

    data["Biological Record"] = ~data[
        "Device ID"
    ].astype(str).str.startswith(
        "e2e-",
        na=False
    )

    # --------------------------------------------------------
    # Temperature validity
    # --------------------------------------------------------

    data["Temperature Valid"] = (
        data["Temperature (C)"].notna()
        &
        data["Biological Record"]
    )

    # --------------------------------------------------------
    # Humidity validity
    # --------------------------------------------------------

    data["Humidity Valid"] = (
        data["Humidity (%)"].notna()
        &
        data["Biological Record"]
    )

    # --------------------------------------------------------
    # Soil-moisture validity
    # --------------------------------------------------------

    data["Soil Valid"] = (
        data["Soil Moisture (%)"].notna()
        &
        data["Biological Record"]
    )

    if condition == "Control":

        control_zero_soil = (
            data["Timestamp UTC"].dt.date.eq(
                pd.Timestamp("2026-08-21").date()
            )
            &
            data["Soil Moisture (%)"].eq(0)
        )

        data.loc[
            control_zero_soil,
            "Soil Valid"
        ] = False

    if condition == "LDPE":

        # The complete LDPE soil-moisture session on
        # 25 August is excluded from the primary quantitative
        # soil analysis. Diagnostic assessment showed repeated
        # switching between approximately 0-1% and 100% during
        # the same session, so the CSV evidence cannot establish
        # which soil-moisture state was reliable.
        #
        # This rule applies ONLY to soil moisture. Other sensor
        # variables retain their own validity rules.

        ldpe_aug25_soil_unstable = (
            data["Timestamp UTC"].dt.date.eq(
                pd.Timestamp("2026-08-25").date()
            )
            &
            data["Soil Moisture (%)"].notna()
        )

        data.loc[
            ldpe_aug25_soil_unstable,
            "Soil Valid"
        ] = False

    # --------------------------------------------------------
    # pH validity
    #
    # Only variable mycosense-pi-01 pH measurements are
    # currently eligible for quantitative pH analysis.
    # Fixed/reference-like values remain preserved.
    # --------------------------------------------------------

    data["pH Valid"] = (
        data["pH"].notna()
        &
        data["Device ID"].eq("mycosense-pi-01")
        &
        data["Biological Record"]
    )

    # --------------------------------------------------------
    # Electrical-activity validity
    # --------------------------------------------------------

    data["Electrical Valid"] = (
        data["Electrical Activity (mV)"].notna()
        &
        data["Biological Record"]
    )

    if condition == "LDPE":

        ldpe_electrical_fault = (
            data["Timestamp UTC"].dt.date.eq(
                pd.Timestamp("2026-08-25").date()
            )
            &
            data["Soil Moisture (%)"].le(1)
            &
            data["Electrical Activity (mV)"].abs().ge(1000)
        )

        data.loc[
            ldpe_electrical_fault,
            "Electrical Valid"
        ] = False

    # --------------------------------------------------------
    # Analysis columns
    #
    # Original values remain untouched.
    # Invalid measurements become NaN ONLY in these separate
    # analysis columns.
    # --------------------------------------------------------

    data["Temperature Analysis (C)"] = (
        data["Temperature (C)"].where(
            data["Temperature Valid"]
        )
    )

    data["Humidity Analysis (%)"] = (
        data["Humidity (%)"].where(
            data["Humidity Valid"]
        )
    )

    data["Soil Moisture Analysis (%)"] = (
        data["Soil Moisture (%)"].where(
            data["Soil Valid"]
        )
    )

    data["pH Analysis"] = (
        data["pH"].where(
            data["pH Valid"]
        )
    )

    data["Electrical Analysis (mV)"] = (
        data["Electrical Activity (mV)"].where(
            data["Electrical Valid"]
        )
    )

    # --------------------------------------------------------
    # Condition label
    # --------------------------------------------------------

    data["Condition"] = condition

    return data


control_processed = prepare_dataset(
    control,
    "Control"
)

ldpe_processed = prepare_dataset(
    ldpe,
    "LDPE"
)


# ------------------------------------------------------------
# Save separate processed datasets
# ------------------------------------------------------------

control_output = (
    PROCESSED_DIR /
    "mycosense_control_analysis_ready.csv"
)

ldpe_output = (
    PROCESSED_DIR /
    "mycosense_ldpe_analysis_ready.csv"
)

control_processed.to_csv(
    control_output,
    index=False
)

ldpe_processed.to_csv(
    ldpe_output,
    index=False
)


# ------------------------------------------------------------
# Create combined analytical dataset
# ------------------------------------------------------------

combined = pd.concat(
    [
        control_processed,
        ldpe_processed
    ],
    ignore_index=True
)

combined = (
    combined
    .sort_values(
        ["Timestamp UTC", "Condition"]
    )
    .reset_index(drop=True)
)

combined_output = (
    PROCESSED_DIR /
    "mycosense_combined_analysis_ready.csv"
)

combined.to_csv(
    combined_output,
    index=False
)


# ------------------------------------------------------------
# Validation report
# ------------------------------------------------------------

print()
print("Analysis-Ready Dataset Preparation")
print("-" * 50)

print()
print("Original row counts:")
print(f"  Control : {len(control)}")
print(f"  LDPE    : {len(ldpe)}")
print(f"  Total   : {len(control) + len(ldpe)}")

print()
print("Processed row counts:")
print(f"  Control : {len(control_processed)}")
print(f"  LDPE    : {len(ldpe_processed)}")
print(f"  Combined: {len(combined)}")

print()
print("Biological records:")
print(
    f"  Control : "
    f"{int(control_processed['Biological Record'].sum())}"
)
print(
    f"  LDPE    : "
    f"{int(ldpe_processed['Biological Record'].sum())}"
)

print()
print("Analysis-ready valid measurements:")

analysis_checks = [
    (
        "Temperature",
        "Temperature Analysis (C)"
    ),
    (
        "Humidity",
        "Humidity Analysis (%)"
    ),
    (
        "Soil moisture",
        "Soil Moisture Analysis (%)"
    ),
    (
        "pH",
        "pH Analysis"
    ),
    (
        "Electrical",
        "Electrical Analysis (mV)"
    )
]

for label, column in analysis_checks:

    control_n = int(
        control_processed[column]
        .notna()
        .sum()
    )

    ldpe_n = int(
        ldpe_processed[column]
        .notna()
        .sum()
    )

    print(
        f"  {label:<15} | "
        f"Control={control_n:4d} | "
        f"LDPE={ldpe_n:4d}"
    )


# ------------------------------------------------------------
# Integrity checks
# ------------------------------------------------------------

print()
print("Integrity checks:")

control_ids_preserved = (
    set(control["ID"])
    ==
    set(control_processed["ID"])
)

ldpe_ids_preserved = (
    set(ldpe["ID"])
    ==
    set(ldpe_processed["ID"])
)

print(
    f"  Control IDs preserved : "
    f"{control_ids_preserved}"
)

print(
    f"  LDPE IDs preserved    : "
    f"{ldpe_ids_preserved}"
)

print(
    f"  Combined rows correct : "
    f"{len(combined) == len(control) + len(ldpe)}"
)

print()
print("Files created:")
print(f"  {control_output}")
print(f"  {ldpe_output}")
print(f"  {combined_output}")

