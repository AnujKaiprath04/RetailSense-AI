# RetailSense AI - Architectural Diagrams & System Design

This document details the architectural blueprints, database entity relationships, software component hierarchies, and behavioral sequence flows for **RetailSense AI**.

---

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    STORE ||--o{ USER : employs
    STORE ||--o{ DEPARTMENT : contains
    STORE ||--o{ EMPLOYEE : employs
    STORE ||--o{ FOOTFALL_DATA : records
    STORE ||--o{ QUEUE_DATA : tracks
    STORE ||--o{ RECOMMENDATION : triggers
    
    DEPARTMENT ||--o{ EMPLOYEE : has
    EMPLOYEE ||--o{ SHIFT : scheduled_for
    USER ||--o{ AI_LOG : queries
    USER ||--o{ AUDIT_LOG : generates

    STORE {
        int id PK
        string name
        string location
        int sqft
    }
    USER {
        int id PK
        string email
        string password_hash
        string role
    }
    EMPLOYEE {
        int id PK
        string name
        string role
        float hourly_rate
    }
    FOOTFALL_DATA {
        int id PK
        datetime timestamp
        int count
        float temperature
        float rain_mm
    }
    QUEUE_DATA {
        int id PK
        int queue_length
        float avg_wait_time_sec
    }
```

---

## 2. System Architecture Component Diagram

```mermaid
graph TD
    Client[Web & Mobile Browsers] -->|HTTPS / REST| Nginx[Nginx Reverse Proxy]
    Nginx -->|FastAPI API Gateway| FastAPI[FastAPI Backend Server]
    
    subgraph Core ML & Optimization Engine
        FastAPI --> XGBoost[XGBoost & LightGBM Predictor]
        FastAPI --> LSTM[PyTorch Sequential LSTM]
        FastAPI --> ORTools[Google OR-Tools ILP Solver]
        FastAPI --> VisionEngine[OpenCV + YOLO Tracking Engine]
        FastAPI --> XAIEngine[SHAP & LIME Explainability Engine]
        FastAPI --> RAGEngine[GenAI Retail Assistant Engine]
    end

    subgraph Data & Caching Layer
        FastAPI --> PostgreSQL[(PostgreSQL Database)]
        FastAPI --> Redis[(Redis Cache & Task Broker)]
        FastAPI --> Celery[Celery Background Task Worker]
    end
```

---

## 3. Data Flow Diagram (DFD Level 1)

```mermaid
flowchart LR
    Sensors[CCTV Cameras & IoT Telemetry] -->|Raw Frame Stream| P1[1. CV Detection Engine]
    P1 -->|Occupancy & Queue Counts| DB[(PostgreSQL Database)]
    
    DB -->|Historical Time Series| P2[2. ML Footfall Predictor]
    P2 -->|Footfall Forecasts| P3[3. OR-Tools Shift Solver]
    P2 -->|Footfall Forecasts| P4[4. M/M/c Queue Model]
    
    P3 -->|Shift Schedule| Manager[Store Operations Manager]
    P4 -->|Open Counter Triggers| Manager
    
    Manager -->|Natural Language Query| P5[5. GenAI Retail Assistant]
    P5 -->|Explainable AI Insight| Manager
```

---

## 4. Sequence Diagram: Real-Time Cashier Open Counter Alert

```mermaid
sequenceDiagram
    autonumber
    participant CCTV as CCTV Camera Stream
    participant CV as Computer Vision Engine
    participant Queue as Queue Analytics Engine
    participant DB as PostgreSQL DB
    participant UI as Manager Dashboard
    
    CCTV->>CV: Stream Video Frame
    CV->>CV: Detect People & Queue Centroids
    CV->>Queue: Send Queue Count = 9, Active Counters = 3
    Queue->>Queue: Compute M/M/c Wait Time = 240s (>180s SLA)
    Queue->>DB: Store Alert "Open Counter 4 Immediately"
    DB->>UI: Push Websocket / API Alert Notification
    UI->>Manager: Display "CRITICAL: Open Counter #4"
```
