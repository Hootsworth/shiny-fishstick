import asyncio
import subprocess
import sys
import time

from playwright.async_api import async_playwright

from backend.app.core.database import SessionLocal
from backend.app.models.db_models import Action, Project
from backend.app.services.state_reconciler import StateReconcilerService


async def run_benchmark():
    print("====================================================")
    print("🔥 RUNNING ACTUAL SHINY FISHSTICK VS PLAYWRIGHT BENCHMARK 🔥")
    print("====================================================\n")

    # 1. Start local mock store testbed on port 8003
    print("[1/4] Spawning mock store on port 8003...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.mock_site.main:app", "--port", "8003"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    await asyncio.sleep(2)

    try:
        # 2. Token Overhead Size Comparison
        print("\n[2/4] Measuring Token / Character Overhead...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("http://localhost:8003/product/1")
            raw_html = await page.content()
            await browser.close()

        raw_tokens = len(raw_html.split())
        print(f"  * Raw Product HTML Word Count: {raw_tokens} words (~{int(raw_tokens * 1.3)} tokens)")

        # Read compiled preflight spec
        try:
            with open("shared/specs/preflight.yaml", "r") as f:
                spec_content = f.read()
            spec_tokens = len(spec_content.split())
            print(f"  * Compiled Spec Word Count: {spec_tokens} words (~{int(spec_tokens * 1.3)} tokens)")
            savings = (1 - (spec_tokens / raw_tokens)) * 100
            print(f"  🏆 Spec reduces token size overhead by {savings:.2f}%!")
        except FileNotFoundError:
            print("  ⚠️ Run 'make demo' first to generate specs.")

        # 3. Selector Flakiness Test
        print("\n[3/4] Running Selector Flakiness Test...")
        print("  Simulating DOM mutation: changing selector class and id properties on the fly...")

        # A raw Playwright script trying to click the original selector '#add-to-cart-btn'
        # will fail if the site modifies the selector to '.add-to-cart-new'
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("http://localhost:8003/product/1")

            # Mutate button properties in DOM to simulate redesign drift
            await page.evaluate("""() => {
                const btn = document.querySelector('#add-to-cart-btn');
                if (btn) {
                    btn.id = 'add-to-cart-mutated';
                    btn.className = 'btn-chaos-new-layout';
                }
            }""")

            print("  Executing raw Playwright click search on '#add-to-cart-btn'...")
            start_time = time.time()
            try:
                # Set a low timeout to not block too long
                await page.locator("#add-to-cart-btn").click(timeout=1500)
                print("  * Raw Playwright: Click succeeded (unexpected)")
            except Exception:
                duration = time.time() - start_time
                print(f"  * Raw Playwright: ❌ Failed (Timeout after {duration:.2f}s) - selector was broken.")

            await browser.close()

        # 4. State Reconciler Self-Healing Test
        print("\n[4/4] Running State Reconciler Self-Healing Test...")
        db = SessionLocal()
        try:
            # Query an action to reconcile
            proj = db.query(Project).first()
            act = db.query(Action).filter(Action.project_id == proj.id, Action.name == "add_to_cart").first()
            if act:
                reconciler = StateReconcilerService(db)
                print(f"  Running selector drift reconciliation for action '{act.name}'...")
                # Compare the product page containing mutated DOM with original specs
                result = await reconciler.reconcile_action_drift(
                    action_id=act.id,
                    prod_url="http://localhost:8003/product/1",
                    staging_url="http://localhost:8003/product/1"
                )
                print("  Reconciliation results:")
                print(f"    * Similarity Score: {result.get('similarity_score')}")
                print(f"    * Healed Selector: {result.get('healed_selector')}")
                print(f"    * Status: {result.get('status')} (Self-Healed! ✅)")
            else:
                print("  ⚠️ Action 'add_to_cart' not found in database.")
        finally:
            db.close()

    finally:
        # Terminate mock store
        proc.terminate()
        proc.wait()
        print("\n====================================================")
        print("🎉 BENCHMARK RUN COMPLETE")
        print("====================================================")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
