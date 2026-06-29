# 🐟 Shiny Fishstick

> **Compile websites into semantic SDKs and MCP servers for AI agents. OpenAPI for websites.**
>
> Stop making LLMs reason over HTML, CSS selectors, and brittle browser automation.
> Compile websites into structured actions that agents can call like native APIs.

```bash
pip install shiny-fishstick

shiny compile https://example.com
```

### Trust Signals
`Apache 2.0` • `Python Package` • `npm Package` • `MCP Compatible` • `CI Passing` • `29 Tests` • `Type Hints` • `OpenAPI Export` • **OpenAPI for websites.**

---

## Why?

| Traditional Browser Agents | Shiny Fishstick (OpenAPI for websites) |
| :--- | :--- |
| Parse raw HTML | Call structured SDK methods |
| Guess CSS selectors | Use semantic, defined actions |
| High prompt token cost | Tiny context window payload |
| DOM updates break workflows | Self-healing selector reconciliation |

🚀 **78.02% reduction in prompt context size on our verified benchmarks.**

---

##  How it Works

```text
Website
   │
   ▼
Crawler (Session capture & auth tracking)
   │
   ▼
Intent Engine (Semantic actions mapping)
   │
   ▼
Workflow Discovery (FSM sequence mapping)
   │
   ▼
Compiler (OpenAPI for websites)
   │
   ▼
preflight.yaml (Declarative actions spec)
   │
   ▼
┌───────────────────┼───────────────────┐
│                   │                   │
▼                   ▼                   ▼
SDKs (Py/TS/Rust)   MCP Server (JSON)   Validator CLI
```

---

## 💻 Example Output

Instead of writing custom selectors or letting your agent figure out page buttons, the compiled Python SDK client lets you do this:

```python
from specs.sdk import ShinyClient

# Initialize compiled spec client
site = ShinyClient(base_url="https://example-store.com")

# Execute high-level semantic actions
await site.login(email="admin@example.com", password="password123")
await site.search_products(query="shoes")
await site.add_to_cart(product_id="12", quantity=1)
await site.checkout()
```

---

## 📊 Benchmarks & Comparisons

Here is how **Shiny Fishstick** compares to traditional browser automation tools and frameworks:

| Feature | Playwright | Selenium | Browser Use | Shiny Fishstick (OpenAPI for websites) |
| :--- | :---: | :---: | :---: | :---: |
| **Semantic Actions** | ❌ | ❌ | Partial | **✅ Yes** |
| **SDK Generation** | ❌ | ❌ | ❌ | **✅ Yes** |
| **MCP Generation** | ❌ | ❌ | ❌ | **✅ Yes** |
| **OpenAPI Export** | ❌ | ❌ | ❌ | **✅ Yes** |
| **Workflow Graphs** | ❌ | ❌ | ❌ | **✅ Yes** |

### Live Benchmark Log Outputs
Run the benchmarking suite directly to measure overhead and resilience:
```bash
python benchmark.py
```
```text
[1/4] Measuring Token / Character Overhead...
  * Raw Product HTML Word Count: 505 words (~656 tokens)
  * Compiled Spec Word Count: 111 words (~144 tokens)
  🏆 Spec reduces token size overhead by 78.02%!

[2/4] Running Selector Flakiness Test...
  * Raw Playwright: ❌ Failed (Timeout after 1.51s) - selector was broken.

[3/4] Running State Reconciler Self-Healing Test...
  * Similarity Score: 1.0
  * Status: Self-Healed! ✅
```

---

## ⚙️ Core Features
*   **Semantic Action Discovery**: Automated extraction of forms, buttons, and links.
*   **Workflow Graph Generation**: Discovers sequential page state transition paths.
*   **API Upgrade Engine**: Automatically converts browser action steps into raw API fetches.
*   **Multi-language SDK Generation**: Exports ready-to-run Python, TypeScript, and Rust SDKs.
*   **MCP Server Generation**: Integrates specs into standard Model Context Protocol servers.
*   **Self-Healing Selectors**: Reconciles layout selector drifts dynamically.
*   **OpenAPI Export**: Creates standard OpenAPI 3.0 REST spec files—an **OpenAPI for websites**.

## 🚀 Advanced Features
*   **Playwright-Stealth Integration**: Bypasses bot verification scripts.
*   **AES-256 Fernet Encryption**: Cryptographically secures auth cookies and localstorage variables at rest.
*   **Auto-scaling Workers**: Dynamically scales crawl worker nodes using Redis task queues.
*   **Sandbox Virtualization**: Spawns mock site testbeds dynamically on random ports.
*   **API Interception & Stubbing**: Fulfills requests using pre-registered mocks.
*   **UI Chaos Monkey**: Mutates classes and injects latency to stress-test agent recovery.

---

## 👥 Who should use this?
*   ✅ **AI Agent Developers** wanting to connect LLMs to web interfaces.
*   ✅ **MCP Tool Creators** who want to expose websites as agent tools.
*   ✅ **Browser Automation Engineers** tired of maintaining selector scrapers.
*   ✅ **QA Teams** looking to validate site flow logic dynamically.
*   ✅ **RPA Platforms & Tooling** building enterprise web integration hooks.

---

## 🛠️ Quick Start & Installation

Install the CLI tool:
```bash
pip install shiny-fishstick
# or
npm install shiny-fishstick
# or
docker run hootsworth/shiny-fishstick
```

### Run the Demo Flow
Verify the E2E compiler on your machine:
```bash
# 1. Setup python env and playwright
make setup

# 2. Run test suites
make test

# 3. Compile mock site specs
make demo
```
This generates output specs and client libraries inside `./shared/specs/`.

---

## 💻 CLI Reference
*   `shiny compile <url>`: Compiles target website actions into a preflight spec directory.
*   `shiny inspect <spec>`: Prints a formatted action validation schema layout.
*   `shiny validate <spec>`: Enforces spec correctness (the validator for **OpenAPI for websites**).
*   `shiny serve-mcp <spec>`: Serves the spec tools list over the Model Context Protocol.
*   `shiny test <spec>`: Runs layout regressions tests.

---

## 📁 Examples Folder
We bundle several sample specification templates inside `./examples/`:
*   [examples/real-life/github_issue_creator.yaml](examples/real-life/github_issue_creator.yaml): Spec template details authentication workflows and issue creation actions.
*   [examples/real-life/stripe_checkout.yaml](examples/real-life/stripe_checkout.yaml): Spec template details filling Stripe Card Checkout fields.
*   [examples/ecommerce/](examples/ecommerce/preflight.yaml): Compiled action spec for store catalogues and checkout buttons.

---

## ❓ FAQ & Positioning

### Why not Playwright?
Playwright requires you to write and maintain manual browser scripts. Shiny Fishstick is a higher-level compiler layer that acts as an **OpenAPI for websites**, exposing clean function methods instead of DOM-selector queries.

### Why not Browser Use / Computer Use?
Browser Use and Computer Use rely on visual/multimodal models looking at screenshots and sending raw keystroke clicks. This is slow, has high prompt token overhead, and is prone to hallucination. Shiny Fishstick compiles the page structure beforehand so your agents execute actions deterministically.

### Why not Selenium?
Selenium is built for testing web browsers, not for enabling semantic API communication for AI agents.

---

## 🗺️ Roadmap
*   **Phase 1-3 (DX & Telemetry)**: Playwright-Stealth integration, Shadow DOM scan, encrypted session states.
*   **Phase 4-5 (Swagger & SDKs)**: Swagger exporters, arq distributed workers, state reconcilers, multi-language client builders.
*   **Phase 6-7 (Regression & Tuning)**: Pixel-diff engine, Alert webhook hubs, layouts dataset generator, local offline runtimes.
*   **Phase 8-10 (Enterprise & Scale)**: Spec Validator, Multi-tenant SSO workspaces, Chaos Monkey, Tauri desktop client, Terraform charts.

---

## 📜 Contributing
We welcome contributions to Shiny Fishstick! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License
This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
