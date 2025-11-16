"""Tests for Workspace model."""

from pathlib import Path

import pytest

from wa.models import Workspace


class TestWorkspaceModel:
    """Test cases for the Workspace model."""

    def test_workspace_creation_with_minimal_fields(self):
        """Test creating a workspace with only required fields."""
        workspace = Workspace(name="test")

        assert workspace.name == "test"
        assert workspace.version  # Should have a default version
        assert workspace.subfolders == []
        assert workspace.config_file == "workspace.json"

    def test_workspace_name_normalization_spaces(self):
        """Test that spaces in names are converted to underscores."""
        workspace = Workspace(name="my test workspace")

        assert workspace.name == "my_test_workspace"

    def test_workspace_name_sanitization_invalid_chars(self):
        """Test that invalid characters are removed from workspace name."""
        # Test all invalid characters: < > : " / \ | ? * and control chars
        workspace = Workspace(name='test<>:"/\\|?*name')

        assert workspace.name == "testname"

    def test_workspace_name_sanitization_control_chars(self):
        """Test that control characters (0x00-0x1F) are removed."""
        workspace = Workspace(name="test\x00\x01\x1Fname")

        assert workspace.name == "testname"

    def test_workspace_name_truncation(self):
        """Test that workspace names are truncated to 255 characters."""
        long_name = "a" * 300
        workspace = Workspace(name=long_name)

        assert len(workspace.name) == 255
        assert workspace.name == "a" * 255

    def test_workspace_name_combined_sanitization(self):
        """Test that both space normalization and sanitization work together."""
        workspace = Workspace(name="my test<name>with:invalid/chars")

        assert workspace.name == "my_testnamewithinvalidchars"

    def test_populate_missing_paths_custom_workspaces_folder(self, tmp_path: Path):
        """Test that custom workspaces_folder_path is preserved."""
        custom_path = tmp_path / "custom_workspaces"
        workspace = Workspace(
            name="test",
            workspaces_folder_path=custom_path,
        )

        assert workspace.workspaces_folder_path == custom_path

    def test_populate_missing_paths_workspace_path(self, tmp_path: Path):
        """Test that workspace path is populated based on name and workspaces_folder_path."""
        workspaces_folder = tmp_path / "workspaces"
        workspace = Workspace(
            name="test",
            workspaces_folder_path=workspaces_folder,
        )

        assert workspace.path == workspaces_folder / "test"

    def test_populate_missing_paths_custom_workspace_path(self, tmp_path: Path):
        """Test that custom workspace path is preserved."""
        custom_path = tmp_path / "custom" / "path"
        workspace = Workspace(
            name="test",
            path=custom_path,
        )

        assert workspace.path == custom_path

    def test_save_creates_config_file(self, tmp_path: Path):
        """Test that save() creates a config file."""
        workspace = Workspace(
            name="test",
            workspaces_folder_path=tmp_path,
        )

        config_path = workspace.save()

        assert config_path.exists()
        assert config_path.name == "workspace.json"
        assert config_path.parent == workspace.path

    def test_save_creates_parent_directories(self, tmp_path: Path):
        """Test that save() creates parent directories if they don't exist."""
        workspaces_folder = tmp_path / "nested" / "workspaces"
        workspace = Workspace(
            name="test",
            workspaces_folder_path=workspaces_folder,
        )

        assert not workspace.path.exists()

        config_path = workspace.save()

        assert workspace.path.exists()
        assert config_path.exists()

    def test_save_with_custom_path(self, tmp_path: Path):
        """Test that save() can save to a custom path."""
        workspace = Workspace(
            name="test",
            workspaces_folder_path=tmp_path,
        )

        custom_path = tmp_path / "custom_config.json"
        config_path = workspace.save(path=custom_path)

        assert config_path == custom_path
        assert custom_path.exists()

    def test_save_content_is_valid_json(self, tmp_path: Path):
        """Test that saved content is valid JSON with correct fields."""
        workspace = Workspace(
            name="test",
            workspaces_folder_path=tmp_path,
            subfolders=["data", "models"],
        )

        config_path = workspace.save()
        content = config_path.read_text()

        assert '"name": "test"' in content
        assert '"subfolders"' in content
        assert '"data"' in content
        assert '"models"' in content

    def test_load_existing_workspace(self, tmp_path: Path):
        """Test loading an existing workspace from config file."""
        # Create and save a workspace
        original_workspace = Workspace(
            name="test",
            workspaces_folder_path=tmp_path,
            subfolders=["data", "models"],
        )
        config_path = original_workspace.save()

        # Load it back
        loaded_workspace = Workspace.load(config_path)

        assert loaded_workspace.name == original_workspace.name
        assert loaded_workspace.subfolders == original_workspace.subfolders
        assert loaded_workspace.config_file == original_workspace.config_file

    def test_load_nonexistent_file_raises_error(self, tmp_path: Path):
        """Test that loading a nonexistent file raises FileNotFoundError."""
        nonexistent_path = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError, match="Workspace file not found"):
            Workspace.load(nonexistent_path)

    def test_workspace_with_all_fields(self, tmp_path: Path):
        """Test creating a workspace with all fields specified."""
        workspaces_folder = tmp_path / "workspaces"
        workspace_path = workspaces_folder / "test"

        workspace = Workspace(
            name="test",
            version="1.0.0",
            path=workspace_path,
            workspaces_folder_path=workspaces_folder,
            subfolders=["data", "models", "outputs"],
            config_file="custom_config.json",
        )

        assert workspace.name == "test"
        assert workspace.version == "1.0.0"
        assert workspace.path == workspace_path
        assert workspace.workspaces_folder_path == workspaces_folder
        assert workspace.subfolders == ["data", "models", "outputs"]
        assert workspace.config_file == "custom_config.json"

    def test_workspace_save_and_load_roundtrip(self, tmp_path: Path):
        """Test that a workspace can be saved and loaded without data loss."""
        original = Workspace(
            name="roundtrip_test",
            workspaces_folder_path=tmp_path,
            subfolders=["data", "models", "outputs"],
        )

        config_path = original.save()
        loaded = Workspace.load(config_path)

        assert loaded.name == original.name
        assert loaded.version == original.version
        assert loaded.path == original.path
        assert loaded.workspaces_folder_path == original.workspaces_folder_path
        assert loaded.subfolders == original.subfolders
        assert loaded.config_file == original.config_file

    def test_workspace_empty_name_normalization(self):
        """Test handling of edge case with empty or whitespace-only names."""
        workspace = Workspace(name="   ")

        assert workspace.name == "___"

    def test_workspace_path_types(self, tmp_path: Path):
        """Test that paths are properly converted to Path objects."""
        workspace = Workspace(
            name="test",
            workspaces_folder_path=tmp_path,
        )

        assert isinstance(workspace.path, Path)
        assert isinstance(workspace.workspaces_folder_path, Path)
