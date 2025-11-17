from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from wa.mcp.uninstall import uninstall


class TestUninstall:
    """Test the MCP uninstall function."""

    @patch("wa.mcp.uninstall.subprocess.run")
    def test_uninstall_claude_code(self, mock_run):
        """Test uninstalling for Claude Code client."""
        mock_run.return_value = MagicMock(returncode=0)

        uninstall(client="claude-code")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["claude", "mcp", "remove", "workspace"]

    @patch("wa.mcp.uninstall.subprocess.run")
    def test_uninstall_gemini_cli(self, mock_run):
        """Test uninstalling for Gemini CLI client."""
        mock_run.return_value = MagicMock(returncode=0)

        uninstall(client="gemini-cli")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["gemini", "mcp", "remove", "workspace"]

    @patch("wa.mcp.uninstall.subprocess.run")
    def test_uninstall_codex(self, mock_run):
        """Test uninstalling for Codex client."""
        mock_run.return_value = MagicMock(returncode=0)

        uninstall(client="codex")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args == ["codex", "mcp", "remove", "workspace"]

    @patch("wa.mcp.uninstall.subprocess.run")
    @patch("wa.mcp.uninstall.rprint")
    def test_uninstall_with_invalid_client(self, mock_rprint, mock_run):
        """Test uninstalling with an invalid client name."""
        uninstall(client="invalid")

        # Verify that subprocess was not called
        mock_run.assert_not_called()

        # Verify that rprint was called with warning message
        mock_rprint.assert_called_once()
        call_args = str(mock_rprint.call_args[0][0])
        assert "No client provided" in call_args

    @patch("wa.mcp.uninstall.subprocess.run")
    @patch("wa.mcp.uninstall.rprint")
    def test_uninstall_handles_subprocess_error(self, mock_rprint, mock_run):
        """Test that uninstall handles subprocess errors gracefully."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["cmd"])

        uninstall(client="claude-code")

        # Verify error message was printed
        mock_rprint.assert_called()
        call_args = " ".join(
            [str(arg) for call in mock_rprint.call_args_list for arg in call[0]]
        )
        assert "failed" in call_args.lower()

    @patch("wa.mcp.uninstall.subprocess.run")
    @patch("wa.mcp.uninstall.rprint")
    def test_uninstall_handles_subprocess_error_with_stderr(
        self, mock_rprint, mock_run
    ):
        """Test that uninstall handles subprocess errors with stderr."""
        error = subprocess.CalledProcessError(1, ["cmd"])
        error.stderr = "Error details"
        mock_run.side_effect = error

        uninstall(client="claude-code")

        # Verify error message was printed with stderr
        mock_rprint.assert_called()
        call_args = " ".join(
            [str(arg) for call in mock_rprint.call_args_list for arg in call[0]]
        )
        assert "Error output" in call_args or "failed" in call_args.lower()

    @patch("wa.mcp.uninstall.subprocess.run")
    @patch("wa.mcp.uninstall.rprint")
    def test_uninstall_handles_unexpected_error(self, mock_rprint, mock_run):
        """Test that uninstall handles unexpected errors gracefully."""
        mock_run.side_effect = Exception("Unexpected error")

        uninstall(client="claude-code")

        # Verify error message was printed
        mock_rprint.assert_called()
        call_args = " ".join(
            [str(arg) for call in mock_rprint.call_args_list for arg in call[0]]
        )
        assert "Unexpected error" in call_args

    @patch("wa.mcp.uninstall.subprocess.run")
    @patch("wa.mcp.uninstall.rprint")
    def test_uninstall_prints_command_before_running(self, mock_rprint, mock_run):
        """Test that uninstall prints the command before executing it."""
        mock_run.return_value = MagicMock(returncode=0)

        uninstall(client="claude-code")

        # Verify command was printed
        mock_rprint.assert_called()
        call_args = " ".join(
            [str(arg) for call in mock_rprint.call_args_list for arg in call[0]]
        )
        assert (
            "Running command" in call_args or "claude mcp remove workspace" in call_args
        )

    @patch("wa.mcp.uninstall.subprocess.run")
    def test_uninstall_uses_correct_server_name(self, mock_run):
        """Test that all clients use 'workspace' as the server name."""
        mock_run.return_value = MagicMock(returncode=0)

        clients = ["claude-code", "gemini-cli", "codex"]

        for client in clients:
            mock_run.reset_mock()
            uninstall(client=client)

            args = mock_run.call_args[0][0]
            # Verify 'workspace' is the server name (last argument)
            assert args[-1] == "workspace"

    @patch("wa.mcp.uninstall.subprocess.run")
    def test_uninstall_with_empty_client(self, mock_run):
        """Test uninstalling with an empty client string."""
        uninstall(client="")

        # Verify that subprocess was not called
        mock_run.assert_not_called()

    @patch("wa.mcp.uninstall.subprocess.run")
    def test_uninstall_runs_with_check_true(self, mock_run):
        """Test that uninstall runs subprocess with check=True."""
        mock_run.return_value = MagicMock(returncode=0)

        uninstall(client="claude-code")

        # Verify subprocess.run was called with check=True
        mock_run.assert_called_once()
        assert mock_run.call_args[1]["check"] is True
