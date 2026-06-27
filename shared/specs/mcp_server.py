# Shiny Fishstick Generated Model Context Protocol (MCP) Server
import sys
import json
import traceback
from sdk import ShinyFishstickSiteSDK

sdk = ShinyFishstickSiteSDK()
sdk_started = False

TOOLS = [
    {
        "name": "login",
        "description": "Logs in the user with credentials",
        "inputSchema": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Value for: email"
                },
                "password": {
                    "type": "string",
                    "description": "Value for: password"
                }
            },
            "required": [
                "email",
                "password"
            ]
        }
    },
    {
        "name": "search_products",
        "description": "Searches for products in the store",
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Value for: q"
                }
            },
            "required": [
                "q"
            ]
        }
    },
    {
        "name": "checkout",
        "description": "Proceeds to place the order and checkout",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "add_to_cart",
        "description": "Adds the current product to the shopping cart",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Value for: product_id"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Value for: quantity"
                }
            },
            "required": [
                "product_id",
                "quantity"
            ]
        }
    }
]

def handle_request(req):
    global sdk_started
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "Shiny-Fishstick-MCP-Server",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        if not sdk_started:
            print("[MCP Server] Starting site SDK...", file=sys.stderr)
            sdk.start(headless=True)
            sdk_started = True
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not sdk_started:
            print("[MCP Server] Auto-starting site SDK...", file=sys.stderr)
            sdk.start(headless=True)
            sdk_started = True

        print(f"[MCP Server] Calling tool {tool_name} with arguments {arguments}", file=sys.stderr)

        try:
            if not hasattr(sdk, tool_name):
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: Tool '{tool_name}' not found in SDK."}],
                        "isError": True
                    }
                }

            method_to_call = getattr(sdk, tool_name)
            res = method_to_call(**arguments)

            res_text = ""
            if res is not None:
                res_text = f"Result: {json.dumps(res)}"
            else:
                res_text = f"Action '{tool_name}' executed successfully."

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": res_text}]
                }
            }
        except Exception as e:
            err_msg = f"Error executing '{tool_name}': {str(e)}\n{traceback.format_exc()}"
            print(f"[MCP Server] {err_msg}", file=sys.stderr)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": err_msg}],
                    "isError": True
                }
            }

    elif method == "shutdown":
        if sdk_started:
            print("[MCP Server] Closing SDK session...", file=sys.stderr)
            sdk.close()
            sdk_started = False
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }

    elif method == "exit":
        sys.exit(0)

    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
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
                print(f"[MCP Server] Invalid JSON: {e}", file=sys.stderr)
                continue

            resp = handle_request(req)
            if resp:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        global sdk_started
        if sdk_started:
            sdk.close()

if __name__ == "__main__":
    main()
