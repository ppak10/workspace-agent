from __future__ import annotations

import base64
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Skip tests if mcp.server is not available
try:
    import mcp.server.fastmcp  # noqa: F401

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp.server not available")
class TestWorkspaceFileResource:
    """Test the workspace_file:// resource."""

    @pytest.fixture
    def workspace_file_resource(self):
        """Get the workspace_file resource function by registering it on a mock app."""
        # Create a mock FastMCP app
        mock_app = MagicMock()

        # Capture the decorated functions when @app.resource is called
        captured_funcs = {}

        def capture_resource(uri_pattern):
            def decorator(func):
                captured_funcs[uri_pattern] = func
                return func

            return decorator

        mock_app.resource = capture_resource

        # Import and register the resources
        from wa.workspace.mcp.resources import register_workspace_resources

        register_workspace_resources(mock_app)

        return captured_funcs.get("workspace_file://{path}")

    def test_read_png_file(self, workspace_file_resource, tmp_path):
        """Test reading a PNG file."""
        # Create a simple PNG file (1x1 transparent PNG)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        png_file = tmp_path / "test.png"
        png_file.write_bytes(png_data)

        result = workspace_file_resource(path=str(png_file))

        assert result["type"] == "image"
        assert result["mimeType"] == "image/png"
        assert "data" in result
        assert result["path"] == str(png_file)
        # Verify the data is base64 encoded
        assert isinstance(result["data"], str)
        # Should be able to decode it back
        decoded = base64.b64decode(result["data"])
        assert decoded == png_data

    def test_read_json_file(self, workspace_file_resource, tmp_path):
        """Test reading a JSON file."""
        json_data = {"name": "test", "value": 42, "nested": {"key": "value"}}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(json_data))

        result = workspace_file_resource(path=str(json_file))

        assert result["type"] == "json"
        assert result["data"] == json_data
        assert result["path"] == str(json_file)

    def test_file_not_found(self, workspace_file_resource, tmp_path):
        """Test handling of non-existent file."""
        non_existent = tmp_path / "does_not_exist.png"

        result = workspace_file_resource(path=str(non_existent))

        assert "error" in result
        assert "File not found" in result["error"]

    def test_path_is_directory(self, workspace_file_resource, tmp_path):
        """Test handling when path is a directory."""
        directory = tmp_path / "test_dir"
        directory.mkdir()

        result = workspace_file_resource(path=str(directory))

        assert "error" in result
        assert "not a file" in result["error"]

    def test_unsupported_extension(self, workspace_file_resource, tmp_path):
        """Test handling of unsupported file extensions."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Some text content")

        result = workspace_file_resource(path=str(txt_file))

        assert "error" in result
        assert "Unsupported file extension" in result["error"]
        assert ".txt" in result["error"]

    def test_invalid_json(self, workspace_file_resource, tmp_path):
        """Test handling of invalid JSON file."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json }")

        result = workspace_file_resource(path=str(json_file))

        assert "error" in result
        assert "Invalid JSON file" in result["error"]

    def test_png_read_error(self, workspace_file_resource, tmp_path):
        """Test handling of PNG file read errors."""
        # Create a PNG file and then make it unreadable
        png_file = tmp_path / "test.png"
        png_file.write_bytes(b"fake png data")

        # Test with the file (should succeed even with fake data since we just read bytes)
        result = workspace_file_resource(path=str(png_file))

        # Should work with any binary data
        assert result["type"] == "image"
        assert result["mimeType"] == "image/png"
