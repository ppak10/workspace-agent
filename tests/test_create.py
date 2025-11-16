"""Tests for workspace folder creation functionality."""

from pathlib import Path

import pytest

from wa.folder.create import create_workspace_folder
from wa.models import Workspace, WorkspaceSubfolder


class TestCreateWorkspaceFolder:
    """Test cases for create_workspace_folder function."""

    def test_create_basic_workspace(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test creating a basic workspace with default settings."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert workspace.name == sample_workspace_name
        assert workspace.path == temp_workspaces_path / sample_workspace_name
        assert workspace.path.exists()
        assert workspace.path.is_dir()

        # Check that config file was created
        config_path = workspace.path / "workspace.json"
        assert config_path.exists()

    def test_create_workspace_creates_parent_dirs(self, tmp_path: Path):
        """Test that creating workspace creates parent directories if they don't exist."""
        workspaces_path = tmp_path / "nested" / "workspaces"
        assert not workspaces_path.exists()

        workspace = create_workspace_folder(
            name="test",
            workspaces_folder_path=workspaces_path,
        )

        assert workspaces_path.exists()
        assert workspace.path.exists()

    def test_create_workspace_already_exists_raises_error(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that creating a workspace that already exists raises FileExistsError."""
        # Create the workspace first time
        create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Attempt to create it again without force flag
        with pytest.raises(FileExistsError, match="Workspace already exists"):
            create_workspace_folder(
                name=sample_workspace_name,
                workspaces_folder_path=temp_workspaces_path,
            )

    def test_create_workspace_with_force_flag(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that force flag allows overwriting existing workspace."""
        # Create the workspace first time
        workspace1 = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create it again with force flag
        workspace2 = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
            force=True,
        )

        assert workspace1.path == workspace2.path
        assert workspace2.path.exists()

    def test_create_workspace_sanitizes_name(self, temp_workspaces_path: Path):
        """Test that workspace name is properly sanitized."""
        # Name with spaces should be converted to underscores
        workspace = create_workspace_folder(
            name="my test workspace",
            workspaces_folder_path=temp_workspaces_path,
        )

        assert workspace.name == "my_test_workspace"
        assert workspace.path.name == "my_test_workspace"

    def test_create_workspace_removes_invalid_chars(self, temp_workspaces_path: Path):
        """Test that invalid characters are removed from workspace name."""
        # Name with invalid characters should have them removed
        workspace = create_workspace_folder(
            name='test<>:"/\\|?*name',
            workspaces_folder_path=temp_workspaces_path,
        )

        # All invalid characters should be removed
        assert workspace.name == "testname"
        assert workspace.path.name == "testname"

    def test_create_workspace_with_kwargs(self, temp_workspaces_path: Path):
        """Test creating workspace with additional keyword arguments."""
        workspace = create_workspace_folder(
            name="test",
            workspaces_folder_path=temp_workspaces_path,
            subfolders=[
                WorkspaceSubfolder(name="data"),
                WorkspaceSubfolder(name="models"),
            ],
        )

        assert set(workspace.subfolders.keys()) == {"data", "models"}

    def test_create_workspace_config_is_valid_json(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that saved workspace config is valid JSON."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        config_path = workspace.path / "workspace.json"
        loaded_workspace = Workspace.load(config_path)

        assert loaded_workspace.name == workspace.name
        assert loaded_workspace.path == workspace.path

    def test_create_workspace_uses_default_path_when_none(
        self, monkeypatch, tmp_path: Path
    ):
        """Test that workspace uses default path from get_project_root when none provided."""
        import wa.folder.create
        import wa.models

        # Mock get_project_root in both modules where it's used
        monkeypatch.setattr("wa.folder.create.get_project_root", lambda: tmp_path)
        monkeypatch.setattr("wa.models.get_project_root", lambda: tmp_path)

        workspace = create_workspace_folder(name="test")

        expected_path = tmp_path / "workspaces" / "test"
        assert workspace.path == expected_path
        assert workspace.path.exists()

    def test_create_workspace_reasonable_long_name(self, temp_workspaces_path: Path):
        """Test that workspace names up to 100 characters work correctly."""
        long_name = "a" * 100
        workspace = create_workspace_folder(
            name=long_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert workspace.name == long_name
        assert workspace.path.exists()
