import json

import yaml

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Action, Project
from backend.app.services.openapi_exporter import OpenAPIExporterService


def test_openapi_exporter_spec_serialization():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create mock project
        project = Project(
            id="proj-open-1",
            name="OpenAPI Spec Proj",
            root_url="http://localhost:8001"
        )
        db.add(project)
        db.commit()

        # Create mock API action
        action = Action(
            project_id="proj-open-1",
            name="add_product",
            description="Adds a product route",
            intent="add_to_cart",
            action_type="api",
            selector="",
            api_url="/api/cart/items",
            api_method="POST",
            parameters=json.dumps([
                {"name": "product_id", "type": "string", "source": "body.product_id", "required": True},
                {"name": "session_tok", "type": "string", "source": "header.Authorization", "required": True}
            ])
        )
        db.add(action)
        db.commit()

        exporter = OpenAPIExporterService(db, "proj-open-1")
        spec_yaml = exporter.export_openapi_spec()
        spec_dict = yaml.safe_load(spec_yaml)

        # Assert correct OpenAPI 3.0 schema values
        assert spec_dict["openapi"] == "3.0.0"
        assert "/api/cart/items" in spec_dict["paths"]
        post_op = spec_dict["paths"]["/api/cart/items"]["post"]

        # Verify body props mapping
        assert "requestBody" in post_op
        body_properties = post_op["requestBody"]["content"]["application/json"]["schema"]["properties"]
        assert "product_id" in body_properties

        # Verify header mapping
        headers = [p for p in post_op["parameters"] if p["in"] == "header"]
        assert len(headers) == 1
        assert headers[0]["name"] == "Authorization"

    finally:
        db.query(Action).filter(Action.project_id == "proj-open-1").delete()
        db.query(Project).filter(Project.id == "proj-open-1").delete()
        db.commit()
        db.close()
