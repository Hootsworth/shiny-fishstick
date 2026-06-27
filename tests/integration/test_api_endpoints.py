from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_ready_endpoint():
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json() == {"status": "ready", "db": "ok"}

def test_list_projects_endpoint():
    res = client.get("/api/projects")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_update_action_endpoint():
    import json

    from backend.app.core.database import SessionLocal
    from backend.app.models.db_models import Action, Project

    db = SessionLocal()
    try:
        # Create mock project
        project = Project(name="API Test Proj", root_url="http://localhost:8001")
        db.add(project)
        db.commit()

        # Create mock action
        action = Action(
            project_id=project.id,
            name="checkout",
            intent="checkout",
            selector="#checkout-btn",
            action_type="browser"
        )
        db.add(action)
        db.commit()

        # Update action via API
        payload = {
            "description": "Updated action description",
            "assertions": json.dumps([{"type": "visible", "selector": "#banner"}])
        }
        res = client.put(f"/api/actions/{action.id}", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["description"] == "Updated action description"
        assert "#banner" in data["assertions"]

    finally:
        db.query(Action).filter(Action.project_id == project.id).delete()
        db.query(Project).filter(Project.id == project.id).delete()
        db.commit()
        db.close()

def test_update_workflow_endpoint():
    import json

    from backend.app.core.database import SessionLocal
    from backend.app.models.db_models import Project, Workflow

    db = SessionLocal()
    try:
        # Create mock project
        project = Project(name="API Test Proj 2", root_url="http://localhost:8001")
        db.add(project)
        db.commit()

        # Create mock workflow
        wf = Workflow(
            project_id=project.id,
            name="test_flow",
            description="Initial desc",
            steps="[]"
        )
        db.add(wf)
        db.commit()

        # Update workflow via API
        payload = {
            "name": "Updated test_flow",
            "description": "Updated desc",
            "steps": [
                {"action": "login", "source_page": "/login", "target_page": "/dashboard"}
            ]
        }
        res = client.put(f"/api/workflows/{wf.id}", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "Updated test_flow"
        assert data["description"] == "Updated desc"
        steps = json.loads(data["steps"])
        assert len(steps) == 1
        assert steps[0]["action"] == "login"

    finally:
        db.query(Workflow).filter(Workflow.project_id == project.id).delete()
        db.query(Project).filter(Project.id == project.id).delete()
        db.commit()
        db.close()
