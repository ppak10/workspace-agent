from mcp.server import FastMCP

from pathlib import Path
from typing import Literal, Union

Method = Literal["list", "create", "read"]


def register_workspace_tools(app: FastMCP):
    from wa.mcp.types import ToolSuccess, ToolError
    from wa.mcp.utils import tool_success, tool_error
    from wa import Workspace, WorkspaceFolder

    @app.tool(
        title="Workspace Management",
        description="List all workspace folders or create and read a given workspace",
        structured_output=True,
    )
    def workspace_management(
        workspace_name: str | None = None,
        folder_name: list[str] = [],
        method: Method = "list",
        include_files: bool = False,
        force: bool = False,
    ) -> Union[
        ToolSuccess[Path | Workspace | WorkspaceFolder | list[str] | None], ToolError
    ]:
        """
        Manage workspace folders.

        Args:
            workspace_name: Folder name of workspace, lists all workspace folders if left empty.
            folder_name: List of folder names, ordered by path heirarchy (i.e. 'workspace/folder/subfolder' is ["workspace", "folder", "subfolder"]).
            method: Either 'list', 'create', or 'read'. Requires 'workspace_name' to be provided.
            include_files: Include file names for 'read' method for workspace folder.
            force: Utilized for either 'create' or 'delete methods.
        """
        from wa.workspace.list import list_workspaces
        from wa.workspace.create import create_workspace, create_workspace_folder
        from wa.workspace.read import read_workspace, read_workspace_folder

        # from wa.workspace.delete import delete_workspace

        try:
            if method == "list":
                # if workspace_name is None:
                workspace_folder_names = list_workspaces()
                return tool_success(workspace_folder_names)

            if workspace_name is not None:
                if method == "create":
                    if len(folder_name) > 0:
                        folder = create_workspace_folder(
                            name_or_path=folder_name,
                            workspace_name=workspace_name,
                            force=force,
                        )
                        return tool_success(folder)
                    else:
                        workspace = create_workspace(
                            workspace_name=workspace_name,
                            force=force,
                        )
                        return tool_success(workspace)

                elif method == "read":
                    if len(folder_name) > 0:
                        folder = read_workspace_folder(
                            workspace_folder_name=folder_name,
                            workspace_name=workspace_name,
                            include_files=include_files,
                        )
                        return tool_success(folder)
                    else:
                        workspace = read_workspace(
                            workspace_name=workspace_name,
                            include_files=include_files,
                        )
                        return tool_success(workspace)

                # TODO: Turn back on when granular delete is implemented
                # Also needs for the update method to be implement to know which
                # folders have been deleted.
                # elif method == "delete":
                #     workspace_path = delete_workspace(
                #         workspace_name=workspace_name,
                #         force=force,
                #     )
                #     return tool_success(workspace_path)

                else:
                    return tool_error(
                        f"Unknown method: {method}.",
                        "UNKNOWN_METHOD",
                        workspace_name=workspace_name,
                    )
            else:
                return tool_error(
                    f"Workspace name not provided.",
                    "INVALID_WORKSPACE_NAME",
                    workspace_name=workspace_name,
                )

        except PermissionError as e:
            return tool_error(
                "Encountered permission error with workspace folder management.",
                "PERMISSION_DENIED",
                workspace_name=workspace_name,
                exception_type=type(e).__name__,
            )
        except FileExistsError as e:
            return tool_error(
                f"Files exist within workspace {workspace_name}, try again with `force` if you intend to overwrite or delete.",
                "FILE_EXISTS",
                workspace_name=workspace_name,
                exception_type=type(e).__name__,
            )
        except FileNotFoundError as e:
            return tool_error(
                f"File or folder within workspace {workspace_name} was not found.",
                "FILE_NOT_FOUND",
                workspace_name=workspace_name,
                exception_type=type(e).__name__,
            )
        except Exception as e:
            return tool_error(
                "Workspace folder management operation failed",
                "WORKSPACE_FOLDER_FAILED",
                workspace_name=workspace_name,
                exception_type=type(e).__name__,
                exception_message=str(e),
            )

    @app.tool(
        title="Workspace File",
        description="Read or copy file content from the workspace (supports .png and .json files for read, all file types for copy)",
        structured_output=True,
    )
    def workspace_file(
        path: str,
        method: Literal["read", "copy"] = "read",
        destination: str | None = None,
    ) -> Union[ToolSuccess[dict | str], ToolError]:
        """
        Read or copy file content from the workspace.

        Args:
            path: Absolute path to the source file.
            method: Either 'read' or 'copy'.
            destination: Required for 'copy' method. Absolute path to destination (file or directory).

        Returns:
            For 'read' method:
                - .png files: {"type": "image", "mimeType": "image/png", "data": "<base64>", "path": "<path>"}
                - .json files: {"type": "json", "data": <json_object>, "path": "<path>"}
            For 'copy' method:
                - {"source": "<source_path>", "destination": "<destination_path>", "copied": true}
        """
        import base64
        import json
        import shutil
        from pathlib import Path

        try:
            file_path = Path(path)

            # Check if file exists
            if not file_path.exists():
                return tool_error(
                    f"File not found: {path}",
                    "FILE_NOT_FOUND",
                    path=path,
                )

            if not file_path.is_file():
                return tool_error(
                    f"Path is not a file: {path}",
                    "INVALID_PATH",
                    path=path,
                )

            # Handle copy method
            if method == "copy":
                if destination is None:
                    return tool_error(
                        "Destination path is required for copy method.",
                        "MISSING_DESTINATION",
                        path=path,
                    )

                dest_path = Path(destination)

                # If destination is a directory, append the source filename
                if dest_path.is_dir():
                    dest_path = dest_path / file_path.name
                else:
                    # Ensure parent directory exists
                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy2(file_path, dest_path)

                return tool_success(
                    {
                        "source": str(file_path),
                        "destination": str(dest_path),
                        "copied": True,
                    }
                )

            # Handle read method
            elif method == "read":
                # Get file extension
                extension = file_path.suffix.lower()

                # Handle PNG images
                if extension == ".png":
                    with open(file_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode("utf-8")
                    return tool_success(
                        {
                            "type": "image",
                            "mimeType": "image/png",
                            "data": image_data,
                            "path": str(file_path),
                        }
                    )

                # Handle JSON files
                elif extension == ".json":
                    with open(file_path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                    return tool_success(
                        {
                            "type": "json",
                            "data": json_data,
                            "path": str(file_path),
                        }
                    )

                # Unsupported file type for read
                else:
                    return tool_error(
                        f"Unsupported file extension for read: {extension}. Supported types: .png, .json",
                        "UNSUPPORTED_FILE_TYPE",
                        path=path,
                        extension=extension,
                    )

            # Unknown method
            else:
                return tool_error(
                    f"Unknown method: {method}. Supported methods: 'read', 'copy'",
                    "UNKNOWN_METHOD",
                    path=path,
                    method=method,
                )

        except PermissionError as e:
            return tool_error(
                "Permission denied when accessing file.",
                "PERMISSION_DENIED",
                path=path,
                exception_type=type(e).__name__,
            )
        except json.JSONDecodeError as e:
            return tool_error(
                f"Invalid JSON file: {str(e)}",
                "INVALID_JSON",
                path=path,
                exception_type=type(e).__name__,
            )
        except Exception as e:
            return tool_error(
                f"Failed to process file: {str(e)}",
                "FILE_OPERATION_FAILED",
                path=path,
                exception_type=type(e).__name__,
                exception_message=str(e),
            )

    _ = (workspace_management, workspace_file)
