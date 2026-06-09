import os
import yaml
import json
from sqlalchemy.orm import Session
from ..models.db_models import Action, Project, SpecVersion

class SDKGeneratorService:
    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id

    def generate_all(self) -> dict:
        project = self.db.query(Project).filter(Project.id == self.project_id).first()
        if not project:
            raise ValueError("Project not found")

        actions = self.db.query(Action).filter(Action.project_id == self.project_id).all()
        
        # 1. Generate YAML Spec
        spec_dict = {
            "version": "1.0.0",
            "site": project.root_url,
            "actions": {}
        }
        
        for act in actions:
            params = json.loads(act.parameters or "[]")
            param_list = []
            for p in params:
                param_list.append({
                    "name": p["name"],
                    "type": p["type"],
                    "required": p.get("required", True),
                    "selector": p.get("selector", "")
                })
            
            action_spec = {
                "description": act.description,
                "action_type": act.action_type,
                "selector": act.selector,
                "parameters": param_list
            }
            if act.action_type == "api":
                action_spec["api"] = {
                    "url": act.api_url,
                    "method": act.api_method
                }
            spec_dict["actions"][act.name] = action_spec

        yaml_content = yaml.dump(spec_dict, sort_keys=False)
        
        # Save to DB SpecVersions
        spec_ver = SpecVersion(
            project_id=self.project_id,
            version="1.0.0",
            yaml_content=yaml_content
        )
        self.db.add(spec_ver)
        self.db.commit()

        # 2. Generate Python SDK
        python_sdk = self.generate_python_sdk(project.root_url, actions)
        
        # 3. Generate TypeScript SDK
        typescript_sdk = self.generate_typescript_sdk(project.root_url, actions)
        
        # 4. Generate JSON Tools Schema (for agents)
        tools_schema = self.generate_tools_schema(actions)

        # Write to files locally for easy access/download
        specs_dir = "/Users/adityadixit/Documents/Code/Preflight Designer/shared/specs"
        os.makedirs(specs_dir, exist_ok=True)
        
        with open(os.path.join(specs_dir, "preflight.yaml"), "w") as f:
            f.write(yaml_content)
        with open(os.path.join(specs_dir, "sdk.py"), "w") as f:
            f.write(python_sdk)
        with open(os.path.join(specs_dir, "sdk.ts"), "w") as f:
            f.write(typescript_sdk)
        with open(os.path.join(specs_dir, "tools.json"), "w") as f:
            json.dump(tools_schema, f, indent=2)

        return {
            "yaml": yaml_content,
            "python": python_sdk,
            "typescript": typescript_sdk,
            "tools": tools_schema
        }

    def generate_python_sdk(self, root_url: str, actions: list) -> str:
        methods_code = ""
        for act in actions:
            params = json.loads(act.parameters or "[]")
            
            # Formulate arguments signature
            arg_sig = "self"
            for p in params:
                arg_sig += f", {p['name']}"
                if p["name"] == "quantity":
                    arg_sig += "=1" # default quantity helper
            
            docstring = f'        """{act.description}"""'
            
            body_code = ""
            if act.action_type == "api":
                # Direct HTTP execution mapping
                body_code = f"""
        # API Action execution
        session_val = None
        if self.session_cookies:
            session_val = next((c["value"] for c in self.session_cookies if c["name"] == "session"), None)
        headers = {{}}
        cookies = {{}}
        if session_val:
            cookies = {{"session": session_val}}
        payload = {{
            "product_id": product_id,
            "quantity": quantity
        }}
        res = requests.{act.api_method.lower()}(
            self.root_url + "{act.api_url}",
            json=payload,
            cookies=cookies
        )
        return res.json()"""
            else:
                # Browser click/type actions
                fill_actions = ""
                for p in params:
                    fill_actions += f'\n        self.page.fill("{p["selector"]}", str({p["name"]}))'
                
                # Custom trigger clicking depending on action
                trigger_click = ""
                if act.name == "login":
                    trigger_click = '\n        self.page.click("#login-submit-btn")'
                elif act.name == "search_products":
                    trigger_click = '\n        self.page.click("#search-submit-btn")'
                elif act.name == "checkout":
                    trigger_click = '\n        self.page.click("#checkout-submit-btn")'
                else:
                    trigger_click = f'\n        self.page.click("{act.selector}")'

                # Navigation targets
                nav_target = ""
                if act.name == "login":
                    nav_target = f'\n        self.page.goto(self.root_url + "/login")'
                elif act.name == "search_products":
                    nav_target = f'\n        self.page.goto(self.root_url + "/catalog")'
                elif act.name == "checkout":
                    nav_target = f'\n        self.page.goto(self.root_url + "/checkout")'

                body_code = f"""{nav_target}{fill_actions}{trigger_click}
        self.page.wait_for_load_state("networkidle")
        if "{act.name}" == "login":
            self.session_cookies = self.page.context.cookies()"""

            methods_code += f"""
    def {act.name}({arg_sig}):
{docstring}
{body_code}
"""

        sdk_template = f"""# Shiny Fishstick Generated Python SDK
import requests
from playwright.sync_api import sync_playwright

class ShinyFishstickSiteSDK:
    def __init__(self, root_url="{root_url}"):
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
{methods_code}
"""
        return sdk_template

    def generate_typescript_sdk(self, root_url: str, actions: list) -> str:
        methods_code = ""
        for act in actions:
            params = json.loads(act.parameters or "[]")
            
            # Formulate parameters signature
            arg_sig = ""
            for p in params:
                type_map = "string" if p["type"] == "string" else "number"
                arg_sig += f"{p['name']}: {type_map}, "
            arg_sig = arg_sig.rstrip(", ")

            body_code = ""
            if act.action_type == "api":
                body_code = f"""
        const sessionCookie = (await this.context.cookies()).find(c => c.name === 'session');
        const cookieHeader = sessionCookie ? `session=${{sessionCookie.value}}` : '';
        const response = await fetch(`${{this.rootUrl}}{act.api_url}`, {{
            method: '{act.api_method}',
            headers: {{
                'Content-Type': 'application/json',
                'Cookie': cookieHeader
            }},
            body: JSON.stringify({{ product_id, quantity }})
        }});
        return response.json();"""
            else:
                fill_actions = ""
                for p in params:
                    fill_actions += f'\n        await this.page.fill("{p["selector"]}", String({p["name"]}));'
                
                trigger_click = ""
                if act.name == "login":
                    trigger_click = '\n        await this.page.click("#login-submit-btn");'
                elif act.name == "search_products":
                    trigger_click = '\n        await this.page.click("#search-submit-btn");'
                elif act.name == "checkout":
                    trigger_click = '\n        await this.page.click("#checkout-submit-btn");'
                else:
                    trigger_click = f'\n        await this.page.click("{act.selector}");'

                nav_target = ""
                if act.name == "login":
                    nav_target = f'\n        await this.page.goto(`${{this.rootUrl}}/login`);'
                elif act.name == "search_products":
                    nav_target = f'\n        await this.page.goto(`${{this.rootUrl}}/catalog`);'
                elif act.name == "checkout":
                    nav_target = f'\n        await this.page.goto(`${{this.rootUrl}}/checkout`);'

                body_code = f"""{nav_target}{fill_actions}{trigger_click}
        await this.page.waitForLoadState("networkidle");"""

            methods_code += f"""
    async {act.name}({arg_sig}): Promise<any> {{
        {body_code}
    }}
"""

        sdk_template = f"""// Shiny Fishstick Generated TypeScript SDK
import {{ chromium, Browser, BrowserContext, Page }} from 'playwright';

export class ShinyFishstickSiteSDK {{
    private rootUrl: string = "{root_url}";
    private browser: Browser | null = null;
    private context: BrowserContext | null = null;
    private page: Page | null = null;

    async start(headless: boolean = true): Promise<ShinyFishstickSiteSDK> {{
        this.browser = await chromium.launch({{ headless }});
        this.context = await this.browser.newContext();
        this.page = await this.context.newPage();
        await this.page.goto(this.rootUrl);
        return this;
    }}

    async close(): Promise<void> {{
        if (this.browser) await this.browser.close();
    }}
{methods_code}
}}
"""
        return sdk_template

    def generate_tools_schema(self, actions: list) -> list:
        tools = []
        for act in actions:
            params = json.loads(act.parameters or "[]")
            properties = {}
            required = []
            
            for p in params:
                properties[p["name"]] = {
                    "type": "string" if p["type"] == "string" else "integer",
                    "description": f"Value for form field: {p['name']}"
                }
                if p.get("required", True):
                    required.append(p["name"])
                    
            tools.append({
                "type": "function",
                "function": {
                    "name": act.name,
                    "description": act.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            })
        return tools
