from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from services.scenario_simulator import RetailDigitalTwinSimulator

router = APIRouter(prefix="/simulator", tags=["Digital Twin Scenario Simulator"])
simulator = RetailDigitalTwinSimulator()

@router.post("/simulate")
def run_scenario_simulation(
    payload: dict = Body(..., example={
        "base_footfall": 250,
        "base_staff_count": 22,
        "promotion_discount_pct": 15.0,
        "rain_mm": 0.0,
        "is_holiday": True,
        "modified_staff_count": 28,
        "modified_cashier_count": 8
    }),
    current_user = Depends(get_current_user)
):
    result = simulator.simulate_scenario(
        base_footfall=payload.get("base_footfall", 250),
        base_staff_count=payload.get("base_staff_count", 22),
        promotion_discount_pct=payload.get("promotion_discount_pct", 0.0),
        rain_mm=payload.get("rain_mm", 0.0),
        is_holiday=payload.get("is_holiday", False),
        modified_staff_count=payload.get("modified_staff_count"),
        modified_cashier_count=payload.get("modified_cashier_count")
    )
    return result
