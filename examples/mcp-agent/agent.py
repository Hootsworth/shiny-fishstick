import json
import subprocess
import sys


def run_agent_workflow():
    print("🤖 Shiny Fishstick AI Agent MCP Client Example")
    print("---------------------------------------------")

    # This example demonstrates starting the server and calling tools via standard input/output
    # Start the serve-mcp process
    # In a real environment, you would start: shiny serve-mcp ./shared/specs/preflight.yaml
    print("Starting MCP server connection...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "app.cli", "serve-mcp", "./examples/ecommerce/preflight.yaml"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 1. Initialize MCP Connection
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "mcp-agent-example",
                "version": "1.0.0"
            }
        }
    }
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()

    response = proc.stdout.readline()
    print("-> Server Initialized:", json.loads(response)["result"]["serverInfo"])

    # 2. List tools
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    proc.stdin.write(json.dumps(list_request) + "\n")
    proc.stdin.flush()

    response = proc.stdout.readline()
    tools = json.loads(response)["result"]["tools"]
    print(f"-> Discovered {len(tools)} tools:")
    for t in tools:
        print(f"   * {t['name']}: {t['description']}")

    # 3. Call tool: login
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "login",
            "arguments": {
                "email": "admin@example.com",
                "password": "password123"
            }
        }
    }
    print("\nCalling tool 'login' via MCP tool call...")
    proc.stdin.write(json.dumps(call_request) + "\n")
    proc.stdin.flush()

    response = proc.stdout.readline()
    result = json.loads(response)["result"]
    print("-> Call Result Content:", result["content"])
    print("-> Success Status:", not result.get("isError", False))

    # Terminate process
    proc.terminate()


if __name__ == "__main__":
    run_agent_workflow()
