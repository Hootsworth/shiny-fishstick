# Contributing to Shiny Fishstick

First off, thank you for checking out Shiny Fishstick! We are excited to build the navigation layer for AI browser agents with you.

This document outlines the guidelines and steps to start contributing to this repository.

---

## 🛠️ Local Environment Setup

You can set up your development environment locally on your host machine or run the containerized stack.

### Option A: Local Machine Setup

#### Prerequisites
- **Python**: 3.9 or higher
- **Node.js**: 18.x or higher
- **Browser Dependencies**: Playwright Chromium driver

#### Setup Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Hootsworth/shiny-fishstick.git
   cd shiny-fishstick
   ```

2. **Setup the Backend**:
   ```bash
   python3 -m venv backend/venv
   source backend/venv/bin/activate
   pip install -r backend/requirements.txt
   playwright install chromium
   ```

3. **Setup the Frontend**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Run the Verification Pipeline**:
   Ensure everything works by compiling the specs and executing tests against the mock sandbox:
   ```bash
   python test_pipeline.py
   ```

5. **Run the local dev servers**:
   - Backend compiler: `python -m uvicorn backend.app.main:app --port 8000 --reload`
   - Target site sandbox: `python -m uvicorn backend.mock_site.main:app --port 8001`
   - Next.js Dashboard: `cd frontend && npm run dev`

---

### Option B: Docker Compose Setup

If you have Docker and Docker Compose installed, you can spin up the entire stack with a single command:

```bash
docker compose up --build
```

This will run:
- Backend compiler at **[http://localhost:8000](http://localhost:8000)**
- Next.js Frontend Dashboard at **[http://localhost:3000](http://localhost:3000)**
- Mock Sandbox Store at **[http://localhost:8001](http://localhost:8001)**

---

## 💅 Coding Standards & Pre-commit Hooks

We use **Ruff** for Python formatting/linting and **Prettier** for JS/TS/CSS/Markdown files.

1. **Install pre-commit**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Run checks manually**:
   ```bash
   pre-commit run --all-files
   ```

All PRs must pass the linting checks and E2E pipeline test suites in GitHub Actions before they can be merged.

---

## 📥 Pull Request Guidelines

1. **Branch Naming**:
   - Use descriptive names: `feature/your-feature-name` or `bugfix/issue-id`.
2. **Commit Messages**:
   - Make commits clean, atomic, and descriptive.
3. **Submit the PR**:
   - Link any open issues that the PR closes.
   - Describe what changed and include screenshots or logs if verifying UI behavior.
