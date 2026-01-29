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
