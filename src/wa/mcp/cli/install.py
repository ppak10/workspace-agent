import typer

from typing_extensions import Annotated
from pathlib import Path
from rich import print as rprint

from wa.mcp.install import install


def register_mcp_install(app: typer.Typer):
    @app.command(name="install")
    def mcp_install(
        client: Annotated[
            str, typer.Argument(help="Target client to install for.")
        ] = "claude-code",
        include_agent: Annotated[bool, typer.Option("--include-agent")] = False,
        project_path: Annotated[str | None, typer.Option("--project-path")] = None,
        dev: Annotated[bool, typer.Option("--dev")] = False,
    ) -> None:
        import wa

        # Determine project root path
        if dev:
            # /Users/ppak/GitHub/workspace-agent on mac mini
            wa_path = Path(wa.__file__).parents[2]
        elif project_path:
            wa_path = Path(project_path)
        else:
            # Path(wa.__file__) example:
            # /GitHub/workspace-agent/.venv/lib/python3.13/site-packages/wa
            # Going up 5 levels to get to the project root
            wa_path = Path(wa.__file__).parents[5]

        rprint(
            f"[bold green]Using `workspace-agent` packaged under project path:[/bold green] {wa_path}"
        )

        install(wa_path, client=client, include_agent=include_agent)

    _ = app.command(name="install")(mcp_install)
    return mcp_install
