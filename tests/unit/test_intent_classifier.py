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

def test_ollama_llm_provider_form_classification(mocker):
    # Mock settings
    mocker.patch("backend.app.services.intent.settings.OLLAMA_MODEL", "llama3")
    mocker.patch("backend.app.services.intent.settings.OLLAMA_URL", "http://localhost:11434")

    # Mock aiohttp client session post context manager
    mock_response = mocker.Mock()
    mock_response.status = 200

    async def mock_json():
        return {
            "response": json.dumps({
                "name": "custom_search",
                "description": "Custom query search",
                "intent": "search",
                "selector": "#search-form",
                "parameters": [
                    {"name": "query", "type": "string", "selector": "#q", "required": True}
                ],
                "action_type": "browser",
                "confidence_score": 0.95
            })
        }

    mock_response.json = mock_json

    mock_post_context = mocker.MagicMock()
    mock_post_context.__aenter__.return_value = mock_response

    mocker.patch("aiohttp.ClientSession.post", return_value=mock_post_context)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        service = SemanticIntentService(db, "proj-555")

        # Verify provider selection
        assert service.llm_provider == "ollama"
        assert service.use_llm is True

        form_el = Element(
            page_id="page-1",
            tag_name="form",
            selector="#search-form",
            element_type="form",
            attributes="{}",
            outer_html="<form id='search-form'><input id='q'/></form>"
        )
        input_el = Element(
            page_id="page-1",
            tag_name="input",
            selector="#q",
            element_type="input",
            attributes='{"name": "query"}',
            outer_html="<input id='q'/>"
        )

        res = asyncio.run(service.classify_form_llm(form_el, [input_el]))
        assert res["name"] == "custom_search"
        assert res["intent"] == "search"
        assert len(res["parameters"]) == 1

    finally:
        db.close()


def test_gemini_llm_provider_form_classification(mocker):
    mocker.patch("backend.app.services.intent.settings.GEMINI_API_KEY", "mock-gemini-key")
    mocker.patch("backend.app.services.intent.settings.OLLAMA_MODEL", "")

    mock_model = mocker.MagicMock()
    mock_response = mocker.AsyncMock()
    mock_response.text = json.dumps({
        "name": "custom_login",
        "description": "User login route",
        "intent": "login",
        "selector": "#login-form",
        "parameters": [
            {"name": "email", "type": "string", "selector": "#email", "required": True},
            {"name": "password", "type": "string", "selector": "#password", "required": True}
        ],
        "action_type": "browser",
        "confidence_score": 0.98
    })
    mock_model.generate_content_async = mocker.AsyncMock(return_value=mock_response)
    mocker.patch("google.generativeai.GenerativeModel", return_value=mock_model)
    mocker.patch("google.generativeai.configure")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        service = SemanticIntentService(db, "proj-gemini")

        assert service.llm_provider == "gemini"
        assert service.use_llm is True

        form_el = Element(
            page_id="page-1",
            tag_name="form",
            selector="#login-form",
            element_type="form",
            attributes="{}",
            outer_html="<form id='login-form'><input id='email'/></form>"
        )
        input_el = Element(
            page_id="page-1",
            tag_name="input",
            selector="#email",
            element_type="input",
            attributes='{"name": "email"}',
            outer_html="<input id='email'/>"
        )

        res = asyncio.run(service.classify_form_llm(form_el, [input_el]))
        assert res["name"] == "custom_login"
        assert res["intent"] == "login"
        assert len(res["parameters"]) == 2

    finally:
        db.close()
