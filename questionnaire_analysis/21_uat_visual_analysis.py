import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "mycosense_uat_analysis_ready.csv"
FIGURE_DIR = BASE_DIR / "outputs" / "figures"
TABLE_DIR = BASE_DIR / "outputs" / "tables"

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)

likert_cols = [f"Q14_{i}" for i in range(1, 11)]

labels = {
    "Q14_1": "Easy navigation",
    "Q14_2": "Sensor identification",
    "Q14_3": "Information clarity",
    "Q14_4": "Control/LDPE distinction",
    "Q14_5": "Condition comparison",
    "Q14_6": "System responsiveness",
    "Q14_7": "Information usefulness",
    "Q14_8": "Visual presentation",
    "Q14_9": "Minimal assistance",
    "Q14_10": "Overall satisfaction"
}

print()
print("MYCOSENSE UAT - VISUAL ANALYSIS")
print("=" * 80)


# ============================================================
# FIGURE 1 - MEAN SCORE BY CRITERION
# ============================================================

means = df[likert_cols].mean()

mean_df = pd.DataFrame({
    "Criterion": [labels[col] for col in likert_cols],
    "Mean": [means[col] for col in likert_cols]
}).sort_values("Mean")

plt.figure(figsize=(10, 7))

bars = plt.barh(
    mean_df["Criterion"],
    mean_df["Mean"]
)

plt.axvline(4, linestyle="--", linewidth=1)

plt.xlabel("Mean Likert Score (1 = Strongly Disagree, 5 = Strongly Agree)")
plt.title("Mean User Acceptance Scores for MycoSense")
plt.xlim(1, 5.1)

for bar, value in zip(bars, mean_df["Mean"]):
    plt.text(
        value + 0.03,
        bar.get_y() + bar.get_height()/2,
        f"{value:.2f}",
        va="center"
    )

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "uat_visual_01_mean_scores.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 2 - AGREE VS STRONGLY AGREE BY CRITERION
# ============================================================

agree = []
strongly_agree = []

for col in likert_cols:
    agree.append((df[col] == 4).sum())
    strongly_agree.append((df[col] == 5).sum())

response_df = pd.DataFrame({
    "Criterion": [labels[col] for col in likert_cols],
    "Agree": agree,
    "Strongly Agree": strongly_agree
})

plt.figure(figsize=(11, 7))

plt.barh(
    response_df["Criterion"],
    response_df["Agree"],
    label="Agree"
)

plt.barh(
    response_df["Criterion"],
    response_df["Strongly Agree"],
    left=response_df["Agree"],
    label="Strongly Agree"
)

plt.xlabel("Number of Participants (n = 6)")
plt.title("Positive UAT Response Distribution by Criterion")
plt.legend()

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "uat_visual_02_positive_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 3 - OVERALL RESPONSE DISTRIBUTION
# ============================================================

all_responses = df[likert_cols].to_numpy().flatten()

categories = [
    "Strongly Disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly Agree"
]

counts = [
    (all_responses == 1).sum(),
    (all_responses == 2).sum(),
    (all_responses == 3).sum(),
    (all_responses == 4).sum(),
    (all_responses == 5).sum()
]

percentages = [
    count / len(all_responses) * 100
    for count in counts
]

overall_df = pd.DataFrame({
    "Response": categories,
    "Count": counts,
    "Percentage": percentages
})

overall_df.to_csv(
    TABLE_DIR / "uat_visual_overall_distribution.csv",
    index=False
)

plt.figure(figsize=(9, 6))

bars = plt.bar(
    categories,
    percentages
)

plt.ylabel("Percentage of All UAT Responses (%)")
plt.xlabel("Likert Response")
plt.title("Overall Distribution of MycoSense UAT Responses")
plt.ylim(0, 100)

for bar, value, count in zip(bars, percentages, counts):
    plt.text(
        bar.get_x() + bar.get_width()/2,
        value + 2,
        f"{value:.1f}%\n(n={count})",
        ha="center"
    )

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "uat_visual_03_overall_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FIGURE 4 - PROTOTYPE SUITABILITY
# Q18: 1 = Yes, 2 = Partially
# ============================================================

q18 = pd.to_numeric(df["Q18"], errors="coerce")

yes_count = (q18 == 1).sum()
partial_count = (q18 == 2).sum()

suitability_labels = ["Yes", "Partially"]
suitability_counts = [yes_count, partial_count]

total = sum(suitability_counts)

suitability_percentages = [
    count / total * 100
    for count in suitability_counts
]

plt.figure(figsize=(7, 6))

bars = plt.bar(
    suitability_labels,
    suitability_percentages
)

plt.ylabel("Participants (%)")
plt.xlabel("Suitability Response")
plt.title("Perceived Suitability of MycoSense as a Prototype")
plt.ylim(0, 100)

for bar, value, count in zip(
    bars,
    suitability_percentages,
    suitability_counts
):
    plt.text(
        bar.get_x() + bar.get_width()/2,
        value + 2,
        f"{value:.1f}%\n({count}/{total})",
        ha="center"
    )

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "uat_visual_04_prototype_suitability.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print()
print("VISUAL SUMMARY")
print("-" * 80)

print(f"Valid participants                 : {len(df)}")
print(f"Total Likert responses             : {len(all_responses)}")
print(f"Strongly Agree                     : {counts[4]} ({percentages[4]:.1f}%)")
print(f"Agree                              : {counts[3]} ({percentages[3]:.1f}%)")
print(f"Neutral/negative responses         : {sum(counts[:3])}")
print(f"Prototype suitable - Yes           : {yes_count}/{total} ({yes_count/total*100:.1f}%)")
print(f"Prototype suitable - Partially     : {partial_count}/{total} ({partial_count/total*100:.1f}%)")

print()
print("FIGURES CREATED")
print("-" * 80)

for file in sorted(FIGURE_DIR.glob("uat_visual_*.png")):
    print(file.name)

print()
print("=" * 80)
print("Visual analysis complete.")
