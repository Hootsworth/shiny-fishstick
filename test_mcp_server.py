# Test script for verifying the generated MCP server
import subprocess
import json
import time
import os
import sys
import requests

def test_mcp():
    # 1. Check if Mock Store is already running on port 8001
    print("Checking if Mock E-Commerce Store is already running on port 8001...")
    mock_proc = None
    try:
        res = requests.get("http://localhost:8001/login", timeout=2)
        if res.status_code == 200:
            print("Mock Store is already running!")
    except Exception:
        print("Starting Mock E-Commerce Store on port 8001...")
        mock_proc = subprocess.Popen(
            ["/Users/adityadixit/Documents/Code/Preflight Designer/backend/venv/bin/python", "-m", "uvicorn", "backend.mock_site.main:app", "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Wait for mock store to boot
        time.sleep(3)
        try:
            res = requests.get("http://localhost:8001/login")
            if res.status_code == 200:
                print("Mock Store successfully started!")
        except Exception as e:
            print(f"Failed to connect to Mock Store: {e}")
            if mock_proc:
                mock_proc.terminate()
            sys.exit(1)

    print("Starting MCP Server test...")
    specs_dir = "/Users/adityadixit/Documents/Code/Preflight Designer/shared/specs"
    mcp_script = os.path.join(specs_dir, "mcp_server.py")
    
    if not os.path.exists(mcp_script):
        print(f"Error: {mcp_script} not found! Compile spec first.")
        if mock_proc:
            mock_proc.terminate()
        sys.exit(1)
        
    env = os.environ.copy()
    env["PYTHONPATH"] = specs_dir
    
    # Start the MCP server process using python
    proc = subprocess.Popen(
        ["/Users/adityadixit/Documents/Code/Preflight Designer/backend/venv/bin/python", mcp_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    try:
        # 1. Send initialize request
        print("Sending 'initialize' request...")
        init_req = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()
        
        line = proc.stdout.readline()
        print("Initialize Response:", line)
        assert "result" in json.loads(line), "Initialize response should contain result"
        
        # 2. Send initialized notification
        print("Sending 'notifications/initialized' notification...")
        init_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        proc.stdin.write(json.dumps(init_notif) + "\n")
        proc.stdin.flush()
        
        time.sleep(1) # wait for initialization
        
        # 3. Send tools/list request
        print("Sending 'tools/list' request...")
        list_req = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/list",
            "params": {}
        }
        proc.stdin.write(json.dumps(list_req) + "\n")
        proc.stdin.flush()
        
        line = proc.stdout.readline()
        print("Tools List Response:", line)
        list_data = json.loads(line)
        assert "tools" in list_data["result"], "Tools list response should contain tools list"
        
        # Verify tools are extracted
        tools = list_data["result"]["tools"]
        print(f"Extracted {len(tools)} tools from MCP server:")
        for t in tools:
            print(f"  - Tool name: {t['name']}, description: {t['description']}")
            
        # 4. Call 'login' tool
        print("Sending 'tools/call' request for login tool...")
        call_req = {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {
                "name": "login",
                "arguments": {
                    "email": "admin@example.com",
                    "password": "password123"
                }
            }
        }
        proc.stdin.write(json.dumps(call_req) + "\n")
        proc.stdin.flush()
        
        line = proc.stdout.readline()
        print("Tool Call Response:", line)
        call_data = json.loads(line)
        assert not call_data.get("result", {}).get("isError"), "Tool call should succeed without error"
        
        # 5. Shutdown
        print("Sending 'shutdown' request...")
        shutdown_req = {
            "jsonrpc": "2.0",
            "id": "4",
            "method": "shutdown",
            "params": {}
        }
        proc.stdin.write(json.dumps(shutdown_req) + "\n")
        proc.stdin.flush()
        
        line = proc.stdout.readline()
        print("Shutdown Response:", line)
        
        print("\n🏆 MCP SERVER TEST SUCCESSFUL! HANDSHAKE, TOOL LISTING, AND CALL VERIFIED!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        # print stderr if available
        try:
            print("Server stderr:")
            proc.terminate()
            stdout, stderr = proc.communicate(timeout=2)
            print(stderr)
        except Exception:
            pass
        if mock_proc:
            mock_proc.terminate()
        sys.exit(1)
    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        if mock_proc:
            mock_proc.terminate()

if __name__ == "__main__":
    test_mcp()
