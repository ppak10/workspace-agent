from mcp.server import FastMCP


def register_workspace_folder_resources(app: FastMCP):
    from wa.models import Workspace

    @app.resource("workspace://")
    def workspace_folders() -> list[str] | None:
        from wa.folder.list import list_workspace_folders

        return list_workspace_folders()

    @app.resource("workspace://{workspace}/")
    def workspace_folder(workspace: str) -> Workspace | None:
        from wa.folder.read import read_workspace_folder

        return read_workspace_folder(workspace)

    _ = (workspace_folders, workspace_folder)
