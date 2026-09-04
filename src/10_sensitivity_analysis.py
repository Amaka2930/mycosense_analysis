import pandas as pd
import numpy as np
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 57: Sensitivity Analysis
#
# Compare:
# A. Raw biological measurements
# B. Analysis-ready variable-specific measurements
#
# Raw biological = explicit E2E software-test records removed,
# but no variable-specific technical exclusions applied.
#
# Analysis-ready = validity decisions established during the
# earlier data-quality investigation.
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

OUTPUT_SESSION = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "sensitivity_analysis_by_session.csv"
)

OUTPUT_IMPACT = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "sensitivity_analysis_cleaning_impact.csv"
)

SESSION_GAP_MINUTES = 10


VARIABLES = {
    "Temperature": {
        "raw": "Temperature (C)",
        "analysis": "Temperature Analysis (C)",
    },

    "Humidity": {
        "raw": "Humidity (%)",
        "analysis": "Humidity Analysis (%)",
    },

    "Soil Moisture": {
        "raw": "Soil Moisture (%)",
        "analysis": "Soil Moisture Analysis (%)",
    },

    "pH": {
        "raw": "pH",
        "analysis": "pH Analysis",
    },

    "Electrical Activity": {
        "raw": "Electrical Activity (mV)",
        "analysis": "Electrical Analysis (mV)",
    },
}


# ------------------------------------------------------------
# Load and prepare
# ------------------------------------------------------------

def prepare_data(path, condition):

    data = pd.read_csv(path)

    data["Timestamp UTC"] = pd.to_datetime(
        data["Timestamp UTC"],
        utc=True,
        errors="coerce"
    )

    data = data.sort_values(
        "Timestamp UTC"
    ).reset_index(drop=True)

    data["Condition"] = condition

    # Explicit software pipeline tests are not biological data.
    data["Sensitivity Biological Record"] = (
        ~data["Device ID"]
        .astype(str)
        .str.lower()
        .str.startswith("e2e-")
    )

    data["Gap Minutes Sensitivity"] = (
        data["Timestamp UTC"]
        .diff()
        .dt.total_seconds()
        .div(60)
    )

    data["New Session Sensitivity"] = (
        data["Gap Minutes Sensitivity"].isna()
        |
        data["Gap Minutes Sensitivity"].gt(
            SESSION_GAP_MINUTES
        )
    )

    data["Sensitivity Session ID"] = (
        data["New Session Sensitivity"]
        .cumsum()
        .astype(int)
    )

    return data


control = prepare_data(
    CONTROL_FILE,
    "Control"
)

ldpe = prepare_data(
    LDPE_FILE,
    "LDPE"
)

combined = pd.concat(
    [control, ldpe],
    ignore_index=True
)


# ------------------------------------------------------------
# Robust summary function
# ------------------------------------------------------------

def robust_summary(values):

    values = pd.to_numeric(
        values,
        errors="coerce"
    ).dropna()

    n = len(values)

    if n == 0:

        return {
            "n": 0,
            "Mean": np.nan,
            "Median": np.nan,
            "SD": np.nan,
            "Q1": np.nan,
            "Q3": np.nan,
            "IQR": np.nan,
            "Min": np.nan,
            "Max": np.nan,
        }

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)

    return {
        "n": n,
        "Mean": values.mean(),
        "Median": values.median(),

        "SD":
            values.std(ddof=1)
            if n > 1
            else np.nan,

        "Q1": q1,
        "Q3": q3,
        "IQR": q3 - q1,
        "Min": values.min(),
        "Max": values.max(),
    }


# ------------------------------------------------------------
# Session-level sensitivity table
# ------------------------------------------------------------

session_rows = []


for (
    condition,
    session_id
), session in combined.groupby(
    [
        "Condition",
        "Sensitivity Session ID"
    ],
    sort=True
):

    session = session.copy()

    start = session[
        "Timestamp UTC"
    ].min()

    end = session[
        "Timestamp UTC"
    ].max()

    duration = (
        end - start
    ).total_seconds() / 60

    biological_session = session[
        session[
            "Sensitivity Biological Record"
        ]
    ].copy()

    for variable_name, columns in (
        VARIABLES.items()
    ):

        raw_stats = robust_summary(
            biological_session[
                columns["raw"]
            ]
        )

        analysis_stats = robust_summary(
            biological_session[
                columns["analysis"]
            ]
        )

        raw_median = raw_stats[
            "Median"
        ]

        analysis_median = analysis_stats[
            "Median"
        ]

        raw_iqr = raw_stats[
            "IQR"
        ]

        analysis_iqr = analysis_stats[
            "IQR"
        ]

        session_rows.append(
            {
                "Condition":
                    condition,

                "Session ID":
                    int(session_id),

                "Date":
                    start.date(),

                "Start UTC":
                    start,

                "End UTC":
                    end,

                "Duration Minutes":
                    duration,

                "Variable":
                    variable_name,

                "Raw Biological n":
                    raw_stats["n"],

                "Analysis Ready n":
                    analysis_stats["n"],

                "Excluded or Masked n":
                    (
                        raw_stats["n"]
                        -
                        analysis_stats["n"]
                    ),

                "Raw Median":
                    raw_median,

                "Analysis Median":
                    analysis_median,

                "Median Change":
                    (
                        analysis_median
                        - raw_median
                        if (
                            not pd.isna(
                                analysis_median
                            )
                            and
                            not pd.isna(
                                raw_median
                            )
                        )
                        else np.nan
                    ),

                "Raw IQR":
                    raw_iqr,

                "Analysis IQR":
                    analysis_iqr,

                "IQR Change":
                    (
                        analysis_iqr
                        - raw_iqr
                        if (
                            not pd.isna(
                                analysis_iqr
                            )
                            and
                            not pd.isna(
                                raw_iqr
                            )
                        )
                        else np.nan
                    ),

                "Raw Min":
                    raw_stats["Min"],

                "Analysis Min":
                    analysis_stats["Min"],

                "Raw Max":
                    raw_stats["Max"],

                "Analysis Max":
                    analysis_stats["Max"],
            }
        )


session_results = pd.DataFrame(
    session_rows
)

session_results.to_csv(
    OUTPUT_SESSION,
    index=False
)


# ------------------------------------------------------------
# Cleaning-impact table
#
# Only rows where raw and analysis-ready data differ.
# ------------------------------------------------------------

impact = session_results[
    (
        session_results[
            "Excluded or Masked n"
        ] > 0
    )
    |
    (
        session_results[
            "Median Change"
        ].abs() > 1e-12
    )
    |
    (
        session_results[
            "IQR Change"
        ].abs() > 1e-12
    )
].copy()


impact.to_csv(
    OUTPUT_IMPACT,
    index=False
)


# ------------------------------------------------------------
# Terminal report
# ------------------------------------------------------------

print()
print("Sensitivity Analysis")
print("-" * 78)

print()
print(
    "Scenario A: Raw biological measurements "
    "(E2E test records excluded only)"
)

print(
    "Scenario B: Analysis-ready measurements "
    "(variable-specific validity rules applied)"
)

print()


for condition in [
    "Control",
    "LDPE"
]:

    print()
    print(condition)
    print("=" * 78)

    condition_impact = impact[
        impact[
            "Condition"
        ].eq(condition)
    ]

    if condition_impact.empty:

        print(
            "No variable-level cleaning impact detected."
        )

        continue

    for _, row in (
        condition_impact
        .sort_values(
            [
                "Session ID",
                "Variable"
            ]
        )
        .iterrows()
    ):

        print()

        print(
            f"Session {int(row['Session ID'])} | "
            f"{row['Date']} | "
            f"{row['Variable']}"
        )

        print(
            f"  Raw biological n    : "
            f"{int(row['Raw Biological n'])}"
        )

        print(
            f"  Analysis-ready n    : "
            f"{int(row['Analysis Ready n'])}"
        )

        print(
            f"  Masked/excluded     : "
            f"{int(row['Excluded or Masked n'])}"
        )

        if (
            not pd.isna(
                row["Raw Median"]
            )
        ):

            print(
                f"  Raw median          : "
                f"{row['Raw Median']:.3f}"
            )

        else:

            print(
                "  Raw median          : NA"
            )

        if (
            not pd.isna(
                row["Analysis Median"]
            )
        ):

            print(
                f"  Analysis median     : "
                f"{row['Analysis Median']:.3f}"
            )

        else:

            print(
                "  Analysis median     : NA"
            )

        if (
            not pd.isna(
                row["Raw IQR"]
            )
        ):

            print(
                f"  Raw IQR             : "
                f"{row['Raw IQR']:.3f}"
            )

        else:

            print(
                "  Raw IQR             : NA"
            )

        if (
            not pd.isna(
                row["Analysis IQR"]
            )
        ):

            print(
                f"  Analysis IQR        : "
                f"{row['Analysis IQR']:.3f}"
            )

        else:

            print(
                "  Analysis IQR        : NA"
            )

        print(
            f"  Raw range           : "
            f"{row['Raw Min']} to "
            f"{row['Raw Max']}"
        )

        print(
            f"  Analysis range      : "
            f"{row['Analysis Min']} to "
            f"{row['Analysis Max']}"
        )


# ------------------------------------------------------------
# Focused diagnostics for known important periods
# ------------------------------------------------------------

print()
print(
    "Focused Sensitivity Diagnostics"
)
print("-" * 78)


focus_cases = [
    (
        "Control",
        pd.Timestamp(
            "2026-08-21"
        ).date(),
        "Soil Moisture"
    ),

    (
        "LDPE",
        pd.Timestamp(
            "2026-08-25"
        ).date(),
        "Soil Moisture"
    ),

    (
        "LDPE",
        pd.Timestamp(
            "2026-08-25"
        ).date(),
        "Electrical Activity"
    ),
]


for (
    condition,
    date,
    variable
) in focus_cases:

    focus = session_results[
        (
            session_results[
                "Condition"
            ].eq(condition)
        )
        &
        (
            pd.to_datetime(
                session_results[
                    "Date"
                ]
            ).dt.date.eq(date)
        )
        &
        (
            session_results[
                "Variable"
            ].eq(variable)
        )
    ]

    print()

    print(
        f"{condition} | "
        f"{date} | "
        f"{variable}"
    )

    if focus.empty:

        print(
            "  No matching session found."
        )

        continue

    for _, row in focus.iterrows():

        print(
            f"  Session             : "
            f"{int(row['Session ID'])}"
        )

        print(
            f"  Raw n               : "
            f"{int(row['Raw Biological n'])}"
        )

        print(
            f"  Analysis-ready n    : "
            f"{int(row['Analysis Ready n'])}"
        )

        print(
            f"  Masked/excluded     : "
            f"{int(row['Excluded or Masked n'])}"
        )

        print(
            f"  Raw median          : "
            f"{row['Raw Median']}"
        )

        print(
            f"  Analysis median     : "
            f"{row['Analysis Median']}"
        )

        print(
            f"  Raw IQR             : "
            f"{row['Raw IQR']}"
        )

        print(
            f"  Analysis IQR        : "
            f"{row['Analysis IQR']}"
        )

        print(
            f"  Raw range           : "
            f"{row['Raw Min']} to "
            f"{row['Raw Max']}"
        )

        print(
            f"  Analysis range      : "
            f"{row['Analysis Min']} to "
            f"{row['Analysis Max']}"
        )


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

expected_rows = (
    (8 + 6)
    * len(VARIABLES)
)


print()
print("Analysis Validation")
print("-" * 78)

print(
    f"Expected session-variable rows : "
    f"{expected_rows}"
)

print(
    f"Actual session-variable rows   : "
    f"{len(session_results)}"
)

print(
    "Row count correct              :",
    len(session_results)
    == expected_rows
)


negative_exclusions = (
    session_results[
        "Excluded or Masked n"
    ] < 0
).sum()


print(
    f"Negative exclusion counts      : "
    f"{negative_exclusions}"
)

print(
    "Exclusion counts valid        :",
    negative_exclusions == 0
)


print()
print(
    f"Rows affected by cleaning      : "
    f"{len(impact)}"
)

print()

print(
    "Sensitivity analysis does not choose the "
    "scenario producing the preferred result."
)

print(
    "Its purpose is to show how documented "
    "data-quality decisions affect the findings."
)

print()

print(
    "Session sensitivity table:"
)

print(
    f"  {OUTPUT_SESSION}"
)

print()

print(
    "Cleaning-impact table:"
)

print(
    f"  {OUTPUT_IMPACT}"
)
