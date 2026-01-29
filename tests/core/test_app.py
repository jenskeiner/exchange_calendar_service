"""Tests for app initialization and update endpoint."""

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from exchange_calendar_service.app.app import app
from exchange_calendar_service.app.settings import Settings


class TestInitFunctionLoading:
    """Tests for the init function loading feature."""

    def test_init_with_valid_callable(self, tmp_path, monkeypatch):
        """Test that a valid init callable is imported and called."""

        # Create a temporary module with a valid init function
        init_module = tmp_path / "test_init_module.py"
        init_module.write_text(
            """
# Track if init was called
called = False
received_settings = None

def init(settings):
    global called, received_settings
    called = True
    received_settings = settings
"""
        )

        # Add tmp_path to sys.path so we can import the module
        monkeypatch.syspath_prepend(str(tmp_path))

        settings = Settings(
            changes_api_key=None,
            init="test_init_module:init",
            exchanges={"XNYS": "XNYS"},
        )

        # Create app - init should be called
        _ = app(settings)

        # Verify init was called
        import test_init_module

        assert test_init_module.called is True
        assert test_init_module.received_settings is settings

    def test_init_with_module_only(self, tmp_path, monkeypatch):
        """Test importing a module without a callable name."""

        # Create a temporary module
        init_module = tmp_path / "test_init_module_only.py"
        init_module.write_text("# Just a module with no callable")
        monkeypatch.syspath_prepend(str(tmp_path))

        settings = Settings(
            changes_api_key=None,
            init="test_init_module_only",
            exchanges={"XNYS": "XNYS"},
        )

        # Should not raise - just imports the module
        _ = app(settings)

    def test_init_not_callable_raises_error(self, tmp_path, monkeypatch):
        """Test that non-callable init raises ValueError."""

        # Create a module with a non-callable
        init_module = tmp_path / "test_init_not_callable.py"
        init_module.write_text("init = 42")
        monkeypatch.syspath_prepend(str(tmp_path))

        settings = Settings(
            changes_api_key=None,
            init="test_init_not_callable:init",
            exchanges={"XNYS": "XNYS"},
        )

        with pytest.raises(ValueError, match="is not callable"):
            app(settings)

    def test_init_not_a_function_raises_error(self, tmp_path, monkeypatch):
        """Test that a callable that is not a function raises ValueError."""

        # Create a module with a callable class (not a function)
        init_module = tmp_path / "test_init_not_function.py"
        init_module.write_text(
            """
class InitCallable:
    def __call__(self):
        pass

init = InitCallable()
"""
        )
        monkeypatch.syspath_prepend(str(tmp_path))

        settings = Settings(
            changes_api_key=None,
            init="test_init_not_function:init",
            exchanges={"XNYS": "XNYS"},
        )

        with pytest.raises(ValueError, match="is not a function"):
            app(settings)

    def test_init_wrong_signature_raises_error(self, tmp_path, monkeypatch):
        """Test that a function with wrong number of arguments raises ValueError."""

        # Create a module with a function that has wrong signature
        init_module = tmp_path / "test_init_wrong_signature.py"
        init_module.write_text(
            """
def init(settings, extra_arg):  # Too many args
    pass
"""
        )
        monkeypatch.syspath_prepend(str(tmp_path))

        settings = Settings(
            changes_api_key=None,
            init="test_init_wrong_signature:init",
            exchanges={"XNYS": "XNYS"},
        )

        with pytest.raises(ValueError, match="does not have exactly one argument"):
            app(settings)

    def test_init_no_args_raises_error(self, tmp_path, monkeypatch):
        """Test that a function with zero arguments raises ValueError."""

        init_module = tmp_path / "test_init_no_args.py"
        init_module.write_text(
            """
def init():  # No args
    pass
"""
        )
        monkeypatch.syspath_prepend(str(tmp_path))

        settings = Settings(
            changes_api_key=None,
            init="test_init_no_args:init",
            exchanges={"XNYS": "XNYS"},
        )

        with pytest.raises(ValueError, match="does not have exactly one argument"):
            app(settings)

    def test_init_two_args_raises_error(self, tmp_path, monkeypatch):
        """Test that a function with two arguments raises ValueError."""

        init_module = tmp_path / "test_init_two_args.py"
        init_module.write_text(
            """
def init(settings, another):  # Two args
    pass
"""
        )
        monkeypatch.syspath_prepend(str(tmp_path))

        settings = Settings(
            changes_api_key=None,
            init="test_init_two_args:init",
            exchanges={"XNYS": "XNYS"},
        )

        with pytest.raises(ValueError, match="does not have exactly one argument"):
            app(settings)

    def test_init_none_skips_loading(self):
        """Test that when init is None, no init loading occurs."""

        settings = Settings(
            changes_api_key=None,
            init=None,
            exchanges={"XNYS": "XNYS"},
        )

        # Should not raise
        client = TestClient(app(settings))
        assert client is not None


class TestUpdateEndpoint:
    """Tests for the /update endpoint."""

    @patch("exchange_calendar_service.app.app.ecx_core.get_changes_for_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.reset_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.update_calendar")
    @patch("exchange_calendar_service.app.app.Context")
    def test_update_with_valid_api_key(
        self, mock_context, mock_update, mock_reset, mock_get_changes, client
    ):
        """Test that valid API key allows access to update endpoint."""
        from exchange_calendars_extensions.api.changes import ChangeSetDict

        mock_get_changes.return_value = ChangeSetDict(root={})
        mock_cache = MagicMock()
        mock_context.return_value.cache = mock_cache

        response = client.post(
            "/update",
            json={
                "XNYS": {
                    "add": {"2020-01-01": {"type": "holiday", "name": "Test Holiday"}},
                    "remove": [],
                    "meta": {},
                }
            },
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_reset.assert_called_once()

    def test_update_with_invalid_api_key(self, client):
        """Test that invalid API key returns 401."""
        response = client.post(
            "/update",
            json={
                "XNYS": {
                    "add": {"2020-01-01": {"type": "holiday", "name": "Test Holiday"}},
                    "remove": [],
                    "meta": {},
                }
            },
            headers={"X-API-KEY": "wrong"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json()["detail"] == "Invalid API key"

    def test_update_with_missing_api_key(self, client):
        """Test that missing API key returns 401."""
        response = client.post(
            "/update",
            json={
                "XNYS": {
                    "add": {"2020-01-01": {"type": "holiday", "name": "Test Holiday"}},
                    "remove": [],
                    "meta": {},
                }
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json()["detail"] == "Invalid API key"

    def test_update_endpoint_not_available_without_api_key_configured(self):
        """Test that /update endpoint is not registered when changes_api_key is None."""
        settings = Settings(
            changes_api_key=None,
            init=None,
            exchanges={"XNYS": "XNYS"},
        )
        client = TestClient(app(settings))

        # Endpoint should not exist (404 instead of 401)
        response = client.post(
            "/update",
            json={
                "XNYS": {
                    "add": {"2020-01-01": {"type": "holiday", "name": "Test Holiday"}},
                    "remove": [],
                    "meta": {},
                }
            },
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    @patch("exchange_calendar_service.app.app.ecx_core.get_changes_for_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.reset_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.update_calendar")
    def test_update_no_op_when_changes_identical(
        self, mock_update, mock_reset, mock_get_changes, client
    ):
        """Test that when changes are identical to existing, no updates occur."""
        # Mock existing changes to match the incoming changes
        existing_changes = MagicMock()
        existing_changes.__eq__ = (
            lambda self, other: True
        )  # Make equality check return True
        mock_get_changes.return_value = existing_changes

        response = client.post(
            "/update",
            json={
                "XNYS": {
                    "add": {"2020-01-01": {"type": "holiday", "name": "Test Holiday"}},
                    "remove": [],
                    "meta": {},
                }
            },
            headers={"X-API-KEY": "test"},
        )

        assert response.status_code == HTTPStatus.OK
        # Reset should not be called when changes are identical
        mock_reset.assert_not_called()
        mock_update.assert_not_called()

    @patch("exchange_calendar_service.app.app.ecx_core.get_changes_for_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.reset_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.update_calendar")
    @patch("exchange_calendar_service.app.app.Context")
    def test_update_adding_new_exchange(
        self, mock_context, mock_update, mock_reset, mock_get_changes, client
    ):
        """Test adding changes for a new exchange."""
        # Mock no existing changes
        from exchange_calendars_extensions.api.changes import ChangeSet, ChangeSetDict

        mock_get_changes.return_value = ChangeSetDict(root={})
        mock_cache = MagicMock()
        mock_context.return_value.cache = mock_cache

        response = client.post(
            "/update",
            json={
                "XNYS": {
                    "add": {"2020-01-01": {"type": "holiday", "name": "New Holiday"}},
                    "remove": [],
                    "meta": {},
                }
            },
            headers={"X-API-KEY": "test"},
        )

        assert response.status_code == HTTPStatus.OK
        mock_reset.assert_called_once()
        mock_update.assert_called_once()

    @patch("exchange_calendar_service.app.app.ecx_core.get_changes_for_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.reset_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.update_calendar")
    @patch("exchange_calendar_service.app.app.Context")
    def test_update_updating_existing_exchange(
        self, mock_context, mock_update, mock_reset, mock_get_changes, client
    ):
        """Test updating changes for an existing exchange."""
        from exchange_calendars_extensions.api.changes import ChangeSet, ChangeSetDict

        # Mock existing changes
        existing = ChangeSetDict(
            root={
                "XNYS": ChangeSet(
                    add={"2020-01-01": {"type": "holiday", "name": "Old Holiday"}},
                    remove=[],
                    meta={},
                )
            }
        )
        mock_get_changes.return_value = existing
        mock_cache = MagicMock()
        mock_context.return_value.cache = mock_cache

        response = client.post(
            "/update",
            json={
                "XNYS": {
                    "add": {
                        "2020-01-01": {"type": "holiday", "name": "Updated Holiday"}
                    },
                    "remove": [],
                    "meta": {},
                }
            },
            headers={"X-API-KEY": "test"},
        )

        assert response.status_code == HTTPStatus.OK
        mock_reset.assert_called_once()
        mock_update.assert_called_once()

    @patch("exchange_calendar_service.app.app.ecx_core.get_changes_for_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.reset_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.update_calendar")
    @patch("exchange_calendar_service.app.app.Context")
    def test_update_removing_exchange_changes(
        self, mock_context, mock_update, mock_reset, mock_get_changes, client
    ):
        """Test removing changes for an exchange by not including it in new changes."""
        from exchange_calendars_extensions.api.changes import ChangeSet, ChangeSetDict

        # Mock existing changes for XNYS
        existing = ChangeSetDict(
            root={
                "XNYS": ChangeSet(
                    add={"2020-01-01": {"type": "holiday", "name": "Old Holiday"}},
                    remove=[],
                    meta={},
                )
            }
        )
        mock_get_changes.return_value = existing
        mock_cache = MagicMock()
        mock_context.return_value.cache = mock_cache

        # Send empty changes (removes XNYS changes)
        response = client.post(
            "/update",
            json={},
            headers={"X-API-KEY": "test"},
        )

        assert response.status_code == HTTPStatus.OK
        mock_reset.assert_called_once()
        # update_calendar should not be called for removed exchanges
        mock_update.assert_not_called()

    @patch("exchange_calendar_service.app.app.ecx_core.get_changes_for_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.reset_all_calendars")
    @patch("exchange_calendar_service.app.app.ecx_core.update_calendar")
    @patch("exchange_calendar_service.app.app.Context")
    def test_update_refreshes_cache(
        self, mock_context, mock_update, mock_reset, mock_get_changes, client
    ):
        """Test that affected calendars are refreshed in cache after update."""
        from exchange_calendars_extensions.api.changes import ChangeSetDict

        mock_get_changes.return_value = ChangeSetDict(root={})
        mock_cache = MagicMock()
        mock_context.return_value.cache = mock_cache

        response = client.post(
            "/update",
            json={
                "XNYS": {
                    "add": {"2020-01-01": {"type": "holiday", "name": "Test"}},
                    "remove": [],
                    "meta": {},
                }
            },
            headers={"X-API-KEY": "test"},
        )

        assert response.status_code == HTTPStatus.OK
        # Cache should be refreshed for the affected exchange
        mock_cache.refresh.assert_called_once_with("XNYS")


class TestTagInjection:
    """Tests for tag injection and retrieval via the update endpoint."""

    def test_inject_and_retrieve_tags(self, client):
        """Test that tags can be injected via update endpoint and retrieved via calendar.meta()."""
        from datetime import date

        from exchange_calendar_service.core.common.context import Context

        mic = "XNYS"
        test_date = "2024-01-15"
        test_tags = ["test-tag", "another-tag"]

        # Inject tags via update endpoint
        response = client.post(
            "/update",
            json={mic: {"meta": {test_date: {"tags": test_tags}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        # Retrieve tags via calendar.meta()
        calendar = Context().cache.get(mic)
        meta_results = calendar.meta(start=date(2024, 1, 1), end=date(2024, 1, 31))

        # Find the test date in results - meta() returns an OrderedDict
        found_date = None
        for d, meta in meta_results.items():
            if d.date().isoformat() == test_date:
                found_date = (d, meta)
                break

        assert found_date is not None, "Test date not found in meta results"
        retrieved_date, retrieved_meta = found_date
        assert set(retrieved_meta.tags) == set(test_tags)

    def test_update_existing_tags(self, client):
        """Test that existing tags can be updated via update endpoint."""
        from datetime import date

        from exchange_calendar_service.core.common.context import Context

        mic = "XNYS"
        test_date = "2024-02-20"
        initial_tags = ["initial-tag"]

        # Inject initial tags
        response = client.post(
            "/update",
            json={mic: {"meta": {test_date: {"tags": initial_tags}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        # Verify initial tags
        calendar = Context().cache.get(mic)
        meta_results = calendar.meta(start=date(2024, 2, 1), end=date(2024, 2, 28))
        for d, meta in meta_results.items():
            if d.date().isoformat() == test_date:
                assert meta.tags == initial_tags
                break

        # Update with new tags
        updated_tags = ["updated-tag", "another-updated"]
        response = client.post(
            "/update",
            json={mic: {"meta": {test_date: {"tags": updated_tags}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        # Verify updated tags
        calendar = Context().cache.get(mic)
        meta_results = calendar.meta(start=date(2024, 2, 1), end=date(2024, 2, 28))
        for d, meta in meta_results.items():
            if d.date().isoformat() == test_date:
                assert set(meta.tags) == set(updated_tags)
                break

    def test_clear_tags(self, client):
        """Test that tags can be cleared by setting empty list."""
        from datetime import date

        from exchange_calendar_service.core.common.context import Context

        mic = "XNYS"
        test_date = "2024-03-10"
        test_tags = ["tag-to-clear"]

        # Inject tags
        response = client.post(
            "/update",
            json={mic: {"meta": {test_date: {"tags": test_tags}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        # Verify tags exist
        calendar = Context().cache.get(mic)
        meta_results = calendar.meta(start=date(2024, 3, 1), end=date(2024, 3, 31))
        for d, meta in meta_results.items():
            if d.date().isoformat() == test_date:
                assert meta.tags == test_tags
                break

        # Clear tags - empty tags removes the tag but the date remains in meta
        response = client.post(
            "/update",
            json={mic: {"meta": {test_date: {"tags": []}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        # Verify tags are cleared - date should still be in meta but with empty tags
        calendar = Context().cache.get(mic)
        meta_results = calendar.meta(start=date(2024, 3, 1), end=date(2024, 3, 31))
        found = False
        for d, meta in meta_results.items():
            if d.date().isoformat() == test_date:
                assert meta.tags == [], f"Date {test_date} should have empty tags"
                found = True
                break
        assert found, f"Date {test_date} should still be in meta with empty tags"
