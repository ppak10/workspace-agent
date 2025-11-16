"""Tests for workspace folder reading functionality."""

from pathlib import Path

import pytest

from wa.folder.read import read_workspace_folder
from wa.models import Workspace, WorkspaceSubfolder


class TestReadWorkspaceFolder:
    """Test cases for read_workspace_folder function."""

    def test_read_existing_workspace(
        self, sample_workspace: Workspace, temp_workspaces_path: Path
    ):
        """Test reading an existing workspace."""
        loaded_workspace = read_workspace_folder(
            name=sample_workspace.name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert loaded_workspace.name == sample_workspace.name
        assert loaded_workspace.path == sample_workspace.path
        assert loaded_workspace.workspaces_folder_path == temp_workspaces_path

    def test_read_workspace_with_subfolders(self, temp_workspaces_path: Path):
        """Test reading a workspace that has subfolders defined."""
        # Create workspace with subfolders
        workspace = Workspace(
            name="test_with_subfolders",
            workspaces_folder_path=temp_workspaces_path,
            subfolders=[
                WorkspaceSubfolder(name="data"),
                WorkspaceSubfolder(name="models"),
                WorkspaceSubfolder(name="results"),
            ],
        )
        workspace.save()

        # Read it back
        loaded_workspace = read_workspace_folder(
            name="test_with_subfolders",
            workspaces_folder_path=temp_workspaces_path,
        )

        assert set(loaded_workspace.subfolders.keys()) == {"data", "models", "results"}

    def test_read_nonexistent_workspace_raises_error(self, temp_workspaces_path: Path):
        """Test that reading a non-existent workspace raises FileNotFoundError."""
        with pytest.raises(
            FileNotFoundError, match="Workspace folder: `nonexistent` does not exist"
        ):
            read_workspace_folder(
                name="nonexistent",
                workspaces_folder_path=temp_workspaces_path,
            )

    def test_read_workspace_folder_not_exists_raises_error(self, tmp_path: Path):
        """Test that reading from non-existent workspaces folder raises FileNotFoundError."""
        nonexistent_path = tmp_path / "nonexistent_workspaces"

        with pytest.raises(FileNotFoundError, match="Workspaces folder does not exist"):
            read_workspace_folder(
                name="test",
                workspaces_folder_path=nonexistent_path,
            )

    def test_read_workspace_preserves_all_fields(self, temp_workspaces_path: Path):
        """Test that all workspace fields are preserved when reading."""
        # Create workspace with all fields
        original = Workspace(
            name="complete_workspace",
            workspaces_folder_path=temp_workspaces_path,
            subfolders=[
                WorkspaceSubfolder(name="sub1"),
                WorkspaceSubfolder(name="sub2"),
            ],
        )
        original.save()

        # Read it back
        loaded = read_workspace_folder(
            name="complete_workspace",
            workspaces_folder_path=temp_workspaces_path,
        )

        assert loaded.name == original.name
        assert loaded.path == original.path
        assert loaded.subfolders.keys() == original.subfolders.keys()
        assert loaded.config_file == original.config_file

    def test_read_workspace_with_default_path(
        self, monkeypatch, tmp_path: Path, sample_workspace_name: str
    ):
        """Test reading workspace with default path from get_project_root."""
        import wa.folder.read
        import wa.models

        # Mock get_project_root in both modules where it's used
        monkeypatch.setattr("wa.folder.read.get_project_root", lambda: tmp_path)
        monkeypatch.setattr("wa.models.get_project_root", lambda: tmp_path)

        # Create workspace at default location
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name=sample_workspace_name,
            workspaces_folder_path=workspaces_path,
        )
        workspace.save()

        # Read without specifying path (should use default)
        loaded = read_workspace_folder(name=sample_workspace_name)

        assert loaded.name == sample_workspace_name
        assert loaded.path == workspaces_path / sample_workspace_name

    def test_read_workspace_empty_subfolders(self, temp_workspaces_path: Path):
        """Test reading a workspace with empty subfolders dict."""
        workspace = Workspace(
            name="test_empty",
            workspaces_folder_path=temp_workspaces_path,
            subfolders={},
        )
        workspace.save()

        loaded = read_workspace_folder(
            name="test_empty",
            workspaces_folder_path=temp_workspaces_path,
        )

        assert loaded.subfolders == {}

    def test_read_workspace_config_file_field(self, temp_workspaces_path: Path):
        """Test that config_file field is properly loaded."""
        workspace = Workspace(
            name="test_config",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace.save()

        loaded = read_workspace_folder(
            name="test_config",
            workspaces_folder_path=temp_workspaces_path,
        )

        assert loaded.config_file == "workspace.json"

    def test_read_workspace_paths_are_path_objects(
        self, sample_workspace: Workspace, temp_workspaces_path: Path
    ):
        """Test that all path fields are proper Path objects after loading."""
        loaded = read_workspace_folder(
            name=sample_workspace.name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert isinstance(loaded.path, Path)
        assert isinstance(loaded.workspaces_folder_path, Path)
