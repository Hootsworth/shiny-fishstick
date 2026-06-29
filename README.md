# 🐟 Shiny Fishstick

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](tests/)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](setup.py)
[![Node Version](https://img.shields.io/badge/node-%3E%3D18.0.0-green.svg)](frontend/)

> **The Navigation Layer for AI Browser Agents.**  
> *Because agents shouldn't have to parse raw HTML, guess CSS selectors, or deal with login redirects just to add a product to a cart.*

---

## 📖 The Story of the Shiny Fishstick

Every AI browser agent begins its journey with a simple goal: *"Buy a pair of red running shoes."* 

But as the agent descends into the raw DOM of modern web applications, the dream quickly turns into a nightmare. It encounters nested shadow DOMs, randomized Tailwind class names (`class="flex items-center justify-between p-4 bg-slate-900"`), dynamically injected popups, and complex, redirect-heavy authentication flows. To click a button, the agent must pay a heavy tax in context window size, sending raw screenshots and megabytes of HTML source back and forth to an LLM. And if a developer changes `#btn-add-to-cart` to `#add-to-cart-btn` next Tuesday? The agent crashes.

**Shiny Fishstick** is the compiler that changes this paradigm. 

Instead of forcing browser agents to navigate raw web pages ad-hoc, Shiny Fishstick pre-compiles any website into a structured, semantic action layer: **OpenAPI but for human-centric websites**. 

When you run Shiny Fishstick on a target site, it executes a complete discovery pipeline:
1. **The Crawler** performs a fast, BFS-based traversal, resolving login redirects and session configurations.
2. **The Analyzer** extracts all forms, interactive elements, and input selectors, generating robust selectors using heuristic scoring.
3. **The Intent Classifier** categorizes interactive elements into semantic actions (like `login`, `search_products`, `add_to_cart`, `checkout`).
4. **The API Discovery Engine** intercepts background network requests (XHR/Fetch) and automatically upgrades UI actions into high-speed API requests where possible.
5. **The Workflow Discovery Engine** models consecutive action transitions as a Finite State Machine (FSM).

The compiler spits out a clean `preflight.yaml` spec and native SDK codes:

```python
# The agent's new reality (Python):
site = ShinyFishstickSiteSDK("http://my-shop.com")
site.start()
site.login(email="agent@gemini.com", password="secure123")
site.search_products(q="running shoes")
site.add_to_cart(product_id="42", quantity=1) # Executes directly as a REST call!
site.checkout()
```

Instead of expensive DOM scraping, AI agents can now interact with web platforms with the speed, stability, and structure of a native REST API.

---

## ⚡ Core Features

- 🔍 **Redirect-Aware BFS Crawler**: Gracefully handles login redirection and maps authorized session states.
- 🏷️ **Dynamic Heuristic DOM Analyzer**: Ranks CSS selectors to ensure stable target selection (`data-testid` > `id` > `name` > `class` > `xpath`).
- 🤖 **Semantic Intent Extraction**: Categorizes UI input targets into high-level agent parameters.
- 🔌 **XHR Interception & API Upgrades**: Captures background fetches to replace slow browser UI clicks with direct API requests.
- 📈 **Workflow FSM Discovery**: Automatically discovers sequential dependencies (e.g. `login` -> `search` -> `add_to_cart` -> `checkout`).
- 🖥️ **Stunning Visual Dashboard**: A beautiful, premium dark-mode Next.js application to monitor crawls, inspect actions, view FSM graphs, and download generated SDKs.
- 🔑 **Generic Auth & Storage Serialization**: Automatically detects credentials forms using pattern matches and captures browser session storage states (`cookies`, `localStorage`, `sessionStorage`).
- 🛡️ **API Authentication Token Propagation**: Sniffs headers during crawling, correlates authentication tokens (e.g., Bearer JWTs) with their storage source, and propagates them in direct SDK API calls.
- 🖥️ **Model Context Protocol (MCP) Server**: Auto-generates a standalone JSON-RPC 2.0 stdio MCP server wrapper directly mapping site actions to callable LLM tools.
- 🧪 **Automated E2E Test Generator**: Auto-compiles a complete Playwright integration verification suite (`test_sdk.py`) executing discovered FSM journeys and asserting validation blocks.
- 🕵️ **Anti-Bot Stealth Evasion**: Integrates `playwright-stealth` to bypass basic bot protection checks (spoofing browser properties, hiding webdriver indicators).
- 🌐 **Configurable Proxy Routing**: Restores connection-level proxy settings (including user/pass authentication) from environment variables to bypass IP-based rate limiting.
- 🖼️ **Sub-Frame / Iframe Traversal**: Scans all sub-frames recursively during analysis, saving nested elements and generating dynamic `frame_locator` actions.
- 🔒 **Encrypted Credentials Store**: Encrypts sensitive database session configurations and credentials using `cryptography.fernet` symmetric encryption (auto-provisions local `.encryption.key`).
- 🎨 **Visual FSM Editor**: Drag-and-drop sorting panel allowing developers to reorder workflow transition sequences, customize target page routing, insert/delete step nodes, and commit saves directly back to the database.
- 📝 **Action Assertions Builder**: Exposes interactive validation configuration on actions directly via the dictionary dashboard. Developers can build custom Playwright verification checks (`visible`, `not_visible`, `contains_text`, `url_equals`) that compile into the E2E test suites.
- 🦀 **Multi-Language SDKs - Rust**: Compile-ready Rust client SDK (`sdk.rs`) output mapping actions using `reqwest` endpoints, `serde_json` objects, and commented browser actions.
- 🦙 **Local Offline LLM Support - Ollama**: Route intent classification prompts entirely offline to local inference servers (e.g. Ollama with `llama3`/`mistral`), avoiding any external API key dependencies.
- 🔗 **Clustered WebSocket Coordination Hub (New)**: Coordinates distributed, parallel crawling nodes via a decentralized WebSocket registry server (`agent_hub.py`), avoiding duplicate URL scanning.
- ⚡ **Sandbox Playground Execution Runner (New)**: Sandbox Playwright runner (`playground.py`) that tests custom assertions live on pages and returns real-time base64 browser screenshot streams to the UI.
- 📄 **OpenAPI Spec Exporter (New)**: Auto-compiles discovered raw user UI actions and network endpoints into standardized Swagger/OpenAPI 3.0 specs (`openapi_exporter.py`).
- 📊 **Worker Queue Autoscaler Metrics (New)**: Integrates a Redis queue length scanner (`worker_scaler.py`) advising scaling actions based on task load.
- 🔄 **Multi-Environment State Reconciler (New)**: Cross-environment DOM reconciler service (`state_reconciler.py`) checking selectors validity across staging and production to report element layout drift.

---

## 🛠️ The Compilation Pipeline in Depth

```
[Target URL] 
     │
     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  1. Crawler  │ ───> │ 2. DOM Scrape│ ───> │ 3. Intent AI │ ───> │  4. API Sniff│
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
                                                                         │
                                                                         ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ 8. SDK Write │ <─── │ 7. YAML Gen  │ <─── │  6. FSM Link │ <─── │  5. Session  │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

---

## 📄 Inside `preflight.yaml`

The output format is a structured YAML navigation descriptor. Here is a commented example of a compiled spec:

```yaml
version: 1.0.0
site: http://localhost:8001
actions:
  login:
    description: Logs in the user with credentials
    action_type: browser
    selector: '#login-form'
    parameters:
      - name: email
        type: string
        required: true
        selector: '#email'
      - name: password
        type: string
        required: true
        selector: '#password'
    assertions:
      - type: visible
        selector: '#success-banner'

  add_to_cart:
    description: Adds the current product to the shopping cart
    action_type: api
    selector: '#add-to-cart-btn'
    parameters:
      - name: product_id
        type: string
        required: true
        selector: ''
      - name: quantity
        type: integer
        required: true
        selector: ''
    api:
      url: /api/cart/add
      method: POST
```

---

## 🖥️ Visual Dashboard Tour

The Next.js frontend provides a comprehensive suite of developer workspace pages:
1. **Projects Manager**: Create projects and track high-level statistics (discovered actions, api upgrades, and spec validity score).
2. **Crawl & Log Feed**: Watch real-time logs stream in from the active Playwright web scraper.
3. **Action Explorer**: Review classified actions, update CSS selectors, and add/remove **Playwright Assertions**.
4. **Assertions Sandbox Playground (New)**: Test actions live in a Playwright sandbox, evaluate assertions, and view real-time screenshot feeds.
5. **FSM Visualizer**: Edit workflow diagrams representing sequential state transitions (add/delete steps, reorder execution steps, modify transition parameters).
6. **SDK Download Center**: Copy and download compiled Python, TypeScript, or Rust SDKs, and standard YAML specifications.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Playwright dependencies (`playwright install`)

### 📦 1. Installation

Clone the repository and set up the backend virtual environment:
```bash
git clone git@github.com:Hootsworth/shiny-fishstick.git
cd shiny-fishstick
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
playwright install chromium
```

Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

---

### 🧪 2. Running Verification & Tests

To run the complete test suite locally:
```bash
python -m pytest --cov=backend/app --cov-report=term-missing tests/
```

To run a single verification pipeline (which spins up a local mock store sandbox, runs the crawler, generates the specifications, and tests the output python SDK):
```bash
python test_pipeline.py
```

Upon success, you will see `🏆 VERIFICATION SUCCESSFUL!` and your generated files will be written to `/shared/specs/`.

---

### 📦 3. Production Deployment (Docker-Compose)

To deploy the entire environment (PostgreSQL, Redis, FastAPI App, background task Worker, Next.js frontend) with a single command:
```bash
docker-compose -f docker-compose.prod.yml up --build
```

---

## 🌐 The Big Vision: A Shared Action-Spec Layer for the Agentic Web

We believe browser agents shouldn't have to guess how to click, search, or buy on every unique website.

Our goal is to turn **Shiny Fishstick** into a standard open-source web action spec ecosystem:
1.  **`preflight.yaml` Spec**: A formal schema declaring semantic web actions and workflows.
2.  **The Compiler & CLI**: Automates crawler-based discovery and spec compiles.
3.  **The Validator (`shiny validate`)**: Enforces spec syntax correctness.
4.  **Generators**: Compiles specs into multi-language client SDKs and Model Context Protocol (MCP) servers.
5.  **Hosted registry**: A public registry where websites publish their preflight specs so agents can call them natively.

By compiling the web into structured actions, we are building the semantic interface for the agentic web.

---

## 📜 Contributing
We welcome contributions to Shiny Fishstick! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License
This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
