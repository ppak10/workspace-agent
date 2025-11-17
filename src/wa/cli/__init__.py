from .__main__ import app
from .options import WorkspaceOption
from .version import register_version

from wa.mcp.cli import app as mcp_app
from wa.workspace.cli import (
    register_create,
    register_delete,
    register_list,
    register_read,
)

__all__ = ["WorkspaceOption"]

app.add_typer(mcp_app, name="mcp", short_help="MCP Installation and Development tools")

_ = register_create(app)
_ = register_delete(app)
_ = register_read(app)
_ = register_list(app)
_ = register_version(app)

if __name__ == "__main__":
    app()
