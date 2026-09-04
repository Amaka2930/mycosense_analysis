import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ------------------------------------------------------------
# MycoSense
# Step 53: Session-Level Time-Series Visualisation
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

FIGURE_DIR = (
    BASE_DIR
    / "outputs"
    / "figures"
)

FIGURE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# Load and prepare data
# ------------------------------------------------------------

control = pd.read_csv(CONTROL_FILE)
ldpe = pd.read_csv(LDPE_FILE)


def prepare_data(data, condition):

    data = data.copy()

    data["Timestamp UTC"] = pd.to_datetime(
        data["Timestamp UTC"],
        utc=True,
        errors="coerce"
    )

    data = data.sort_values(
        "Timestamp UTC"
    ).reset_index(drop=True)

    data["Condition"] = condition

    return data


control = prepare_data(
    control,
    "Control"
)

ldpe = prepare_data(
    ldpe,
    "LDPE"
)


# ------------------------------------------------------------
# Assign sessions using the validated >10-minute rule
# ------------------------------------------------------------

SESSION_GAP_MINUTES = 10


def assign_sessions(data):

    data = data.copy()

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


control = assign_sessions(control)
ldpe = assign_sessions(ldpe)


# ------------------------------------------------------------
# Analysis variables
# ------------------------------------------------------------

VARIABLES = {
    "Electrical Activity":
        (
            "Electrical Analysis (mV)",
            "Electrical Activity (mV)",
            "electrical_activity"
        ),

    "Soil Moisture":
        (
            "Soil Moisture Analysis (%)",
            "Soil Moisture (%)",
            "soil_moisture"
        ),

    "Temperature":
        (
            "Temperature Analysis (C)",
            "Temperature (C)",
            "temperature"
        ),

    "Humidity":
        (
            "Humidity Analysis (%)",
            "Humidity (%)",
            "humidity"
        ),

    "pH":
        (
            "pH Analysis",
            "pH",
            "ph"
        ),
}


# ------------------------------------------------------------
# Plot each condition separately.
#
# Important:
# Each monitoring session is drawn as a separate line.
# We do NOT connect observations across session gaps.
# ------------------------------------------------------------

def plot_condition_variable(
    data,
    condition,
    column,
    ylabel,
    filename
):

    fig, ax = plt.subplots(
        figsize=(11, 6)
    )

    plotted_sessions = 0

    for session_id, session in data.groupby(
        "Session ID",
        sort=True
    ):

        valid = session[
            [
                "Timestamp UTC",
                column
            ]
        ].dropna()

        if valid.empty:
            continue

        session_start = (
            session["Timestamp UTC"].min()
        )

        elapsed_minutes = (
            valid["Timestamp UTC"]
            - session_start
        ).dt.total_seconds() / 60

        session_date = (
            session_start.strftime(
                "%d %b %Y"
            )
        )

        ax.plot(
            elapsed_minutes,
            valid[column],
            marker=".",
            markersize=3,
            linewidth=1,
            label=(
                f"Session {session_id} "
                f"({session_date})"
            )
        )

        plotted_sessions += 1

    ax.set_title(
        f"{condition}: {ylabel} by Monitoring Session"
    )

    ax.set_xlabel(
        "Elapsed Time Within Session (minutes)"
    )

    ax.set_ylabel(
        ylabel
    )

    ax.grid(
        True,
        alpha=0.25
    )

    if plotted_sessions > 0:

        ax.legend(
            fontsize=8,
            loc="best"
        )

    fig.tight_layout()

    output_path = (
        FIGURE_DIR
        / f"{condition.lower()}_{filename}_by_session.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    return output_path, plotted_sessions


# ------------------------------------------------------------
# Create figures
# ------------------------------------------------------------

print()
print("Session-Level Time-Series Visualisation")
print("-" * 72)


created_figures = []


for variable_name, (
    column,
    ylabel,
    filename
) in VARIABLES.items():

    print()
    print(variable_name)
    print("-" * 72)

    control_path, control_count = (
        plot_condition_variable(
            control,
            "Control",
            column,
            ylabel,
            filename
        )
    )

    ldpe_path, ldpe_count = (
        plot_condition_variable(
            ldpe,
            "LDPE",
            column,
            ylabel,
            filename
        )
    )

    created_figures.extend(
        [
            control_path,
            ldpe_path
        ]
    )

    print(
        f"  Control sessions plotted : "
        f"{control_count}"
    )

    print(
        f"  LDPE sessions plotted    : "
        f"{ldpe_count}"
    )

    print(
        f"  Control figure           : "
        f"{control_path.name}"
    )

    print(
        f"  LDPE figure              : "
        f"{ldpe_path.name}"
    )


# ------------------------------------------------------------
# Specific diagnostic:
# LDPE electrical activity on 21 August
#
# Step 52 showed unusually high variability in this session.
# We therefore create a dedicated high-resolution figure.
# ------------------------------------------------------------

ldpe_aug21 = ldpe[
    (
        ldpe["Timestamp UTC"]
        .dt.date
        ==
        pd.Timestamp(
            "2026-08-21"
        ).date()
    )
    &
    (
        ldpe[
            "Electrical Analysis (mV)"
        ].notna()
    )
].copy()


print()
print("LDPE 21 August Electrical Diagnostic")
print("-" * 72)

print(
    f"Valid electrical observations : "
    f"{len(ldpe_aug21)}"
)


if not ldpe_aug21.empty:

    start_time = (
        ldpe_aug21[
            "Timestamp UTC"
        ].min()
    )

    ldpe_aug21[
        "Elapsed Minutes"
    ] = (
        ldpe_aug21[
            "Timestamp UTC"
        ]
        - start_time
    ).dt.total_seconds() / 60


    fig, ax = plt.subplots(
        figsize=(11, 6)
    )

    ax.plot(
        ldpe_aug21[
            "Elapsed Minutes"
        ],
        ldpe_aug21[
            "Electrical Analysis (mV)"
        ],
        marker=".",
        markersize=4,
        linewidth=1
    )

    ax.axhline(
        y=0,
        linewidth=0.8
    )

    ax.set_title(
        "LDPE: Electrical Activity on 21 August 2026"
    )

    ax.set_xlabel(
        "Elapsed Time (minutes)"
    )

    ax.set_ylabel(
        "Electrical Activity (mV)"
    )

    ax.grid(
        True,
        alpha=0.25
    )

    fig.tight_layout()

    diagnostic_path = (
        FIGURE_DIR
        / "ldpe_21_august_electrical_diagnostic.png"
    )

    fig.savefig(
        diagnostic_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    created_figures.append(
        diagnostic_path
    )

    print(
        "Diagnostic figure created : "
        f"{diagnostic_path.name}"
    )


# ------------------------------------------------------------
# Specific matched-session diagnostic:
# Control and LDPE 24 August
#
# These sessions were recorded almost simultaneously and each
# contains 21 valid electrical observations.
# ------------------------------------------------------------

control_aug24 = control[
    (
        control["Timestamp UTC"]
        .dt.date
        ==
        pd.Timestamp(
            "2026-08-24"
        ).date()
    )
    &
    (
        control[
            "Electrical Analysis (mV)"
        ].notna()
    )
].copy()


ldpe_aug24 = ldpe[
    (
        ldpe["Timestamp UTC"]
        .dt.date
        ==
        pd.Timestamp(
            "2026-08-24"
        ).date()
    )
    &
    (
        ldpe[
            "Electrical Analysis (mV)"
        ].notna()
    )
].copy()


print()
print("24 August Matched Electrical Diagnostic")
print("-" * 72)

print(
    f"Control valid electrical observations : "
    f"{len(control_aug24)}"
)

print(
    f"LDPE valid electrical observations    : "
    f"{len(ldpe_aug24)}"
)


if (
    not control_aug24.empty
    and
    not ldpe_aug24.empty
):

    common_start = min(
        control_aug24[
            "Timestamp UTC"
        ].min(),

        ldpe_aug24[
            "Timestamp UTC"
        ].min()
    )

    control_aug24[
        "Elapsed Minutes"
    ] = (
        control_aug24[
            "Timestamp UTC"
        ]
        - common_start
    ).dt.total_seconds() / 60

    ldpe_aug24[
        "Elapsed Minutes"
    ] = (
        ldpe_aug24[
            "Timestamp UTC"
        ]
        - common_start
    ).dt.total_seconds() / 60


    fig, ax = plt.subplots(
        figsize=(11, 6)
    )

    ax.plot(
        control_aug24[
            "Elapsed Minutes"
        ],
        control_aug24[
            "Electrical Analysis (mV)"
        ],
        marker="o",
        markersize=3,
        linewidth=1,
        label="Control"
    )

    ax.plot(
        ldpe_aug24[
            "Elapsed Minutes"
        ],
        ldpe_aug24[
            "Electrical Analysis (mV)"
        ],
        marker="s",
        markersize=3,
        linewidth=1,
        label="LDPE"
    )

    ax.set_title(
        "Control and LDPE Electrical Activity: "
        "24 August 2026"
    )

    ax.set_xlabel(
        "Elapsed Time from Common Start (minutes)"
    )

    ax.set_ylabel(
        "Electrical Activity (mV)"
    )

    ax.grid(
        True,
        alpha=0.25
    )

    ax.legend()

    fig.tight_layout()

    matched_path = (
        FIGURE_DIR
        / "matched_24_august_electrical_comparison.png"
    )

    fig.savefig(
        matched_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    created_figures.append(
        matched_path
    )

    print(
        "Matched figure created : "
        f"{matched_path.name}"
    )


# ------------------------------------------------------------
# Final validation
# ------------------------------------------------------------

print()
print("Figure Creation Validation")
print("-" * 72)

existing_figures = [
    path
    for path in created_figures
    if path.exists()
]

print(
    f"Figures requested : "
    f"{len(created_figures)}"
)

print(
    f"Figures confirmed : "
    f"{len(existing_figures)}"
)

print(
    "All requested figures created :",
    len(existing_figures)
    == len(created_figures)
)

print()
print("Figures saved in:")
print(f"  {FIGURE_DIR}")

