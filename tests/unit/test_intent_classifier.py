import asyncio
import json

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.db_models import Action, Element
from backend.app.services.intent import SemanticIntentService


def test_heuristic_fallback_when_llm_disabled():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create elements matching login form heuristic patterns
        el_login = Element(
            page_id="page-1",
            tag_name="form",
            selector="#login-form",
            element_type="form",
            text_content="",
            attributes=json.dumps({"id": "login-form"}),
            outer_html="<form id='login-form'><input type='email'/></form>"
        )
        el_email = Element(
            page_id="page-1",
            tag_name="input",
            selector="#email",
            element_type="input",
            text_content="",
            attributes=json.dumps({"name": "email"}),
            outer_html="<input id='email'/>"
        )
        el_password = Element(
            page_id="page-1",
            tag_name="input",
            selector="#password",
            element_type="input",
            text_content="",
            attributes=json.dumps({"name": "password"}),
            outer_html="<input id='password'/>"
        )

        service = SemanticIntentService(db, "project-123")
        service.use_llm = False  # force heuristic path

        # Run async function in synchronous test wrapper
        actions = asyncio.run(service.classify_and_save([el_login, el_email, el_password]))

        assert len(actions) == 1
        assert actions[0].name == "login"
        assert actions[0].intent == "login"

        params = json.loads(actions[0].parameters)
        assert len(params) == 2
        assert any(p["name"] == "email" for p in params)
        assert any(p["name"] == "password" for p in params)
    finally:
        db.query(Action).filter(Action.project_id == "project-123").delete()
        db.commit()
        db.close()
