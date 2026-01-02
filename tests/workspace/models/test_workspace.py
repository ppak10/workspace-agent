from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from wa import __version__
from wa.workspace.models.workspace import Workspace
from wa.workspace.models.workspace_folder import WorkspaceFolder


class TestWorkspace:
    """Test the Workspace class."""

    def test_basic_initialization(self):
        """Test that Workspace can be initialized with basic parameters."""
        workspace = Workspace(name="test_workspace")
        assert workspace.name == "test_workspace"
        assert workspace.version == __version__
        assert workspace.folders == {}
        assert workspace.files == []

    def test_default_version(self):
        """Test that workspace has the correct default version."""
        workspace = Workspace(name="test")
        assert workspace.version == __version__

    def test_custom_version(self):
        """Test that custom version can be set."""
        workspace = Workspace(name="test", version="1.0.0")
        assert workspace.version == "1.0.0"

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

    def test_custom_config_file(self):
        """Test that custom config_file can be set."""
        workspace = Workspace(name="test", config_file="custom.json")
        assert workspace.config_file == "custom.json"

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

    def test_save_creates_parent_directories(self, tmp_path):
        """Test that save creates parent directories if they don't exist."""
        workspace = Workspace(name="test", path=tmp_path / "deep" / "nested" / "test")
        config_path = workspace.save()
        assert config_path.exists()
        assert config_path.parent.exists()

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

    def test_load_preserves_folders(self, tmp_path):
        """Test that loading workspace preserves folder structure."""
        workspace = Workspace(
            name="test",
            path=tmp_path / "test",
            workspaces_path=tmp_path,
            folders=[
                WorkspaceFolder(name="folder1"),
                WorkspaceFolder(name="folder2"),
            ],
        )
        config_path = workspace.save()
        loaded = Workspace.load(config_path)
        assert len(loaded.folders) == 2
        assert "folder1" in loaded.folders
        assert "folder2" in loaded.folders

    def test_create_folder_string_name(self, tmp_path):
        """Test that create_folder creates a folder with string name."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        result = workspace.create_folder(name_or_path="new_folder")
        assert (tmp_path / "test" / "new_folder").exists()
        assert "new_folder" in workspace.folders
        assert result.name == "new_folder"

    def test_create_folder_path_name(self, tmp_path):
        """Test that create_folder works with Path object."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        result = workspace.create_folder(name_or_path=Path("path_folder"))

        # The name is sanitized (slashes removed) from the full path
        from wa.utils import create_pathname

        expected_name = create_pathname(str(tmp_path / "test" / "path_folder"))

        assert result.name == expected_name
        assert result.path.exists()
        assert expected_name in workspace.folders

    def test_create_folder_list_name(self, tmp_path):
        """Test that create_folder creates nested folders from list."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        result = workspace.create_folder(name_or_path=["parent", "child", "grandchild"])
        assert result.name == "grandchild"
        assert result.path == tmp_path / "test" / "parent" / "child" / "grandchild"
        assert (tmp_path / "test" / "parent" / "child" / "grandchild").exists()

    def test_create_folder_returns_deepest_folder(self, tmp_path):
        """Test that create_folder returns the deepest nested folder."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        result = workspace.create_folder(name_or_path=["a", "b", "c"])
        assert result.name == "c"
        assert "a" in workspace.folders

    def test_create_folder_merges_existing_folder(self, tmp_path):
        """Test that create_folder merges into existing folders."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        workspace.create_folder(name_or_path=["parent", "child1"])
        workspace.create_folder(name_or_path=["parent", "child2"])

        assert (tmp_path / "test" / "parent" / "child1").exists()
        assert (tmp_path / "test" / "parent" / "child2").exists()
        assert len(workspace.folders["parent"].folders) == 2

    def test_create_folder_saves_config(self, tmp_path):
        """Test that create_folder saves the workspace configuration."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)
        workspace.create_folder(name_or_path="new_folder")
        config_path = tmp_path / "test" / "workspace.json"
        assert config_path.exists()

    def test_create_folder_with_force(self, tmp_path):
        """Test that create_folder with force overwrites existing folder."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        workspace.create_folder(name_or_path="existing")
        result = workspace.create_folder(name_or_path="existing", force=True)

        assert result.name == "existing"
        assert (tmp_path / "test" / "existing").exists()

    def test_create_folder_with_append_timestamp_string(self, tmp_path):
        """Test that create_folder appends timestamp to string name."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        result = workspace.create_folder(
            name_or_path="timestamped", append_timestamp=True
        )

        assert result.name.startswith("timestamped_")
        assert len(result.name) == len("timestamped_") + 15
        assert result.path.exists()

    def test_create_folder_with_append_timestamp_list(self, tmp_path):
        """Test that create_folder appends timestamp to last item in list."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        result = workspace.create_folder(
            name_or_path=["parent", "timestamped"], append_timestamp=True
        )

        assert result.name.startswith("timestamped_")
        assert (workspace.path / "parent").exists()

    def test_create_folder_single_item_list(self, tmp_path):
        """Test that create_folder handles single-item list."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        result = workspace.create_folder(name_or_path=["single"])

        assert result.name == "single"
        assert result.path.exists()

    def test_create_folder_with_kwargs(self, tmp_path):
        """Test that create_folder passes kwargs to WorkspaceFolder."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        result = workspace.create_folder(
            name_or_path="folder_with_files", files=["file1.txt", "file2.txt"]
        )

        assert result.files == ["file1.txt", "file2.txt"]

    def test_get_deepest_folder_simple(self, tmp_path):
        """Test _get_deepest_folder with a simple folder."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        folder = WorkspaceFolder(name="simple")
        result = workspace._get_deepest_folder(folder)
        assert result.name == "simple"

    def test_get_deepest_folder_nested(self, tmp_path):
        """Test _get_deepest_folder with nested folders."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        deepest = WorkspaceFolder(name="deepest")
        middle = WorkspaceFolder(name="middle", folders={"deepest": deepest})
        top = WorkspaceFolder(name="top", folders={"middle": middle})

        result = workspace._get_deepest_folder(top)
        assert result.name == "deepest"

    def test_merge_folders_basic(self, tmp_path):
        """Test _merge_folders merges new folders into existing."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        existing = WorkspaceFolder(
            name="parent",
            path=tmp_path / "test" / "parent",
            folders={"child1": WorkspaceFolder(name="child1")},
        )
        existing.initialize()

        new = WorkspaceFolder(
            name="parent", folders={"child2": WorkspaceFolder(name="child2")}
        )

        workspace._merge_folders(existing, new)

        assert len(existing.folders) == 2
        assert "child1" in existing.folders
        assert "child2" in existing.folders

    def test_merge_folders_recursive(self, tmp_path):
        """Test _merge_folders handles deeply nested structures."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        existing = WorkspaceFolder(
            name="root",
            path=tmp_path / "test" / "root",
            folders={
                "level1": WorkspaceFolder(
                    name="level1",
                    folders={"level2a": WorkspaceFolder(name="level2a")},
                )
            },
        )
        existing.initialize()

        new = WorkspaceFolder(
            name="root",
            folders={
                "level1": WorkspaceFolder(
                    name="level1",
                    folders={"level2b": WorkspaceFolder(name="level2b")},
                )
            },
        )

        workspace._merge_folders(existing, new)

        assert len(existing.folders["level1"].folders) == 2
        assert "level2a" in existing.folders["level1"].folders
        assert "level2b" in existing.folders["level1"].folders

    def test_merge_folders_preserves_existing_paths(self, tmp_path):
        """Test that _merge_folders preserves paths of existing folders."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        existing_path = tmp_path / "test" / "parent" / "child"
        existing = WorkspaceFolder(
            name="parent",
            path=tmp_path / "test" / "parent",
            folders={"child": WorkspaceFolder(name="child", path=existing_path)},
        )
        existing.initialize()

        new = WorkspaceFolder(
            name="parent",
            folders={
                "child": WorkspaceFolder(
                    name="child",
                    folders={"grandchild": WorkspaceFolder(name="grandchild")},
                )
            },
        )

        workspace._merge_folders(existing, new)

        assert existing.folders["child"].path == existing_path

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

    def test_workspace_inherits_base_model_behavior(self):
        """Test that Workspace inherits WorkspaceBaseModel behavior."""
        workspace = Workspace(name="Test Workspace")
        assert workspace.name == "Test_Workspace"

    def test_workspace_saves_with_custom_config_file(self, tmp_path):
        """Test that workspace saves with custom config file name."""
        workspace = Workspace(
            name="test",
            path=tmp_path / "test",
            config_file="custom_config.json",
        )
        config_path = workspace.save()
        assert config_path.name == "custom_config.json"

    def test_create_folder_empty_list_raises_error(self, tmp_path):
        """Test that create_folder with empty list raises appropriate error."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        with pytest.raises(Exception):
            workspace.create_folder(name_or_path=[])

    def test_workspace_with_files(self, tmp_path):
        """Test that workspace can have files."""
        workspace = Workspace(
            name="test",
            path=tmp_path / "test",
            files=["file1.txt", "file2.txt"],
        )
        assert workspace.files == ["file1.txt", "file2.txt"]

        config_path = workspace.save()
        loaded = Workspace.load(config_path)
        assert loaded.files == ["file1.txt", "file2.txt"]

    def test_merge_folders_with_force_flag(self, tmp_path):
        """Test that _merge_folders respects force flag."""
        workspace = Workspace(name="test", path=tmp_path / "test")
        workspace.path.mkdir(parents=True, exist_ok=True)

        existing = WorkspaceFolder(
            name="parent",
            path=tmp_path / "test" / "parent",
        )
        existing.initialize()

        new = WorkspaceFolder(
            name="parent",
            folders={"new_child": WorkspaceFolder(name="new_child")},
        )

        workspace._merge_folders(existing, new, force=True)

        assert "new_child" in existing.folders
        assert existing.folders["new_child"].path.exists()
