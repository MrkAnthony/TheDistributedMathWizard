
# 🧙 Distributed Math Wizard

A distributed systems simulation demonstrating the evolution from synchronous API calls to a non-blocking, producer–consumer architecture using Valkey and multiprocessing.

---

## 🚀 Running the Project

To build the containers and start the entire cluster, run:

```bash
docker compose up --build
````

* **Access the UI:** [http://localhost](http://localhost)
* **Stop the cluster:** Press `Ctrl+C` or run `docker compose down`

> **Note:** Use `--build` whenever you modify the Python code to ensure containers reflect the latest changes.

---

## 🏗 Current Architecture (Distributed Phase)

The system now operates as a **true distributed, asynchronous architecture** with shared state and background workers.

### Core Components

* **Gateway:** Nginx (reverse proxy on port `80`)
* **Application Nodes:** Flask (Python) on port `5000`

  * Each container runs **two processes**:

    * **API Process (Producer)** – handles HTTP requests
    * **Worker Process (Consumer)** – performs background math
* **Message Broker / State Store:** **Valkey (Redis-compatible)**
* **Frontend:** Alpine.js + Pico.css (polling-based UI)

### Symmetric Container Design

Every `math_wizard` container is identical and self-sufficient:

* Accepts API requests
* Pushes jobs into Valkey
* Runs a background worker that can process jobs from *any* container

There are **no dedicated worker containers** — scaling the service scales both API capacity and worker throughput automatically.

---

## 🔁 Request Lifecycle (Producer–Consumer Flow)

1. **Task Creation**

   * Client calls `POST /task`
   * API generates a `task_id`
   * Task metadata is stored in Valkey (`task:<uuid>`)
   * Job payload is pushed to a Valkey queue (`LPUSH task_queue`)
   * API immediately returns `202 Accepted`

2. **Task Processing**

   * A worker process (from any container) blocks on `BRPOP task_queue`
   * When a job arrives, it performs the calculation
   * Result and status are written back to Valkey
   * Worker records its container ID as `handled_by`

3. **Task Polling**

   * Client polls `GET /tasks/<id>/status`
   * Any API container can serve the request
   * Response includes:

     * `status`
     * `checked_by` (API container ID)
     * `handled_by` (worker container ID, once complete)

---

## 🧬 Identity Tracking (3-Step Visibility)

Each task exposes container-level observability:

1. **Initiated By** – container that accepted the `POST /task`
2. **Checked By** – container serving the status request
3. **Handled By** – container whose worker completed the task

This proves:

* Load balancing works
* Any node can process any job
* State is fully decoupled from individual containers

---

## 🛠 API Endpoints

| Method | Endpoint             | Description                                            |
| ------ | -------------------- | ------------------------------------------------------ |
| `GET`  | `/`                  | Serves the UI dashboard                                |
| `GET`  | `/whoami`            | Returns the current container ID                       |
| `GET`  | `/add`               | **Sync:** Immediate calculation (blocking)             |
| `POST` | `/task`              | **Async:** Enqueues background task, returns `task_id` |
| `GET`  | `/tasks/<id>/status` | Returns task status, `checked_by`, and `handled_by`    |
| `GET`  | `/valkey_test`       | Connectivity diagnostics for Valkey                    |

---

## ⚙️ Key Design Decisions

* **Multiprocessing over threading**

  * Avoids Python GIL
  * CPU-bound math never blocks the API

* **Blocking queue (`BRPOP`)**

  * Zero CPU usage while idle
  * Efficient worker behavior

* **Externalized state**

  * Task history survives container restarts
  * Enables horizontal scaling

* **No async framework required**

  * Achieves non-blocking behavior using classic OS processes

---

## 🔮 Possible Extensions

* Multiple worker processes per container
* Retry / dead-letter queues
* Graceful worker shutdown
* Rate limiting / backpressure
* Migration to Gunicorn or Kubernetes

---

This project demonstrates how real production systems decouple request handling from execution using queues, shared state, and background workers — without relying on heavy frameworks.

