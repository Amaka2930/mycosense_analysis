import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 60: Research Question Evidence Matrix
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

EVIDENCE_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "integrated_evidence_assessment.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "research_question_evidence_matrix.csv"
)


# ------------------------------------------------------------
# Load validated integrated evidence
# ------------------------------------------------------------

evidence = pd.read_csv(EVIDENCE_FILE)


# ------------------------------------------------------------
# Validation before interpretation
# ------------------------------------------------------------

expected_ids = {
    "F1", "F2", "F3", "F4", "F5", "F6", "F7"
}

actual_ids = set(
    evidence["Finding ID"]
    .dropna()
    .astype(str)
)

if actual_ids != expected_ids:

    raise ValueError(
        "Integrated evidence file does not contain "
        "the expected F1-F7 findings."
    )


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------

def finding_text(finding_id):

    subset = evidence[
        evidence["Finding ID"].eq(finding_id)
    ]

    if len(subset) != 1:

        raise ValueError(
            f"Expected exactly one row for {finding_id}; "
            f"found {len(subset)}."
        )

    row = subset.iloc[0]

    return (
        row["Defensible Interpretation"],
        row["Evidence Strength"]
    )


# ------------------------------------------------------------
# Retrieve validated findings
# ------------------------------------------------------------

F1, F1_strength = finding_text("F1")
F2, F2_strength = finding_text("F2")
F3, F3_strength = finding_text("F3")
F4, F4_strength = finding_text("F4")
F5, F5_strength = finding_text("F5")
F6, F6_strength = finding_text("F6")
F7, F7_strength = finding_text("F7")


# ------------------------------------------------------------
# Research question and objectives
# ------------------------------------------------------------

research_question = (
    "How can IoT technologies be used to explore how "
    "Pleurotus ostreatus responds to plastic pollution "
    "in its environment?"
)

rows = [

    {
        "Item ID": "RQ",

        "Research Item":
            research_question,

        "Relevant Findings":
            "F1; F2; F3; F4; F5; F6; F7",

        "Evidence Summary":
            (
                "MycoSense captured fungal bioelectrical and "
                "environmental measurements over time, identified "
                "a pronounced candidate LDPE-associated electrical "
                "episode, examined environmental co-variation, "
                "performed a closely time-matched Control-LDPE "
                "comparison, and applied data-quality screening "
                "to documented acquisition faults."
            ),

        "Level of Achievement":
            "Answered with important limitations",

        "Defensible Conclusion":
            (
                "IoT technologies can be used to explore fungal "
                "responses to plastic-polluted environments by "
                "integrating repeated bioelectrical and environmental "
                "measurements with time-series and comparative analysis. "
                "In this experiment, MycoSense identified measurable "
                "temporal variation and candidate response patterns, "
                "but the design does not establish that LDPE exposure "
                "caused those differences."
            ),
    },

    {
        "Item ID": "O1",

        "Research Item":
            (
                "Cultivate Pleurotus ostreatus and establish "
                "Control and LDPE-exposed experimental conditions."
            ),

        "Relevant Findings":
            "Experimental implementation",

        "Evidence Summary":
            (
                "Two experimental conditions were established: "
                "Control - No Plastic and LDPE Plastic Exposed. "
                "These conditions provided the physical basis for "
                "comparative IoT monitoring."
            ),

        "Level of Achievement":
            "Achieved",

        "Defensible Conclusion":
            (
                "The experimental conditions required for the "
                "exploratory comparison were successfully established."
            ),
    },

    {
        "Item ID": "O2",

        "Research Item":
            (
                "Measure fungal electrical activity using the "
                "MycoSense sensing system."
            ),

        "Relevant Findings":
            "F1; F2; F3",

        "Evidence Summary":
            (
                f"F1 ({F1_strength}): {F1} "
                f"F2 ({F2_strength}): {F2} "
                f"F3 ({F3_strength}): {F3}"
            ),

        "Level of Achievement":
            "Achieved",

        "Defensible Conclusion":
            (
                "MycoSense successfully captured usable fungal "
                "electrical measurements and detected substantial "
                "temporal and session-level variation."
            ),
    },

    {
        "Item ID": "O3",

        "Research Item":
            (
                "Monitor environmental conditions alongside "
                "fungal electrical activity."
            ),

        "Relevant Findings":
            "F4; F5",

        "Evidence Summary":
            (
                f"F4 ({F4_strength}): {F4} "
                f"F5 ({F5_strength}): {F5}"
            ),

        "Level of Achievement":
            "Achieved with data-quality limitations",

        "Defensible Conclusion":
            (
                "Temperature, humidity, soil moisture and limited "
                "quantitative pH measurements provided environmental "
                "context for interpreting the electrical signal. "
                "Coverage and validity differed between variables "
                "and monitoring sessions."
            ),
    },

    {
        "Item ID": "O4",

        "Research Item":
            (
                "Compare observed responses between the Control "
                "and LDPE-exposed conditions."
            ),

        "Relevant Findings":
            "F2; F3; F5; F7",

        "Evidence Summary":
            (
                f"F2 ({F2_strength}): {F2} "
                f"F3 ({F3_strength}): {F3} "
                f"F5 ({F5_strength}): {F5} "
                f"F7 ({F7_strength}): {F7}"
            ),

        "Level of Achievement":
            "Achieved descriptively",

        "Defensible Conclusion":
            (
                "The two conditions were compared at session and "
                "matched-session levels. Differences were observed, "
                "but they were not sufficiently consistent or "
                "controlled to support an LDPE-specific causal claim."
            ),
    },

    {
        "Item ID": "O5",

        "Research Item":
            (
                "Evaluate whether fungal electrical signals could "
                "serve as potential indicators of environmental response."
            ),

        "Relevant Findings":
            "F1; F2; F4; F6; F7",

        "Evidence Summary":
            (
                f"F1 ({F1_strength}): {F1} "
                f"F2 ({F2_strength}): {F2} "
                f"F4 ({F4_strength}): {F4} "
                f"F6 ({F6_strength}): {F6} "
                f"F7 ({F7_strength}): {F7}"
            ),

        "Level of Achievement":
            "Partially achieved",

        "Defensible Conclusion":
            (
                "The observed electrical signals show potential "
                "as exploratory indicators because measurable "
                "temporal responses and environmental co-variation "
                "were detected. Their specificity to LDPE cannot "
                "be established from this single-cluster exploratory "
                "design and requires replicated controlled validation."
            ),
    },
]


matrix = pd.DataFrame(rows)


# ------------------------------------------------------------
# Save matrix
# ------------------------------------------------------------

matrix.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print()
print("Research Question Evidence Matrix")
print("=" * 88)

print()

print(
    f"Total research items : {len(matrix)}"
)

print()

print("Achievement distribution")
print("-" * 88)

for level, count in (
    matrix["Level of Achievement"]
    .value_counts()
    .items()
):
    print(
        f"{level:<40} : {count}"
    )


print()
print("Validation checks")
print("-" * 88)

print(
    "Research question included             :",
    matrix["Item ID"].eq("RQ").any()
)

print(
    "Five objectives included               :",
    matrix["Item ID"].str.startswith("O").sum() == 5
)

print(
    "No missing conclusions                 :",
    matrix["Defensible Conclusion"].notna().all()
)

print(
    "Causal limitation preserved            :",
    matrix["Defensible Conclusion"]
    .str.contains(
        "caus",
        case=False,
        na=False
    )
    .any()
)

print(
    "Replication limitation preserved       :",
    matrix["Defensible Conclusion"]
    .str.contains(
        "replic",
        case=False,
        na=False
    )
    .any()
)


print()
print("Research Question")
print("=" * 88)

print(research_question)

print()

rq = matrix[
    matrix["Item ID"].eq("RQ")
].iloc[0]

print("Evidence-based answer:")
print(
    rq["Defensible Conclusion"]
)


print()
print("Objective Assessment")
print("=" * 88)

for _, row in matrix[
    matrix["Item ID"].str.startswith("O")
].iterrows():

    print()

    print(
        f"{row['Item ID']} | "
        f"{row['Level of Achievement']}"
    )

    print(
        row["Research Item"]
    )

    print("Conclusion:")

    print(
        row["Defensible Conclusion"]
    )


print()
print("=" * 88)

print(
    "Research question evidence matrix created:"
)

print(
    f"  {OUTPUT_FILE}"
)
