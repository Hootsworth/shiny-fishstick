import socket
import subprocess
import sys
import time

import requests


class SandboxOrchestrator:
    def __init__(self):
        self.active_processes = {}

    def _is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def start_sandbox(self, port: int) -> dict:
        if port in self.active_processes:
            return {"status": "running", "port": port, "pid": self.active_processes[port].pid}

        if self._is_port_in_use(port):
            raise RuntimeError(f"Port {port} is already in use by another process")

        print(f"[Sandbox Orchestrator] Spawning mock store sandbox on port {port}...", file=sys.stderr)
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.mock_site.main:app", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Wait for startup

        # Verify active endpoint response
        try:
            res = requests.get(f"http://localhost:{port}/login", timeout=2)
            if res.status_code != 200:
                proc.terminate()
                raise RuntimeError(f"Sandbox on port {port} returned status {res.status_code}")
        except Exception as e:
            proc.terminate()
            raise RuntimeError(f"Failed to connect to sandbox on port {port}: {e}")

        self.active_processes[port] = proc
        return {"status": "success", "port": port, "pid": proc.pid}

    def stop_sandbox(self, port: int) -> dict:
        if port not in self.active_processes:
            return {"status": "not_found", "port": port}

        proc = self.active_processes.pop(port)
        proc.terminate()
        proc.wait()
        return {"status": "stopped", "port": port}

    def list_sandboxes(self) -> dict:
        return {port: proc.pid for port, proc in self.active_processes.items()}

    def shutdown_all(self):
        ports = list(self.active_processes.keys())
        for port in ports:
            self.stop_sandbox(port)


# Global singleton instance for app state management
orchestrator = SandboxOrchestrator()
