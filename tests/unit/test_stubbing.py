from backend.app.services.stubbing import MockStubEngine


def test_stubbing_engine_registration_and_retrieval():
    engine = MockStubEngine()

    # Register stubs
    engine.register_stub(
        url_pattern=r"http://localhost:8001/api/v1/users/.*",
        method="GET",
        status=200,
        body='{"username": "chaos_monkey"}',
        headers={"Content-Type": "application/json"}
    )

    # Validate correct match
    stub = engine.get_stub("GET", "http://localhost:8001/api/v1/users/12345")
    assert stub is not None
    assert stub["status"] == 200
    assert stub["body"] == '{"username": "chaos_monkey"}'

    # Validate incorrect method mismatch
    stub_fail_method = engine.get_stub("POST", "http://localhost:8001/api/v1/users/12345")
    assert stub_fail_method is None

    # Validate URL regex mismatch
    stub_fail_url = engine.get_stub("GET", "http://localhost:8001/api/v2/users/123")
    assert stub_fail_url is None

    # List registered stubs
    stubs_list = engine.list_stubs()
    assert len(stubs_list) == 1
    assert stubs_list[0]["method"] == "GET"

    # Clear stubs
    engine.clear_stubs()
    assert len(engine.list_stubs()) == 0
