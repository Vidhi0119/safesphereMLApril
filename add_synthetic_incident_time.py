import pandas as pd
import numpy as np


CSV_PATH = "mumbai_safety_dataset.csv"
SEED = 42


def sample_hour(crime_type: str, rng: np.random.Generator) -> int:
    """
    Synthetic hour-of-day sampler (0-23) with simple, realistic priors.
    This is NOT real incident data—it's for prototyping spatio-temporal models.
    """
    ct = (crime_type or "").strip().lower()

    # Default: daytime-heavy distribution
    # bins: night(0-5), morning(6-11), afternoon(12-17), evening(18-23)
    base = np.array([0.12, 0.28, 0.32, 0.28])

    if "assault" in ct or "harassment" in ct:
        # More evening/night
        base = np.array([0.22, 0.18, 0.22, 0.38])
    elif "theft" in ct:
        # Even distribution with a slight evening bump
        base = np.array([0.16, 0.26, 0.28, 0.30])
    elif "vandalism" in ct:
        # More late evening
        base = np.array([0.18, 0.22, 0.26, 0.34])
    elif "suspicious" in ct:
        # Slightly more evening
        base = np.array([0.15, 0.25, 0.28, 0.32])

    group = rng.choice(4, p=base / base.sum())
    if group == 0:
        return int(rng.integers(0, 6))
    if group == 1:
        return int(rng.integers(6, 12))
    if group == 2:
        return int(rng.integers(12, 18))
    return int(rng.integers(18, 24))


def main():
    rng = np.random.default_rng(SEED)
    df = pd.read_csv(CSV_PATH)

    if "incident_time" not in df.columns:
        df["incident_time"] = ""

    # Fill only missing/empty values
    missing_mask = df["incident_time"].isna() | (df["incident_time"].astype(str).str.strip() == "")

    # Sample dates within 2023 (adjust later if you want a different range)
    start = np.datetime64("2023-01-01")
    end = np.datetime64("2024-01-01")  # exclusive
    day_span = (end - start).astype("timedelta64[D]").astype(int)

    incident_times = []
    for _, row in df.loc[missing_mask].iterrows():
        day_offset = int(rng.integers(0, day_span))
        hour = sample_hour(row.get("crime_type", ""), rng)
        minute = int(rng.integers(0, 60))
        second = int(rng.integers(0, 60))
        dt = (start + np.timedelta64(day_offset, "D")).astype("datetime64[s]")
        dt = dt + np.timedelta64(hour, "h") + np.timedelta64(minute, "m") + np.timedelta64(second, "s")
        incident_times.append(pd.Timestamp(dt).isoformat())

    df.loc[missing_mask, "incident_time"] = incident_times

    df.to_csv(CSV_PATH, index=False)
    print(f"Updated {missing_mask.sum()} rows with synthetic incident_time in {CSV_PATH}")


if __name__ == "__main__":
    main()

