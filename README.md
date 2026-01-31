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
