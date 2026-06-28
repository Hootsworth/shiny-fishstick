import base64
import json
import time
from typing import Any, Dict

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from sqlalchemy.orm import Session

from ..core.logging import log
from ..core.security import decrypt_data
from ..models.db_models import Action, AuthConfig


class PlaygroundService:
    def __init__(self, db: Session):
        self.db = db

    async def execute_action(self, project_id: str, action_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        action = self.db.query(Action).filter(Action.id == action_id).first()
        if not action:
            return {"success": False, "error": "Action not found"}

        from ..models.db_models import Project
        project = self.db.query(Project).filter(Project.id == project_id).first()
        root_url = project.root_url if project else "http://localhost:8001"

        start_time = time.time()
        screenshot_base64 = ""
        success = False
        error_msg = ""
        assertion_results = []

        try:
            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                auth_cfg = self.db.query(AuthConfig).filter(AuthConfig.project_id == project_id).first()
                if auth_cfg:
                    try:
                        details_str = decrypt_data(auth_cfg.details) if not auth_cfg.details.startswith("{") else auth_cfg.details
                        details = json.loads(details_str)
                        session_ind = details.get("session_indicators", {})
                        cookies = session_ind.get("cookies", [])
                        if cookies:
                            await context.add_cookies(cookies)
                    except Exception:
                        pass

                target_url = root_url
                if action.name == "login":
                    target_url = f"{root_url.rstrip('/')}/login"
                elif action.name == "search_products":
                    target_url = f"{root_url.rstrip('/')}/catalog"

                await page.goto(target_url, wait_until="networkidle")

                action_params = json.loads(action.parameters or "[]")
                frame_selector = ""
                for param in action_params:
                    if param.get("name") == "_frame_selector":
                        frame_selector = param.get("selector", "")
                        break

                target_context = page.frame_locator(frame_selector) if frame_selector else page

                for param in action_params:
                    p_name = param["name"]
                    if p_name == "_frame_selector":
                        continue
                    p_val = parameters.get(p_name, "")
                    if p_val and param.get("selector"):
                        await target_context.locator(param["selector"]).fill(str(p_val))

                if action.action_type == "browser":
                    trigger_sel = action.selector
                    if action.name == "login":
                        trigger_sel = "#login-submit-btn"
                    elif action.name == "search_products":
                        trigger_sel = "#search-submit-btn"

                    await target_context.locator(trigger_sel).click()
                    await page.wait_for_load_state("networkidle")

                if action.assertions:
                    assertions_list = json.loads(action.assertions)
                    for ast in assertions_list:
                        atype = ast.get("type")
                        asel = ast.get("selector", "")
                        aval = ast.get("value", "")

                        ast_success = False
                        if atype == "visible":
                            ast_success = await page.locator(asel).is_visible()
                        elif atype == "not_visible":
                            ast_success = not (await page.locator(asel).is_visible())
                        elif atype == "contains_text":
                            txt = await page.locator(asel).inner_text()
                            ast_success = aval in txt
                        elif atype == "url_equals":
                            ast_success = page.url == aval

                        assertion_results.append({
                            "type": atype,
                            "selector": asel,
                            "value": aval,
                            "passed": ast_success
                        })

                screenshot_bytes = await page.screenshot(type="png")
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                await browser.close()
                success = True

        except Exception as e:
            error_msg = str(e)
            log.error("playground_execution_failed", action_id=action_id, error=error_msg)

        execution_time = (time.time() - start_time) * 1000

        return {
            "success": success and all(a["passed"] for a in assertion_results),
            "execution_time_ms": execution_time,
            "error": error_msg,
            "assertion_results": assertion_results,
            "screenshot": screenshot_base64
        }
