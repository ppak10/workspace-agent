from mcp.server import FastMCP

from pathlib import Path
from typing import Literal, Union

Method = Literal["create", "read", "delete"]


def register_workspace_tools(app: FastMCP):
    from wa.mcp.types import ToolSuccess, ToolError
    from wa.mcp.utils import tool_success, tool_error
    from wa.models import Workspace

    @app.tool(
        title="Workspace Management",
        description="List all workspace folders or create, read, and delete a given workspace",
        structured_output=True,
    )
    def workspace_folder(
        workspace_name: str | None = None,
        method: Method = "read",
        force: bool = False,
    ) -> Union[ToolSuccess[Path | Workspace | list[str] | None], ToolError]:
        """
        Manage workspace folders.

        Args:
            workspace_name: Folder name of workspace, lists all workspace folders if left empty.
            method: Either 'create', 'read', or 'delete'. Requires 'workspace_name' to be provided.
            force: Utilized for either 'create' or 'delete methods.
        """
        from wa.workspace.list import list_workspaces
        from wa.workspace.create import create_workspace
        from wa.workspace.read import read_workspace
        from wa.workspace.delete import delete_workspace

        try:
            if workspace_name is None:
                workspace_folder_names = list_workspaces()
                return tool_success(workspace_folder_names)

            elif method == "create":
                workspace = create_workspace(
                    workspace_name=workspace_name,
                    force=force,
                )
                return tool_success(workspace)

            elif method == "read":
                workspace = read_workspace(workspace_name=workspace_name)
                return tool_success(workspace)

            elif method == "delete":
                workspace_path = delete_workspace(
                    workspace_name=workspace_name,
                    force=force,
                )
                return tool_success(workspace_path)

            else:
                return tool_error(
                    f"Unknown method: {method}.",
                    "UNKNOWN_METHOD",
                    workspace_name=workspace_name,
                    exception_type=type(e).__name__,
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

    _ = workspace_folder
