# The Distributed Math Wizard

A high-availability load balancing project that teaches web infrastructure and traffic management fundamentals.

## What It Does

A simple "Identity Adder" where the user provides two numbers via URL (e.g., `/add?a=10&b=5`). The system returns the sum and displays the unique ID of the server that performed the calculation.

**Example output:** `{"sum": 15, "handled_by": "a1b2c3d4e5f6"}`

## Project Structure

The project uses a **Controller-Service** architecture and an **Nginx Reverse Proxy** for security and load balancing:

* **`nginx/`**: Contains the reverse proxy configuration that hides the internal workers.
* **`app/controllers/`**: Handlers that manage the request/response cycle.
* **`app/services/`**: The "brain" of the app containing math and identity logic.
* **`app/app.py`**: The main entry point that connects routes to handlers.
* **`app/exceptions.py`**: Custom exceptions and global error handling logic.

## Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Python 3.x
* Git

## Verify Installation

```bash
docker --version
docker-compose --version
python --version
git --version

```

## Run the Project

The project is now managed via **Docker Compose**, which automatically handles the network between Nginx and the Flask worker.

```bash
# Build and start the entire stack
docker-compose up --build

# Run in detached mode (background)
docker-compose up -d --build

```

## Testing the Infrastructure

Once the containers are running, you can test the layers:

1. **Public Access (via Nginx):** `curl "http://localhost/add?a=10&b=5"`
2. **Private Security (Direct bypass):** `curl "http://localhost:5000/add"` (This should fail/timeout)