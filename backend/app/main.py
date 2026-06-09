import json
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import SessionLocal, engine, Base, get_db
from backend.app.models.db_models import Project, Crawl, Page, Element, Action, Workflow, AuthConfig, SpecVersion
from backend.app.schemas.pyd_models import ProjectCreate, ProjectResponse, CrawlResponse, ActionResponse, WorkflowResponse
from backend.app.services.crawler import CrawlerService
from backend.app.services.workflow import WorkflowDiscoveryService
from backend.app.services.generator import SDKGeneratorService

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

# Async Background Task for Crawling
async def run_crawl_task(project_id: str, crawl_id: str, root_url: str):
    db = SessionLocal()
    try:
        # Run Crawl and DOM Analysis
        crawler = CrawlerService(db, project_id, crawl_id, root_url)
        await crawler.crawl()
        
        # Re-open session to refresh SQLAlchemy entity cache
        db.close()
        db = SessionLocal()
        
        # Discover workflows after crawl completes
        wf_service = WorkflowDiscoveryService(db, project_id)
        wf_service.discover_and_save()
        
        # Compile specs and generate SDKs
        sdk_service = SDKGeneratorService(db, project_id)
        sdk_service.generate_all()
    except Exception as e:
        print(f"[Background Crawl] Error: {e}")
        crawl_obj = db.query(Crawl).filter(Crawl.id == crawl_id).first()
        if crawl_obj:
            crawl_obj.status = "failed"
            crawl_obj.error_message = str(e)
            db.commit()
    finally:
        db.close()

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

@app.post("/api/projects/{project_id}/crawl")
def trigger_crawl(project_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    crawl = Crawl(project_id=project_id, status="pending")
    db.add(crawl)
    db.commit()
    db.refresh(crawl)
    
    background_tasks.add_task(run_crawl_task, project_id, crawl.id, project.root_url)
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
