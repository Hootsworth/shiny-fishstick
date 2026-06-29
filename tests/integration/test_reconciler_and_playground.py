import os
import sys
import time
import subprocess
import requests
import json
import pytest
from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Action, Project
from backend.app.services.playground import PlaygroundService
from backend.app.services.state_reconciler import StateReconcilerService


@pytest.fixture(scope="module")
def mock_store_server():
    print("Starting Mock Store on port 8002...")
    mock_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.mock_site.main:app", "--port", "8002"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    try:
        requests.get("http://localhost:8002/login")
    except Exception as e:
        mock_proc.terminate()
        raise RuntimeError("Could not start mock store") from e

    yield "http://localhost:8002"

    mock_proc.terminate()


@pytest.mark.anyio
async def test_playground_and_reconciler_live_integration(mock_store_server, mocker):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        db.query(Action).filter(Action.project_id == "proj-live-1").delete()
        db.query(Project).filter(Project.id == "proj-live-1").delete()
        db.commit()

        proj = Project(id="proj-live-1", name="Live Test Store", root_url=mock_store_server)
        db.add(proj)
        db.commit()

        act = Action(
            id="act-live-1",
            project_id="proj-live-1",
            name="login",
            intent="login",
            action_type="browser",
            selector="#login-submit-btn",
            parameters=json.dumps([
                {"name": "email", "type": "string", "selector": "#email"},
                {"name": "password", "type": "string", "selector": "#password"}
            ]),
            assertions=json.dumps([
                {"type": "visible", "selector": "#search-form"},
                {"type": "url_equals", "value": f"{mock_store_server}/catalog"}
            ])
        )
        db.add(act)
        db.commit()

        playground = PlaygroundService(db)
        res = await playground.execute_action(
            project_id="proj-live-1",
            action_id="act-live-1",
            parameters={"email": "admin@example.com", "password": "password123"}
        )

        print("PLAYGROUND ERROR:", res.get("error"), "ASSERTIONS:", res.get("assertion_results"))
        assert res["success"] is True
        assert len(res["screenshot"]) > 0
        assert len(res["assertion_results"]) == 2
        assert res["assertion_results"][0]["passed"] is True
        assert res["assertion_results"][1]["passed"] is True

        reconciler = StateReconcilerService(db)
        recon_res = await reconciler.reconcile_action_drift(
            action_id="act-live-1",
            prod_url=f"{mock_store_server}/login",
            staging_url=f"{mock_store_server}/login"
        )
        assert recon_res["success"] is True
        assert recon_res["prod_exists"] is True
        assert recon_res["staging_exists"] is True
        assert recon_res["drift_detected"] is False

    finally:
        db.query(Action).filter(Action.project_id == "proj-live-1").delete()
        db.query(Project).filter(Project.id == "proj-live-1").delete()
        db.commit()
        db.close()
