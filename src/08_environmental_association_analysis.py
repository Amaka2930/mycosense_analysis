import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr


# ------------------------------------------------------------
# MycoSense
# Step 55: Environmental-Electrical Association Analysis
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
    / "environmental_electrical_spearman_correlations.csv"
)

SESSION_GAP_MINUTES = 10

ELECTRICAL_COLUMN = "Electrical Analysis (mV)"

ENVIRONMENTAL_VARIABLES = {
    "Temperature": "Temperature Analysis (C)",
    "Humidity": "Humidity Analysis (%)",
    "Soil Moisture": "Soil Moisture Analysis (%)",
}


# ------------------------------------------------------------
# Load and prepare data
# ------------------------------------------------------------

def prepare_data(path):

    data = pd.read_csv(path)

    data["Timestamp UTC"] = pd.to_datetime(
        data["Timestamp UTC"],
        utc=True,
        errors="coerce"
    )

    data = data.sort_values(
        "Timestamp UTC"
    ).reset_index(drop=True)

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


control = prepare_data(CONTROL_FILE)
ldpe = prepare_data(LDPE_FILE)


# ------------------------------------------------------------
# Correlation interpretation
# ------------------------------------------------------------

def strength_label(rho):

    if pd.isna(rho):
        return "Not estimable"

    absolute_rho = abs(rho)

    if absolute_rho < 0.20:
        return "Very weak"

    elif absolute_rho < 0.40:
        return "Weak"

    elif absolute_rho < 0.60:
        return "Moderate"

    elif absolute_rho < 0.80:
        return "Strong"

    else:
        return "Very strong"


def direction_label(rho):

    if pd.isna(rho):
        return "Not estimable"

    if rho > 0:
        return "Positive"

    elif rho < 0:
        return "Negative"

    else:
        return "No direction"


# ------------------------------------------------------------
# Calculate session-level Spearman correlations
# ------------------------------------------------------------

def analyse_condition(data, condition):

    results = []

    for session_id, session in data.groupby(
        "Session ID",
        sort=True
    ):

        start_time = session[
            "Timestamp UTC"
        ].min()

        end_time = session[
            "Timestamp UTC"
        ].max()

        duration_minutes = (
            end_time - start_time
        ).total_seconds() / 60

        for variable_name, variable_column in (
            ENVIRONMENTAL_VARIABLES.items()
        ):

            paired = session[
                [
                    ELECTRICAL_COLUMN,
                    variable_column
                ]
            ].dropna()

            paired_n = len(paired)

            rho = np.nan
            p_value = np.nan
            status = "Not estimable"

            # At least 5 paired observations are required
            # for this exploratory calculation.
            if paired_n >= 5:

                electrical_unique = (
                    paired[
                        ELECTRICAL_COLUMN
                    ].nunique()
                )

                environmental_unique = (
                    paired[
                        variable_column
                    ].nunique()
                )

                # Spearman correlation cannot provide a
                # meaningful coefficient when one variable
                # is constant.
                if (
                    electrical_unique >= 2
                    and
                    environmental_unique >= 2
                ):

                    rho, p_value = spearmanr(
                        paired[
                            ELECTRICAL_COLUMN
                        ],
                        paired[
                            variable_column
                        ],
                        nan_policy="omit"
                    )

                    status = "Estimated"

                else:

                    status = (
                        "Not estimable - constant variable"
                    )

            elif paired_n > 0:

                status = (
                    "Not estimable - fewer than 5 pairs"
                )

            else:

                status = "Not estimable - no paired data"

            results.append(
                {
                    "Condition": condition,
                    "Session ID": int(session_id),
                    "Date": start_time.date(),
                    "Start UTC": start_time,
                    "End UTC": end_time,
                    "Duration Minutes":
                        duration_minutes,
                    "Environmental Variable":
                        variable_name,
                    "Paired n": paired_n,
                    "Spearman rho": rho,
                    "Absolute rho":
                        abs(rho)
                        if not pd.isna(rho)
                        else np.nan,
                    "Direction":
                        direction_label(rho),
                    "Strength":
                        strength_label(rho),
                    "Exploratory p-value":
                        p_value,
                    "Status":
                        status,
                }
            )

    return pd.DataFrame(results)


control_results = analyse_condition(
    control,
    "Control"
)

ldpe_results = analyse_condition(
    ldpe,
    "LDPE"
)

results = pd.concat(
    [
        control_results,
        ldpe_results
    ],
    ignore_index=True
)


# ------------------------------------------------------------
# Save complete results
# ------------------------------------------------------------

results.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Terminal report
# ------------------------------------------------------------

print()
print(
    "Environmental-Electrical Association Analysis"
)
print("-" * 78)

print()
print(
    "Method: within-session Spearman rank correlation"
)

print(
    "Minimum paired observations required: 5"
)

print(
    "p-values are exploratory because timestamp "
    "observations are temporally dependent."
)


for condition in ["Control", "LDPE"]:

    condition_results = results[
        results["Condition"].eq(condition)
    ]

    print()
    print(condition)
    print("=" * 78)

    for session_id in sorted(
        condition_results[
            "Session ID"
        ].unique()
    ):

        session_results = (
            condition_results[
                condition_results[
                    "Session ID"
                ].eq(session_id)
            ]
        )

        first = session_results.iloc[0]

        print()
        print(
            f"Session {session_id} | "
            f"{first['Date']} | "
            f"{first['Duration Minutes']:.2f} min"
        )

        for _, row in session_results.iterrows():

            variable = row[
                "Environmental Variable"
            ]

            paired_n = int(
                row["Paired n"]
            )

            if row["Status"] == "Estimated":

                print(
                    f"  {variable:<16} "
                    f"n={paired_n:>3} | "
                    f"rho={row['Spearman rho']:>7.3f} | "
                    f"{row['Strength']:<11} | "
                    f"{row['Direction']:<8} | "
                    f"p={row['Exploratory p-value']:.4g}"
                )

            else:

                print(
                    f"  {variable:<16} "
                    f"n={paired_n:>3} | "
                    f"{row['Status']}"
                )


# ------------------------------------------------------------
# Highlight LDPE 21 August session
# ------------------------------------------------------------

print()
print(
    "LDPE 21 August Electrical-Environment Diagnostic"
)
print("-" * 78)

ldpe_aug21 = results[
    (results["Condition"] == "LDPE")
    &
    (
        pd.to_datetime(
            results["Date"]
        ).dt.date
        ==
        pd.Timestamp(
            "2026-08-21"
        ).date()
    )
]

if ldpe_aug21.empty:

    print(
        "No LDPE 21 August session found."
    )

else:

    for _, row in ldpe_aug21.iterrows():

        print()

        print(
            f"{row['Environmental Variable']}"
        )

        print(
            f"  Paired observations : "
            f"{int(row['Paired n'])}"
        )

        print(
            f"  Status              : "
            f"{row['Status']}"
        )

        if row["Status"] == "Estimated":

            print(
                f"  Spearman rho        : "
                f"{row['Spearman rho']:.3f}"
            )

            print(
                f"  Association strength: "
                f"{row['Strength']}"
            )

            print(
                f"  Direction           : "
                f"{row['Direction']}"
            )

            print(
                f"  Exploratory p-value : "
                f"{row['Exploratory p-value']:.6f}"
            )


# ------------------------------------------------------------
# Count estimable correlations
# ------------------------------------------------------------

estimated = results[
    results["Status"].eq(
        "Estimated"
    )
]

print()
print("Analysis Validation")
print("-" * 78)

print(
    f"Expected session-variable rows : "
    f"{(8 + 6) * 3}"
)

print(
    f"Actual session-variable rows   : "
    f"{len(results)}"
)

print(
    "Row count correct              :",
    len(results)
    ==
    (8 + 6) * 3
)

print(
    f"Estimable correlations         : "
    f"{len(estimated)}"
)

print()
print("Correlation table created:")
print(f"  {OUTPUT_FILE}")
