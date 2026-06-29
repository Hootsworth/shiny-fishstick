from unittest.mock import MagicMock, patch

from backend.app.services.sandbox_orchestrator import SandboxOrchestrator


def test_sandbox_orchestrator_lifecycle():
    orchestrator = SandboxOrchestrator()

    # Mock _is_port_in_use to False
    orchestrator._is_port_in_use = MagicMock(return_value=False)

    with patch("subprocess.Popen") as mock_popen, patch("requests.get") as mock_get:
        mock_process = MagicMock()
        mock_process.pid = 9999
        mock_popen.return_value = mock_process

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # 1. Start sandbox
        res = orchestrator.start_sandbox(8090)
        assert res["status"] == "success"
        assert res["port"] == 8090
        assert res["pid"] == 9999
        assert 8090 in orchestrator.active_processes

        # Start again (should return running status)
        res_again = orchestrator.start_sandbox(8090)
        assert res_again["status"] == "running"
        assert res_again["pid"] == 9999

        # List sandboxes
        lst = orchestrator.list_sandboxes()
        assert lst == {8090: 9999}

        # 2. Stop sandbox
        stop_res = orchestrator.stop_sandbox(8090)
        assert stop_res["status"] == "stopped"
        assert 8090 not in orchestrator.active_processes

        # Stop non-existent
        stop_fail = orchestrator.stop_sandbox(9999)
        assert stop_fail["status"] == "not_found"
