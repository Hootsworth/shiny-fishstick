import os

from arq.connections import RedisSettings

from backend.app.core.database import SessionLocal
from backend.app.models.db_models import Crawl
from backend.app.services.crawler import CrawlerService
from backend.app.services.generator import SDKGeneratorService
from backend.app.services.workflow import WorkflowDiscoveryService


async def crawl_task(ctx, project_id: str, crawl_id: str, root_url: str):
    db = SessionLocal()
    try:
        print(f"[Background Crawl Worker] Starting crawl for project={project_id}, crawl={crawl_id}")
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
        print(f"[Background Crawl Worker] Completed crawl for project={project_id}, crawl={crawl_id}")
    except Exception as e:
        print(f"[Background Crawl Worker] Error: {e}")
        crawl_obj = db.query(Crawl).filter(Crawl.id == crawl_id).first()
        if crawl_obj:
            crawl_obj.status = "failed"
            db.commit()
    finally:
        db.close()

class WorkerSettings:
    functions = [crawl_task]
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

if __name__ == "__main__":
    import asyncio
    from arq import run_worker
    run_worker(WorkerSettings)
