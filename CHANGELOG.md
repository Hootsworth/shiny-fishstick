# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-alpha] — 2025-06-30

### Added

- **BFS Crawler** with stealth mode, depth tracking, proxy support, and agent-clustered WebSocket mode
- **DOM Analyzer** with heuristic selector scoring (`data-testid > id > class > xpath`)
- **Intent Classifier** — LLM-based (OpenAI / Ollama) with heuristic fallback
- **API Discovery Engine** — intercepts XHR/Fetch traffic and upgrades browser actions to direct API calls
- **Workflow FSM Builder** — models multi-step action sequences as a finite state machine
- **SDK Generator** — outputs Python, TypeScript, and Rust client SDKs
- **MCP Server Generator** — auto-generates a JSON-RPC 2.0 MCP server for LLM tool use
- **OpenAPI Exporter** — compiles discovered endpoints into OpenAPI 3.0 specs
- **`preflight.yaml` spec format** — declarative, version-controllable action schema
- **State Reconciler** — detects selector drift and proposes healed selectors
- **Chaos Monkey** — mutates selectors and injects latency to test self-healing
- **Encrypted credential storage** — AES-256 Fernet symmetric encryption for auth sessions
- **iFrame traversal** — recursive frame scanning with `frame_locator` action generation
- **Next.js Dashboard** — projects, crawl feed, action explorer, FSM visualizer, SDK download
- **CLI** — `shiny compile`, `shiny inspect`, `shiny validate`, `shiny serve-mcp`, `shiny test`
- **Benchmarks** — mock store, real-site, and developer-effort benchmark suites
- **Static documentation site** (`docs/`) with HTTPie-style Flow design system

### Security

- Encrypted credential storage at rest (AES-256 Fernet)
- `SECURITY.md` with vulnerability reporting guidelines
- Dependency updates: Next.js 15.5.19, React 19, postcss 8.5.16 (0 npm audit vulnerabilities)

[0.1.0-alpha]: https://github.com/Hootsworth/shiny-fishstick/releases/tag/v0.1.0-alpha
