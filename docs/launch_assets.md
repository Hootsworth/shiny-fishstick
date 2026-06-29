# Shiny Fishstick Launch Assets 🚀

This document compiles marketing, blog posts, and release copy to announce **Shiny Fishstick v0.1.0-alpha** to the open-source web and developer communities.

---

## 📝 Blog Post
**Title**: OpenAPI for websites: compiling browser workflows for agents.

Every AI browser agent begins its journey with a simple goal: *"Buy a pair of red running shoes."*

But as the agent descends into the raw DOM of modern web applications, the dream quickly turns into a nightmare. It encounters nested shadow DOMs, randomized Tailwind CSS classes, dynamic overlays, and cookie redirects. To click a button, the agent pays a heavy context window tax, sending megabytes of raw HTML and screenshots back and forth to an LLM. And if a selector changes next Tuesday? The agent crashes.

**Shiny Fishstick** is the compiler that changes this paradigm.

Instead of forcing browser agents to reason over raw web layouts ad-hoc, Shiny Fishstick pre-compiles any web page into a structured, semantic action layer: **OpenAPI but for human-centric websites**.

### How it Works:
1.  **The Crawler** performs a fast, BFS-based traversal, resolving login redirects and session configurations.
2.  **The Analyzer** extracts all forms, interactive elements, and input selectors.
3.  **The Spec compiler** outputs a clean, language-agnostic `preflight.yaml` definition.
4.  **The Code Generator** creates clean, type-safe Python/TypeScript/Rust client SDKs and Model Context Protocol (MCP) server scripts out-of-the-box.

---

## 🎪 Show HN Pitch
**Title**: Show HN: Shiny Fishstick – Compile any website into a semantic SDK for AI agents

Hey HN,

We are building Shiny Fishstick, an open-source tool that turns websites into agent-callable action specifications.

We love Playwright, but it gives low-level browser control. When browser agents use it, they spend massive amounts of context tokens reasoning over raw elements. 

Shiny Fishstick solves this by compiling websites. It crawls the page, discovers forms, buttons, and workflows, and outputs a semantic `preflight.yaml` spec. It then generates Python/TypeScript SDKs and starts a Model Context Protocol (MCP) server out-of-the-box.

Instead of an agent reasoning over selectors, it simply calls `add_to_cart(product_id, quantity)`.

We support a zero-config SQLite mode, automatic session capture, and a clean local Next.js workspace dashboard to preview and test workflows.

Repo: https://github.com/Hootsworth/shiny-fishstick
Feedback and contributions are welcome!

---

## 👽 Reddit Announcement (`r/LocalLLaMA`, `r/Python`)
**Title**: [OS] Shiny Fishstick: Compile any website into a Model Context Protocol (MCP) server for browser agents

Hi everyone,

I wanted to share Shiny Fishstick, an open-source compiler that helps AI agents interact with web pages without paying the heavy DOM-context tax.

It compiles website flows into structured `preflight.yaml` specifications. From there, you get:
*   Python/TypeScript/Rust client SDKs.
*   A standalone Model Context Protocol (MCP) tool server to plug directly into LLM agent loops.
*   Cross-environment layout drift checks to heal selectors when site changes happen.

It’s open source under Apache-2.0. Check out the setup steps:
```bash
git clone git@github.com:Hootsworth/shiny-fishstick.git
make setup
make demo
```

Check it out and let me know what you think!

---

## 🐦 X / Twitter Announcement
> 🐟 Introducing Shiny Fishstick: Compile any website into a semantic SDK & Model Context Protocol (MCP) server for browser agents.
> 
> Stop forcing LLMs to parse raw HTML and shadow DOMs. Compile actions once, let agents execute them at native speeds.
> 
> 📦 Zero-config SQLite default
> 🔌 Instant MCP tool serving
> 🧪 Interactive dashboard
> 
> Check out the repo: https://github.com/Hootsworth/shiny-fishstick
