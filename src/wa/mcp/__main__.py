from mcp.server.fastmcp import FastMCP

from wa.folder.mcp import (
    register_workspace_folder_resources,
    register_workspace_folder_tools,
)

app = FastMCP(name="workspace-agent")

_ = register_workspace_folder_resources(app)
_ = register_workspace_folder_tools(app)


def main():
    """Entry point for the direct execution server."""
    app.run()


if __name__ == "__main__":
    main()
