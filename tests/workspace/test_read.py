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

    def test_read_workspace_with_include_files(self, tmp_path):
        """Test that read_workspace populates files when include_files=True."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="folder1")],
        )
        workspace.save()

        # Initialize folder and create files
        folder_path = workspace.path / "folder1"
        folder_path.mkdir(parents=True, exist_ok=True)
        (folder_path / "file1.txt").write_text("content1")
        (folder_path / "file2.txt").write_text("content2")

        loaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            include_files=True,
        )

        assert "folder1" in loaded.folders
        assert "file1.txt" in loaded.folders["folder1"].files
        assert "file2.txt" in loaded.folders["folder1"].files

    def test_read_workspace_with_include_files_nested(self, tmp_path):
        """Test that read_workspace populates files recursively in nested folders."""
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

        # Create directories and files at each level
        parent_path = workspace.path / "parent"
        child_path = parent_path / "child"
        grandchild_path = child_path / "grandchild"

        parent_path.mkdir(parents=True, exist_ok=True)
        child_path.mkdir(parents=True, exist_ok=True)
        grandchild_path.mkdir(parents=True, exist_ok=True)

        (parent_path / "parent_file.txt").write_text("parent content")
        (child_path / "child_file.txt").write_text("child content")
        (grandchild_path / "grandchild_file.txt").write_text("grandchild content")

        loaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            include_files=True,
        )

        assert "parent_file.txt" in loaded.folders["parent"].files
        assert "child_file.txt" in loaded.folders["parent"].folders["child"].files
        assert (
            "grandchild_file.txt"
            in loaded.folders["parent"].folders["child"].folders["grandchild"].files
        )

    def test_read_workspace_without_include_files_does_not_populate(self, tmp_path):
        """Test that read_workspace does not populate files when include_files=False."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="folder1")],
        )
        workspace.save()

        # Initialize folder and create files
        folder_path = workspace.path / "folder1"
        folder_path.mkdir(parents=True, exist_ok=True)
        (folder_path / "file1.txt").write_text("content1")

        loaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            include_files=False,
        )

        assert "folder1" in loaded.folders
        assert loaded.folders["folder1"].files == []

    def test_read_workspace_include_files_default_is_false(self, tmp_path):
        """Test that include_files defaults to False."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="folder1")],
        )
        workspace.save()

        # Initialize folder and create files
        folder_path = workspace.path / "folder1"
        folder_path.mkdir(parents=True, exist_ok=True)
        (folder_path / "file1.txt").write_text("content1")

        # Call without include_files parameter
        loaded = read_workspace(
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
        )

        assert loaded.folders["folder1"].files == []


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

    def test_read_workspace_folder_with_include_files(self, tmp_path):
        """Test that read_workspace_folder populates files when include_files=True."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[
                WorkspaceFolder(
                    name="parent",
                    folders=[WorkspaceFolder(name="child")],
                ),
            ],
        )
        workspace.save()

        # Create directories and files
        parent_path = workspace.path / "parent"
        child_path = parent_path / "child"
        parent_path.mkdir(parents=True, exist_ok=True)
        child_path.mkdir(parents=True, exist_ok=True)
        (parent_path / "parent_file.txt").write_text("parent content")
        (child_path / "child_file.txt").write_text("child content")

        folder = read_workspace_folder(
            workspace_folder_name="parent",
            workspace_name="test_workspace",
            workspaces_path=workspaces_path,
            include_files=True,
        )

        assert "parent_file.txt" in folder.files
        assert "child_file.txt" in folder.folders["child"].files

    def test_read_workspace_folder_list_nonexistent_first_folder(self, tmp_path):
        """Test that read_workspace_folder raises error when first folder in list doesn't exist."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
            folders=[WorkspaceFolder(name="existing")],
        )
        workspace.save()

        with pytest.raises(
            FileNotFoundError, match="Workspace subfolder `nonexistent` not found"
        ):
            read_workspace_folder(
                workspace_folder_name=["nonexistent", "child"],
                workspace_name="test_workspace",
                workspaces_path=workspaces_path,
            )


class TestReadWorkspaceErrors:
    """Test error conditions in read functions."""

    def test_read_workspace_missing_config_file(self, tmp_path):
        """Test that read_workspace raises error when workspace.json is missing."""
        workspaces_path = tmp_path / "workspaces"
        workspace_path = workspaces_path / "test_workspace"
        workspace_path.mkdir(parents=True, exist_ok=True)
        # Don't create workspace.json file

        with pytest.raises(
            FileNotFoundError, match="Config file.*workspace.json.*does not exist"
        ):
            read_workspace(
                workspace_name="test_workspace",
                workspaces_path=workspaces_path,
            )
