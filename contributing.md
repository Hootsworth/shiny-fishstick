# 🤝 Contributing to Shiny Fishstick

Thank you for choosing to contribute to Shiny Fishstick! We want to make contributing to this project as easy and transparent as possible.

---

## 🛠️ Development Setup

1. **Fork the Repository** and clone your fork locally:
   ```bash
   git clone git@github.com:your-username/shiny-fishstick.git
   cd shiny-fishstick
   ```

2. **Backend Setup**:
   Initialize the Python virtual environment and install dependencies:
   ```bash
   python3 -m venv backend/venv
   source backend/venv/bin/activate
   pip install -r backend/requirements.txt
   playwright install chromium
   ```

3. **Frontend Setup**:
   Install Node modules inside the frontend folder:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## 🧪 Testing Guidelines

Before submitting any code changes, you **must** run the E2E verification test pipeline to ensure that all crawler, discovery, intent, and generator services are fully functional.

Run the test suite:
```bash
backend/venv/bin/python test_pipeline.py
```

### Writing New Tests
- If you add a new compiler component, add a verification step inside `test_pipeline.py` or create a unit test under `backend/tests/`.
- Ensure that you test mock sandbox interactions to verify Playwright navigation reliability.

---

## 🎨 Coding Style & Best Practices

### Python (Backend)
- Follow **PEP 8** style guidelines.
- Use type hints wherever possible to make compilation boundaries readable.
- Keep FastAPI path routing logic separate from service managers: route handling lives in `backend/app/main.py` while compiler logic lives in `backend/app/services/`.

### TypeScript / Next.js (Frontend)
- Adhere to functional React components using hooks.
- Styling must use vanilla Tailwind CSS classes with absolute layout responsive design.
- Always provide fallback states for client interface views when the backend server is offline.

---

## 📥 Submission Process

1. **Create a Branch**: Create a feature branch off of the `main` branch.
   ```bash
   git checkout -b feature/my-amazing-feature
   ```
2. **Commit Your Changes**: Keep commit messages descriptive and clear:
   ```bash
   git commit -m "feat: add support for dynamic form schema nested variables"
   ```
3. **Verify Everything**: Confirm that `test_pipeline.py` executes successfully and Next.js builds properly (`npm run build`).
4. **Push and PR**: Push your branch and open a Pull Request to the upstream repository.
   ```bash
   git push -u origin feature/my-amazing-feature
   ```

---

## 📄 Code of Conduct
We are committed to fostering a welcoming, supportive, and harassment-free community. Please be respectful and collaborative when interacting on issues and pull requests.
