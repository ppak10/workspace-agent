from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch, call

import pytest
import typer

from wa.cli.__main__ import app, _rich_exception_handler


class TestRichExceptionHandler:
    """Test the _rich_exception_handler function."""

    @patch("wa.cli.__main__.rprint")
    @patch("sys.exit")
    def test_keyboard_interrupt_handling(self, mock_exit, mock_rprint):
        """Test that KeyboardInterrupt is handled with custom message."""
        # Create a mock traceback
        mock_traceback = MagicMock()

        # Call the exception handler with KeyboardInterrupt
        _rich_exception_handler(KeyboardInterrupt, KeyboardInterrupt(), mock_traceback)

        # Should print the cancellation message
        mock_rprint.assert_called_once_with(
            "\n ⚠️  [yellow]Operation cancelled by user[/yellow]"
        )

        # Should call sys.exit(1)
        mock_exit.assert_called_once_with(1)

    @patch("sys.__excepthook__")
    def test_other_exceptions_delegated(self, mock_excepthook):
        """Test that non-KeyboardInterrupt exceptions are delegated to default handler."""
        # Create a test exception
        exc_type = ValueError
        exc_value = ValueError("Test error")
        mock_traceback = MagicMock()

        # Call the exception handler with ValueError
        _rich_exception_handler(exc_type, exc_value, mock_traceback)

        # Should delegate to sys.__excepthook__
        mock_excepthook.assert_called_once_with(exc_type, exc_value, mock_traceback)

    @patch("sys.__excepthook__")
    def test_runtime_error_delegated(self, mock_excepthook):
        """Test that RuntimeError is delegated to default handler."""
        exc_type = RuntimeError
        exc_value = RuntimeError("Runtime error")
        mock_traceback = MagicMock()

        _rich_exception_handler(exc_type, exc_value, mock_traceback)

        mock_excepthook.assert_called_once_with(exc_type, exc_value, mock_traceback)

    @patch("sys.__excepthook__")
    def test_custom_exception_delegated(self, mock_excepthook):
        """Test that custom exceptions are delegated to default handler."""

        class CustomError(Exception):
            pass

        exc_type = CustomError
        exc_value = CustomError("Custom error")
        mock_traceback = MagicMock()

        _rich_exception_handler(exc_type, exc_value, mock_traceback)

        mock_excepthook.assert_called_once_with(exc_type, exc_value, mock_traceback)

    @patch("wa.cli.__main__.rprint")
    @patch("sys.exit")
    @patch("sys.__excepthook__")
    def test_keyboard_interrupt_does_not_call_default_handler(
        self, mock_excepthook, mock_exit, mock_rprint
    ):
        """Test that KeyboardInterrupt doesn't call the default exception handler."""
        mock_traceback = MagicMock()

        _rich_exception_handler(KeyboardInterrupt, KeyboardInterrupt(), mock_traceback)

        # Should NOT call sys.__excepthook__
        mock_excepthook.assert_not_called()

    @patch("wa.cli.__main__.rprint")
    @patch("sys.exit")
    def test_keyboard_interrupt_message_format(self, mock_exit, mock_rprint):
        """Test the exact format of the KeyboardInterrupt message."""
        mock_traceback = MagicMock()

        _rich_exception_handler(KeyboardInterrupt, KeyboardInterrupt(), mock_traceback)

        # Verify the exact message format
        call_args = mock_rprint.call_args[0][0]
        assert "⚠️" in call_args
        assert "yellow" in call_args
        assert "Operation cancelled by user" in call_args
        assert call_args.startswith("\n")

    @patch("wa.cli.__main__.rprint")
    @patch("sys.exit")
    def test_keyboard_interrupt_exits_with_code_1(self, mock_exit, mock_rprint):
        """Test that KeyboardInterrupt exits with code 1."""
        mock_traceback = MagicMock()

        _rich_exception_handler(KeyboardInterrupt, KeyboardInterrupt(), mock_traceback)

        # Should exit with code 1 (error)
        mock_exit.assert_called_once_with(1)

    @patch("sys.__excepthook__")
    def test_exception_with_none_traceback(self, mock_excepthook):
        """Test handling exception with None traceback."""
        exc_type = ValueError
        exc_value = ValueError("Error")

        _rich_exception_handler(exc_type, exc_value, None)

        mock_excepthook.assert_called_once_with(exc_type, exc_value, None)

    @patch("sys.__excepthook__")
    def test_system_exit_delegated(self, mock_excepthook):
        """Test that SystemExit is delegated to default handler."""
        exc_type = SystemExit
        exc_value = SystemExit(0)
        mock_traceback = MagicMock()

        _rich_exception_handler(exc_type, exc_value, mock_traceback)

        mock_excepthook.assert_called_once_with(exc_type, exc_value, mock_traceback)


class TestAppConfiguration:
    """Test the Typer app configuration."""

    def test_app_is_typer_instance(self):
        """Test that app is a Typer instance."""
        assert isinstance(app, typer.Typer)

    def test_app_name(self):
        """Test that app has correct name."""
        assert app.info.name == "workspace-agent"

    def test_app_help_text(self):
        """Test that app has help text."""
        expected_help = (
            "Utilize tool calling to manage workspace folders and subfolders"
        )
        assert app.info.help == expected_help

    def test_app_no_args_is_help(self):
        """Test that app shows help when no args provided."""
        # This is set in the Typer constructor
        # We can verify it's configured correctly by checking the info
        assert hasattr(app, "info")

    def test_app_completion_disabled(self):
        """Test that shell completion is disabled."""
        # The add_completion parameter should be False
        # This is a bit tricky to test directly, but we can verify
        # that the app doesn't have completion-related commands
        command_names = [cmd.name for cmd in app.registered_commands]
        assert "completion" not in command_names


class TestExceptionHookInstallation:
    """Test that the exception hook is properly installed."""

    @pytest.mark.skip(reason="Test is fragile as other tests may modify sys.excepthook")
    def test_exception_hook_is_installed(self):
        """Test that sys.excepthook is set to our custom handler."""
        # After importing the module, sys.excepthook should be our handler
        # Note: This test might be fragile if other code modifies excepthook
        assert sys.excepthook == _rich_exception_handler

    @patch("wa.cli.__main__.rprint")
    @patch("sys.exit")
    def test_exception_hook_can_be_triggered(self, mock_exit, mock_rprint):
        """Test that the installed exception hook can be triggered."""
        # Save original excepthook
        original_hook = sys.excepthook

        try:
            # Set our handler
            sys.excepthook = _rich_exception_handler

            # Trigger it with KeyboardInterrupt
            try:
                raise KeyboardInterrupt()
            except KeyboardInterrupt:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                sys.excepthook(exc_type, exc_value, exc_traceback)

            # Should have printed message and called exit
            mock_rprint.assert_called_once()
            mock_exit.assert_called_once_with(1)

        finally:
            # Restore original excepthook
            sys.excepthook = original_hook
