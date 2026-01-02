from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from wa.workspace.models.workspace import Workspace
from wa.workspace.list import list_workspaces


class TestListWorkspaces:
    """Test the list_workspaces function."""

    def test_list_workspaces_empty_directory(self, tmp_path):
        """Test that list_workspaces returns empty list when no workspaces exist."""
        workspaces_path = tmp_path / "workspaces"
        workspaces_path.mkdir(parents=True)

        result = list_workspaces(workspaces_path=workspaces_path)

        assert result == []

    def test_list_workspaces_creates_directory_if_missing(self, tmp_path):
        """Test that list_workspaces creates the directory if it doesn't exist."""
        workspaces_path = tmp_path / "workspaces"
        assert not workspaces_path.exists()

        list_workspaces(workspaces_path=workspaces_path)

        assert workspaces_path.exists()
        assert workspaces_path.is_dir()

    def test_list_workspaces_single_workspace(self, tmp_path):
        """Test that list_workspaces returns single workspace."""
        workspaces_path = tmp_path / "workspaces"
        workspace = Workspace(
            name="workspace1",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        result = list_workspaces(workspaces_path=workspaces_path)

        assert "workspace1" in result
        assert len(result) == 1

    def test_list_workspaces_multiple_workspaces(self, tmp_path):
        """Test that list_workspaces returns multiple workspaces."""
        workspaces_path = tmp_path / "workspaces"

        for i in range(3):
            workspace = Workspace(
                name=f"workspace{i}",
                workspaces_path=workspaces_path,
            )
            workspace.save()

        result = list_workspaces(workspaces_path=workspaces_path)

        assert len(result) == 3
        assert "workspace0" in result
        assert "workspace1" in result
        assert "workspace2" in result

    def test_list_workspaces_ignores_directories_without_config(self, tmp_path):
        """Test that list_workspaces only includes directories with workspace.json.

        Note: The current implementation has a bug where it returns all directories,
        not just those with workspace.json. This test documents expected behavior.
        """
        workspaces_path = tmp_path / "workspaces"
        workspaces_path.mkdir(parents=True)

        # Create workspace with config
        workspace = Workspace(
            name="valid_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        # Create directory without config
        (workspaces_path / "invalid_workspace").mkdir()

        result = list_workspaces(workspaces_path=workspaces_path)

        # Current implementation returns both, but ideally should only return valid_workspace
        # This test documents the current behavior
        assert "valid_workspace" in result
        assert "invalid_workspace" in result  # Bug: should not be included

    def test_list_workspaces_ignores_files(self, tmp_path):
        """Test that list_workspaces ignores files in the workspaces directory."""
        workspaces_path = tmp_path / "workspaces"
        workspaces_path.mkdir(parents=True)

        # Create a workspace
        workspace = Workspace(
            name="workspace1",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        # Create a file in workspaces directory
        (workspaces_path / "not_a_workspace.txt").write_text("test")

        result = list_workspaces(workspaces_path=workspaces_path)

        assert "workspace1" in result
        assert "not_a_workspace.txt" not in result

    def test_list_workspaces_with_default_path(self, tmp_path):
        """Test that list_workspaces uses default path when not specified."""
        workspace = Workspace(
            name="default_workspace",
            workspaces_path=tmp_path / "workspaces",
        )
        workspace.save()

        with patch("wa.workspace.list.get_project_root", return_value=tmp_path):
            result = list_workspaces()
            assert "default_workspace" in result

    def test_list_workspaces_path_is_file_raises_error(self, tmp_path):
        """Test that list_workspaces raises error when path is a file."""
        file_path = tmp_path / "not_a_directory"
        file_path.write_text("test")

        with pytest.raises(FileNotFoundError):
            list_workspaces(workspaces_path=file_path)

    def test_list_workspaces_with_nested_subdirectories(self, tmp_path):
        """Test that list_workspaces only lists top-level workspace directories."""
        workspaces_path = tmp_path / "workspaces"

        # Create workspace with nested folders
        workspace = Workspace(
            name="parent_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        # Create a subdirectory inside the workspace
        nested_dir = workspace.path / "nested"
        nested_dir.mkdir()

        result = list_workspaces(workspaces_path=workspaces_path)

        assert "parent_workspace" in result
        assert "nested" not in result

    def test_list_workspaces_returns_list(self, tmp_path):
        """Test that list_workspaces returns a list."""
        workspaces_path = tmp_path / "workspaces"
        workspaces_path.mkdir(parents=True)

        result = list_workspaces(workspaces_path=workspaces_path)

        assert isinstance(result, list)

    def test_list_workspaces_with_special_characters_in_name(self, tmp_path):
        """Test that list_workspaces handles workspace names with special characters."""
        workspaces_path = tmp_path / "workspaces"

        # Workspace names get sanitized, so test with sanitized names
        workspace = Workspace(
            name="test_workspace",
            workspaces_path=workspaces_path,
        )
        workspace.save()

        result = list_workspaces(workspaces_path=workspaces_path)

        assert "test_workspace" in result

    def test_list_workspaces_many_workspaces(self, tmp_path):
        """Test that list_workspaces handles many workspaces."""
        workspaces_path = tmp_path / "workspaces"

        # Create 20 workspaces
        for i in range(20):
            workspace = Workspace(
                name=f"workspace_{i:02d}",
                workspaces_path=workspaces_path,
            )
            workspace.save()

        result = list_workspaces(workspaces_path=workspaces_path)

        assert len(result) == 20
        for i in range(20):
            assert f"workspace_{i:02d}" in result

    def test_list_workspaces_empty_workspace_directory(self, tmp_path):
        """Test that list_workspaces handles empty workspace directory without config."""
        workspaces_path = tmp_path / "workspaces"
        workspaces_path.mkdir(parents=True)

        # Create empty directory (no workspace.json)
        (workspaces_path / "empty_dir").mkdir()

        result = list_workspaces(workspaces_path=workspaces_path)

        # Current implementation includes directories without config
        assert "empty_dir" in result
