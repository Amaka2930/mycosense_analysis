from pathlib import Path

# ------------------------------------------------------------
# MycoSense Raw Data Inspection
# ------------------------------------------------------------

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Raw experimental datasets
CONTROL_FILE = RAW_DATA_DIR / "mycosense-control-2026-08-25.csv"
LDPE_FILE = RAW_DATA_DIR / "mycosense-ldpe_exposed-2026-08-25.csv"

print("MycoSense Data Inspection")
print("-" * 50)
print(f"Project root : {PROJECT_ROOT}")
print(f"Raw data     : {RAW_DATA_DIR}")
print(f"Control file : {CONTROL_FILE}")
print(f"LDPE file    : {LDPE_FILE}")

# ------------------------------------------------------------
# Load Raw Datasets
# ------------------------------------------------------------

import pandas as pd

control_df = pd.read_csv(CONTROL_FILE)
ldpe_df = pd.read_csv(LDPE_FILE)

print()
print("Dataset Dimensions")
print("-" * 50)
print(f"Control : {control_df.shape[0]} rows x {control_df.shape[1]} columns")
print(f"LDPE    : {ldpe_df.shape[0]} rows x {ldpe_df.shape[1]} columns")

# ------------------------------------------------------------
# Inspect Column Structure
# ------------------------------------------------------------

print()
print("Column Structure")
print("-" * 50)

print("Control columns:")
for number, column in enumerate(control_df.columns, start=1):
    print(f"  {number}. {column}")

print()
print("LDPE columns:")
for number, column in enumerate(ldpe_df.columns, start=1):
    print(f"  {number}. {column}")

print()
print(f"Same column structure: {control_df.columns.equals(ldpe_df.columns)}")

# ------------------------------------------------------------
# Inspect Data Types
# ------------------------------------------------------------

print()
print("Data Types")
print("-" * 50)

print("Control:")
print(control_df.dtypes)

print()
print("LDPE:")
print(ldpe_df.dtypes)

# ------------------------------------------------------------
# Inspect Sample Labels and Device IDs
# ------------------------------------------------------------

print()
print("Sample and Device Identification")
print("-" * 50)

print("Control - Sample Type values:")
print(control_df["Sample Type"].value_counts(dropna=False))

print()
print("Control - Device ID values:")
print(control_df["Device ID"].value_counts(dropna=False))

print()
print("LDPE - Sample Type values:")
print(ldpe_df["Sample Type"].value_counts(dropna=False))

print()
print("LDPE - Device ID values:")
print(ldpe_df["Device ID"].value_counts(dropna=False))

# ------------------------------------------------------------
# Inspect Missing Values
# ------------------------------------------------------------

print()
print("Missing Value Assessment")
print("-" * 50)

print("Control:")
control_missing = control_df.isna().sum()
control_missing_pct = (control_missing / len(control_df) * 100).round(2)

for column in control_df.columns:
    print(
        f"  {column:<28} "
        f"{control_missing[column]:>4} missing "
        f"({control_missing_pct[column]:>6.2f}%)"
    )

print()
print("LDPE:")
ldpe_missing = ldpe_df.isna().sum()
ldpe_missing_pct = (ldpe_missing / len(ldpe_df) * 100).round(2)

for column in ldpe_df.columns:
    print(
        f"  {column:<28} "
        f"{ldpe_missing[column]:>4} missing "
        f"({ldpe_missing_pct[column]:>6.2f}%)"
    )

# ------------------------------------------------------------
# Inspect Duplicate Records
# ------------------------------------------------------------

print()
print("Duplicate Record Assessment")
print("-" * 50)

control_exact_duplicates = control_df.duplicated().sum()
ldpe_exact_duplicates = ldpe_df.duplicated().sum()

control_duplicate_ids = control_df["ID"].duplicated().sum()
ldpe_duplicate_ids = ldpe_df["ID"].duplicated().sum()

print("Control:")
print(f"  Exact duplicate rows : {control_exact_duplicates}")
print(f"  Duplicate IDs        : {control_duplicate_ids}")

print()
print("LDPE:")
print(f"  Exact duplicate rows : {ldpe_exact_duplicates}")
print(f"  Duplicate IDs        : {ldpe_duplicate_ids}")

# ------------------------------------------------------------
# Inspect Timestamp Integrity
# ------------------------------------------------------------

print()
print("Timestamp Integrity Assessment")
print("-" * 50)

# Convert timestamps temporarily for inspection only.
# The raw CSV files are not modified.
control_time = pd.to_datetime(
    control_df["Created At"],
    errors="coerce",
    utc=True
)

ldpe_time = pd.to_datetime(
    ldpe_df["Created At"],
    errors="coerce",
    utc=True
)

print("Control:")
print(f"  Valid timestamps   : {control_time.notna().sum()}")
print(f"  Invalid timestamps : {control_time.isna().sum()}")
print(f"  Earliest timestamp : {control_time.min()}")
print(f"  Latest timestamp   : {control_time.max()}")
print(f"  Chronological order: {control_time.is_monotonic_increasing}")

print()
print("LDPE:")
print(f"  Valid timestamps   : {ldpe_time.notna().sum()}")
print(f"  Invalid timestamps : {ldpe_time.isna().sum()}")
print(f"  Earliest timestamp : {ldpe_time.min()}")
print(f"  Latest timestamp   : {ldpe_time.max()}")
print(f"  Chronological order: {ldpe_time.is_monotonic_increasing}")

# ------------------------------------------------------------
# Inspect Sampling Intervals
# ------------------------------------------------------------

print()
print("Sampling Interval Assessment")
print("-" * 50)

# Sort temporary timestamp copies for interval calculation.
# Raw CSV files remain unchanged.
control_time_sorted = control_time.sort_values().reset_index(drop=True)
ldpe_time_sorted = ldpe_time.sort_values().reset_index(drop=True)

# Calculate elapsed time between consecutive observations in minutes.
control_intervals = control_time_sorted.diff().dropna().dt.total_seconds() / 60
ldpe_intervals = ldpe_time_sorted.diff().dropna().dt.total_seconds() / 60

print("Control:")
print(f"  Number of intervals : {len(control_intervals)}")
print(f"  Minimum interval    : {control_intervals.min():.2f} minutes")
print(f"  Median interval     : {control_intervals.median():.2f} minutes")
print(f"  Mean interval       : {control_intervals.mean():.2f} minutes")
print(f"  Maximum interval    : {control_intervals.max():.2f} minutes")

print()
print("LDPE:")
print(f"  Number of intervals : {len(ldpe_intervals)}")
print(f"  Minimum interval    : {ldpe_intervals.min():.2f} minutes")
print(f"  Median interval     : {ldpe_intervals.median():.2f} minutes")
print(f"  Mean interval       : {ldpe_intervals.mean():.2f} minutes")
print(f"  Maximum interval    : {ldpe_intervals.max():.2f} minutes")

# ------------------------------------------------------------
# Inspect Recording Dates
# ------------------------------------------------------------

print()
print("Recording Date Assessment")
print("-" * 50)

control_dates = control_time.dt.date.value_counts().sort_index()
ldpe_dates = ldpe_time.dt.date.value_counts().sort_index()

print("Control:")
for date, count in control_dates.items():
    print(f"  {date} : {count} observations")

print()
print("LDPE:")
for date, count in ldpe_dates.items():
    print(f"  {date} : {count} observations")

# ------------------------------------------------------------
# Inspect Daily Recording Windows
# ------------------------------------------------------------

print()
print("Daily Recording Window Assessment")
print("-" * 50)

def print_daily_windows(label, timestamps):
    timestamp_table = pd.DataFrame({"timestamp": timestamps})
    timestamp_table["date"] = timestamp_table["timestamp"].dt.date

    daily_windows = (
        timestamp_table
        .groupby("date")["timestamp"]
        .agg(["count", "min", "max"])
    )

    print(f"{label}:")
    for date, row in daily_windows.iterrows():
        duration_minutes = (
            row["max"] - row["min"]
        ).total_seconds() / 60

        print(
            f"  {date} | "
            f"n={int(row['count'])} | "
            f"start={row['min'].strftime('%H:%M:%S')} UTC | "
            f"end={row['max'].strftime('%H:%M:%S')} UTC | "
            f"span={duration_minutes:.2f} min"
        )


print_daily_windows("Control", control_time)

print()

print_daily_windows("LDPE", ldpe_time)

# ------------------------------------------------------------
# Inspect Recording Sessions
# ------------------------------------------------------------

print()
print("Recording Session Assessment")
print("-" * 50)

SESSION_GAP_MINUTES = 10


def identify_sessions(label, timestamps):
    session_table = pd.DataFrame({
        "timestamp": timestamps
    }).sort_values("timestamp").reset_index(drop=True)

    # Time elapsed since the previous observation
    session_table["gap_minutes"] = (
        session_table["timestamp"]
        .diff()
        .dt.total_seconds()
        .div(60)
    )

    # A new session begins at the first observation
    # or after a gap greater than the chosen inspection threshold.
    session_table["new_session"] = (
        session_table["gap_minutes"].isna()
        | (session_table["gap_minutes"] > SESSION_GAP_MINUTES)
    )

    session_table["session_id"] = (
        session_table["new_session"].cumsum()
    )

    sessions = (
        session_table
        .groupby("session_id")
        .agg(
            start=("timestamp", "min"),
            end=("timestamp", "max"),
            observations=("timestamp", "size")
        )
        .reset_index()
    )

    sessions["duration_minutes"] = (
        (sessions["end"] - sessions["start"])
        .dt.total_seconds()
        .div(60)
    )

    print(f"{label}:")
    print(f"  Sessions detected : {len(sessions)}")
    print()

    for _, row in sessions.iterrows():
        print(
            f"  Session {int(row['session_id']):>2} | "
            f"{row['start'].strftime('%Y-%m-%d %H:%M:%S')} -> "
            f"{row['end'].strftime('%Y-%m-%d %H:%M:%S')} UTC | "
            f"n={int(row['observations'])} | "
            f"duration={row['duration_minutes']:.2f} min"
        )


identify_sessions("Control", control_time)

print()

identify_sessions("LDPE", ldpe_time)

# ------------------------------------------------------------
# Inspect End-to-End Test Records
# ------------------------------------------------------------

print()
print("End-to-End Test Record Assessment")
print("-" * 50)

control_e2e = control_df[
    control_df["Device ID"].str.contains(
        "e2e", case=False, na=False
    )
]

ldpe_e2e = ldpe_df[
    ldpe_df["Device ID"].str.contains(
        "e2e", case=False, na=False
    )
]

print("Control E2E records:")
if control_e2e.empty:
    print("  None found")
else:
    print(control_e2e.to_string(index=False))

print()

print("LDPE E2E records:")
if ldpe_e2e.empty:
    print("  None found")
else:
    print(ldpe_e2e.to_string(index=False))

# ------------------------------------------------------------
# Inspect mycosense-pi-01 Records
# ------------------------------------------------------------

print()
print("mycosense-pi-01 Record Assessment")
print("-" * 50)

SENSOR_COLUMNS = [
    "Temperature (C)",
    "Humidity (%)",
    "Soil Moisture (%)",
    "pH",
    "Electrical Activity (mV)"
]


def inspect_pi01_records(label, dataframe):

    pi_records = dataframe[
        dataframe["Device ID"] == "mycosense-pi-01"
    ].copy()

    print(f"{label}:")
    print(f"  Number of records : {len(pi_records)}")

    if pi_records.empty:
        print("  No mycosense-pi-01 records found")
        return

    pi_records["timestamp"] = pd.to_datetime(
        pi_records["Created At"],
        errors="coerce",
        utc=True
    )

    print(
        f"  Earliest record   : "
        f"{pi_records['timestamp'].min()}"
    )

    print(
        f"  Latest record     : "
        f"{pi_records['timestamp'].max()}"
    )

    print()
    print("  Records by date:")

    date_counts = (
        pi_records["timestamp"]
        .dt.date
        .value_counts()
        .sort_index()
    )

    for date, count in date_counts.items():
        print(f"    {date} : {count}")

    print()
    print("  Sensor summary:")

    summary = (
        pi_records[SENSOR_COLUMNS]
        .agg(["count", "min", "median", "max"])
        .T
    )

    print(summary.to_string())


inspect_pi01_records("Control", control_df)

print()

inspect_pi01_records("LDPE", ldpe_df)

# ------------------------------------------------------------
# Inspect Overall Sensor Value Ranges
# ------------------------------------------------------------

print()
print("Overall Sensor Range Assessment")
print("-" * 50)

SENSOR_COLUMNS = [
    "Temperature (C)",
    "Humidity (%)",
    "Soil Moisture (%)",
    "pH",
    "Electrical Activity (mV)"
]


def print_sensor_ranges(label, dataframe):

    print(f"{label}:")

    for column in SENSOR_COLUMNS:

        values = dataframe[column].dropna()

        print()
        print(f"  {column}")
        print(f"    Valid count : {len(values)}")
        print(f"    Minimum     : {values.min():.4f}")
        print(f"    25th pct    : {values.quantile(0.25):.4f}")
        print(f"    Median      : {values.median():.4f}")
        print(f"    75th pct    : {values.quantile(0.75):.4f}")
        print(f"    Maximum     : {values.max():.4f}")


print_sensor_ranges("Control", control_df)

print()

print_sensor_ranges("LDPE", ldpe_df)

# ------------------------------------------------------------
# Inspect Sensor Ranges by Recording Date
# ------------------------------------------------------------

print()
print("Sensor Range by Recording Date")
print("-" * 50)


def sensor_ranges_by_date(label, dataframe):

    dated_data = dataframe.copy()

    dated_data["timestamp"] = pd.to_datetime(
        dated_data["Created At"],
        errors="coerce",
        utc=True
    )

    dated_data["date"] = dated_data["timestamp"].dt.date

    print(f"{label}:")

    for date, group in dated_data.groupby("date"):

        print()
        print(f"  Date: {date}")
        print(f"  Total records: {len(group)}")

        for column in SENSOR_COLUMNS:

            values = group[column].dropna()

            if values.empty:
                print(
                    f"    {column:<27} "
                    f"n=0 | no valid readings"
                )
                continue

            print(
                f"    {column:<27} "
                f"n={len(values):<3} | "
                f"min={values.min():>9.3f} | "
                f"median={values.median():>9.3f} | "
                f"max={values.max():>9.3f}"
            )


sensor_ranges_by_date("Control", control_df)

print()

sensor_ranges_by_date("LDPE", ldpe_df)

# ------------------------------------------------------------
# Inspect LDPE 25 August Fault Pattern Over Time
# ------------------------------------------------------------

print()
print("LDPE 25 August Fault Pattern Assessment")
print("-" * 50)

ldpe_25 = ldpe_df.copy()

ldpe_25["timestamp"] = pd.to_datetime(
    ldpe_25["Created At"],
    errors="coerce",
    utc=True
)

ldpe_25 = ldpe_25[
    ldpe_25["timestamp"].dt.date ==
    pd.Timestamp("2026-08-25").date()
].copy()

ldpe_25 = ldpe_25.sort_values("timestamp").reset_index(drop=True)

# Divide the chronological session into 8 blocks.
ldpe_25["block"] = pd.qcut(
    ldpe_25.index,
    q=8,
    labels=False
) + 1

print(f"Total records : {len(ldpe_25)}")
print(
    f"Session start : "
    f"{ldpe_25['timestamp'].min()}"
)
print(
    f"Session end   : "
    f"{ldpe_25['timestamp'].max()}"
)

print()
print("Chronological block summary:")
print()

for block_number, group in ldpe_25.groupby("block"):

    start_time = group["timestamp"].min().strftime("%H:%M:%S")
    end_time = group["timestamp"].max().strftime("%H:%M:%S")

    soil = group["Soil Moisture (%)"].dropna()
    electrical = group["Electrical Activity (mV)"].dropna()

    print(
        f"Block {block_number} | "
        f"{start_time} -> {end_time} UTC | "
        f"n={len(group)}"
    )

    print(
        f"  Soil moisture       : "
        f"min={soil.min():8.3f} | "
        f"median={soil.median():8.3f} | "
        f"max={soil.max():8.3f}"
    )

    print(
        f"  Electrical activity : "
        f"min={electrical.min():8.3f} | "
        f"median={electrical.median():8.3f} | "
        f"max={electrical.max():8.3f}"
    )

    print()

# ------------------------------------------------------------
# Pinpoint LDPE 25 August Transition
# ------------------------------------------------------------

print()
print("LDPE 25 August Exact Transition Assessment")
print("-" * 50)

transition_columns = [
    "ID",
    "timestamp",
    "Soil Moisture (%)",
    "Electrical Activity (mV)"
]

first_records = ldpe_25[
    transition_columns
].head(15).copy()

first_records["Time UTC"] = (
    first_records["timestamp"]
    .dt.strftime("%H:%M:%S.%f")
    .str[:-3]
)

first_records = first_records[
    [
        "ID",
        "Time UTC",
        "Soil Moisture (%)",
        "Electrical Activity (mV)"
    ]
]

print(first_records.to_string(index=False))

# ------------------------------------------------------------
# Detect LDPE 25 August Measurement-State Changes
# ------------------------------------------------------------

print()
print("LDPE 25 August Measurement-State Change Assessment")
print("-" * 50)

state_data = ldpe_25.copy()

# Diagnostic soil-moisture state
def classify_soil(value):

    if pd.isna(value):
        return "MISSING"

    if value >= 99:
        return "HIGH/SATURATED"

    if value <= 1:
        return "VERY LOW"

    return "MID-RANGE"


# Diagnostic electrical state
def classify_electrical(value):

    if pd.isna(value):
        return "MISSING"

    if abs(value) >= 1000:
        return "EXTREME"

    return "NON-EXTREME"


state_data["Soil State"] = (
    state_data["Soil Moisture (%)"]
    .apply(classify_soil)
)

state_data["Electrical State"] = (
    state_data["Electrical Activity (mV)"]
    .apply(classify_electrical)
)

# Combine both sensor states
state_data["Combined State"] = (
    state_data["Soil State"]
    + " | "
    + state_data["Electrical State"]
)

# A transition occurs whenever the combined state differs
# from the preceding record.
state_data["State Change"] = (
    state_data["Combined State"]
    .ne(state_data["Combined State"].shift())
)

transitions = state_data[
    state_data["State Change"]
].copy()

transitions["Time UTC"] = (
    transitions["timestamp"]
    .dt.strftime("%H:%M:%S.%f")
    .str[:-3]
)

print(f"Total session records : {len(state_data)}")
print(f"State transitions     : {len(transitions)}")

print()
print("Combined-state frequency:")
print()

print(
    state_data["Combined State"]
    .value_counts()
    .to_string()
)

print()
print("Chronological state transitions:")
print()

print(
    transitions[
        [
            "ID",
            "Time UTC",
            "Soil Moisture (%)",
            "Electrical Activity (mV)",
            "Soil State",
            "Electrical State"
        ]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# Assess Electrical Activity by Recording Session
# ------------------------------------------------------------

print()
print("Electrical Activity by Recording Session")
print("-" * 50)


def electrical_by_session(label, dataframe):

    working = dataframe.copy()

    working["timestamp"] = pd.to_datetime(
        working["Created At"],
        errors="coerce",
        utc=True
    )

    working = (
        working
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    # Calculate gap between consecutive records.
    working["gap_minutes"] = (
        working["timestamp"]
        .diff()
        .dt.total_seconds()
        .div(60)
    )

    # Same provisional session rule used earlier:
    # a new session starts after a gap greater than 10 minutes.
    working["session"] = (
        working["gap_minutes"]
        .gt(10)
        .cumsum()
        .add(1)
    )

    print(f"{label}:")

    for session_number, group in working.groupby("session"):

        electrical = (
            group["Electrical Activity (mV)"]
            .dropna()
        )

        start = group["timestamp"].min()
        end = group["timestamp"].max()

        print()
        print(
            f"  Session {session_number} | "
            f"{start.strftime('%Y-%m-%d %H:%M:%S')} -> "
            f"{end.strftime('%H:%M:%S')} UTC"
        )

        print(
            f"    Total rows       : {len(group)}"
        )

        print(
            f"    Electrical valid : {len(electrical)}"
        )

        if electrical.empty:
            print("    No valid electrical readings")
            continue

        q1 = electrical.quantile(0.25)
        median = electrical.median()
        q3 = electrical.quantile(0.75)

        count_50 = (electrical.abs() >= 50).sum()
        count_100 = (electrical.abs() >= 100).sum()
        count_1000 = (electrical.abs() >= 1000).sum()

        print(
            f"    Minimum          : {electrical.min():.3f} mV"
        )

        print(
            f"    Q1               : {q1:.3f} mV"
        )

        print(
            f"    Median           : {median:.3f} mV"
        )

        print(
            f"    Q3               : {q3:.3f} mV"
        )

        print(
            f"    Maximum          : {electrical.max():.3f} mV"
        )

        print(
            f"    |value| >= 50    : {count_50}"
        )

        print(
            f"    |value| >= 100   : {count_100}"
        )

        print(
            f"    |value| >= 1000  : {count_1000}"
        )


electrical_by_session(
    "Control",
    control_df
)

print()

electrical_by_session(
    "LDPE",
    ldpe_df
)

# ------------------------------------------------------------
# Examine LDPE 21 August Electrical Pattern Over Time
# ------------------------------------------------------------

print()
print("LDPE 21 August Temporal Electrical Assessment")
print("-" * 50)

ldpe_21 = ldpe_df.copy()

ldpe_21["timestamp"] = pd.to_datetime(
    ldpe_21["Created At"],
    errors="coerce",
    utc=True
)

ldpe_21 = ldpe_21[
    ldpe_21["timestamp"].dt.date ==
    pd.Timestamp("2026-08-21").date()
].copy()

ldpe_21 = (
    ldpe_21
    .sort_values("timestamp")
    .reset_index(drop=True)
)

# 147 records divide exactly into
# 7 chronological blocks of 21 records.
ldpe_21["block"] = (
    ldpe_21.index // 21
) + 1

print(f"Total records : {len(ldpe_21)}")

print(
    f"Session start : "
    f"{ldpe_21['timestamp'].min()}"
)

print(
    f"Session end   : "
    f"{ldpe_21['timestamp'].max()}"
)

print()
print("Chronological block summary:")
print()

for block_number, group in ldpe_21.groupby("block"):

    electrical = (
        group["Electrical Activity (mV)"]
        .dropna()
    )

    soil = (
        group["Soil Moisture (%)"]
        .dropna()
    )

    temperature = (
        group["Temperature (C)"]
        .dropna()
    )

    humidity = (
        group["Humidity (%)"]
        .dropna()
    )

    start_time = (
        group["timestamp"]
        .min()
        .strftime("%H:%M:%S")
    )

    end_time = (
        group["timestamp"]
        .max()
        .strftime("%H:%M:%S")
    )

    count_50 = (
        electrical.abs() >= 50
    ).sum()

    count_100 = (
        electrical.abs() >= 100
    ).sum()

    print(
        f"Block {block_number} | "
        f"{start_time} -> {end_time} UTC | "
        f"n={len(group)}"
    )

    print(
        f"  Electrical : "
        f"min={electrical.min():8.3f} | "
        f"Q1={electrical.quantile(0.25):8.3f} | "
        f"median={electrical.median():8.3f} | "
        f"Q3={electrical.quantile(0.75):8.3f} | "
        f"max={electrical.max():8.3f}"
    )

    print(
        f"  Electrical counts : "
        f"|value| >= 50 = {count_50:2d} | "
        f"|value| >= 100 = {count_100:2d}"
    )

    if not soil.empty:
        print(
            f"  Soil moisture : "
            f"min={soil.min():6.2f} | "
            f"median={soil.median():6.2f} | "
            f"max={soil.max():6.2f}"
        )
    else:
        print("  Soil moisture : no valid readings")

    if not temperature.empty:
        print(
            f"  Temperature   : "
            f"min={temperature.min():6.2f} | "
            f"median={temperature.median():6.2f} | "
            f"max={temperature.max():6.2f}"
        )
    else:
        print("  Temperature   : no valid readings")

    if not humidity.empty:
        print(
            f"  Humidity      : "
            f"min={humidity.min():6.2f} | "
            f"median={humidity.median():6.2f} | "
            f"max={humidity.max():6.2f}"
        )
    else:
        print("  Humidity      : no valid readings")

    print()

# ------------------------------------------------------------
# Inspect Control 21 August Maximum Electrical Event
# ------------------------------------------------------------

print()
print("Control 21 August Maximum Electrical Event Assessment")
print("-" * 50)

control_21 = control_df.copy()

control_21["timestamp"] = pd.to_datetime(
    control_21["Created At"],
    errors="coerce",
    utc=True
)

control_21 = control_21[
    control_21["timestamp"].dt.date ==
    pd.Timestamp("2026-08-21").date()
].copy()

control_21 = (
    control_21
    .sort_values("timestamp")
    .reset_index(drop=True)
)

# Find the row containing the largest electrical reading.
max_position = (
    control_21["Electrical Activity (mV)"]
    .idxmax()
)

max_row = control_21.loc[max_position]

print(
    f"Maximum electrical reading : "
    f"{max_row['Electrical Activity (mV)']:.3f} mV"
)

print(
    f"Record ID                  : "
    f"{int(max_row['ID'])}"
)

print(
    f"Timestamp                  : "
    f"{max_row['timestamp']}"
)

# Select five records before and five records after the event.
window_start = max(0, max_position - 5)

window_end = min(
    len(control_21),
    max_position + 6
)

event_window = control_21.iloc[
    window_start:window_end
].copy()

event_window["Time UTC"] = (
    event_window["timestamp"]
    .dt.strftime("%H:%M:%S.%f")
    .str[:-3]
)

event_window["Event"] = ""

event_window.loc[
    event_window.index == max_position,
    "Event"
] = "<-- MAX"

print()
print("Readings surrounding maximum:")
print()

print(
    event_window[
        [
            "ID",
            "Time UTC",
            "Electrical Activity (mV)",
            "Soil Moisture (%)",
            "Temperature (C)",
            "Humidity (%)",
            "Event"
        ]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# Assess Control 21 August Soil-Moisture Zero Period
# ------------------------------------------------------------

print()
print("Control 21 August Soil-Moisture State Assessment")
print("-" * 50)

control_soil_21 = control_df.copy()

control_soil_21["timestamp"] = pd.to_datetime(
    control_soil_21["Created At"],
    errors="coerce",
    utc=True
)

control_soil_21 = control_soil_21[
    control_soil_21["timestamp"].dt.date ==
    pd.Timestamp("2026-08-21").date()
].copy()

control_soil_21 = (
    control_soil_21
    .sort_values("timestamp")
    .reset_index(drop=True)
)


def classify_soil(value):

    if pd.isna(value):
        return "MISSING"

    if value == 0:
        return "ZERO"

    if value < 50:
        return "LOW"

    if value < 90:
        return "MID"

    return "HIGH"


control_soil_21["Soil State"] = (
    control_soil_21["Soil Moisture (%)"]
    .apply(classify_soil)
)

# Detect whenever the soil state changes.
control_soil_21["State Changed"] = (
    control_soil_21["Soil State"]
    .ne(
        control_soil_21["Soil State"]
        .shift()
    )
)

state_changes = control_soil_21[
    control_soil_21["State Changed"]
].copy()

state_changes["Time UTC"] = (
    state_changes["timestamp"]
    .dt.strftime("%H:%M:%S.%f")
    .str[:-3]
)

print(
    f"Total records       : "
    f"{len(control_soil_21)}"
)

print(
    f"Valid soil readings : "
    f"{control_soil_21['Soil Moisture (%)'].notna().sum()}"
)

print()

print("Soil-state frequency:")
print()

print(
    control_soil_21["Soil State"]
    .value_counts()
    .to_string()
)

print()
print("Chronological soil-state transitions:")
print()

print(
    state_changes[
        [
            "ID",
            "Time UTC",
            "Soil Moisture (%)",
            "Electrical Activity (mV)",
            "Temperature (C)",
            "Humidity (%)",
            "Soil State"
        ]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# Examine every zero-soil run
# ------------------------------------------------------------

zero_mask = (
    control_soil_21["Soil State"] == "ZERO"
)

control_soil_21["Zero Run"] = (
    zero_mask.ne(zero_mask.shift())
    .cumsum()
)

zero_runs = control_soil_21[
    zero_mask
].copy()

print()
print("Zero-soil runs:")
print()

if zero_runs.empty:

    print("No zero-soil readings found.")

else:

    run_number = 0

    for _, group in zero_runs.groupby("Zero Run"):

        run_number += 1

        start = group["timestamp"].min()
        end = group["timestamp"].max()

        duration_seconds = (
            end - start
        ).total_seconds()

        electrical = (
            group["Electrical Activity (mV)"]
            .dropna()
        )

        print(
            f"  Zero run {run_number}"
        )

        print(
            f"    Start        : {start}"
        )

        print(
            f"    End          : {end}"
        )

        print(
            f"    Records      : {len(group)}"
        )

        print(
            f"    Duration     : "
            f"{duration_seconds / 60:.2f} minutes"
        )

        if not electrical.empty:

            print(
                f"    Electrical   : "
                f"min={electrical.min():.3f} | "
                f"median={electrical.median():.3f} | "
                f"max={electrical.max():.3f} mV"
            )

        print()

# ------------------------------------------------------------
# Assess pH Measurement Regimes
# ------------------------------------------------------------

print()
print("pH Measurement-Regime Assessment")
print("-" * 50)


def assess_ph_regimes(df, condition_name):

    ph_df = df.copy()

    ph_df["timestamp"] = pd.to_datetime(
        ph_df["Created At"],
        errors="coerce",
        utc=True
    )

    ph_df["recording_date"] = (
        ph_df["timestamp"].dt.date
    )

    print()
    print(f"{condition_name}:")
    print()

    grouped = ph_df.groupby(
        ["recording_date", "Device ID"],
        sort=True
    )

    for (recording_date, device_id), group in grouped:

        ph = group["pH"]
        valid_ph = ph.dropna()

        total_records = len(group)
        valid_count = valid_ph.count()
        missing_count = ph.isna().sum()
        unique_count = valid_ph.nunique()

        print(
            f"Date   : {recording_date}"
        )

        print(
            f"Device : {device_id}"
        )

        print(
            f"  Total records : {total_records}"
        )

        print(
            f"  Valid pH      : {valid_count}"
        )

        print(
            f"  Missing pH    : {missing_count}"
        )

        if valid_count == 0:

            print(
                "  pH summary    : "
                "no valid readings"
            )

        else:

            most_common_value = (
                valid_ph
                .value_counts()
                .index[0]
            )

            most_common_count = (
                valid_ph
                .value_counts()
                .iloc[0]
            )

            most_common_pct = (
                most_common_count /
                valid_count *
                100
            )

            print(
                f"  Unique values : "
                f"{unique_count}"
            )

            print(
                f"  Minimum       : "
                f"{valid_ph.min():.3f}"
            )

            print(
                f"  Q1            : "
                f"{valid_ph.quantile(0.25):.3f}"
            )

            print(
                f"  Median        : "
                f"{valid_ph.median():.3f}"
            )

            print(
                f"  Q3            : "
                f"{valid_ph.quantile(0.75):.3f}"
            )

            print(
                f"  Maximum       : "
                f"{valid_ph.max():.3f}"
            )

            print(
                f"  Most frequent : "
                f"{most_common_value:.3f} "
                f"({most_common_count}/{valid_count}, "
                f"{most_common_pct:.1f}%)"
            )

            # When only a small number of distinct values
            # exist, display all of them and their frequencies.
            if unique_count <= 10:

                print(
                    "  Value frequencies:"
                )

                frequencies = (
                    valid_ph
                    .value_counts()
                    .sort_index()
                )

                for value, count in frequencies.items():

                    print(
                        f"    {value:.3f} : "
                        f"{count}"
                    )

        print()


assess_ph_regimes(
    control_df,
    "Control"
)

assess_ph_regimes(
    ldpe_df,
    "LDPE"
)

# ------------------------------------------------------------
# Control 21 August pH State-Transition Assessment
# ------------------------------------------------------------

print()
print("Control 21 August pH State-Transition Assessment")
print("-" * 50)

control_21_ph = control_df.copy()

control_21_ph["timestamp"] = pd.to_datetime(
    control_21_ph["Created At"],
    errors="coerce",
    utc=True
)

control_21_ph = control_21_ph[
    control_21_ph["timestamp"].dt.date ==
    pd.Timestamp("2026-08-21").date()
].copy()

control_21_ph = (
    control_21_ph
    .sort_values("timestamp")
    .reset_index(drop=True)
)

# Classify the recorded pH states.
def classify_ph(value):

    if pd.isna(value):
        return "MISSING"

    if value == 1.0:
        return "PH_1.0"

    if value == 5.5:
        return "PH_5.5"

    return "OTHER"


control_21_ph["pH State"] = (
    control_21_ph["pH"]
    .apply(classify_ph)
)

# Identify each point where the recorded pH state changes.
control_21_ph["Previous pH State"] = (
    control_21_ph["pH State"]
    .shift(1)
)

ph_transitions = control_21_ph[
    (
        control_21_ph["pH State"] !=
        control_21_ph["Previous pH State"]
    )
].copy()

print(
    f"Total records       : "
    f"{len(control_21_ph)}"
)

print(
    f"Valid pH readings   : "
    f"{control_21_ph['pH'].notna().sum()}"
)

print()

print("pH-state frequency:")
print()

print(
    control_21_ph["pH State"]
    .value_counts()
    .to_string()
)

print()
print("Chronological pH-state transitions:")
print()

transition_display = (
    ph_transitions[
        [
            "ID",
            "timestamp",
            "pH",
            "Soil Moisture (%)",
            "Electrical Activity (mV)",
            "Temperature (C)",
            "Humidity (%)",
            "pH State"
        ]
    ]
    .copy()
)

transition_display["Time UTC"] = (
    transition_display["timestamp"]
    .dt.strftime("%H:%M:%S.%f")
    .str[:-3]
)

transition_display = transition_display[
    [
        "ID",
        "Time UTC",
        "pH",
        "Soil Moisture (%)",
        "Electrical Activity (mV)",
        "Temperature (C)",
        "Humidity (%)",
        "pH State"
    ]
]

print(
    transition_display.to_string(
        index=False
    )
)

# Display records surrounding the first appearance
# of pH 5.5.
ph_55_positions = control_21_ph.index[
    control_21_ph["pH"] == 5.5
].tolist()

if ph_55_positions:

    first_ph55_position = ph_55_positions[0]

    start_position = max(
        0,
        first_ph55_position - 5
    )

    end_position = min(
        len(control_21_ph),
        first_ph55_position + 6
    )

    neighbourhood = (
        control_21_ph
        .iloc[start_position:end_position]
        .copy()
    )

    neighbourhood["Time UTC"] = (
        neighbourhood["timestamp"]
        .dt.strftime("%H:%M:%S.%f")
        .str[:-3]
    )

    neighbourhood["Event"] = ""

    neighbourhood.loc[
        neighbourhood.index ==
        first_ph55_position,
        "Event"
    ] = "<-- FIRST pH 5.5"

    print()
    print("Records surrounding first pH 5.5:")
    print()

    print(
        neighbourhood[
            [
                "ID",
                "Time UTC",
                "pH",
                "Soil Moisture (%)",
                "Electrical Activity (mV)",
                "Temperature (C)",
                "Humidity (%)",
                "Event"
            ]
        ].to_string(
            index=False
        )
    )


# ------------------------------------------------------------
# Temperature-Humidity Missingness Relationship Assessment
# ------------------------------------------------------------

print()
print("Temperature-Humidity Missingness Relationship Assessment")
print("-" * 50)

def assess_temp_humidity_missingness(df, label):

    working = df.copy()

    working["timestamp"] = pd.to_datetime(
        working["Created At"],
        errors="coerce",
        utc=True
    )

    working = (
        working
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    temp_missing = working["Temperature (C)"].isna()
    humidity_missing = working["Humidity (%)"].isna()

    both_present = (
        (~temp_missing) &
        (~humidity_missing)
    )

    both_missing = (
        temp_missing &
        humidity_missing
    )

    temp_only_missing = (
        temp_missing &
        (~humidity_missing)
    )

    humidity_only_missing = (
        (~temp_missing) &
        humidity_missing
    )

    print()
    print(f"{label}:")
    print()

    print(
        f"Total records              : "
        f"{len(working)}"
    )

    print(
        f"Both temperature/humidity present : "
        f"{both_present.sum()}"
    )

    print(
        f"Both temperature/humidity missing : "
        f"{both_missing.sum()}"
    )

    print(
        f"Temperature missing only           : "
        f"{temp_only_missing.sum()}"
    )

    print(
        f"Humidity missing only              : "
        f"{humidity_only_missing.sum()}"
    )

    agreement = (
        (
            both_present.sum() +
            both_missing.sum()
        )
        / len(working)
        * 100
    )

    print(
        f"Missingness-state agreement        : "
        f"{agreement:.2f}%"
    )

    print()
    print("Missingness by recording date:")
    print()

    working["Date"] = (
        working["timestamp"]
        .dt.date
    )

    for date_value, group in working.groupby("Date"):

        group_temp_missing = (
            group["Temperature (C)"]
            .isna()
        )

        group_humidity_missing = (
            group["Humidity (%)"]
            .isna()
        )

        group_both_missing = (
            group_temp_missing &
            group_humidity_missing
        )

        group_both_present = (
            (~group_temp_missing) &
            (~group_humidity_missing)
        )

        group_temp_only = (
            group_temp_missing &
            (~group_humidity_missing)
        )

        group_humidity_only = (
            (~group_temp_missing) &
            group_humidity_missing
        )

        print(
            f"  {date_value} | "
            f"total={len(group):3d} | "
            f"both present={group_both_present.sum():3d} | "
            f"both missing={group_both_missing.sum():3d} | "
            f"temp only missing={group_temp_only.sum():3d} | "
            f"humidity only missing={group_humidity_only.sum():3d}"
        )


assess_temp_humidity_missingness(
    control_df,
    "Control"
)

assess_temp_humidity_missingness(
    ldpe_df,
    "LDPE"
)


# ------------------------------------------------------------
# Provisional Record-Level Data-Quality Classification
# ------------------------------------------------------------

print()
print("Provisional Record-Level Data-Quality Classification")
print("-" * 50)


def classify_data_quality(df, condition):

    assessed = df.copy()

    assessed["timestamp"] = pd.to_datetime(
        assessed["Created At"],
        errors="coerce",
        utc=True
    )

    # Default classification:
    # A record is retained unless objective evidence identified
    # during the inspection indicates otherwise.
    assessed["Quality Status"] = "RETAIN"
    assessed["Quality Reason"] = "No currently identified record-level exclusion criterion"

    # --------------------------------------------------------
    # 1. Known end-to-end software test records
    # --------------------------------------------------------
    e2e_mask = assessed["Device ID"].astype(str).str.startswith(
        "e2e-",
        na=False
    )

    assessed.loc[e2e_mask, "Quality Status"] = "EXCLUDE_TEST"
    assessed.loc[e2e_mask, "Quality Reason"] = (
        "Known end-to-end software/system test record; "
        "not a biological experimental observation"
    )

    # --------------------------------------------------------
    # 2. LDPE 25 August extreme multi-sensor measurement regime
    #
    # Diagnostic evidence already established:
    # soil moisture <= 1% together with
    # |electrical activity| >= 1000 mV.
    #
    # This identifies the objectively observed extreme regime.
    # It is NOT a general biological outlier rule.
    # --------------------------------------------------------
    if condition == "LDPE":

        ldpe_fault_mask = (
            assessed["timestamp"].dt.date.eq(
                pd.Timestamp("2026-08-25").date()
            )
            & assessed["Soil Moisture (%)"].le(1)
            & assessed["Electrical Activity (mV)"].abs().ge(1000)
            & ~e2e_mask
        )

        assessed.loc[ldpe_fault_mask, "Quality Status"] = "FAULT_CANDIDATE"
        assessed.loc[ldpe_fault_mask, "Quality Reason"] = (
            "25 August LDPE extreme measurement regime: "
            "soil moisture <= 1% and |electrical activity| >= 1000 mV"
        )

    # --------------------------------------------------------
    # 3. Control 21 August zero-soil measurement regime
    #
    # Retained but explicitly flagged.
    # We do not yet have enough evidence to delete these rows.
    # --------------------------------------------------------
    if condition == "Control":

        control_zero_soil_mask = (
            assessed["timestamp"].dt.date.eq(
                pd.Timestamp("2026-08-21").date()
            )
            & assessed["Soil Moisture (%)"].eq(0)
            & ~e2e_mask
        )

        assessed.loc[
            control_zero_soil_mask,
            "Quality Status"
        ] = "RETAIN_FLAGGED"

        assessed.loc[
            control_zero_soil_mask,
            "Quality Reason"
        ] = (
            "Control 21 August sustained zero-soil regime; "
            "retained pending variable-specific sensitivity analysis"
        )

        # Explicitly note the isolated electrical maximum.
        event_mask = (
            assessed["ID"].eq(1153)
            & ~e2e_mask
        )

        assessed.loc[
            event_mask,
            "Quality Status"
        ] = "RETAIN_FLAGGED"

        assessed.loc[
            event_mask,
            "Quality Reason"
        ] = (
            "Control 21 August isolated +101.531 mV electrical excursion "
            "within sustained zero-soil regime; retained and flagged"
        )

    return assessed


control_quality = classify_data_quality(
    control_df,
    "Control"
)

ldpe_quality = classify_data_quality(
    ldpe_df,
    "LDPE"
)


def print_quality_summary(df, label):

    print()
    print(f"{label}:")
    print()

    counts = df["Quality Status"].value_counts()

    for status, count in counts.items():
        percentage = (count / len(df)) * 100

        print(
            f"  {status:18s}: "
            f"{count:4d} "
            f"({percentage:6.2f}%)"
        )

    print()
    print("Reasons:")

    reason_counts = (
        df.groupby(
            ["Quality Status", "Quality Reason"]
        )
        .size()
        .reset_index(name="Count")
    )

    for _, row in reason_counts.iterrows():

        print()
        print(
            f"  {row['Quality Status']} "
            f"| n={int(row['Count'])}"
        )
        print(
            f"    {row['Quality Reason']}"
        )


print_quality_summary(
    control_quality,
    "Control"
)

print_quality_summary(
    ldpe_quality,
    "LDPE"
)


print()
print("Important flagged records")
print("-" * 50)

important_control = control_quality[
    control_quality["Quality Status"].ne("RETAIN")
][
    [
        "ID",
        "timestamp",
        "Soil Moisture (%)",
        "Electrical Activity (mV)",
        "Quality Status"
    ]
]

important_ldpe = ldpe_quality[
    ldpe_quality["Quality Status"].ne("RETAIN")
][
    [
        "ID",
        "timestamp",
        "Soil Moisture (%)",
        "Electrical Activity (mV)",
        "Quality Status"
    ]
]

print()
print("Control non-standard records:")
print(f"  Number of records : {len(important_control)}")

print()
print("LDPE non-standard records:")
print(f"  Number of records : {len(important_ldpe)}")

print()
print("LDPE fault-candidate time range:")

ldpe_faults = ldpe_quality[
    ldpe_quality["Quality Status"].eq("FAULT_CANDIDATE")
]

if ldpe_faults.empty:
    print("  No fault-candidate records identified.")
else:
    print(
        f"  First : {ldpe_faults['timestamp'].min()}"
    )
    print(
        f"  Last  : {ldpe_faults['timestamp'].max()}"
    )
    print(
        f"  Count : {len(ldpe_faults)}"
    )

# ------------------------------------------------------------
# Variable-Level Validity Framework
# ------------------------------------------------------------

print()
print("Variable-Level Validity Framework")
print("-" * 50)


def create_variable_validity_flags(df, label):

    assessed = df.copy()

    assessed["timestamp"] = pd.to_datetime(
        assessed["Created At"],
        errors="coerce",
        utc=True
    )

    # --------------------------------------------------------
    # 1. Temperature
    # Valid when an actual reading is present.
    # No imputation is performed.
    # --------------------------------------------------------
    assessed["Temperature Valid"] = assessed[
        "Temperature (C)"
    ].notna()

    # --------------------------------------------------------
    # 2. Humidity
    # Valid when an actual reading is present.
    # No imputation is performed.
    # --------------------------------------------------------
    assessed["Humidity Valid"] = assessed[
        "Humidity (%)"
    ].notna()

    # --------------------------------------------------------
    # 3. Soil moisture
    # Begin by accepting non-missing measurements.
    # Known/questionable measurement regimes are then flagged.
    # --------------------------------------------------------
    assessed["Soil Valid"] = assessed[
        "Soil Moisture (%)"
    ].notna()

    if label == "Control":

        control_zero_soil = (
            (assessed["timestamp"].dt.date ==
             pd.Timestamp("2026-08-21").date())
            &
            (assessed["Soil Moisture (%)"] == 0)
        )

        assessed.loc[
            control_zero_soil,
            "Soil Valid"
        ] = False

    if label == "LDPE":

        ldpe_fault_soil = (
            (assessed["timestamp"].dt.date ==
             pd.Timestamp("2026-08-25").date())
            &
            (assessed["Soil Moisture (%)"] <= 1)
            &
            (assessed["Electrical Activity (mV)"].abs() >= 1000)
        )

        assessed.loc[
            ldpe_fault_soil,
            "Soil Valid"
        ] = False

    # --------------------------------------------------------
    # 4. pH
    # Only variable sensor measurements from mycosense-pi-01
    # are currently accepted for quantitative pH analysis.
    #
    # Fixed/reference-like pH values remain preserved in the
    # dataset but are not treated as continuous measured pH.
    # --------------------------------------------------------
    assessed["pH Valid"] = (
        assessed["pH"].notna()
        &
        (assessed["Device ID"] == "mycosense-pi-01")
    )

    # --------------------------------------------------------
    # 5. Electrical activity
    # Begin by accepting non-missing electrical measurements.
    # Exclude only the strongly evidenced LDPE fault regime.
    # --------------------------------------------------------
    assessed["Electrical Valid"] = assessed[
        "Electrical Activity (mV)"
    ].notna()

    if label == "LDPE":

        ldpe_fault_electrical = (
            (assessed["timestamp"].dt.date ==
             pd.Timestamp("2026-08-25").date())
            &
            (assessed["Soil Moisture (%)"] <= 1)
            &
            (assessed["Electrical Activity (mV)"].abs() >= 1000)
        )

        assessed.loc[
            ldpe_fault_electrical,
            "Electrical Valid"
        ] = False

    # --------------------------------------------------------
    # Known E2E software test records are not biological
    # observations and therefore cannot contribute to any
    # biological sensor analysis.
    # --------------------------------------------------------
    e2e_mask = assessed["Device ID"].str.startswith(
        "e2e-",
        na=False
    )

    validity_columns = [
        "Temperature Valid",
        "Humidity Valid",
        "Soil Valid",
        "pH Valid",
        "Electrical Valid"
    ]

    assessed.loc[
        e2e_mask,
        validity_columns
    ] = False

    # --------------------------------------------------------
    # Report validity counts
    # --------------------------------------------------------
    print()
    print(f"{label}:")
    print()

    print(f"Total records : {len(assessed)}")
    print()

    for column in validity_columns:

        valid_count = int(assessed[column].sum())
        invalid_count = len(assessed) - valid_count

        valid_pct = (
            valid_count / len(assessed) * 100
            if len(assessed) > 0
            else 0
        )

        print(
            f"  {column:<20} : "
            f"{valid_count:>4} valid "
            f"({valid_pct:>6.2f}%) | "
            f"{invalid_count:>4} not valid"
        )

    return assessed


control_validity = create_variable_validity_flags(
    control_df,
    "Control"
)

ldpe_validity = create_variable_validity_flags(
    ldpe_df,
    "LDPE"
)


# ------------------------------------------------------------
# Cross-check specific evidence-based exclusions
# ------------------------------------------------------------

print()
print("Variable-Level Validity Cross-Checks")
print("-" * 50)

control_zero_invalid = control_validity[
    (control_validity["timestamp"].dt.date ==
     pd.Timestamp("2026-08-21").date())
    &
    (control_validity["Soil Moisture (%)"] == 0)
    &
    (~control_validity["Soil Valid"])
]

print()
print(
    "Control 21 August zero-soil readings marked "
    f"not valid : {len(control_zero_invalid)}"
)

ldpe_fault_invalid = ldpe_validity[
    (ldpe_validity["timestamp"].dt.date ==
     pd.Timestamp("2026-08-25").date())
    &
    (~ldpe_validity["Electrical Valid"])
    &
    (ldpe_validity["Electrical Activity (mV)"].notna())
]

print(
    "LDPE 25 August electrical readings marked "
    f"not valid : {len(ldpe_fault_invalid)}"
)

control_ph_valid = control_validity[
    control_validity["pH Valid"]
]

ldpe_ph_valid = ldpe_validity[
    ldpe_validity["pH Valid"]
]

print(
    "Control quantitative pH readings retained "
    f": {len(control_ph_valid)}"
)

print(
    "LDPE quantitative pH readings retained "
    f": {len(ldpe_ph_valid)}"
)

print()
print("Control retained quantitative pH range:")

if len(control_ph_valid) > 0:
    print(
        f"  {control_ph_valid['pH'].min():.3f} "
        f"to {control_ph_valid['pH'].max():.3f}"
    )

print()
print("LDPE retained quantitative pH range:")

if len(ldpe_ph_valid) > 0:
    print(
        f"  {ldpe_ph_valid['pH'].min():.3f} "
        f"to {ldpe_ph_valid['pH'].max():.3f}"
    )
