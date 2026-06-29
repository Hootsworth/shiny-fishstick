import re


class MockStubEngine:
    def __init__(self):
        # Maps (method, url_pattern_regex) -> stub details
        self.stubs = {}

    def register_stub(self, url_pattern: str, method: str, status: int, body: str, headers: dict = None):
        method = method.upper()
        # Compile regex pattern to match requested urls
        try:
            pattern_regex = re.compile(url_pattern)
        except re.error as e:
            raise ValueError(f"Invalid URL pattern regex: {e}")

        self.stubs[(method, url_pattern)] = {
            "regex": pattern_regex,
            "status": status,
            "body": body,
            "headers": headers or {"Content-Type": "application/json"}
        }

    def get_stub(self, method: str, url: str) -> dict:
        method = method.upper()
        for (m, pattern), stub in self.stubs.items():
            if m == method and stub["regex"].search(url):
                return stub
        return None

    def clear_stubs(self):
        self.stubs.clear()

    def list_stubs(self) -> list:
        return [
            {"method": m, "pattern": pattern, "status": s["status"]}
            for (m, pattern), s in self.stubs.items()
        ]


# Global singleton instance for app state management
stub_engine = MockStubEngine()
