import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from wa.workspace.cli.initialize import register_workspace_initialize


class TestWorkspaceInitializeCLI:
    @pytest.fixture
    def app(self):
        """Create a test Typer app with the initialize command registered."""
        test_app = typer.Typer()
        register_workspace_initialize(test_app)
        return test_app

    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()

    def test_initialize_command_success(self, app, runner):
        """Test successful workspace initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(
                app, ["initialize", "test_workspace", "--out-path", temp_dir]
            )

            assert result.exit_code == 0
            assert "Workspace initialized at:" in result.stdout
            assert "test_workspace" in result.stdout

            # Verify workspace was created
            workspace_path = Path(temp_dir) / "test_workspace"
            assert workspace_path.exists()
            assert (workspace_path / "workspace.json").exists()

    def test_initialize_command_with_init_alias(self, app, runner):
        """Test that 'init' alias works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(
                app, ["init", "test_workspace", "--out-path", temp_dir]
            )

            assert result.exit_code == 0
            assert "Workspace initialized at:" in result.stdout

    def test_initialize_command_existing_workspace_without_force(self, app, runner):
        """Test that initializing an existing workspace without --force fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workspace first time
            runner.invoke(app, ["initialize", "test_workspace", "--out-path", temp_dir])

            # Try to create again without --force
            result = runner.invoke(
                app, ["initialize", "test_workspace", "--out-path", temp_dir]
            )

            assert "already exists" in result.stdout
            assert "--force" in result.stdout

    def test_initialize_command_existing_workspace_with_force(self, app, runner):
        """Test that --force flag allows overwriting existing workspace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workspace first time
            runner.invoke(app, ["initialize", "test_workspace", "--out-path", temp_dir])

            # Create again with --force
            result = runner.invoke(
                app,
                ["initialize", "test_workspace", "--out-path", temp_dir, "--force"],
            )

            assert result.exit_code == 0
            assert "Workspace initialized at:" in result.stdout

    def test_initialize_command_without_out_path(self, app, runner):
        """Test initialization with default out_path."""
        with patch("wa.workspace.tools.create.get_project_root") as mock_root:
            with tempfile.TemporaryDirectory() as temp_dir:
                mock_root.return_value = Path(temp_dir)

                result = runner.invoke(app, ["initialize", "test_workspace"])

                assert result.exit_code == 0
                assert "Workspace initialized at:" in result.stdout

                # Verify workspace was created in default location
                workspace_path = Path(temp_dir) / "out" / "test_workspace"
                assert workspace_path.exists()

    def test_initialize_command_with_spaces_in_name(self, app, runner):
        """Test that workspace names with spaces are handled properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(
                app, ["initialize", "test workspace", "--out-path", temp_dir]
            )

            assert result.exit_code == 0
            assert "Workspace initialized at:" in result.stdout

            # Verify sanitized workspace name
            workspace_path = Path(temp_dir) / "test_workspace"
            assert workspace_path.exists()

    def test_initialize_command_creates_out_path(self, app, runner):
        """Test that non-existent out_path is created (single level)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "out"

            result = runner.invoke(
                app, ["initialize", "test_workspace", "--out-path", str(out_path)]
            )

            assert result.exit_code == 0
            assert out_path.exists()
            assert (out_path / "test_workspace").exists()

    def test_initialize_command_nested_out_path_fails(self, app, runner):
        """Test that nested non-existent out_path fails (expected behavior)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "out"

            result = runner.invoke(
                app, ["initialize", "test_workspace", "--out-path", str(nested_path)]
            )

            # Should fail because parent directory doesn't exist
            assert "Unable to create workspace directory" in result.stdout
