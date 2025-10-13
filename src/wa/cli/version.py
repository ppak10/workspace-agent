import importlib.metadata
import typer

from rich import print as rprint


def register_version(app: typer.Typer):
    @app.command()
    def version() -> None:
        """Show the installed version of `workspace-agent` package."""
        try:
            version = importlib.metadata.version("workspace-agent")
            rprint(f"✅ workspace-agent version {version}")
        except importlib.metadata.PackageNotFoundError:
            rprint(
                "⚠️  [yellow]workspace-agent version unknown (package not installed)[/yellow]"
            )
            raise typer.Exit()

    return version
