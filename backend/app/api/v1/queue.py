from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from optimization.queue_predictor import QueueAnalyticsPredictor

router = APIRouter(prefix="/queue", tags=["Queue Analytics"])

@router.get("/predict")
def predict_queue_metrics(
    arrival_rate: float = Query(280.0, description="Customer arrival rate per hour"),
    active_counters: int = Query(4, description="Currently open checkout counters"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    predictor = QueueAnalyticsPredictor(avg_service_time_seconds=120.0)
    metrics = predictor.calculate_queue_metrics(arrival_rate, active_counters)

    # Detailed counter breakdown
    counters_status = []
    for c_id in range(1, 11):
        is_open = c_id <= active_counters
        counters_status.append({
            "counter_id": f"Counter #{c_id}",
            "status": "OPEN" if is_open else "CLOSED",
            "current_queue": metrics["predicted_queue_length"] if is_open else 0,
            "avg_wait_sec": metrics["predicted_avg_wait_time_sec"] if is_open else 0.0
        })

    return {
        "arrival_rate_per_hour": arrival_rate,
        "metrics": metrics,
        "counter_details": counters_status
    }
