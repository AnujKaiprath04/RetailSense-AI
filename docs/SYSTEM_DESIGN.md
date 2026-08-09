# 🏛️ RetailSense AI — Enterprise System Design & Architecture Document

> **Document Version:** 2.0.0 (MNC Production Grade)  
> **Target SLA:** <50ms P95 API Latency, 99.95% Availability  
> **Scale Target:** 10,000+ Retail Stores, 100M+ Daily Telemetry Events  

---

## 1. High-Level Architecture (HLD)

```
[ CCTV Cameras / Store Sensors ] ──▶ ( RTSP / Video Stream ) ──▶ [ OpenCV + YOLO Vision Microservice ]
                                                                             │
[ 100K Dataset / POS Logs ]       ──▶ ( Batch ETL Pipeline )  ──▶ [ Pandas / PyArrow Pipeline ]
                                                                             │
                                                                             ▼
                                                                  [ Feature Store / DB ]
                                                                             │
                        ┌────────────────────────────────────────────────────┴───────────────────────────────────────────────────┐
                        │                                                                                                        │
                        ▼                                                                                                        ▼
     [ Multi-Model Footfall ML Engine ]                                                                      [ Google OR-Tools Scheduler ]
   (XGBoost / LightGBM / Prophet / PyTorch LSTM)                                                             (Integer Linear Programming - ILP)
                        │                                                                                                        │
                        └────────────────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                                                             │
                                                                             ▼
                                                                    [ FastAPI Gateway ]
                                                                             │
                                              ┌──────────────────────────────┴──────────────────────────────┐
                                              ▼                                                             ▼
                                     [ REST API Endpoints ]                                     [ WebSocket Telemetry Stream ]
                                              │                                                             │
                                              └──────────────────────────────┬──────────────────────────────┘
                                                                             │
                                                                             ▼
                                                                  [ Single-Page App UI ]
                                                                (Chart.js / Bootstrap 5)
```

---

## 2. Mathematical Formulations & Algorithms

### 2.1 M/M/c Queuing Theory Formulation

To model checkout counter queue dynamics and predict customer wait times, RetailSense AI uses an **$M/M/c$ Poisson Queue Model**:

- **Arrival Rate ($\lambda$):** Customers arriving per minute at checkout.
- **Service Rate ($\mu$):** Customers processed per cashier per minute.
- **Active Cashiers ($c$):** Number of open checkout counters.
- **Traffic Intensity ($\rho$):**
  $$\rho = \frac{\lambda}{c \cdot \mu}$$
  *(Must satisfy $\rho < 1$ for system stability).*

- **Probability of Zero Customers in Queue ($P_0$):**
  $$P_0 = \left[ \sum_{k=0}^{c-1} \frac{(c\rho)^k}{k!} + \frac{(c\rho)^c}{c! (1 - \rho)} \right]^{-1}$$

- **Erlang-C Delay Probability ($P_q$):**
  $$P_q = \frac{\frac{(c\rho)^c}{c! (1 - \rho)}}{\sum_{k=0}^{c-1} \frac{(c\rho)^k}{k!} + \frac{(c\rho)^c}{c! (1 - \rho)}}$$

- **Expected Waiting Time in Line ($W_q$):**
  $$W_q = \frac{P_q}{c\mu - \lambda}$$

---

### 2.2 Google OR-Tools Integer Linear Programming (ILP) Shift Optimization

To minimize store labor costs while guaranteeing zero cashier shortages during peak footfall:

$$\min \sum_{s \in S} \text{Cost}_s \cdot x_s$$

**Subject to:**
1. **Coverage Constraint:**
   $$\sum_{s \text{ covers } t} x_s \ge \text{RequiredStaff}_t \quad \forall t \in \{8\text{AM}, \dots, 10\text{PM}\}$$
2. **Max Work Duration:**
   $$\text{ShiftHours}_s \le 8 \quad \forall s \in S$$
3. **Mandatory Rest Period:**
   $$x_{s_1} + x_{s_2} \le 1 \quad \forall s_1, s_2 \text{ overlapping within 11 hours}$$

---

### 2.3 SHAP (SHapley Additive exPlanations) Attribution

Feature contribution $f_x(i)$ to footfall forecast is calculated using cooperative game theory:

$$\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N|-|S|-1)!}{|N|!} \left[ v(S \cup \{i\}) - v(S) \right]$$

---

## 3. Database Schema & Data Modeling

- **Primary Entities:** `stores`, `footfall_logs`, `cashiers`, `shift_schedules`, `alerts`.
- **Indexing Strategy:** Composite B-Tree index on `(store_id, timestamp)` for $O(\log N)$ range queries over 100,000+ telemetry rows.
- **Partitioning Plan:** Range partitioning by `timestamp` (Monthly tables) for enterprise PostgreSQL deployment.

---

## 4. Scalability & MNC Reliability Engineering

1. **Caching Strategy:** Redis Cache layer for hot dashboard queries (`TTL = 15s`), achieving <5ms response time for 90% of requests.
2. **Asynchronous Task Queue:** Celery + RabbitMQ worker pool handling heavy model retraining and PDF report generation off the main API loop.
3. **Containerization & Deployment:** Multi-stage Docker build, Nginx reverse proxy with TLS 1.3 encryption, and Kubernetes Horizontal Pod Autoscaling (HPA) based on CPU/RAM metrics.
