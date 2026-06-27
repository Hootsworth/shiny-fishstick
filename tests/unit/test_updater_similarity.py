import json

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Crawl, Element, Page, Project
from backend.app.services.updater import SpecUpdaterService


def test_updater_crawls_drift():
    # Setup test database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create Project
        project = Project(name="Drift Test Project", root_url="http://localhost:9999")
        db.add(project)
        db.commit()
        db.refresh(project)

        # 1. Create Baseline Crawl
        crawl_1 = Crawl(project_id=project.id, status="completed")
        db.add(crawl_1)
        db.commit()
        db.refresh(crawl_1)

        page_1 = Page(crawl_id=crawl_1.id, url="http://localhost:9999/catalog", path="/catalog", title="Catalog")
        db.add(page_1)
        db.commit()
        db.refresh(page_1)

        # Add elements for Page 1
        el_1_1 = Element(
            page_id=page_1.id,
            tag_name="button",
            selector="#btn-add-to-cart",
            element_type="button",
            text_content="Add to Cart",
            attributes=json.dumps({"id": "btn-add-to-cart", "class": "btn btn-primary"})
        )
        el_1_2 = Element(
            page_id=page_1.id,
            tag_name="input",
            selector="#search-input",
            element_type="input",
            text_content="",
            attributes=json.dumps({"id": "search-input", "name": "q", "type": "text"})
        )
        el_1_3 = Element(
            page_id=page_1.id,
            tag_name="button",
            selector="#btn-delete-item",
            element_type="button",
            text_content="Delete",
            attributes=json.dumps({"id": "btn-delete-item"})
        )
        db.add_all([el_1_1, el_1_2, el_1_3])
        db.commit()

        # 2. Create Drifted Crawl
        crawl_2 = Crawl(project_id=project.id, status="completed")
        db.add(crawl_2)
        db.commit()
        db.refresh(crawl_2)

        page_2 = Page(crawl_id=crawl_2.id, url="http://localhost:9999/catalog", path="/catalog", title="Catalog")
        db.add(page_2)
        db.commit()
        db.refresh(page_2)

        # Add elements for Page 2
        el_2_1 = Element(
            page_id=page_2.id,
            tag_name="button",
            selector="#add-to-cart-action",
            element_type="button",
            text_content="Add to Cart",
            attributes=json.dumps({"id": "add-to-cart-action", "class": "btn btn-primary"})
        )
        el_2_2 = Element(
            page_id=page_2.id,
            tag_name="input",
            selector="#search-input",
            element_type="input",
            text_content="",
            attributes=json.dumps({"id": "search-input", "name": "q", "type": "text"})
        )
        el_2_4 = Element(
            page_id=page_2.id,
            tag_name="button",
            selector="#btn-checkout",
            element_type="button",
            text_content="Checkout",
            attributes=json.dumps({"id": "btn-checkout"})
        )
        db.add_all([el_2_1, el_2_2, el_2_4])
        db.commit()

        # 3. Execute comparison engine
        updater = SpecUpdaterService(db, project.id)
        res = updater.compare_crawls(crawl_1.id, crawl_2.id)

        catalog_delta = res.get("/catalog", {})
        elements = catalog_delta.get("elements", {})

        # Assertions
        assert len(elements["added"]) == 1
        assert elements["added"][0]["selector"] == "#btn-checkout"

        assert len(elements["deleted"]) == 1
        assert elements["deleted"][0]["selector"] == "#btn-delete-item"

        assert len(elements["modified"]) == 1
        assert elements["modified"][0]["old_selector"] == "#btn-add-to-cart"
        assert elements["modified"][0]["new_selector"] == "#add-to-cart-action"

        assert len(elements["unmodified"]) == 1
        assert elements["unmodified"][0]["selector"] == "#search-input"

    finally:
        # Clean up database
        db.query(Element).filter(Element.page_id.in_([page_1.id, page_2.id])).delete(synchronize_session=False)
        db.query(Page).filter(Page.crawl_id.in_([crawl_1.id, crawl_2.id])).delete(synchronize_session=False)
        db.query(Crawl).filter(Crawl.project_id == project.id).delete(synchronize_session=False)
        db.query(Project).filter(Project.id == project.id).delete(synchronize_session=False)
        db.commit()
        db.close()
