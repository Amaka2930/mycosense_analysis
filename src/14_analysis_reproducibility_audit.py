from pathlib import Path
import pandas as pd


# ------------------------------------------------------------
# MycoSense
# Step 61: Analysis Completeness and Reproducibility Audit
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

SRC_DIR = BASE_DIR / "src"
TABLE_DIR = BASE_DIR / "outputs" / "tables"
FIGURE_DIR = BASE_DIR / "outputs" / "figures"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = (
    TABLE_DIR
    / "analysis_reproducibility_audit.csv"
)


# ------------------------------------------------------------
# Expected scripts
# ------------------------------------------------------------

expected_scripts = [

    "01_inspect_raw_data.py",
    "02_prepare_analysis_data.py",
    "03_descriptive_analysis.py",
    "04_session_analysis.py",
    "05_session_descriptive_statistics.py",
    "06_time_series_visualisation.py",
    "07_electrical_signal_features.py",
    "08_environmental_association_analysis.py",
    "09_matched_session_comparison.py",
    "10_sensitivity_analysis.py",
    "11_master_results_table.py",
    "12_integrated_evidence_assessment.py",
    "13_research_question_evidence_matrix.py",
    "14_analysis_reproducibility_audit.py",
]


# ------------------------------------------------------------
# Expected processed datasets
# ------------------------------------------------------------

expected_processed = [

    "mycosense_control_analysis_ready.csv",
    "mycosense_ldpe_analysis_ready.csv",
    "mycosense_combined_analysis_ready.csv",
]


# ------------------------------------------------------------
# Expected tables
# ------------------------------------------------------------

expected_tables = [

    "initial_robust_descriptive_statistics.csv",
    "session_structure_summary.csv",
    "session_robust_descriptive_statistics.csv",
    "electrical_signal_features_by_session.csv",
    "environmental_electrical_spearman_correlations.csv",
    "matched_24_august_comparison.csv",
    "sensitivity_analysis_by_session.csv",
    "sensitivity_analysis_cleaning_impact.csv",
    "master_results_table.csv",
    "integrated_evidence_assessment.csv",
    "research_question_evidence_matrix.csv",
]


# ------------------------------------------------------------
# Expected figures
# ------------------------------------------------------------

expected_figures = [

    "control_electrical_activity_by_session.png",
    "ldpe_electrical_activity_by_session.png",

    "control_soil_moisture_by_session.png",
    "ldpe_soil_moisture_by_session.png",

    "control_temperature_by_session.png",
    "ldpe_temperature_by_session.png",

    "control_humidity_by_session.png",
    "ldpe_humidity_by_session.png",

    "control_ph_by_session.png",
    "ldpe_ph_by_session.png",

    "ldpe_21_august_electrical_diagnostic.png",
    "matched_24_august_electrical_comparison.png",
]


# ------------------------------------------------------------
# Audit helper
# ------------------------------------------------------------

rows = []


def audit_file(category, directory, filename):

    path = directory / filename

    exists = path.exists()

    size_bytes = (
        path.stat().st_size
        if exists
        else 0
    )

    nonempty = (
        size_bytes > 0
        if exists
        else False
    )

    rows.append(
        {
            "Category": category,
            "File": filename,
            "Exists": exists,
            "Nonempty": nonempty,
            "Size Bytes": size_bytes,
        }
    )


# ------------------------------------------------------------
# Audit scripts
# ------------------------------------------------------------

for filename in expected_scripts:

    audit_file(
        "Analysis Script",
        SRC_DIR,
        filename,
    )


# ------------------------------------------------------------
# Audit processed datasets
# ------------------------------------------------------------

for filename in expected_processed:

    audit_file(
        "Processed Dataset",
        PROCESSED_DIR,
        filename,
    )


# ------------------------------------------------------------
# Audit output tables
# ------------------------------------------------------------

for filename in expected_tables:

    audit_file(
        "Analysis Table",
        TABLE_DIR,
        filename,
    )


# ------------------------------------------------------------
# Audit figures
# ------------------------------------------------------------

for filename in expected_figures:

    audit_file(
        "Analysis Figure",
        FIGURE_DIR,
        filename,
    )


audit = pd.DataFrame(rows)


# ------------------------------------------------------------
# Additional CSV validation
# ------------------------------------------------------------

csv_rows = []

csv_targets = (

    [
        (
            "Processed Dataset",
            PROCESSED_DIR / filename
        )
        for filename in expected_processed
    ]

    +

    [
        (
            "Analysis Table",
            TABLE_DIR / filename
        )
        for filename in expected_tables
    ]
)


for category, path in csv_targets:

    if not path.exists():

        csv_rows.append(
            {
                "Category": category,
                "File": path.name,
                "CSV Readable": False,
                "Rows": 0,
                "Columns": 0,
            }
        )

        continue

    try:

        df = pd.read_csv(path)

        csv_rows.append(
            {
                "Category": category,
                "File": path.name,
                "CSV Readable": True,
                "Rows": len(df),
                "Columns": len(df.columns),
            }
        )

    except Exception:

        csv_rows.append(
            {
                "Category": category,
                "File": path.name,
                "CSV Readable": False,
                "Rows": 0,
                "Columns": 0,
            }
        )


csv_audit = pd.DataFrame(csv_rows)


# ------------------------------------------------------------
# Merge CSV audit information
# ------------------------------------------------------------

audit = audit.merge(
    csv_audit,
    on=[
        "Category",
        "File"
    ],
    how="left"
)


# ------------------------------------------------------------
# Status classification
# ------------------------------------------------------------

def classify_status(row):

    if not row["Exists"]:
        return "MISSING"

    if not row["Nonempty"]:
        return "EMPTY"

    if pd.notna(row["CSV Readable"]):

        if not bool(row["CSV Readable"]):
            return "CSV READ ERROR"

        if row["Rows"] == 0:
            return "CSV HAS NO ROWS"

    return "PASS"


audit["Status"] = audit.apply(
    classify_status,
    axis=1
)


# ------------------------------------------------------------
# Save audit
# ------------------------------------------------------------

audit.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Summary calculations
# ------------------------------------------------------------

total_items = len(audit)

passed_items = (
    audit["Status"].eq("PASS").sum()
)

failed_items = (
    total_items - passed_items
)

all_scripts_present = (
    audit.loc[
        audit["Category"].eq(
            "Analysis Script"
        ),
        "Status"
    ]
    .eq("PASS")
    .all()
)

all_processed_present = (
    audit.loc[
        audit["Category"].eq(
            "Processed Dataset"
        ),
        "Status"
    ]
    .eq("PASS")
    .all()
)

all_tables_present = (
    audit.loc[
        audit["Category"].eq(
            "Analysis Table"
        ),
        "Status"
    ]
    .eq("PASS")
    .all()
)

all_figures_present = (
    audit.loc[
        audit["Category"].eq(
            "Analysis Figure"
        ),
        "Status"
    ]
    .eq("PASS")
    .all()
)

all_csv_readable = (
    csv_audit[
        "CSV Readable"
    ]
    .eq(True)
    .all()
)

all_csv_have_rows = (
    csv_audit[
        "Rows"
    ]
    .gt(0)
    .all()
)


# ------------------------------------------------------------
# Print results
# ------------------------------------------------------------

print()
print("MycoSense Analysis Reproducibility Audit")
print("=" * 88)

print()

print(
    f"Total audited items : {total_items}"
)

print(
    f"Passed items        : {passed_items}"
)

print(
    f"Failed items        : {failed_items}"
)


print()
print("Category summary")
print("-" * 88)

category_summary = (
    audit
    .groupby("Category")
    ["Status"]
    .value_counts()
)

print(
    category_summary.to_string()
)


print()
print("Validation checks")
print("-" * 88)

print(
    "All analysis scripts present       :",
    all_scripts_present
)

print(
    "All processed datasets present     :",
    all_processed_present
)

print(
    "All analysis tables present        :",
    all_tables_present
)

print(
    "All analysis figures present       :",
    all_figures_present
)

print(
    "All CSV files readable             :",
    all_csv_readable
)

print(
    "All CSV files contain data rows    :",
    all_csv_have_rows
)


print()
print("CSV dimensions")
print("-" * 88)

print(
    csv_audit[
        [
            "File",
            "Rows",
            "Columns",
            "CSV Readable"
        ]
    ]
    .to_string(
        index=False
    )
)


failed = audit[
    ~audit["Status"].eq("PASS")
]


print()
print("Failed audit items")
print("-" * 88)

if failed.empty:

    print(
        "None - all expected analytical "
        "artifacts passed the audit."
    )

else:

    print(
        failed[
            [
                "Category",
                "File",
                "Status"
            ]
        ]
        .to_string(
            index=False
        )
    )


print()
print("=" * 88)

print(
    "Audit file created:"
)

print(
    f"  {OUTPUT_FILE}"
)
