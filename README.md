Here is the updated README. It maintains your original style and structure while incorporating the new directory organization and the specific run command you requested.

---

# The Distributed Math Wizard

A high-availability load balancing project that teaches web infrastructure and traffic management fundamentals.

## What It Does

A simple "Identity Adder" where the user provides two numbers via URL (e.g., `add?a=10&b=5`). The system returns the sum and displays the unique ID of the server that performed the calculation.

**Example output:** `{"sum": 15, "handled_by": "a1b2c3d4e5f6"}`

## Project Structure

The project is organized into a modular **Controller-Service** architecture:

* **`app/controllers/`**: Handlers that manage the request/response cycle.
* **`app/services/`**: The "brain" of the app containing math and identity logic.
* **`app/app.py`**: The main entry point that connects routes to handlers.

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

```bash
# Build the image
docker build -t math-wizard .

# Run the container
docker run --rm -p 5000:5000 -e FLASK_APP=app.app:app math-wizard

```

# Rayhan's run

```bash
docker build -t math-wizard .
docker run --rm -p 5000:5000 -e FLASK_APP=app.app:app math-wizard

```

# Nicole's run

```bash
docker build -t math-wizard .
docker run --rm -p 5000:5000 -e FLASK_APP=app/app.py math-wizard

```