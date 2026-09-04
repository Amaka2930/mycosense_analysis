import pandas as pd
import numpy as np
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 56: Matched-Session Comparative Analysis
# 24 August 2026
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
    / "matched_24_august_comparison.csv"
)


TARGET_DATE = pd.Timestamp(
    "2026-08-24"
).date()


VARIABLES = {
    "Temperature":
        (
            "Temperature Analysis (C)",
            "C"
        ),

    "Humidity":
        (
            "Humidity Analysis (%)",
            "%"
        ),

    "Soil Moisture":
        (
            "Soil Moisture Analysis (%)",
            "%"
        ),

    "pH":
        (
            "pH Analysis",
            "pH units"
        ),

    "Electrical Activity":
        (
            "Electrical Analysis (mV)",
            "mV"
        ),
}


# ------------------------------------------------------------
# Load datasets
# ------------------------------------------------------------

def load_data(path):

    data = pd.read_csv(path)

    data["Timestamp UTC"] = pd.to_datetime(
        data["Timestamp UTC"],
        utc=True,
        errors="coerce"
    )

    data = data.sort_values(
        "Timestamp UTC"
    ).reset_index(drop=True)

    return data


control = load_data(CONTROL_FILE)
ldpe = load_data(LDPE_FILE)


# ------------------------------------------------------------
# Select biological 24 August session
#
# The E2E record later on 24 August contains no valid analysis
# measurements, so requiring at least one valid analytical
# measurement isolates the biological monitoring window.
# ------------------------------------------------------------

analysis_columns = [
    item[0]
    for item in VARIABLES.values()
]


def select_aug24_session(data):

    target = data[
        data[
            "Timestamp UTC"
        ].dt.date.eq(
            TARGET_DATE
        )
    ].copy()

    has_valid_analysis = (
        target[
            analysis_columns
        ]
        .notna()
        .any(axis=1)
    )

    target = target[
        has_valid_analysis
    ].copy()

    target = target.sort_values(
        "Timestamp UTC"
    ).reset_index(drop=True)

    return target


control_match = select_aug24_session(
    control
)

ldpe_match = select_aug24_session(
    ldpe
)


# ------------------------------------------------------------
# Cliff's delta
#
# delta = P(LDPE > Control) - P(LDPE < Control)
#
# Positive delta:
# LDPE observations tend to be higher.
#
# Negative delta:
# LDPE observations tend to be lower.
#
# This is used descriptively. Timestamp observations are
# repeated measurements, not independent biological replicates.
# ------------------------------------------------------------

def cliffs_delta(control_values, ldpe_values):

    x = np.asarray(
        control_values,
        dtype=float
    )

    y = np.asarray(
        ldpe_values,
        dtype=float
    )

    x = x[
        ~np.isnan(x)
    ]

    y = y[
        ~np.isnan(y)
    ]

    if (
        len(x) == 0
        or
        len(y) == 0
    ):
        return np.nan

    greater = 0
    lower = 0

    for ldpe_value in y:

        greater += np.sum(
            ldpe_value > x
        )

        lower += np.sum(
            ldpe_value < x
        )

    total_pairs = (
        len(x)
        * len(y)
    )

    return (
        greater - lower
    ) / total_pairs


# ------------------------------------------------------------
# Conventional descriptive magnitude labels
#
# |delta| < 0.147       negligible
# |delta| < 0.330       small
# |delta| < 0.474       medium
# otherwise             large
#
# These labels describe distributional separation only.
# ------------------------------------------------------------

def delta_magnitude(delta):

    if pd.isna(delta):
        return "Not estimable"

    absolute_delta = abs(delta)

    if absolute_delta < 0.147:
        return "Negligible"

    elif absolute_delta < 0.330:
        return "Small"

    elif absolute_delta < 0.474:
        return "Medium"

    else:
        return "Large"


def delta_direction(delta):

    if pd.isna(delta):
        return "Not estimable"

    if delta > 0:
        return "LDPE higher"

    elif delta < 0:
        return "Control higher"

    else:
        return "No separation"


# ------------------------------------------------------------
# Temporal alignment diagnostics
# ------------------------------------------------------------

control_start = (
    control_match[
        "Timestamp UTC"
    ].min()
)

control_end = (
    control_match[
        "Timestamp UTC"
    ].max()
)

ldpe_start = (
    ldpe_match[
        "Timestamp UTC"
    ].min()
)

ldpe_end = (
    ldpe_match[
        "Timestamp UTC"
    ].max()
)


start_difference_seconds = abs(
    (
        ldpe_start
        - control_start
    ).total_seconds()
)

end_difference_seconds = abs(
    (
        ldpe_end
        - control_end
    ).total_seconds()
)


control_duration = (
    control_end
    - control_start
).total_seconds() / 60

ldpe_duration = (
    ldpe_end
    - ldpe_start
).total_seconds() / 60


# ------------------------------------------------------------
# Variable comparison
# ------------------------------------------------------------

rows = []


for variable_name, (
    column,
    unit
) in VARIABLES.items():

    control_values = (
        pd.to_numeric(
            control_match[column],
            errors="coerce"
        )
        .dropna()
    )

    ldpe_values = (
        pd.to_numeric(
            ldpe_match[column],
            errors="coerce"
        )
        .dropna()
    )

    control_q1 = (
        control_values.quantile(0.25)
    )

    control_q3 = (
        control_values.quantile(0.75)
    )

    ldpe_q1 = (
        ldpe_values.quantile(0.25)
    )

    ldpe_q3 = (
        ldpe_values.quantile(0.75)
    )

    control_median = (
        control_values.median()
    )

    ldpe_median = (
        ldpe_values.median()
    )

    median_difference = (
        ldpe_median
        - control_median
    )

    delta = cliffs_delta(
        control_values,
        ldpe_values
    )

    rows.append(
        {
            "Variable":
                variable_name,

            "Unit":
                unit,

            "Control n":
                len(control_values),

            "LDPE n":
                len(ldpe_values),

            "Control Median":
                control_median,

            "Control Q1":
                control_q1,

            "Control Q3":
                control_q3,

            "Control IQR":
                control_q3
                - control_q1,

            "LDPE Median":
                ldpe_median,

            "LDPE Q1":
                ldpe_q1,

            "LDPE Q3":
                ldpe_q3,

            "LDPE IQR":
                ldpe_q3
                - ldpe_q1,

            "Median Difference (LDPE-Control)":
                median_difference,

            "Cliffs Delta":
                delta,

            "Absolute Cliffs Delta":
                abs(delta),

            "Effect Magnitude":
                delta_magnitude(delta),

            "Direction":
                delta_direction(delta),
        }
    )


comparison = pd.DataFrame(
    rows
)

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Terminal output
# ------------------------------------------------------------

print()
print(
    "Matched 24 August Comparative Analysis"
)
print("-" * 78)

print()
print("Temporal Alignment")
print("-" * 78)

print(
    f"Control start : "
    f"{control_start}"
)

print(
    f"LDPE start    : "
    f"{ldpe_start}"
)

print(
    f"Start difference : "
    f"{start_difference_seconds:.3f} seconds"
)

print()

print(
    f"Control end   : "
    f"{control_end}"
)

print(
    f"LDPE end      : "
    f"{ldpe_end}"
)

print(
    f"End difference   : "
    f"{end_difference_seconds:.3f} seconds"
)

print()

print(
    f"Control duration : "
    f"{control_duration:.3f} minutes"
)

print(
    f"LDPE duration    : "
    f"{ldpe_duration:.3f} minutes"
)

print()

print(
    f"Control session rows : "
    f"{len(control_match)}"
)

print(
    f"LDPE session rows    : "
    f"{len(ldpe_match)}"
)


# ------------------------------------------------------------
# Print comparisons
# ------------------------------------------------------------

print()
print("Variable Comparisons")
print("=" * 78)


for _, row in comparison.iterrows():

    print()

    print(
        row["Variable"]
    )

    print(
        f"  Control n             : "
        f"{int(row['Control n'])}"
    )

    print(
        f"  LDPE n                : "
        f"{int(row['LDPE n'])}"
    )

    print(
        f"  Control median        : "
        f"{row['Control Median']:.3f} "
        f"{row['Unit']}"
    )

    print(
        f"  Control IQR           : "
        f"{row['Control IQR']:.3f}"
    )

    print(
        f"  LDPE median           : "
        f"{row['LDPE Median']:.3f} "
        f"{row['Unit']}"
    )

    print(
        f"  LDPE IQR              : "
        f"{row['LDPE IQR']:.3f}"
    )

    print(
        f"  Median difference     : "
        f"{row['Median Difference (LDPE-Control)']:.3f} "
        f"{row['Unit']}"
    )

    print(
        f"  Cliff's delta         : "
        f"{row['Cliffs Delta']:.3f}"
    )

    print(
        f"  Magnitude             : "
        f"{row['Effect Magnitude']}"
    )

    print(
        f"  Direction             : "
        f"{row['Direction']}"
    )


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print()
print("Analysis Validation")
print("-" * 78)

print(
    f"Expected variables : "
    f"{len(VARIABLES)}"
)

print(
    f"Actual variables   : "
    f"{len(comparison)}"
)

print(
    "Variable count correct :",
    len(comparison)
    == len(VARIABLES)
)


all_control_21 = (
    comparison[
        "Control n"
    ].eq(21).all()
)

all_ldpe_21 = (
    comparison[
        "LDPE n"
    ].eq(21).all()
)


print(
    "All Control variables n=21 :",
    all_control_21
)

print(
    "All LDPE variables n=21    :",
    all_ldpe_21
)

print()
print(
    "Interpretation note:"
)

print(
    "Cliff's delta is descriptive here. "
    "The timestamp observations are repeated "
    "measurements from one biological unit per condition."
)

print()
print("Matched comparison table created:")
print(f"  {OUTPUT_FILE}")
