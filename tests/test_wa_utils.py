from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch
import importlib.util

import pytest

from wa.utils import get_project_root, create_pathname, append_timestamp_to_name


class TestGetProjectRoot:
    """Test the get_project_root function."""

    def test_get_project_root_development_mode(self):
        """Test get_project_root in development mode (with src/ folder)."""
        # Mock spec to simulate development setup
        mock_spec = MagicMock()
        # Simulate: /path/to/workspace-agent/src/wa/__init__.py
        mock_spec.origin = "/path/to/workspace-agent/src/wa/__init__.py"

        with patch("importlib.util.find_spec", return_value=mock_spec):
            result = get_project_root()
            # Should return /path/to/workspace-agent
            assert result == Path("/path/to/workspace-agent")

    def test_get_project_root_pypi_install(self):
        """Test get_project_root in PyPI installation (site-packages)."""
        # Mock spec to simulate PyPI installation
        mock_spec = MagicMock()
        # Simulate: /path/to/workspace-agent/.venv/lib/python3.13/site-packages/wa/__init__.py
        mock_spec.origin = (
            "/path/to/workspace-agent/.venv/lib/python3.13/site-packages/wa/__init__.py"
        )

        with patch("importlib.util.find_spec", return_value=mock_spec):
            result = get_project_root(parents_index=4)
            # Should return /path/to/workspace-agent
            assert result == Path("/path/to/workspace-agent")

    def test_get_project_root_custom_parents_index(self):
        """Test get_project_root with custom parents_index."""
        mock_spec = MagicMock()
        # Simulate a different depth
        mock_spec.origin = "/a/b/c/d/e/wa/__init__.py"

        with patch("importlib.util.find_spec", return_value=mock_spec):
            # parents[2] would be /a/b/c
            result = get_project_root(parents_index=2)
            assert result == Path("/a/b/c")

    def test_get_project_root_spec_is_none(self):
        """Test get_project_root when spec is None."""
        with patch("importlib.util.find_spec", return_value=None):
            result = get_project_root()
            # Should fallback to current working directory
            assert result == Path.cwd()

    def test_get_project_root_spec_origin_is_none(self):
        """Test get_project_root when spec.origin is None."""
        mock_spec = MagicMock()
        mock_spec.origin = None

        with patch("importlib.util.find_spec", return_value=mock_spec):
            result = get_project_root()
            # Should fallback to current working directory
            assert result == Path.cwd()

    def test_get_project_root_import_error(self):
        """Test get_project_root when ImportError is raised."""
        with patch(
            "importlib.util.find_spec", side_effect=ImportError("Module not found")
        ):
            result = get_project_root()
            # Should fallback to current working directory
            assert result == Path.cwd()

    def test_get_project_root_returns_path_object(self):
        """Test that get_project_root returns a Path object."""
        mock_spec = MagicMock()
        mock_spec.origin = "/some/path/src/wa/__init__.py"

        with patch("importlib.util.find_spec", return_value=mock_spec):
            result = get_project_root()
            assert isinstance(result, Path)


class TestCreatePathname:
    """Test the create_pathname function."""

    def test_create_pathname_replaces_spaces(self):
        """Test that create_pathname replaces spaces with underscores."""
        result = create_pathname("my project name")
        assert result == "my_project_name"

    def test_create_pathname_removes_forbidden_characters(self):
        """Test that create_pathname removes forbidden characters."""
        # Test common forbidden characters: < > : " / \ | ? *
        result = create_pathname('bad<>:"/\\|?*name')
        assert result == "badname"

    def test_create_pathname_removes_control_characters(self):
        """Test that create_pathname removes control characters (0x00-0x1F)."""
        # Include various control characters
        name_with_controls = "test\x00\x01\x0A\x0D\x1Fname"
        result = create_pathname(name_with_controls)
        assert result == "testname"

    def test_create_pathname_truncates_to_255_characters(self):
        """Test that create_pathname truncates names to 255 characters."""
        long_name = "a" * 300
        result = create_pathname(long_name)
        assert len(result) == 255
        assert result == "a" * 255

    def test_create_pathname_exactly_255_characters(self):
        """Test that create_pathname handles exactly 255 characters."""
        name_255 = "b" * 255
        result = create_pathname(name_255)
        assert len(result) == 255
        assert result == name_255

    def test_create_pathname_preserves_unicode(self):
        """Test that create_pathname preserves Unicode characters."""
        # Unicode characters should be preserved (only ASCII forbidden chars removed)
        result = create_pathname("projet_été_2024")
        assert result == "projet_été_2024"

    def test_create_pathname_preserves_emoji(self):
        """Test that create_pathname preserves emoji characters."""
        result = create_pathname("my project 🚀")
        assert result == "my_project_🚀"

    def test_create_pathname_complex_combination(self):
        """Test create_pathname with combination of issues."""
        # Spaces + forbidden chars + control chars
        complex_name = 'my project: "test" \x00\x1F folder/subfolder'
        result = create_pathname(complex_name)
        assert result == "my_project_test__foldersubfolder"

    def test_create_pathname_empty_string(self):
        """Test that create_pathname handles empty string."""
        result = create_pathname("")
        assert result == ""

    def test_create_pathname_only_forbidden_characters(self):
        """Test create_pathname with only forbidden characters."""
        result = create_pathname('<>:"/\\|?*')
        assert result == ""

    def test_create_pathname_multiple_spaces(self):
        """Test that create_pathname handles multiple consecutive spaces."""
        result = create_pathname("my    project    name")
        assert result == "my____project____name"

    def test_create_pathname_special_characters_preserved(self):
        """Test that create_pathname preserves allowed special characters."""
        # These should be preserved: - _ . ( ) [ ] { } , ; ! @ # $ % ^ & + =
        result = create_pathname("file-name_v1.0(test)[final]{copy},ready;ok!@#$%^&+=")
        assert result == "file-name_v1.0(test)[final]{copy},ready;ok!@#$%^&+="

    def test_create_pathname_windows_forbidden_names(self):
        """Test create_pathname with Windows forbidden characters."""
        # All Windows forbidden characters
        result = create_pathname("file<name>with:bad/chars\\and|more?stuff*here")
        assert result == "filenamewithbadcharsandmorestuffhere"

    def test_create_pathname_null_character(self):
        """Test that create_pathname removes null character."""
        result = create_pathname("before\x00after")
        assert result == "beforeafter"
        assert "\x00" not in result


class TestAppendTimestampToName:
    """Test the append_timestamp_to_name function."""

    def test_append_timestamp_to_name_string_input(self):
        """Test that append_timestamp_to_name adds timestamp to string."""
        from datetime import datetime

        # Mock datetime to return a fixed time
        mock_datetime = MagicMock()
        mock_datetime.now.return_value.strftime.return_value = (
            "test_folder_20240315_143022"
        )

        with patch("wa.utils.datetime", mock_datetime):
            result = append_timestamp_to_name("test_folder")
            assert result == "test_folder_20240315_143022"
            # Verify strftime was called with correct format
            mock_datetime.now.return_value.strftime.assert_called_once_with(
                "test_folder_%Y%m%d_%H%M%S"
            )

    def test_append_timestamp_to_name_list_input_single_element(self):
        """Test that append_timestamp_to_name modifies last element of single-element list."""
        from datetime import datetime

        mock_datetime = MagicMock()
        mock_datetime.now.return_value.strftime.return_value = (
            "workspace_20240315_143022"
        )

        with patch("wa.utils.datetime", mock_datetime):
            result = append_timestamp_to_name(["workspace"])
            assert result == ["workspace_20240315_143022"]
            assert isinstance(result, list)

    def test_append_timestamp_to_name_list_input_multiple_elements(self):
        """Test that append_timestamp_to_name only modifies last element of multi-element list."""
        from datetime import datetime

        mock_datetime = MagicMock()
        mock_datetime.now.return_value.strftime.return_value = (
            "subfolder_20240315_143022"
        )

        with patch("wa.utils.datetime", mock_datetime):
            result = append_timestamp_to_name(["folder1", "folder2", "subfolder"])
            assert result == ["folder1", "folder2", "subfolder_20240315_143022"]
            assert isinstance(result, list)
            # Verify first two elements are unchanged
            assert result[0] == "folder1"
            assert result[1] == "folder2"

    def test_append_timestamp_to_name_empty_string(self):
        """Test that append_timestamp_to_name handles empty string."""
        from datetime import datetime

        mock_datetime = MagicMock()
        mock_datetime.now.return_value.strftime.return_value = "_20240315_143022"

        with patch("wa.utils.datetime", mock_datetime):
            result = append_timestamp_to_name("")
            assert result == "_20240315_143022"
            # Verify the format string starts with empty string
            mock_datetime.now.return_value.strftime.assert_called_once_with(
                "_%Y%m%d_%H%M%S"
            )

    def test_append_timestamp_to_name_format_verification(self):
        """Test that append_timestamp_to_name uses correct datetime format without mocking."""
        import re
        from datetime import datetime

        # Test with actual datetime (no mocking) to verify format pattern
        result = append_timestamp_to_name("test")

        # Verify the format matches: name_YYYYMMDD_HHMMSS
        pattern = r"^test_\d{8}_\d{6}$"
        assert re.match(
            pattern, result
        ), f"Result '{result}' does not match expected format"

        # Extract and verify the timestamp part
        timestamp_part = result.replace("test_", "")
        date_part, time_part = timestamp_part.split("_")

        # Verify date format (YYYYMMDD)
        assert len(date_part) == 8
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        assert 2020 <= year <= 2100  # Reasonable year range
        assert 1 <= month <= 12
        assert 1 <= day <= 31

        # Verify time format (HHMMSS)
        assert len(time_part) == 6
        hour = int(time_part[:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
        assert 0 <= second <= 59

    def test_append_timestamp_to_name_list_format_verification(self):
        """Test that append_timestamp_to_name uses correct format for list input."""
        import re

        result = append_timestamp_to_name(["parent", "child"])

        # Verify list structure
        assert len(result) == 2
        assert result[0] == "parent"

        # Verify second element has timestamp appended
        pattern = r"^child_\d{8}_\d{6}$"
        assert re.match(
            pattern, result[1]
        ), f"Result '{result[1]}' does not match expected format"

    def test_append_timestamp_to_name_preserves_list_reference(self):
        """Test that append_timestamp_to_name modifies and returns the same list object."""
        original_list = ["test", "folder"]
        result = append_timestamp_to_name(original_list)

        # The function should modify and return the same list object
        assert result is original_list

    def test_append_timestamp_to_name_string_with_special_characters(self):
        """Test that append_timestamp_to_name works with strings containing special characters."""
        from datetime import datetime

        mock_datetime = MagicMock()
        mock_datetime.now.return_value.strftime.return_value = (
            "my-folder_name_20240315_143022"
        )

        with patch("wa.utils.datetime", mock_datetime):
            result = append_timestamp_to_name("my-folder_name")
            assert result == "my-folder_name_20240315_143022"
