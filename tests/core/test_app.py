"""Tests for app initialization, specifically the init function loading feature."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from exchange_calendar_service.app.app import app
from exchange_calendar_service.app.settings import Settings, set_settings


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
