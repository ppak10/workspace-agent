import typer

from pathlib import Path
from rich import print as rprint


def register_workspace_folder_read(app: typer.Typer):
    @app.command(name="read")
    def workspace_folder_read(
        name: str,
        workspaces_folder_path: Path | None = None,
    ) -> None:
        """Read the contents workspace folder and its associated subfolders."""
        from wa.folder.read import read_workspace_folder

        try:
            workspace = read_workspace_folder(
                name=name, workspaces_folder_path=workspaces_folder_path
            )
            rprint(workspace)
        except:
            rprint(f"⚠️  [yellow]Unable to read workspace: {name}[/yellow]")
            _ = typer.Exit()

    return workspace_folder_read
