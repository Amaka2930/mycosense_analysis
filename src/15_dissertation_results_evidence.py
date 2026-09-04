import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 62: Dissertation Results Evidence Table
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TABLE_DIR = BASE_DIR / "outputs" / "tables"

MASTER_FILE = (
    TABLE_DIR
    / "master_results_table.csv"
)

INTEGRATED_FILE = (
    TABLE_DIR
    / "integrated_evidence_assessment.csv"
)

RQ_FILE = (
    TABLE_DIR
    / "research_question_evidence_matrix.csv"
)

OUTPUT_FILE = (
    TABLE_DIR
    / "dissertation_results_evidence.csv"
)


# ------------------------------------------------------------
# Load validated evidence
# ------------------------------------------------------------

master = pd.read_csv(MASTER_FILE)
integrated = pd.read_csv(INTEGRATED_FILE)
rq_matrix = pd.read_csv(RQ_FILE)


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def master_result(
    evidence_type,
    comparison,
    metric
):

    subset = master[
        master["Evidence Type"].eq(evidence_type)
        &
        master["Comparison / Session"].eq(comparison)
        &
        master["Metric"].eq(metric)
    ]

    if len(subset) != 1:

        raise ValueError(
            f"Expected one master result for "
            f"{evidence_type} | "
            f"{comparison} | "
            f"{metric}. "
            f"Found {len(subset)}."
        )

    return subset.iloc[0]["Result"]


def integrated_conclusion(
    finding_id
):

    subset = integrated[
        integrated["Finding ID"].eq(
            finding_id
        )
    ]

    if len(subset) != 1:

        raise ValueError(
            f"Expected one integrated finding "
            f"for {finding_id}. "
            f"Found {len(subset)}."
        )

    return subset.iloc[0][
        "Defensible Interpretation"
    ]


# ------------------------------------------------------------
# Retrieve authoritative numerical evidence
# ------------------------------------------------------------

control21 = master_result(
    "Electrical session behaviour",
    "Control 21 August Session 4",
    "Electrical Activity",
)

ldpe21 = master_result(
    "Electrical session behaviour",
    "LDPE 21 August Session 3",
    "Electrical Activity",
)

control25 = master_result(
    "Electrical session behaviour",
    "Control 25 August Session 8",
    "Electrical Activity",
)

matched_temp = master_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Temperature",
)

matched_humidity = master_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Humidity",
)

matched_soil = master_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Soil Moisture",
)

matched_ph = master_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "pH",
)

matched_electrical = master_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Electrical Activity",
)

ldpe21_temp_assoc = master_result(
    "Environmental association",
    "LDPE 21 August Session 3",
    "Electrical vs Temperature",
)

ldpe21_humidity_assoc = master_result(
    "Environmental association",
    "LDPE 21 August Session 3",
    "Electrical vs Humidity",
)

ldpe21_soil_assoc = master_result(
    "Environmental association",
    "LDPE 21 August Session 3",
    "Electrical vs Soil Moisture",
)

control21_soil_sensitivity = master_result(
    "Sensitivity analysis",
    "Control 2026-08-21 Session 4",
    "Soil Moisture",
)

ldpe25_soil_sensitivity = master_result(
    "Sensitivity analysis",
    "LDPE 2026-08-25 Session 6",
    "Soil Moisture",
)

ldpe25_electrical_sensitivity = master_result(
    "Sensitivity analysis",
    "LDPE 2026-08-25 Session 6",
    "Electrical Activity",
)


# ------------------------------------------------------------
# Build dissertation Results evidence
# ------------------------------------------------------------

rows = [

    {
        "Results Section":
            "Data quality and analytical dataset",

        "Finding":
            "Analysis used variable-specific validity screening.",

        "Quantitative Evidence":
            (
                "Control valid observations: temperature 651, "
                "humidity 651, soil moisture 670, pH 21, "
                "electrical activity 882. "
                "LDPE valid observations: temperature 254, "
                "humidity 254, soil moisture 260, pH 21, "
                "electrical activity 416."
            ),

        "Recommended Figure/Table":
            "Data-quality summary table",

        "Reporting Status":
            "Primary",

        "Interpretive Boundary":
            (
                "Observation counts represent repeated sensor "
                "measurements, not independent biological replicates."
            ),
    },

    {
        "Results Section":
            "Electrical activity",

        "Finding":
            (
                "A pronounced high-variability electrical episode "
                "occurred in the LDPE condition on 21 August."
            ),

        "Quantitative Evidence":
            ldpe21,

        "Recommended Figure/Table":
            "ldpe_21_august_electrical_diagnostic.png",

        "Reporting Status":
            "Primary",

        "Interpretive Boundary":
            integrated_conclusion("F2"),
    },

    {
        "Results Section":
            "Electrical activity",

        "Finding":
            (
                "Large electrical excursions were not unique "
                "to the LDPE condition."
            ),

        "Quantitative Evidence":
            (
                f"Control 21 August: {control21}. "
                f"Control 25 August: {control25}."
            ),

        "Recommended Figure/Table":
            "control_electrical_activity_by_session.png",

        "Reporting Status":
            "Primary counter-evidence",

        "Interpretive Boundary":
            (
                "Control variability prevents interpretation "
                "of electrical magnitude alone as an "
                "LDPE-specific signature."
            ),
    },

    {
        "Results Section":
            "Matched condition comparison",

        "Finding":
            (
                "The closely time-matched 24 August session "
                "showed little electrical separation between "
                "Control and LDPE."
            ),

        "Quantitative Evidence":
            matched_electrical,

        "Recommended Figure/Table":
            "matched_24_august_electrical_comparison.png",

        "Reporting Status":
            "Primary",

        "Interpretive Boundary":
            integrated_conclusion("F3"),
    },

    {
        "Results Section":
            "Matched environmental comparison",

        "Finding":
            (
                "Temperature, humidity and pH showed negligible "
                "distributional separation during the matched "
                "24 August session, while soil moisture showed "
                "a small separation."
            ),

        "Quantitative Evidence":
            (
                f"Temperature: {matched_temp}. "
                f"Humidity: {matched_humidity}. "
                f"Soil moisture: {matched_soil}. "
                f"pH: {matched_ph}."
            ),

        "Recommended Figure/Table":
            "Matched-session comparison table",

        "Reporting Status":
            "Primary",

        "Interpretive Boundary":
            integrated_conclusion("F5"),
    },

    {
        "Results Section":
            "Environmental association",

        "Finding":
            (
                "Electrical activity co-varied with temperature "
                "and soil moisture during the pronounced "
                "21 August LDPE session."
            ),

        "Quantitative Evidence":
            (
                f"Temperature: {ldpe21_temp_assoc}. "
                f"Humidity: {ldpe21_humidity_assoc}. "
                f"Soil moisture: {ldpe21_soil_assoc}."
            ),

        "Recommended Figure/Table":
            "Environmental-electrical association table",

        "Reporting Status":
            "Exploratory",

        "Interpretive Boundary":
            integrated_conclusion("F4"),
    },

    {
        "Results Section":
            "Sensitivity and data quality",

        "Finding":
            (
                "Known acquisition anomalies materially altered "
                "raw measurements and required variable-specific "
                "screening."
            ),

        "Quantitative Evidence":
            (
                f"Control soil: {control21_soil_sensitivity}. "
                f"LDPE soil: {ldpe25_soil_sensitivity}. "
                f"LDPE electrical: "
                f"{ldpe25_electrical_sensitivity}."
            ),

        "Recommended Figure/Table":
            "Sensitivity-analysis table",

        "Reporting Status":
            "Primary methodological evidence",

        "Interpretive Boundary":
            integrated_conclusion("F6"),
    },

    {
        "Results Section":
            "Overall experimental finding",

        "Finding":
            (
                "The experiment detected candidate response "
                "patterns but did not establish an "
                "LDPE-specific causal effect."
            ),

        "Quantitative Evidence":
            (
                f"Pronounced LDPE session: {ldpe21}. "
                f"Matched electrical comparison: "
                f"{matched_electrical}."
            ),

        "Recommended Figure/Table":
            "Integrated evidence summary",

        "Reporting Status":
            "Overall conclusion",

        "Interpretive Boundary":
            integrated_conclusion("F7"),
    },
]


results = pd.DataFrame(rows)


# ------------------------------------------------------------
# Add reporting order
# ------------------------------------------------------------

results.insert(
    0,
    "Reporting Order",
    range(
        1,
        len(results) + 1
    )
)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

results.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print()
print("Dissertation Results Evidence")
print("=" * 92)

print()

print(
    f"Total evidence blocks : {len(results)}"
)

print()

print("Reporting-status distribution")
print("-" * 92)

for status, count in (
    results["Reporting Status"]
    .value_counts()
    .items()
):

    print(
        f"{status:<35} : {count}"
    )


print()
print("Validation checks")
print("-" * 92)

print(
    "Data-quality section included        :",
    results[
        "Results Section"
    ]
    .eq(
        "Data quality and analytical dataset"
    )
    .any()
)

print(
    "LDPE 21 Aug result included          :",
    results[
        "Quantitative Evidence"
    ]
    .str.contains(
        "78.562",
        na=False
    )
    .any()
)

print(
    "Matched electrical effect included   :",
    results[
        "Quantitative Evidence"
    ]
    .str.contains(
        "0.145",
        na=False
    )
    .any()
)

print(
    "Sensitivity evidence included        :",
    results[
        "Quantitative Evidence"
    ]
    .str.contains(
        "1822.25",
        na=False
    )
    .any()
)

print(
    "Causal limitation included           :",
    results[
        "Interpretive Boundary"
    ]
    .str.contains(
        "caus",
        case=False,
        na=False
    )
    .any()
)

print(
    "Pseudoreplication warning included   :",
    results[
        "Interpretive Boundary"
    ]
    .str.contains(
        "not independent biological replicates",
        case=False,
        na=False
    )
    .any()
)

print(
    "No missing evidence blocks           :",
    results.notna().all().all()
)


print()
print("Recommended Results Structure")
print("=" * 92)

for _, row in results.iterrows():

    print()

    print(
        f"{row['Reporting Order']}. "
        f"{row['Results Section']}"
    )

    print(
        f"Finding: {row['Finding']}"
    )

    print(
        f"Status: {row['Reporting Status']}"
    )

    print(
        f"Evidence: {row['Quantitative Evidence']}"
    )

    print(
        f"Boundary: {row['Interpretive Boundary']}"
    )


print()
print("=" * 92)

print(
    "Dissertation results evidence file created:"
)

print(
    f"  {OUTPUT_FILE}"
)
