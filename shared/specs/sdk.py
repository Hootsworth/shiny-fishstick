# Shiny Fishstick Generated Python SDK
import requests
import json
from playwright.sync_api import sync_playwright

class ShinyFishstickSiteSDK:
    def __init__(self, root_url="http://localhost:8001"):
        self.root_url = root_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_cookies = []
        self.session_local_storage = {}
        self.session_session_storage = {}

    def start(self, headless=True, session_data=None):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        if session_data:
            cookies = session_data.get("cookies", [])
            if cookies:
                self.context.add_cookies(cookies)
            self.page.goto(self.root_url)

            ls = session_data.get("localStorage", {})
            ss = session_data.get("sessionStorage", {})
            if ls:
                self.page.evaluate("ls => { for (let k in ls) { localStorage.setItem(k, ls[k]); } }", ls)
            if ss:
                self.page.evaluate("ss => { for (let k in ss) { sessionStorage.setItem(k, ss[k]); } }", ss)
            self.session_cookies = cookies
            self.session_local_storage = ls
            self.session_session_storage = ss
        else:
            self.page.goto(self.root_url)
            self.session_cookies = []
            self.session_local_storage = {}
            self.session_session_storage = {}
        return self

    def export_session(self):
        return {
            "cookies": self.session_cookies or [],
            "localStorage": self.session_local_storage or {},
            "sessionStorage": self.session_session_storage or {}
        }

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login(self, email, password):
        """Logs in the user with credentials"""

        self.page.goto(self.root_url + "/login")
        self.page.fill("#email", str(email))
        self.page.fill("#password", str(password))
        self.page.click("#login-submit-btn")
        self.page.wait_for_load_state("networkidle")
        self.session_cookies = self.page.context.cookies()
        import json
        try:
            ls_str = self.page.evaluate("() => JSON.stringify(localStorage)")
            self.session_local_storage = json.loads(ls_str or '{}')
            ss_str = self.page.evaluate("() => JSON.stringify(sessionStorage)")
            self.session_session_storage = json.loads(ss_str or '{}')
        except Exception:
            self.session_local_storage = {}
            self.session_session_storage = {}

    def search_products(self, q):
        """Searches for products in the store"""

        self.page.goto(self.root_url + "/catalog")
        self.page.fill("#search-input", str(q))
        self.page.click("#search-submit-btn")
        self.page.wait_for_load_state("networkidle")
        self.session_cookies = self.page.context.cookies()
        import json
        try:
            ls_str = self.page.evaluate("() => JSON.stringify(localStorage)")
            self.session_local_storage = json.loads(ls_str or '{}')
            ss_str = self.page.evaluate("() => JSON.stringify(sessionStorage)")
            self.session_session_storage = json.loads(ss_str or '{}')
        except Exception:
            self.session_local_storage = {}
            self.session_session_storage = {}

    def checkout(self):
        """Proceeds to place the order and checkout"""

        self.page.goto(self.root_url + "/checkout")
        self.page.click("#checkout-submit-btn")
        self.page.wait_for_load_state("networkidle")
        self.session_cookies = self.page.context.cookies()
        import json
        try:
            ls_str = self.page.evaluate("() => JSON.stringify(localStorage)")
            self.session_local_storage = json.loads(ls_str or '{}')
            ss_str = self.page.evaluate("() => JSON.stringify(sessionStorage)")
            self.session_session_storage = json.loads(ss_str or '{}')
        except Exception:
            self.session_local_storage = {}
            self.session_session_storage = {}

    def add_to_cart(self, product_id, quantity=1):
        """Adds the current product to the shopping cart"""

        # API Action execution
        session_val = None
        if self.session_cookies:
            session_val = next((c["value"] for c in self.session_cookies if c["name"] == "session"), None)
        cookies = {}
        if session_val:
            cookies = {"session": session_val}
        payload = {
        "product_id": product_id,
        "quantity": quantity
    }
        query_params = {}
        headers = {}
        res = requests.post(
            self.root_url + "/api/cart/add", json=payload,
            cookies=cookies,
            headers=headers
        )
        return res.json()

