from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

from wa.mcp.install import install


class TestInstall:
    """Test the MCP install function."""

    @patch("wa.mcp.install.subprocess.run")
    def test_install_claude_code(self, mock_run, tmp_path):
        """Test installing for Claude Code client."""
        mock_run.return_value = MagicMock(returncode=0)

        install(path=tmp_path, client="claude-code", include_agent=False)

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "claude"
        assert args[1] == "mcp"
        assert args[2] == "add-json"
        assert args[3] == "workspace"
        assert "uv" in args[4]
        assert "wa.mcp" in args[4]

    @patch("wa.mcp.install.subprocess.run")
    @patch("wa.mcp.install.shutil.copyfileobj")
    @patch("wa.mcp.install.files")
    def test_install_claude_code_with_agent(
        self, mock_files, mock_copy, mock_run, tmp_path
    ):
        """Test installing for Claude Code client with agent configuration."""
        mock_run.return_value = MagicMock(returncode=0)
        mock_agent_file = MagicMock()
        mock_files.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_agent_file
        )

        install(path=tmp_path, client="claude-code", include_agent=True)

        # Verify the agent directory was created
        claude_agents_path = tmp_path / ".claude" / "agents"
        assert claude_agents_path.exists()

        # Verify subprocess was called
        mock_run.assert_called_once()

    @patch("wa.mcp.install.subprocess.run")
    def test_install_gemini_cli(self, mock_run, tmp_path):
        """Test installing for Gemini CLI client."""
        mock_run.return_value = MagicMock(returncode=0)

        install(path=tmp_path, client="gemini-cli")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "gemini"
        assert args[1] == "mcp"
        assert args[2] == "add"
        assert args[3] == "workspace"
        assert args[4] == "uv"
        assert "--directory" in args
        assert "wa.mcp" in args

    @patch("wa.mcp.install.subprocess.run")
    def test_install_codex(self, mock_run, tmp_path):
        """Test installing for Codex client."""
        mock_run.return_value = MagicMock(returncode=0)

        install(path=tmp_path, client="codex")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "codex"
        assert args[1] == "mcp"
        assert args[2] == "add"
        assert args[3] == "workspace"
        assert args[4] == "uv"
        assert "--directory" in args
        assert "wa.mcp" in args

    @patch("wa.mcp.install.subprocess.run")
    @patch("wa.mcp.install.rprint")
    def test_install_with_invalid_client(self, mock_rprint, mock_run, tmp_path):
        """Test installing with an invalid client name."""
        install(path=tmp_path, client="invalid")

        # Verify that rprint was called with warning message
        mock_rprint.assert_called()
        call_args = " ".join(
            [str(arg) for call in mock_rprint.call_args_list for arg in call[0]]
        )
        assert "No client provided" in call_args

    @patch("wa.mcp.install.subprocess.run")
    @patch("wa.mcp.install.rprint")
    def test_install_handles_subprocess_error(self, mock_rprint, mock_run, tmp_path):
        """Test that install handles subprocess errors gracefully."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["cmd"])

        install(path=tmp_path, client="claude-code", include_agent=False)

        # Verify error message was printed
        mock_rprint.assert_called()
        call_args = " ".join(
            [str(arg) for call in mock_rprint.call_args_list for arg in call[0]]
        )
        assert "failed" in call_args.lower()

    @patch("wa.mcp.install.subprocess.run")
    @patch("wa.mcp.install.rprint")
    def test_install_handles_unexpected_error(self, mock_rprint, mock_run, tmp_path):
        """Test that install handles unexpected errors gracefully."""
        mock_run.side_effect = Exception("Unexpected error")

        install(path=tmp_path, client="claude-code", include_agent=False)

        # Verify error message was printed
        mock_rprint.assert_called()
        call_args = " ".join(
            [str(arg) for call in mock_rprint.call_args_list for arg in call[0]]
        )
        assert "Unexpected error" in call_args

    @patch("wa.mcp.install.subprocess.run")
    def test_install_uses_correct_server_name(self, mock_run, tmp_path):
        """Test that all clients use 'workspace' as the server name."""
        mock_run.return_value = MagicMock(returncode=0)

        clients = ["claude-code", "gemini-cli", "codex"]

        for client in clients:
            mock_run.reset_mock()
            install(path=tmp_path, client=client, include_agent=False)

            args = mock_run.call_args[0][0]
            # Verify 'workspace' appears in the command
            if client == "claude-code":
                assert args[3] == "workspace"
            else:
                assert args[3] == "workspace"
