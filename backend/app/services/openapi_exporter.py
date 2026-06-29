import json

import yaml
from sqlalchemy.orm import Session

from ..models.db_models import Action, Project


class OpenAPIExporterService:
    def __init__(self, db: Session, project_id: str):
        self.db = db
        self.project_id = project_id

    def export_openapi_spec(self) -> str:
        project = self.db.query(Project).filter(Project.id == self.project_id).first()
        root_url = project.root_url if project else "http://localhost:8001"

        api_actions = self.db.query(Action).filter(
            Action.project_id == self.project_id,
            Action.action_type == "api"
        ).all()

        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{project.name if project else 'Shiny Fishstick'} Discovered API",
                "version": "1.0.0",
                "description": "Auto-discovered REST API routes upgraded from browser user actions."
            },
            "servers": [
                {"url": root_url}
            ],
            "paths": {}
        }

        for act in api_actions:
            path = act.api_url or "/api/unknown"
            if not path.startswith("/"):
                path = "/" + path

            method = (act.api_method or "POST").lower()

            if path not in spec["paths"]:
                spec["paths"][path] = {}

            params = json.loads(act.parameters or "[]")

            query_params = []
            header_params = []
            body_props = {}

            for p in params:
                p["name"]
                src = p.get("source", "")

                if src.startswith("query."):
                    query_key = src.split("query.")[1]
                    query_params.append({
                        "name": query_key,
                        "in": "query",
                        "required": p.get("required", True),
                        "schema": {
                            "type": "string" if p["type"] == "string" else "integer"
                        }
                    })
                elif src.startswith("header."):
                    header_key = src.split("header.")[1]
                    header_params.append({
                        "name": header_key,
                        "in": "header",
                        "required": p.get("required", True),
                        "schema": {
                            "type": "string" if p["type"] == "string" else "integer"
                        }
                    })
                elif src.startswith("body."):
                    body_key = src.split("body.")[1]
                    body_props[body_key] = {
                        "type": "string" if p["type"] == "string" else "integer"
                    }

            operation = {
                "summary": act.description or f"Discovered {act.name} action route",
                "description": f"Triggered semantically by intent: {act.intent}",
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
            }

            if query_params or header_params:
                operation["parameters"] = query_params + header_params

            if body_props:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": body_props
                            }
                        }
                    }
                }

            spec["paths"][path][method] = operation

        return yaml.dump(spec, sort_keys=False)
