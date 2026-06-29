from backend.app.services.validator import SpecValidator


def test_specification_validator_checks():
    # 1. Valid spec structure
    valid_spec = {
        "version": "1.0.0",
        "site": "https://example.com",
        "actions": {
            "login": {
                "action_type": "browser",
                "selector": "#submit",
                "parameters": [
                    {"name": "email", "type": "string", "required": True}
                ]
            }
        }
    }
    is_valid, errors = SpecValidator.validate_spec(valid_spec)
    assert is_valid is True
    assert len(errors) == 0

    # 2. Invalid spec structure (missing site, invalid URL format, parameter type mismatch)
    invalid_spec = {
        "version": "1.0.0",
        "site": "invalid-url-path",
        "actions": {
            "search": {
                "action_type": "browser",
                "parameters": [
                    {"name": "query", "type": "float"} # invalid type
                ]
            }
        }
    }
    is_valid, errors = SpecValidator.validate_spec(invalid_spec)
    assert is_valid is False
    assert len(errors) > 0
