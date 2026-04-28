# 🧙 Distributed Math Wizard

A distributed systems simulation demonstrating the evolution from synchronous API calls to a non-blocking, producer–consumer architecture using Valkey, multiprocessing, and secure tunneling.

## 🚀 Running the Project

The project now supports two running modes: **Local Development** and **Public Production**.

### 1. Developer Mode (Localhost)

Best for testing code changes without internet exposure.

```bash
docker compose up --build

```

* **Access:** [http://localhost](https://www.google.com/search?q=http://localhost)
* **Features:** HTTP (Port 80), 3 Workers, Valkey.

### 2. Public Mode (Secure Tunnel)

Launches the Cloudflare Tunnel to expose the app to the internet securely.

```bash
docker compose --profile public up --build

```

* **Access:** `https://math-wizard.shockcloud.win`
* **Features:** HTTPS (Port 443), End-to-End Encryption, Zero Trust Access.

> **Stop the cluster:** Press `Ctrl+C` or run `docker compose down`

---

## 🏗 Current Architecture (Distributed Phase)

The system operates as a **true distributed, asynchronous architecture** with shared state, load balancing, and secure ingress.

### Core Components

* **Ingress / Security:**
* **Cloudflare Tunnel:** `cloudflared` container (Sidecar) creating a secure outbound tunnel.
* **Gateway:** Nginx (Reverse Proxy). Listens on **Port 443** (Internal SSL) and **Port 80**.


* **Application Layer (Scaled):**
* **Replica Count:** **3 Containers** (Round Robin Load Balanced).
* **Process Model:** Each container runs:
* **API Process (Producer):** Handles HTTP requests.
* **Worker Process (Consumer):** Blocks on Valkey Queue for background math.




* **State Layer:**
* **Valkey (Redis-compatible):** Single source of truth. No local memory is used for state.



---

## 🔒 Security & Infrastructure (New)

We have moved beyond simple port forwarding to a **Zero Trust** architecture:

1. **Cloudflare Tunnel (US-3.1):**
* No open ports on the host router.
* Traffic enters via a secure edge connection.


2. **Origin CA Encryption (US-3.2):**
* Traffic between Cloudflare and Nginx is encrypted using a strict Origin CA Certificate.
* Nginx verifies the certificate chain.


3. **Zero Trust Access (US-3.3):**
* Public access is protected by an identity policy (e.g., University Email required).



---

## 🔁 Request Lifecycle (The "Shared Brain")

This system prevents "Split Brain" issues by enforcing a strict Producer-Consumer flow via Valkey:

1. **Task Creation (Producer)**
* Client calls `POST /task`.
* Load Balancer routes to **Node A**.
* Node A writes metadata to Valkey (`HSET task:<id>`) and pushes ID to Queue (`LPUSH task_queue`).
* Node A returns `202 Accepted`.


2. **Task Processing (Consumer)**
* **Node B** (or C, or A) is waiting on `BRPOP task_queue`.
* Node B pops the task and performs the calculation.
* Node B writes the result to Valkey.


3. **Task Polling (Observer)**
* Client polls `GET /tasks/<id>/status`.
* Load Balancer routes to **Node C**.
* Node C reads the status from Valkey (Shared State).
* **Result:** Any node can serve the status of a task created by any other node.



---

## 🛠 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Serves the UI dashboard. |
| `GET` | `/whoami` | Returns the current container ID. |
| `GET` | `/add` | **Sync:** Immediate calculation (blocking). |
| `POST` | `/task` | **Async:** Enqueues background task. Returns `task_id`. |
| `GET` | `/tasks/<id>/status` | **Async:** Returns task status, `checked_by` (API ID), and `handled_by` (Worker ID). |
| `GET` | `/valkey_test` | Connectivity diagnostics for Valkey. |

---

## ⚙️ Key Design Decisions

* **Horizontal Scaling:**
* Running `replicas: 3` proves that state is fully externalized.
* If one container dies, others pick up the work immediately.


* **Multiprocessing over Threading:**
* Avoids Python GIL. CPU-bound math never blocks the API.


* **Blocking Queue (`BRPOP`):**
* Zero CPU usage while idle. Instant reaction to new jobs.


* **Profile-Based Deployment:**
* Uses Docker Compose Profiles to separate "Dev" and "Public" environments easily.



---

## 🔮 Possible Extensions

* [ ] **Rate Limiting:** Use Valkey to limit requests per IP.
* [ ] **Dead Letter Queue:** Handle crashed tasks that never finish.
* [ ] **Kubernetes Migration:** Move from Docker Compose to K8s.

To update your **README.md** with the latest performance results and architectural safety measures, insert the following sections. This reflects your successful "Staircase" stress test and the implementation of the "Server Busy" circuit breaker.

---

## 📈 Performance & Stress Testing (Staircase Analysis)

The system was subjected to a **3-Stage Rocket** load profile using JMeter to identify the architectural "Inflection Point"—the exact moment where demand exceeds worker capacity.

### 1. The "Staircase" Test Strategy

We simulated three waves of computational load against the 3-worker cluster:

* **Wave 1 (Efficiency):** 3 concurrent users. Each task maps 1:1 to a worker container.
* **Wave 2 (Saturation):** 6 concurrent users. Workers at 100% utilization; tasks begin to queue in Valkey.
* **Wave 3 (Overload):** 12 concurrent users. Submission rate is double the processing throughput.

### 2. Findings: Architectural Integrity

The **Composite Graph** validates that our asynchronous architecture effectively protects the user experience:

* **Math Latency (Blue Spike):** Remains stable through Wave 2 but spikes vertically during Wave 3 as the Valkey queue backs up.
* **Casual UX Stability:** Despite background saturation, the decoupled API ensures "Casual Browsers" maintain sub-500ms response times.

---

## 🛡️ Stability & Fault Tolerance

We implemented two critical "Safety Valves" to prevent system collapse during peak overload:

### 1. Client-Side: Polling Timeout

The test plan includes a **JSR223 Assertion** and a **Counter** to prevent infinite client-side loops.

* **Logic:** If a task does not return a `COMPLETED` status within 10 polling attempts, the client aborts and signals a "Server Busy" state.
* **Benefit:** Reduces unnecessary network traffic and "zombie" polling.

### 2. Server-Side: Circuit Breaker

The `task_controller.py` implements a fast-fail mechanism to protect the Valkey state layer.

* **Action:** If the `task_queue` length exceeds a threshold (e.g., 20 jobs), the API rejects new submissions with a `503 Service Unavailable` error.
* **Standard:** Prevents memory exhaustion and ensures the system remains responsive for status checks of existing tasks.

---

## 📁 Project Structure (Updated)

```text
THE DISTRIBUTED MATH WIZARD
├── app/
│   ├── controllers/
│   │   ├── task_controller.py   # Circuit breaker logic
│   │   └── valkey_controller.py # Shared state observer
│   ├── services/
│   │   ├── adder_service.py     # CPU-bound logic
│   │   └── worker_service.py    # Background consumer
│   └── app.py                   # Flask entry point
├── nginx/                       # Load balancing & SSL
├── wizards_test.jmx             # Automated staircase test plan
├── jtestresults.png             # Stress test visualization
└── docker-compose.yml           # Multi-node orchestration

```
