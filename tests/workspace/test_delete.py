from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from wa.models import Workspace, WorkspaceFolder
from wa.workspace.delete import delete_workspace


class TestDeleteWorkspace:
    """Test the delete_workspace function."""

    def test_delete_workspace_basic(self, tmp_path):
        """Test that delete_workspace removes a workspace directory."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        assert workspace.path.exists()

        deleted_path = delete_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert deleted_path == workspace.path
        assert not workspace.path.exists()

    def test_delete_workspace_with_folders_requires_force(self, tmp_path):
        """Test that deleting workspace with folders requires force flag."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="folder1")],
        )
        workspace.save()

        with pytest.raises(FileExistsError, match="Workspace currently has folders"):
            delete_workspace(
                workspace_name="test_workspace",
                workspaces_path=workspaces_path,
                force=False,
            )

        # Workspace should still exist
        assert workspace.path.exists()

    def test_delete_workspace_with_folders_and_force(self, tmp_path):
        """Test that delete_workspace with force removes workspace with folders."""
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

        deleted_path = delete_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            force=True,
        )

        assert not workspace.path.exists()
        assert deleted_path == workspace.path

    def test_delete_workspace_removes_all_contents(self, tmp_path):
        """Test that delete_workspace removes all workspace contents."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        # Create some files in the workspace
        (workspace.path / "file1.txt").write_text("content1")
        (workspace.path / "file2.txt").write_text("content2")
        subdir = workspace.path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")

        delete_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert not workspace.path.exists()
        assert not (workspace.path / "file1.txt").exists()
        assert not (workspace.path / "file2.txt").exists()
        assert not subdir.exists()

    def test_delete_workspace_nonexistent_workspace_raises_error(self, tmp_path):
        """Test that deleting nonexistent workspace raises error."""
        workspaces_path = tmp_path / "workspaces"
        workspaces_path.mkdir(parents=True)

        with pytest.raises(FileNotFoundError):
            delete_workspace(
                workspace_name="nonexistent",
                workspaces_path=workspaces_path,
            )

    def test_delete_workspace_with_default_path(self, tmp_path):
        """Test that delete_workspace uses default path when not specified."""
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=tmp_path / "workspaces",
        )
        workspace.save()

        with patch("wa.workspace.read.get_project_root", return_value=tmp_path):
            delete_workspace(workspace_name="test_workspace")

        assert not workspace.path.exists()

    def test_delete_workspace_returns_deleted_path(self, tmp_path):
        """Test that delete_workspace returns the path of deleted workspace."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        result = delete_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert isinstance(result, Path)
        assert result == workspaces_path / "test_workspace"

    def test_delete_workspace_with_nested_folders(self, tmp_path):
        """Test that delete_workspace handles nested folder structures."""
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

        # Initialize the folders
        parent_folder = workspace.folders["parent"]
        parent_folder.path = workspace.path / "parent"
        parent_folder.initialize(force=True)

        # Verify nested structure exists
        assert (workspace.path / "parent" / "child" / "grandchild").exists()

        delete_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            force=True,
        )

        assert not workspace.path.exists()

    def test_delete_workspace_empty_workspace(self, tmp_path):
        """Test that delete_workspace works on empty workspace without folders."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="empty_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        # Should not require force for empty workspace
        delete_workspace(
            workspace_name="empty_workspace",
            workspaces_path=workspaces_path,
            force=False,
        )

        assert not workspace.path.exists()

    def test_delete_workspace_with_one_folder_requires_force(self, tmp_path):
        """Test that workspace with single folder requires force."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="single_folder")],
        )
        workspace.save()

        with pytest.raises(FileExistsError):
            delete_workspace(
                workspace_name="test_workspace",
                workspaces_path=workspaces_path,
                force=False,
            )

    def test_delete_workspace_force_default_is_false(self, tmp_path):
        """Test that force parameter defaults to False."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="folder")],
        )
        workspace.save()

        # Should raise error without explicitly setting force=False
        with pytest.raises(FileExistsError):
            delete_workspace(
                workspace_name="test_workspace",
                workspaces_path=workspaces_path,
            )

    def test_delete_workspace_multiple_sequential_deletes(self, tmp_path):
        """Test that multiple workspaces can be deleted sequentially."""
        workspaces_path = tmp_path / "workspaces"

        # Create multiple workspaces
        for i in range(3):
            workspace = Workspace(
                name=f"workspace{i}",
                workspaces_path=workspaces_path,
            )
            workspace.save()

        # Delete them all
        for i in range(3):
            delete_workspace(
                workspace_name=f"workspace{i}",
                workspaces_path=workspaces_path,
            )

        # Verify all are deleted
        for i in range(3):
            assert not (workspaces_path / f"workspace{i}").exists()

    def test_delete_workspace_preserves_other_workspaces(self, tmp_path):
        """Test that deleting one workspace doesn't affect others."""
        workspaces_path = tmp_path / "workspaces"

        # Create two workspaces
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

        # Delete only workspace1
        delete_workspace(
            workspace_name="workspace1",
            workspaces_path=workspaces_path,
        )

        # workspace1 should be deleted, workspace2 should still exist
        assert not workspace1.path.exists()
        assert workspace2.path.exists()

    def test_delete_workspace_with_symlinks(self, tmp_path):
        """Test that delete_workspace handles symlinks in workspace."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        # Create a file and symlink to it
        target_file = tmp_path / "target.txt"
        target_file.write_text("target content")
        symlink = workspace.path / "link.txt"
        symlink.symlink_to(target_file)

        delete_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        # Workspace and symlink should be deleted
        assert not workspace.path.exists()
        assert not symlink.exists()
        # Target file should still exist
        assert target_file.exists()
