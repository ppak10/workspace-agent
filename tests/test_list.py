"""Tests for workspace folder listing functionality."""

from pathlib import Path

import pytest

from wa.folder.list import list_workspace_folders
from wa.models import Workspace


class TestListWorkspaceFolders:
    """Test cases for list_workspace_folders function."""

    def test_list_empty_workspaces_folder(self, temp_workspaces_path: Path):
        """Test listing when workspaces folder is empty."""
        result = list_workspace_folders(workspaces_folder_path=temp_workspaces_path)

        assert result == []

    def test_list_single_workspace(
        self, sample_workspace: Workspace, temp_workspaces_path: Path
    ):
        """Test listing a single workspace."""
        result = list_workspace_folders(workspaces_folder_path=temp_workspaces_path)

        assert len(result) == 1
        assert sample_workspace.name in result

    def test_list_multiple_workspaces(self, temp_workspaces_path: Path):
        """Test listing multiple workspaces."""
        # Create multiple workspaces
        workspace_names = ["workspace1", "workspace2", "workspace3"]
        for name in workspace_names:
            workspace = Workspace(
                name=name,
                workspaces_folder_path=temp_workspaces_path,
            )
            workspace.save()

        result = list_workspace_folders(workspaces_folder_path=temp_workspaces_path)

        assert len(result) == 3
        assert set(result) == set(workspace_names)

    def test_list_creates_workspaces_folder_if_not_exists(self, tmp_path: Path):
        """Test that list creates workspaces folder if it doesn't exist."""
        workspaces_path = tmp_path / "new_workspaces"
        assert not workspaces_path.exists()

        result = list_workspace_folders(workspaces_folder_path=workspaces_path)

        assert workspaces_path.exists()
        assert result == []

    def test_list_ignores_files_in_workspaces_folder(self, temp_workspaces_path: Path):
        """Test that listing ignores regular files, only shows directories."""
        # Create a workspace
        workspace = Workspace(
            name="valid_workspace",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace.save()

        # Create a regular file in workspaces folder
        (temp_workspaces_path / "some_file.txt").write_text("test")

        result = list_workspace_folders(workspaces_folder_path=temp_workspaces_path)

        assert len(result) == 1
        assert "valid_workspace" in result
        assert "some_file.txt" not in result

    def test_list_includes_dirs_without_config(self, temp_workspaces_path: Path):
        """Test that listing includes all directories, even without config files."""
        # Create a workspace with config
        workspace = Workspace(
            name="with_config",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace.save()

        # Create a directory without config file
        (temp_workspaces_path / "without_config").mkdir()

        result = list_workspace_folders(workspaces_folder_path=temp_workspaces_path)

        # Both directories should be listed (based on actual implementation)
        assert len(result) == 2
        assert "with_config" in result
        assert "without_config" in result

    def test_list_with_default_path(self, monkeypatch, tmp_path: Path):
        """Test listing with default path from get_project_root."""
        import wa.folder.list
        import wa.models

        # Mock get_project_root in both modules where it's used
        monkeypatch.setattr("wa.folder.list.get_project_root", lambda: tmp_path)
        monkeypatch.setattr("wa.models.get_project_root", lambda: tmp_path)

        # Create workspace at default location
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test",
            workspaces_folder_path=workspaces_path,
        )
        workspace.save()

        # List without specifying path (should use default)
        result = list_workspace_folders()

        assert "test" in result

    def test_list_workspaces_folder_is_file_raises_error(self, tmp_path: Path):
        """Test that listing raises error if workspaces_folder_path is a file."""
        # Create a file instead of directory
        file_path = tmp_path / "workspaces_file"
        file_path.write_text("test")

        with pytest.raises(FileNotFoundError):
            list_workspace_folders(workspaces_folder_path=file_path)

    def test_list_nested_directories_not_listed(self, temp_workspaces_path: Path):
        """Test that nested directories within workspaces are not listed."""
        # Create a workspace
        workspace = Workspace(
            name="parent_workspace",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace.save()

        # Create a nested directory inside the workspace
        nested_dir = workspace.path / "nested"
        nested_dir.mkdir()

        result = list_workspace_folders(workspaces_folder_path=temp_workspaces_path)

        assert len(result) == 1
        assert "parent_workspace" in result
        assert "nested" not in result

    def test_list_returns_list_of_strings(self, temp_workspaces_path: Path):
        """Test that list returns a list of strings, not Path objects."""
        workspace = Workspace(
            name="test",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace.save()

        result = list_workspace_folders(workspaces_folder_path=temp_workspaces_path)

        assert isinstance(result, list)
        assert all(isinstance(name, str) for name in result)

    def test_list_workspace_names_only(self, temp_workspaces_path: Path):
        """Test that list returns workspace names, not full paths."""
        workspace = Workspace(
            name="my_workspace",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace.save()

        result = list_workspace_folders(workspaces_folder_path=temp_workspaces_path)

        assert result == ["my_workspace"]
        # Ensure it's not the full path
        assert str(temp_workspaces_path) not in result[0]
