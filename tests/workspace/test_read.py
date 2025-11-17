from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from wa.models import Workspace, WorkspaceFolder
from wa.workspace.read import read_workspace, read_workspace_folder


class TestReadWorkspace:
    """Test the read_workspace function."""

    def test_read_workspace_basic(self, tmp_path):
        """Test that read_workspace loads a workspace correctly."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        loaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert loaded.name == "test_workspace"
        assert loaded.path == workspace.path

    def test_read_workspace_with_default_path(self, tmp_path):
        """Test that read_workspace uses default path when not specified."""
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=tmp_path / "workspaces",
        )
        workspace.save()

        with patch("wa.workspace.read.get_project_root", return_value=tmp_path):
            loaded = read_workspace(workspace_name="test_workspace")
            assert loaded.name == "test_workspace"

    def test_read_workspace_nonexistent_workspaces_folder(self, tmp_path):
        """Test that read_workspace raises error when workspaces folder doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Workspaces folder does not exist"):
            read_workspace(
                workspace_name="test",
                workspaces_path=tmp_path / "nonexistent",
            )

    def test_read_workspace_nonexistent_workspace(self, tmp_path):
        """Test that read_workspace raises error when workspace doesn't exist."""
        workspaces_path = tmp_path / "workspaces"
        workspaces_path.mkdir(parents=True)

        with pytest.raises(
            FileNotFoundError, match="Workspace folder: `nonexistent` does not exist"
        ):
            read_workspace(
                workspace_name="nonexistent",
                workspaces_path=workspaces_path,
            )

    def test_read_workspace_with_folders(self, tmp_path):
        """Test that read_workspace loads workspace with folders correctly."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[
                WorkspaceFolder(name="folder1"),
                WorkspaceFolder(name="folder2"),
            ],
        )
        workspace.save()

        loaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert len(loaded.folders) == 2
        assert "folder1" in loaded.folders
        assert "folder2" in loaded.folders

    def test_read_workspace_with_nested_folders(self, tmp_path):
        """Test that read_workspace loads workspace with nested folders correctly."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[
                WorkspaceFolder(
                    name="parent",
                    folders=[
                        WorkspaceFolder(name="child1"),
                        WorkspaceFolder(name="child2"),
                    ],
                ),
            ],
        )
        workspace.save()

        loaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert "parent" in loaded.folders
        assert "child1" in loaded.folders["parent"].folders
        assert "child2" in loaded.folders["parent"].folders

    def test_read_workspace_preserves_version(self, tmp_path):
        """Test that read_workspace preserves the version from saved workspace."""
        from wa import __version__

        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        loaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert loaded.version == __version__


class TestReadWorkspaceFolder:
    """Test the read_workspace_folder function."""

    def test_read_workspace_folder_string_name(self, tmp_path):
        """Test that read_workspace_folder loads a folder with string name."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="test_folder")],
        )
        workspace.save()

        folder = read_workspace_folder(
            workspace_folder_name="test_folder",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert folder.name == "test_folder"
        assert isinstance(folder, WorkspaceFolder)

    def test_read_workspace_folder_nonexistent_folder(self, tmp_path):
        """Test that read_workspace_folder raises error for nonexistent folder."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        with pytest.raises(
            Exception, match="Workspace subfolder `nonexistent` not found"
        ):
            read_workspace_folder(
                workspace_folder_name="nonexistent",
                workspace_name="test_workspace",
                workspaces_path=workspaces_path,
            )

    def test_read_workspace_folder_list_name(self, tmp_path):
        """Test that read_workspace_folder loads nested folder with list name."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[
                WorkspaceFolder(
                    name="parent",
                    folders=[
                        WorkspaceFolder(
                            name="child",
                            folders=[WorkspaceFolder(name="grandchild")],
                        ),
                    ],
                ),
            ],
        )
        workspace.save()

        folder = read_workspace_folder(
            workspace_folder_name=["parent", "child", "grandchild"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert folder.name == "grandchild"
        assert isinstance(folder, WorkspaceFolder)

    def test_read_workspace_folder_empty_list_raises_error(self, tmp_path):
        """Test that read_workspace_folder raises error for empty list."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        with pytest.raises(Exception, match="No folder names provided"):
            read_workspace_folder(
                workspace_folder_name=[],
                workspace_name="test_workspace",
                workspaces_path=workspaces_path,
            )

    def test_read_workspace_folder_missing_intermediate_folder(self, tmp_path):
        """Test that read_workspace_folder raises error for missing intermediate folder."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[
                WorkspaceFolder(
                    name="parent",
                    folders=[WorkspaceFolder(name="child1")],
                ),
            ],
        )
        workspace.save()

        with pytest.raises(FileNotFoundError, match="missing `child2`"):
            read_workspace_folder(
                workspace_folder_name=["parent", "child2", "grandchild"],
                workspace_name="test_workspace",
                workspaces_path=workspaces_path,
            )

    def test_read_workspace_folder_single_item_list(self, tmp_path):
        """Test that read_workspace_folder handles single-item list."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="single")],
        )
        workspace.save()

        folder = read_workspace_folder(
            workspace_folder_name=["single"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert folder.name == "single"

    def test_read_workspace_folder_two_level_nesting(self, tmp_path):
        """Test that read_workspace_folder handles two-level nesting."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[
                WorkspaceFolder(
                    name="level1",
                    folders=[WorkspaceFolder(name="level2")],
                ),
            ],
        )
        workspace.save()

        folder = read_workspace_folder(
            workspace_folder_name=["level1", "level2"],
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert folder.name == "level2"

    def test_read_workspace_folder_nonexistent_workspace(self, tmp_path):
        """Test that read_workspace_folder raises error for nonexistent workspace."""
        with pytest.raises(FileNotFoundError):
            read_workspace_folder(
                workspace_folder_name="folder",
                workspace_name="nonexistent",
                workspaces_path=tmp_path / "workspaces",
            )

    def test_read_workspace_folder_with_default_path(self, tmp_path):
        """Test that read_workspace_folder uses default path when not specified."""
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=tmp_path / "workspaces",
            folders=[WorkspaceFolder(name="test_folder")],
        )
        workspace.save()

        with patch("wa.workspace.read.get_project_root", return_value=tmp_path):
            folder = read_workspace_folder(
                workspace_folder_name="test_folder",
                workspace_name="test_workspace",
            )

            assert folder.name == "test_folder"

    def test_read_workspace_folder_preserves_folder_structure(self, tmp_path):
        """Test that read_workspace_folder preserves folder structure."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[
                WorkspaceFolder(
                    name="parent",
                    folders=[
                        WorkspaceFolder(name="child1"),
                        WorkspaceFolder(name="child2"),
                    ],
                ),
            ],
        )
        workspace.save()

        parent = read_workspace_folder(
            workspace_folder_name="parent",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert len(parent.folders) == 2
        assert "child1" in parent.folders
        assert "child2" in parent.folders
