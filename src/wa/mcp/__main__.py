from mcp.server.fastmcp import FastMCP

from wa.workspace.mcp import (
    register_workspace_resources,
    register_workspace_tools,
)

app = FastMCP(name="workspace-agent")

_ = register_workspace_resources(app)
_ = register_workspace_tools(app)


def main():
    """Entry point for the direct execution server."""
    app.run()


if __name__ == "__main__":
    main()
