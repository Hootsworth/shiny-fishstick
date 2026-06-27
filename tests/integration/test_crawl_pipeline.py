import os
import subprocess
import sys
import time

import requests

# Add workspace to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))
sys.path.append(BASE_DIR)

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Action, Crawl, Project, Workflow
from backend.app.services.crawler import CrawlerService
from backend.app.services.generator import SDKGeneratorService
from backend.app.services.workflow import WorkflowDiscoveryService


def test_crawl_pipeline():
    # 1. Start Mock Store on port 8001
    print("Starting Mock E-Commerce Store on port 8001...")
    mock_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.mock_site.main:app", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for mock store to boot
    time.sleep(3)
    try:
        res = requests.get("http://localhost:8001/login")
        if res.status_code == 200:
            print("Mock Store successfully started!")
    except Exception as e:
        print(f"Failed to connect to Mock Store: {e}")
        mock_proc.terminate()
        raise e

    # 2. Setup SQLite tables
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Clean previous runs
    db.query(Action).delete()
    db.query(Workflow).delete()
    db.query(Crawl).delete()
    db.query(Project).delete()
    db.commit()

    # 3. Create Project
    print("Creating Project...")
    project = Project(name="Mock Store Test", root_url="http://localhost:8001")
    db.add(project)
    db.commit()
    db.refresh(project)
    project_id = project.id

    # Create Crawl record
    crawl = Crawl(project_id=project_id, status="pending")
    db.add(crawl)
    db.commit()
    db.refresh(crawl)

    # 4. Run Crawler
    print("Running crawler analysis...")
    import asyncio
    crawler = CrawlerService(db, project_id, crawl.id, "http://localhost:8001")
    asyncio.run(crawler.crawl())

    # Re-open session to refresh SQLAlchemy entity cache
    db.close()
    db = SessionLocal()

    # Debug actions in DB
    print("DEBUG ACTIONS IN DB:")
    for act in db.query(Action).all():
        print(f"  Action: name={act.name}, type={act.action_type}, intent={act.intent}, selector={act.selector}")

    # 5. Build Workflows
    print("Building workflows...")
    wf_service = WorkflowDiscoveryService(db, project_id)
    wf_service.discover_and_save()

    # 6. Generate SDK
    print("Compiling specs and generating SDK...")
    sdk_service = SDKGeneratorService(db, project_id)
    sdk_service.generate_all()

    # Close DB session
    db.close()

    print("\n--- Spec compilation complete! ---")

    # Read generated yaml
    yaml_path = os.path.join(BASE_DIR, "shared/specs/preflight.yaml")
    if os.path.exists(yaml_path):
        print(f"YAML Spec generated successfully at: {yaml_path}")
        with open(yaml_path, "r") as f:
            print(f.read())

    # 7. Execute generated Python SDK!
    print("Executing integration verification using generated Python SDK...")
    sdk_path = os.path.join(BASE_DIR, "shared/specs/sdk.py")
    if not os.path.exists(sdk_path):
        print("Error: SDK file was not created!")
        mock_proc.terminate()
        sys.exit(1)

    # Append shared/specs to path so we can import the generated SDK
    sys.path.append(os.path.join(BASE_DIR, "shared/specs"))

    try:
        from sdk import ShinyFishstickSiteSDK

        # Instantiate generated SDK
        sdk = ShinyFishstickSiteSDK("http://localhost:8001")
        print("Launching Playwright via generated SDK...")
        sdk.start(headless=True)

        print("Executing: sdk.login('admin@example.com', 'password123')...")
        sdk.login("admin@example.com", "password123")

        print("Executing: sdk.search_products('Quantum')...")
        sdk.search_products("Quantum")

        print("Executing: sdk.add_to_cart('2')...")
        res_cart = sdk.add_to_cart("2")
        print(f"Cart response: {res_cart}")

        print("Executing: sdk.checkout()...")
        sdk.checkout()

        print("Closing SDK session...")
        sdk.close()

        print("\n🏆 VERIFICATION SUCCESSFUL! The generated SDK executed the workflow successfully!")

    except Exception as e:
        print(f"Error executing generated SDK: {e}")
        mock_proc.terminate()
        raise e

    # Clean up mock store
    mock_proc.terminate()
    print("Cleaned up processes. Verification complete.")

if __name__ == "__main__":
    test_crawl_pipeline()
