import json

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Crawl, Element, Page, Project
from backend.app.services.updater import SpecUpdaterService


def test_drift_engine():
    print("Initializing Database Session...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Creating Mock Project...")
        project = Project(name="Drift Test Project", root_url="http://localhost:9999")
        db.add(project)
        db.commit()
        db.refresh(project)

        # 1. Create Crawl 1 (Baseline)
        print("Creating Baseline Crawl 1...")
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

        # 2. Create Crawl 2 (Shifted/Drifted state)
        print("Creating Drifted Crawl 2...")
        crawl_2 = Crawl(project_id=project.id, status="completed")
        db.add(crawl_2)
        db.commit()
        db.refresh(crawl_2)

        page_2 = Page(crawl_id=crawl_2.id, url="http://localhost:9999/catalog", path="/catalog", title="Catalog")
        db.add(page_2)
        db.commit()
        db.refresh(page_2)

        # Add elements for Page 2:
        # - el_2_1: Selector drift: #btn-add-to-cart -> #add-to-cart-action (same text and attributes)
        # - el_2_2: Unmodified: #search-input
        # - el_2_3: Added: #btn-checkout (new element)
        # (Missing el_1_3: #btn-delete-item represents deleted element)

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

        # 3. Execute comparison delta engine
        print("Running SpecUpdaterService Drift Detection Engine...")
        updater = SpecUpdaterService(db, project.id)
        res = updater.compare_crawls(crawl_1.id, crawl_2.id)

        # Output results
        print("\n--- Drift Engine Comparison Results ---")
        catalog_delta = res.get("/catalog", {})
        print(f"Catalog Page Status: {catalog_delta.get('status')}")

        elements = catalog_delta.get("elements", {})
        print("\n[ADDED Elements]:")
        for el in elements.get("added", []):
            print(f"  + Tag: {el['tag_name']}, Selector: {el['selector']}, Text: {el['text_content']}")

        print("\n[DELETED Elements]:")
        for el in elements.get("deleted", []):
            print(f"  - Tag: {el['tag_name']}, Selector: {el['selector']}, Text: {el['text_content']}")

        print("\n[MODIFIED (DRIFTED) Elements]:")
        for el in elements.get("modified", []):
            print(f"  ~ Tag: {el['tag_name']}, Old: {el['old_selector']}, New: {el['new_selector']}, Confidence: {el['drift_confidence']}")

        print("\n[UNMODIFIED Elements]:")
        for el in elements.get("unmodified", []):
            print(f"  = Tag: {el['tag_name']}, Selector: {el['selector']}")

        # Assertions to verify correctness
        assert len(elements["added"]) == 1, "Should detect 1 added element"
        assert elements["added"][0]["selector"] == "#btn-checkout", "Added element should be #btn-checkout"

        assert len(elements["deleted"]) == 1, "Should detect 1 deleted element"
        assert elements["deleted"][0]["selector"] == "#btn-delete-item", "Deleted element should be #btn-delete-item"

        assert len(elements["modified"]) == 1, "Should detect 1 drifted element"
        assert elements["modified"][0]["old_selector"] == "#btn-add-to-cart", "Old selector should be #btn-add-to-cart"
        assert elements["modified"][0]["new_selector"] == "#add-to-cart-action", "New selector should be #add-to-cart-action"

        assert len(elements["unmodified"]) == 1, "Should detect 1 unmodified element"
        assert elements["unmodified"][0]["selector"] == "#search-input", "Unmodified selector should be #search-input"

        print("\n🎉 ALL DRIFT ENGINE ASSERTIONS PASSED SUCCESSFULLY!")

    finally:
        # Clean up database records
        print("Cleaning up test records...")
        db.query(Element).filter(Element.page_id.in_([page_1.id, page_2.id])).delete(synchronize_session=False)
        db.query(Page).filter(Page.crawl_id.in_([crawl_1.id, crawl_2.id])).delete(synchronize_session=False)
        db.query(Crawl).filter(Crawl.project_id == project.id).delete(synchronize_session=False)
        db.query(Project).filter(Project.id == project.id).delete(synchronize_session=False)
        db.commit()
        db.close()

if __name__ == "__main__":
    test_drift_engine()
