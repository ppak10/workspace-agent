from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from wa.mcp.types import ToolError, ToolSuccess, T


class TestToolError:
    """Test the ToolError Pydantic model."""

    def test_tool_error_basic_creation(self):
        """Test creating a basic ToolError."""
        error = ToolError(error="Something went wrong", error_code="ERR_001")
        assert error.success is False
        assert error.error == "Something went wrong"
        assert error.error_code == "ERR_001"
        assert error.details == {}

    def test_tool_error_with_details(self):
        """Test creating ToolError with additional details."""
        error = ToolError(
            error="File not found",
            error_code="ERR_FILE_NOT_FOUND",
            details={"path": "/some/path", "line": 42},
        )
        assert error.success is False
        assert error.error == "File not found"
        assert error.error_code == "ERR_FILE_NOT_FOUND"
        assert error.details == {"path": "/some/path", "line": 42}

    def test_tool_error_success_always_false(self):
        """Test that success field is always False for ToolError."""
        error = ToolError(error="Error", error_code="ERR")
        assert error.success is False

    def test_tool_error_empty_details_default(self):
        """Test that details defaults to empty dict."""
        error = ToolError(error="Error", error_code="ERR")
        assert error.details == {}
        assert isinstance(error.details, dict)

    def test_tool_error_serialization(self):
        """Test ToolError serialization to dict."""
        error = ToolError(
            error="Invalid input",
            error_code="INVALID_INPUT",
            details={"field": "username"},
        )
        serialized = error.model_dump()
        assert serialized == {
            "success": False,
            "error": "Invalid input",
            "error_code": "INVALID_INPUT",
            "details": {"field": "username"},
        }

    def test_tool_error_json_serialization(self):
        """Test ToolError JSON serialization."""
        error = ToolError(error="Test error", error_code="TEST")
        json_str = error.model_dump_json()
        assert "success" in json_str
        assert "false" in json_str.lower()
        assert "Test error" in json_str
        assert "TEST" in json_str

    def test_tool_error_required_fields(self):
        """Test that error and error_code are required."""
        with pytest.raises(ValidationError):
            ToolError()  # Missing required fields

    def test_tool_error_missing_error_field(self):
        """Test that error field is required."""
        with pytest.raises(ValidationError):
            ToolError(error_code="ERR")  # Missing error

    def test_tool_error_missing_error_code_field(self):
        """Test that error_code field is required."""
        with pytest.raises(ValidationError):
            ToolError(error="Error message")  # Missing error_code

    def test_tool_error_details_can_be_nested(self):
        """Test that details can contain nested structures."""
        error = ToolError(
            error="Complex error",
            error_code="COMPLEX",
            details={"nested": {"level1": {"level2": "value"}}, "list": [1, 2, 3]},
        )
        assert error.details["nested"]["level1"]["level2"] == "value"
        assert error.details["list"] == [1, 2, 3]


class TestToolSuccess:
    """Test the ToolSuccess Pydantic model."""

    def test_tool_success_basic_creation_string(self):
        """Test creating ToolSuccess with string data."""
        success = ToolSuccess[str](data="Operation completed")
        assert success.success is True
        assert success.data == "Operation completed"

    def test_tool_success_basic_creation_dict(self):
        """Test creating ToolSuccess with dict data."""
        data = {"result": "OK", "count": 42}
        success = ToolSuccess[dict](data=data)
        assert success.success is True
        assert success.data == data

    def test_tool_success_basic_creation_list(self):
        """Test creating ToolSuccess with list data."""
        data = ["item1", "item2", "item3"]
        success = ToolSuccess[list](data=data)
        assert success.success is True
        assert success.data == data

    def test_tool_success_success_always_true(self):
        """Test that success field is always True for ToolSuccess."""
        success = ToolSuccess[str](data="test")
        assert success.success is True

    def test_tool_success_serialization_string(self):
        """Test ToolSuccess serialization with string data."""
        success = ToolSuccess[str](data="hello")
        serialized = success.model_dump()
        assert serialized == {"success": True, "data": "hello"}

    def test_tool_success_serialization_complex_data(self):
        """Test ToolSuccess serialization with complex data."""
        data = {"workspace": "test", "folders": ["a", "b"], "created": True}
        success = ToolSuccess[dict](data=data)
        serialized = success.model_dump()
        assert serialized == {"success": True, "data": data}

    def test_tool_success_json_serialization(self):
        """Test ToolSuccess JSON serialization."""
        success = ToolSuccess[str](data="test data")
        json_str = success.model_dump_json()
        assert "success" in json_str
        assert "true" in json_str.lower()
        assert "test data" in json_str

    def test_tool_success_required_data_field(self):
        """Test that data field is required."""
        with pytest.raises(ValidationError):
            ToolSuccess[str]()  # Missing data

    def test_tool_success_with_none_data(self):
        """Test ToolSuccess with None as data."""
        success = ToolSuccess[None](data=None)
        assert success.success is True
        assert success.data is None

    def test_tool_success_with_integer_data(self):
        """Test ToolSuccess with integer data."""
        success = ToolSuccess[int](data=12345)
        assert success.success is True
        assert success.data == 12345

    def test_tool_success_with_boolean_data(self):
        """Test ToolSuccess with boolean data."""
        success = ToolSuccess[bool](data=True)
        assert success.success is True
        assert success.data is True

    def test_tool_success_generic_type_preserved(self):
        """Test that generic type information is preserved."""
        success_str = ToolSuccess[str](data="text")
        success_int = ToolSuccess[int](data=42)

        assert isinstance(success_str.data, str)
        assert isinstance(success_int.data, int)

    def test_tool_success_with_nested_dict(self):
        """Test ToolSuccess with nested dict structure."""
        custom_data = {"value": "test", "nested": {"level1": {"level2": "deep"}}}
        success = ToolSuccess[dict](data=custom_data)
        assert success.success is True
        assert success.data["value"] == "test"
        assert success.data["nested"]["level1"]["level2"] == "deep"


class TestToolResponse:
    """Test the ToolResponse type alias."""

    def test_tool_response_can_be_success(self):
        """Test that ToolResponse can hold ToolSuccess."""
        response: Any = ToolSuccess[str](data="success")
        assert isinstance(response, ToolSuccess)
        assert response.success is True

    def test_tool_response_can_be_error(self):
        """Test that ToolResponse can hold ToolError."""
        response: Any = ToolError(error="Failed", error_code="FAIL")
        assert isinstance(response, ToolError)
        assert response.success is False

    def test_tool_response_discriminated_by_success_field(self):
        """Test that ToolResponse can be discriminated by success field."""
        success_response: Any = ToolSuccess[str](data="ok")
        error_response: Any = ToolError(error="error", error_code="ERR")

        # Can discriminate based on success field
        if success_response.success:
            assert hasattr(success_response, "data")
        else:
            assert hasattr(success_response, "error")

        if not error_response.success:
            assert hasattr(error_response, "error")
            assert hasattr(error_response, "error_code")
