# 🐟 Shiny Fishstick

> **The Navigation Layer for AI Browser Agents.**  
> *Because agents shouldn't have to parse raw HTML, guess CSS selectors, or deal with login redirects just to add a product to a cart.*

---

## 📖 The Story of the Shiny Fishstick

Every AI browser agent begins its journey with a simple goal: *"Buy a pair of red running shoes."* 

But as the agent descends into the raw DOM of modern web applications, the dream quickly turns into a nightmare. It encounters nested shadow DOMs, randomized Tailwind class names (`class="flex items-center justify-between p-4 md:p-6 bg-slate-900/40 border-b border-slate-800/60"`), dynamically injected popups, and complex, redirect-heavy authentication flows. To click a button, the agent must pay a heavy tax in context window size, sending raw screenshots and megabytes of HTML source back and forth to an LLM. And if a developer changes `#btn-add-to-cart` to `#add-to-cart-btn` next Tuesday? The agent crashes.

**Shiny Fishstick** is the compiler that changes this paradigm. 

Instead of forcing browser agents to navigate raw web pages ad-hoc, Shiny Fishstick pre-compiles any website into a structured, semantic action layer: **OpenAPI but for human-centric websites**. 

When you run Shiny Fishstick on a target site, it executes a complete discovery pipeline:
1. **The Crawler** performs a fast, BFS-based traversal, resolving login redirects and session configurations.
2. **The Analyzer** extracts all forms, interactive elements, and input selectors, generating robust selectors using heuristic scoring.
3. **The Intent Classifier** categories interactive elements into semantic actions (like `login`, `search_products`, `add_to_cart`, `checkout`).
4. **The API Discovery Engine** intercepts background network requests (XHR/Fetch) and automatically upgrades UI actions into high-speed API requests where possible.
5. **The Workflow Discovery Engine** models consecutive action transitions as a Finite State Machine (FSM).

The compiler spits out a clean `preflight.yaml` spec and native SDK code (Python/TypeScript):

```python
# The agent's new reality:
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

---

## 🛠️ The Compilation Pipeline in Depth

Shiny Fishstick works by executing a multi-stage compilation pipeline. Here is exactly what happens during each phase:

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

### 1. Crawling & URL Clustering
The Playwright-powered crawler starts at the seed URL and discovers child links. To prevent state explosion on dynamic paths (like `/product/1`, `/product/2`), the crawler clusters paths. It normalizes path templates into a single logical route, e.g., `/product/{id}`.

### 2. Heuristic DOM Selector Scoring
The analyzer parses the DOM structure of every discovered page. When it finds interactive elements (inputs, select fields, button controls), it scores possible CSS target selectors:
- **`data-testid`**: Ranks highest (Score: `1.0`) because it is purpose-built for testing stability.
- **`id`**: Ranks high (Score: `0.9`) if it is unique.
- **`name`**: Ranks medium (Score: `0.7`) for form input matching.
- **`class`**: Ranks low (Score: `0.4`) since CSS styling classes often drift.
- **`XPath / Tag`**: Used as a fallback of last resort (Score: `0.1`).

### 3. Intent Classification
Using a hybrid AI engine (Gemini API + regex-based local fallback rules), input parameters are clustered together. If a page has an `<input type="email">`, `<input type="password">`, and a submit button, they are combined into a single logical `login` action containing `email` and `password` variables.

### 4. Background API Upgrades
While the crawler performs actions (such as clicking the `#add-to-cart-btn`), it monitors network traffic. If the button click triggers a background XHR request (`POST /api/cart/add` carrying JSON keys `product_id` and `quantity`), Shiny Fishstick intercepts this network boundary. It maps the UI action directly to the REST API endpoint, bypassing DOM rendering for faster execution.

### 5. Finite State Machine (FSM) Linking
By analyzing consecutive step transitions, the system compiles logical user journeys into FSM paths. For example, the `purchase_flow` state machine outlines:
- **State 1**: `/login` (Action: `login` ➔ Transition to `/catalog`)
- **State 2**: `/catalog` (Action: `search_products` ➔ Transition to `/catalog`)
- **State 3**: `/product/{id}` (Action: `add_to_cart` ➔ Transition to `/checkout`)
- **State 4**: `/checkout` (Action: `checkout` ➔ Transition to order confirmation)

---

## 📄 Inside `preflight.yaml`

The output format is a structured YAML navigation descriptor. Here is a commented example of a compiled spec:

```yaml
version: 1.0.0
site: http://localhost:8001
actions:
  # Browser-based Action
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

  # Direct API-upgraded Action
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
3. **Action Explorer**: Review classified browser and API actions, view generated CSS target anchors, and inspect parameter schemas.
4. **FSM Visualizer**: Interactive workflow diagrams representing sequential state transitions.
5. **API Router**: Lists network intercepts and mapping schemas.
6. **SDK Download Center**: Copy and download compiled Python SDK, TypeScript SDK, or standard YAML specifications.

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

### 🧪 2. Run the Verification Pipeline

To execute a complete test compile run (which spins up a local mock store sandbox, runs the crawler, generates the specifications, and tests the output python SDK):

```bash
# From the project root
backend/venv/bin/python test_pipeline.py
```

Upon success, you will see `🏆 VERIFICATION SUCCESSFUL!` and your generated files will be written to `/shared/specs/`.

---

### 🖥️ 3. Running the Dashboard and APIs

To run the complete platform locally, open three terminal split tabs:

#### Tab A: Backend FastAPI Server
```bash
backend/venv/bin/python -m uvicorn backend.app.main:app --port 8000 --reload
```

#### Tab B: Sandbox Target Website
```bash
backend/venv/bin/python -m uvicorn backend.mock_site.main:app --port 8001 --reload
```

#### Tab C: Next.js Frontend Dashboard
```bash
cd frontend
npm run dev
```

Visit **[http://localhost:3000](http://localhost:3000)** to view your Shiny Fishstick workspace!

---

## 📜 Contributing
We welcome contributions to Shiny Fishstick! Please read [CONTRIBUTING.md](file:///Users/adityadixit/Documents/Code/Preflight%20Designer/contributing.md) for details on our code of conduct and submission process.

## 📄 License
This project is licensed under the Shiny Fishstick Proprietary Developer License. See [LICENSE](file:///Users/adityadixit/Documents/Code/Preflight%20Designer/LICENSE) for full details.
