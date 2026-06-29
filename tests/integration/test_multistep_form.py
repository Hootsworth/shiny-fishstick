import subprocess
import sys
import time

import pytest
import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


@pytest.fixture(scope="module")
def mock_store_server_multistep():
    print("Starting Mock Store on port 8003...")
    mock_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.mock_site.main:app", "--port", "8003"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    try:
        requests.get("http://localhost:8003/multistep")
    except Exception as e:
        mock_proc.terminate()
        raise RuntimeError("Could not start mock store on port 8003") from e

    yield "http://localhost:8003"

    mock_proc.terminate()


@pytest.mark.anyio
async def test_multistep_form_e2e_navigation(mock_store_server_multistep):
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Load Step 1
        await page.goto(f"{mock_store_server_multistep}/multistep?step=1")
        assert await page.locator("#step1-form").count() == 1

        # Fill Step 1 Contact Info
        await page.locator("#step1-name").fill("Dev Tester")
        await page.locator("#step1-submit-btn").click()
        await page.wait_for_load_state("networkidle")

        # 2. Assert Step 2 is loaded
        assert await page.locator("#step2-form").count() == 1
        await page.locator("#step2-pref").fill("FastAPI")
        await page.locator("#step2-submit-btn").click()
        await page.wait_for_load_state("networkidle")

        # 3. Assert questionnaire completed
        assert "Questionnaire Completed!" in await page.inner_text("#multistep-container")

        await browser.close()
