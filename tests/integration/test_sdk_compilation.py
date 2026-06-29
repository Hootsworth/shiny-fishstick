import importlib.util
import os
import subprocess
import sys
import time

import pytest
import requests

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Action, Crawl, Project, Workflow
from backend.app.services.crawler import CrawlerService
from backend.app.services.generator import SDKGeneratorService
from backend.app.services.workflow import WorkflowDiscoveryService


@pytest.fixture(scope="module")
def mock_store_server_compilation():
    print("Starting Mock Store on port 8005...")
    mock_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.mock_site.main:app", "--port", "8005"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    try:
        requests.get("http://localhost:8005/login")
    except Exception as e:
        mock_proc.terminate()
        raise RuntimeError("Could not start mock store on port 8005") from e

    yield "http://localhost:8005"

    mock_proc.terminate()


def test_generated_sdk_compilation_and_execution(mock_store_server_compilation, tmp_path):
    # 1. Setup SQLite tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clean database
    db.query(Action).delete()
    db.query(Workflow).delete()
    db.query(Crawl).delete()
    db.query(Project).delete()
    db.commit()

    # 2. Setup Project
    project = Project(name="Compilation Verification Project", root_url=mock_store_server_compilation)
    db.add(project)
    db.commit()
    db.refresh(project)

    crawl = Crawl(project_id=project.id, status="pending")
    db.add(crawl)
    db.commit()
    db.refresh(crawl)

    # 3. Crawl & Discover
    import asyncio
    crawler = CrawlerService(db, project.id, crawl.id, mock_store_server_compilation)
    asyncio.run(crawler.crawl())

    wf_service = WorkflowDiscoveryService(db, project.id)
    wf_service.discover_and_save()

    # 4. Generate SDK to temp directory
    out_dir = str(tmp_path)
    sdk_service = SDKGeneratorService(db, project.id)
    sdk_service.generate_all(specs_dir=out_dir)
    db.close()

    # Verify sdk.py exists
    sdk_path = os.path.join(out_dir, "sdk.py")
    assert os.path.exists(sdk_path)

    # 5. Dynamically load and import the generated sdk.py
    spec = importlib.util.spec_from_file_location("generated_sdk", sdk_path)
    generated_sdk_module = importlib.util.module_from_spec(spec)
    sys.modules["generated_sdk"] = generated_sdk_module
    spec.loader.exec_module(generated_sdk_module)

    # Instantiate generated SDK class
    sdk_class = getattr(generated_sdk_module, "ShinyFishstickSiteSDK")
    sdk_instance = sdk_class()

    # Run actions via playwright inside the generated SDK
    # The generated login method takes email and password parameters
    sdk_instance.start(headless=True)
    try:
        sdk_instance.login(email="admin@example.com", password="password123")
        assert sdk_instance.page.url.endswith("/catalog")
    finally:
        sdk_instance.close()
