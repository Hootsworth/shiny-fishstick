import subprocess
import sys
import time

import pytest
import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


@pytest.fixture(scope="module")
def mock_store_server_saas():
    print("Starting Mock Store on port 8004...")
    mock_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.mock_site.main:app", "--port", "8004"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    try:
        requests.get("http://localhost:8004/login")
    except Exception as e:
        mock_proc.terminate()
        raise RuntimeError("Could not start mock store on port 8004") from e

    yield "http://localhost:8004"

    mock_proc.terminate()


@pytest.mark.anyio
async def test_saas_dashboard_metrics_and_search_integration(mock_store_server_saas):
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Login to establish authenticated session cookies
        await page.goto(f"{mock_store_server_saas}/login")
        await page.locator("#email").fill("admin@example.com")
        await page.locator("#password").fill("password123")
        await page.locator("#login-submit-btn").click()
        await page.wait_for_load_state("networkidle")

        # 1. Access SaaS dashboard page
        await page.goto(f"{mock_store_server_saas}/saas")
        assert await page.locator("#saas-metrics-table").count() == 1
        assert "ACTIVE CONNECTIONS" in await page.inner_text("#saas-metrics-table")

        # 2. Access Index Search Page
        await page.goto(f"{mock_store_server_saas}/search")
        assert await page.locator("#paginated-results-table").count() == 1

        # Test table search filter action
        await page.locator("#search-query-val").fill("Beta")
        await page.locator("#search-filter-submit-btn").click()
        await page.wait_for_load_state("networkidle")

        # Verify only Beta element row remains in results
        results_text = await page.inner_text("#paginated-results-table")
        assert "Beta" in results_text
        assert "Alpha" not in results_text

        await browser.close()
