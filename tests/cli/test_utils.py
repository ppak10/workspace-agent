from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from wa.cli.utils import get_workspace_path, print_list


class TestPrintList:
    """Test the print_list function."""

    @patch("wa.cli.utils.rprint")
    def test_print_list_with_values(self, mock_rprint):
        """Test that print_list outputs values correctly."""
        values = ["item1", "item2", "item3"]
        print_list("Test Items", values)

        # Should call rprint 4 times: header + 3 items
        assert mock_rprint.call_count == 4
        mock_rprint.assert_any_call("\n  Test Items:")
        mock_rprint.assert_any_call("  1. [cyan]item1[/cyan]")
        mock_rprint.assert_any_call("  2. [cyan]item2[/cyan]")
        mock_rprint.assert_any_call("  3. [cyan]item3[/cyan]")

    @patch("wa.cli.utils.rprint")
    def test_print_list_with_empty_list(self, mock_rprint):
        """Test that print_list handles empty list correctly."""
        print_list("Empty Items", [])

        # Should call rprint 1 time for header only (no items to display)
        assert mock_rprint.call_count == 1
        mock_rprint.assert_any_call("\n  Empty Items:")

    @patch("wa.cli.utils.rprint")
    def test_print_list_with_none(self, mock_rprint):
        """Test that print_list handles None correctly."""
        print_list("Missing Items", None)

        # Should call rprint 2 times: header + warning message
        assert mock_rprint.call_count == 2
        mock_rprint.assert_any_call("\n  Missing Items:")
        mock_rprint.assert_any_call("  ⚠️  [yellow]No Missing Items found.[/yellow]")

    @patch("wa.cli.utils.rprint")
    def test_print_list_with_single_item(self, mock_rprint):
        """Test that print_list handles single item correctly."""
        print_list("Single Item", ["only_one"])

        assert mock_rprint.call_count == 2
        mock_rprint.assert_any_call("\n  Single Item:")
        mock_rprint.assert_any_call("  1. [cyan]only_one[/cyan]")

    @patch("wa.cli.utils.rprint")
    def test_print_list_indexing_starts_at_one(self, mock_rprint):
        """Test that print_list numbering starts at 1 not 0."""
        values = ["first", "second"]
        print_list("Items", values)

        # Check that indices are 1-based
        mock_rprint.assert_any_call("  1. [cyan]first[/cyan]")
        mock_rprint.assert_any_call("  2. [cyan]second[/cyan]")


class TestGetWorkspacePath:
    """Test the get_workspace_path function."""

    def test_get_workspace_path_with_workspace_option(self, tmp_path):
        """Test that get_workspace_path returns correct path when workspace is specified."""
        # Create workspace structure
        workspaces_dir = tmp_path / "workspaces" / "my_workspace"
        workspaces_dir.mkdir(parents=True)
        config_file = workspaces_dir / "workspace.json"
        config_file.write_text("{}")

        with patch("wa.cli.utils.get_project_root", return_value=tmp_path):
            result = get_workspace_path(workspace="my_workspace")
            assert result == workspaces_dir
            assert result.exists()

    def test_get_workspace_path_current_directory(self, tmp_path, monkeypatch):
        """Test that get_workspace_path uses current directory when workspace is None."""
        # Set up current directory with config file
        config_file = tmp_path / "workspace.json"
        config_file.write_text("{}")

        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)

        result = get_workspace_path(workspace=None)
        assert result == tmp_path
        assert result.exists()

    def test_get_workspace_path_missing_config_raises_error(self, tmp_path):
        """Test that get_workspace_path raises error when config file doesn't exist."""
        workspaces_dir = tmp_path / "workspaces" / "no_config"
        workspaces_dir.mkdir(parents=True)

        with patch("wa.cli.utils.get_project_root", return_value=tmp_path):
            with pytest.raises(typer.Exit) as exc_info:
                get_workspace_path(workspace="no_config")
            assert exc_info.value.exit_code == 1

    def test_get_workspace_path_current_dir_missing_config(self, tmp_path, monkeypatch):
        """Test that get_workspace_path raises error when current dir has no config."""
        # Change to empty directory
        monkeypatch.chdir(tmp_path)

        with pytest.raises(typer.Exit) as exc_info:
            get_workspace_path(workspace=None)
        assert exc_info.value.exit_code == 1

    def test_get_workspace_path_custom_config_file(self, tmp_path):
        """Test that get_workspace_path works with custom config file name."""
        workspaces_dir = tmp_path / "workspaces" / "custom_workspace"
        workspaces_dir.mkdir(parents=True)
        custom_config = workspaces_dir / "custom.json"
        custom_config.write_text("{}")

        with patch("wa.cli.utils.get_project_root", return_value=tmp_path):
            result = get_workspace_path(
                workspace="custom_workspace", config_file="custom.json"
            )
            assert result == workspaces_dir

    def test_get_workspace_path_custom_workspaces_folder(self, tmp_path):
        """Test that get_workspace_path works with custom workspaces folder name."""
        custom_dir = tmp_path / "my_workspaces" / "test_workspace"
        custom_dir.mkdir(parents=True)
        config_file = custom_dir / "workspace.json"
        config_file.write_text("{}")

        with patch("wa.cli.utils.get_project_root", return_value=tmp_path):
            result = get_workspace_path(
                workspace="test_workspace", workspaces_folder_name="my_workspaces"
            )
            assert result == custom_dir

    def test_get_workspace_path_nested_workspace_structure(self, tmp_path):
        """Test that get_workspace_path handles nested workspace paths."""
        nested_dir = tmp_path / "workspaces" / "nested" / "deep"
        nested_dir.mkdir(parents=True)

        # This should fail since workspace is just "nested" not "nested/deep"
        # and nested doesn't have workspace.json
        with patch("wa.cli.utils.get_project_root", return_value=tmp_path):
            with pytest.raises(typer.Exit) as exc_info:
                get_workspace_path(workspace="nested")
            assert exc_info.value.exit_code == 1

    @patch("wa.cli.utils.rprint")
    def test_get_workspace_path_error_message_format(self, mock_rprint, tmp_path):
        """Test that error message is properly formatted when config is missing."""
        workspaces_dir = tmp_path / "workspaces" / "missing"
        workspaces_dir.mkdir(parents=True)

        with patch("wa.cli.utils.get_project_root", return_value=tmp_path):
            with pytest.raises(typer.Exit):
                get_workspace_path(workspace="missing")

            # Verify error message was printed
            expected_config_path = workspaces_dir / "workspace.json"
            mock_rprint.assert_called_once()
            call_args = mock_rprint.call_args[0][0]
            assert "❌" in call_args
            assert "not a valid workspace folder" in call_args
            assert str(expected_config_path) in call_args

    def test_get_workspace_path_returns_path_object(self, tmp_path, monkeypatch):
        """Test that get_workspace_path returns a Path object."""
        config_file = tmp_path / "workspace.json"
        config_file.write_text("{}")
        monkeypatch.chdir(tmp_path)

        result = get_workspace_path(workspace=None)
        assert isinstance(result, Path)
