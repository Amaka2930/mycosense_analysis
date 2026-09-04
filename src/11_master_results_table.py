import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 58: Master Results Table
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INITIAL_STATS_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "initial_robust_descriptive_statistics.csv"
)

SESSION_STATS_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "session_robust_descriptive_statistics.csv"
)

ELECTRICAL_FEATURE_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "electrical_signal_features_by_session.csv"
)

CORRELATION_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "environmental_electrical_spearman_correlations.csv"
)

MATCHED_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "matched_24_august_comparison.csv"
)

SENSITIVITY_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "sensitivity_analysis_cleaning_impact.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "master_results_table.csv"
)


# ------------------------------------------------------------
# Load validated outputs
# ------------------------------------------------------------

initial_stats = pd.read_csv(
    INITIAL_STATS_FILE
)

session_stats = pd.read_csv(
    SESSION_STATS_FILE
)

electrical_features = pd.read_csv(
    ELECTRICAL_FEATURE_FILE
)

correlations = pd.read_csv(
    CORRELATION_FILE
)

matched = pd.read_csv(
    MATCHED_FILE
)

sensitivity = pd.read_csv(
    SENSITIVITY_FILE
)


rows = []


def add_result(
    evidence_type,
    comparison,
    metric,
    result,
    interpretation
):

    rows.append(
        {
            "Evidence Type":
                evidence_type,

            "Comparison / Session":
                comparison,

            "Metric":
                metric,

            "Result":
                result,

            "Interpretation":
                interpretation,
        }
    )


# ------------------------------------------------------------
# 1. Overall robust analysis-ready summaries
# ------------------------------------------------------------

for _, row in initial_stats.iterrows():

    condition = row["Condition"]
    variable = row["Variable"]

    result = (
        f"n={int(row['n'])}; "
        f"median={row['median']:.3f}; "
        f"IQR={row['iqr']:.3f}; "
        f"range={row['min']:.3f} to {row['max']:.3f}"
    )

    add_result(
        "Overall robust descriptive",
        condition,
        variable,
        result,
        (
            "Analysis-ready summary across available sessions. "
            "Interpret cautiously because monitoring sessions "
            "occurred at different times and conditions."
        ),
    )


# ------------------------------------------------------------
# 2. Key electrical session findings
# ------------------------------------------------------------

key_electrical_sessions = [
    ("Control", 4, "Control 21 August Session 4"),
    ("Control", 8, "Control 25 August Session 8"),
    ("LDPE", 3, "LDPE 21 August Session 3"),
    ("Control", 6, "Control 24 August matched session"),
    ("LDPE", 4, "LDPE 24 August matched session"),
]


for condition, session_id, label in key_electrical_sessions:

    subset = electrical_features[
        (
            electrical_features[
                "Condition"
            ].eq(condition)
        )
        &
        (
            electrical_features[
                "Session ID"
            ].eq(session_id)
        )
    ]

    if subset.empty:
        continue

    row = subset.iloc[0]

    result = (
        f"n={int(row['Valid n'])}; "
        f"median={row['Median']:.3f} mV; "
        f"IQR={row['IQR']:.3f} mV; "
        f"SD={row['SD']:.3f} mV; "
        f"median absolute activity="
        f"{row['Median Absolute Activity']:.3f} mV; "
        f"range={row['Min']:.3f} to {row['Max']:.3f} mV"
    )

    if (
        condition == "LDPE"
        and
        session_id == 3
    ):

        interpretation = (
            "Highest sustained electrical variability in the "
            "dataset. Treated as a candidate episodic response, "
            "not evidence of an LDPE-specific causal effect."
        )

    elif (
        condition == "Control"
        and
        session_id == 4
    ):

        interpretation = (
            "Contains an isolated high positive excursion. "
            "This demonstrates that large electrical excursions "
            "were not unique to the LDPE condition."
        )

    elif (
        condition == "Control"
        and
        session_id == 8
    ):

        interpretation = (
            "Control also exhibited substantial within-session "
            "electrical variability on 25 August."
        )

    else:

        interpretation = (
            "Matched 24 August electrical session used for "
            "direct descriptive comparison between conditions."
        )

    add_result(
        "Electrical session behaviour",
        label,
        "Electrical Activity",
        result,
        interpretation,
    )


# ------------------------------------------------------------
# 3. LDPE 21 August environmental associations
# ------------------------------------------------------------

ldpe_aug21 = correlations[
    (
        correlations[
            "Condition"
        ].eq("LDPE")
    )
    &
    (
        correlations[
            "Session ID"
        ].eq(3)
    )
]


for _, row in ldpe_aug21.iterrows():

    variable = row[
        "Environmental Variable"
    ]

    if row["Status"] == "Estimated":

        result = (
            f"paired n={int(row['Paired n'])}; "
            f"Spearman rho={row['Spearman rho']:.3f}; "
            f"{row['Strength']} {row['Direction'].lower()}"
        )

        interpretation = (
            "Exploratory within-session association only. "
            "Timestamp observations are temporally dependent, "
            "so this is not independent inferential evidence."
        )

    else:

        result = (
            f"paired n={int(row['Paired n'])}; "
            f"{row['Status']}"
        )

        interpretation = (
            "No meaningful within-session correlation could "
            "be estimated for this variable."
        )

    add_result(
        "Environmental association",
        "LDPE 21 August Session 3",
        f"Electrical vs {variable}",
        result,
        interpretation,
    )


# ------------------------------------------------------------
# 4. Matched 24 August comparisons
# ------------------------------------------------------------

for _, row in matched.iterrows():

    variable = row["Variable"]
    unit = row["Unit"]

    result = (
        f"Control median={row['Control Median']:.3f} {unit}; "
        f"LDPE median={row['LDPE Median']:.3f} {unit}; "
        f"difference={row['Median Difference (LDPE-Control)']:.3f} {unit}; "
        f"Cliff's delta={row['Cliffs Delta']:.3f}; "
        f"{row['Effect Magnitude']}"
    )

    interpretation = (
        "Descriptive distributional comparison during the "
        "closely time-matched 24 August monitoring window. "
        "Repeated timestamps are not independent biological replicates."
    )

    add_result(
        "Matched 24 August comparison",
        "Control vs LDPE",
        variable,
        result,
        interpretation,
    )


# ------------------------------------------------------------
# 5. Sensitivity-analysis highlights
# ------------------------------------------------------------

focus = sensitivity[
    (
        (
            sensitivity["Condition"].eq("LDPE")
            &
            sensitivity["Date"].astype(str).eq("2026-08-25")
            &
            sensitivity["Variable"].isin(
                [
                    "Electrical Activity",
                    "Soil Moisture"
                ]
            )
        )
        |
        (
            sensitivity["Condition"].eq("Control")
            &
            sensitivity["Date"].astype(str).eq("2026-08-21")
            &
            sensitivity["Variable"].eq(
                "Soil Moisture"
            )
        )
    )
]


for _, row in focus.iterrows():

    variable = row["Variable"]

    result = (
        f"raw n={int(row['Raw Biological n'])}; "
        f"analysis-ready n={int(row['Analysis Ready n'])}; "
        f"masked={int(row['Excluded or Masked n'])}; "
        f"raw median={row['Raw Median']}; "
        f"analysis median={row['Analysis Median']}"
    )

    interpretation = (
        "Sensitivity result showing the effect of documented "
        "variable-specific data-quality screening."
    )

    add_result(
        "Sensitivity analysis",
        f"{row['Condition']} {row['Date']} Session {int(row['Session ID'])}",
        variable,
        result,
        interpretation,
    )


# ------------------------------------------------------------
# Build and save master table
# ------------------------------------------------------------

master = pd.DataFrame(
    rows
)

master.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print()
print("Master Results Table")
print("-" * 78)

print()

print(
    f"Total master result rows : "
    f"{len(master)}"
)

print()

print("Evidence-type counts")
print("-" * 78)

counts = (
    master[
        "Evidence Type"
    ]
    .value_counts()
)

for evidence_type, count in counts.items():

    print(
        f"{evidence_type:<32} : "
        f"{count}"
    )


print()
print("Key checks")
print("-" * 78)


ldpe21_present = (
    (
        master[
            "Comparison / Session"
        ]
        ==
        "LDPE 21 August Session 3"
    )
    &
    (
        master[
            "Metric"
        ]
        ==
        "Electrical Activity"
    )
).any()


matched_electrical_present = (
    (
        master[
            "Evidence Type"
        ]
        ==
        "Matched 24 August comparison"
    )
    &
    (
        master[
            "Metric"
        ]
        ==
        "Electrical Activity"
    )
).any()


sensitivity_electrical_present = (
    (
        master[
            "Evidence Type"
        ]
        ==
        "Sensitivity analysis"
    )
    &
    (
        master[
            "Metric"
        ]
        ==
        "Electrical Activity"
    )
).any()


print(
    "LDPE 21 Aug electrical result present :",
    ldpe21_present
)

print(
    "Matched electrical result present     :",
    matched_electrical_present
)

print(
    "Sensitivity electrical result present :",
    sensitivity_electrical_present
)


print()
print("Preview")
print("=" * 78)

print(
    master[
        [
            "Evidence Type",
            "Comparison / Session",
            "Metric",
            "Result"
        ]
    ]
    .to_string(
        index=False
    )
)


print()
print(
    "Master results table created:"
)

print(
    f"  {OUTPUT_FILE}"
)



