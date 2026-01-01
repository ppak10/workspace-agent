from __future__ import annotations

from pathlib import Path

import pytest

from wa.workspace.models.workspace_base_model import WorkspaceBaseModel
from wa.workspace.models.workspace_folder import WorkspaceFolder

# Rebuild the model to resolve forward references after WorkspaceFolder is imported
WorkspaceBaseModel.model_rebuild()


class TestWorkspaceBaseModel:
    """Test the WorkspaceBaseModel class."""

    def test_basic_initialization(self):
        """Test that WorkspaceBaseModel can be initialized with basic parameters."""
        model = WorkspaceBaseModel(name="test_model")
        assert model.name == "test_model"
        assert model.path == Path("")
        assert model.folders == {}
        assert model.files == []

    def test_name_sanitization(self):
        """Test that names are sanitized properly."""
        model = WorkspaceBaseModel(name="My Test Model")
        assert model.name == "My_Test_Model"

    def test_name_removes_invalid_characters(self):
        """Test that invalid characters are removed from names."""
        model = WorkspaceBaseModel(name='invalid<>:"/\\|?*chars')
        assert model.name == "invalidchars"

    def test_name_truncates_long_names(self):
        """Test that names longer than 255 characters are truncated."""
        long_name = "a" * 300
        model = WorkspaceBaseModel(name=long_name)
        assert len(model.name) == 255

    def test_path_initialization(self):
        """Test that path can be initialized."""
        model = WorkspaceBaseModel(name="test", path=Path("/tmp/test"))
        assert model.path == Path("/tmp/test")

    def test_folders_dict_format(self):
        """Test that folders can be provided as a dict."""
        folders = {
            "folder1": WorkspaceFolder(name="folder1"),
            "folder2": WorkspaceFolder(name="folder2"),
        }
        model = WorkspaceBaseModel(name="test", folders=folders)
        assert len(model.folders) == 2
        assert "folder1" in model.folders
        assert "folder2" in model.folders

    def test_folders_list_of_workspace_folder_objects(self):
        """Test that folders can be provided as a list of WorkspaceFolder objects."""
        folders = [
            WorkspaceFolder(name="folder1"),
            WorkspaceFolder(name="folder2"),
        ]
        model = WorkspaceBaseModel(name="test", folders=folders)
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
        model = WorkspaceBaseModel(name="test", folders=folders)
        assert len(model.folders) == 2
        assert "folder1" in model.folders
        assert "folder2" in model.folders

    def test_folders_list_of_strings(self):
        """Test that folders can be provided as a list of strings."""
        folders = ["folder1", "folder2"]
        model = WorkspaceBaseModel(name="test", folders=folders)
        assert len(model.folders) == 2
        assert "folder1" in model.folders
        assert "folder2" in model.folders
        assert isinstance(model.folders["folder1"], WorkspaceFolder)

    def test_folders_empty_by_default(self):
        """Test that folders default to an empty dict."""
        model = WorkspaceBaseModel(name="test")
        assert model.folders == {}

    def test_folders_invalid_format_returns_empty(self):
        """Test that invalid folder formats return an empty dict."""
        model = WorkspaceBaseModel(name="test", folders="invalid")
        assert model.folders == {}

    def test_files_default_empty_list(self):
        """Test that files default to an empty list."""
        model = WorkspaceBaseModel(name="test")
        assert model.files == []

    def test_files_can_be_provided(self):
        """Test that files can be provided during initialization."""
        files = ["file1.txt", "file2.txt"]
        model = WorkspaceBaseModel(name="test", files=files)
        assert model.files == files

    def test_parse_folders_mixed_list(self):
        """Test that parse_folders handles a mixed list of folder types."""
        folders = [
            WorkspaceFolder(name="ws_folder"),
            {"name": "dict_folder"},
            "string_folder",
        ]
        model = WorkspaceBaseModel(name="test", folders=folders)
        assert len(model.folders) == 3
        assert "ws_folder" in model.folders
        assert "dict_folder" in model.folders
        assert "string_folder" in model.folders

    def test_folders_preserve_nested_structure(self):
        """Test that nested folder structures are preserved."""
        nested_folder = WorkspaceFolder(
            name="parent",
            folders=[
                WorkspaceFolder(name="child1"),
                WorkspaceFolder(name="child2"),
            ],
        )
        model = WorkspaceBaseModel(name="test", folders=[nested_folder])
        assert "parent" in model.folders
        assert len(model.folders["parent"].folders) == 2
        assert "child1" in model.folders["parent"].folders
        assert "child2" in model.folders["parent"].folders

    def test_name_sanitization_with_underscores(self):
        """Test that existing underscores are preserved during sanitization."""
        model = WorkspaceBaseModel(name="test_model_name")
        assert model.name == "test_model_name"

    def test_name_sanitization_with_special_cases(self):
        """Test name sanitization with various special cases."""
        test_cases = [
            ("name with  multiple   spaces", "name_with__multiple___spaces"),
            ("trailing_spaces   ", "trailing_spaces___"),
            ("   leading_spaces", "___leading_spaces"),
            ("dots.in.name", "dots.in.name"),
            ("dashes-in-name", "dashes-in-name"),
        ]
        for input_name, expected_name in test_cases:
            model = WorkspaceBaseModel(name=input_name)
            assert model.name == expected_name

    def test_folders_dict_with_sanitized_names(self):
        """Test that folder names in dict are properly keyed after sanitization."""
        folders = [
            WorkspaceFolder(name="Folder One"),
            WorkspaceFolder(name="Folder Two"),
        ]
        model = WorkspaceBaseModel(name="test", folders=folders)
        # Names should be sanitized
        assert "Folder_One" in model.folders
        assert "Folder_Two" in model.folders
