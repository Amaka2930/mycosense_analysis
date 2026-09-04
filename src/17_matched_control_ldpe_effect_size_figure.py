import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 67: Matched Control vs LDPE Effect-Size Figure
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "tables"
    / "control_vs_ldpe_comparison_summary.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "figures"
    / "matched_control_vs_ldpe_effect_sizes.png"
)


# ------------------------------------------------------------
# Load comparison table
# ------------------------------------------------------------

comparison = pd.read_csv(INPUT_FILE)


# ------------------------------------------------------------
# Extract Cliff's delta values
# ------------------------------------------------------------

comparison["Cliffs_Delta"] = (
    comparison["Comparative Result"]
    .str.extract(r"Cliff's delta=([-+]?\d*\.?\d+)")[0]
    .astype(float)
)


def classify_delta(value):
    magnitude = abs(value)

    if magnitude < 0.147:
        return "Negligible"
    elif magnitude < 0.33:
        return "Small"
    elif magnitude < 0.474:
        return "Medium"
    else:
        return "Large"


comparison["Magnitude"] = (
    comparison["Cliffs_Delta"]
    .apply(classify_delta)
)


# ------------------------------------------------------------
# Print values for validation
# ------------------------------------------------------------

print()
print(
    "Matched Control – No Plastic vs "
    "LDPE – Plastic Exposed Effect Sizes"
)
print("=" * 90)

print(
    comparison[
        [
            "Variable",
            "Cliffs_Delta",
            "Magnitude",
        ]
    ].to_string(index=False)
)

print()


# ------------------------------------------------------------
# Create figure
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.barh(
    comparison["Variable"],
    comparison["Cliffs_Delta"],
)

ax.axvline(
    0,
    linewidth=1,
)

# Small-effect reference boundaries
ax.axvline(
    0.147,
    linestyle="--",
    linewidth=1,
)

ax.axvline(
    -0.147,
    linestyle="--",
    linewidth=1,
)

ax.set_xlabel("Cliff's delta")

ax.set_ylabel("Measured variable")

ax.set_title(
    "Matched Control – No Plastic vs "
    "LDPE – Plastic Exposed\n"
    "24 August Effect-Size Comparison"
)


# ------------------------------------------------------------
# Add labels to bars
# ------------------------------------------------------------

for bar, value, magnitude in zip(
    bars,
    comparison["Cliffs_Delta"],
    comparison["Magnitude"],
):
    x_position = (
        value + 0.012
        if value >= 0
        else value - 0.012
    )

    horizontal_alignment = (
        "left"
        if value >= 0
        else "right"
    )

    ax.text(
        x_position,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.3f} ({magnitude})",
        va="center",
        ha=horizontal_alignment,
    )


ax.set_xlim(-0.35, 0.35)

ax.grid(
    axis="x",
    alpha=0.25,
)

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight",
)

plt.close()


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print("=" * 90)
print("Validation checks")
print("-" * 90)

print(
    "Five variables plotted             :",
    len(comparison) == 5
)

print(
    "No missing Cliff's delta values    :",
    comparison["Cliffs_Delta"]
    .notna()
    .all()
)

print(
    "Electrical activity included       :",
    comparison["Variable"]
    .eq("Electrical Activity")
    .any()
)

print(
    "Soil moisture included             :",
    comparison["Variable"]
    .eq("Soil Moisture")
    .any()
)

print(
    "Output figure created              :",
    OUTPUT_FILE.exists()
)

print()
print("Figure saved to:")
print(f"  {OUTPUT_FILE}")

