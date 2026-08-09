from typing import Dict, Any

class RetailDigitalTwinSimulator:
    """
    Scenario Simulator / Digital Twin Engine
    
    Allows retail managers to simulate hypothetical operational changes:
    - Weather changes (rain_mm, temperature)
    - Promotional discounts %
    - Holiday status
    - Staff / Cashier counts
    
    Outputs impact on Footfall, Revenue, Queue Length, Wait Time, and Net Profit.
    """

    def __init__(self, avg_spend_per_customer: float = 450.00, gross_margin_pct: float = 0.35):
        self.avg_spend_per_customer = avg_spend_per_customer
        self.gross_margin_pct = gross_margin_pct

    def simulate_scenario(
        self,
        base_footfall: int,
        base_staff_count: int,
        promotion_discount_pct: float = 0.0,
        rain_mm: float = 0.0,
        is_holiday: bool = False,
        modified_staff_count: int = None,
        modified_cashier_count: int = None
    ) -> Dict[str, Any]:
        
        staff = modified_staff_count if modified_staff_count is not None else base_staff_count
        cashiers = modified_cashier_count if modified_cashier_count is not None else max(2, int(staff * 0.35))

        # 1. Footfall Multiplier Factors
        promo_factor = 1.0 + (promotion_discount_pct * 0.015)  # +15% per 10% discount
        weather_factor = 1.0 - min(0.35, (rain_mm * 0.025))      # heavy rain reduces footfall
        holiday_factor = 1.35 if is_holiday else 1.0

        simulated_footfall = int(base_footfall * promo_factor * weather_factor * holiday_factor)
        simulated_footfall = max(10, simulated_footfall)

        # 2. Conversion & Revenue Calculation
        # Longer queues degrade conversion rate slightly
        capacity_per_cashier = 30  # customers per hour
        total_cashier_capacity = cashiers * capacity_per_cashier
        
        backlog_customers = max(0, simulated_footfall - total_cashier_capacity)
        abandonment_pct = min(0.20, (backlog_customers / simulated_footfall) * 0.15) if simulated_footfall > 0 else 0.0
        
        effective_buyers = int(simulated_footfall * (1.0 - abandonment_pct))
        simulated_revenue = round(effective_buyers * self.avg_spend_per_customer, 2)

        # Baseline Revenue Comparison
        base_buyers = int(base_footfall * 0.95)
        base_revenue = round(base_buyers * self.avg_spend_per_customer, 2)
        revenue_delta = round(simulated_revenue - base_revenue, 2)
        revenue_delta_pct = round((revenue_delta / base_revenue) * 100, 2) if base_revenue > 0 else 0.0

        # 3. Queue Dynamics
        queue_length = max(1, int(backlog_customers / max(1, cashiers)))
        avg_wait_sec = round((queue_length * 120.0) / max(1, cashiers), 1)

        # 4. Financial Impact
        labor_cost = staff * 250.00 * 8  # 8-hour shift cost in INR
        gross_profit = round(simulated_revenue * self.gross_margin_pct, 2)
        net_profit = round(gross_profit - labor_cost, 2)

        return {
            "baseline": {
                "footfall": base_footfall,
                "revenue": base_revenue,
                "staff_count": base_staff_count
            },
            "simulated": {
                "footfall": simulated_footfall,
                "revenue": simulated_revenue,
                "revenue_delta": revenue_delta,
                "revenue_delta_pct": revenue_delta_pct,
                "effective_buyers": effective_buyers,
                "abandoned_customers": simulated_footfall - effective_buyers,
                "predicted_queue_length": queue_length,
                "predicted_avg_wait_sec": avg_wait_sec,
                "estimated_labor_cost": labor_cost,
                "gross_profit": gross_profit,
                "net_profit": net_profit
            },
            "impact_summary": (
                f"Scenario projects footfall of {simulated_footfall} ({'+' if revenue_delta >= 0 else ''}{revenue_delta_pct}% revenue change). "
                f"Queue length estimated at {queue_length} customers with {avg_wait_sec}s average wait."
            )
        }
