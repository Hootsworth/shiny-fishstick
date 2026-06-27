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

def test_sdk_tests_assertion_compilation():
    from backend.app.models.db_models import Workflow
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create mock action with assertions
        action = Action(
            project_id="proj-888",
            name="checkout",
            description="Proceed to place the order",
            intent="checkout",
            action_type="browser",
            selector="#checkout-btn",
            parameters="[]",
            assertions=json.dumps([
                {"type": "visible", "selector": "#success-banner"},
                {"type": "contains_text", "selector": ".order-status", "value": "Placed"},
                {"type": "url_equals", "value": "http://localhost:8001/success"}
            ])
        )
        db.add(action)
        db.commit()

        # Create mock workflow
        wf = Workflow(
            project_id="proj-888",
            name="purchase_flow",
            description="Happy path purchase",
            steps=json.dumps([
                {"action": "checkout", "source_page": "/cart", "target_page": "/success"}
            ])
        )
        db.add(wf)
        db.commit()

        generator = SDKGeneratorService(db, "proj-888")
        sdk_tests = generator.generate_sdk_tests("http://localhost:8001", [wf])

        # Assert code contains custom unittest assertions mapped to playwright selectors
        assert "self.assertTrue(sdk.page.locator('#success-banner').is_visible())" in sdk_tests
        assert "self.assertIn('Placed', sdk.page.locator('.order-status').inner_text())" in sdk_tests
        assert "self.assertEqual(sdk.page.url, 'http://localhost:8001/success')" in sdk_tests

    finally:
        db.query(Action).filter(Action.project_id == "proj-888").delete()
        db.query(Workflow).filter(Workflow.project_id == "proj-888").delete()
        db.commit()
        db.close()

def test_rust_sdk_generation_output():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        action = Action(
            project_id="proj-777",
            name="checkout",
            description="Proceed to place the order",
            intent="checkout",
            action_type="api",
            selector="#checkout-btn",
            api_url="/checkout",
            api_method="POST",
            parameters=json.dumps([
                {"name": "cart_id", "type": "string", "source": "body.cart_id"}
            ])
        )
        db.add(action)
        db.commit()

        generator = SDKGeneratorService(db, "proj-777")
        rust_sdk = generator.generate_rust_sdk("http://localhost:8001", [action])

        # Assert correct structures and reqwest/json mapping
        assert "pub struct ShinyFishstickSiteSDK" in rust_sdk
        assert "pub fn checkout(&mut self, cart_id: &str)" in rust_sdk
        assert 'let body = json!({"cart_id": cart_id});' in rust_sdk

    finally:
        db.query(Action).filter(Action.project_id == "proj-777").delete()
        db.commit()
        db.close()
