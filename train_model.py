import os
import json
from datetime import datetime

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import HistGradientBoostingRegressor


DATASET_PATH = "mumbai_safety_dataset.csv"
FEEDBACK_PATH = os.getenv("SAFESPHERE_FEEDBACK_CSV", "feedback_events.csv")
MODEL_DIR = "artifacts"
MODEL_PATH = os.path.join(MODEL_DIR, "safety_model.joblib")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")


CRIME_SEVERITY = {
    "Others": 1,
    "Suspicious Activity": 2,
    "Vandalism": 3,
    "Theft": 4,
    "Harassment": 5,
    "Assault": 6,
}


def rule_based_safety_score(row: pd.Series) -> float:
    crime_severity = CRIME_SEVERITY.get(row.get("crime_type", "Others"), 3)
    crime_safety = (7 - crime_severity) / 6 * 3
    cctv_safety = float(row.get("cctv_presence", 0)) * 2

    max_police_dist = 5.0
    police_prox = float(row.get("police_station_prox", max_police_dist))
    if police_prox > max_police_dist:
        police_safety = 0.0
    else:
        police_safety = (1 - (police_prox / max_police_dist)) * 3

    risk_score = float(row.get("risk_score", 0.5))
    risk_safety = (1 - risk_score) * 2

    total = crime_safety + cctv_safety + police_safety + risk_safety
    return float(max(1.0, min(10.0, total)))


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # Parse incident_time; if missing, use a neutral timestamp
    t = pd.to_datetime(out.get("incident_time", pd.NaT), errors="coerce", utc=False)
    # Fill missing with median to avoid dropping many rows
    if t.isna().any():
        t = t.fillna(t.dropna().median() if (~t.isna()).any() else pd.Timestamp("2023-07-01T12:00:00"))

    out["hour"] = t.dt.hour.astype(int)
    out["day_of_week"] = t.dt.dayofweek.astype(int)  # 0=Mon
    out["month"] = t.dt.month.astype(int)

    # Cyclical encoding for hour and day_of_week
    out["hour_sin"] = np.sin(2 * np.pi * out["hour"] / 24.0)
    out["hour_cos"] = np.cos(2 * np.pi * out["hour"] / 24.0)
    out["dow_sin"] = np.sin(2 * np.pi * out["day_of_week"] / 7.0)
    out["dow_cos"] = np.cos(2 * np.pi * out["day_of_week"] / 7.0)
    return out


def build_training_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    # Create training target from your existing scoring logic (acts as a baseline "label")
    df["target_safety_score"] = df.apply(rule_based_safety_score, axis=1)

    df = add_time_features(df)

    feature_cols = [
        "latitude",
        "longitude",
        "crime_type",
        "cctv_presence",
        "police_station_prox",
        "risk_score",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
        "month",
    ]

    X = df[feature_cols].copy()
    y = df["target_safety_score"].astype(float)
    return X, y


def load_feedback_as_training_rows() -> pd.DataFrame:
    """
    Convert user feedback into additional training rows.

    This is the "continuous training" bridge:
    - feedback_risk (0..1) becomes a safety label (1..10) via: safety = 10 - 9*risk
    - we fill missing feature columns with conservative defaults
    """
    if not os.path.exists(FEEDBACK_PATH):
        return pd.DataFrame()

    fb = pd.read_csv(FEEDBACK_PATH)
    if fb.empty:
        return pd.DataFrame()

    # Normalize and clamp
    fb["feedback_risk"] = pd.to_numeric(fb.get("feedback_risk", 0), errors="coerce").fillna(0.0).clip(0.0, 1.0)
    fb["target_safety_score"] = (10.0 - 9.0 * fb["feedback_risk"]).clip(1.0, 10.0)

    fb["crime_type"] = fb.get("crime_type", "").fillna("").astype(str)
    fb.loc[fb["crime_type"].str.strip() == "", "crime_type"] = "Others"

    # Provide conservative defaults for missing infra features
    fb["cctv_presence"] = 0
    fb["police_station_prox"] = 5.0
    fb["risk_score"] = fb["feedback_risk"]

    # Use feedback timestamp as incident_time
    created = pd.to_datetime(fb.get("created_at", pd.NaT), errors="coerce")
    if created.isna().any():
        created = created.fillna(pd.Timestamp.utcnow())
    fb["incident_time"] = created.astype(str)

    keep = [
        "latitude",
        "longitude",
        "crime_type",
        "cctv_presence",
        "police_station_prox",
        "risk_score",
        "incident_time",
        "target_safety_score",
    ]
    for c in keep:
        if c not in fb.columns:
            fb[c] = np.nan

    fb = fb[keep].copy()
    fb = fb.dropna(subset=["latitude", "longitude"])
    return fb


def train() -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)

    base_df = pd.read_csv(DATASET_PATH)
    base_df["target_safety_score"] = base_df.apply(rule_based_safety_score, axis=1)

    fb_df = load_feedback_as_training_rows()
    if not fb_df.empty:
        df = pd.concat([base_df, fb_df], ignore_index=True)
        target_note = f"baseline rule-based + feedback (n_feedback={len(fb_df)})"
    else:
        df = base_df
        target_note = "rule_based_safety_score (baseline label)"

    df = add_time_features(df)

    feature_cols = [
        "latitude",
        "longitude",
        "crime_type",
        "cctv_presence",
        "police_station_prox",
        "risk_score",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
        "month",
    ]

    X = df[feature_cols].copy()
    y = df["target_safety_score"].astype(float)

    numeric_features = [
        "latitude",
        "longitude",
        "cctv_presence",
        "police_station_prox",
        "risk_score",
        "hour_sin",
        "hour_cos",
        "dow_sin",
        "dow_cos",
        "month",
    ]
    categorical_features = ["crime_type"]

    pre = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = HistGradientBoostingRegressor(
        learning_rate=0.08,
        max_depth=6,
        max_iter=300,
        random_state=42,
    )

    pipe = Pipeline([("pre", pre), ("model", model)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)

    metrics = {
        "mae": float(mean_absolute_error(y_test, preds)),
        "rmse": float(mean_squared_error(y_test, preds, squared=False)),
        "r2": float(r2_score(y_test, preds)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "target": target_note,
        "n_feedback_rows": int(len(fb_df)) if "fb_df" in locals() else 0,
    }

    dump(pipe, MODEL_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Model trained and saved:")
    print(f"- {MODEL_PATH}")
    print(f"- {META_PATH}")
    print("Metrics:", metrics)


if __name__ == "__main__":
    train()

