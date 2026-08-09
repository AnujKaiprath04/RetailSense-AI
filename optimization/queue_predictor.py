import math
from typing import Dict, Any

class QueueAnalyticsPredictor:
    """
    Queue Analytics & Multi-Server Queuing Theory Engine (M/M/c Model)
    
    Predicts:
    - Expected Queue Length
    - Average Customer Wait Time (seconds)
    - Billing Counter Utilization (%)
    - Recommended Number of Open Counters to maintain Wait Time < 3 minutes (180 seconds).
    """

    def __init__(self, avg_service_time_seconds: float = 120.0):
        # Default average checkout service time per customer = 2 minutes (120 seconds)
        self.avg_service_time_seconds = avg_service_time_seconds
        self.service_rate_mu = 3600.0 / avg_service_time_seconds  # customers per hour per counter

    def calculate_queue_metrics(
        self,
        arrival_rate_lambda: float,  # Customers arriving per hour
        active_counters: int,
        max_acceptable_wait_sec: float = 180.0
    ) -> Dict[str, Any]:
        c = max(1, active_counters)
        mu = self.service_rate_mu
        traffic_intensity_rho = arrival_rate_lambda / (c * mu)

        if traffic_intensity_rho >= 1.0:
            # Over-saturated queue system
            avg_queue_len = int((arrival_rate_lambda - c * mu) * 0.75 + c * 3)
            avg_wait_sec = round((avg_queue_len * self.avg_service_time_seconds / c) + 120.0, 1)
            utilization = 99.9
        else:
            # Erlang-C Queue Formula approximation
            rho = traffic_intensity_rho
            avg_queue_len = round((rho ** 2) / (1 - rho) * (1 / c), 2)
            avg_wait_sec = round((avg_queue_len / arrival_rate_lambda) * 3600, 1) if arrival_rate_lambda > 0 else 0.0
            utilization = round(rho * 100, 1)

        # Calculate recommended open counters
        recommended_counters = c
        while True:
            r_rho = arrival_rate_lambda / (recommended_counters * mu)
            if r_rho < 0.85:
                r_q = (r_rho ** 2) / (1 - r_rho) * (1 / recommended_counters)
                r_wait = (r_q / arrival_rate_lambda) * 3600 if arrival_rate_lambda > 0 else 0.0
                if r_wait <= max_acceptable_wait_sec or recommended_counters >= 12:
                    break
            recommended_counters += 1

        action_required = recommended_counters > c
        
        return {
            "predicted_queue_length": int(round(avg_queue_len)),
            "predicted_avg_wait_time_sec": avg_wait_sec,
            "predicted_avg_wait_time_min": round(avg_wait_sec / 60.0, 1),
            "counter_utilization_pct": utilization,
            "currently_active_counters": c,
            "recommended_open_counters": recommended_counters,
            "action_required": action_required,
            "recommendation_message": f"Open {recommended_counters - c} additional counter(s) immediately." if action_required else "Current counter allocation is optimal."
        }
