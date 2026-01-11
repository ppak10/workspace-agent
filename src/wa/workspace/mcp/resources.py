import base64
import json
from pathlib import Path

from mcp.server import FastMCP


def register_workspace_resources(app: FastMCP):
    from wa import Workspace

    @app.resource("workspace://")
    def workspaces() -> list[str] | None:
        from wa.workspace.list import list_workspaces

        return list_workspaces()

    @app.resource("workspace://{workspace}/")
    def workspace(workspace: str) -> Workspace | None:
        from wa.workspace.read import read_workspace

        return read_workspace(workspace)

    @app.resource("workspace_file://{path}")
    def workspace_file(path: str) -> dict | str:
        """
        Read file content from the workspace based on file extension.
        Supports:
        - .png files: Returns base64 encoded image data with MIME type
        - .json files: Returns parsed JSON content
        """
        file_path = Path(path)

        # Check if file exists
        if not file_path.exists():
            return {"error": f"File not found: {path}"}

        if not file_path.is_file():
            return {"error": f"Path is not a file: {path}"}

        # Get file extension
        extension = file_path.suffix.lower()

        # Handle PNG images
        if extension == ".png":
            try:
                with open(file_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                return {
                    "type": "image",
                    "mimeType": "image/png",
                    "data": image_data,
                    "path": str(file_path),
                }
            except Exception as e:
                return {"error": f"Failed to read PNG file: {str(e)}"}

        # Handle JSON files
        elif extension == ".json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                return {
                    "type": "json",
                    "data": json_data,
                    "path": str(file_path),
                }
            except json.JSONDecodeError as e:
                return {"error": f"Invalid JSON file: {str(e)}"}
            except Exception as e:
                return {"error": f"Failed to read JSON file: {str(e)}"}

        # Unsupported file type
        else:
            return {
                "error": f"Unsupported file extension: {extension}. Supported types: .png, .json"
            }

    _ = (workspaces, workspace, workspace_file)
