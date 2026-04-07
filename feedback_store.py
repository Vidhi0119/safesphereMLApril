import os
import csv
from datetime import datetime, timezone
from typing import Optional, Dict, Any


FEEDBACK_PATH = os.getenv("SAFESPHERE_FEEDBACK_CSV", "feedback_events.csv")


FIELDNAMES = [
    "created_at",
    "latitude",
    "longitude",
    "crime_type",
    "feedback_risk",  # 0=safe, 1=unsafe (user perception)
    "notes",
]


def append_feedback(
    latitude: float,
    longitude: float,
    crime_type: Optional[str],
    feedback_risk: float,
    notes: Optional[str],
) -> None:
    exists = os.path.exists(FEEDBACK_PATH)
    os.makedirs(os.path.dirname(FEEDBACK_PATH) or ".", exist_ok=True)

    row: Dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "latitude": latitude,
        "longitude": longitude,
        "crime_type": crime_type or "",
        "feedback_risk": float(feedback_risk),
        "notes": (notes or "")[:500],
    }

    with open(FEEDBACK_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not exists:
            w.writeheader()
        w.writerow(row)

