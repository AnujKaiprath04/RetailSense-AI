# RetailSense AI - Plain-English Guide & Project Summary

This guide explains **RetailSense AI** in simple, clear, and understandable terms. Whether you are presenting this project to professors, project evaluators, or team members, this document will help you explain every component effortlessly.

---

## 💡 What is RetailSense AI? (30-Second Summary)

**RetailSense AI** is an AI Operations Manager for retail stores (like Amazon Fresh, Walmart, or Target). 

Instead of just predicting footfall numbers, it helps store managers solve 4 core problems:
1. **Customer Traffic**: How many shoppers will visit the store in the next hour or day?
2. **Staff Allocation**: How many cashiers and floor employees are needed right now?
3. **Queue Bottlenecks**: How long will checkout queues become, and when should we open extra billing counters?
4. **Actionable Recommendations**: What exact steps should store management take to increase revenue and satisfy customers?

---

## 🧭 Simple Tour of the 6 Project Modules

| Module Name | What It Does | Technology Used |
| :--- | :--- | :--- |
| **1. Executive Dashboard** | Displays live footfall, projected hourly visitors, estimated daily revenue, active staff count, and high-priority operational alerts. | FastAPI, Bootstrap 5, Chart.js |
| **2. Footfall Predictor** | Predicts footfall across 4 time horizons (Next Hour, Next Day, Weekend, Festival Surge). Compares 4 ML algorithms (**XGBoost**, **LightGBM**, **PyTorch LSTM**, **Prophet**). | Scikit-learn, XGBoost, PyTorch |
| **3. Staff Optimizer** | Automatically schedules employee shifts (Cashiers, Sales, Security) to satisfy customer demand while minimizing labor wage costs. | Google OR-Tools (Integer Linear Programming) |
| **4. CCTV Computer Vision** | Tracks customer counts entering/exiting via camera feeds and generates visual thermal heatmaps of crowded zones. | OpenCV, Contour Tracking, Thermal Map Accumulator |
| **5. Scenario Simulator** | Allows managers to test "What-if?" scenarios using sliders (e.g. *What if rain falls? What if we offer 20% discount?*). | Digital Twin Engine |
| **6. AI Retail Assistant** | A ChatGPT-like AI assistant that answers manager questions in plain English (*"Why is tomorrow crowded?"*, *"How many cashiers should I assign?"*). | GenAI Decision Support (RAG Engine) |

---

## 📂 Understanding the Folder Structure

```
RetailSense AI/
├── backend/            --> The brain of the platform (Python + FastAPI server)
│   ├── app/api/        --> Web APIs (Endpoints for Auth, Dashboard, ML, Staff, Vision)
│   ├── app/core/       --> Security, JWT authentication, & database settings
│   └── app/db/         --> Database tables (Users, Stores, Footfall, Queues, Shifts)
├── frontend/           --> The user interface (HTML5 + Glassmorphic CSS + Vanilla JS)
│   ├── index.html      --> Single Page Application dashboard shell
│   └── static/         --> Stylesheet (style.css) and JavaScript logic (app.js)
├── ml/                 --> Machine Learning & Explainable AI (SHAP & LIME)
│   ├── footfall_models.py --> XGBoost, LightGBM, LSTM, Prophet algorithms
│   └── explainable_ai.py --> SHAP feature importance breakdown
├── optimization/       --> Operations Research
│   ├── workforce_solver.py --> Google OR-Tools integer programming shift scheduler
│   └── queue_predictor.py  --> M/M/c queuing theory & wait time calculator
├── vision/             --> Computer Vision
│   └── cv_analytics.py --> OpenCV CCTV stream simulator & thermal heatmap generator
├── docs/               --> Project documentation & research paper
│   ├── research_paper.md --> Formatted IEEE research paper draft
│   └── architecture/   --> Mermaid ERD, DFD, and Sequence diagrams
└── README.md           --> Complete setup instructions
```

---

## ⚡ How to Run the Project (Simple Steps)

### Step 1: Open Terminal & Run Backend Server
```bash
python backend/app/db/seed.py
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Open Web Browser
Navigate to: **`http://localhost:8000`**

### Step 3: Test Credentials
- **Role**: Store Manager
- **Email**: `manager@retailsense.ai`
- **Password**: `Manager123!`

---

## 🎓 How to Present This Project in Your Viva / Defense

When explaining this project to evaluators:

1. **Highlight the Research Novelty**:
   - Explain that most college projects only do basic forecasting. RetailSense AI connects forecasting directly to **prescriptive optimization** (Google OR-Tools) and **Explainable AI** (SHAP/LIME).

2. **Demonstrate the Scenario Simulator**:
   - Move the *Promotional Discount* slider to 30% and click *Run Digital Twin Simulation*. Show how footfall increases and how the system recommends opening additional billing counters.

3. **Demonstrate the AI Operations Assistant**:
   - Ask the chat drawer: *"Why is tomorrow crowded?"* and show how it explains the weather, promotional discount, and weekend surge factors.
