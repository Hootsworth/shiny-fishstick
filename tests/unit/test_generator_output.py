import json

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Action
from backend.app.services.generator import SDKGeneratorService


def test_sdk_generation_output():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create mock action with frame selector parameters
        action = Action(
            project_id="proj-999",
            name="test_action",
            description="Test action description",
            intent="click",
            action_type="browser",
            selector="#test-btn",
            parameters=json.dumps([
                {"name": "param_1", "type": "string", "selector": "#input-1"},
                {"name": "_frame_selector", "type": "meta", "selector": "#my-iframe"}
            ])
        )
        db.add(action)
        db.commit()

        generator = SDKGeneratorService(db, "proj-999")
        python_sdk = generator.generate_python_sdk("http://localhost:8001", [action])

        # Assert correct method signatures and frame locator wrappers are compiled
        assert "class ShinyFishstickSiteSDK:" in python_sdk
        assert "def test_action(self, param_1):" in python_sdk
        assert 'self.page.frame_locator("#my-iframe").fill("#input-1", str(param_1))' in python_sdk
        assert 'self.page.frame_locator("#my-iframe").click("#test-btn")' in python_sdk

        # Assert metadata is excluded from parameter list
        args_part = python_sdk.split("def test_action(")[1].split(")")[0]
        assert "_frame_selector" not in args_part

    finally:
        db.query(Action).filter(Action.project_id == "proj-999").delete()
        db.commit()
        db.close()
