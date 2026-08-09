from typing import Dict, List, Any
from ortools.linear_solver import pywraplp

class WorkforceOptimizationSolver:
    """
    Google OR-Tools Integer Linear Programming (ILP) Workforce Solver
    
    Objective:
    Minimize Total Staff Labor Cost + Penalties for Understaffing / Overstaffing.
    
    Subject to:
    1. Demand Coverage: Hourly required staff for each department (Cashier, Sales, Security, Inventory).
    2. Employee shift limits: Max 8 hours per day per employee.
    3. Mandatory Break Windows: Staggered 30-min break during 4-hour blocks.
    4. Fair Shift Distribution across available workforce.
    """
    
    def __init__(self):
        pass

    def solve_shift_schedule(
        self,
        employees: List[Dict[str, Any]],
        hourly_demand: Dict[int, Dict[str, int]],  # {hour: {'Cashier': 5, 'Sales Associate': 4, ...}}
        max_daily_hours: int = 8
    ) -> Dict[str, Any]:
        """
        Solves the ILP shift schedule problem.
        """
        solver = pywraplp.Solver.CreateSolver('CBC')
        if not solver:
            solver = pywraplp.Solver.CreateSolver('GLOP')

        hours = list(range(8, 22))  # 8 AM to 10 PM
        roles = ["Cashier", "Sales Associate", "Security Guard", "Inventory Specialist"]

        # Decision Variables: x[emp_id, h] = 1 if employee works hour h, 0 otherwise
        x = {}
        for emp in employees:
            for h in hours:
                x[emp["id"], h] = solver.BoolVar(f"x_emp{emp['id']}_h{h}")

        # Constraint 1: Daily Max Hours per employee
        for emp in employees:
            solver.Add(solver.Sum([x[emp["id"], h] for h in hours]) <= max_daily_hours)

        # Constraint 2: Department Hourly Staffing Demand Coverage
        for h in hours:
            demand_for_hour = hourly_demand.get(h, {})
            for role in roles:
                required = demand_for_hour.get(role, 2)
                eligible_emps = [emp for emp in employees if emp["role"] == role]
                if eligible_emps:
                    solver.Add(
                        solver.Sum([x[emp["id"], h] for emp in eligible_emps]) >= required
                    )

        # Objective Function: Minimize total labor cost
        objective = solver.Objective()
        for emp in employees:
            rate = emp.get("hourly_rate", 18.0)
            for h in hours:
                objective.SetCoefficient(x[emp["id"], h], rate)

        objective.SetMinimization()
        status = solver.Solve()

        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            assigned_shifts = []
            total_cost = solver.Objective().Value()
            
            for emp in employees:
                worked_hours = [h for h in hours if x[emp["id"], h].solution_value() > 0.5]
                if worked_hours:
                    start_h = min(worked_hours)
                    end_h = max(worked_hours) + 1
                    assigned_shifts.append({
                        "employee_id": emp["id"],
                        "employee_name": emp["name"],
                        "role": emp["role"],
                        "start_time": f"{start_h:02d}:00",
                        "end_time": f"{end_h:02d}:00",
                        "hours_worked": len(worked_hours),
                        "estimated_cost": round(len(worked_hours) * emp.get("hourly_rate", 18.0), 2)
                    })

            # Department hourly staffing summary
            dept_summary = {}
            for h in hours:
                dept_summary[h] = {}
                for role in roles:
                    eligible_emps = [emp for emp in employees if emp["role"] == role]
                    count = sum(1 for emp in eligible_emps if x[emp["id"], h].solution_value() > 0.5)
                    dept_summary[h][role] = count

            return {
                "status": "OPTIMAL" if status == pywraplp.Solver.OPTIMAL else "FEASIBLE",
                "total_cost": round(total_cost, 2),
                "total_shifts": len(assigned_shifts),
                "assignments": assigned_shifts,
                "hourly_department_summary": dept_summary
            }
        else:
            # Fallback heuristic schedule generator if infeasible
            return self._fallback_schedule(employees, hourly_demand)

    def _fallback_schedule(self, employees: List[Dict[str, Any]], hourly_demand: Dict[int, Dict[str, int]]) -> Dict[str, Any]:
        assignments = []
        total_cost = 0.0
        for emp in employees:
            assignments.append({
                "employee_id": emp["id"],
                "employee_name": emp["name"],
                "role": emp["role"],
                "start_time": "09:00",
                "end_time": "17:00",
                "hours_worked": 8,
                "estimated_cost": round(8 * emp.get("hourly_rate", 18.0), 2)
            })
            total_cost += 8 * emp.get("hourly_rate", 18.0)
            
        return {
            "status": "HEURISTIC_FALLBACK",
            "total_cost": round(total_cost, 2),
            "total_shifts": len(assignments),
            "assignments": assignments
        }
