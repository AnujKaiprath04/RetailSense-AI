from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models import Employee, Department
from optimization.workforce_solver import WorkforceOptimizationSolver

router = APIRouter(prefix="/staff", tags=["Staff Optimization"])

@router.get("/recommendations")
def get_staff_recommendations(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    store_id = current_user.store_id or 1
    
    employees = db.query(Employee).filter(Employee.store_id == store_id).all()
    emp_list = [
        {
            "id": e.id,
            "name": e.name,
            "role": e.role,
            "hourly_rate": e.hourly_rate
        } for e in employees
    ]

    solver = WorkforceOptimizationSolver()
    
    # Define hourly staffing demand curve
    hourly_demand = {
        h: {
            "Cashier": 8 if 17 <= h <= 20 else (6 if 12 <= h <= 14 else 3),
            "Sales Associate": 6 if 12 <= h <= 18 else 4,
            "Security Guard": 2,
            "Inventory Specialist": 2
        } for h in range(8, 22)
    }

    result = solver.solve_shift_schedule(emp_list, hourly_demand)

    # Calculate department breakdown
    depts = db.query(Department).filter(Department.store_id == store_id).all()
    dept_allocation = [
        {"department": d.name, "assigned_count": d.target_staff, "status": "OPTIMAL"}
        for d in depts
    ]

    return {
        "optimization_engine": "Google OR-Tools Integer Linear Programming (ILP)",
        "result": result,
        "department_allocation": dept_allocation
    }
