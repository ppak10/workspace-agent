import typer

from pathlib import Path
from rich import print as rprint
from typing_extensions import Annotated


def register_workspace_subfolder_read(app: typer.Typer):
    @app.command(name="read")
    def workspace_subfolder_read(
        workspace_name: str,
        subfolder_name: Annotated[list[str], typer.Argument()],
        workspaces_folder_path: Path | None = None,
    ) -> None:
        """Read the contents workspace subfolder and its associated subfolders."""
        from wa.subfolder.read import read_workspace_subfolder

        try:
            subfolder = read_workspace_subfolder(
                workspace_subfolder_name=subfolder_name,
                workspace_folder_name=workspace_name,
                workspaces_folder_path=workspaces_folder_path,
            )
            rprint(subfolder)
        except FileNotFoundError as e:
            rprint(e)
        except:
            rprint(
                f"⚠️  [yellow]Unable to read workspace subfolder: {subfolder_name}[/yellow]"
            )
            _ = typer.Exit()

    return workspace_subfolder_read
