from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch
import importlib.util

import pytest

from wa.utils import get_project_root, create_pathname


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
