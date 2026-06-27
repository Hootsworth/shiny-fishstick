import json
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.app.core.database import Base, engine, get_db
from backend.app.models.db_models import Action, Crawl, Project, SpecVersion, Workflow
from backend.app.schemas.pyd_models import (
    ActionResponse,
    CrawlResponse,
    ProjectCreate,
    ProjectResponse,
)
from backend.app.services.generator import SDKGeneratorService
from backend.app.services.updater import SpecUpdaterService

# Initialize database schemas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shiny Fishstick API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(name=project.name, root_url=project.root_url)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/api/projects", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@app.get("/api/projects/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    crawls = db.query(Crawl).filter(Crawl.project_id == project_id).all()
    actions = db.query(Action).filter(Action.project_id == project_id).all()
    workflows = db.query(Workflow).filter(Workflow.project_id == project_id).all()

    return {
        "id": project.id,
        "name": project.name,
        "root_url": project.root_url,
        "created_at": project.created_at,
        "crawls": [c.id for c in crawls],
        "actions_count": len(actions),
        "workflows_count": len(workflows)
    }

# Async Task enqueued to arq worker
@app.post("/api/projects/{project_id}/crawl")
async def trigger_crawl(project_id: str, db: Session = Depends(get_db)):
    import os

    from arq import create_pool
    from arq.connections import RedisSettings

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    crawl = Crawl(project_id=project_id, status="pending")
    db.add(crawl)
    db.commit()
    db.refresh(crawl)

    redis_dsn = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    pool = await create_pool(RedisSettings.from_dsn(redis_dsn))
    await pool.enqueue_job("crawl_task", project_id, crawl.id, project.root_url)

    return {"message": "Crawl triggered", "crawl_id": crawl.id}

@app.get("/api/crawls/{crawl_id}", response_model=CrawlResponse)
def get_crawl_status(crawl_id: str, db: Session = Depends(get_db)):
    crawl = db.query(Crawl).filter(Crawl.id == crawl_id).first()
    if not crawl:
        raise HTTPException(status_code=404, detail="Crawl not found")
    return crawl

@app.get("/api/projects/{project_id}/actions", response_model=List[ActionResponse])
def get_actions(project_id: str, db: Session = Depends(get_db)):
    return db.query(Action).filter(Action.project_id == project_id).all()

@app.get("/api/projects/{project_id}/workflows")
def get_workflows(project_id: str, db: Session = Depends(get_db)):
    workflows = db.query(Workflow).filter(Workflow.project_id == project_id).all()
    out = []
    for w in workflows:
        out.append({
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "steps": json.loads(w.steps)
        })
    return out

@app.get("/api/projects/{project_id}/spec")
def get_yaml_spec(project_id: str, db: Session = Depends(get_db)):
    spec = db.query(SpecVersion).filter(SpecVersion.project_id == project_id).order_by(SpecVersion.created_at.desc()).first()
    if not spec:
        raise HTTPException(status_code=404, detail="Specification not generated yet")
    return PlainTextResponse(content=spec.yaml_content)

@app.get("/api/projects/{project_id}/sdk/{lang}")
def get_sdk(project_id: str, lang: str, db: Session = Depends(get_db)):
    generator = SDKGeneratorService(db, project_id)
    sdks = generator.generate_all()

    if lang.lower() == "python":
        return PlainTextResponse(content=sdks["python"])
    elif lang.lower() in ["ts", "typescript"]:
        return PlainTextResponse(content=sdks["typescript"])
    elif lang.lower() == "yaml":
        return PlainTextResponse(content=sdks["yaml"])
    else:
        raise HTTPException(status_code=400, detail="Unsupported language. Use 'python', 'typescript' or 'yaml'")

@app.get("/api/projects/{project_id}/deltas")
def get_project_deltas(
    project_id: str,
    crawl_1: str = None,
    crawl_2: str = None,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    updater = SpecUpdaterService(db, project_id)

    c1_id = crawl_1
    c2_id = crawl_2

    if not c1_id or not c2_id:
        crawls = updater.get_latest_completed_crawls(project_id, limit=2)
        if len(crawls) < 2:
            return {
                "project_id": project_id,
                "message": "Fewer than 2 completed crawls found. Cannot perform comparison.",
                "deltas": {}
            }
        if not c2_id:
            c2_id = crawls[0].id
        if not c1_id:
            c1_id = crawls[1].id

    deltas = updater.compare_crawls(c1_id, c2_id)
    return {
        "project_id": project_id,
        "crawl_1_id": c1_id,
        "crawl_2_id": c2_id,
        "deltas": deltas
    }
