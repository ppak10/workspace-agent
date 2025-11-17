from mcp.server import FastMCP


def register_workspace_resources(app: FastMCP):
    from wa.models import Workspace

    @app.resource("workspace://")
    def workspaces() -> list[str] | None:
        from wa.workspace.list import list_workspaces

        return list_workspaces()

    @app.resource("workspace://{workspace}/")
    def workspace(workspace: str) -> Workspace | None:
        from wa.workspace.read import read_workspace

        return read_workspace(workspace)

    _ = (workspaces, workspace)
