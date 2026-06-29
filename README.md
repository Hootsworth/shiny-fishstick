# 🐟 Shiny Fishstick

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![CI Status](https://github.com/Hootsworth/shiny-fishstick/actions/workflows/ci.yml/badge.svg)](https://github.com/Hootsworth/shiny-fishstick/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](backend/)
[![Node](https://img.shields.io/badge/node-%3E%3D18-green.svg)](frontend/)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](examples/mcp-agent/)

> **Compile websites into semantic SDKs and MCP servers for AI agents.**  
> *Because agents shouldn't have to parse raw HTML, guess CSS selectors, or crash when a button gets renamed.*

---

## The Problem

Every AI browser agent today faces the same wall.

The agent gets a task: *"Buy a pair of running shoes."*

And then it has to:
- Parse thousands of tokens of raw HTML just to find a button
- Guess at CSS selectors that break the moment a developer refactors the frontend
- Handle login redirects, session state, shadow DOMs, and dynamic injections
- Pay a steep LLM context tax on every single page interaction

This is not a browser problem. It's an abstraction problem.

**Shiny Fishstick** is the compiler that fixes it.

---

## The Solution

Run Shiny Fishstick on any website once. It crawls the site, discovers what it can do, and compiles the result into a clean, typed, agent-ready SDK.

Your agent goes from this:

```python
# Without Shiny Fishstick 😰
page = await browser.new_page()
await page.goto("https://shop.example.com")
await page.locator("#email").fill("agent@example.com")
await page.locator("#password").fill("hunter2")
await page.locator("#login-submit-btn").click()
await page.wait_for_selector(".dashboard")
# ... 40 more lines for every action
```

To this:

```python
# With Shiny Fishstick 🐟
site = ShinyClient("https://shop.example.com")
await site.login(email="agent@example.com", password="hunter2")
await site.search_products(query="running shoes")
await site.add_to_cart(product_id="42", quantity=1)  # direct API call, no browser needed
await site.checkout()
```

---

## Quick Start

**Requirements:** Python 3.9+, Node.js 18+

```bash
# Clone and set up in one shot
git clone git@github.com:Hootsworth/shiny-fishstick.git
cd shiny-fishstick
make setup

# Run the live demo — crawls a local mock store, generates all SDKs
make demo
```

Generated files land in `./shared/specs/`:

```
shared/specs/
├── preflight.yaml     # The compiled action spec
├── sdk.py             # Python client SDK
├── sdk.ts             # TypeScript client SDK
├── sdk.rs             # Rust client SDK
└── mcp_server.py      # MCP server — ready to plug into any LLM
```

---

## How It Works

```
Target URL
    │
    ▼
Crawler          →  BFS traversal, handles auth redirects & session state
    │
    ▼
DOM Analyzer     →  Heuristic selector scoring (data-testid > id > class > xpath)
    │
    ▼
Intent Engine    →  LLM/heuristic classifier maps elements to semantic actions
    │
    ▼
API Sniffer      →  Intercepts XHR/Fetch traffic, upgrades UI actions to API calls
    │
    ▼
Workflow Builder →  Models action sequences as a Finite State Machine (FSM)
    │
    ▼
Compiler         →  Generates preflight.yaml + SDKs + MCP server
```

The key insight: once `add_to_cart` is discovered as a `POST /api/cart/add` call, future executions skip the browser entirely and call the API directly. Faster, cheaper, more reliable.

---

## The `preflight.yaml` Format

The output is a human-readable, version-controllable action spec:

```yaml
version: 1.0.0
site: https://shop.example.com
actions:
  login:
    description: Authenticates the user
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
        selector: '#dashboard'

  add_to_cart:
    description: Adds a product to the cart
    action_type: api          # ← upgraded to direct API call
    api:
      url: /api/cart/add
      method: POST
    parameters:
      - name: product_id
        type: string
        required: true
      - name: quantity
        type: integer
        required: true
```

Think of it as OpenAPI — but for websites that were never designed to have an API.

---

## Benchmarks

Full methodology and reproduction instructions: **[BENCHMARKS.md](BENCHMARKS.md)**

Three suites, all numbers live and verifiable:

```bash
make demo && python benchmark.py           # mock store (controlled)
python benchmark_real_sites.py             # Wikipedia, HN, GitHub (live)
python benchmark_developer_effort.py       # developer effort (code metrics)
```

### Performance — Mock Store

| Benchmark | Raw Playwright | Compiled SDK | Result |
|---|---|---|---|
| Token overhead | ~669 tokens/call | ~144 tokens/call | **78.5% fewer tokens** |
| Action latency (avg) | 1,444 ms | 1.5 ms | **953× faster** |
| DOM mutation reliability | 0% (20/20 fail) | 100% (0/20 fail) | **+100 pp** |
| Python heap delta | 1,642 KB | 21 KB | **99% less** |
| Selector self-healing | ❌ manual fix | ✅ 1,648 ms auto | similarity: 1.00 |

### Performance — Real Sites (Wikipedia, Hacker News, GitHub)

No mock servers. The "Compiled SDK" column is the API Shiny Fishstick discovers and exposes as a typed method.

| Site | Page tokens | API tokens | Reduction | Speed-up | Reliability |
|---|---|---|---|---|---|
| Wikipedia | 40,833 | 131 | **99.7%** | 8× | 0% → 100% |
| Hacker News | 2,298 | 1 | **100%** | 3.5× | 0% → 100% |
| GitHub (vscode) | 34,292 | 5 | **100%** | 24× | 0% → 100% |
| **Average** | **25,808** | **46** | **99.9%** | **12×** | **+100 pp** |

### Developer Effort — Writing the Same Agent in Both Approaches

Task: login → search → add\_to\_cart → checkout.

| Metric | Raw Playwright | Shiny Fishstick | Improvement |
|---|---|---|---|
| Lines of code | 75 | 10 | **87% less** |
| CSS selectors to hand-discover & maintain | 6 | 0 | **none to manage** |
| Explicit browser sync calls | 12 | 0 | **100% less** |
| Boilerplate lines (session/teardown/errors) | 43 of 75 (57%) | 1 of 10 (10%) | **98% less** |
| Cyclomatic complexity | 11 | 1 | **10× simpler** |
| Setup steps before first line of agent code | 10 | 3 | **7 fewer** |
| Manual fixes needed per full site redesign | 8 | 0 | **zero maintenance** |

The 75-line raw Playwright script and the 10-line Shiny Fishstick script do exactly the same thing. 57% of the Playwright version is pure infrastructure — session capture, error handling, teardown. With Shiny Fishstick, 90% of the script is intent.

> See [BENCHMARKS.md](BENCHMARKS.md) for full per-metric explanations, the complete code side-by-side, and honest caveats on every number.

---


## Features

### Core
| Feature | What it does |
|---|---|
| 🔍 BFS Crawler | Traverses pages, handles auth redirects, captures session state |
| 🏷️ DOM Analyzer | Heuristic selector scoring for stable element targeting |
| 🤖 Intent Classifier | Maps UI elements to semantic action names via LLM or heuristics |
| 🔌 API Upgrade Engine | Intercepts XHR/Fetch and converts UI clicks to direct API calls |
| 📈 Workflow FSM | Models multi-step action sequences as a state machine |
| 🛠️ SDK Generator | Outputs Python, TypeScript, and Rust clients |
| 📄 MCP Server | Auto-generates a JSON-RPC 2.0 MCP server for LLM tool use |
| 📋 OpenAPI Exporter | Compiles discovered endpoints into standard OpenAPI 3.0 specs |

### Advanced
| Feature | What it does |
|---|---|
| 🔒 Encrypted Credentials | Auth sessions encrypted at rest with AES-256 Fernet |
| 🕵️ Stealth Mode | `playwright-stealth` integration to bypass bot detection |
| 🌐 Proxy Support | Environment-based proxy config including authenticated proxies |
| 🖼️ iFrame Traversal | Scans nested frames recursively, generates `frame_locator` actions |
| 🔄 State Reconciler | Detects selector drift across environments and auto-heals |
| 🧪 Chaos Monkey | Mutates selectors and injects latency to test self-healing |
| 🧪 Sandbox Orchestrator | Spins up mock site instances on demand for testing |
| 🦙 Offline LLM | Routes intent classification to local Ollama instances |
| 📡 WebSocket Agent Hub | Coordinates distributed crawl workers via WebSocket registry |

---

## Dashboard

A Next.js frontend ships with the project for when you want a visual interface:

- **Projects** — create and manage compilation targets
- **Crawl Feed** — watch real-time logs from the Playwright crawler
- **Action Explorer** — inspect, edit, and add assertions to discovered actions
- **FSM Visualizer** — drag-and-drop workflow editor with live graph rendering
- **SDK Download** — copy or download compiled SDKs and specs
- **Docs & Help** — inline reference for the CLI, architecture, and FAQ

---

## CLI Reference

```bash
# Compile a website into a spec + SDKs
shiny compile https://example.com --out ./specs

# Inspect a spec file
shiny inspect ./specs/preflight.yaml

# Validate spec structure
shiny validate ./specs/preflight.yaml

# Serve the spec as an MCP server
shiny serve-mcp ./specs/preflight.yaml

# Run layout regression tests
shiny test ./specs/preflight.yaml
```

---

## Examples

```
examples/
├── ecommerce/          → preflight.yaml for a catalogue + checkout flow
├── saas-dashboard/     → preflight.yaml for a metrics dashboard
├── mcp-agent/          → Python agent calling a compiled MCP server
└── real-life/
    ├── github_issue_creator.yaml   → Login + create issue on GitHub
    ├── stripe_checkout.yaml        → Fill Stripe payment form
    └── hackernews_searcher.yaml    → Search HN via compiled action
```

---

## vs. Everything Else

| | Playwright | Selenium | Browser Use | Shiny Fishstick |
|---|:---:|:---:|:---:|:---:|
| Semantic action layer | ❌ | ❌ | Partial | ✅ |
| SDK generation | ❌ | ❌ | ❌ | ✅ |
| MCP server generation | ❌ | ❌ | ❌ | ✅ |
| OpenAPI export | ❌ | ❌ | ❌ | ✅ |
| Self-healing selectors | ❌ | ❌ | ❌ | ✅ |
| Workflow graph | ❌ | ❌ | ❌ | ✅ |
| API upgrade engine | ❌ | ❌ | ❌ | ✅ |

**Playwright** is a great browser control library. Shiny Fishstick sits on top of it to add a compilation and abstraction layer.

**Browser Use / Computer Use** works by having an LLM look at screenshots and decide what to click. High token overhead, non-deterministic. Shiny Fishstick compiles the site upfront so execution is deterministic and cheap.

**Selenium** is for testing. Shiny Fishstick is for agents.

---

## FAQ

**Why not just use Playwright directly?**  
You can, but then you're maintaining CSS selectors manually and paying the full DOM-parsing token tax on every LLM call. Shiny Fishstick compiles the navigation layer once, so agents get typed methods instead of raw locators.

**Can I run this without an LLM API key?**  
Yes. The intent classifier falls back to heuristic DOM analysis when no API key is configured. You can also point it at a local Ollama instance.

**Is auth session data secure?**  
Yes. Captured cookies and localStorage values are encrypted before writing to the database using AES-256 Fernet symmetric encryption.

**What if the website changes?**  
The state reconciler compares selector similarity across environments. When drift is detected, it proposes a healed selector. The chaos monkey suite lets you test how resilient your compiled spec is to layout changes.

**Can I use the compiled spec without the dashboard?**  
Yes, the CLI is fully standalone. The dashboard is optional.

---

## The Vision

We think the agentic web needs a shared action-spec standard — the same way REST APIs needed OpenAPI.

The goal is to build `preflight.yaml` into an open standard:

1. **Spec** — a declarative format for web actions
2. **Compiler** — automated discovery and compilation from any site
3. **Validator** — `shiny validate` enforces correctness
4. **Registry** — eventually, a place where sites publish their own specs

If a site publishes a `preflight.yaml`, any agent can call it natively. No scraping, no guessing, no breakage.

---

## Contributing

Issues, PRs, and feedback welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

If you're building AI agents, browser automation tools, or MCP integrations and hit a limitation — open an issue. That's the most useful contribution right now.

---

## License

Apache 2.0. See [LICENSE](LICENSE).
