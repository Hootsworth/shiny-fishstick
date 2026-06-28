from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_websocket_agent_hub_coordination():
    # Connect first agent
    with client.websocket_connect("/api/ws/hub/agent-1") as ws1:
        # Register discovery of seed URLs
        ws1.send_json({
            "type": "discover",
            "urls": ["http://localhost:8001/catalog", "http://localhost:8001/checkout"]
        })

        # Connect second agent
        with client.websocket_connect("/api/ws/hub/agent-2") as ws2:
            # Agent 2 requests work assignment
            ws2.send_json({"type": "request_work"})

            # Agent 2 should receive assigned target URL
            msg2 = ws2.receive_json()
            assert msg2["type"] == "assign"
            assert msg2["url"] in ["http://localhost:8001/catalog", "http://localhost:8001/checkout"]

            # Agent 1 requests work assignment
            ws1.send_json({"type": "request_work"})
            msg1 = ws1.receive_json()
            assert msg1["type"] == "assign"
            assert msg1["url"] in ["http://localhost:8001/catalog", "http://localhost:8001/checkout"]
            assert msg1["url"] != msg2["url"]  # Ensure lock-free route isolation
