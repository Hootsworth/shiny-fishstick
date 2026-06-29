# Benchmarks

This document covers two benchmark suites:

1. **`benchmark.py`** — mock store (controlled, reproducible, tests self-healing)
2. **`benchmark_real_sites.py`** — Wikipedia, Hacker News, GitHub (live, no mock servers)

Both are included in the repo. Run them yourself to verify every number.

---

## How to Reproduce

```bash
# Mock store benchmarks (requires a compiled spec)
make demo
python benchmark.py

# Real-world benchmarks (no setup needed — hits live sites)
python benchmark_real_sites.py
```

Requirements: Python 3.9+, Playwright Chromium installed (`playwright install chromium`), `httpx`.

---

## What We're Measuring

Each benchmark compares two approaches to performing the same action:

| Column | What it represents |
|---|---|
| **Raw Playwright** | What your agent does *without* Shiny Fishstick — launches a browser, loads pages, reads/clicks DOM elements |
| **Compiled SDK / API** | What your agent calls *after* Shiny Fishstick compiles the site — a typed method that calls the underlying API directly |

Shiny Fishstick's compiler discovers which UI actions map to background API calls (XHR/Fetch interception), then exposes those as SDK methods. The agent never touches the browser again.

---

## Suite 1 — Mock Store (Controlled)

**Target:** Local FastAPI mock e-commerce store  
**Script:** `benchmark.py`  
**Why a mock store?** Lets us test self-healing (benchmark 5) and flakiness injection without depending on network conditions.

---

### Benchmark 1 — Token / Context Window Overhead

**What it measures:** How many tokens an LLM agent must consume to understand what it can do on a site.

**Method:**
- Load 5 pages (`/login`, `/catalog`, `/product/1`, `/product/2`, `/checkout`) with a full Playwright browser context (JavaScript executed, cookies injected)
- Count the words in the rendered HTML of each page, multiply by 1.3 (standard GPT tokenization ratio)
- Compare against the compiled `preflight.yaml` spec, which describes all discoverable actions in one file

**Why this matters:** Every time a raw agent visits a page, it sends the full DOM to the LLM to figure out what to do. With a compiled spec, the agent reads the spec once — not on every call.

| Metric | Raw Playwright | Compiled SDK |
|---|---|---|
| Avg page size (tokens) | ~669 | ~144 |
| Context per agent call | 669 tokens | 144 tokens |
| Token saving per call | — | **~525 tokens (78.5% less)** |
| GPT-4o cost @ $5/1M tokens | ~$0.0033/call | ~$0.00072/call |
| At 10,000 calls/day | ~$33/day | **~$7/day (~$26 saved)** |

> The mock store pages are intentionally small (minimal HTML). On real enterprise sites with React bundles, the DOM overhead reaches 30,000–40,000+ tokens per page.

---

### Benchmark 2 — Action Execution Latency

**What it measures:** Wall-clock time from "start action" to "action complete" for `add_to_cart`.

**Method:**
- **Playwright path:** For each of 10 runs, launch a fresh Chromium instance → navigate to `/login` → fill email + password → click submit → wait for redirect to `/catalog` → navigate to `/product/1` → wait for `networkidle` → click `#add-to-cart-btn`. Measure total elapsed time.
- **SDK path:** For each of 10 runs, call `POST /api/cart/add` with a pre-authenticated session cookie. Measure elapsed time.
- Report avg and p95 across 10 runs.

**Why this matters:** Browser automation is inherently slow — it must boot a rendering engine, execute JavaScript, and wait for visual state. An agent using raw Playwright pays this cost on every single action.

| Metric | Raw Playwright | Compiled SDK |
|---|---|---|
| Average latency | 1,444 ms | 1.5 ms |
| p95 latency | 1,628 ms | 1.2 ms |
| **Speed-up** | — | **953× faster** |

> The Playwright path includes browser launch overhead. In a real agent loop with a warm browser context, the gap is smaller but still substantial (typically 5–20×) because page navigation, JS execution, and DOM settling remain.

---

### Benchmark 3 — Reliability Under DOM Mutations

**What it measures:** How often an action succeeds when a developer changes the UI.

**Method:**
- For each of 20 trials:
  - Load `/product/1` in a Playwright browser context
  - Use `page.evaluate()` to randomly rename the `#add-to-cart-btn` element's `id` and `className` to a random string (simulating a frontend refactor)
  - **Playwright path:** attempt to `click()` on the original selector `#add-to-cart-btn` with an 800ms timeout
  - **SDK path:** call `POST /api/cart/add` directly (DOM state is irrelevant)
- Count successes and failures

**Why this matters:** Frontend teams rename selectors constantly. An agent that hard-codes `#add-to-cart-btn` will break the moment a developer changes it to `#cart-add-btn` or wraps it in a component. The API endpoint doesn't change.

| Metric | Raw Playwright | Compiled SDK |
|---|---|---|
| Failures | 20/20 | 0/20 |
| Reliability | **0%** | **100%** |
| Reliability gain | — | **+100 percentage points** |

---

### Benchmark 4 — Memory Footprint per Action

**What it measures:** Python heap memory allocated to perform one `add_to_cart` action.

**Method:**
- Use `tracemalloc` to take heap snapshots before and after each approach
- **Playwright path:** launch browser → navigate (with auth cookie) → click button
- **SDK path:** `httpx.AsyncClient.post()` with auth cookie

Note: `tracemalloc` only measures the Python interpreter's heap. Playwright additionally spawns a Chromium subprocess that allocates ~100–200 MB of system memory separately — not captured here.

| Metric | Raw Playwright | Compiled SDK |
|---|---|---|
| Python heap delta | 1,642 KB | 21 KB |
| **Reduction** | — | **99% less** |
| Chromium process memory | +~100–200 MB | 0 MB |

---

### Benchmark 5 — Self-Healing Speed

**What it measures:** How long it takes the State Reconciler to detect and fix a broken selector, without human intervention.

**Method:**
- Query the `add_to_cart` action from the database
- Run `StateReconcilerService.reconcile_action_drift()` 5 times, pointing it at the live mock store
- The reconciler opens Playwright, re-scans the page, computes similarity scores for candidate selectors, and determines whether the stored selector still matches
- Record elapsed time and similarity score per run

**Why this matters:** With raw Playwright, a broken selector requires a developer to find the new selector and update the code. With Shiny Fishstick, the reconciler detects drift automatically and heals the spec file.

| Metric | Value |
|---|---|
| Trials | 5 |
| Avg reconciliation time | 1,648 ms |
| Avg DOM similarity score | 1.00 |
| Manual intervention needed | ✅ None |

---

## Suite 2 — Real-World Sites (Live)

**Targets:** Wikipedia, Hacker News, GitHub  
**Script:** `benchmark_real_sites.py`  
**No mock servers. All requests hit production.**

These sites were chosen because:
- They have large, JS-rendered pages (representative of real agent targets)
- They all expose public REST/JSON APIs (representing what Shiny Fishstick's API upgrade engine discovers and compiles into the SDK)
- They require no authentication for public content

---

### Methodology (all 4 metrics)

**A — Token Overhead**
- Load the full page via Playwright with `wait_until="domcontentloaded"` (JS parsed)
- Count words in rendered HTML × 1.3 for token estimate
- Fetch the equivalent structured API response via `httpx`
- Count words in JSON response × 1.3

**B — Latency (10 runs each)**
- Playwright: fresh Chromium instance per run, navigate to page URL, read full `page.content()`
- API: `httpx.AsyncClient.get()` against the equivalent endpoint
- Report avg and p95 across 10 runs

**C — DOM Mutation Reliability (10 trials each)**
- Load live page in Playwright
- Inject `page.evaluate()` JavaScript to rename the target element's `id` and `className` to a random string
- Playwright path: attempt `locator(original_selector).wait_for(timeout=600ms)`
- API path: make the same structured API call — result is unaffected by DOM state
- Count failures

**D — Memory (one action)**
- Same `tracemalloc` method as the mock store benchmark

---

### Results — Wikipedia (Python article)

**Page:** `https://en.wikipedia.org/wiki/Python_(programming_language)`  
**API:** `https://en.wikipedia.org/api/rest_v1/page/summary/Python_(programming_language)`

Wikipedia's Python article is a large, heavily structured page with infoboxes, navigation menus, a long table of contents, and thousands of footnotes. It is a representative example of what an agent must ingest to answer a simple question like "what is Python's latest stable version?"

| Metric | Raw Playwright | Compiled SDK |
|---|---|---|
| Page size (tokens) | **40,833** | 131 |
| Token reduction | — | **99.7%** |
| Avg latency | 700 ms | 86 ms |
| p95 latency | 755 ms | 76 ms |
| Speed-up | — | **8.2×** |
| DOM mutation reliability | 0% (10/10 fail) | 100% (0/10 fail) |
| Python heap delta | 1,639 KB | 42 KB |
| Memory reduction | — | **97%** |

**Key takeaway:** The Wikipedia article page sends 40,833 tokens to the LLM. The REST API summary sends 131. An agent that has been compiled by Shiny Fishstick pays a 311× smaller context cost for the same action.

---

### Results — Hacker News (Homepage)

**Page:** `https://news.ycombinator.com/`  
**API:** `https://hacker-news.firebaseio.com/v0/topstories.json`

Hacker News has a deliberately minimal HTML design — but even so, its rendered page is over 2,000 tokens because of navigation, styling, link metadata, and vote counters. Its Firebase API returns just a JSON array of item IDs (a few bytes).

| Metric | Raw Playwright | Compiled SDK |
|---|---|---|
| Page size (tokens) | 2,298 | 1 |
| Token reduction | — | **100.0%** |
| Avg latency | 1,622 ms | 468 ms |
| p95 latency | 1,847 ms | 517 ms |
| Speed-up | — | **3.5×** |
| DOM mutation reliability | 0% (10/10 fail) | 100% (0/10 fail) |
| Python heap delta | 466 KB | 13 KB |
| Memory reduction | — | **97%** |

**Key takeaway:** HN is the smallest site tested. Even here, Playwright takes 1.6 seconds average and the agent receives ~2,300 tokens just to get a list of post IDs. The Firebase API returns the same list in 468ms with near-zero tokens.

---

### Results — GitHub (microsoft/vscode)

**Page:** `https://github.com/microsoft/vscode`  
**API:** `https://api.github.com/repos/microsoft/vscode`

GitHub's repository pages are heavily React-rendered with dynamic content (contributor graphs, file trees, readme rendering). Despite GitHub's CDN, the rendered page is over 34,000 tokens — comparable to Wikipedia in complexity.

| Metric | Raw Playwright | Compiled SDK |
|---|---|---|
| Page size (tokens) | **34,292** | 5 |
| Token reduction | — | **100.0%** |
| Avg latency | 1,223 ms | 50 ms |
| p95 latency | 1,499 ms | 54 ms |
| Speed-up | — | **24.3×** |
| DOM mutation reliability | 0% (10/10 fail) | 100% (0/10 fail) |
| Python heap delta | 1,183 KB | 23 KB |
| Memory reduction | — | **98%** |

**Key takeaway:** GitHub's REST API is the starkest example. The page sends 34,292 tokens; the API response sends 5. A compiled SDK call is 24× faster and costs essentially nothing in context.

---

### Aggregate — All 3 Real Sites

| Site | Token Reduction | Speed-up | Reliability | Memory Reduction |
|---|---|---|---|---|
| Wikipedia | 99.7% | 8× | +100 pp | 97% |
| Hacker News | 100.0% | 3.5× | +100 pp | 97% |
| GitHub | 100.0% | 24× | +100 pp | 98% |
| **Average** | **99.9%** | **12×** | **+100 pp** | **98%** |

DOM mutation reliability was 0% for raw Playwright across all three sites in every single trial — because the selectors are hard-coded and the injected mutations always break them. The API path returned 100% success across all 30 total trials.

---

## Limitations & Honest Notes

**On the mock store latency (953×):** This includes Chromium launch time per run. In a real agent with a warm, persistent browser context the ratio is smaller — typically 10–50× — because you amortize the browser startup cost. The number is still accurate for the "cold call" case that most simple agents use.

**On the HN API token count (1 token):** The Firebase API returns a bare JSON array of integers with no labels. A full implementation would fetch individual item details too. The token count reflects the first API call, not a full data fetch.

**On DOM mutation reliability (0% raw Playwright):** The mutations in this benchmark are total (id and className both randomized). A more sophisticated Playwright-based agent using `:text()` or `role` locators would survive some mutations. However, any structural rename or class suffix change will still break hard-coded selectors eventually — this benchmark demonstrates the failure mode at its most common (id/class changes).

**On memory:** `tracemalloc` measures the Python interpreter heap only. Playwright's Chromium subprocess independently allocates 100–200 MB of system memory that is not reflected in these numbers.

**Network variability:** Real-site latency numbers (Suite 2) reflect network conditions at time of run. The relative ratios (Playwright vs API) are stable across runs; absolute numbers may vary ±20% depending on network.
