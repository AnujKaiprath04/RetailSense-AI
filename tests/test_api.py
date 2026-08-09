import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_login_manager():
    response = client.post(
        "/api/v1/auth/login-json",
        json={"email": "manager@retailsense.ai", "password": "Manager123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "Manager"

def test_dashboard_summary():
    login_res = client.post(
        "/api/v1/auth/login-json",
        json={"email": "manager@retailsense.ai", "password": "Manager123!"}
    )
    token = login_res.json()["access_token"]
    
    response = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "health_score" in data["kpis"]
    assert "charts" in data

def test_model_comparison_endpoint():
    response = client.get("/api/v1/footfall/model-comparison")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) >= 4

def test_queue_analytics_prediction():
    login_res = client.post(
        "/api/v1/auth/login-json",
        json={"email": "manager@retailsense.ai", "password": "Manager123!"}
    )
    token = login_res.json()["access_token"]
    
    response = client.get(
        "/api/v1/queue/predict?arrival_rate=280&active_counters=4",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "predicted_queue_length" in data["metrics"]

def test_scenario_simulator():
    login_res = client.post(
        "/api/v1/auth/login-json",
        json={"email": "manager@retailsense.ai", "password": "Manager123!"}
    )
    token = login_res.json()["access_token"]
    
    response = client.post(
        "/api/v1/simulator/simulate",
        json={
            "base_footfall": 250,
            "base_staff_count": 22,
            "promotion_discount_pct": 15.0,
            "rain_mm": 0.0,
            "is_holiday": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "simulated" in data
    assert data["simulated"]["footfall"] > 250

def test_recommendations_endpoint():
    login_res = client.post(
        "/api/v1/auth/login-json",
        json={"email": "manager@retailsense.ai", "password": "Manager123!"}
    )
    token = login_res.json()["access_token"]
    
    response = client.get(
        "/api/v1/recommendations/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0

def test_explainability_shap():
    login_res = client.post(
        "/api/v1/auth/login-json",
        json={"email": "manager@retailsense.ai", "password": "Manager123!"}
    )
    token = login_res.json()["access_token"]
    
    response = client.get(
        "/api/v1/explainability/shap",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "shap_summary" in data

def test_vision_telemetry():
    response = client.get("/api/v1/vision/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "live_occupancy" in data["metrics"]
