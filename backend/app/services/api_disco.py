import json
from urllib.parse import parse_qs, parse_qsl, urlparse

from playwright.async_api import Page as PlaywrightPage
from playwright.async_api import Request as PlaywrightRequest
from sqlalchemy.orm import Session

from ..core.logging import log
from ..models.db_models import Action

# --- Constants ---
STATIC_ASSET_EXTENSIONS = {
    ".js", ".css", ".png", ".jpg", ".jpeg", ".html", ".ico",
    ".woff", ".woff2", ".ttf", ".svg", ".gif", ".webp",
}
AUTH_HEADER_NAMES = {
    "authorization", "x-auth-token", "x-api-key", "token", "jwt", "x-csrf-token",
}


class APIDiscoveryService:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.captured_requests = []
        self.current_action = None
        self.action_inputs = {}

    def attach(self, page: PlaywrightPage):
        # Bind the request handler
        page.on("request", self.handle_request)

    def start_recording(self, action_name: str, inputs: dict):
        self.current_action = action_name
        self.action_inputs = inputs
        log.info("api_disco_recording_started", action=action_name, inputs=inputs)

    def stop_recording(self):
        if self.current_action:
            log.info("api_disco_recording_stopped", action=self.current_action)
        self.current_action = None
        self.action_inputs = {}

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

                # Sniff for auth headers
                auth_headers = {}
                for k, v in headers.items():
                    if k.lower() in AUTH_HEADER_NAMES:
                        auth_headers[k] = v

                self.captured_requests.append({
                    "url": url,
                    "method": method,
                    "headers": headers,
                    "body": body,
                    "associated_action": self.current_action,
                    "action_inputs": self.action_inputs.copy() if self.action_inputs else {},
                    "auth_headers": auth_headers
                })
        except Exception as e:
            log.error("api_disco_request_capture_failed", error=str(e))

    async def save_discovered_apis(self, db: Session, crawl_id: str):
        # Fetch actions for the project
        actions = db.query(Action).filter(Action.project_id == self.project_id).all()

        for action in actions:
            # Find requests recorded for this action
            reqs = [r for r in self.captured_requests if r.get("associated_action") == action.name]
            if not reqs:
                continue

            log.info("api_disco_requests_found", action=action.name, count=len(reqs))

            # Select the most likely API candidate request (prefer non-GET, or JSON/form-containing if available)
            candidate = None
            for r in reqs:
                parsed_url = urlparse(r["url"])
                # Avoid static assets
                if any(parsed_url.path.lower().endswith(ext) for ext in STATIC_ASSET_EXTENSIONS):
                    continue
                # Prefer write methods
                if r["method"] in ["POST", "PUT", "PATCH", "DELETE"]:
                    candidate = r
                    break
            if not candidate and reqs:
                candidate = reqs[0]

            if not candidate:
                continue

            parsed = urlparse(candidate["url"])
            path = parsed.path
            method = candidate["method"]
            body_str = candidate["body"]

            log.info("api_disco_candidate_selected", action=action.name, method=method, path=path)

            # Now, map action parameters to the request payload
            existing_params = []
            try:
                existing_params = json.loads(action.parameters or "[]")
            except Exception:
                existing_params = []

            mapped_params = []

            # Parse body if it is JSON or form-urlencoded
            body_json = None
            if body_str:
                try:
                    body_json = json.loads(body_str)
                except Exception:
                    try:
                        body_json = {k: v[0] for k, v in parse_qs(body_str).items()}
                    except Exception:
                        pass

            # Query params
            query_params = dict(parse_qsl(parsed.query))

            # Context inputs (all values available from crawler recording context)
            inputs = candidate.get("action_inputs", {})

            for param in existing_params:
                param_name = param["name"]
                param_type = param["type"]
                param_sel = param.get("selector", "")
                param_req = param.get("required", True)
                param_attr_src = param.get("attribute_source", "")

                mapped_source = None

                # Retrieve the value we used for this parameter during crawling
                val_to_match = None
                keys_to_check = [param_name, param_attr_src, "url_id", "id"]
                for key in keys_to_check:
                    if key and key in inputs:
                        val_to_match = inputs[key]
                        break

                # Fallback: if not found, check all input values
                if val_to_match is None and inputs:
                    val_to_match = list(inputs.values())[0]

                if val_to_match is not None:
                    val_str = str(val_to_match).strip()

                    # Search body
                    if body_json:
                        for k, v in body_json.items():
                            if str(v).strip() == val_str:
                                mapped_source = f"body.{k}"
                                break

                    # Search query params
                    if not mapped_source and query_params:
                        for k, v in query_params.items():
                            if str(v).strip() == val_str:
                                mapped_source = f"query.{k}"
                                break

                if mapped_source:
                    mapped_params.append({
                        "name": param_name,
                        "type": param_type,
                        "selector": param_sel,
                        "required": param_req,
                        "source": mapped_source
                    })
                else:
                    mapped_params.append(param)

            # Check if there are other fields in the request body that are NOT mapped yet
            if body_json:
                for k, v in body_json.items():
                    already_mapped = any(p.get("source") == f"body.{k}" for p in mapped_params)
                    if not already_mapped:
                        val_type = "number" if isinstance(v, (int, float)) else "boolean" if isinstance(v, bool) else "string"
                        mapped_params.append({
                            "name": k,
                            "type": val_type,
                            "required": True,
                            "source": f"body.{k}",
                            "default": v
                        })

            # Same for query parameters
            if query_params:
                for k, v in query_params.items():
                    already_mapped = any(p.get("source") == f"query.{k}" for p in mapped_params)
                    if not already_mapped:
                        mapped_params.append({
                            "name": k,
                            "type": "string",
                            "required": False,
                            "source": f"query.{k}",
                            "default": v
                        })

            # Sniff for authorization headers in candidate request
            auth_headers = candidate.get("auth_headers", {})
            if auth_headers:
                # Retrieve saved AuthConfig to look up where these token values came from
                from ..models.db_models import AuthConfig
                auth_cfg = db.query(AuthConfig).filter(AuthConfig.project_id == self.project_id).first()
                auth_details = {}
                if auth_cfg:
                    try:
                        auth_details = json.loads(auth_cfg.details)
                    except Exception:
                        pass

                session_ind = auth_details.get("session_indicators", {})
                cookies_list = session_ind.get("cookies", [])
                ls_dict = session_ind.get("localStorage", {})
                ss_dict = session_ind.get("sessionStorage", {})

                for h_name, h_val in auth_headers.items():
                    already_mapped = any(p.get("source") == f"header.{h_name}" for p in mapped_params)
                    if already_mapped:
                        continue

                    token_source = None
                    token_val = h_val
                    if h_val.lower().startswith("bearer "):
                        token_val = h_val[7:].strip()

                    # Check cookies
                    for cookie in cookies_list:
                        if cookie.get("value") == token_val:
                            token_source = f"cookie.{cookie.get('name')}"
                            break

                    # Check localStorage
                    if not token_source:
                        for ls_k, ls_v in ls_dict.items():
                            if str(ls_v).strip() == token_val:
                                token_source = f"localStorage.{ls_k}"
                                break

                    # Check sessionStorage
                    if not token_source:
                        for ss_k, ss_v in ss_dict.items():
                            if str(ss_v).strip() == token_val:
                                token_source = f"sessionStorage.{ss_k}"
                                break

                    mapped_params.append({
                        "name": h_name,
                        "type": "string",
                        "required": True,
                        "source": f"header.{h_name}",
                        "token_source": token_source,
                        "default": h_val
                    })

            # Update Action in database
            action.action_type = "api"
            action.api_url = path
            action.api_method = method
            action.parameters = json.dumps(mapped_params)
            db.commit()
            log.info("api_disco_action_upgraded", action=action.name, method=method, path=path, param_count=len(mapped_params))
