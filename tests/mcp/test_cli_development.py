from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
import typer

from wa.mcp.cli.development import register_mcp_development

# Skip all MCP development tests if mcp.cli is not available
try:
    import mcp.cli

    MCP_CLI_AVAILABLE = True
except ImportError:
    MCP_CLI_AVAILABLE = False

skip_if_no_mcp_cli = pytest.mark.skipif(
    not MCP_CLI_AVAILABLE, reason="mcp.cli module not available"
)


class TestRegisterMcpDevelopment:
    """Test the register_mcp_development function."""

    def test_register_mcp_development_creates_command(self):
        """Test that register_mcp_development registers a command with the app."""
        mock_app = typer.Typer()
        result = register_mcp_development(mock_app)

        # Should return the mcp_development function
        assert callable(result)
        assert result.__name__ == "mcp_development"

        # Should have registered two commands: "development" and "dev"
        assert len(mock_app.registered_commands) == 2

        command_names = [cmd.name for cmd in mock_app.registered_commands]
        assert "development" in command_names
        assert "dev" in command_names

    def test_register_mcp_development_returns_function(self):
        """Test that register_mcp_development returns the development function."""
        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)

        assert callable(dev_func)
        assert dev_func.__name__ == "mcp_development"

    def test_register_mcp_development_creates_aliases(self):
        """Test that both 'development' and 'dev' commands point to same function."""
        mock_app = typer.Typer()
        register_mcp_development(mock_app)

        # Get both commands
        commands = {cmd.name: cmd for cmd in mock_app.registered_commands}

        # Both should exist
        assert "development" in commands
        assert "dev" in commands

        # Both should have the same callback function
        assert commands["development"].callback == commands["dev"].callback


@skip_if_no_mcp_cli
class TestMcpDevelopmentCommand:
    """Test the mcp_development command functionality."""

    @patch("wa.mcp.cli.development.subprocess.run")
    @patch("wa.mcp.cli.development.files")
    @patch("wa.mcp.cli.development.rprint")
    @patch("builtins.print")
    @patch("mcp.cli.cli")
    def test_mcp_development_success(
        self, mock_cli, mock_print, mock_rprint, mock_files, mock_subprocess_run
    ):
        """Test mcp_development command successful execution."""
        # Mock the MCP CLI
        mock_cli._get_npx_command.return_value = "npx"

        # Mock files resource
        mock_file_spec = MagicMock()
        mock_file_spec.__str__ = lambda self: "/path/to/wa/mcp/__main__.py"
        mock_files.return_value.joinpath.return_value = mock_file_spec

        # Mock subprocess
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)

        # Call the function
        dev_func()

        # Should print starting message
        assert mock_rprint.call_count >= 1
        mock_rprint.assert_any_call("Starting MCP Development Server")

        # Should call subprocess.run with correct arguments
        mock_subprocess_run.assert_called_once()

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.rprint")
    def test_mcp_development_npx_not_found(self, mock_rprint, mock_cli):
        """Test mcp_development when npx is not found."""
        # Mock the MCP CLI with no npx command
        mock_cli._get_npx_command.return_value = None
        mock_cli.logger = MagicMock()

        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)

        # Should raise typer.Exit with code 1
        with pytest.raises(typer.Exit) as exc_info:
            dev_func()

        assert exc_info.value.exit_code == 1

        # Should log error message
        mock_cli.logger.error.assert_called_once()
        error_msg = mock_cli.logger.error.call_args[0][0]
        assert "npx not found" in error_msg

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.subprocess.run")
    @patch("wa.mcp.cli.development.files")
    @patch("wa.mcp.cli.development.rprint")
    @patch("builtins.print")
    def test_mcp_development_windows_shell_flag(
        self, mock_print, mock_rprint, mock_files, mock_subprocess_run, mock_cli
    ):
        """Test that shell=True is used on Windows."""
        mock_cli._get_npx_command.return_value = "npx"

        mock_file_spec = MagicMock()
        mock_file_spec.__str__ = lambda self: "/path/to/__main__.py"
        mock_files.return_value.joinpath.return_value = mock_file_spec

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        with patch("wa.mcp.cli.development.sys.platform", "win32"):
            mock_app = typer.Typer()
            dev_func = register_mcp_development(mock_app)
            dev_func()

        # Check that shell=True was used
        call_kwargs = mock_subprocess_run.call_args[1]
        assert call_kwargs["shell"] is True

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.subprocess.run")
    @patch("wa.mcp.cli.development.files")
    @patch("wa.mcp.cli.development.rprint")
    @patch("builtins.print")
    def test_mcp_development_non_windows_shell_flag(
        self, mock_print, mock_rprint, mock_files, mock_subprocess_run, mock_cli
    ):
        """Test that shell=False is used on non-Windows platforms."""
        mock_cli._get_npx_command.return_value = "npx"

        mock_file_spec = MagicMock()
        mock_file_spec.__str__ = lambda self: "/path/to/__main__.py"
        mock_files.return_value.joinpath.return_value = mock_file_spec

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        with patch("wa.mcp.cli.development.sys.platform", "linux"):
            mock_app = typer.Typer()
            dev_func = register_mcp_development(mock_app)
            dev_func()

        # Check that shell=False was used
        call_kwargs = mock_subprocess_run.call_args[1]
        assert call_kwargs["shell"] is False

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.subprocess.run")
    @patch("wa.mcp.cli.development.files")
    @patch("wa.mcp.cli.development.rprint")
    @patch("builtins.print")
    def test_mcp_development_subprocess_command_structure(
        self, mock_print, mock_rprint, mock_files, mock_subprocess_run, mock_cli
    ):
        """Test the structure of the subprocess command."""
        mock_cli._get_npx_command.return_value = "npx"

        mock_file_spec = MagicMock()
        mock_file_spec.__str__ = lambda self: "/path/to/wa/mcp/__main__.py"
        mock_files.return_value.joinpath.return_value = mock_file_spec

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)
        dev_func()

        # Get the command that was passed to subprocess.run
        call_args = mock_subprocess_run.call_args[0][0]

        # Should start with npx and inspector package
        assert call_args[0] == "npx"
        assert call_args[1] == "@modelcontextprotocol/inspector"

        # Should contain uv run commands
        assert "uv" in call_args
        assert "run" in call_args
        assert "--with" in call_args
        assert "mcp" in call_args

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.subprocess.run")
    @patch("wa.mcp.cli.development.files")
    @patch("wa.mcp.cli.development.rprint")
    @patch("builtins.print")
    def test_mcp_development_uses_environment(
        self, mock_print, mock_rprint, mock_files, mock_subprocess_run, mock_cli
    ):
        """Test that subprocess uses current environment."""
        mock_cli._get_npx_command.return_value = "npx"

        mock_file_spec = MagicMock()
        mock_file_spec.__str__ = lambda self: "/path/to/__main__.py"
        mock_files.return_value.joinpath.return_value = mock_file_spec

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)
        dev_func()

        # Check that env was passed
        call_kwargs = mock_subprocess_run.call_args[1]
        assert "env" in call_kwargs
        assert isinstance(call_kwargs["env"], dict)

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.subprocess.run")
    @patch("wa.mcp.cli.development.files")
    @patch("wa.mcp.cli.development.rprint")
    @patch("builtins.print")
    def test_mcp_development_exception_handling(
        self, mock_print, mock_rprint, mock_files, mock_subprocess_run, mock_cli
    ):
        """Test exception handling in mcp_development."""
        mock_cli._get_npx_command.return_value = "npx"

        mock_file_spec = MagicMock()
        mock_files.return_value.joinpath.return_value = mock_file_spec

        # Simulate subprocess raising an exception
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, "npx", stderr="Error"
        )

        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)

        with pytest.raises(typer.Exit) as exc_info:
            dev_func()

        # Should exit with code 1
        assert exc_info.value.exit_code == 1

        # Should print error message
        error_calls = [
            call
            for call in mock_rprint.call_args_list
            if "Unable to initialize" in str(call)
        ]
        assert len(error_calls) > 0

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.subprocess.run")
    @patch("wa.mcp.cli.development.files")
    @patch("wa.mcp.cli.development.rprint")
    @patch("builtins.print")
    def test_mcp_development_file_spec_resolution(
        self, mock_print, mock_rprint, mock_files, mock_subprocess_run, mock_cli
    ):
        """Test that file spec is resolved correctly."""
        mock_cli._get_npx_command.return_value = "npx"

        mock_file_spec = MagicMock()
        mock_file_spec.__str__ = lambda self: "/resolved/path/__main__.py"
        mock_joinpath = MagicMock(return_value=mock_file_spec)
        mock_files.return_value.joinpath = mock_joinpath

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)
        dev_func()

        # Should have called files with "wa.mcp"
        mock_files.assert_called_once_with("wa.mcp")

        # Should have joined with "__main__.py"
        mock_joinpath.assert_called_once_with("__main__.py")

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.subprocess.run")
    @patch("wa.mcp.cli.development.files")
    @patch("wa.mcp.cli.development.rprint")
    @patch("builtins.print")
    def test_mcp_development_subprocess_check_flag(
        self, mock_print, mock_rprint, mock_files, mock_subprocess_run, mock_cli
    ):
        """Test that subprocess.run is called with check=True."""
        mock_cli._get_npx_command.return_value = "npx"

        mock_file_spec = MagicMock()
        mock_file_spec.__str__ = lambda self: "/path/__main__.py"
        mock_files.return_value.joinpath.return_value = mock_file_spec

        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_subprocess_run.return_value = mock_process

        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)
        dev_func()

        # Should have check=True
        call_kwargs = mock_subprocess_run.call_args[1]
        assert call_kwargs["check"] is True

    @patch("mcp.cli.cli")
    @patch("wa.mcp.cli.development.rprint")
    def test_mcp_development_starting_message(self, mock_rprint, mock_cli):
        """Test that starting message is printed."""
        mock_cli._get_npx_command.return_value = None
        mock_cli.logger = MagicMock()

        mock_app = typer.Typer()
        dev_func = register_mcp_development(mock_app)

        with pytest.raises(typer.Exit):
            dev_func()

        # First rprint call should be the starting message
        first_call = mock_rprint.call_args_list[0][0][0]
        assert first_call == "Starting MCP Development Server"
