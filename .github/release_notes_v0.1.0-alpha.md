# 🐟 Shiny Fishstick v0.1.0-alpha

> **Compile websites into semantic SDKs and MCP servers for AI agents.**

This is the first public alpha release of Shiny Fishstick. It is early, intentionally rough around some edges, and ready for feedback from people building AI agents, browser automation tooling, or MCP integrations.

---

## What's in this release

### Core compiler pipeline
- **BFS Crawler** — traverses websites, handles auth redirects and session state (cookies, localStorage, sessionStorage)
- **DOM Analyzer** — heuristic selector scoring (`data-testid` > `id` > `name` > `class` > `xpath`) for stable element targeting
- **Intent Classifier** — maps UI elements to semantic action names via LLM or offline heuristics (Ollama compatible)
- **API Upgrade Engine** — intercepts XHR/Fetch traffic during crawl; upgrades browser actions to direct API calls where possible
- **Workflow FSM** — models multi-step action sequences as a Finite State Machine

### Output formats
- `preflight.yaml` — human-readable, version-controllable action spec
- Python SDK (`sdk.py`) — typed methods wrapping Playwright (browser actions) or `requests` (API actions)
- TypeScript SDK (`sdk.ts`) — equivalent using `fetch` and Playwright async API
- Rust SDK (`sdk.rs`) — `reqwest`-based for API actions; stub comments for browser actions
- MCP server (`mcp_server.py`) — JSON-RPC 2.0 stdio server mapping compiled actions to LLM tools
- OpenAPI 3.0 export

### Dashboard (Next.js)
- Projects manager, real-time crawl log feed
- Action Explorer with assertion builder
- FSM visualizer with drag-and-drop step editor
- SDK download center
- Assertions sandbox playground (live Playwright runner with screenshot stream)

### Infrastructure
- Encrypted credentials store (AES-256 Fernet)
- Playwright-stealth integration for bot detection bypass
- iFrame / shadow DOM traversal
- State reconciler — detects selector drift across environments, auto-heals
- Chaos Monkey — DOM mutation + latency injection for resilience testing
- WebSocket agent hub for distributed crawl coordination
- Redis-backed worker autoscaler metrics
- Offline LLM support (Ollama)

### Benchmarks (verified, reproducible)

| Metric | Raw Playwright | Shiny Fishstick |
|---|---|---|
| Token overhead (mock store) | ~669 tokens/call | ~144 tokens/call |
| Action latency | 1,444 ms | 1.5 ms |
| DOM mutation reliability | 0% | 100% |
| Memory per action | 1,642 KB | 21 KB |
| Lines of code (same task) | 75 | 10 |

Real-site results: Wikipedia pages average 40,833 tokens vs 131 via compiled API. GitHub repo pages average 34,292 tokens vs 5. See [BENCHMARKS.md](BENCHMARKS.md) for full methodology.

---

## Known limitations in this alpha

- **Rust SDK** — browser-backed actions emit stub comments only; no Playwright/CDP binding for Rust yet
- **CAPTCHA / full server-render** — actions on pages with no XHR/Fetch traffic stay as `browser` type; API upgrade is not possible
- **Multi-tenant / SSO** — workspace isolation and SSO auth are not implemented yet (roadmap Phase 8)
- **Hosted registry** — the public `preflight.yaml` registry is not live yet
- **Windows** — not tested; known Playwright path issues likely

---

## Getting started

```bash
git clone git@github.com:Hootsworth/shiny-fishstick.git
cd shiny-fishstick
make setup
make demo     # compile a local mock store, verify the full pipeline
```

See [README.md](README.md) for full setup, CLI reference, and examples.

---

## Feedback

This is an alpha. The most useful contributions right now are:

- **Bug reports** — especially against real sites that behave unexpectedly
- **Feature requests** — what's missing for your agent use case?
- **Site reports** — tried compiling a site? Open an issue with what worked and what didn't

Open an issue or start a discussion. Every report helps.
