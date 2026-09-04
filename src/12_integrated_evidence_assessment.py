import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 59: Integrated Evidence Assessment
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "master_results_table.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "integrated_evidence_assessment.csv"
)


# ------------------------------------------------------------
# Load authoritative master results
# ------------------------------------------------------------

master = pd.read_csv(MASTER_FILE)


# ------------------------------------------------------------
# Helper: retrieve exactly one master result
# ------------------------------------------------------------

def get_result(evidence_type, comparison, metric):

    subset = master[
        master["Evidence Type"].eq(evidence_type)
        &
        master["Comparison / Session"].eq(comparison)
        &
        master["Metric"].eq(metric)
    ]

    if len(subset) != 1:
        raise ValueError(
            f"Expected exactly one result for:\n"
            f"Evidence Type = {evidence_type}\n"
            f"Comparison = {comparison}\n"
            f"Metric = {metric}\n"
            f"Found = {len(subset)}"
        )

    return subset.iloc[0]["Result"]


# ------------------------------------------------------------
# Retrieve key evidence
# ------------------------------------------------------------

ldpe21_electrical = get_result(
    "Electrical session behaviour",
    "LDPE 21 August Session 3",
    "Electrical Activity",
)

control21_electrical = get_result(
    "Electrical session behaviour",
    "Control 21 August Session 4",
    "Electrical Activity",
)

control25_electrical = get_result(
    "Electrical session behaviour",
    "Control 25 August Session 8",
    "Electrical Activity",
)

matched_electrical = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Electrical Activity",
)

matched_temperature = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Temperature",
)

matched_humidity = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Humidity",
)

matched_soil = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "Soil Moisture",
)

matched_ph = get_result(
    "Matched 24 August comparison",
    "Control vs LDPE",
    "pH",
)

ldpe21_temperature_association = get_result(
    "Environmental association",
    "LDPE 21 August Session 3",
    "Electrical vs Temperature",
)

ldpe21_soil_association = get_result(
    "Environmental association",
    "LDPE 21 August Session 3",
    "Electrical vs Soil Moisture",
)

ldpe25_fault = get_result(
    "Sensitivity analysis",
    "LDPE 2026-08-25 Session 6",
    "Electrical Activity",
)

ldpe25_soil_fault = get_result(
    "Sensitivity analysis",
    "LDPE 2026-08-25 Session 6",
    "Soil Moisture",
)


# ------------------------------------------------------------
# Build integrated evidence assessment
# ------------------------------------------------------------

rows = [

    {
        "Finding ID": "F1",

        "Analytical Question":
            "Did MycoSense detect measurable fungal electrical activity?",

        "Supporting Evidence":
            (
                "Valid electrical measurements were recorded in both "
                "Control and LDPE conditions across multiple monitoring "
                "sessions. Session-level electrical distributions showed "
                "changes in median, spread and temporal behaviour."
            ),

        "Key Quantitative Evidence":
            (
                f"LDPE 21 Aug: {ldpe21_electrical} | "
                f"Control 21 Aug: {control21_electrical}"
            ),

        "Counter / Qualifying Evidence":
            (
                "Electrical activity varied substantially between sessions, "
                "and some extreme acquisition periods were identified as "
                "technical faults."
            ),

        "Evidence Strength":
            "Moderate",

        "Defensible Interpretation":
            (
                "The prototype successfully detected measurable and "
                "temporally varying fungal bioelectrical signals, supporting "
                "the feasibility of IoT-based fungal biosensing."
            ),
    },

    {
        "Finding ID": "F2",

        "Analytical Question":
            (
                "Was a pronounced electrical response observed in the "
                "LDPE-exposed condition?"
            ),

        "Supporting Evidence":
            (
                "The LDPE session on 21 August showed sustained high "
                "within-session electrical variability and a structured "
                "transition from positive to negative electrical activity."
            ),

        "Key Quantitative Evidence":
            ldpe21_electrical,

        "Counter / Qualifying Evidence":
            (
                f"Large electrical variation was not unique to LDPE. "
                f"Control evidence included: {control21_electrical}. "
                f"Control also showed substantial variability on 25 August: "
                f"{control25_electrical}."
            ),

        "Evidence Strength":
            "Moderate",

        "Defensible Interpretation":
            (
                "The 21 August LDPE pattern is a candidate episodic "
                "bioelectrical response. It should not be interpreted as "
                "proof of an LDPE-specific effect."
            ),
    },

    {
        "Finding ID": "F3",

        "Analytical Question":
            (
                "Did the closely time-matched comparison show clear "
                "electrical separation between Control and LDPE?"
            ),

        "Supporting Evidence":
            matched_electrical,

        "Key Quantitative Evidence":
            matched_electrical,

        "Counter / Qualifying Evidence":
            (
                "The matched monitoring window contained only one fungal "
                "cluster per condition and repeated timestamp observations "
                "within a short monitoring period."
            ),

        "Evidence Strength":
            "Weak for condition separation",

        "Defensible Interpretation":
            (
                "The closely matched 24 August session showed little "
                "distributional separation in electrical activity between "
                "Control and LDPE. This counterbalances the pronounced "
                "LDPE behaviour observed on 21 August."
            ),
    },

    {
        "Finding ID": "F4",

        "Analytical Question":
            (
                "Were electrical changes associated with environmental "
                "conditions during the pronounced LDPE session?"
            ),

        "Supporting Evidence":
            (
                f"Temperature association: "
                f"{ldpe21_temperature_association}. "
                f"Soil-moisture association: "
                f"{ldpe21_soil_association}."
            ),

        "Key Quantitative Evidence":
            (
                f"{ldpe21_temperature_association} | "
                f"{ldpe21_soil_association}"
            ),

        "Counter / Qualifying Evidence":
            (
                "Successive sensor observations were temporally dependent, "
                "humidity was constant within the analysed session, and the "
                "temperature range was narrow."
            ),

        "Evidence Strength":
            "Exploratory",

        "Defensible Interpretation":
            (
                "Electrical activity co-varied with temperature and soil "
                "moisture during the 21 August LDPE session, but these "
                "relationships are descriptive and cannot establish "
                "environmental or LDPE causation."
            ),
    },

    {
        "Finding ID": "F5",

        "Analytical Question":
            (
                "Did environmental differences remain important when "
                "Control and LDPE were monitored at nearly the same time?"
            ),

        "Supporting Evidence":
            (
                f"Temperature: {matched_temperature}. "
                f"Humidity: {matched_humidity}. "
                f"Soil moisture: {matched_soil}. "
                f"pH: {matched_ph}."
            ),

        "Key Quantitative Evidence":
            matched_soil,

        "Counter / Qualifying Evidence":
            (
                "The matched session was short and still involved only one "
                "fungal cluster per experimental condition."
            ),

        "Evidence Strength":
            "Descriptive",

        "Defensible Interpretation":
            (
                "Most matched environmental differences were small or "
                "negligible, while soil moisture showed a small "
                "distributional separation. Environmental measurements "
                "were nevertheless strongly session-dependent across the "
                "full experiment."
            ),
    },

    {
        "Finding ID": "F6",

        "Analytical Question":
            (
                "Did data-quality screening materially affect the "
                "interpretation of the experiment?"
            ),

        "Supporting Evidence":
            (
                f"LDPE electrical fault sensitivity result: "
                f"{ldpe25_fault}. "
                f"LDPE soil-moisture sensitivity result: "
                f"{ldpe25_soil_fault}."
            ),

        "Key Quantitative Evidence":
            ldpe25_fault,

        "Counter / Qualifying Evidence":
            (
                "Screening was variable-specific rather than a general "
                "removal of unusual values. The pronounced but technically "
                "plausible LDPE 21 August electrical observations remained "
                "in the analysis."
            ),

        "Evidence Strength":
            "Strong",

        "Defensible Interpretation":
            (
                "Predefined data-quality screening prevented documented "
                "acquisition faults from dominating the findings while "
                "preserving potentially meaningful biological variability."
            ),
    },

    {
        "Finding ID": "F7",

        "Analytical Question":
            (
                "Can the observed differences be attributed specifically "
                "to LDPE exposure?"
            ),

        "Supporting Evidence":
            (
                "The LDPE condition showed a pronounced structured "
                "electrical episode on 21 August and differences in some "
                "environmental and morphological observations."
            ),

        "Key Quantitative Evidence":
            (
                f"Pronounced LDPE session: {ldpe21_electrical}. "
                f"Matched electrical comparison: {matched_electrical}."
            ),

        "Counter / Qualifying Evidence":
            (
                "Only one fungal cluster represented each condition. "
                "Monitoring sessions were not fully environmentally matched, "
                "soil moisture differed between sessions, sunlight exposure "
                "was not fully controlled, and the matched 24 August "
                "electrical comparison showed negligible separation."
            ),

        "Evidence Strength":
            "Insufficient for causal attribution",

        "Defensible Interpretation":
            (
                "The experiment identifies candidate response patterns but "
                "does not establish that LDPE exposure caused the observed "
                "bioelectrical differences."
            ),
    },
]


evidence = pd.DataFrame(rows)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

evidence.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print()
print("Integrated Evidence Assessment")
print("=" * 88)

print()

print(
    f"Total integrated findings : {len(evidence)}"
)

print()

print("Evidence-strength distribution")
print("-" * 88)

for strength, count in (
    evidence["Evidence Strength"]
    .value_counts()
    .items()
):
    print(
        f"{strength:<35} : {count}"
    )


print()
print("Validation checks")
print("-" * 88)

print(
    "All finding IDs unique                  :",
    evidence["Finding ID"].is_unique
)

print(
    "No missing interpretations              :",
    evidence["Defensible Interpretation"].notna().all()
)

print(
    "Causal-attribution limitation included  :",
    evidence["Finding ID"].eq("F7").any()
)

print(
    "Data-quality evidence included           :",
    evidence["Finding ID"].eq("F6").any()
)

print(
    "Matched-session evidence included        :",
    evidence["Finding ID"].eq("F3").any()
)


print()
print("Interpretive Summary")
print("=" * 88)

for _, row in evidence.iterrows():

    print()

    print(
        f"{row['Finding ID']} | "
        f"{row['Evidence Strength']}"
    )

    print(
        row["Analytical Question"]
    )

    print(
        "Conclusion:"
    )

    print(
        row["Defensible Interpretation"]
    )


print()
print("=" * 88)

print(
    "Integrated evidence assessment created:"
)

print(
    f"  {OUTPUT_FILE}"
)
