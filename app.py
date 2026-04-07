from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from typing import List, Dict
import uvicorn
import os
import subprocess
import sys
from joblib import load
from feedback_store import append_feedback

app = FastAPI(title="SafeSphere ML API", description="Safety Score Prediction API")

# Add CORS middleware to allow frontend requests
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load dataset
df = pd.read_csv('mumbai_safety_dataset.csv')

# Optional trained model (spatio-temporal baseline)
MODEL_PATH = os.path.join("artifacts", "safety_model.joblib")
_MODEL = None
if os.path.exists(MODEL_PATH):
    try:
        _MODEL = load(MODEL_PATH)
        print(f"Loaded trained model: {MODEL_PATH}")
    except Exception as e:
        print(f"Failed to load model {MODEL_PATH}: {e}")

# Crime type severity mapping (lower is safer, higher is more dangerous)
CRIME_SEVERITY = {
    'Others': 1,
    'Suspicious Activity': 2,
    'Vandalism': 3,
    'Theft': 4,
    'Harassment': 5,
    'Assault': 6
}

class LocationInput(BaseModel):
    latitude: float
    longitude: float

class LocationResult(BaseModel):
    name: str
    safety_score: float

class SafetyResponse(BaseModel):
    locations: List[LocationResult]
    average_safety_score: float
    average_safety_percentage: float

class FeedbackInput(BaseModel):
    latitude: float
    longitude: float
    crime_type: str | None = None
    feedback_risk: float  # 0 (safe) .. 1 (unsafe)
    notes: str | None = None

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def calculate_safety_score(row: pd.Series) -> float:
    """
    Calculate safety score (1-10) based on:
    - crime_type (severity)
    - cctv_presence (1 = safer, 0 = less safe)
    - police_station_prox (closer = safer, normalized)
    - risk_score (lower = safer)
    """
    # Crime type component (1-6, normalized to 0-3 scale, inverted for safety)
    crime_severity = CRIME_SEVERITY.get(row['crime_type'], 3)
    crime_safety = (7 - crime_severity) / 6 * 3  # Invert: 6->0, 1->3
    
    # CCTV presence (0 or 1, contributes 0-2 points)
    cctv_safety = row['cctv_presence'] * 2
    
    # Police station proximity (closer = safer, max 5km, contributes 0-3 points)
    # Inverse relationship: closer police = higher safety
    max_police_dist = 5.0  # Assume max distance of 5km
    police_prox = row['police_station_prox']
    if police_prox > max_police_dist:
        police_safety = 0
    else:
        police_safety = (1 - (police_prox / max_police_dist)) * 3
    
    # Risk score (0-1, lower = safer, contributes 0-2 points)
    # Invert risk_score: 0 risk = 2 points, 1 risk = 0 points
    risk_safety = (1 - row['risk_score']) * 2
    
    # Sum all components (max = 3 + 2 + 3 + 2 = 10)
    total_safety = crime_safety + cctv_safety + police_safety + risk_safety
    
    # Ensure score is between 1 and 10
    safety_score = max(1.0, min(10.0, total_safety))
    
    return round(safety_score, 2)


def model_predict_score(row: pd.Series) -> float:
    """
    Predict safety score using trained model if available.
    Falls back to rule-based scoring if model isn't loaded.
    """
    global _MODEL
    if _MODEL is None:
        return calculate_safety_score(row)

    # Build a 1-row frame with features expected by train_model.py
    t = pd.to_datetime(row.get("incident_time", pd.Timestamp("2023-07-01T12:00:00")), errors="coerce")
    if pd.isna(t):
        t = pd.Timestamp("2023-07-01T12:00:00")

    hour = int(getattr(t, "hour", 12))
    dow = int(getattr(t, "dayofweek", 0))
    month = int(getattr(t, "month", 7))

    features = pd.DataFrame([{
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "crime_type": str(row.get("crime_type", "Others")),
        "cctv_presence": float(row.get("cctv_presence", 0)),
        "police_station_prox": float(row.get("police_station_prox", 5.0)),
        "risk_score": float(row.get("risk_score", 0.5)),
        "hour_sin": float(np.sin(2 * np.pi * hour / 24.0)),
        "hour_cos": float(np.cos(2 * np.pi * hour / 24.0)),
        "dow_sin": float(np.sin(2 * np.pi * dow / 7.0)),
        "dow_cos": float(np.cos(2 * np.pi * dow / 7.0)),
        "month": month,
    }])

    pred = float(_MODEL.predict(features)[0])
    return float(max(1.0, min(10.0, pred)))

def find_nearest_locations(lat: float, lon: float, n: int = 10) -> pd.DataFrame:
    """
    Find n nearest locations to the given coordinates
    """
    # Calculate distances
    distances = df.apply(
        lambda row: haversine_distance(lat, lon, row['latitude'], row['longitude']),
        axis=1
    )
    
    # Add distance column
    df_with_dist = df.copy()
    df_with_dist['distance'] = distances
    
    # Sort by distance and get top n
    nearest = df_with_dist.nsmallest(n, 'distance')
    
    return nearest

@app.get("/")
def read_root():
    return {"message": "SafeSphere ML API", "status": "running"}

@app.post("/predict-safety", response_model=SafetyResponse)
def predict_safety(location: LocationInput):
    """
    Predict safety score for a given location based on 10 nearest neighbors
    """
    try:
        # Validate coordinates
        if not (-90 <= location.latitude <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        if not (-180 <= location.longitude <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
        
        # Find 10 nearest locations
        nearest_locations = find_nearest_locations(location.latitude, location.longitude, n=6)
        
        # Calculate safety scores for each location
        results = []
        for idx, row in nearest_locations.iterrows():
            safety_score = model_predict_score(row)
            results.append({
                "name": row['location'],
                "safety_score": safety_score
            })
        
        # Calculate average safety score
        safety_scores = [loc['safety_score'] for loc in results]
        average_safety = sum(safety_scores) / len(safety_scores)
        average_safety_percentage = round(average_safety * 10, 2)  # Convert to percentage (1-10 scale to 10-100%)
        
        return {
            "locations": results,
            "average_safety_score": round(average_safety, 2),
            "average_safety_percentage": average_safety_percentage
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/feedback")
def submit_feedback(feedback: FeedbackInput):
    """
    Store real-world feedback for future retraining.
    feedback_risk: 0 (safe) .. 1 (unsafe)
    """
    try:
        if not (-90 <= feedback.latitude <= 90) or not (-180 <= feedback.longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        if not (0.0 <= feedback.feedback_risk <= 1.0):
            raise HTTPException(status_code=400, detail="feedback_risk must be between 0 and 1")

        append_feedback(
            latitude=feedback.latitude,
            longitude=feedback.longitude,
            crime_type=feedback.crime_type,
            feedback_risk=feedback.feedback_risk,
            notes=feedback.notes,
        )

        return {"status": "success", "message": "Feedback stored"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store feedback: {str(e)}")


@app.post("/retrain")
def retrain_model():
    """
    Trigger retraining locally by running train_model.py.
    For production, schedule retraining as a background job instead.
    """
    try:
        # Run retraining script
        subprocess.check_call([sys.executable, "train_model.py"])
        # Reload model
        global _MODEL
        _MODEL = load(MODEL_PATH)
        return {"status": "success", "message": "Model retrained and reloaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

