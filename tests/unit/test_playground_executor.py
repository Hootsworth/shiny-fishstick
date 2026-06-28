import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.models.db_models import Action
from backend.app.services.playground import PlaygroundService


@pytest.mark.anyio
async def test_playground_execution_and_assertion_checking(mocker):
    action = Action(
        id="act-123",
        project_id="proj-123",
        name="test_action",
        action_type="browser",
        selector="#my-btn",
        parameters="[]",
        assertions=json.dumps([
            {"type": "visible", "selector": "#banner"},
            {"type": "url_equals", "value": "http://localhost:8001/dashboard"}
        ])
    )

    db = MagicMock()
    
    def query_side_effect(model):
        from backend.app.models.db_models import Action, Project
        mock_query = MagicMock()
        if model == Action:
            mock_query.filter.return_value.first.return_value = action
        elif model == Project:
            project = Project(root_url="http://localhost:8001")
            mock_query.filter.return_value.first.return_value = project
        return mock_query
        
    db.query.side_effect = query_side_effect

    mock_page = AsyncMock()
    mock_page.url = "http://localhost:8001/dashboard"
    mock_locator = AsyncMock()
    mock_locator.is_visible = AsyncMock(side_effect=[True, True])
    mock_locator.click = AsyncMock()
    mock_locator.fill = AsyncMock()
    mock_page.locator = MagicMock(return_value=mock_locator)
    mock_page.screenshot = AsyncMock(return_value=b"mock-png-bytes")

    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page

    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    mock_stealth_context = MagicMock()
    mock_stealth_context.__aenter__.return_value = mock_playwright
    mocker.patch("playwright_stealth.Stealth.use_async", return_value=mock_stealth_context)

    service = PlaygroundService(db)
    res = await service.execute_action("proj-123", "act-123", {})

    assert res["success"] is True
    assert len(res["assertion_results"]) == 2
    assert res["assertion_results"][0]["passed"] is True
    assert res["assertion_results"][1]["passed"] is True
    assert res["screenshot"] != ""
