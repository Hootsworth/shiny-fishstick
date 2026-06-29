import asyncio
import os
import subprocess
import sys
import time

import requests

# Setup import path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Action, Crawl, Project, Workflow
from backend.app.services.crawler import CrawlerService
from backend.app.services.generator import SDKGeneratorService
from backend.app.services.workflow import WorkflowDiscoveryService


def main():
    print("🐟 Shiny Fishstick E2E Discovery & SDK Compilation Demo 🐟")
    print("=========================================================")

    # 1. Start Mock Store on port 8001
    print("\n[1/5] Starting local Mock Store testbed on port 8001...")
    mock_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.mock_site.main:app", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(3)
    try:
        res = requests.get("http://localhost:8001/login")
        if res.status_code == 200:
            print("  Mock Store successfully running!")
    except Exception as e:
        print(f"  ❌ Error starting mock store: {e}")
        mock_proc.terminate()
        sys.exit(1)

    # 2. Setup SQLite tables
    print("\n[2/5] Initializing local database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Pre-clean tables
    db.query(Action).delete()
    db.query(Workflow).delete()
    db.query(Crawl).delete()
    db.query(Project).delete()
    db.commit()

    project = Project(name="Mock Store Demo", root_url="http://localhost:8001")
    db.add(project)
    db.commit()
    db.refresh(project)

    crawl = Crawl(project_id=project.id, status="pending")
    db.add(crawl)
    db.commit()
    db.refresh(crawl)

    # 3. Run Crawler
    print("\n[3/5] Launching browser crawl analysis on target pages...")
    crawler = CrawlerService(db, project.id, crawl.id, "http://localhost:8001")
    asyncio.run(crawler.crawl())

    # 4. Discover Workflows
    print("\n[4/5] Discovering workflows and building FSM transitions...")
    wf_service = WorkflowDiscoveryService(db, project.id)
    wf_service.discover_and_save()

    # 5. Generate SDK
    print("\n[5/5] Generating OpenAPI YAML specs, clients SDKs, and MCP servers...")
    sdk_service = SDKGeneratorService(db, project.id)
    sdk_service.generate_all()

    # Close DB and clean mock store
    db.close()
    mock_proc.terminate()

    print("\n=========================================================")
    print("✨ Demo execution complete!")
    print("Generated files successfully saved to './shared/specs/':")
    print("  * preflight.yaml  (OpenAPI-style actions dictionary)")
    print("  * sdk.py          (Python Client SDK)")
    print("  * sdk.ts          (TypeScript Client SDK)")
    print("  * sdk.rs          (Rust Client SDK)")
    print("  * mcp_server.py   (Model Context Protocol Server)")
    print("=========================================================")


if __name__ == "__main__":
    main()
