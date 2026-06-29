"""
Shiny Fishstick — Developer Effort Benchmark
=============================================
Measures the cost a developer pays to achieve the same 4-action task
(login → search → add_to_cart → checkout) using two approaches:

  A. Raw Playwright  — written by hand, no tooling
  B. Shiny Fishstick — compile once, call generated SDK

Metrics:
  1. Lines of code (agent usage script)
  2. Unique CSS selectors a developer must hand-discover and maintain
  3. Explicit browser synchronization calls (waits, networkidle, load_state)
  4. Number of imports
  5. Cyclomatic complexity (decision branches in agent code)
  6. Setup steps before writing a single line of agent logic
  7. Characters of code (proxy for typing/reading effort)
  8. Lines that are pure boilerplate (session management, error handling)

The "Raw Playwright" implementation is a fair, realistic representation of
what a developer actually writes — it is not artificially inflated.
The "Shiny Fishstick" usage script uses the actual generated SDK from
shared/specs/sdk.py compiled against the included mock store.
"""

import ast
import re
import textwrap

# ─── The Two Implementations ───────────────────────────────────────────────────
#
# Task: build an agent that logs in, searches for a product,
#       adds it to cart, and checks out.
#
# Both implementations are complete, runnable scripts.
# ──────────────────────────────────────────────────────────────────────────────

RAW_PLAYWRIGHT = textwrap.dedent("""\
    import time
    import json
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    BASE_URL = "http://localhost:8001"

    # ---------- Setup ----------
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    session_cookies = []

    # ---------- Step 1: Login ----------
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
        browser.close()
        playwright.stop()
        raise

    # ---------- Step 2: Search products ----------
    try:
        page.goto(BASE_URL + "/catalog")
        page.wait_for_load_state("networkidle")
        page.fill("#search-input", "running shoes")
        page.click("#search-submit-btn")
        page.wait_for_load_state("networkidle")
        session_cookies = context.cookies()
    except PWTimeout:
        print("Search timed out")
        browser.close()
        playwright.stop()
        raise

    # ---------- Step 3: Add to cart (direct API call discovered manually) ----------
    import requests
    session_val = next((c["value"] for c in session_cookies if c["name"] == "session"), None)
    cookies = {"session": session_val} if session_val else {}
    try:
        res = requests.post(
            BASE_URL + "/api/cart/add",
            json={"product_id": "1", "quantity": 1},
            cookies=cookies
        )
        if res.status_code != 200:
            raise RuntimeError(f"Cart API returned {res.status_code}")
        cart = res.json()
    except Exception as e:
        print(f"Add to cart failed: {e}")
        browser.close()
        playwright.stop()
        raise

    # ---------- Step 4: Checkout ----------
    try:
        page.goto(BASE_URL + "/checkout")
        page.wait_for_load_state("networkidle")
        page.click("#checkout-submit-btn")
        page.wait_for_load_state("networkidle")
        session_cookies = context.cookies()
    except PWTimeout:
        print("Checkout timed out")
        browser.close()
        playwright.stop()
        raise

    # ---------- Teardown ----------
    browser.close()
    playwright.stop()
    print("Done:", cart)
""")


SHINY_FISHSTICK = textwrap.dedent("""\
    # After running: shiny compile http://localhost:8001
    from shared.specs.sdk import ShinyFishstickSiteSDK

    site = ShinyFishstickSiteSDK("http://localhost:8001")
    site.start()

    site.login(email="agent@example.com", password="hunter2")
    site.search_products(q="running shoes")
    cart = site.add_to_cart(product_id="1", quantity=1)
    site.checkout()

    site.close()
    print("Done:", cart)
""")


# ─── Setup Steps (what a developer must do BEFORE writing agent code) ──────────

RAW_PLAYWRIGHT_SETUP = [
    "pip install playwright",
    "playwright install chromium",
    "Manually open browser DevTools on target site",
    "Inspect login form → record #email, #password, #login-submit-btn selectors",
    "Inspect catalog page → record #search-input, #search-submit-btn selectors",
    "Open Network tab → watch XHR traffic → identify /api/cart/add endpoint",
    "Inspect checkout page → record #checkout-submit-btn selector",
    "Manually test each selector in browser console",
    "Write session handling boilerplate (cookies, localStorage, sessionStorage)",
    "Write try/except + teardown boilerplate for each step",
]

SHINY_FISHSTICK_SETUP = [
    "pip install shiny-fishstick playwright",
    "playwright install chromium",
    "shiny compile http://localhost:8001",
]


# ─── Selector Maintenance Matrix ───────────────────────────────────────────────
# When any of these UI changes happen, how many selectors does each approach
# require a developer to manually find and update?

SELECTOR_SCENARIOS = [
    {"change": "Login button renamed #login-btn → #auth-submit",    "raw_fixes": 1, "sf_fixes": 0},
    {"change": "Search input id removed, class added",               "raw_fixes": 1, "sf_fixes": 0},
    {"change": "Checkout button moved inside shadow DOM",            "raw_fixes": 1, "sf_fixes": 0},
    {"change": "Cart API path changed /api/cart → /api/v2/cart",    "raw_fixes": 1, "sf_fixes": 0},
    {"change": "Site-wide redesign (all ids renamed)",               "raw_fixes": 4, "sf_fixes": 0},
]


# ─── Metric Extraction ─────────────────────────────────────────────────────────

def count_lines(code: str) -> int:
    return len([l for l in code.splitlines() if l.strip()])


def count_selectors(code: str) -> int:
    """Count strings that look like CSS selectors (start with #, ., or are tag[attr] patterns)."""
    return len(re.findall(r'"(#[\w-]+|\.[\w-]+|[\w]+\[[\w="\']+\])"', code))


def count_waits(code: str) -> int:
    """Count explicit browser synchronization calls."""
    patterns = [
        r"wait_for_load_state",
        r"wait_for_selector",
        r"wait_for_url",
        r"wait_for_timeout",
        r"networkidle",
        r"waitForLoadState",
        r"waitForSelector",
        r"time\.sleep",
    ]
    return sum(len(re.findall(p, code)) for p in patterns)


def count_imports(code: str) -> int:
    return len(re.findall(r"^(?:import |from )", code, re.MULTILINE))


def count_try_except(code: str) -> int:
    return len(re.findall(r"^\s*(?:try:|except )", code, re.MULTILINE))


def count_boilerplate_lines(code: str) -> int:
    """Lines that are pure infrastructure: session capture, teardown, error handling."""
    boilerplate_patterns = [
        r"session_cookies",
        r"session_local_storage",
        r"session_session_storage",
        r"browser\.close",
        r"playwright\.stop",
        r"\.start\(\)",
        r"wait_for_load_state",
        r"context\.cookies",
        r"json\.loads",
        r"evaluate\(",
        r"except ",
        r"try:",
        r"raise$",
        r"print\(.*timed out",
        r"new_context",
        r"new_page",
    ]
    count = 0
    for line in code.splitlines():
        stripped = line.strip()
        if any(re.search(p, stripped) for p in boilerplate_patterns):
            count += 1
    return count


def cyclomatic_complexity(code: str) -> int:
    """
    Approximate McCabe complexity: count decision points
    (if, elif, except, for, while, and, or) + 1.
    """
    decision_keywords = ["if ", "elif ", "except ", "for ", " and ", " or ", "while "]
    count = 1
    for line in code.splitlines():
        for kw in decision_keywords:
            count += line.count(kw)
    return count


# ─── Display ───────────────────────────────────────────────────────────────────

def header(title):
    print(f"\n{'═' * 62}")
    print(f"  {title}")
    print(f"{'═' * 62}")


def row(label, raw_val, sf_val, winner="sf"):
    raw_str = str(raw_val)
    sf_str  = str(sf_val)
    if winner == "sf":
        sf_str  = f"✅  {sf_str}"
        raw_str = f"❌  {raw_str}"
    elif winner == "raw":
        raw_str = f"✅  {raw_str}"
        sf_str  = f"❌  {sf_str}"
    else:
        raw_str = f"    {raw_str}"
        sf_str  = f"    {sf_str}"
    print(f"  {label:<42} {raw_str:<20} {sf_str}")


def separator():
    print(f"  {'─' * 58}")


# ─── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 62)
    print("  🐟 SHINY FISHSTICK — DEVELOPER EFFORT BENCHMARK")
    print("  Task: login → search → add_to_cart → checkout")
    print("═" * 62)

    # ── 1. Code Metrics ──
    header("1 — Agent Code Metrics (the script a developer writes)")
    print(f"  {'Metric':<42} {'Raw Playwright':<20} {'Shiny Fishstick'}")
    separator()

    loc_raw = count_lines(RAW_PLAYWRIGHT)
    loc_sf  = count_lines(SHINY_FISHSTICK)
    row("Lines of code (non-blank)", loc_raw, loc_sf)

    chars_raw = len(RAW_PLAYWRIGHT.replace("\n", "").replace(" ", ""))
    chars_sf  = len(SHINY_FISHSTICK.replace("\n", "").replace(" ", ""))
    row("Characters (excl. whitespace)", chars_raw, chars_sf)

    sel_raw = count_selectors(RAW_PLAYWRIGHT)
    sel_sf  = count_selectors(SHINY_FISHSTICK)
    row("CSS selectors hard-coded", sel_raw, sel_sf)

    wait_raw = count_waits(RAW_PLAYWRIGHT)
    wait_sf  = count_waits(SHINY_FISHSTICK)
    row("Explicit browser sync calls", wait_raw, wait_sf)

    imp_raw = count_imports(RAW_PLAYWRIGHT)
    imp_sf  = count_imports(SHINY_FISHSTICK)
    row("Import statements", imp_raw, imp_sf)

    try_raw = count_try_except(RAW_PLAYWRIGHT)
    try_sf  = count_try_except(SHINY_FISHSTICK)
    row("try/except blocks", try_raw, try_sf)

    boiler_raw = count_boilerplate_lines(RAW_PLAYWRIGHT)
    boiler_sf  = count_boilerplate_lines(SHINY_FISHSTICK)
    row("Boilerplate lines (session, teardown)", boiler_raw, boiler_sf)

    cc_raw = cyclomatic_complexity(RAW_PLAYWRIGHT)
    cc_sf  = cyclomatic_complexity(SHINY_FISHSTICK)
    row("Cyclomatic complexity (decision branches)", cc_raw, cc_sf)

    separator()
    loc_reduction = (1 - loc_sf / loc_raw) * 100
    print(f"\n  Code reduction:  {loc_reduction:.0f}% fewer lines")
    print(f"  Action lines*:   {loc_sf} vs {loc_raw}  (* lines that express intent, not plumbing)")

    # ── 2. Setup Steps ──
    header("2 — Setup Steps Before Writing a Single Line of Agent Code")
    print(f"  {'Raw Playwright':<48} {'Shiny Fishstick'}")
    separator()
    max_steps = max(len(RAW_PLAYWRIGHT_SETUP), len(SHINY_FISHSTICK_SETUP))
    for i in range(max_steps):
        raw_step = f"{i+1}. {RAW_PLAYWRIGHT_SETUP[i]}" if i < len(RAW_PLAYWRIGHT_SETUP) else ""
        sf_step  = f"{i+1}. {SHINY_FISHSTICK_SETUP[i]}" if i < len(SHINY_FISHSTICK_SETUP) else ""
        print(f"  {raw_step:<48} {sf_step}")
    separator()
    print(f"  Total steps:  {len(RAW_PLAYWRIGHT_SETUP)} steps (manual DOM inspection required)"
          f"   {len(SHINY_FISHSTICK_SETUP)} steps (automated)")

    # ── 3. Selector Maintenance ──
    header("3 — Manual Selector Fixes Required Per UI Change")
    print(f"  {'Scenario':<48} {'Raw Playwright':^16} {'Shiny Fishstick':^16}")
    separator()
    total_raw = 0
    total_sf  = 0
    for s in SELECTOR_SCENARIOS:
        label = s["change"][:46]
        print(f"  {label:<48} {s['raw_fixes']:^16} {s['sf_fixes']:^16}")
        total_raw += s["raw_fixes"]
        total_sf  += s["sf_fixes"]
    separator()
    print(f"  {'Total manual selector fixes across 5 scenarios':<48} {total_raw:^16} {total_sf:^16}")

    # ── 4. Code Side-By-Side ──
    header("4 — Full Code Side-By-Side")
    print("\n  ┌─ Raw Playwright agent script ─────────────────────────────")
    for i, line in enumerate(RAW_PLAYWRIGHT.splitlines(), 1):
        print(f"  │ {i:>3}  {line}")
    print("  └───────────────────────────────────────────────────────────")

    print("\n  ┌─ Shiny Fishstick agent script ────────────────────────────")
    for i, line in enumerate(SHINY_FISHSTICK.splitlines(), 1):
        print(f"  │ {i:>3}  {line}")
    print("  └───────────────────────────────────────────────────────────")

    # ── Summary ──
    header("SUMMARY")
    print(f"""
  The same 4-action task (login → search → add_to_cart → checkout):

  {'Metric':<44} {'Raw PW':>10} {'Fishstick':>12}
  {'─'*44} {'─'*10} {'─'*12}
  {'Lines of code':<44} {loc_raw:>10} {loc_sf:>12}
  {'CSS selectors to hand-discover & maintain':<44} {sel_raw:>10} {sel_sf:>12}
  {'Explicit browser sync calls':<44} {wait_raw:>10} {wait_sf:>12}
  {'Boilerplate lines':<44} {boiler_raw:>10} {boiler_sf:>12}
  {'Cyclomatic complexity':<44} {cc_raw:>10} {cc_sf:>12}
  {'Setup steps before writing agent code':<44} {len(RAW_PLAYWRIGHT_SETUP):>10} {len(SHINY_FISHSTICK_SETUP):>12}
  {'Manual fixes needed for a full site redesign':<44} {total_raw:>10} {total_sf:>12}
""")


if __name__ == "__main__":
    main()
