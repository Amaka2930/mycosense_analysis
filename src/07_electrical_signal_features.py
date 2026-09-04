import pandas as pd
import numpy as np
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 54: Electrical Signal Feature Analysis
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
    / "electrical_signal_features_by_session.csv"
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
# Assign sessions using the validated >10-minute rule
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
# Robust electrical feature calculation
# ------------------------------------------------------------

def calculate_electrical_features(series):

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
            "Median": np.nan,
            "SD": np.nan,
            "Q1": np.nan,
            "Q3": np.nan,
            "IQR": np.nan,
            "Mean Absolute Activity": np.nan,
            "Median Absolute Activity": np.nan,
            "Min": np.nan,
            "Max": np.nan,
            "MAD": np.nan,
            "Scaled MAD": np.nan,
            "Lower Excursion Threshold": np.nan,
            "Upper Excursion Threshold": np.nan,
            "Negative Excursion Count": 0,
            "Positive Excursion Count": 0,
            "Total Excursion Count": 0,
            "Negative Excursion Percent": np.nan,
            "Positive Excursion Percent": np.nan,
            "Total Excursion Percent": np.nan,
            "Maximum Negative Excursion": np.nan,
            "Maximum Positive Excursion": np.nan,
        }

    median = values.median()

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)

    mad = np.median(
        np.abs(
            values - median
        )
    )

    scaled_mad = 1.4826 * mad

    lower_threshold = (
        median
        - 3 * scaled_mad
    )

    upper_threshold = (
        median
        + 3 * scaled_mad
    )

    negative_excursions = values[
        values < lower_threshold
    ]

    positive_excursions = values[
        values > upper_threshold
    ]

    negative_count = len(
        negative_excursions
    )

    positive_count = len(
        positive_excursions
    )

    total_count = (
        negative_count
        + positive_count
    )

    return {
        "Valid n": n,
        "Mean": values.mean(),
        "Median": median,

        "SD":
            values.std(ddof=1)
            if n > 1
            else np.nan,

        "Q1": q1,
        "Q3": q3,
        "IQR": q3 - q1,

        "Mean Absolute Activity":
            values.abs().mean(),

        "Median Absolute Activity":
            values.abs().median(),

        "Min": values.min(),
        "Max": values.max(),

        "MAD": mad,
        "Scaled MAD": scaled_mad,

        "Lower Excursion Threshold":
            lower_threshold,

        "Upper Excursion Threshold":
            upper_threshold,

        "Negative Excursion Count":
            negative_count,

        "Positive Excursion Count":
            positive_count,

        "Total Excursion Count":
            total_count,

        "Negative Excursion Percent":
            (
                negative_count
                / n
                * 100
            ),

        "Positive Excursion Percent":
            (
                positive_count
                / n
                * 100
            ),

        "Total Excursion Percent":
            (
                total_count
                / n
                * 100
            ),

        "Maximum Negative Excursion":
            (
                negative_excursions.min()
                if negative_count > 0
                else np.nan
            ),

        "Maximum Positive Excursion":
            (
                positive_excursions.max()
                if positive_count > 0
                else np.nan
            ),
    }


# ------------------------------------------------------------
# Build session-level feature table
# ------------------------------------------------------------

def build_feature_table(
    data,
    condition
):

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

        features = (
            calculate_electrical_features(
                session[
                    "Electrical Analysis (mV)"
                ]
            )
        )

        row = {
            "Condition": condition,
            "Session ID": int(session_id),
            "Date": start.date(),
            "Start UTC": start,
            "End UTC": end,
            "Duration Minutes": duration,
            "Total Session Records": len(session),
        }

        row.update(features)

        rows.append(row)

    return pd.DataFrame(rows)


control_features = build_feature_table(
    control,
    "Control"
)

ldpe_features = build_feature_table(
    ldpe,
    "LDPE"
)

features = pd.concat(
    [
        control_features,
        ldpe_features
    ],
    ignore_index=True
)


# ------------------------------------------------------------
# Save table
# ------------------------------------------------------------

features.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Validation output
# ------------------------------------------------------------

print()
print("Electrical Signal Feature Analysis")
print("-" * 78)

print()
print(
    f"Control sessions : "
    f"{len(control_features)}"
)

print(
    f"LDPE sessions    : "
    f"{len(ldpe_features)}"
)

print(
    f"Total sessions   : "
    f"{len(features)}"
)


# ------------------------------------------------------------
# Print compact feature summaries
# ------------------------------------------------------------

for condition, condition_features in [
    ("Control", control_features),
    ("LDPE", ldpe_features),
]:

    print()
    print(condition)
    print("=" * 78)

    for _, row in condition_features.iterrows():

        print()

        print(
            f"Session {int(row['Session ID'])} | "
            f"{row['Date']} | "
            f"{row['Duration Minutes']:.2f} min"
        )

        if row["Valid n"] == 0:

            print(
                "  No valid electrical measurements"
            )

            continue

        print(
            f"  Valid n                  : "
            f"{int(row['Valid n'])}"
        )

        print(
            f"  Median                   : "
            f"{row['Median']:.3f} mV"
        )

        print(
            f"  IQR                      : "
            f"{row['IQR']:.3f} mV"
        )

        print(
            f"  SD                       : "
            f"{row['SD']:.3f} mV"
        )

        print(
            f"  Median absolute activity : "
            f"{row['Median Absolute Activity']:.3f} mV"
        )

        print(
            f"  Mean absolute activity   : "
            f"{row['Mean Absolute Activity']:.3f} mV"
        )

        print(
            f"  Range                    : "
            f"{row['Min']:.3f} to "
            f"{row['Max']:.3f} mV"
        )

        print(
            f"  MAD                      : "
            f"{row['MAD']:.3f} mV"
        )

        print(
            f"  Robust lower threshold   : "
            f"{row['Lower Excursion Threshold']:.3f} mV"
        )

        print(
            f"  Robust upper threshold   : "
            f"{row['Upper Excursion Threshold']:.3f} mV"
        )

        print(
            f"  Negative excursions      : "
            f"{int(row['Negative Excursion Count'])} "
            f"({row['Negative Excursion Percent']:.2f}%)"
        )

        print(
            f"  Positive excursions      : "
            f"{int(row['Positive Excursion Count'])} "
            f"({row['Positive Excursion Percent']:.2f}%)"
        )

        print(
            f"  Total excursions         : "
            f"{int(row['Total Excursion Count'])} "
            f"({row['Total Excursion Percent']:.2f}%)"
        )


# ------------------------------------------------------------
# Cross-check valid electrical totals
# ------------------------------------------------------------

control_expected = (
    control[
        "Electrical Analysis (mV)"
    ]
    .notna()
    .sum()
)

ldpe_expected = (
    ldpe[
        "Electrical Analysis (mV)"
    ]
    .notna()
    .sum()
)

control_observed = int(
    control_features[
        "Valid n"
    ].sum()
)

ldpe_observed = int(
    ldpe_features[
        "Valid n"
    ].sum()
)


print()
print("Electrical Validity Cross-Check")
print("-" * 78)

print(
    f"Control dataset total : "
    f"{control_expected}"
)

print(
    f"Control session total : "
    f"{control_observed}"
)

print(
    "Control match         :",
    control_expected
    == control_observed
)

print()

print(
    f"LDPE dataset total    : "
    f"{ldpe_expected}"
)

print(
    f"LDPE session total    : "
    f"{ldpe_observed}"
)

print(
    "LDPE match            :",
    ldpe_expected
    == ldpe_observed
)


print()
print("Electrical feature table created:")
print(f"  {OUTPUT_FILE}")
