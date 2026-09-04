import pandas as pd
import numpy as np
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 52: Robust Session-Level Descriptive Statistics
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

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "session_robust_descriptive_statistics.csv"
)


# ------------------------------------------------------------
# Load datasets
# ------------------------------------------------------------

control = pd.read_csv(CONTROL_FILE)
ldpe = pd.read_csv(LDPE_FILE)


def prepare_data(data):

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


control = prepare_data(control)
ldpe = prepare_data(ldpe)


# ------------------------------------------------------------
# Assign monitoring sessions using the same operational rule
# established and validated in Step 51.
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
# Analysis variables
# ------------------------------------------------------------

VARIABLES = {
    "Temperature":
        "Temperature Analysis (C)",

    "Humidity":
        "Humidity Analysis (%)",

    "Soil Moisture":
        "Soil Moisture Analysis (%)",

    "pH":
        "pH Analysis",

    "Electrical Activity":
        "Electrical Analysis (mV)",
}


# ------------------------------------------------------------
# Robust descriptive statistics
# ------------------------------------------------------------

def calculate_statistics(series):

    values = (
        pd.to_numeric(
            series,
            errors="coerce"
        )
        .dropna()
    )

    n = len(values)

    if n == 0:

        return {
            "Valid n": 0,
            "Mean": np.nan,
            "SD": np.nan,
            "Median": np.nan,
            "Q1": np.nan,
            "Q3": np.nan,
            "IQR": np.nan,
            "Min": np.nan,
            "Max": np.nan,
        }

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)

    return {
        "Valid n": n,
        "Mean": values.mean(),

        "SD":
            values.std(ddof=1)
            if n > 1
            else np.nan,

        "Median": values.median(),
        "Q1": q1,
        "Q3": q3,
        "IQR": q3 - q1,
        "Min": values.min(),
        "Max": values.max(),
    }


# ------------------------------------------------------------
# Build long-format session statistics table
# ------------------------------------------------------------

def build_session_statistics(data, condition):

    rows = []

    for session_id, session in data.groupby(
        "Session ID",
        sort=True
    ):

        start = session[
            "Timestamp UTC"
        ].min()

        end = session[
            "Timestamp UTC"
        ].max()

        duration = (
            end - start
        ).total_seconds() / 60

        for variable_name, column in VARIABLES.items():

            stats = calculate_statistics(
                session[column]
            )

            row = {
                "Condition": condition,
                "Session ID": int(session_id),
                "Date": start.date(),
                "Start UTC": start,
                "End UTC": end,
                "Duration Minutes": duration,
                "Total Session Records": len(session),
                "Variable": variable_name,
            }

            row.update(stats)

            rows.append(row)

    return pd.DataFrame(rows)


control_stats = build_session_statistics(
    control,
    "Control"
)

ldpe_stats = build_session_statistics(
    ldpe,
    "LDPE"
)

session_stats = pd.concat(
    [
        control_stats,
        ldpe_stats
    ],
    ignore_index=True
)


# ------------------------------------------------------------
# Save complete table
# ------------------------------------------------------------

session_stats.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print()
print("Session-Level Robust Descriptive Statistics")
print("-" * 72)

print()
print(
    f"Control sessions : "
    f"{control['Session ID'].nunique()}"
)

print(
    f"LDPE sessions    : "
    f"{ldpe['Session ID'].nunique()}"
)


expected_rows = (
    control["Session ID"].nunique()
    +
    ldpe["Session ID"].nunique()
) * len(VARIABLES)


print(
    f"Expected summary rows : "
    f"{expected_rows}"
)

print(
    f"Actual summary rows   : "
    f"{len(session_stats)}"
)

print(
    "Summary row check    :",
    len(session_stats) == expected_rows
)


# ------------------------------------------------------------
# Print compact session summaries
#
# We focus on median and IQR here because these are the primary
# robust descriptive measures for the project.
# ------------------------------------------------------------

for condition, condition_stats in [
    ("Control", control_stats),
    ("LDPE", ldpe_stats),
]:

    print()
    print(condition)
    print("=" * 72)

    session_ids = (
        condition_stats["Session ID"]
        .drop_duplicates()
        .tolist()
    )

    for session_id in session_ids:

        current = condition_stats[
            condition_stats["Session ID"]
            == session_id
        ]

        first = current.iloc[0]

        print()
        print(
            f"Session {session_id} | "
            f"{first['Date']} | "
            f"{first['Duration Minutes']:.2f} min | "
            f"{int(first['Total Session Records'])} records"
        )

        print("-" * 72)

        for _, row in current.iterrows():

            if row["Valid n"] == 0:

                print(
                    f"{row['Variable']:<21} "
                    f"n=0 | no valid measurements"
                )

            else:

                print(
                    f"{row['Variable']:<21} "
                    f"n={int(row['Valid n']):>3} | "
                    f"Median={row['Median']:>8.3f} | "
                    f"IQR={row['IQR']:>8.3f} | "
                    f"Min={row['Min']:>8.3f} | "
                    f"Max={row['Max']:>8.3f}"
                )


# ------------------------------------------------------------
# Cross-check totals against the processed datasets.
# ------------------------------------------------------------

print()
print("Valid Measurement Cross-Check")
print("-" * 72)


for variable_name, column in VARIABLES.items():

    control_expected = (
        control[column]
        .notna()
        .sum()
    )

    ldpe_expected = (
        ldpe[column]
        .notna()
        .sum()
    )

    control_observed = int(
        control_stats.loc[
            control_stats["Variable"]
            == variable_name,
            "Valid n"
        ].sum()
    )

    ldpe_observed = int(
        ldpe_stats.loc[
            ldpe_stats["Variable"]
            == variable_name,
            "Valid n"
        ].sum()
    )

    print()
    print(variable_name)

    print(
        f"  Control dataset total : "
        f"{control_expected}"
    )

    print(
        f"  Control session total : "
        f"{control_observed}"
    )

    print(
        f"  Control match         : "
        f"{control_expected == control_observed}"
    )

    print(
        f"  LDPE dataset total    : "
        f"{ldpe_expected}"
    )

    print(
        f"  LDPE session total    : "
        f"{ldpe_observed}"
    )

    print(
        f"  LDPE match            : "
        f"{ldpe_expected == ldpe_observed}"
    )


print()
print("Session statistics table created:")
print(f"  {OUTPUT_FILE}")
