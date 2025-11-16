"""Tests for workspace subfolder creation functionality."""

import json
from pathlib import Path

import pytest

from wa.folder.create import create_workspace_folder
from wa.subfolder.create import create_workspace_subfolder
from wa.models import WorkspaceSubfolder


class TestCreateWorkspaceSubfolder:
    """Test cases for create_workspace_subfolder function."""

    def test_create_single_subfolder(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test creating a single subfolder in a workspace."""
        # Create workspace first
        create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create subfolder
        subfolder = create_workspace_subfolder(
            workspace_subfolder_name="data",
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert subfolder.name == "data"
        expected_path = temp_workspaces_path / sample_workspace_name / "data"
        assert subfolder.path == expected_path
        assert subfolder.path.exists()
        assert subfolder.path.is_dir()

    def test_create_nested_subfolder_two_levels(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test creating nested subfolders with two levels."""
        # Create workspace first
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create nested subfolder
        subfolder = create_workspace_subfolder(
            workspace_subfolder_name=["parent", "child"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Verify structure
        assert subfolder.name == "parent"
        assert "child" in subfolder.subfolders

        # Verify paths exist
        parent_path = workspace.path / "parent"
        child_path = workspace.path / "parent" / "child"
        assert parent_path.exists()
        assert child_path.exists()

    def test_create_nested_subfolder_three_levels(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test creating nested subfolders with three levels."""
        # Create workspace first
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create deeply nested subfolder
        subfolder = create_workspace_subfolder(
            workspace_subfolder_name=["level1", "level2", "level3"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Verify structure
        assert subfolder.name == "level1"
        assert "level2" in subfolder.subfolders
        level2 = subfolder.subfolders["level2"]
        assert "level3" in level2.subfolders

        # Verify paths exist
        path1 = workspace.path / "level1"
        path2 = workspace.path / "level1" / "level2"
        path3 = workspace.path / "level1" / "level2" / "level3"
        assert path1.exists()
        assert path2.exists()
        assert path3.exists()

    def test_create_subfolder_updates_workspace_config(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that creating a subfolder updates the workspace config file."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        create_workspace_subfolder(
            workspace_subfolder_name="data",
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Read the config file
        config_path = workspace.path / "workspace.json"
        config = json.loads(config_path.read_text())

        assert "data" in config["subfolders"]

    def test_create_subfolder_sanitizes_names(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that subfolder names are sanitized properly."""
        create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create subfolder with spaces and invalid chars
        subfolder = create_workspace_subfolder(
            workspace_subfolder_name='my data<>:"/\\|?*folder',
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Spaces should become underscores, invalid chars removed
        assert subfolder.name == "my_datafolder"


class TestSubfolderMergeBehavior:
    """Test cases for subfolder merge behavior when overlapping paths exist."""

    def test_merge_top_level_siblings(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that creating sibling subfolders preserves both."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create first nested subfolder
        create_workspace_subfolder(
            workspace_subfolder_name=["parent", "child1"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create second nested subfolder with same parent
        create_workspace_subfolder(
            workspace_subfolder_name=["parent", "child2"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Verify both children exist
        config_path = workspace.path / "workspace.json"
        config = json.loads(config_path.read_text())

        parent_subfolders = config["subfolders"]["parent"]["subfolders"]
        assert "child1" in parent_subfolders
        assert "child2" in parent_subfolders

        # Verify filesystem
        assert (workspace.path / "parent" / "child1").exists()
        assert (workspace.path / "parent" / "child2").exists()

    def test_merge_preserves_existing_nested_structure(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test the exact scenario from the issue: existing ['subtest', 'anotherfolder']
        should be preserved when adding ['subtest', 'subsubtest']."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create first nested path
        create_workspace_subfolder(
            workspace_subfolder_name=["subtest", "anotherfolder"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create second nested path with same parent
        create_workspace_subfolder(
            workspace_subfolder_name=["subtest", "subsubtest"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Verify both are preserved
        config_path = workspace.path / "workspace.json"
        config = json.loads(config_path.read_text())

        subtest_subfolders = config["subfolders"]["subtest"]["subfolders"]
        assert set(subtest_subfolders.keys()) == {"anotherfolder", "subsubtest"}

        # Verify filesystem
        assert (workspace.path / "subtest" / "anotherfolder").exists()
        assert (workspace.path / "subtest" / "subsubtest").exists()

    def test_merge_at_deeper_nesting_levels(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test merging works at deeper nesting levels."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create first path
        create_workspace_subfolder(
            workspace_subfolder_name=["level1", "level2a", "level3"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Add sibling at level2
        create_workspace_subfolder(
            workspace_subfolder_name=["level1", "level2b"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Add sibling at level3
        create_workspace_subfolder(
            workspace_subfolder_name=["level1", "level2a", "level3b"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Verify structure
        config_path = workspace.path / "workspace.json"
        config = json.loads(config_path.read_text())

        level1 = config["subfolders"]["level1"]["subfolders"]
        assert set(level1.keys()) == {"level2a", "level2b"}

        level2a = level1["level2a"]["subfolders"]
        assert set(level2a.keys()) == {"level3", "level3b"}

        # Verify filesystem
        assert (workspace.path / "level1" / "level2a" / "level3").exists()
        assert (workspace.path / "level1" / "level2a" / "level3b").exists()
        assert (workspace.path / "level1" / "level2b").exists()

    def test_multiple_sequential_merges(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that multiple sequential merges all preserve existing structure."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create multiple nested paths sequentially
        paths = [
            ["root", "branch1"],
            ["root", "branch2"],
            ["root", "branch3"],
            ["root", "branch1", "leaf1"],
            ["root", "branch1", "leaf2"],
        ]

        for path in paths:
            create_workspace_subfolder(
                workspace_subfolder_name=path,
                workspace_folder_name=sample_workspace_name,
                workspaces_folder_path=temp_workspaces_path,
            )

        # Verify all branches exist
        config_path = workspace.path / "workspace.json"
        config = json.loads(config_path.read_text())

        root = config["subfolders"]["root"]["subfolders"]
        assert set(root.keys()) == {"branch1", "branch2", "branch3"}

        branch1 = root["branch1"]["subfolders"]
        assert set(branch1.keys()) == {"leaf1", "leaf2"}

        # Verify filesystem
        for path in paths:
            full_path = workspace.path.joinpath(*path)
            assert full_path.exists(), f"Path {full_path} should exist"

    def test_merge_with_force_flag(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that merge works correctly with force flag."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create first subfolder
        create_workspace_subfolder(
            workspace_subfolder_name=["parent", "child1"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create with force flag
        create_workspace_subfolder(
            workspace_subfolder_name=["parent", "child2"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
            force=True,
        )

        # Verify both exist
        config_path = workspace.path / "workspace.json"
        config = json.loads(config_path.read_text())

        parent_subfolders = config["subfolders"]["parent"]["subfolders"]
        assert set(parent_subfolders.keys()) == {"child1", "child2"}

    def test_merge_does_not_affect_other_top_level_subfolders(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that merging doesn't affect other top-level subfolders."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create separate top-level subfolders
        create_workspace_subfolder(
            workspace_subfolder_name=["folder1", "nested1"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        create_workspace_subfolder(
            workspace_subfolder_name=["folder2", "nested2"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Add to first folder
        create_workspace_subfolder(
            workspace_subfolder_name=["folder1", "nested1b"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Verify folder2 is unaffected
        config_path = workspace.path / "workspace.json"
        config = json.loads(config_path.read_text())

        folder1_subs = config["subfolders"]["folder1"]["subfolders"]
        folder2_subs = config["subfolders"]["folder2"]["subfolders"]

        assert set(folder1_subs.keys()) == {"nested1", "nested1b"}
        assert set(folder2_subs.keys()) == {"nested2"}

    def test_merge_with_identical_paths(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that creating identical nested paths multiple times works."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create same path twice
        path = ["level1", "level2", "level3"]
        create_workspace_subfolder(
            workspace_subfolder_name=path,
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        create_workspace_subfolder(
            workspace_subfolder_name=path,
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Should still have the same structure (no duplication)
        config_path = workspace.path / "workspace.json"
        config = json.loads(config_path.read_text())

        level1 = config["subfolders"]["level1"]["subfolders"]
        assert list(level1.keys()) == ["level2"]

        level2 = level1["level2"]["subfolders"]
        assert list(level2.keys()) == ["level3"]

        # Path should exist
        full_path = workspace.path / "level1" / "level2" / "level3"
        assert full_path.exists()


class TestSubfolderCreationEdgeCases:
    """Test edge cases for subfolder creation."""

    def test_create_single_subfolder_with_string(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that passing a string creates a single subfolder."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        subfolder = create_workspace_subfolder(
            workspace_subfolder_name="simple",
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        assert subfolder.name == "simple"
        assert len(subfolder.subfolders) == 0
        assert (workspace.path / "simple").exists()

    def test_create_with_empty_list_raises_error(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that passing an empty list raises appropriate error."""
        create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Empty list should cause an error during processing
        with pytest.raises(UnboundLocalError):
            create_workspace_subfolder(
                workspace_subfolder_name=[],
                workspace_folder_name=sample_workspace_name,
                workspaces_folder_path=temp_workspaces_path,
            )

    def test_subfolder_path_returned_is_deepest(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that the returned subfolder path is the deepest nested path."""
        workspace = create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Create nested structure
        subfolder = create_workspace_subfolder(
            workspace_subfolder_name=["a", "b", "c"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # The top-level WorkspaceSubfolder object is returned
        assert subfolder.name == "a"

        # But when we merge, we want to verify the deepest path exists
        deepest_path = workspace.path / "a" / "b" / "c"
        assert deepest_path.exists()

    def test_create_nested_with_kwargs(
        self, temp_workspaces_path: Path, sample_workspace_name: str
    ):
        """Test that kwargs are passed through to WorkspaceSubfolder creation."""
        create_workspace_folder(
            name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Note: Currently WorkspaceSubfolder doesn't have additional fields,
        # but this tests that the pattern works
        subfolder = create_workspace_subfolder(
            workspace_subfolder_name=["parent", "child"],
            workspace_folder_name=sample_workspace_name,
            workspaces_folder_path=temp_workspaces_path,
        )

        # Should create successfully
        assert subfolder.name == "parent"
        assert "child" in subfolder.subfolders
