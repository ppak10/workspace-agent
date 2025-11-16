"""Tests for workspace folder deletion functionality."""

from pathlib import Path

import pytest

from wa.folder.delete import delete_workspace_folder
from wa.models import Workspace


class TestDeleteWorkspaceFolder:
    """Test cases for delete_workspace_folder function."""

    def test_delete_empty_workspace(
        self, sample_workspace: Workspace, temp_workspaces_path: Path
    ):
        """Test deleting an empty workspace without subfolders."""
        workspace_path = sample_workspace.path
        assert workspace_path.exists()

        result = delete_workspace_folder(
            name=sample_workspace.name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert result == workspace_path
        assert not workspace_path.exists()

    def test_delete_workspace_with_force_flag(self, temp_workspaces_path: Path):
        """Test deleting workspace with subfolders using force flag."""
        # Create workspace with subfolders
        workspace = Workspace(
            name="workspace_with_subs",
            workspaces_folder_path=temp_workspaces_path,
            subfolders=["data", "models"],
        )
        workspace.save()

        assert workspace.path.exists()

        # Delete with force flag
        result = delete_workspace_folder(
            name="workspace_with_subs",
            workspaces_folder_path=temp_workspaces_path,
            force=True,
        )

        assert result == workspace.path
        assert not workspace.path.exists()

    def test_delete_workspace_with_subfolders_without_force_raises_error(
        self, temp_workspaces_path: Path
    ):
        """Test that deleting workspace with subfolders without force raises error."""
        # Create workspace with subfolders
        workspace = Workspace(
            name="workspace_with_subs",
            workspaces_folder_path=temp_workspaces_path,
            subfolders=["data", "models"],
        )
        workspace.save()

        # Attempt to delete without force flag
        with pytest.raises(
            FileExistsError,
            match="Workspace currently has subfolders, use --force to delete",
        ):
            delete_workspace_folder(
                name="workspace_with_subs",
                workspaces_folder_path=temp_workspaces_path,
                force=False,
            )

        # Workspace should still exist
        assert workspace.path.exists()

    def test_delete_nonexistent_workspace_raises_error(
        self, temp_workspaces_path: Path
    ):
        """Test that deleting a non-existent workspace raises FileNotFoundError."""
        with pytest.raises(
            FileNotFoundError, match="Workspace folder: `nonexistent` does not exist"
        ):
            delete_workspace_folder(
                name="nonexistent",
                workspaces_folder_path=temp_workspaces_path,
            )

    def test_delete_workspace_removes_all_contents(self, temp_workspaces_path: Path):
        """Test that deleting workspace removes all files and subdirectories."""
        # Create workspace
        workspace = Workspace(
            name="test_workspace",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace.save()

        # Add some files and directories
        (workspace.path / "file1.txt").write_text("content1")
        (workspace.path / "file2.txt").write_text("content2")
        subdir = workspace.path / "subdir"
        subdir.mkdir()
        (subdir / "nested_file.txt").write_text("nested content")

        assert workspace.path.exists()
        assert (workspace.path / "file1.txt").exists()
        assert subdir.exists()

        # Delete workspace
        delete_workspace_folder(
            name="test_workspace",
            workspaces_folder_path=temp_workspaces_path,
        )

        # Everything should be gone
        assert not workspace.path.exists()
        assert not (workspace.path / "file1.txt").exists()
        assert not subdir.exists()

    def test_delete_workspace_returns_correct_path(
        self, sample_workspace: Workspace, temp_workspaces_path: Path
    ):
        """Test that delete function returns the path that was deleted."""
        expected_path = sample_workspace.path

        result = delete_workspace_folder(
            name=sample_workspace.name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert isinstance(result, Path)
        assert result == expected_path

    def test_delete_workspace_with_default_path(
        self, monkeypatch, tmp_path: Path, sample_workspace_name: str
    ):
        """Test deleting workspace with default path from get_project_root."""
        import wa.folder.read
        import wa.models

        # Mock get_project_root in modules where it's used
        # delete.py doesn't import it, it calls read_workspace_folder which does
        monkeypatch.setattr("wa.folder.read.get_project_root", lambda: tmp_path)
        monkeypatch.setattr("wa.models.get_project_root", lambda: tmp_path)

        # Create workspace at default location
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name=sample_workspace_name,
            workspaces_folder_path=workspaces_path,
        )
        workspace.save()

        assert workspace.path.exists()

        # Delete without specifying path (should use default)
        delete_workspace_folder(name=sample_workspace_name)

        assert not workspace.path.exists()

    def test_delete_workspace_with_empty_subfolders_list(
        self, temp_workspaces_path: Path
    ):
        """Test deleting workspace with empty subfolders list doesn't require force."""
        workspace = Workspace(
            name="empty_subs",
            workspaces_folder_path=temp_workspaces_path,
            subfolders=[],
        )
        workspace.save()

        # Should work without force flag since subfolders list is empty
        result = delete_workspace_folder(
            name="empty_subs",
            workspaces_folder_path=temp_workspaces_path,
            force=False,
        )

        assert not workspace.path.exists()

    def test_delete_workspace_removes_config_file(
        self, sample_workspace: Workspace, temp_workspaces_path: Path
    ):
        """Test that deleting workspace removes the config file."""
        config_path = sample_workspace.path / "workspace.json"
        assert config_path.exists()

        delete_workspace_folder(
            name=sample_workspace.name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert not config_path.exists()

    def test_delete_preserves_other_workspaces(self, temp_workspaces_path: Path):
        """Test that deleting one workspace doesn't affect others."""
        # Create two workspaces
        workspace1 = Workspace(
            name="workspace1",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace1.save()

        workspace2 = Workspace(
            name="workspace2",
            workspaces_folder_path=temp_workspaces_path,
        )
        workspace2.save()

        # Delete first workspace
        delete_workspace_folder(
            name="workspace1",
            workspaces_folder_path=temp_workspaces_path,
        )

        # First workspace should be gone
        assert not workspace1.path.exists()

        # Second workspace should still exist
        assert workspace2.path.exists()
        assert (workspace2.path / "workspace.json").exists()
