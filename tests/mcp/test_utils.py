from __future__ import annotations

import pytest

from wa.mcp.utils import tool_error, tool_success
from wa.mcp.types import ToolError, ToolSuccess


class TestToolError:
    """Test the tool_error convenience function."""

    def test_tool_error_basic_creation(self):
        """Test creating a basic error using tool_error function."""
        error = tool_error(message="Something went wrong", code="ERR_001")

        assert isinstance(error, ToolError)
        assert error.success is False
        assert error.error == "Something went wrong"
        assert error.error_code == "ERR_001"
        assert error.details == {}

    def test_tool_error_with_details(self):
        """Test creating error with additional details."""
        error = tool_error(
            message="File not found",
            code="ERR_FILE_NOT_FOUND",
            path="/some/path",
            line=42,
        )

        assert isinstance(error, ToolError)
        assert error.error == "File not found"
        assert error.error_code == "ERR_FILE_NOT_FOUND"
        assert error.details == {"path": "/some/path", "line": 42}

    def test_tool_error_with_multiple_details(self):
        """Test creating error with multiple detail fields."""
        error = tool_error(
            message="Validation failed",
            code="VALIDATION_ERROR",
            field="username",
            expected="string",
            received="integer",
            value=123,
        )

        assert error.error == "Validation failed"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details["field"] == "username"
        assert error.details["expected"] == "string"
        assert error.details["received"] == "integer"
        assert error.details["value"] == 123

    def test_tool_error_details_empty_by_default(self):
        """Test that details is empty when no kwargs provided."""
        error = tool_error(message="Error", code="ERR")

        assert error.details == {}

    def test_tool_error_returns_tool_error_instance(self):
        """Test that tool_error returns ToolError instance."""
        error = tool_error(message="Test", code="TEST")

        assert isinstance(error, ToolError)
        assert hasattr(error, "success")
        assert hasattr(error, "error")
        assert hasattr(error, "error_code")
        assert hasattr(error, "details")

    def test_tool_error_success_is_false(self):
        """Test that success field is always False."""
        error = tool_error(message="Error", code="ERR")

        assert error.success is False

    def test_tool_error_with_nested_details(self):
        """Test creating error with nested detail structures."""
        error = tool_error(
            message="Complex error",
            code="COMPLEX",
            metadata={"user": "john", "timestamp": "2024-01-01"},
            context={"operation": "delete", "resource": "workspace"},
        )

        assert error.details["metadata"] == {"user": "john", "timestamp": "2024-01-01"}
        assert error.details["context"] == {
            "operation": "delete",
            "resource": "workspace",
        }

    def test_tool_error_serializable(self):
        """Test that tool_error result is serializable."""
        error = tool_error(
            message="API Error",
            code="API_ERR",
            status_code=404,
            endpoint="/api/v1/resource",
        )

        serialized = error.model_dump()
        assert serialized["success"] is False
        assert serialized["error"] == "API Error"
        assert serialized["error_code"] == "API_ERR"
        assert serialized["details"]["status_code"] == 404
        assert serialized["details"]["endpoint"] == "/api/v1/resource"


class TestToolSuccess:
    """Test the tool_success convenience function."""

    def test_tool_success_with_string_data(self):
        """Test creating success with string data."""
        success = tool_success(data="Operation completed")

        assert isinstance(success, ToolSuccess)
        assert success.success is True
        assert success.data == "Operation completed"

    def test_tool_success_with_dict_data(self):
        """Test creating success with dict data."""
        data = {"workspace": "my_workspace", "folders": ["folder1", "folder2"]}
        success = tool_success(data=data)

        assert isinstance(success, ToolSuccess)
        assert success.success is True
        assert success.data == data

    def test_tool_success_with_list_data(self):
        """Test creating success with list data."""
        data = ["item1", "item2", "item3"]
        success = tool_success(data=data)

        assert isinstance(success, ToolSuccess)
        assert success.success is True
        assert success.data == data

    def test_tool_success_with_integer_data(self):
        """Test creating success with integer data."""
        success = tool_success(data=42)

        assert success.success is True
        assert success.data == 42

    def test_tool_success_with_boolean_data(self):
        """Test creating success with boolean data."""
        success = tool_success(data=True)

        assert success.success is True
        assert success.data is True

    def test_tool_success_with_none_data(self):
        """Test creating success with None data."""
        success = tool_success(data=None)

        assert success.success is True
        assert success.data is None

    def test_tool_success_returns_tool_success_instance(self):
        """Test that tool_success returns ToolSuccess instance."""
        success = tool_success(data="test")

        assert isinstance(success, ToolSuccess)
        assert hasattr(success, "success")
        assert hasattr(success, "data")

    def test_tool_success_success_is_true(self):
        """Test that success field is always True."""
        success = tool_success(data="anything")

        assert success.success is True

    def test_tool_success_with_complex_nested_data(self):
        """Test creating success with complex nested data."""
        data = {
            "workspace": {
                "name": "test",
                "folders": [
                    {"name": "folder1", "files": ["a.txt", "b.txt"]},
                    {"name": "folder2", "files": ["c.txt"]},
                ],
            },
            "metadata": {"created": "2024-01-01", "author": "user"},
        }
        success = tool_success(data=data)

        assert success.success is True
        assert success.data == data
        assert success.data["workspace"]["folders"][0]["files"] == ["a.txt", "b.txt"]

    def test_tool_success_serializable(self):
        """Test that tool_success result is serializable."""
        data = {"result": "OK", "count": 5}
        success = tool_success(data=data)

        serialized = success.model_dump()
        assert serialized["success"] is True
        assert serialized["data"] == data

    def test_tool_success_with_empty_dict(self):
        """Test creating success with empty dict."""
        success = tool_success(data={})

        assert success.success is True
        assert success.data == {}

    def test_tool_success_with_empty_list(self):
        """Test creating success with empty list."""
        success = tool_success(data=[])

        assert success.success is True
        assert success.data == []


class TestToolErrorAndSuccessIntegration:
    """Test interaction between tool_error and tool_success."""

    def test_error_and_success_have_different_success_values(self):
        """Test that error and success have opposite success values."""
        error = tool_error(message="Failed", code="FAIL")
        success = tool_success(data="OK")

        assert error.success is False
        assert success.success is True

    def test_error_and_success_can_be_discriminated(self):
        """Test that error and success can be distinguished by success field."""

        def process_response(response):
            if response.success:
                return f"Success: {response.data}"
            else:
                return f"Error: {response.error}"

        error_resp = tool_error(message="Failed", code="ERR")
        success_resp = tool_success(data="Done")

        assert process_response(error_resp) == "Error: Failed"
        assert process_response(success_resp) == "Success: Done"

    def test_both_are_serializable_to_consistent_format(self):
        """Test that both error and success serialize to consistent format."""
        error = tool_error(message="Error", code="ERR", extra="info")
        success = tool_success(data={"result": "ok"})

        error_dict = error.model_dump()
        success_dict = success.model_dump()

        # Both should have success field
        assert "success" in error_dict
        assert "success" in success_dict

        # Error should have error-specific fields
        assert "error" in error_dict
        assert "error_code" in error_dict
        assert "details" in error_dict

        # Success should have data field
        assert "data" in success_dict
