# 🏪 RetailSense AI — Enterprise Retail Intelligence Platform

<div align="center">

![RetailSense AI](https://img.shields.io/badge/RetailSense-AI-3b82f6?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTV6TTIgMTdsOSA1IDktNXY0bC05IDV6Ii8+PC9zdmc+)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-FF6600?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://chartjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)](LICENSE)

**A production-ready, research-grade retail analytics OS — built for final year engineering projects, retail operations teams, and enterprise deployments.**

[🚀 Live Demo](#quickstart) · [📖 Docs](#documentation) · [🧪 Features](#features) · [📊 Dataset](#dataset)

</div>

---

## 📸 Screenshots

> **Dark Enterprise Dashboard** · Premium UI with frosted glass top bar, multi-model ML chart, and real-time KPI panel.

<p align="center">
  <img src="docs/screenshots/dashboard_dark.png" alt="RetailSense AI Dashboard" width="100%">
</p>

---

## 🌟 Key Features

| Module | Description |
|---|---|
| 📈 **Footfall Forecasting** | XGBoost, LightGBM, Prophet, PyTorch LSTM — next hour / day / week |
| 👥 **Shift Optimizer** | Google OR-Tools ILP for cashiers, staff scheduling, and cost minimization |
| 🎯 **Queue Analytics** | M/M/c queuing model — real-time wait time and counter recommendations |
| 📹 **Vision AI (CCTV)** | OpenCV + YOLO crowd detection, thermal heatmaps, gate-line people counting |
| 🧠 **Explainable AI (XAI)** | SHAP & LIME feature attribution explaining footfall drivers |
| 🤖 **AI Assistant** | RAG-based GenAI retail operations chat assistant |
| 🔬 **Scenario Simulator** | Sensitivity analysis for weather, promos, staff, and holidays |
| 📊 **100K Dataset** | 1 lakh rows across 5 stores, 2+ years of synthetic hourly retail data |
| 📄 **Report Export** | PDF / Excel / CSV executive intelligence reports |

---

## 🏗️ Architecture

```
retailsense-ai/
├── backend/                  # FastAPI REST API + SQLAlchemy ORM
│   ├── app/
│   │   ├── api/v1/           # Route handlers (footfall, staff, queue, vision, XAI...)
│   │   ├── core/             # Config, auth, security
│   │   └── db/               # SQLite/PostgreSQL session & seed data
├── frontend/                 # Static HTML/CSS/JS enterprise UI
│   ├── index.html            # Single-page application shell
│   └── static/
│       ├── css/style.css     # Full custom design system (dark + light)
│       └── js/app.js         # Frontend logic, charts, API polling
├── ml/                       # Machine learning engines
│   ├── footfall_models.py    # XGBoost, LightGBM, LSTM training
│   ├── data_pipeline.py      # Feature engineering pipeline
│   ├── explainable_ai.py     # SHAP + LIME explainability
│   └── generate_100k_dataset.py # 1 lakh row synthetic dataset generator
├── optimization/             # OR-Tools ILP workforce scheduler
├── vision/                   # OpenCV + YOLO people detection
├── services/                 # Queue simulation (M/M/c)
├── tests/                    # Pytest integration tests
└── docker-compose.yml        # Full-stack Docker deployment
```

---

## 🚀 Quickstart

### Option 1: Local Development

**1. Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/retailsense-ai.git
cd retailsense-ai
```

**2. Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

**3. Install dependencies:**
```bash
pip install -r backend/requirements.txt
```

**4. Generate the 1 Lakh (100K) dataset:**
```bash
python ml/generate_100k_dataset.py
```

**5. Start the server:**
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**6. Open in browser:**
```
http://localhost:8000
```

**Default credentials:**
```
Email:    manager@retailsense.ai
Password: Manager123!
```

> API Docs (Swagger): http://localhost:8000/docs

---

### Option 2: Docker Compose

```bash
docker-compose up --build
```
Access at http://localhost

---

## 📊 Dataset

| Property | Value |
|---|---|
| Total Rows | **100,000 records (1 Lakh)** |
| Time Span | **2+ Years of Hourly Data** |
| Store Locations | 5 (Koramangala, Indiranagar, Whitefield, MG Road, Jayanagar) |
| Departments | Grocery, Apparel, Electronics, Beverages, Personal Care |
| Features | Footfall, Revenue, Staff, Cashiers, Wait Time, Weather, Promotions, Holidays |
| File Size | ~9.5 MB CSV |

Run the generator:
```bash
python ml/generate_100k_dataset.py
```

---

## 🧠 ML Models

| Model | MAE | RMSE | R² |
|---|---|---|---|
| **XGBoost** | ~12.3 | ~18.7 | **0.94** |
| LightGBM | ~13.1 | ~19.4 | 0.92 |
| Prophet | ~18.5 | ~25.2 | 0.87 |
| PyTorch LSTM | ~14.2 | ~20.8 | 0.91 |

---

## 🎨 UI Design System

- **Typography:** Plus Jakarta Sans (headings), Inter (body), JetBrains Mono (metrics)
- **Dark Mode:** Deep navy (`#080d19`) canvas, `#0f172a` cards, `#1e293b` borders
- **Light Mode:** `#f8fafc` canvas, white cards, `#e2e8f0` borders
- **Accent:** Deep Blue `#3b82f6`, Emerald `#10b981`, Amber `#f59e0b`, Crimson `#ef4444`
- **Effects:** Frosted glass top bar, smooth hover elevation, sparkline mini-charts, confidence band gradients

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## 📄 Documentation

- [Architecture Diagrams](docs/architecture/diagrams.md)
- [Research Paper Draft](docs/research_paper.md)

---

## 📦 Tech Stack

**Backend:** Python 3.10, FastAPI, SQLAlchemy, SQLite/PostgreSQL, Pydantic  
**Machine Learning:** Scikit-Learn, XGBoost, LightGBM, Prophet, PyTorch  
**Optimization:** Google OR-Tools (CBC Solver)  
**Computer Vision:** OpenCV, YOLO  
**Explainability:** SHAP, LIME  
**Frontend:** HTML5, Bootstrap 5, Vanilla JS, Chart.js  
**Deployment:** Docker, Docker Compose, Nginx, GitHub Actions  

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Made with ❤️ for Final Year Engineering Project<br>
<strong>RetailSense AI — Smarter Stores. Better Decisions.</strong>
</div>
