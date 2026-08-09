from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models import Recommendation

router = APIRouter(prefix="/recommendations", tags=["AI Prescriptive Recommendations"])

@router.get("/")
def get_recommendations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    store_id = current_user.store_id or 1
    
    # Generate enterprise recommendations
    recommendations_data = [
        {
            "id": 101,
            "category": "Cashier Optimization",
            "priority": "CRITICAL",
            "title": "Open Billing Counters 5 & 6 Immediately",
            "description": "Footfall model projects arrival spike of 340 customers/hr at 5:00 PM. Opening 2 extra counters prevents queue length from exceeding 4 shoppers.",
            "expected_revenue_gain_inr": 42500.0,
            "queue_reduction_pct": "38%",
            "estimated_savings_inr": 18500.0,
            "confidence_pct": "96.4%",
            "affected_departments": "Checkout & Billing",
            "status": "PENDING"
        },
        {
            "id": 102,
            "category": "Break Optimization",
            "priority": "HIGH",
            "title": "Stagger Cashier Evening Shift Breaks",
            "description": "Reschedule 6:00 PM breaks to 4:15 PM to ensure 100% counter capacity during peak rush hour.",
            "expected_revenue_gain_inr": 24000.0,
            "queue_reduction_pct": "22%",
            "estimated_savings_inr": 9200.0,
            "confidence_pct": "94.1%",
            "affected_departments": "Store Roster",
            "status": "PENDING"
        },
        {
            "id": 103,
            "category": "Floor Staffing",
            "priority": "MEDIUM",
            "title": "Reallocate 2 Associates from Grocery to Apparel",
            "description": "Apparel aisle footfall is 45% above average while Grocery traffic is steady. Reallocating staff maximizes customer assistance.",
            "expected_revenue_gain_inr": 15800.0,
            "queue_reduction_pct": "12%",
            "estimated_savings_inr": 6500.0,
            "confidence_pct": "91.8%",
            "affected_departments": "Grocery & Apparel",
            "status": "PENDING"
        }
    ]

    return {
        "store_id": store_id,
        "total_active": len(recommendations_data),
        "recommendations": recommendations_data
    }
