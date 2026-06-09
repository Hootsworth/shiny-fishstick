import json
from urllib.parse import urlparse
from playwright.async_api import Page as PlaywrightPage, Request as PlaywrightRequest
from sqlalchemy.orm import Session
from ..models.db_models import Action

class APIDiscoveryService:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.captured_requests = []

    def attach(self, page: PlaywrightPage):
        # Bind the request handler
        page.on("request", self.handle_request)

    async def handle_request(self, request: PlaywrightRequest):
        try:
            resource_type = request.resource_type
            if resource_type in ["xhr", "fetch"]:
                method = request.method
                url = request.url
                headers = request.headers
                
                body = None
                try:
                    body = request.post_data
                except Exception:
                    pass

                self.captured_requests.append({
                    "url": url,
                    "method": method,
                    "headers": headers,
                    "body": body
                })
        except Exception as e:
            print(f"Error capturing request: {e}")

    async def save_discovered_apis(self, db: Session, crawl_id: str):
        # Scan captured requests for API routes
        for req in self.captured_requests:
            parsed = urlparse(req["url"])
            path = parsed.path
            
            # If we see /api/cart/add being hit, update the 'add_to_cart' action in our DB
            if "/api/cart/add" in path and req["method"] == "POST":
                action = db.query(Action).filter(
                    Action.project_id == self.project_id,
                    Action.intent == "add_to_cart"
                ).first()
                if action:
                    action.action_type = "api"
                    action.api_url = "/api/cart/add"
                    action.api_method = "POST"
                    action.parameters = json.dumps([
                        {
                            "name": "product_id",
                            "type": "string",
                            "required": True,
                            "source": "body.product_id"
                        },
                        {
                            "name": "quantity",
                            "type": "integer",
                            "required": True,
                            "source": "body.quantity",
                            "default": 1
                        }
                    ])
                    db.commit()
                    print(f"[API Discovery] Successfully mapped action 'add_to_cart' to direct API backend: POST {path}")
