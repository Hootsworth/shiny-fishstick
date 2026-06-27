import json
import os

import yaml
from sqlalchemy.orm import Session

from ..models.db_models import Action, Project, SpecVersion, Workflow


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
            if act.assertions:
                try:
                    action_spec["assertions"] = json.loads(act.assertions)
                except Exception:
                    pass
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

        # 5. Generate Model Context Protocol (MCP) Server
        mcp_server = self.generate_mcp_server(actions)

        # 6. Generate E2E SDK Test Suite
        workflows = self.db.query(Workflow).filter(Workflow.project_id == self.project_id).all()
        sdk_tests = self.generate_sdk_tests(project.root_url, workflows)

        # Write to files locally for easy access/download
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
        specs_dir = os.path.join(project_root, "shared/specs")
        os.makedirs(specs_dir, exist_ok=True)

        with open(os.path.join(specs_dir, "preflight.yaml"), "w") as f:
            f.write(yaml_content)
        with open(os.path.join(specs_dir, "sdk.py"), "w") as f:
            f.write(python_sdk)
        with open(os.path.join(specs_dir, "sdk.ts"), "w") as f:
            f.write(typescript_sdk)
        with open(os.path.join(specs_dir, "tools.json"), "w") as f:
            json.dump(tools_schema, f, indent=2)
        with open(os.path.join(specs_dir, "mcp_server.py"), "w") as f:
            f.write(mcp_server)
        with open(os.path.join(specs_dir, "test_sdk.py"), "w") as f:
            f.write(sdk_tests)

        return {
            "yaml": yaml_content,
            "python": python_sdk,
            "typescript": typescript_sdk,
            "tools": tools_schema,
            "mcp": mcp_server,
            "tests": sdk_tests
        }

    def generate_python_sdk(self, root_url: str, actions: list) -> str:
        methods_code = ""
        for act in actions:
            params = json.loads(act.parameters or "[]")

            # Formulate arguments signature
            arg_sig = "self"
            for p in params:
                if p["name"] == "_frame_selector":
                    continue
                if p.get("source", "").startswith("header."):
                    arg_sig += f", {p['name']}=None"
                else:
                    arg_sig += f", {p['name']}"
                    if p["name"] == "quantity":
                        arg_sig += "=1" # default quantity helper

            docstring = f'        """{act.description}"""'

            body_code = ""
            if act.action_type == "api":
                # Direct HTTP execution mapping
                body_items = []
                query_items = []
                header_items = []
                resolve_headers_code = ""

                for p in params:
                    src = p.get("source", "")
                    p_name = p["name"]
                    if src.startswith("body."):
                        body_key = src.split("body.")[1]
                        body_items.append(f'        "{body_key}": {p_name}')
                    elif src.startswith("query."):
                        query_key = src.split("query.")[1]
                        query_items.append(f'        "{query_key}": {p_name}')
                    elif src.startswith("header."):
                        header_key = src.split("header.")[1]
                        t_src = p.get("token_source")
                        if t_src:
                            if t_src.startswith("localStorage."):
                                ls_key = t_src.split("localStorage.")[1]
                                resolve_headers_code += f"""
        if {p_name} is None:
            {p_name} = self.session_local_storage.get("{ls_key}")
            if {p_name} and not {p_name}.startswith("Bearer "):
                {p_name} = "Bearer " + {p_name}"""
                            elif t_src.startswith("cookie."):
                                c_key = t_src.split("cookie.")[1]
                                resolve_headers_code += f"""
        if {p_name} is None:
            cookie_val = next((c["value"] for c in self.session_cookies if c["name"] == "{c_key}"), None)
            if cookie_val:
                {p_name} = "Bearer " + cookie_val if not cookie_val.startswith("Bearer ") else cookie_val"""
                        header_items.append(f'        "{header_key}": {p_name}')

                payload_code = "payload = {\n" + ",\n".join(body_items) + "\n    }" if body_items else "payload = {}"
                query_code = "query_params = {\n" + ",\n".join(query_items) + "\n    }" if query_items else "query_params = {}"
                header_code = "headers = {\n" + ",\n".join(header_items) + "\n    }" if header_items else "headers = {}"

                json_arg = ", json=payload" if body_items else ""
                params_arg = ", params=query_params" if query_items else ""

                body_code = f"""{resolve_headers_code}
        # API Action execution
        session_val = None
        if self.session_cookies:
            session_val = next((c["value"] for c in self.session_cookies if c["name"] == "session"), None)
        cookies = {{}}
        if session_val:
            cookies = {{"session": session_val}}
        {payload_code}
        {query_code}
        {header_code}
        res = requests.{act.api_method.lower()}(
            self.root_url + "{act.api_url}"{json_arg}{params_arg},
            cookies=cookies,
            headers=headers
        )
        return res.json()"""
            else:
                # Browser click/type actions
                frame_selector = ""
                for p in params:
                    if p.get("name") == "_frame_selector":
                        frame_selector = p.get("selector", "")
                        break
                    elif p.get("frame_selector"):
                        frame_selector = p.get("frame_selector", "")
                        break

                target_expr = f'self.page.frame_locator("{frame_selector}")' if frame_selector else 'self.page'
                fill_actions = ""
                for p in params:
                    if p["name"] == "_frame_selector":
                        continue
                    fill_actions += f'\n        {target_expr}.fill("{p["selector"]}", str({p["name"]}))'

                # Custom trigger clicking depending on action
                trigger_click = ""
                if act.name == "login":
                    trigger_click = f'\n        {target_expr}.click("#login-submit-btn")'
                elif act.name == "search_products":
                    trigger_click = f'\n        {target_expr}.click("#search-submit-btn")'
                elif act.name == "checkout":
                    trigger_click = f'\n        {target_expr}.click("#checkout-submit-btn")'
                else:
                    trigger_click = f'\n        {target_expr}.click("{act.selector}")'

                # Navigation targets
                nav_target = ""
                if act.name == "login":
                    nav_target = '\n        self.page.goto(self.root_url + "/login")'
                elif act.name == "search_products":
                    nav_target = '\n        self.page.goto(self.root_url + "/catalog")'
                elif act.name == "checkout":
                    nav_target = '\n        self.page.goto(self.root_url + "/checkout")'

                body_code = f"""{nav_target}{fill_actions}{trigger_click}
        self.page.wait_for_load_state("networkidle")
        self.session_cookies = self.page.context.cookies()
        import json
        try:
            ls_str = self.page.evaluate("() => JSON.stringify(localStorage)")
            self.session_local_storage = json.loads(ls_str or '{{}}')
            ss_str = self.page.evaluate("() => JSON.stringify(sessionStorage)")
            self.session_session_storage = json.loads(ss_str or '{{}}')
        except Exception:
            self.session_local_storage = {{}}
            self.session_session_storage = {{}}"""

            methods_code += f"""
    def {act.name}({arg_sig}):
{docstring}
{body_code}
"""

        sdk_template = f"""# Shiny Fishstick Generated Python SDK
import requests
import json
from playwright.sync_api import sync_playwright

class ShinyFishstickSiteSDK:
    def __init__(self, root_url="{root_url}"):
        self.root_url = root_url
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.session_cookies = []
        self.session_local_storage = {{}}
        self.session_session_storage = {{}}

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

            ls = session_data.get("localStorage", {{}})
            ss = session_data.get("sessionStorage", {{}})
            if ls:
                self.page.evaluate("ls => {{ for (let k in ls) {{ localStorage.setItem(k, ls[k]); }} }}", ls)
            if ss:
                self.page.evaluate("ss => {{ for (let k in ss) {{ sessionStorage.setItem(k, ss[k]); }} }}", ss)
            self.session_cookies = cookies
            self.session_local_storage = ls
            self.session_session_storage = ss
        else:
            self.page.goto(self.root_url)
            self.session_cookies = []
            self.session_local_storage = {{}}
            self.session_session_storage = {{}}
        return self

    def export_session(self):
        return {{
            "cookies": self.session_cookies or [],
            "localStorage": self.session_local_storage or {{}},
            "sessionStorage": self.session_session_storage or {{}}
        }}

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
                if p["name"] == "_frame_selector":
                    continue
                type_map = "string" if p["type"] == "string" else "number"
                if p.get("source", "").startswith("header."):
                    arg_sig += f"{p['name']}?: {type_map}, "
                else:
                    arg_sig += f"{p['name']}: {type_map}, "
            arg_sig = arg_sig.rstrip(", ")

            body_code = ""
            if act.action_type == "api":
                body_items = []
                query_items = []
                header_items = []
                resolve_headers_code = ""

                for p in params:
                    src = p.get("source", "")
                    p_name = p["name"]
                    if src.startswith("body."):
                        body_key = src.split("body.")[1]
                        body_items.append(f'"{body_key}": {p_name}')
                    elif src.startswith("query."):
                        query_key = src.split("query.")[1]
                        query_items.append(f'"{query_key}": {p_name}')
                    elif src.startswith("header."):
                        header_key = src.split("header.")[1]
                        t_src = p.get("token_source")
                        if t_src:
                            if t_src.startswith("localStorage."):
                                ls_key = t_src.split("localStorage.")[1]
                                resolve_headers_code += f"""
        if (!{p_name}) {{
            {p_name} = this.sessionLocalStorage['{ls_key}'];
            if ({p_name} && !{p_name}.startsWith("Bearer ")) {{
                {p_name} = "Bearer " + {p_name};
            }}
        }}"""
                            elif t_src.startswith("cookie."):
                                c_key = t_src.split("cookie.")[1]
                                resolve_headers_code += f"""
        if (!{p_name}) {{
            const cookieVal = this.sessionCookies.find(c => c.name === '{c_key}')?.value;
            if (cookieVal) {{
                {p_name} = cookieVal.startsWith("Bearer ") ? cookieVal : "Bearer " + cookieVal;
            }}
        }}"""
                        header_items.append(f'"{header_key}": {p_name}')

                # Body stringify code
                if body_items:
                    body_json_str = "JSON.stringify({ " + ", ".join(body_items) + " })"
                    body_line = f"\n            body: {body_json_str},"
                else:
                    body_line = ""

                # Query parameters construction
                if query_items:
                    query_def = "const queryParams = new URLSearchParams({\n"
                    for q in query_items:
                        k, v = q.split(":")
                        k = k.strip().replace('"', '').replace("'", "")
                        v = v.strip()
                        query_def += f"            {k}: String({v}),\n"
                    query_def += "        }).toString();\n"
                    url_expr = f"`${{this.rootUrl}}{act.api_url}?${{queryParams}}`"
                else:
                    query_def = ""
                    url_expr = f"`${{this.rootUrl}}{act.api_url}`"

                # Header construction
                header_lines = "'Content-Type': 'application/json',\n                'Cookie': cookieHeader"
                for h in header_items:
                    k, v = h.split(":")
                    k = k.strip().replace('"', '').replace("'", "")
                    v = v.strip()
                    header_lines += f",\n                '{k}': String({v})"

                body_code = f"""{resolve_headers_code}
        const sessionCookie = this.sessionCookies.find(c => c.name === 'session');
        const cookieHeader = sessionCookie ? `session=${{sessionCookie.value}}` : '';
        {query_def}const response = await fetch({url_expr}, {{
            method: '{act.api_method}',
            headers: {{
                {header_lines}
            }},{body_line}
        }});
        return response.json();"""
            else:
                frame_selector = ""
                for p in params:
                    if p.get("name") == "_frame_selector":
                        frame_selector = p.get("selector", "")
                        break
                    elif p.get("frame_selector"):
                        frame_selector = p.get("frame_selector", "")
                        break

                target_expr = f'this.page.frameLocator("{frame_selector}")' if frame_selector else 'this.page'
                fill_actions = ""
                for p in params:
                    if p["name"] == "_frame_selector":
                        continue
                    fill_actions += f'\n        await {target_expr}.fill("{p["selector"]}", String({p["name"]}));'

                trigger_click = ""
                if act.name == "login":
                    trigger_click = f'\n        await {target_expr}.click("#login-submit-btn");'
                elif act.name == "search_products":
                    trigger_click = f'\n        await {target_expr}.click("#search-submit-btn");'
                elif act.name == "checkout":
                    trigger_click = f'\n        await {target_expr}.click("#checkout-submit-btn");'
                else:
                    trigger_click = f'\n        await {target_expr}.click("{act.selector}");'

                nav_target = ""
                if act.name == "login":
                    nav_target = '\n        await this.page.goto(`${this.rootUrl}/login`);'
                elif act.name == "search_products":
                    nav_target = '\n        await this.page.goto(`${this.rootUrl}/catalog`);'
                elif act.name == "checkout":
                    nav_target = '\n        await this.page.goto(`${this.rootUrl}/checkout`);'

                body_code = f"""{nav_target}{fill_actions}{trigger_click}
        await this.page.waitForLoadState("networkidle");
        this.sessionCookies = await this.context.cookies();
        try {{
            this.sessionLocalStorage = JSON.parse(await this.page.evaluate(() => JSON.stringify(localStorage)) || '{{}}');
            this.sessionSessionStorage = JSON.parse(await this.page.evaluate(() => JSON.stringify(sessionStorage)) || '{{}}');
        }} catch (e) {{
            this.sessionLocalStorage = {{}};
            this.sessionSessionStorage = {{}};
        }}"""

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
    private sessionCookies: any[] = [];
    private sessionLocalStorage: any = {{}};
    private sessionSessionStorage: any = {{}};

    async start(headless: boolean = true, sessionData?: any): Promise<ShinyFishstickSiteSDK> {{
        this.browser = await chromium.launch({{ headless }});
        this.context = await this.browser.newContext();
        this.page = await this.context.newPage();

        if (sessionData) {{
            if (sessionData.cookies) {{
                await this.context.addCookies(sessionData.cookies);
            }}
            await this.page.goto(this.rootUrl);
            if (sessionData.localStorage) {{
                await this.page.evaluate((ls) => {{
                    for (let k in ls) localStorage.setItem(k, ls[k]);
                }}, sessionData.localStorage);
            }}
            if (sessionData.sessionStorage) {{
                await this.page.evaluate((ss) => {{
                    for (let k in ss) sessionStorage.setItem(k, ss[k]);
                }}, sessionData.sessionStorage);
            }}
            this.sessionCookies = sessionData.cookies || [];
            this.sessionLocalStorage = sessionData.localStorage || {{}};
            this.sessionSessionStorage = sessionData.sessionStorage || {{}};
        }} else {{
            await this.page.goto(this.rootUrl);
            this.sessionCookies = [];
            this.sessionLocalStorage = {{}};
            this.sessionSessionStorage = {{}};
        }}
        return this;
    }}

    async exportSession(): Promise<any> {{
        return {{
            cookies: this.sessionCookies || [],
            localStorage: this.sessionLocalStorage || {{}},
            sessionStorage: this.sessionSessionStorage || {{}}
        }};
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

    def generate_mcp_server(self, actions: list) -> str:
        mcp_tools = []
        for act in actions:
            params = json.loads(act.parameters or "[]")
            properties = {}
            required = []
            for p in params:
                properties[p["name"]] = {
                    "type": "string" if p["type"] == "string" else "integer",
                    "description": f"Value for: {p['name']}"
                }
                if p.get("required", True):
                    required.append(p["name"])
            mcp_tools.append({
                "name": act.name,
                "description": act.description,
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            })

        mcp_tools_json = json.dumps(mcp_tools, indent=4)

        template = f"""# Shiny Fishstick Generated Model Context Protocol (MCP) Server
import sys
import json
import traceback
from sdk import ShinyFishstickSiteSDK

sdk = ShinyFishstickSiteSDK()
sdk_started = False

TOOLS = {mcp_tools_json}

def handle_request(req):
    global sdk_started
    method = req.get("method")
    params = req.get("params", {{}})
    req_id = req.get("id")

    if method == "initialize":
        return {{
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {{
                "protocolVersion": "2024-11-05",
                "capabilities": {{
                    "tools": {{}}
                }},
                "serverInfo": {{
                    "name": "Shiny-Fishstick-MCP-Server",
                    "version": "1.0.0"
                }}
            }}
        }}

    elif method == "notifications/initialized":
        if not sdk_started:
            print("[MCP Server] Starting site SDK...", file=sys.stderr)
            sdk.start(headless=True)
            sdk_started = True
        return None

    elif method == "tools/list":
        return {{
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {{
                "tools": TOOLS
            }}
        }}

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {{}})

        if not sdk_started:
            print("[MCP Server] Auto-starting site SDK...", file=sys.stderr)
            sdk.start(headless=True)
            sdk_started = True

        print(f"[MCP Server] Calling tool {{tool_name}} with arguments {{arguments}}", file=sys.stderr)

        try:
            if not hasattr(sdk, tool_name):
                return {{
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {{
                        "content": [{{"type": "text", "text": f"Error: Tool '{{tool_name}}' not found in SDK."}}],
                        "isError": True
                    }}
                }}

            method_to_call = getattr(sdk, tool_name)
            res = method_to_call(**arguments)

            res_text = ""
            if res is not None:
                res_text = f"Result: {{json.dumps(res)}}"
            else:
                res_text = f"Action '{{tool_name}}' executed successfully."

            return {{
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {{
                    "content": [{{"type": "text", "text": res_text}}]
                }}
            }}
        except Exception as e:
            err_msg = f"Error executing '{{tool_name}}': {{str(e)}}\\n{{traceback.format_exc()}}"
            print(f"[MCP Server] {{err_msg}}", file=sys.stderr)
            return {{
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {{
                    "content": [{{"type": "text", "text": err_msg}}],
                    "isError": True
                }}
            }}

    elif method == "shutdown":
        if sdk_started:
            print("[MCP Server] Closing SDK session...", file=sys.stderr)
            sdk.close()
            sdk_started = False
        return {{
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {{}}
        }}

    elif method == "exit":
        sys.exit(0)

    else:
        if req_id is not None:
            return {{
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {{
                    "code": -32601,
                    "message": f"Method not found: {{method}}"
                }}
            }}
        return None

def main():
    print("[MCP Server] Running JSON-RPC stdio server...", file=sys.stderr)
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except Exception as e:
                print(f"[MCP Server] Invalid JSON: {{e}}", file=sys.stderr)
                continue

            resp = handle_request(req)
            if resp:
                sys.stdout.write(json.dumps(resp) + "\\n")
                sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        global sdk_started
        if sdk_started:
            sdk.close()

if __name__ == "__main__":
    main()
"""
        return template

    def generate_sdk_tests(self, root_url: str, workflows: list) -> str:
        test_methods = ""
        for wf in workflows:
            steps = json.loads(wf.steps)
            step_code = ""
            for idx, step in enumerate(steps):
                act_name = step["action"]
                if act_name == "login":
                    step_code += f"\n            # Step {idx}: login\n            print('Executing login...', flush=True)\n            sdk.login('admin@example.com', 'password123')"
                elif act_name == "search_products":
                    step_code += f"\n            # Step {idx}: search_products\n            print('Executing search_products...', flush=True)\n            sdk.search_products('Quantum')"
                elif act_name == "add_to_cart":
                    step_code += f"\n            # Step {idx}: add_to_cart\n            print('Executing add_to_cart...', flush=True)\n            res = sdk.add_to_cart('2')\n            self.assertIsNotNone(res)\n            self.assertEqual(res.get('status'), 'success')"
                elif act_name == "checkout":
                    step_code += f"\n            # Step {idx}: checkout\n            print('Executing checkout...', flush=True)\n            sdk.checkout()"
                else:
                    step_code += f"\n            # Step {idx}: {act_name}\n            print('Executing {act_name}...', flush=True)\n            sdk.{act_name}()"

                # Append assertions code if configured
                action_obj = self.db.query(Action).filter(
                    Action.project_id == self.project_id,
                    Action.name == act_name
                ).first()
                if action_obj and action_obj.assertions:
                    try:
                        assertions_list = json.loads(action_obj.assertions)
                        for assert_item in assertions_list:
                            atype = assert_item.get("type")
                            asel = assert_item.get("selector", "")
                            aval = assert_item.get("value", "")

                            cleaned_val = aval.replace("'", "\\'")
                            cleaned_sel = asel.replace("'", "\\'")

                            if atype == "visible":
                                step_code += f"\n            self.assertTrue(sdk.page.locator('{cleaned_sel}').is_visible())"
                            elif atype == "not_visible":
                                step_code += f"\n            self.assertFalse(sdk.page.locator('{cleaned_sel}').is_visible())"
                            elif atype == "contains_text":
                                step_code += f"\n            self.assertIn('{cleaned_val}', sdk.page.locator('{cleaned_sel}').inner_text())"
                            elif atype == "url_equals":
                                step_code += f"\n            self.assertEqual(sdk.page.url, '{cleaned_val}')"
                    except Exception:
                        pass

            test_methods += f"""
    def test_{wf.name}(self):
        \"\"\"Test workflow: {wf.description}\"\"\"
        sdk = ShinyFishstickSiteSDK("{root_url}")
        print("Launching Playwright E2E SDK...", flush=True)
        sdk.start(headless=True)
        try:{step_code}
            print("Workflow test_{wf.name} passed successfully!", flush=True)
        finally:
            sdk.close()
"""

        test_suite_template = f"""# Auto-generated E2E Integration Test Suite
import unittest
import sys
import os

# Ensure specs folder is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sdk import ShinyFishstickSiteSDK

class TestShinyFishstickE2E(unittest.TestCase):
{test_methods}

if __name__ == "__main__":
    unittest.main()
"""
        return test_suite_template
