from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from wa import __version__
from wa.models import WorkspaceFolder
from wa.workspace.create import create_workspace, create_workspace_folder


class TestCreateWorkspace:
    """Test the create_workspace function."""

    def test_create_workspace_basic(self, tmp_path):
        """Test that create_workspace creates a basic workspace."""
        workspaces_path = tmp_path / "workspaces"
        workspace = create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert workspace.name == "test_workspace"
        assert workspace.path.exists()
        assert workspace.path.is_dir()
        assert (workspace.path / "workspace.json").exists()

    def test_create_workspace_with_default_path(self, tmp_path):
        """Test that create_workspace uses default path when not specified."""
        with patch("wa.workspace.create.get_project_root", return_value=tmp_path):
            workspace = create_workspace(workspace_name="default_workspace")
            assert workspace.workspaces_path == tmp_path / "workspaces"
            assert workspace.path == tmp_path / "workspaces" / "default_workspace"

    def test_create_workspace_creates_workspaces_directory(self, tmp_path):
        """Test that create_workspace creates the workspaces directory if it doesn't exist."""
        workspaces_path = tmp_path / "new_workspaces"
        assert not workspaces_path.exists()

        create_workspace(
            workspace_name="test",
            workspaces_path=workspaces_path,
        )

        assert workspaces_path.exists()
        assert workspaces_path.is_dir()

    def test_create_workspace_with_existing_workspace_raises_error(self, tmp_path):
        """Test that creating a workspace that already exists raises FileExistsError."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="existing",
            workspaces_path=workspaces_path,
        )

        with pytest.raises(FileExistsError, match="Workspace already exists"):
            create_workspace(
                workspace_name="existing",
                workspaces_path=workspaces_path,
                force=False,
            )

    def test_create_workspace_with_force_overwrites_existing(self, tmp_path):
        """Test that create_workspace with force=True overwrites existing workspace."""
        workspaces_path = tmp_path / "workspaces"
        workspace1 = create_workspace(
            workspace_name="overwrite",
            workspaces_path=workspaces_path,
        )

        # Create again with force
        workspace2 = create_workspace(
            workspace_name="overwrite",
            workspaces_path=workspaces_path,
            force=True,
        )

        assert workspace1.path == workspace2.path
        assert workspace2.path.exists()

    def test_create_workspace_has_correct_version(self, tmp_path):
        """Test that created workspace has the correct version."""
        workspace = create_workspace(
            workspace_name="versioned",
            workspaces_path=tmp_path / "workspaces",
        )
        assert workspace.version == __version__

    def test_create_workspace_sanitizes_name(self, tmp_path):
        """Test that workspace name is sanitized."""
        workspace = create_workspace(
            workspace_name="Test Workspace",
            workspaces_path=tmp_path / "workspaces",
        )
        assert workspace.name == "Test_Workspace"

    def test_create_workspace_with_folders(self, tmp_path):
        """Test that create_workspace can be initialized with folders."""
        workspace = create_workspace(
            workspace_name="with_folders",
            workspaces_path=tmp_path / "workspaces",
            folders=[
                WorkspaceFolder(name="folder1"),
                WorkspaceFolder(name="folder2"),
            ],
        )
        assert len(workspace.folders) == 2
        assert "folder1" in workspace.folders
        assert "folder2" in workspace.folders


class TestCreateWorkspaceFolder:
    """Test the create_workspace_folder function."""

    def test_create_workspace_folder_basic(self, tmp_path):
        """Test that create_workspace_folder creates a basic folder."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        folder = create_workspace_folder(
            name_or_path="test_folder",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert folder.name == "test_folder"
        assert folder.path.exists()
        assert folder.path.is_dir()

    def test_create_workspace_folder_string_name(self, tmp_path):
        """Test that create_workspace_folder works with string folder name."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        folder = create_workspace_folder(
            name_or_path="simple_folder",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert folder.name == "simple_folder"
        assert (
            folder.path == tmp_path / "workspaces" / "test_workspace" / "simple_folder"
        )

    def test_create_workspace_folder_nested_list(self, tmp_path):
        """Test that create_workspace_folder creates nested folders from list."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        folder = create_workspace_folder(
            name_or_path=["parent", "child", "grandchild"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        # Should return the deepest folder
        assert folder.name == "grandchild"
        assert (
            folder.path
            == tmp_path
            / "workspaces"
            / "test_workspace"
            / "parent"
            / "child"
            / "grandchild"
        )
        assert folder.path.exists()

    def test_create_workspace_folder_nested_structure_exists(self, tmp_path):
        """Test that nested folder structure is created correctly."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        create_workspace_folder(
            name_or_path=["level1", "level2", "level3"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        base_path = tmp_path / "workspaces" / "test_workspace"
        assert (base_path / "level1").exists()
        assert (base_path / "level1" / "level2").exists()
        assert (base_path / "level1" / "level2" / "level3").exists()

    def test_create_workspace_folder_updates_workspace_config(self, tmp_path):
        """Test that creating a folder updates the workspace config."""
        workspaces_path = tmp_path / "workspaces"
        workspace = create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert len(workspace.folders) == 0

        create_workspace_folder(
            name_or_path="new_folder",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        # Reload workspace and check folder was added
        from wa.workspace.read import read_workspace

        reloaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )
        assert "new_folder" in reloaded.folders

    def test_create_workspace_folder_with_force(self, tmp_path):
        """Test that create_workspace_folder with force overwrites existing folder."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        create_workspace_folder(
            name_or_path="existing_folder",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        # Create again with force
        folder = create_workspace_folder(
            name_or_path="existing_folder",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            force=True,
        )

        assert folder.name == "existing_folder"
        assert folder.path.exists()

    def test_create_workspace_folder_merges_with_existing(self, tmp_path):
        """Test that creating a folder with same parent merges correctly."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        # Create parent with child1
        create_workspace_folder(
            name_or_path=["parent", "child1"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        # Create parent with child2
        create_workspace_folder(
            name_or_path=["parent", "child2"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        # Both children should exist
        base_path = tmp_path / "workspaces" / "test_workspace"
        assert (base_path / "parent" / "child1").exists()
        assert (base_path / "parent" / "child2").exists()

    def test_create_workspace_folder_nonexistent_workspace_creates_workspace(
        self, tmp_path
    ):
        """Test that creating a folder in nonexistent workspace auto-creates the workspace."""
        workspaces_path = tmp_path / "workspaces"
        workspace_path = workspaces_path / "nonexistent"

        # Verify workspace doesn't exist
        assert not workspace_path.exists()

        # Create folder in nonexistent workspace
        folder = create_workspace_folder(
            name_or_path="folder",
            workspace_name="nonexistent",
            workspaces_path=workspaces_path,
        )

        # Verify workspace and folder were created
        assert workspace_path.exists()
        assert (workspace_path / "folder").exists()
        assert folder.name == "folder"
        assert folder.path == workspace_path / "folder"

    def test_create_workspace_folder_single_item_list(self, tmp_path):
        """Test that create_workspace_folder handles single-item list."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        folder = create_workspace_folder(
            name_or_path=["single"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert folder.name == "single"
        assert folder.path.exists()

    def test_create_workspace_folder_with_default_workspaces_path(self, tmp_path):
        """Test that create_workspace_folder uses default path when not specified."""
        with patch("wa.workspace.create.get_project_root", return_value=tmp_path):
            with patch("wa.workspace.read.get_project_root", return_value=tmp_path):
                create_workspace(workspace_name="test_workspace")

                folder = create_workspace_folder(
                    name_or_path="default_folder",
                    workspace_name="test_workspace",
                )

                assert (
                    folder.path
                    == tmp_path / "workspaces" / "test_workspace" / "default_folder"
                )

    def test_create_workspace_folder_with_append_timestamp_string(self, tmp_path):
        """Test that create_workspace_folder appends timestamp to string folder name."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        folder = create_workspace_folder(
            name_or_path="timestamped_folder",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            append_timestamp=True,
        )

        # Verify folder name starts with original name and has timestamp pattern
        assert folder.name.startswith("timestamped_folder_")
        # Check timestamp pattern: _YYYYMMDD_HHMMSS
        assert len(folder.name) == len("timestamped_folder_") + 15
        assert folder.path.exists()

    def test_create_workspace_folder_with_append_timestamp_list(self, tmp_path):
        """Test that create_workspace_folder appends timestamp to last item in list."""
        workspaces_path = tmp_path / "workspaces"
        create_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        folder = create_workspace_folder(
            name_or_path=["parent", "child", "timestamped"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            append_timestamp=True,
        )

        # The last folder should have timestamp, parent and child should not
        assert folder.name.startswith("timestamped_")
        assert len(folder.name) == len("timestamped_") + 15

        # Verify the full path structure
        base_path = tmp_path / "workspaces" / "test_workspace"
        assert (base_path / "parent").exists()
        assert (base_path / "parent" / "child").exists()
        assert folder.path.exists()
        assert "parent" in str(folder.path)
        assert "child" in str(folder.path)
