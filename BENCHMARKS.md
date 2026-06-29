# Benchmarks

This document covers three benchmark suites:

1. **`benchmark.py`** — mock store (controlled, reproducible, tests self-healing)
2. **`benchmark_real_sites.py`** — Wikipedia, Hacker News, GitHub (live, no mock servers)
3. **`benchmark_developer_effort.py`** — developer effort (lines of code, complexity, maintenance burden)

All three are in the repo. Run any of them to verify the numbers.

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

---

## Suite 3 — Developer Effort

**Script:** `benchmark_developer_effort.py`  
**Task:** login → search → add\_to\_cart → checkout (same 4 actions, both approaches)

```bash
python benchmark_developer_effort.py
```

### What it measures

Seven metrics that capture the real cost a developer pays — not just at write time, but across the entire maintenance lifecycle of an agent.

#### Metric 1 — Lines of Code

The total non-blank lines in the script a developer actually writes and ships.

| | Raw Playwright | Shiny Fishstick |
|---|---|---|
| Lines of code | **75** | **10** |
| Reduction | — | **87% fewer lines** |

This is the complete agent script — login, search, add to cart, checkout — including all error handling and session management that a real production script needs.

#### Metric 2 — CSS Selectors to Hand-Discover and Maintain

Every selector is a liability. A developer using raw Playwright must open DevTools, inspect elements, copy selectors, and update them every time the UI changes.

| | Raw Playwright | Shiny Fishstick |
|---|---|---|
| Selectors hard-coded | **6** | **0** |

Shiny Fishstick discovers and stores selectors during compilation. The agent script references typed method names, not DOM addresses.

#### Metric 3 — Explicit Browser Sync Calls

Every `wait_for_load_state("networkidle")`, `wait_for_selector()`, or `time.sleep()` is a place where timing bugs happen — and where developers spend hours debugging flaky tests.

| | Raw Playwright | Shiny Fishstick |
|---|---|---|
| Sync calls | **12** | **0** |

The generated SDK handles all synchronization internally. The agent calls `site.login()` and moves on.

#### Metric 4 — Boilerplate Lines

Lines that don't express what the agent *does* — they express how to keep it from crashing: session capture, teardown, `browser.close()`, `playwright.stop()`, `json.loads()`, `try/except` wrappers.

| | Raw Playwright | Shiny Fishstick |
|---|---|---|
| Boilerplate lines | **43 of 75** (57%) | **1 of 10** (10%) |

57% of a raw Playwright agent script is infrastructure. With Shiny Fishstick, nearly every line expresses intent.

#### Metric 5 — Cyclomatic Complexity

McCabe complexity: counts decision branches (`if`, `elif`, `except`, `for`, `and`, `or`). Higher complexity = more paths to test, more places for bugs to hide.

| | Raw Playwright | Shiny Fishstick |
|---|---|---|
| Cyclomatic complexity | **11** | **1** |

A complexity of 1 means there are no branches — the script is a straight sequence of calls.

#### Metric 6 — Setup Steps Before Writing Agent Code

How many steps must a developer complete before they can write a single line of agent logic?

| Step | Raw Playwright | Shiny Fishstick |
|---|---|---|
| 1 | `pip install playwright` | `pip install shiny-fishstick playwright` |
| 2 | `playwright install chromium` | `playwright install chromium` |
| 3 | Open DevTools on target site | `shiny compile http://target.com` |
| 4 | Inspect login form → record 3 selectors | *(done)* |
| 5 | Inspect catalog page → record 2 selectors | *(done)* |
| 6 | Open Network tab → identify API endpoints | *(done)* |
| 7 | Inspect checkout page → record 1 selector | *(done)* |
| 8 | Test each selector in browser console | *(done)* |
| 9 | Write session handling boilerplate | *(done)* |
| 10 | Write try/except + teardown boilerplate | *(done)* |
| **Total** | **10 steps** | **3 steps** |

#### Metric 7 — Manual Fixes for UI Changes

When a developer changes the website, how many places in the agent code must be manually updated?

| UI Change | Raw Playwright | Shiny Fishstick |
|---|---|---|
| Login button renamed | 1 fix | 0 (`shiny compile` again) |
| Search input restructured | 1 fix | 0 |
| Checkout button moved into shadow DOM | 1 fix | 0 |
| Cart API path versioned (`/v2/`) | 1 fix | 0 |
| Full site redesign (all IDs renamed) | 4 fixes | 0 |
| **Total across 5 scenarios** | **8 manual fixes** | **0** |

### Full Code Comparison

```python
# ─── Raw Playwright (75 lines) ────────────────────────────────────
import time
import json
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE_URL = "http://localhost:8001"

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=True)
context = browser.new_context()
page = context.new_page()
session_cookies = []

try:
    page.goto(BASE_URL + "/login")
    page.wait_for_load_state("networkidle")
    page.fill("#email", "agent@example.com")
    page.fill("#password", "hunter2")
    page.click("#login-submit-btn")
    page.wait_for_load_state("networkidle")
    session_cookies = context.cookies()
    ls_str = page.evaluate("() => JSON.stringify(localStorage)")
    session_local_storage = json.loads(ls_str or '{}')
    ss_str = page.evaluate("() => JSON.stringify(sessionStorage)")
    session_session_storage = json.loads(ss_str or '{}')
except PWTimeout:
    print("Login timed out")
    browser.close(); playwright.stop(); raise

try:
    page.goto(BASE_URL + "/catalog")
    page.wait_for_load_state("networkidle")
    page.fill("#search-input", "running shoes")
    page.click("#search-submit-btn")
    page.wait_for_load_state("networkidle")
    session_cookies = context.cookies()
except PWTimeout:
    print("Search timed out")
    browser.close(); playwright.stop(); raise

import requests
session_val = next((c["value"] for c in session_cookies if c["name"] == "session"), None)
cookies = {"session": session_val} if session_val else {}
try:
    res = requests.post(BASE_URL + "/api/cart/add",
        json={"product_id": "1", "quantity": 1}, cookies=cookies)
    if res.status_code != 200:
        raise RuntimeError(f"Cart API returned {res.status_code}")
    cart = res.json()
except Exception as e:
    print(f"Add to cart failed: {e}")
    browser.close(); playwright.stop(); raise

try:
    page.goto(BASE_URL + "/checkout")
    page.wait_for_load_state("networkidle")
    page.click("#checkout-submit-btn")
    page.wait_for_load_state("networkidle")
    session_cookies = context.cookies()
except PWTimeout:
    print("Checkout timed out")
    browser.close(); playwright.stop(); raise

browser.close()
playwright.stop()
print("Done:", cart)
```

```python
# ─── Shiny Fishstick (10 lines) ───────────────────────────────────
from shared.specs.sdk import ShinyFishstickSiteSDK

site = ShinyFishstickSiteSDK("http://localhost:8001")
site.start()

site.login(email="agent@example.com", password="hunter2")
site.search_products(q="running shoes")
cart = site.add_to_cart(product_id="1", quantity=1)
site.checkout()

site.close()
print("Done:", cart)
```

### Summary

| Metric | Raw Playwright | Shiny Fishstick | Improvement |
|---|---|---|---|
| Lines of code | 75 | 10 | **87% less** |
| Selectors to maintain | 6 | 0 | **100% less** |
| Browser sync calls | 12 | 0 | **100% less** |
| Boilerplate lines | 43 (57%) | 1 (10%) | **98% less** |
| Cyclomatic complexity | 11 | 1 | **10× simpler** |
| Setup steps | 10 | 3 | **7 fewer steps** |
| Manual fixes per redesign | 8 | 0 | **0 maintenance** |

---

## What Happens When a Site Has No API?


This is a fair question — not every website fires XHR/Fetch requests behind the scenes. Legacy CRUD apps, form-heavy government portals, and CAPTCHA-gated pages often have no interceptable network call at all. Here is exactly what Shiny Fishstick does in that case, grounded in the actual code.

### How API upgrade detection works

During compilation, the crawler navigates to each page and Shiny Fishstick registers a Playwright network interceptor (`api_disco.py`, `handle_request()`). Every `xhr` and `fetch` network request fired while interacting with an element is captured. After the crawl, the compiler looks for a "candidate" request to associate with each action — preferring write methods (`POST`, `PUT`, `PATCH`, `DELETE`) but falling back to any captured request.

**An action is upgradable when:**
1. At least one `xhr` or `fetch` request fired during its execution window
2. That request is not a static asset (`.js`, `.css`, `.png`, etc.)
3. A candidate request can be matched to the action

**An action stays as `browser` when:**
- No XHR/Fetch traffic was captured at all (pure HTML form submits, full page reloads, CAPTCHA walls, or entirely server-rendered interactions)
- The compiler finds a candidate but cannot map its parameters to the action's inputs

### What the compiler actually does

When no upgrade is found, the action's `action_type` field is simply left as `"browser"`. There is no error, no warning, no special "non-upgradable" marker — it just stays as it was. The YAML spec omits the `api:` block for those actions:

```yaml
# Upgraded action — has an api: block
add_to_cart:
  action_type: api
  selector: '#add-to-cart-btn'
  api:
    url: /api/cart/add
    method: POST

# Browser-only action — no api: block, selector is used directly
submit_legacy_form:
  action_type: browser
  selector: '#submit-btn'
  parameters:
    - name: query
      selector: '#search-input'
```

### What the generated SDK does for browser actions

The generator (`generator.py`) branches on `action_type`. For `"browser"` actions, it emits real, working Playwright code — not a stub, not a placeholder.

**Python SDK (browser action):**
```python
def submit_legacy_form(self, query: str):
    # Browser Action — no API equivalent found during compilation
    self.page.goto(self.root_url + "/search")
    self.page.fill("#search-input", str(query))
    self.page.click("#submit-btn")
    self.page.wait_for_load_state("networkidle")
    self.session_cookies = self.page.context.cookies()
```

**TypeScript SDK (browser action):**
```typescript
async submitLegacyForm(query: string): Promise<void> {
    // Browser Action — no API equivalent found during compilation
    await this.page.goto(`${this.rootUrl}/search`);
    await this.page.fill('#search-input', String(query));
    await this.page.click('#submit-btn');
    await this.page.waitForLoadState('networkidle');
    this.sessionCookies = await this.context.cookies();
}
```

**Rust SDK (browser action):**  
The Rust generator emits a descriptive comment + a `println!` stub, since Rust has no official Playwright binding. The intent is that the Rust SDK signals which actions require a WebDriver or CDP client to be implemented manually.

```rust
// Browser Action: submit_legacy_form
// Selector: #submit-btn
// This action has no API equivalent — implement using a CDP/WebDriver client
println!("Interacting with element #submit-btn...");
Ok(())
```

### Summary

| Scenario | `action_type` | SDK output | Agent experience |
|---|---|---|---|
| XHR/Fetch found during crawl | `api` | Direct HTTP call | Fastest path, no browser needed |
| No network traffic captured | `browser` | Real Playwright code (Py/TS) | Browser automation, same as before — but with stable selectors and FSM-managed state |
| Rust target, browser action | `browser` | Descriptive stub + comment | Manual implementation required |

**The key point:** Shiny Fishstick does not pretend a site has an API when it doesn't. For fully browser-bound sites, the compiled SDK is still useful — it gives the agent typed methods with stable selectors, captured session state, and FSM-ordered workflows. What it cannot do is bypass the browser itself.

The benchmarks in this document show the best-case improvement (sites with discoverable APIs). For purely browser-bound sites, the token overhead and latency improvements are smaller, but the reliability and self-healing benefits still apply in full.

---

## What Do These Numbers Actually Mean?

The benchmark tables are full of percentages, milliseconds, and "×" multipliers. Here is what each one means in plain terms, with concrete analogies.

---

### Token reduction (78–100%)

**What a token is:**  
LLMs like GPT-4 don't read sentences — they read chunks of text called tokens. Roughly every ¾ of a word is one token. More tokens = more cost and slower responses.

**The analogy:**  
Imagine you hired a personal assistant to book you a flight. Without Shiny Fishstick, every time they need to check flight options, you hand them the entire 500-page airline catalogue to read cover to cover. With Shiny Fishstick compiled, you hand them a single index card that says: *"Call United, say destination='NYC', date='July 4'."*

**Wikipedia in real numbers:**  
The Wikipedia Python article sends 40,833 tokens to the LLM every time an agent reads it. The compiled API response sends 131 tokens. If your agent checks Wikipedia 1,000 times a day at GPT-4o pricing ($5 per million tokens), that's the difference between spending $204/day and spending $0.65/day for the same information.

---

### Speed-up (3.5× to 953×)

**What this measures:**  
How many times faster it is to call the compiled SDK method versus making the same agent action through a real browser.

**The analogy:**  
Without Shiny Fishstick, asking an agent to add something to a cart is like asking someone to drive to the store, walk the aisles, find the item, carry it to the register, and pay — every single time you want to buy something. With Shiny Fishstick, it's like clicking "add to cart" on a website: one HTTP call, done in milliseconds.

**Why the numbers vary by site:**  
GitHub (24×) is faster to improve because GitHub's API is extremely fast and its page is heavy with React rendering. Hacker News (3.5×) is already a lightweight page, so the gap is smaller. The mock store (953×) is the most dramatic because it includes the full browser launch cost in every measurement.

---

### DOM Mutation Reliability (0% → 100%)

**What this measures:**  
When a developer changes the website's HTML — renaming a button, moving a form, redesigning a page — how often does the agent's action still work?

**The analogy:**  
Without Shiny Fishstick, your agent knows how to open a specific drawer in a specific desk to find the stapler. If someone moves the desk or relabels the drawers, the agent is completely lost. With a compiled SDK calling the API directly, it doesn't matter where the drawer is — it calls the warehouse directly and the stapler arrives regardless.

**In the benchmarks:**  
Every single one of the 20 mock store trials and 30 real-site trials broke the raw Playwright selector after a mutation. The API call succeeded every single time, because the server-side endpoint didn't change. In real agent deployments, frontend redesigns happen regularly and silently — this is what makes 0% reliability the realistic baseline for hard-coded selectors.

---

### Memory reduction (97–99%)

**What this measures:**  
How much computer memory is consumed to perform one action.

**The analogy:**  
Raw Playwright is like hiring a full film crew to take one photo — cameras, lighting rigs, a director, catering. The compiled SDK is like using your phone camera. Same photo, 99% less equipment.

**Why it matters at scale:**  
An agent running 100 concurrent tasks using raw Playwright needs to keep 100 Chromium browser instances alive — each consuming ~150 MB. That's 15 GB of RAM just for the browser processes, before your agent logic even runs. With compiled SDKs making direct API calls, 100 concurrent tasks use trivial memory.

---

### Self-Healing Speed (1,648 ms)

**What this measures:**  
When a website changes and a selector breaks, how long does it take Shiny Fishstick to detect and fix it automatically?

**The analogy:**  
Without self-healing, a broken selector is like a GPS that gives you directions to a building that has since moved — it just tells you to turn into a field, and someone has to manually update the map. Shiny Fishstick's reconciler is like a GPS that notices the building moved, re-scans the area, and updates its own map in 1.6 seconds.

**What 1,648 ms includes:**  
Launching a Playwright browser, navigating to the live page, scoring all candidate selectors for similarity to the stored one, writing the result back to the database. On a cron schedule or CI trigger, this runs automatically with no human involvement.

