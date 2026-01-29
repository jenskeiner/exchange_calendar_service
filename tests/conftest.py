import pytest
from fastapi.testclient import TestClient

_test_exchanges = {
    "XAMS": "Euronext Amsterdam",
    "XLON": "London Stock Exchange",
    "XSWX": "SIX Swiss Exchange",
}


@pytest.fixture
def test_settings():
    """Create test settings with a limited set of exchanges."""
    from exchange_calendar_service.app.settings import (
        Settings,
        get_settings,
        set_settings,
    )

    previous = get_settings(create=False)
    settings = Settings(changes_api_key="test", init=None, exchanges=_test_exchanges)
    set_settings(settings)
    yield settings
    set_settings(previous)


@pytest.fixture
def client(test_settings) -> TestClient:
    """Create test client with test settings injected."""
    from exchange_calendar_service.app.app import app

    return TestClient(app(test_settings))


@pytest.fixture
def tagged_dates(client):
    """Set up dates with tags for testing exclude_tags functionality.

    Adds tags to specific dates and cleans them up after the test.
    Uses the update endpoint to add metadata tags.
    """
    from exchange_calendar_service.app.settings import get_settings

    # Set up tags on specific dates
    tags_to_add = {
        "XLON": {
            "2024-12-25": {"tags": ["test-tag", "holiday-tag"]},
            "2024-12-26": {"tags": ["test-tag"]},
            "2024-12-24": {"tags": ["tag-c"]},
            "2024-03-29": {"tags": ["future-tag"]},
            "2024-03-27": {"tags": ["exclude-business-day"]},
        },
        "XAMS": {
            "2024-12-25": {"tags": ["test-tag"]},
        },
    }

    # Add the tags via update endpoint
    for mic, dates_meta in tags_to_add.items():
        client.post(
            "/update",
            json={mic: {"meta": dates_meta}},
            headers={"X-API-KEY": "test"},
        )

    # Clear cache so tags are reflected
    from exchange_calendar_service.core.common.context import Context
    for mic in tags_to_add.keys():
        if Context().cache:
            Context().cache.refresh(mic)

    yield tags_to_add

    # Clean up: remove all tags
    for mic, dates_meta in tags_to_add.items():
        dates_meta_clean = {date: {"tags": []} for date in dates_meta.keys()}
        client.post(
            "/update",
            json={mic: {"meta": dates_meta_clean}},
            headers={"X-API-KEY": "test"},
        )

    # Clear cache again after cleanup
    for mic in tags_to_add.keys():
        if Context().cache:
            Context().cache.refresh(mic)
