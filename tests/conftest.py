import pytest
from fastapi.testclient import TestClient

_test_exchanges = {
    "XAMS": "Euronext Amsterdam",
    "XLON": "London Stock Exchange",
    "XSWX": "SIX Swiss Exchange",
}


@pytest.fixture(autouse=True)
def settings():
    import exchange_calendar_service.app.settings
    from exchange_calendar_service.app.settings import Settings

    # Save the original settings.
    settings0 = exchange_calendar_service.app.settings.settings

    # Create a new settings object.
    settings = Settings(changes_api_key="test", init=None, exchanges=_test_exchanges)

    # Set the new settings object.
    exchange_calendar_service.app.settings.settings = settings

    yield settings

    # Reinstated the original settings.
    exchange_calendar_service.app.settings.settings = settings0


@pytest.fixture
def client() -> TestClient:
    from exchange_calendar_service.app.app import app

    return TestClient(app())
