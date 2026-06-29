from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.models.db_models import Action
from backend.app.services.state_reconciler import StateReconcilerService


@pytest.mark.anyio
async def test_reconciler_reconcile_action_drift(mocker):
    # Mock action
    action = Action(
        id="act-rec-1",
        project_id="proj-rec-1",
        name="add_product",
        action_type="browser",
        selector="#cart-btn",
        parameters="[]"
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = action

    # Mock playwright page locator candidates
    mock_candidate = AsyncMock()
    mock_candidate.inner_text = AsyncMock(return_value="Add Product Button")
    mock_candidate.get_attribute = AsyncMock(side_effect=["new-cart-btn", "btn btn-primary"])
    mock_candidate.evaluate = AsyncMock(return_value="button")

    mock_page = AsyncMock()
    mock_locator = AsyncMock()
    mock_locator.count = AsyncMock(side_effect=[1, 0])
    mock_locator.all = AsyncMock(return_value=[mock_candidate])
    mock_page.locator = MagicMock(return_value=mock_locator)

    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page

    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    mock_stealth_context = MagicMock()
    mock_stealth_context.__aenter__.return_value = mock_playwright
    mocker.patch("playwright_stealth.Stealth.use_async", return_value=mock_stealth_context)

    reconciler = StateReconcilerService(db)
    res = await reconciler.reconcile_action_drift("act-rec-1", "http://localhost:8001/prod", "http://localhost:8001/stage")

    assert res["success"] is True
    assert res["prod_exists"] is True
    assert res["staging_exists"] is False
    assert res["drift_detected"] is True
    # Verify healed selector recommendation is mapped correctly
    assert res["recommended_selector"] == "#new-cart-btn"
