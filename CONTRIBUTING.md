# Contributing to Shiny Fishstick 🐟

First off, thank you for checking out Shiny Fishstick! We are building a semantic navigation compiler for AI browser agents, and we need your help to make it rock-solid.

This guide will help you set up your local development environment, understand the architecture, and find starter issues to work on.

---

## 🏗️ Architecture Overview

Before writing code, review the core topology:
*   **FastAPI Backend (`backend/app/`)**: Exposes REST interfaces, registers WebSocket crawl node sync streams (`agent_hub.py`), and executes sandbox Playwright runs (`playground.py`).
*   **Compiler Services (`backend/app/services/`)**: Translates DOM interactive selectors into FSM state workflows (`workflow.py`), intercepts raw background API calls (`api_disco.py`), compiles multi-language client wrappers (`generator.py`), and healed broken locators (`state_reconciler.py`).
*   **Next.js Frontend (`frontend/src/`)**: A rich visual workspace dashboard with drag-and-drop FSM diagrams, assertions config panels, and live sandbox screenshot debugger streams.

---

## 🛠️ Local Development Setup

To configure a clean developer workspace:

### 1. Clone the Repository
```bash
git clone git@github.com:Hootsworth/shiny-fishstick.git
cd shiny-fishstick
```

### 2. Configure Python Backend
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
playwright install chromium
```

### 3. Configure React Frontend
```bash
cd frontend
npm install
cd ..
```

### 4. Run the Full Stack
We support zero-config out-of-the-box SQLite mode! To run using Docker Compose:
```bash
docker-compose up --build
```
This launches Redis, the background Task Worker, FastAPI web server, the mock ecommerce testbed, and Next.js frontend concurrently.

---

## 🧪 Testing Guidelines

Verify your modifications by running our pytest validation suite:
```bash
source backend/venv/bin/activate
python -m pytest --cov=backend/app --cov-report=term-missing tests/
```

Before sending a PR, please format and lint using `ruff`:
```bash
ruff check --fix .
```

---

## 🎯 real Starter Issues (Good First Issues)

Here are 10 concrete tasks you can pick up today:

1.  **#1: Crawler URL Wildcard Exclusions**: Add options to filter out specific regex URL patterns during crawl traversals.
2.  **#2: TypeScript SDK Headers Customization**: Extend generated typescript outputs to accept external config-level HTTP headers.
3.  **#3: Action Dictionary Parameter Sorting**: Order input attributes alphabetically inside the dashboard tables.
4.  **#4: SQLite DB Backup Command**: Add a script to backup the active `preflight.db` to a local file.
5.  **#5: Multi-page Form Custom Timeout**: Add adjustable navigation timeout parameters inside the `PlaygroundService`.
6.  **#6: Anti-bot Fingerprint Rotations**: Add randomized user-agent headers inside `playwright-stealth` sessions.
7.  **#7: JSON Schema Export Format**: Add option to compile specifications as a validated JSON file in addition to YAML.
8.  **#8: Sandbox Screenshots Carousel**: Add carousel display layouts to compare screenshots of consecutive page runs.
9.  **#9: Staging Drift Heuristic Weighting**: Adjust similarity ratios to favor selector ID weights over text similarity ratios.
10. **#10: Swagger spec custom server URL**: Expose options to configure custom Server base URLs in openapi exports.
