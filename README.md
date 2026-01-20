# 🧙‍♂️ The Distributed Math Wizard

A high-availability load balancing project designed to demonstrate web infrastructure, traffic management, and secure proxying.

## What It Does

The Math Wizard provides a simple web interface and API to perform addition. While the math is simple, the infrastructure is robust:

* **Web UI**: A clean, minimalist frontend built with Pico.css.
* **Reverse Proxy**: Nginx acts as the entry point, hiding the Flask worker from the public internet.
* **Identity Tracking**: Each response includes the unique ID of the specific container that processed the request.

**Example JSON output:** `{"sum": 15, "handled_by": "a1b2c3d4e5f6"}`

---

## Project Structure

The project follows a modular **Controller-Service** pattern to separate web logic from business logic:

* **`nginx/`**: Nginx configuration for proxying and security.
* **`app/templates/`**: HTML files for the client-facing UI.
* **`app/controllers/`**: Request handlers that manage the API lifecycle.
* **`app/services/`**: The core logic for math and system identity.
* **`app/app.py`**: The Flask application entry point.

---

## Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Python 3.11+ (for local development)
* WSL2 (if on Windows)

---

## How to Run

The entire stack is managed via **Docker Compose**.

```bash
# Build and start the infrastructure
docker-compose up --build

# Run in the background
docker-compose up -d --build

# Stop the project and clean up old containers
docker-compose down --remove-orphans

```

Access the wizard at: **`http://localhost`**

---

## Testing the Layers

1. **UI/Proxy Test**: Visit `http://localhost` in your browser.
2. **API Test**: `curl "http://localhost/add?a=10&b=5"`.
3. **Security Check**: `curl "http://localhost:5000"` (This should be blocked/inaccessible, proving the worker is hidden).

---