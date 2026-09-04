import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "mycosense_uat_raw.csv"

OUTPUT_DIR = BASE_DIR / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD AND CLEAN DATA
# ============================================================

df = pd.read_csv(RAW_FILE)

# Remove Qualtrics metadata rows
df = df.iloc[2:].copy()

# Retain genuine anonymous responses only
df = df[
    df["DistributionChannel"]
    .astype(str)
    .str.lower()
    .eq("anonymous")
].copy()

consent_items = [f"Q12_{i}" for i in range(1, 10)]
likert_cols = [f"Q14_{i}" for i in range(1, 11)]

numeric_cols = (
    consent_items
    + ["Q13", "Progress", "Finished", "Q18"]
    + likert_cols
)

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Valid participant criteria
valid = (
    df["Progress"].eq(100)
    & df["Finished"].eq(1)
    & df[consent_items].eq(1).all(axis=1)
    & df["Q13"].eq(1)
    & df[likert_cols].notna().all(axis=1)
)

uat = df.loc[valid].copy()

print()
print("MYCOSENSE USER ACCEPTANCE TESTING - COMPLETE ANALYSIS")
print("=" * 90)
print(f"Valid participants: {len(uat)}")


# ============================================================
# SAVE ANALYSIS-READY DATA
# ============================================================

analysis_cols = (
    likert_cols
    + ["Q16_1", "Q16_2", "Q16_3", "Q18"]
)

uat[analysis_cols].to_csv(
    PROCESSED_DIR / "mycosense_uat_analysis_ready.csv",
    index=False
)


# ============================================================
# QUESTION LABELS
# ============================================================

labels = {
    "Q14_1": "Dashboard easy to navigate",
    "Q14_2": "Easy to identify sensor measurements",
    "Q14_3": "Information clear and understandable",
    "Q14_4": "Could distinguish Control and LDPE",
    "Q14_5": "Could compare experimental conditions",
    "Q14_6": "System responded as expected",
    "Q14_7": "Dashboard provided useful information",
    "Q14_8": "Visual presentation supported understanding",
    "Q14_9": "Confident using with minimal assistance",
    "Q14_10": "Overall satisfaction",
}


# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

results = []

for col in likert_cols:

    responses = uat[col].dropna()

    results.append({
        "Question": col,
        "Criterion": labels[col],
        "N": len(responses),
        "Mean": responses.mean(),
        "Median": responses.median(),
        "Std_Dev": responses.std(ddof=1),
        "Minimum": responses.min(),
        "Maximum": responses.max(),
        "Agree_n": (responses == 4).sum(),
        "Strongly_Agree_n": (responses == 5).sum(),
        "Positive_n": responses.isin([4, 5]).sum(),
        "Positive_Percent": responses.isin([4, 5]).mean() * 100
    })

summary = pd.DataFrame(results)

summary.to_csv(
    TABLE_DIR / "uat_likert_descriptive_statistics.csv",
    index=False
)

print()
print("LIKERT DESCRIPTIVE STATISTICS")
print("-" * 90)

print(
    summary[
        [
            "Question",
            "Criterion",
            "N",
            "Mean",
            "Median",
            "Agree_n",
            "Strongly_Agree_n",
            "Positive_Percent"
        ]
    ].round(2).to_string(index=False)
)


# ============================================================
# OVERALL ACCEPTANCE
# ============================================================

all_responses = uat[likert_cols].to_numpy().flatten()

overall_mean = np.mean(all_responses)
overall_median = np.median(all_responses)

strongly_agree = np.sum(all_responses == 5)
agree = np.sum(all_responses == 4)
neutral = np.sum(all_responses == 3)
disagree = np.sum(all_responses == 2)
strongly_disagree = np.sum(all_responses == 1)

positive = strongly_agree + agree
total = len(all_responses)

overall_table = pd.DataFrame({
    "Measure": [
        "Valid participants",
        "Total Likert responses",
        "Overall mean",
        "Overall median",
        "Strongly Agree",
        "Agree",
        "Neutral",
        "Disagree",
        "Strongly Disagree",
        "Positive responses",
        "Positive response percentage"
    ],
    "Value": [
        len(uat),
        total,
        round(overall_mean, 3),
        round(overall_median, 3),
        strongly_agree,
        agree,
        neutral,
        disagree,
        strongly_disagree,
        positive,
        round((positive / total) * 100, 2)
    ]
})

overall_table.to_csv(
    TABLE_DIR / "uat_overall_acceptance_summary.csv",
    index=False
)

print()
print("=" * 90)
print("OVERALL USER ACCEPTANCE")
print("-" * 90)

print(f"Participants              : {len(uat)}")
print(f"Total Likert responses    : {total}")
print(f"Overall mean score        : {overall_mean:.2f} / 5")
print(f"Overall median            : {overall_median:.2f}")
print(f"Strongly Agree            : {strongly_agree}")
print(f"Agree                     : {agree}")
print(f"Neutral                   : {neutral}")
print(f"Disagree                  : {disagree}")
print(f"Strongly Disagree         : {strongly_disagree}")
print(f"Positive responses        : {positive}/{total}")
print(f"Positive percentage       : {(positive/total)*100:.1f}%")


# ============================================================
# SUITABILITY
# ============================================================

suitability = (
    uat["Q18"]
    .value_counts()
    .sort_index()
)

print()
print("=" * 90)
print("PROTOTYPE SUITABILITY - Q18")
print("-" * 90)

print(suitability)

suitability_table = pd.DataFrame({
    "Response_Code": suitability.index,
    "Count": suitability.values,
    "Percentage": (
        suitability.values / suitability.values.sum() * 100
    )
})

suitability_table.to_csv(
    TABLE_DIR / "uat_prototype_suitability.csv",
    index=False
)


# ============================================================
# QUALITATIVE FEEDBACK
# ============================================================

print()
print("=" * 90)
print("QUALITATIVE FEEDBACK")
print("=" * 90)

qualitative_questions = {
    "Q16_1": "MOST USEFUL",
    "Q16_2": "DIFFICULTIES / CONFUSION",
    "Q16_3": "RECOMMENDED IMPROVEMENT"
}

qualitative_rows = []

for col, heading in qualitative_questions.items():

    print()
    print(heading)
    print("-" * 90)

    responses = uat[col].dropna()

    for number, response in enumerate(responses, start=1):
        response = str(response).strip()

        if response:
            print(f"{number}. {response}")

            qualitative_rows.append({
                "Question": col,
                "Category": heading,
                "Response": response
            })

pd.DataFrame(qualitative_rows).to_csv(
    TABLE_DIR / "uat_qualitative_feedback.csv",
    index=False
)


# ============================================================
# FIGURE 1 - MEAN UAT SCORES
# ============================================================

plot_data = summary.sort_values("Mean")

plt.figure(figsize=(10, 7))

plt.barh(
    plot_data["Criterion"],
    plot_data["Mean"]
)

plt.axvline(
    4,
    linestyle="--",
    linewidth=1
)

plt.xlabel("Mean Likert Score (1-5)")
plt.ylabel("")
plt.title("MycoSense User Acceptance Evaluation")
plt.xlim(1, 5)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "uat_mean_scores.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 2 - RESPONSE DISTRIBUTION
# ============================================================

distribution = []

for col in likert_cols:

    responses = uat[col]

    distribution.append({
        "Criterion": labels[col],
        "Strongly Disagree": (responses == 1).sum(),
        "Disagree": (responses == 2).sum(),
        "Neutral": (responses == 3).sum(),
        "Agree": (responses == 4).sum(),
        "Strongly Agree": (responses == 5).sum()
    })

distribution_df = pd.DataFrame(distribution)

distribution_df.to_csv(
    TABLE_DIR / "uat_response_distribution.csv",
    index=False
)

plot_df = distribution_df.set_index("Criterion")

plt.figure(figsize=(11, 8))

left = np.zeros(len(plot_df))

for response_category in [
    "Strongly Disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly Agree"
]:
    values = plot_df[response_category].values

    plt.barh(
        plot_df.index,
        values,
        left=left,
        label=response_category
    )

    left += values

plt.xlabel("Number of Participants")
plt.ylabel("")
plt.title("Distribution of MycoSense UAT Responses")
plt.legend(loc="lower right")

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "uat_likert_response_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 90)
print("FILES CREATED")
print("-" * 90)

print("Processed data:")
print(PROCESSED_DIR / "mycosense_uat_analysis_ready.csv")

print()
print("Tables:")
for file in sorted(TABLE_DIR.glob("*.csv")):
    print(file.name)

print()
print("Figures:")
for file in sorted(FIGURE_DIR.glob("*.png")):
    print(file.name)

print()
print("=" * 90)
print("UAT analysis complete.")
