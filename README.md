# 🧙 Distributed Math Wizard

A distributed system simulation demonstrating the evolution from synchronous API calls to asynchronous, polling-based architectures.

## 🚀 Running the Project

To build the containers and start the entire cluster, run:

```bash
docker compose up --build

```

* **Access the UI:** [http://localhost](https://www.google.com/search?q=http://localhost)
* **Stop the cluster:** Press `Ctrl+C` or run `docker compose down`

> **Note:** Use `--build` whenever you modify the Python code to ensure the containers update with your latest changes.

---

## 🏗 Current Architecture (Hybrid Phase)

The system currently mimics a microservices environment using a single Flask application with background threading:

* **Gateway:** Nginx (Reverse Proxy on port `80`).
* **Application:** Flask (Python) handling API requests on port `5000`.
* **Background Workers:** Python `threading` module (Simulating distributed worker nodes).
* **State Store:** In-Memory Python Dictionary (Volatile storage).
* **Frontend:** Alpine.js + Pico.css (Reactive UI with polling logic).

### Identity Tracking (The 3-Step Lifecycle)

The system now tracks the Container ID for every stage of the request lifecycle:

1. **Initiated By:** The API node that accepted the `POST` request.
2. **Last Checked By:** The API node that served the status update (`checked_by`).
3. **Processed By:** The Worker node that actually performed the calculation (`handled_by`).

---

## 🛠 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Serves the UI dashboard. |
| `GET` | `/whoami` | Returns the current container ID. |
| `GET` | `/add` | **Sync:** Performs calculation immediately (blocking). |
| `POST` | `/task` | **Async:** Queues a background task. Returns `task_id`. |
| `GET` | `/tasks/<id>/status` | **Async:** Returns status, `checked_by` (API ID), and `handled_by` (Worker ID, if complete). |
| `GET` | `/valkey_test` | Diagnostics for distributed store connectivity. |

---

## 🔮 Future State (Valkey Integration)

The next phase of this project moves from "Simulation" to "Production Architecture" by introducing **Valkey** (a Redis fork) as the central nervous system.

### How it will work:

1. **Decoupling:** The API will no longer spawn threads. Instead, it will act as a **Producer**.
2. **The Queue:** When `/task` is called, the API will push a JSON job payload into a Valkey List (e.g., `lpush tasks_queue`).
3. **The Workers:** A separate fleet of Worker Containers (running a `worker.py` script) will act as **Consumers**. They will block-pop (`brpop`) items from Valkey.
4. **Persistence:** Task status and results will be stored in Valkey Keys (e.g., `SET task:123 ...`) instead of a local Python dictionary. This allows the API to restart without losing task history.
5. **Scalability:** We will be able to scale the API nodes and Worker nodes independently.

### To Be Implemented

* [ ] **Valkey Producer:** Update `task_service.py` to push jobs to Valkey instead of starting a Thread.
* [ ] **Valkey Consumer:** Create a dedicated `worker.py` entry point that listens to the Valkey queue.
* [ ] **State Persistence:** Update `get_task_status` to query Valkey for results instead of the local memory.
* [ ] **Docker Compose Update:** Define the standalone `worker` service in `docker-compose.yml` to run multiple instances.

```

```