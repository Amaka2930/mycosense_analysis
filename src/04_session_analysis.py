import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 51: Session-Aware Time-Series Structure
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CONTROL_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "mycosense_control_analysis_ready.csv"
)

LDPE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "mycosense_ldpe_analysis_ready.csv"
)


# ------------------------------------------------------------
# Load processed datasets
# ------------------------------------------------------------

control = pd.read_csv(CONTROL_FILE)
ldpe = pd.read_csv(LDPE_FILE)


def prepare_timestamps(data):

    data = data.copy()

    data["Timestamp UTC"] = pd.to_datetime(
        data["Timestamp UTC"],
        utc=True,
        errors="coerce"
    )

    data = data.sort_values(
        "Timestamp UTC"
    ).reset_index(drop=True)

    return data


control = prepare_timestamps(control)
ldpe = prepare_timestamps(ldpe)


# ------------------------------------------------------------
# Session identification
#
# A new session begins when:
#   1. the record is the first record, OR
#   2. more than 10 minutes have elapsed since the previous
#      timestamp.
#
# The 10-minute threshold is an operational segmentation rule.
# ------------------------------------------------------------

SESSION_GAP_MINUTES = 10


def assign_sessions(data):

    data = data.copy()

    data["Gap Minutes"] = (
        data["Timestamp UTC"]
        .diff()
        .dt.total_seconds()
        .div(60)
    )

    data["New Session"] = (
        data["Gap Minutes"].isna()
        |
        data["Gap Minutes"].gt(
            SESSION_GAP_MINUTES
        )
    )

    data["Session ID"] = (
        data["New Session"]
        .cumsum()
        .astype(int)
    )

    return data


control = assign_sessions(control)
ldpe = assign_sessions(ldpe)


# ------------------------------------------------------------
# Build session summary
# ------------------------------------------------------------

def build_session_summary(data, condition):

    rows = []

    for session_id, session in data.groupby(
        "Session ID",
        sort=True
    ):

        start = session["Timestamp UTC"].min()
        end = session["Timestamp UTC"].max()

        duration_minutes = (
            end - start
        ).total_seconds() / 60

        rows.append(
            {
                "Condition": condition,
                "Session ID": int(session_id),
                "Date": start.date(),
                "Start UTC": start,
                "End UTC": end,
                "Duration Minutes": duration_minutes,
                "Total Records": len(session),

                "Temperature Valid n":
                    session[
                        "Temperature Analysis (C)"
                    ].notna().sum(),

                "Humidity Valid n":
                    session[
                        "Humidity Analysis (%)"
                    ].notna().sum(),

                "Soil Valid n":
                    session[
                        "Soil Moisture Analysis (%)"
                    ].notna().sum(),

                "pH Valid n":
                    session[
                        "pH Analysis"
                    ].notna().sum(),

                "Electrical Valid n":
                    session[
                        "Electrical Analysis (mV)"
                    ].notna().sum(),
            }
        )

    return pd.DataFrame(rows)


control_sessions = build_session_summary(
    control,
    "Control"
)

ldpe_sessions = build_session_summary(
    ldpe,
    "LDPE"
)

session_summary = pd.concat(
    [
        control_sessions,
        ldpe_sessions
    ],
    ignore_index=True
)


# ------------------------------------------------------------
# Print session structure
# ------------------------------------------------------------

print()
print("Session-Aware Time-Series Validation")
print("-" * 70)

print()
print(
    f"Operational session gap threshold : "
    f">{SESSION_GAP_MINUTES} minutes"
)

print(
    f"Control sessions                  : "
    f"{control['Session ID'].nunique()}"
)

print(
    f"LDPE sessions                     : "
    f"{ldpe['Session ID'].nunique()}"
)


# ------------------------------------------------------------
# Detailed summary
# ------------------------------------------------------------

for condition, summary in [
    ("Control", control_sessions),
    ("LDPE", ldpe_sessions),
]:

    print()
    print(condition)
    print("-" * 70)

    for _, row in summary.iterrows():

        print()
        print(
            f"Session {int(row['Session ID'])}"
        )

        print(
            f"  Date              : "
            f"{row['Date']}"
        )

        print(
            f"  Start UTC         : "
            f"{row['Start UTC']}"
        )

        print(
            f"  End UTC           : "
            f"{row['End UTC']}"
        )

        print(
            f"  Duration          : "
            f"{row['Duration Minutes']:.2f} minutes"
        )

        print(
            f"  Total records     : "
            f"{int(row['Total Records'])}"
        )

        print(
            f"  Temperature valid : "
            f"{int(row['Temperature Valid n'])}"
        )

        print(
            f"  Humidity valid    : "
            f"{int(row['Humidity Valid n'])}"
        )

        print(
            f"  Soil valid        : "
            f"{int(row['Soil Valid n'])}"
        )

        print(
            f"  pH valid          : "
            f"{int(row['pH Valid n'])}"
        )

        print(
            f"  Electrical valid  : "
            f"{int(row['Electrical Valid n'])}"
        )


# ------------------------------------------------------------
# Validation checks
# ------------------------------------------------------------

print()
print("Session Integrity Checks")
print("-" * 70)

control_records_from_sessions = (
    control
    .groupby("Session ID")
    .size()
    .sum()
)

ldpe_records_from_sessions = (
    ldpe
    .groupby("Session ID")
    .size()
    .sum()
)


print(
    "Control records preserved :",
    control_records_from_sessions
    == len(control)
)

print(
    "LDPE records preserved    :",
    ldpe_records_from_sessions
    == len(ldpe)
)


control_gap_check = (
    control.loc[
        ~control["New Session"],
        "Gap Minutes"
    ]
    .le(SESSION_GAP_MINUTES)
    .all()
)

ldpe_gap_check = (
    ldpe.loc[
        ~ldpe["New Session"],
        "Gap Minutes"
    ]
    .le(SESSION_GAP_MINUTES)
    .all()
)


print(
    "Control within-session gaps valid :",
    control_gap_check
)

print(
    "LDPE within-session gaps valid    :",
    ldpe_gap_check
)


# ------------------------------------------------------------
# Check total valid measurements against Step 50
# ------------------------------------------------------------

print()
print("Valid Measurement Cross-Check")
print("-" * 70)

variables = {
    "Temperature":
        "Temperature Analysis (C)",

    "Humidity":
        "Humidity Analysis (%)",

    "Soil moisture":
        "Soil Moisture Analysis (%)",

    "pH":
        "pH Analysis",

    "Electrical":
        "Electrical Analysis (mV)",
}


for label, column in variables.items():

    control_n = (
        control[column]
        .notna()
        .sum()
    )

    ldpe_n = (
        ldpe[column]
        .notna()
        .sum()
    )

    print(
        f"{label:<15} | "
        f"Control={control_n:>4} | "
        f"LDPE={ldpe_n:>4}"
    )


# ------------------------------------------------------------
# Save session summary
# ------------------------------------------------------------

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "session_structure_summary.csv"
)

session_summary.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("Session summary created:")
print(f"  {OUTPUT_FILE}")
