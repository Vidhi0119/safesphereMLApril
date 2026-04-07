# SafeSphere ML API

A FastAPI-based machine learning service that predicts safety scores for locations in Mumbai based on crime data, CCTV presence, police station proximity, and risk scores.

## Features

- **Location-based Safety Prediction**: Input latitude and longitude to get safety scores for 10 nearest locations
- **Safety Score Calculation**: Uses multiple factors:
  - Crime type severity
  - CCTV presence
  - Police station proximity
  - Risk score
- **JSON API Response**: Returns safety scores and average safety percentage

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Start the FastAPI server:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8001`

## API Endpoints

### Root Endpoint
- **GET** `/`
- Returns API status

### Safety Prediction
- **POST** `/predict-safety`
- **Request Body**:
```json
{
  "latitude": 19.1197,
  "longitude": 72.8464
}
```

- **Response**:
```json
{
  "locations": [
    {
      "name": "Location Name",
      "safety_score": 7.5
    },
    ...
  ],
  "average_safety_score": 7.2,
  "average_safety_percentage": 72.0
}
```

## Testing

Run the test suite:
```bash
python test_api.py
```

Make sure the API server is running before executing tests.

## Safety Score Calculation

The safety score (1-10) is calculated using:
- **Crime Type** (0-3 points): Based on severity (Others < Suspicious Activity < Vandalism < Theft < Harassment < Assault)
- **CCTV Presence** (0-2 points): 1 if CCTV present, 0 otherwise
- **Police Station Proximity** (0-3 points): Closer police stations = higher safety
- **Risk Score** (0-2 points): Lower risk = higher safety

## Dataset

The model uses `mumbai_safety_dataset.csv` which contains:
- Location name
- Latitude and Longitude
- Crime type
- CCTV presence (0/1)
- Police station proximity (km)
- Risk score (0-1)
