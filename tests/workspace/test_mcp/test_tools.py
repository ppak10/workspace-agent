from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from wa.workspace.models.workspace import Workspace
from wa.workspace.models.workspace_folder import WorkspaceFolder

# Skip tests if mcp.server is not available (can happen due to import order issues)
try:
    import mcp.server.fastmcp  # noqa: F401

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp.server not available")
class TestWorkspaceManagementTool:
    """Test the workspace_management MCP tool."""

    @pytest.fixture
    def workspace_tool(self):
        """Get the workspace_management tool function by registering it on a mock app."""
        # Create a mock FastMCP app
        mock_app = MagicMock()

        # Capture the decorated function when @app.tool is called
        captured_func = None

        def capture_tool(**kwargs):
            def decorator(func):
                nonlocal captured_func
                captured_func = func
                return func

            return decorator

        mock_app.tool = capture_tool

        # Import and register the tools
        from wa.workspace.mcp.tools import register_workspace_tools

        register_workspace_tools(mock_app)

        return captured_func

    def test_list_workspaces(self, workspace_tool, tmp_path):
        """Test listing workspaces."""
        workspaces_path = tmp_path / "workspaces"

        # Create some workspaces
        workspace1 = Workspace(
            name="workspace1",
            workspaces_path=workspaces_path,
        )
        workspace1.save()

        workspace2 = Workspace(
            name="workspace2",
            workspaces_path=workspaces_path,
        )
        workspace2.save()

        with patch("wa.workspace.list.get_project_root", return_value=tmp_path):
            result = workspace_tool(method="list")

        assert result.success is True
        assert "workspace1" in result.data
        assert "workspace2" in result.data

    def test_create_workspace(self, workspace_tool, tmp_path):
        """Test creating a workspace."""
        with patch("wa.workspace.create.get_project_root", return_value=tmp_path):
            result = workspace_tool(
                workspace_name="new_workspace",
                method="create",
            )

        assert result.success is True
        assert (tmp_path / "workspaces" / "new_workspace").exists()

    def test_create_workspace_folder(self, workspace_tool, tmp_path):
        """Test creating a folder within a workspace."""
        workspaces_path = tmp_path / "workspaces"

        # Create workspace first
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()
        workspace.path.mkdir(parents=True, exist_ok=True)

        with patch("wa.workspace.create.get_project_root", return_value=tmp_path):
            result = workspace_tool(
                workspace_name="test_workspace",
                folder_name=["new_folder"],
                method="create",
            )

        assert result.success is True

    def test_read_workspace(self, workspace_tool, tmp_path):
        """Test reading a workspace."""
        workspaces_path = tmp_path / "workspaces"

        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="folder1")],
        )
        workspace.save()

        with patch("wa.workspace.read.get_project_root", return_value=tmp_path):
            result = workspace_tool(
                workspace_name="test_workspace",
                method="read",
            )

        assert result.success is True

    def test_read_workspace_with_include_files(self, workspace_tool, tmp_path):
        """Test reading a workspace with include_files=True."""
        workspaces_path = tmp_path / "workspaces"

        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="folder1")],
        )
        workspace.save()

        # Create a file in the workspace
        (workspace.path / "test_file.txt").write_text("content")

        with patch("wa.workspace.read.get_project_root", return_value=tmp_path):
            result = workspace_tool(
                workspace_name="test_workspace",
                method="read",
                include_files=True,
            )

        assert result.success is True

    def test_read_workspace_folder(self, workspace_tool, tmp_path):
        """Test reading a specific folder within a workspace."""
        workspaces_path = tmp_path / "workspaces"

        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="folder1")],
        )
        workspace.save()

        # Create the folder
        folder_path = workspace.path / "folder1"
        folder_path.mkdir(parents=True, exist_ok=True)

        with patch("wa.workspace.read.get_project_root", return_value=tmp_path):
            result = workspace_tool(
                workspace_name="test_workspace",
                folder_name=["folder1"],
                method="read",
                include_files=True,
            )

        assert result.success is True

    def test_unknown_method_error(self, workspace_tool):
        """Test that unknown methods return an error."""
        result = workspace_tool(
            workspace_name="test",
            method="invalid_method",
        )

        assert result.success is False
        assert "UNKNOWN_METHOD" in result.error_code

    def test_missing_workspace_name_error(self, workspace_tool):
        """Test that missing workspace name for create/read returns an error."""
        result = workspace_tool(
            workspace_name=None,
            method="create",
        )

        assert result.success is False
        assert "INVALID_WORKSPACE_NAME" in result.error_code

    def test_file_not_found_error(self, workspace_tool, tmp_path):
        """Test that FileNotFoundError is handled."""
        with patch("wa.workspace.read.get_project_root", return_value=tmp_path):
            result = workspace_tool(
                workspace_name="nonexistent",
                method="read",
            )

        assert result.success is False
        assert "FILE_NOT_FOUND" in result.error_code

    def test_file_exists_error(self, workspace_tool, tmp_path):
        """Test that FileExistsError is handled."""
        workspaces_path = tmp_path / "workspaces"

        # Create workspace
        workspace = Workspace(
            name="existing",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        with patch("wa.workspace.create.get_project_root", return_value=tmp_path):
            # Try to create again without force
            result = workspace_tool(
                workspace_name="existing",
                method="create",
                force=False,
            )

        assert result.success is False
        assert "FILE_EXISTS" in result.error_code

    def test_permission_error(self, workspace_tool, tmp_path):
        """Test that PermissionError is handled."""
        with patch("wa.workspace.create.get_project_root", return_value=tmp_path):
            with patch(
                "wa.workspace.create.create_workspace",
                side_effect=PermissionError("Permission denied"),
            ):
                result = workspace_tool(
                    workspace_name="test",
                    method="create",
                )

        assert result.success is False
        assert "PERMISSION_DENIED" in result.error_code

    def test_generic_exception_error(self, workspace_tool, tmp_path):
        """Test that generic exceptions are handled."""
        with patch(
            "wa.workspace.list.list_workspaces",
            side_effect=RuntimeError("Something went wrong"),
        ):
            result = workspace_tool(method="list")

        assert result.success is False
        assert "WORKSPACE_FOLDER_FAILED" in result.error_code
