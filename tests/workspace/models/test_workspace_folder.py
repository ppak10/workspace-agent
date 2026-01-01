from __future__ import annotations

from pathlib import Path

import pytest

from wa.workspace.models.workspace_folder import WorkspaceFolder


class TestWorkspaceFolder:
    """Test the WorkspaceFolder class."""

    def test_basic_initialization(self):
        """Test that WorkspaceFolder can be initialized with basic parameters."""
        folder = WorkspaceFolder(name="test_folder")
        assert folder.name == "test_folder"
        assert folder.path == Path("")
        assert folder.folders == {}
        assert folder.files == []

    def test_inherits_from_workspace_base_model(self):
        """Test that WorkspaceFolder inherits WorkspaceBaseModel behavior."""
        folder = WorkspaceFolder(name="Test Folder")
        # Should sanitize name
        assert folder.name == "Test_Folder"

    def test_initialize_creates_directory(self, tmp_path):
        """Test that initialize creates the folder directory."""
        folder = WorkspaceFolder(name="test_folder", path=tmp_path / "test_folder")
        folder.initialize()
        assert folder.path.exists()
        assert folder.path.is_dir()

    def test_initialize_with_nested_folders(self, tmp_path):
        """Test that initialize creates nested folder structures."""
        folder = WorkspaceFolder(
            name="parent",
            path=tmp_path / "parent",
            folders=[
                WorkspaceFolder(name="child1"),
                WorkspaceFolder(name="child2"),
            ],
        )
        folder.initialize()
        assert folder.path.exists()
        assert (folder.path / "child1").exists()
        assert (folder.path / "child2").exists()

    def test_initialize_deeply_nested_folders(self, tmp_path):
        """Test that initialize creates deeply nested folder structures."""
        folder = WorkspaceFolder(
            name="root",
            path=tmp_path / "root",
            folders=[
                WorkspaceFolder(
                    name="level1",
                    folders=[
                        WorkspaceFolder(
                            name="level2",
                            folders=[WorkspaceFolder(name="level3")],
                        )
                    ],
                )
            ],
        )
        folder.initialize()
        assert (tmp_path / "root" / "level1" / "level2" / "level3").exists()

    def test_initialize_with_force_on_existing_directory(self, tmp_path):
        """Test that initialize with force=True works on existing directories."""
        folder_path = tmp_path / "existing"
        folder_path.mkdir()
        folder = WorkspaceFolder(name="existing", path=folder_path)
        folder.initialize(force=True)
        assert folder_path.exists()

    def test_initialize_without_force_on_existing_directory_raises_error(
        self, tmp_path
    ):
        """Test that initialize without force raises error on existing directories."""
        folder_path = tmp_path / "existing"
        folder_path.mkdir()
        folder = WorkspaceFolder(name="existing", path=folder_path)
        with pytest.raises(FileExistsError):
            folder.initialize(force=False)

    def test_initialize_sets_nested_folder_paths(self, tmp_path):
        """Test that initialize sets correct paths for nested folders."""
        child1 = WorkspaceFolder(name="child1")
        child2 = WorkspaceFolder(name="child2")
        parent = WorkspaceFolder(
            name="parent",
            path=tmp_path / "parent",
            folders={"child1": child1, "child2": child2},
        )
        parent.initialize()

        assert child1.path == tmp_path / "parent" / "child1"
        assert child2.path == tmp_path / "parent" / "child2"

    def test_initialize_with_empty_folders(self, tmp_path):
        """Test that initialize works with no nested folders."""
        folder = WorkspaceFolder(name="simple", path=tmp_path / "simple")
        folder.initialize()
        assert folder.path.exists()
        assert len(list(folder.path.iterdir())) == 0

    def test_initialize_recursive_path_setting(self, tmp_path):
        """Test that initialize recursively sets paths for all nested levels."""
        deepest = WorkspaceFolder(name="level3")
        middle = WorkspaceFolder(name="level2", folders={"level3": deepest})
        top = WorkspaceFolder(
            name="level1", path=tmp_path / "level1", folders={"level2": middle}
        )

        top.initialize()

        assert top.path == tmp_path / "level1"
        assert middle.path == tmp_path / "level1" / "level2"
        assert deepest.path == tmp_path / "level1" / "level2" / "level3"

    def test_initialize_creates_parent_directories(self, tmp_path):
        """Test that initialize creates all directories in nested structure."""
        folder = WorkspaceFolder(
            name="root",
            path=tmp_path / "root",
            folders=[
                WorkspaceFolder(
                    name="a",
                    folders=[
                        WorkspaceFolder(name="b", folders=[WorkspaceFolder(name="c")])
                    ],
                )
            ],
        )
        folder.initialize()

        full_path = tmp_path / "root" / "a" / "b" / "c"
        assert full_path.exists()
        assert full_path.is_dir()

    def test_initialize_with_files_parameter(self, tmp_path):
        """Test that folders can have files parameter."""
        folder = WorkspaceFolder(
            name="folder_with_files",
            path=tmp_path / "folder_with_files",
            files=["file1.txt", "file2.txt"],
        )
        folder.initialize()

        assert folder.path.exists()
        assert folder.files == ["file1.txt", "file2.txt"]

    def test_initialize_multiple_times_with_force(self, tmp_path):
        """Test that initialize can be called multiple times with force=True."""
        folder = WorkspaceFolder(name="multi_init", path=tmp_path / "multi_init")
        folder.initialize()
        assert folder.path.exists()

        # Should work fine with force=True
        folder.initialize(force=True)
        assert folder.path.exists()

    def test_initialize_preserves_folder_structure(self, tmp_path):
        """Test that initialize doesn't modify the folders dict."""
        child_folders = {
            "child1": WorkspaceFolder(name="child1"),
            "child2": WorkspaceFolder(name="child2"),
        }
        parent = WorkspaceFolder(
            name="parent", path=tmp_path / "parent", folders=child_folders
        )

        parent.initialize()

        # Folders dict should still have the same keys
        assert len(parent.folders) == 2
        assert "child1" in parent.folders
        assert "child2" in parent.folders

    def test_folder_with_complex_nested_structure(self, tmp_path):
        """Test initialization with a complex nested structure."""
        folder = WorkspaceFolder(
            name="root",
            path=tmp_path / "root",
            folders=[
                WorkspaceFolder(
                    name="branch1",
                    folders=[
                        WorkspaceFolder(name="leaf1"),
                        WorkspaceFolder(name="leaf2"),
                    ],
                ),
                WorkspaceFolder(
                    name="branch2",
                    folders=[
                        WorkspaceFolder(
                            name="subbranch",
                            folders=[WorkspaceFolder(name="leaf3")],
                        )
                    ],
                ),
            ],
        )

        folder.initialize()

        assert (tmp_path / "root" / "branch1" / "leaf1").exists()
        assert (tmp_path / "root" / "branch1" / "leaf2").exists()
        assert (tmp_path / "root" / "branch2" / "subbranch" / "leaf3").exists()

    def test_folder_path_is_mutable(self):
        """Test that folder path can be changed after initialization."""
        folder = WorkspaceFolder(name="test")
        assert folder.path == Path("")

        folder.path = Path("/new/path")
        assert folder.path == Path("/new/path")
