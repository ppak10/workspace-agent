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

        # Capture the decorated functions when @app.tool is called
        captured_funcs = []

        def capture_tool(**kwargs):
            def decorator(func):
                captured_funcs.append(func)
                return func

            return decorator

        mock_app.tool = capture_tool

        # Import and register the tools
        from wa.workspace.mcp.tools import register_workspace_tools

        register_workspace_tools(mock_app)

        # Return the workspace_management tool (first one registered)
        return captured_funcs[0] if len(captured_funcs) > 0 else None

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


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp.server not available")
class TestWorkspaceFileTool:
    """Test the workspace_file MCP tool."""

    @pytest.fixture
    def workspace_file_tool(self):
        """Get the workspace_file tool function by registering it on a mock app."""
        # Create a mock FastMCP app
        mock_app = MagicMock()

        # Capture the decorated functions when @app.tool is called
        captured_funcs = []

        def capture_tool(**kwargs):
            def decorator(func):
                captured_funcs.append(func)
                return func

            return decorator

        mock_app.tool = capture_tool

        # Import and register the tools
        from wa.workspace.mcp.tools import register_workspace_tools

        register_workspace_tools(mock_app)

        # Return the workspace_file tool (second one registered)
        return captured_funcs[1] if len(captured_funcs) > 1 else None

    def test_read_png_file(self, workspace_file_tool, tmp_path):
        """Test reading a PNG file."""
        import base64

        # Create a simple PNG file (1x1 transparent PNG)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        png_file = tmp_path / "test.png"
        png_file.write_bytes(png_data)

        result = workspace_file_tool(path=str(png_file), method="read")

        assert result.success is True
        assert result.data["type"] == "image"
        assert result.data["mimeType"] == "image/png"
        assert "data" in result.data
        assert result.data["path"] == str(png_file)

    def test_read_json_file(self, workspace_file_tool, tmp_path):
        """Test reading a JSON file."""
        import json

        json_data = {"name": "test", "value": 42}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(json_data))

        result = workspace_file_tool(path=str(json_file), method="read")

        assert result.success is True
        assert result.data["type"] == "json"
        assert result.data["data"] == json_data
        assert result.data["path"] == str(json_file)

    def test_file_not_found(self, workspace_file_tool, tmp_path):
        """Test handling of non-existent file."""
        non_existent = tmp_path / "does_not_exist.png"

        result = workspace_file_tool(path=str(non_existent), method="read")

        assert result.success is False
        assert "FILE_NOT_FOUND" in result.error_code

    def test_path_is_directory(self, workspace_file_tool, tmp_path):
        """Test handling when path is a directory."""
        directory = tmp_path / "test_dir"
        directory.mkdir()

        result = workspace_file_tool(path=str(directory), method="read")

        assert result.success is False
        assert "INVALID_PATH" in result.error_code

    def test_unsupported_file_type(self, workspace_file_tool, tmp_path):
        """Test handling of unsupported file extensions."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Some text")

        result = workspace_file_tool(path=str(txt_file), method="read")

        assert result.success is False
        assert "UNSUPPORTED_FILE_TYPE" in result.error_code

    def test_invalid_json(self, workspace_file_tool, tmp_path):
        """Test handling of invalid JSON file."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json }")

        result = workspace_file_tool(path=str(json_file), method="read")

        assert result.success is False
        assert "INVALID_JSON" in result.error_code

    def test_unknown_method(self, workspace_file_tool, tmp_path):
        """Test handling of unknown method."""
        png_file = tmp_path / "test.png"
        png_file.write_bytes(b"fake data")

        result = workspace_file_tool(path=str(png_file), method="write")

        assert result.success is False
        assert "UNKNOWN_METHOD" in result.error_code

    def test_copy_file_to_directory(self, workspace_file_tool, tmp_path):
        """Test copying a file to a directory destination."""
        # Create source file
        source_file = tmp_path / "source.txt"
        source_file.write_text("test content")

        # Create destination directory
        dest_dir = tmp_path / "destination"
        dest_dir.mkdir()

        result = workspace_file_tool(
            path=str(source_file), method="copy", destination=str(dest_dir)
        )

        assert result.success is True
        assert result.data["copied"] is True
        assert result.data["source"] == str(source_file)
        assert result.data["destination"] == str(dest_dir / "source.txt")

        # Verify file was copied
        copied_file = dest_dir / "source.txt"
        assert copied_file.exists()
        assert copied_file.read_text() == "test content"

    def test_copy_file_to_file_path(self, workspace_file_tool, tmp_path):
        """Test copying a file to a specific file path."""
        # Create source file
        source_file = tmp_path / "source.png"
        source_file.write_bytes(b"fake png data")

        # Specify destination file path
        dest_file = tmp_path / "destination" / "renamed.png"

        result = workspace_file_tool(
            path=str(source_file), method="copy", destination=str(dest_file)
        )

        assert result.success is True
        assert result.data["copied"] is True
        assert result.data["source"] == str(source_file)
        assert result.data["destination"] == str(dest_file)

        # Verify file was copied with new name
        assert dest_file.exists()
        assert dest_file.read_bytes() == b"fake png data"

    def test_copy_creates_destination_directory(self, workspace_file_tool, tmp_path):
        """Test that copy creates destination directory if it doesn't exist."""
        # Create source file
        source_file = tmp_path / "source.json"
        source_file.write_text('{"key": "value"}')

        # Specify destination in non-existent directory
        dest_file = tmp_path / "new_dir" / "subdir" / "file.json"

        result = workspace_file_tool(
            path=str(source_file), method="copy", destination=str(dest_file)
        )

        assert result.success is True
        assert dest_file.exists()
        assert dest_file.read_text() == '{"key": "value"}'

    def test_copy_missing_destination(self, workspace_file_tool, tmp_path):
        """Test that copy fails when destination is not provided."""
        source_file = tmp_path / "source.txt"
        source_file.write_text("content")

        result = workspace_file_tool(path=str(source_file), method="copy")

        assert result.success is False
        assert "MISSING_DESTINATION" in result.error_code

    def test_copy_preserves_file_metadata(self, workspace_file_tool, tmp_path):
        """Test that copy preserves file metadata."""
        import time

        # Create source file
        source_file = tmp_path / "source.txt"
        source_file.write_text("content")

        # Set a specific modification time
        old_time = time.time() - 86400  # 1 day ago
        import os

        os.utime(source_file, (old_time, old_time))

        # Copy file
        dest_file = tmp_path / "dest.txt"
        result = workspace_file_tool(
            path=str(source_file), method="copy", destination=str(dest_file)
        )

        assert result.success is True

        # Verify metadata was preserved (shutil.copy2 preserves timestamps)
        source_stat = source_file.stat()
        dest_stat = dest_file.stat()
        assert abs(source_stat.st_mtime - dest_stat.st_mtime) < 1  # Within 1 second

    def test_copy_non_existent_source(self, workspace_file_tool, tmp_path):
        """Test copying a non-existent file."""
        source_file = tmp_path / "does_not_exist.txt"
        dest_file = tmp_path / "dest.txt"

        result = workspace_file_tool(
            path=str(source_file), method="copy", destination=str(dest_file)
        )

        assert result.success is False
        assert "FILE_NOT_FOUND" in result.error_code
