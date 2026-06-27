export const MOCK_PROJECTS = [
  { id: "proj-1", name: "E-Commerce Mock Store", root_url: "http://localhost:8001", created_at: "2026-06-09T18:00:00Z" }
];

export const MOCK_CRAWLS = [
  { id: "crawl-1", project_id: "proj-1", status: "completed", started_at: "2026-06-09T18:01:00Z", completed_at: "2026-06-09T18:02:15Z" }
];

export const MOCK_ACTIONS = [
  { id: "act-1", name: "login", intent: "login", selector: "#login-form", action_type: "browser", confidence_score: 0.95, description: "Logs in the user with credentials", parameters: JSON.stringify([{ name: "email", type: "string", selector: "#email" }, { name: "password", type: "string", selector: "#password" }]) },
  { id: "act-2", name: "search_products", intent: "search", selector: "#search-form", action_type: "browser", confidence_score: 0.95, description: "Searches for products in the store", parameters: JSON.stringify([{ name: "q", type: "string", selector: "#search-input" }]) },
  { id: "act-3", name: "add_to_cart", intent: "add_to_cart", selector: "#add-to-cart-btn", action_type: "api", confidence_score: 0.98, description: "Adds the current product to the shopping cart", api_url: "/api/cart/add", api_method: "POST", parameters: JSON.stringify([{ name: "product_id", type: "string", selector: "" }, { name: "quantity", type: "integer", selector: "" }]) },
  { id: "act-4", name: "checkout", intent: "checkout", selector: "#checkout-submit-btn", action_type: "browser", confidence_score: 0.90, description: "Proceeds to place the order and checkout", parameters: "[]" }
];

export const MOCK_WORKFLOWS = [
  {
    id: "wf-1",
    name: "purchase_flow",
    description: "End-to-end purchasing workflow from login to order confirmation",
    steps: [
      { action: "login", source_page: "/login", target_page: "/catalog" },
      { action: "search_products", source_page: "/catalog", target_page: "/catalog" },
      { action: "add_to_cart", source_page: "/product/{id}", target_page: "/checkout" },
      { action: "checkout", source_page: "/checkout", target_page: "/catalog" }
    ]
  }
];

export const MOCK_APIS = [
  { id: "api-1", method: "POST", url: "/api/cart/add", request_body: { product_id: "string", quantity: "integer" }, mapped_action: "add_to_cart" }
];

export const MOCK_SPECS = {
  yaml: `version: 1.0.0
site: http://localhost:8001
actions:
  login:
    description: Logs in the user with credentials
    action_type: browser
    selector: '#login-form'
    parameters:
    - name: email
      type: string
      required: true
      selector: '#email'
    - name: password
      type: string
      required: true
      selector: '#password'
  search_products:
    description: Searches for products in the store
    action_type: browser
    selector: '#search-form'
    parameters:
    - name: q
      type: string
      required: true
      selector: '#search-input'
  add_to_cart:
    description: Adds the current product to shopping cart
    action_type: api
    selector: '#add-to-cart-btn'
    parameters:
    - name: product_id
      type: string
      required: true
    - name: quantity
      type: integer
      required: true
    api:
      url: /api/cart/add
      method: POST
  checkout:
    description: Proceeds to place the order and checkout
    action_type: browser
    selector: '#checkout-submit-btn'
    parameters: []`,
  python: `# Shiny Fishstick Generated Python SDK
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
        self.session_cookies = self.page.context.cookies()

    def search_products(self, q):
        """Searches for products in the store"""
        self.page.goto(self.root_url + "/catalog")
        self.page.fill("#search-input", str(q))
        self.page.click("#search-submit-btn")
        self.page.wait_for_load_state("networkidle")

    def add_to_cart(self, product_id, quantity=1):
        """Adds the current product to shopping cart"""
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

    def checkout(self):
        """Proceeds to place the order and checkout"""
        self.page.goto(self.root_url + "/checkout")
        self.page.click("#checkout-submit-btn")
        self.page.wait_for_load_state("networkidle")`
};
