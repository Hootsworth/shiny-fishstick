"""
Shiny Fishstick — Real-World Benchmark Suite
=============================================
Tests across 3 real public websites:
  1. Wikipedia     (large article pages vs REST summary API)
  2. Hacker News   (rendered homepage vs Firebase JSON API)
  3. GitHub        (repo page vs GitHub REST API)

For each site we measure:
  A. Token overhead  — full rendered HTML vs structured API response
  B. Action latency  — Playwright page load vs direct API call (10 runs each)
  C. DOM flakiness   — mutate a real selector, test raw Playwright vs API fallback
  D. Memory          — Python heap delta for each approach

This mirrors what Shiny Fishstick's compiler produces:
  - The "Playwright" column = what your agent does WITHOUT Shiny Fishstick
  - The "API" column       = what your agent calls AFTER Shiny Fishstick compiles the site

No auth, no accounts. All endpoints are public.
"""

import asyncio
import statistics
import time
import tracemalloc

import httpx
from playwright.async_api import async_playwright

REPEAT = 10

# ─── Helpers ───────────────────────────────────────────────────────────────────

def words_to_tokens(word_count: int) -> int:
    """Approximate GPT token count from word count (ratio ~1.3)."""
    return int(word_count * 1.3)


def header(title):
    print(f"\n{'═' * 64}")
    print(f"  {title}")
    print(f"{'═' * 64}")


def site_header(name, url):
    print(f"\n  ┌─ {name}")
    print(f"  │  {url}")
    print(f"  └{'─' * 58}")


def row(label, value, indent=4):
    print(f"{' ' * indent}{label:<44} {value}")


def separator(indent=4):
    print(f"{' ' * indent}{'─' * 58}")


# ─── Site Definitions ──────────────────────────────────────────────────────────

SITES = [
    {
        "name": "Wikipedia",
        "description": "Python article",
        "page_url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "api_url": "https://en.wikipedia.org/api/rest_v1/page/summary/Python_(programming_language)",
        "api_label": "REST Summary API",
        "mutation_selector": "#firstHeading",
        "mutation_target": "#firstHeading h1",
    },
    {
        "name": "Hacker News",
        "description": "Homepage",
        "page_url": "https://news.ycombinator.com/",
        "api_url": "https://hacker-news.firebaseio.com/v0/topstories.json?limitToFirst=10&orderBy=%22$key%22",
        "api_label": "Firebase JSON API",
        "mutation_selector": ".hnname",
        "mutation_target": ".hnname a",
    },
    {
        "name": "GitHub",
        "description": "microsoft/vscode repo",
        "page_url": "https://github.com/microsoft/vscode",
        "api_url": "https://api.github.com/repos/microsoft/vscode",
        "api_label": "GitHub REST API",
        "mutation_selector": "#repository-container-header",
        "mutation_target": "strong[itemprop='name']",
    },
]


# ─── A. Token Overhead ─────────────────────────────────────────────────────────

async def bench_tokens(site: dict, page) -> tuple[int, int]:
    """Returns (html_tokens, api_tokens)."""
    await page.goto(site["page_url"], wait_until="domcontentloaded", timeout=30000)
    html = await page.content()
    html_tokens = words_to_tokens(len(html.split()))

    async with httpx.AsyncClient(
        headers={"User-Agent": "shiny-fishstick-benchmark/1.0"},
        timeout=15.0
    ) as client:
        resp = await client.get(site["api_url"])
        api_tokens = words_to_tokens(len(resp.text.split()))

    return html_tokens, api_tokens


# ─── B. Action Latency ─────────────────────────────────────────────────────────

async def bench_latency(site: dict) -> tuple[list[float], list[float]]:
    """Returns (playwright_times_ms, api_times_ms) for REPEAT runs each."""
    pw_times = []
    async with async_playwright() as p:
        for _ in range(REPEAT):
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            t0 = time.perf_counter()
            await page.goto(site["page_url"], wait_until="domcontentloaded", timeout=30000)
            _ = await page.content()  # force full read — simulates what an agent does
            pw_times.append((time.perf_counter() - t0) * 1000)
            await browser.close()

    api_times = []
    async with httpx.AsyncClient(
        headers={"User-Agent": "shiny-fishstick-benchmark/1.0"},
        timeout=15.0
    ) as client:
        for _ in range(REPEAT):
            t0 = time.perf_counter()
            await client.get(site["api_url"])
            api_times.append((time.perf_counter() - t0) * 1000)

    return pw_times, api_times


# ─── C. DOM Flakiness ──────────────────────────────────────────────────────────

FLAKE_RUNS = 10

async def bench_flakiness(site: dict) -> tuple[int, int]:
    """Returns (pw_failures, api_failures) out of FLAKE_RUNS trials."""
    pw_failures = 0
    api_failures = 0

    async with async_playwright() as p:
        for _ in range(FLAKE_RUNS):
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(site["page_url"], wait_until="domcontentloaded", timeout=30000)

            original_sel = site["mutation_selector"]

            # Inject a class mutation to simulate a UI redesign
            await page.evaluate(f"""() => {{
                const el = document.querySelector('{original_sel}');
                if (el) {{
                    el.className = 'chaos-mutated-' + Math.random().toString(36).slice(2, 6);
                    el.id = 'chaos-mutated-' + Math.random().toString(36).slice(2, 6);
                }}
            }}""")

            try:
                # Raw Playwright: try to find the element by its original selector
                await page.locator(original_sel).wait_for(timeout=600)
            except Exception:
                pw_failures += 1

            await browser.close()

    # API path: completely unaffected by DOM changes
    async with httpx.AsyncClient(
        headers={"User-Agent": "shiny-fishstick-benchmark/1.0"},
        timeout=15.0
    ) as client:
        for _ in range(FLAKE_RUNS):
            try:
                resp = await client.get(site["api_url"])
                if resp.status_code not in (200, 201):
                    api_failures += 1
            except Exception:
                api_failures += 1

    return pw_failures, api_failures


# ─── D. Memory ─────────────────────────────────────────────────────────────────

async def bench_memory(site: dict) -> tuple[float, float]:
    """Returns (pw_kb, api_kb) Python heap deltas."""
    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(site["page_url"], wait_until="domcontentloaded", timeout=30000)
        _ = await page.content()
        await browser.close()
    after_pw = tracemalloc.take_snapshot()
    tracemalloc.stop()
    pw_kb = sum(s.size_diff for s in after_pw.compare_to(before, "lineno") if s.size_diff > 0) / 1024

    tracemalloc.start()
    before = tracemalloc.take_snapshot()
    async with httpx.AsyncClient(
        headers={"User-Agent": "shiny-fishstick-benchmark/1.0"},
        timeout=15.0
    ) as client:
        await client.get(site["api_url"])
    after_api = tracemalloc.take_snapshot()
    tracemalloc.stop()
    api_kb = sum(s.size_diff for s in after_api.compare_to(before, "lineno") if s.size_diff > 0) / 1024

    return pw_kb, api_kb


# ─── Aggregate Summary ─────────────────────────────────────────────────────────

def print_summary(results: list[dict]):
    header("AGGREGATE SUMMARY — All 3 Real Sites")

    print(f"\n  {'Site':<20} {'Token Reduction':>16} {'Latency Speed-up':>18} {'Reliability':>13} {'Memory Reduction':>18}")
    print(f"  {'─'*20} {'─'*16} {'─'*18} {'─'*13} {'─'*18}")
    for r in results:
        tok_pct = f"{r['token_reduction']:.1f}%"
        speedup = f"{r['speedup']:.0f}×"
        reliability = f"+{r['reliability_gain']:.0f} pp"
        mem = f"{r['memory_reduction']:.0f}%"
        print(f"  {r['name']:<20} {tok_pct:>16} {speedup:>18} {reliability:>13} {mem:>18}")

    # Averages
    print(f"  {'─'*20} {'─'*16} {'─'*18} {'─'*13} {'─'*18}")
    avg_tok  = statistics.mean(r["token_reduction"]   for r in results)
    avg_spd  = statistics.mean(r["speedup"]           for r in results)
    avg_rel  = statistics.mean(r["reliability_gain"]  for r in results)
    avg_mem  = statistics.mean(r["memory_reduction"]  for r in results)
    print(f"  {'AVERAGE':<20} {f'{avg_tok:.1f}%':>16} {f'{avg_spd:.0f}×':>18} {f'+{avg_rel:.0f} pp':>13} {f'{avg_mem:.0f}%':>18}")
    print()


# ─── Main ───────────────────────────────────────────────────────────────────────

async def main():
    print("\n" + "═" * 64)
    print("  🐟 SHINY FISHSTICK — REAL-WORLD BENCHMARK")
    print("  Wikipedia · Hacker News · GitHub")
    print("  All numbers are live — no mock servers")
    print("═" * 64)

    all_results = []

    for site in SITES:
        header(f"SITE: {site['name'].upper()} — {site['description']}")

        # A. Tokens
        print(f"\n  [A] Token / Context Overhead")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            html_tokens, api_tokens = await bench_tokens(site, page)
            await browser.close()
        token_reduction = (1 - api_tokens / html_tokens) * 100
        row("Full rendered page (tokens ~):", f"{html_tokens:,}")
        row(f"API response [{site['api_label']}] (tokens ~):", f"{api_tokens:,}")
        row("Token reduction:", f"{token_reduction:.1f}%")

        # B. Latency
        print(f"\n  [B] Action Latency ({REPEAT} runs each)")
        pw_times, api_times = await bench_latency(site)
        pw_avg = statistics.mean(pw_times)
        pw_p95 = sorted(pw_times)[int(REPEAT * 0.95) - 1]
        api_avg = statistics.mean(api_times)
        api_p95 = sorted(api_times)[int(REPEAT * 0.95) - 1]
        speedup = pw_avg / api_avg
        row("Playwright — avg / p95:", f"{pw_avg:.0f} ms  /  {pw_p95:.0f} ms")
        row("API call   — avg / p95:", f"{api_avg:.0f} ms  /  {api_p95:.0f} ms")
        row("Speed-up:", f"{speedup:.1f}×  faster")

        # C. Flakiness
        print(f"\n  [C] DOM Mutation Reliability ({FLAKE_RUNS} trials each)")
        pw_fail, api_fail = await bench_flakiness(site)
        pw_rel = ((FLAKE_RUNS - pw_fail) / FLAKE_RUNS) * 100
        api_rel = ((FLAKE_RUNS - api_fail) / FLAKE_RUNS) * 100
        reliability_gain = api_rel - pw_rel
        row("Playwright — failures / reliability:", f"{pw_fail}/{FLAKE_RUNS}  ({pw_rel:.0f}%)")
        row("API call   — failures / reliability:", f"{api_fail}/{FLAKE_RUNS}  ({api_rel:.0f}%)")
        row("Reliability gain:", f"+{reliability_gain:.0f} percentage points")

        # D. Memory
        print(f"\n  [D] Python Heap Delta (one action)")
        pw_kb, api_kb = await bench_memory(site)
        mem_reduction = (1 - api_kb / pw_kb) * 100 if pw_kb > 0 else 0
        row("Playwright heap delta:", f"{pw_kb:.0f} KB")
        row("API call heap delta:", f"{api_kb:.0f} KB")
        row("Memory reduction:", f"{mem_reduction:.0f}%")

        all_results.append({
            "name": site["name"],
            "token_reduction": token_reduction,
            "speedup": speedup,
            "reliability_gain": reliability_gain,
            "memory_reduction": mem_reduction,
        })

    print_summary(all_results)
    print("  Note: 'API call' column represents what Shiny Fishstick exposes as the compiled SDK.")
    print("  Playwright column = what your agent does without Shiny Fishstick.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
