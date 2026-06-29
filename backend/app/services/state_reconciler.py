import difflib

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from sqlalchemy.orm import Session

from ..models.db_models import Action
from .updater import SpecUpdaterService


class StateReconcilerService:
    def __init__(self, db: Session):
        self.db = db

    async def reconcile_action_drift(self, action_id: str, prod_url: str, staging_url: str) -> dict:
        action = self.db.query(Action).filter(Action.id == action_id).first()
        if not action:
            return {"success": False, "error": "Action not found"}

        selector = action.selector
        prod_exists = False
        staging_exists = False
        drift_detected = False
        recommended_selector = selector
        similarity_score = 1.0

        try:
            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # 1. Check in Production
                try:
                    await page.goto(prod_url, wait_until="networkidle")
                    prod_count = await page.locator(selector).count()
                    prod_exists = prod_count > 0
                except Exception:
                    pass

                # 2. Check in Staging
                try:
                    await page.goto(staging_url, wait_until="networkidle")
                    staging_count = await page.locator(selector).count()
                    staging_exists = staging_count > 0

                    if not staging_exists and prod_exists:
                        drift_detected = True
                        # Search for layout target replacements
                        SpecUpdaterService(self.db, action.project_id)
                        candidates = await page.locator("button, input, a").all()
                        best_candidate = None
                        best_score = 0.0

                        for cand in candidates:
                            try:
                                text = await cand.inner_text() or ""
                                await cand.evaluate("el => el.outerHTML") or ""
                                ratio = difflib.SequenceMatcher(None, action.name.lower(), text.lower()).ratio()
                                if ratio > best_score and ratio > 0.4:
                                    best_score = ratio
                                    best_candidate = cand
                            except Exception:
                                pass

                        if best_candidate:
                            try:
                                cand_id = await best_candidate.get_attribute("id")
                                if cand_id:
                                    recommended_selector = f"#{cand_id}"
                                else:
                                    cand_class = await best_candidate.get_attribute("class")
                                    if cand_class:
                                        first_class = cand_class.split()[0]
                                        recommended_selector = f"{await best_candidate.evaluate('el => el.tagName.toLowerCase()')}.{first_class}"
                                    else:
                                        recommended_selector = await best_candidate.evaluate("el => el.tagName.toLowerCase()")
                                similarity_score = best_score
                            except Exception:
                                pass
                except Exception:
                    pass

                await browser.close()

            return {
                "success": True,
                "action_name": action.name,
                "prod_exists": prod_exists,
                "staging_exists": staging_exists,
                "drift_detected": drift_detected or (prod_exists and not staging_exists),
                "similarity_score": similarity_score,
                "recommended_selector": recommended_selector
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
