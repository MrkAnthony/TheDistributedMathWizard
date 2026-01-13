# The Distributed Math Wizard

A high-availability load balancing project that teaches web infrastructure and traffic management fundamentals.

## What It Does

A simple "Identity Adder" where the user provides two numbers via URL (e.g., `?num1=10&num2=5`). The system returns the sum and displays the unique ID and color-coded name of the server that performed the calculation.

Example output: `Sum: 15 | Processed by: Wizard-Blue (ID: a1b2c3)`

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.x
- Git

## Verify Installation

```bash
docker --version
docker-compose --version
python --version
git --version
```

## Run the Project

```bash
docker-compose up
```