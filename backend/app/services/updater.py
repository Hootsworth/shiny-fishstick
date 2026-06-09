import json
from sqlalchemy.orm import Session
from ..models.db_models import Action, Element, Page
from playwright.async_api import Page as PlaywrightPage

class SpecUpdaterService:
    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id

    async def detect_drift_and_heal(self, page: PlaywrightPage) -> list:
        # Load all actions for this project
        actions = self.db.query(Action).filter(Action.project_id == self.project_id).all()
        healed_actions = []

        for action in actions:
            if action.action_type == "api":
                # API actions are stable against DOM changes
                continue

            selector = action.selector
            # Test if selector is still present on the current browser page
            try:
                # First wait a tiny bit to let DOM load
                count = await page.locator(selector).count()
                if count > 0:
                    # Selector is stable!
                    continue
                
                # Selector is missing! Let's attempt self-healing
                print(f"[Spec Updater] Action '{action.name}' selector drifted! Attempting to heal: '{selector}'")
                
                # 1. Grab all interactive elements on the current page to search for a match
                buttons = await page.locator("button, input[type='submit'], a.btn, a.button").all()
                inputs = await page.locator("input, textarea, select").all()
                
                healed = False
                
                # For buttons (like login, checkout, add to cart), check text match or partial tag match
                if action.intent in ["login", "checkout", "add_to_cart"]:
                    for btn in buttons:
                        btn_text = await btn.inner_text()
                        btn_text = btn_text.strip().lower() if btn_text else ""
                        
                        # Match by intent keywords or text resemblance
                        intent_match = (
                            (action.intent == "login" and "continue" in btn_text or "sign in" in btn_text) or
                            (action.intent == "checkout" and "place order" in btn_text or "purchase" in btn_text) or
                            (action.intent == "add_to_cart" and "add" in btn_text or "cart" in btn_text)
                        )
                        
                        if intent_match:
                            # Generate new selector
                            new_sel = await self.generate_selector_fallback(btn)
                            action.selector = new_sel
                            action.confidence_score = 0.8  # slightly lower confidence after healing
                            self.db.commit()
                            healed_actions.append({
                                "action": action.name,
                                "status": "healed",
                                "old_selector": selector,
                                "new_selector": new_sel
                            })
                            healed = True
                            print(f"[Spec Updater] Healed action '{action.name}' with new selector: '{new_sel}'")
                            break
                            
                if not healed:
                    # Mark action as broken if healing fails
                    action.confidence_score = 0.0
                    self.db.commit()
                    healed_actions.append({
                        "action": action.name,
                        "status": "broken",
                        "old_selector": selector,
                        "new_selector": None
                    })
                    print(f"[Spec Updater] Action '{action.name}' is broken. Manual review needed.")
                    
            except Exception as e:
                print(f"[Spec Updater] Error scanning element drift: {e}")

        return healed_actions

    async def generate_selector_fallback(self, element) -> str:
        el_id = await element.get_attribute("id")
        if el_id:
            return f"#{el_id}"
        name = await element.get_attribute("name")
        tag = await element.evaluate("el => el.tagName.toLowerCase()")
        if name:
            return f"{tag}[name='{name}']"
        classes = await element.get_attribute("class")
        if classes:
            class_list = classes.split()
            valid = [c for c in class_list if ":" not in c and "[" not in c]
            if valid:
                return f"{tag}.{'.'.join(valid[:2])}"
        return tag
