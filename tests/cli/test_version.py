from __future__ import annotations

from unittest.mock import patch, MagicMock
import importlib.metadata

import pytest
import typer

from wa.cli.version import register_version


class TestRegisterVersion:
    """Test the register_version function."""

    def test_register_version_creates_command(self):
        """Test that register_version registers a command with the app."""
        mock_app = typer.Typer()
        result = register_version(mock_app)

        # Should return the version function
        assert callable(result)
        assert result.__name__ == "version"

        # Should have registered a command
        assert len(mock_app.registered_commands) == 1
        # Command name can be None when @app.command() is used without name argument
        # The callback function name is what matters
        assert mock_app.registered_commands[0].callback.__name__ == "version"

    def test_register_version_command_has_docstring(self):
        """Test that the version command has a proper docstring."""
        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        expected_doc = "Show the installed version of `workspace-agent` package."
        assert version_func.__doc__ == expected_doc

    def test_register_version_returns_version_function(self):
        """Test that register_version returns the version function."""
        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        assert callable(version_func)
        assert version_func.__name__ == "version"


class TestVersionCommand:
    """Test the version command functionality."""

    @patch("wa.cli.version.rprint")
    @patch("importlib.metadata.version")
    def test_version_command_success(self, mock_version, mock_rprint):
        """Test version command when package is installed."""
        mock_version.return_value = "0.1.1"

        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        # Call the version function
        version_func()

        # Should call importlib.metadata.version with package name
        mock_version.assert_called_once_with("workspace-agent")

        # Should print success message with version
        mock_rprint.assert_called_once_with("✅ workspace-agent version 0.1.1")

    @patch("wa.cli.version.rprint")
    @patch("importlib.metadata.version")
    def test_version_command_different_version(self, mock_version, mock_rprint):
        """Test version command with different version number."""
        mock_version.return_value = "1.2.3"

        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        version_func()

        mock_rprint.assert_called_once_with("✅ workspace-agent version 1.2.3")

    @patch("wa.cli.version.rprint")
    @patch("importlib.metadata.version")
    def test_version_command_package_not_found(self, mock_version, mock_rprint):
        """Test version command when package is not installed."""
        mock_version.side_effect = importlib.metadata.PackageNotFoundError()

        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        # Should raise typer.Exit
        with pytest.raises(typer.Exit):
            version_func()

        # Should print warning message
        mock_rprint.assert_called_once_with(
            "⚠️  [yellow]workspace-agent version unknown (package not installed)[/yellow]"
        )

    @patch("wa.cli.version.rprint")
    @patch("importlib.metadata.version")
    def test_version_command_no_return_value(self, mock_version, mock_rprint):
        """Test that version command has no return value."""
        mock_version.return_value = "0.1.1"

        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        result = version_func()

        # Function should return None
        assert result is None

    @patch("wa.cli.version.rprint")
    @patch("importlib.metadata.version")
    def test_version_command_message_format_success(self, mock_version, mock_rprint):
        """Test the exact format of the success message."""
        mock_version.return_value = "2.0.0"

        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        version_func()

        call_args = mock_rprint.call_args[0][0]
        assert "✅" in call_args
        assert "workspace-agent" in call_args
        assert "version" in call_args
        assert "2.0.0" in call_args
        assert call_args == "✅ workspace-agent version 2.0.0"

    @patch("wa.cli.version.rprint")
    @patch("importlib.metadata.version")
    def test_version_command_message_format_error(self, mock_version, mock_rprint):
        """Test the exact format of the error message."""
        mock_version.side_effect = importlib.metadata.PackageNotFoundError()

        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        with pytest.raises(typer.Exit):
            version_func()

        call_args = mock_rprint.call_args[0][0]
        assert "⚠️" in call_args
        assert "yellow" in call_args
        assert "workspace-agent" in call_args
        assert "version unknown" in call_args
        assert "package not installed" in call_args

    @patch("wa.cli.version.rprint")
    @patch("importlib.metadata.version")
    def test_version_command_exit_has_no_code(self, mock_version, mock_rprint):
        """Test that typer.Exit is raised without specific exit code."""
        mock_version.side_effect = importlib.metadata.PackageNotFoundError()

        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        # Catch the Exit exception and verify it has no explicit exit code
        with pytest.raises(typer.Exit) as exc_info:
            version_func()

        # typer.Exit() without arguments defaults to code 0
        # But checking that exit code is either 0 or None (default)
        assert exc_info.value.exit_code in (0, None)

    @patch("wa.cli.version.rprint")
    @patch("importlib.metadata.version")
    def test_version_command_handles_version_with_metadata(
        self, mock_version, mock_rprint
    ):
        """Test version command with version that includes metadata."""
        # Some packages have versions like "1.0.0+local" or "1.0.0.dev1"
        mock_version.return_value = "0.1.1+dev.20240101"

        mock_app = typer.Typer()
        version_func = register_version(mock_app)

        version_func()

        mock_rprint.assert_called_once_with(
            "✅ workspace-agent version 0.1.1+dev.20240101"
        )


class TestVersionCommandIntegration:
    """Integration tests for the version command."""

    def test_version_command_can_be_invoked_via_app(self):
        """Test that version command can be invoked through the app."""
        mock_app = typer.Typer()
        register_version(mock_app)

        # Verify command is registered
        assert len(mock_app.registered_commands) == 1
        command = mock_app.registered_commands[0]
        # Verify the callback function name instead of command.name
        assert command.callback.__name__ == "version"

    def test_multiple_apps_can_have_version_command(self):
        """Test that multiple apps can each have their own version command."""
        app1 = typer.Typer()
        app2 = typer.Typer()

        version1 = register_version(app1)
        version2 = register_version(app2)

        # Both should have version commands registered
        assert len(app1.registered_commands) == 1
        assert len(app2.registered_commands) == 1

        # The functions should be different instances
        assert version1 is not version2
