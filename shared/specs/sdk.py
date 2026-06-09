# Shiny Fishstick Generated Python SDK
import requests
from playwright.sync_api import sync_playwright

class ShinyFishstickSiteSDK:
    def __init__(self, root_url="http://localhost:8001"):
        self.root_url = root_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_cookies = None

    def start(self, headless=True):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(self.root_url)
        return self

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
        if "login" == "login":
            self.session_cookies = self.page.context.cookies()

    def search_products(self, q):
        """Searches for products in the store"""

        self.page.goto(self.root_url + "/catalog")
        self.page.fill("#search-input", str(q))
        self.page.click("#search-submit-btn")
        self.page.wait_for_load_state("networkidle")
        if "search_products" == "login":
            self.session_cookies = self.page.context.cookies()

    def checkout(self):
        """Proceeds to place the order and checkout"""

        self.page.goto(self.root_url + "/checkout")
        self.page.click("#checkout-submit-btn")
        self.page.wait_for_load_state("networkidle")
        if "checkout" == "login":
            self.session_cookies = self.page.context.cookies()

    def add_to_cart(self, product_id, quantity=1):
        """Adds the current product to the shopping cart"""

        # API Action execution
        session_val = None
        if self.session_cookies:
            session_val = next((c["value"] for c in self.session_cookies if c["name"] == "session"), None)
        headers = {}
        cookies = {}
        if session_val:
            cookies = {"session": session_val}
        payload = {
            "product_id": product_id,
            "quantity": quantity
        }
        res = requests.post(
            self.root_url + "/api/cart/add",
            json=payload,
            cookies=cookies
        )
        return res.json()

