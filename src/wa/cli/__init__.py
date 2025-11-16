from .__main__ import app
from .options import WorkspaceOption
from .version import register_version

from wa.mcp.cli import app as mcp_app
from wa.folder.cli import app as workspace_folder_app

# from wa.subfolder.cli import app as workspace_subfolder_app

__all__ = ["WorkspaceOption"]

app.add_typer(mcp_app, name="mcp", short_help="MCP Installation and Development tools")

app.add_typer(
    workspace_folder_app, name="folder", short_help="Manage workspace folders"
)

# app.add_typer(
#     workspace_subfolder_app,
#     name="subfolder",
#     short_help="Manage subfolders within a workspace"
# )

_ = register_version(app)

if __name__ == "__main__":
    app()
