import typer

from typing_extensions import Annotated


def register_mcp_uninstall(app: typer.Typer):
    @app.command(name="uninstall")
    def mcp_uninstall(
        client: Annotated[
            str,
            typer.Option("--client", help="Target client to install for."),
        ] = "claude-code",
    ) -> None:
        from wa.mcp.uninstall import uninstall

        uninstall(client=client)

    _ = app.command(name="uninstall")(mcp_uninstall)
    return mcp_uninstall
