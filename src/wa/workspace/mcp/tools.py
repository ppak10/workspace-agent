from mcp.server import FastMCP

from pathlib import Path
from typing import Literal, Union

Method = Literal["list", "create", "read"]


def register_workspace_tools(app: FastMCP):
    from wa.mcp.types import ToolSuccess, ToolError
    from wa.mcp.utils import tool_success, tool_error
    from wa.models import Workspace, WorkspaceFolder

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
                            workspace_folder_name=folder_name,
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

    _ = workspace_management
