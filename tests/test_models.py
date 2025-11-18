from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from wa import __version__
from wa.models import Workspace, WorkspaceFolder, WorkspaceModel


class TestWorkspaceModel:
    """Test the base WorkspaceModel class."""

    def test_name_sanitization(self):
        """Test that names are sanitized properly."""
        model = WorkspaceModel(name="My Test Workspace")
        assert model.name == "My_Test_Workspace"

    def test_name_removes_invalid_characters(self):
        """Test that invalid characters are removed from names."""
        model = WorkspaceModel(name='invalid<>:"/\\|?*chars')
        assert model.name == "invalidchars"

    def test_name_truncates_long_names(self):
        """Test that names longer than 255 characters are truncated."""
        long_name = "a" * 300
        model = WorkspaceModel(name=long_name)
        assert len(model.name) == 255

    def test_folders_dict_format(self):
        """Test that folders can be provided as a dict."""
        folders = {
            "folder1": WorkspaceFolder(name="folder1"),
            "folder2": WorkspaceFolder(name="folder2"),
        }
        model = WorkspaceModel(name="test", folders=folders)
        assert len(model.folders) == 2
        assert "folder1" in model.folders
        assert "folder2" in model.folders

    def test_folders_list_of_workspace_folder_objects(self):
        """Test that folders can be provided as a list of WorkspaceFolder objects."""
        folders = [
            WorkspaceFolder(name="folder1"),
            WorkspaceFolder(name="folder2"),
        ]
        model = WorkspaceModel(name="test", folders=folders)
        assert len(model.folders) == 2
        assert "folder1" in model.folders
        assert "folder2" in model.folders
        assert isinstance(model.folders["folder1"], WorkspaceFolder)

    def test_folders_list_of_dicts(self):
        """Test that folders can be provided as a list of dicts."""
        folders = [
            {"name": "folder1"},
            {"name": "folder2"},
        ]
        model = WorkspaceModel(name="test", folders=folders)
        assert len(model.folders) == 2
        assert "folder1" in model.folders
        assert "folder2" in model.folders

    def test_folders_list_of_strings(self):
        """Test that folders can be provided as a list of strings."""
        folders = ["folder1", "folder2"]
        model = WorkspaceModel(name="test", folders=folders)
        assert len(model.folders) == 2
        assert "folder1" in model.folders
        assert "folder2" in model.folders
        assert isinstance(model.folders["folder1"], WorkspaceFolder)

    def test_folders_empty_by_default(self):
        """Test that folders default to an empty dict."""
        model = WorkspaceModel(name="test")
        assert model.folders == {}

    def test_folders_invalid_format_returns_empty(self):
        """Test that invalid folder formats return an empty dict."""
        model = WorkspaceModel(name="test", folders="invalid")
        assert model.folders == {}


class TestWorkspaceFolder:
    """Test the WorkspaceFolder class."""

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


class TestWorkspace:
    """Test the Workspace class."""

    def test_default_version(self):
        """Test that workspace has the correct default version."""
        workspace = Workspace(name="test")
        assert workspace.version == __version__

    def test_path_population(self, tmp_path):
        """Test that workspace path is populated automatically."""
        workspace = Workspace(
            name="test_workspace", workspaces_path=tmp_path / "workspaces"
        )
        assert workspace.workspaces_path == tmp_path / "workspaces"
        assert workspace.path == tmp_path / "workspaces" / "test_workspace"

    def test_custom_workspaces_path(self, tmp_path):
        """Test that custom workspaces_path is respected."""
        custom_path = tmp_path / "custom"
        workspace = Workspace(name="test", workspaces_path=custom_path)
        assert workspace.workspaces_path == custom_path
        assert workspace.path == custom_path / "test"

    def test_custom_path(self, tmp_path):
        """Test that custom path is respected."""
        custom_path = tmp_path / "my_workspace"
        workspace = Workspace(name="test", path=custom_path)
        assert workspace.path == custom_path

    def test_save_creates_json_file(self, tmp_path):
        """Test that save creates a JSON configuration file."""
        workspace = Workspace(
            name="test",
            path=tmp_path / "test",
            workspaces_path=tmp_path,
        )
        config_path = workspace.save()
        assert config_path.exists()
        assert config_path.name == "workspace.json"
        assert config_path.parent == workspace.path

    def test_save_content_is_valid_json(self, tmp_path):
        """Test that saved file contains valid JSON."""
        workspace = Workspace(
            name="test",
            path=tmp_path / "test",
            workspaces_path=tmp_path,
        )
        config_path = workspace.save()
        data = json.loads(config_path.read_text())
        assert data["name"] == "test"
        assert data["version"] == __version__

    def test_save_custom_path(self, tmp_path):
        """Test that save can use a custom path."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        custom_path = tmp_path / "custom" / "config.json"
        saved_path = workspace.save(path=custom_path)
        assert saved_path == custom_path
        assert custom_path.exists()

    def test_load_workspace(self, tmp_path):
        """Test that workspace can be loaded from file."""
        workspace = Workspace(
            name="test",
            path=tmp_path / "test",
            workspaces_path=tmp_path,
        )
        config_path = workspace.save()
        loaded = Workspace.load(config_path)
        assert loaded.name == "test"
        assert loaded.version == __version__
        assert loaded.path == Path(tmp_path / "test")

    def test_load_nonexistent_file_raises_error(self, tmp_path):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Workspace file not found"):
            Workspace.load(tmp_path / "nonexistent.json")

    def test_initialize_folder_creates_folder(self, tmp_path):
        """Test that initialize_folder creates the folder."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        folder = WorkspaceFolder(name="new_folder")
        result = workspace.initialize_folder(folder)
        assert (tmp_path / "test" / "new_folder").exists()
        assert "new_folder" in workspace.folders

    def test_initialize_folder_returns_deepest_folder(self, tmp_path):
        """Test that initialize_folder returns the deepest nested folder."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        folder = WorkspaceFolder(
            name="parent",
            folders=[
                WorkspaceFolder(
                    name="child",
                    folders=[WorkspaceFolder(name="grandchild")],
                )
            ],
        )
        result = workspace.initialize_folder(folder)
        assert result.name == "grandchild"
        assert result.path == tmp_path / "test" / "parent" / "child" / "grandchild"

    def test_initialize_folder_merges_existing_folder(self, tmp_path):
        """Test that initialize_folder merges into existing folders."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        # Create first folder with child1
        folder1 = WorkspaceFolder(
            name="parent",
            folders=[WorkspaceFolder(name="child1")],
        )
        workspace.initialize_folder(folder1)

        # Create second folder with child2 under same parent
        folder2 = WorkspaceFolder(
            name="parent",
            folders=[WorkspaceFolder(name="child2")],
        )
        workspace.initialize_folder(folder2)

        # Both children should exist
        assert (tmp_path / "test" / "parent" / "child1").exists()
        assert (tmp_path / "test" / "parent" / "child2").exists()
        assert len(workspace.folders["parent"].folders) == 2

    def test_initialize_folder_saves_config(self, tmp_path):
        """Test that initialize_folder saves the workspace configuration."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        folder = WorkspaceFolder(name="new_folder")
        workspace.initialize_folder(folder)
        config_path = tmp_path / "test" / "workspace.json"
        assert config_path.exists()

    def test_workspace_with_folders_save_and_load(self, tmp_path):
        """Test that workspace with folders can be saved and loaded."""
        workspace = Workspace(
            name="test",
            path=tmp_path / "test",
            workspaces_path=tmp_path,
            folders=[
                WorkspaceFolder(
                    name="folder1",
                    folders=[WorkspaceFolder(name="subfolder1")],
                ),
                WorkspaceFolder(name="folder2"),
            ],
        )
        config_path = workspace.save()
        loaded = Workspace.load(config_path)
        assert len(loaded.folders) == 2
        assert "folder1" in loaded.folders
        assert "folder2" in loaded.folders
        assert "subfolder1" in loaded.folders["folder1"].folders

    def test_merge_folders_recursively(self, tmp_path):
        """Test that _merge_folders handles deeply nested structures."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        # Create initial structure: root -> level1 -> level2a
        folder1 = WorkspaceFolder(
            name="root",
            folders=[
                WorkspaceFolder(
                    name="level1",
                    folders=[WorkspaceFolder(name="level2a")],
                )
            ],
        )
        workspace.initialize_folder(folder1)

        # Merge in: root -> level1 -> level2b
        folder2 = WorkspaceFolder(
            name="root",
            folders=[
                WorkspaceFolder(
                    name="level1",
                    folders=[WorkspaceFolder(name="level2b")],
                )
            ],
        )
        workspace.initialize_folder(folder2)

        # Both level2a and level2b should exist
        assert (tmp_path / "test" / "root" / "level1" / "level2a").exists()
        assert (tmp_path / "test" / "root" / "level1" / "level2b").exists()
        assert len(workspace.folders["root"].folders["level1"].folders) == 2
