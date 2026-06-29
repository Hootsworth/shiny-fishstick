import urllib.parse


class SpecValidator:
    @staticmethod
    def validate_spec(spec: dict) -> tuple[bool, list[str]]:
        errors = []

        # 1. Root checks
        if "version" not in spec:
            errors.append("Missing root field: 'version'")
        if "site" not in spec:
            errors.append("Missing root field: 'site'")
        else:
            site = spec["site"]
            parsed = urllib.parse.urlparse(site)
            if not parsed.scheme or not parsed.netloc:
                errors.append(f"Invalid 'site' URL format: '{site}'")

        if "actions" not in spec:
            errors.append("Missing root field: 'actions'")
            return False, errors

        actions = spec["actions"]
        if not isinstance(actions, dict):
            errors.append("'actions' must be a dictionary")
            return False, errors

        # 2. Actions checks
        for name, details in actions.items():
            if not isinstance(details, dict):
                errors.append(f"Action '{name}' details must be a dictionary")
                continue

            # Check action type
            action_type = details.get("action_type")
            if not action_type:
                errors.append(f"Action '{name}' is missing 'action_type'")
            elif action_type not in ["browser", "api"]:
                errors.append(f"Action '{name}' has invalid 'action_type': '{action_type}'")

            # Check selector for browser actions
            if action_type == "browser" and "selector" not in details:
                errors.append(f"Action '{name}' of type 'browser' is missing selector trigger")

            # Validate parameters schema
            params = details.get("parameters")
            if params is not None:
                if not isinstance(params, list):
                    errors.append(f"Action '{name}' parameters must be a list")
                else:
                    for i, p in enumerate(params):
                        if not isinstance(p, dict):
                            errors.append(f"Parameter index {i} in action '{name}' must be a dictionary")
                            continue
                        if "name" not in p:
                            errors.append(f"Parameter index {i} in action '{name}' is missing 'name'")
                        if "type" not in p:
                            errors.append(f"Parameter index {i} in action '{name}' is missing 'type'")
                        elif p["type"] not in ["string", "integer", "boolean"]:
                            errors.append(f"Parameter index {i} in action '{name}' has invalid type: '{p['type']}'")

        return len(errors) == 0, errors
