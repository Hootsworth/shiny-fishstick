import json

from playwright.async_api import Page as PlaywrightPage
from sqlalchemy.orm import Session

from ..models.db_models import Action, Crawl, Element, Page


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

    def get_latest_completed_crawls(self, project_id: str, limit: int = 2) -> list:
        return (
            self.db.query(Crawl)
            .filter(Crawl.project_id == project_id, Crawl.status == "completed")
            .order_by(Crawl.completed_at.desc())
            .limit(limit)
            .all()
        )

    def compare_crawls(self, crawl_id_1: str, crawl_id_2: str) -> dict:
        # Fetch pages for crawl 1
        pages_1 = self.db.query(Page).filter(Page.crawl_id == crawl_id_1).all()
        # Fetch pages for crawl 2
        pages_2 = self.db.query(Page).filter(Page.crawl_id == crawl_id_2).all()

        # Group pages by path template
        page_map_1 = {p.path: p for p in pages_1}
        page_map_2 = {p.path: p for p in pages_2}

        all_paths = set(page_map_1.keys()).union(set(page_map_2.keys()))

        deltas = {}
        for path in all_paths:
            p1 = page_map_1.get(path)
            p2 = page_map_2.get(path)

            if p1 and not p2:
                # Page deleted
                deltas[path] = {
                    "status": "page_deleted",
                    "elements": {
                        "added": [],
                        "deleted": [
                            {
                                "element_type": el.element_type,
                                "tag_name": el.tag_name,
                                "selector": el.selector,
                                "text_content": el.text_content
                            }
                            for el in p1.elements
                        ],
                        "modified": [],
                        "unmodified": []
                    }
                }
            elif p2 and not p1:
                # Page added
                deltas[path] = {
                    "status": "page_added",
                    "elements": {
                        "added": [
                            {
                                "element_type": el.element_type,
                                "tag_name": el.tag_name,
                                "selector": el.selector,
                                "text_content": el.text_content
                            }
                            for el in p2.elements
                        ],
                        "deleted": [],
                        "modified": [],
                        "unmodified": []
                    }
                }
            else:
                # Page exists in both, diff elements
                element_diff = self._diff_elements(p1.elements, p2.elements)

                # Check if there are any changes on this page
                has_changes = (
                    len(element_diff["added"]) > 0 or
                    len(element_diff["deleted"]) > 0 or
                    len(element_diff["modified"]) > 0
                )

                deltas[path] = {
                    "status": "modified" if has_changes else "unmodified",
                    "elements": element_diff
                }

        return deltas

    def _calculate_element_similarity(self, e1: Element, e2: Element) -> float:
        tag1 = e1.tag_name.lower()
        tag2 = e2.tag_name.lower()
        if tag1 != tag2:
            if not ((tag1 in ["button", "input"] and tag2 in ["button", "input"])):
                return 0.0

        score = 0.0

        try:
            attrs1 = json.loads(e1.attributes or "{}")
            attrs2 = json.loads(e2.attributes or "{}")
        except Exception:
            attrs1 = {}
            attrs2 = {}

        # Check high-quality matching attributes
        for attr in ["data-testid", "id", "name"]:
            val1 = attrs1.get(attr)
            val2 = attrs2.get(attr)
            if val1 and val2:
                if val1 == val2:
                    score += 0.5
                else:
                    score -= 0.1

        # Check class overlap
        class1 = attrs1.get("class", "")
        class2 = attrs2.get("class", "")
        if class1 and class2:
            cls_set1 = set(class1.split())
            cls_set2 = set(class2.split())
            intersection = cls_set1.intersection(cls_set2)
            if intersection:
                score += min(0.3, len(intersection) * 0.1)

        # Check other attributes
        for attr in ["type", "placeholder", "value"]:
            val1 = attrs1.get(attr)
            val2 = attrs2.get(attr)
            if val1 and val2 and val1 == val2:
                score += 0.2

        # Compare text content
        txt1 = (e1.text_content or "").strip().lower()
        txt2 = (e2.text_content or "").strip().lower()
        if txt1 and txt2:
            if txt1 == txt2:
                score += 0.4
            elif txt1 in txt2 or txt2 in txt1:
                score += 0.2

        # Selector similarity
        if e1.selector == e2.selector:
            score += 0.2

        return max(0.0, min(1.0, score))

    def _diff_elements(self, elements_1: list, elements_2: list) -> dict:
        added = []
        deleted = []
        modified = []
        unmodified = []

        matched_2_ids = set()

        for e1 in elements_1:
            best_match = None
            best_score = 0.0

            for e2 in elements_2:
                if e2.id in matched_2_ids:
                    continue
                score = self._calculate_element_similarity(e1, e2)
                if score > best_score:
                    best_score = score
                    best_match = e2

            if best_match and best_score >= 0.5:
                matched_2_ids.add(best_match.id)

                if e1.selector == best_match.selector:
                    unmodified.append({
                        "element_type": e1.element_type,
                        "tag_name": e1.tag_name,
                        "selector": e1.selector,
                        "text_content": e1.text_content
                    })
                else:
                    modified.append({
                        "element_type": e1.element_type,
                        "tag_name": e1.tag_name,
                        "old_selector": e1.selector,
                        "new_selector": best_match.selector,
                        "text_content": best_match.text_content,
                        "drift_confidence": best_score
                    })
            else:
                deleted.append({
                    "element_type": e1.element_type,
                    "tag_name": e1.tag_name,
                    "selector": e1.selector,
                    "text_content": e1.text_content
                })

        for e2 in elements_2:
            if e2.id not in matched_2_ids:
                added.append({
                    "element_type": e2.element_type,
                    "tag_name": e2.tag_name,
                    "selector": e2.selector,
                    "text_content": e2.text_content
                })

        return {
            "added": added,
            "deleted": deleted,
            "modified": modified,
            "unmodified": unmodified
        }
