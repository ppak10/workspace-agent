import typer

from pathlib import Path
from rich import print as rprint
from typing_extensions import Annotated


def register_read(app: typer.Typer):
    @app.command(name="read")
    def read(
        workspace_name: str,
        folder_name: Annotated[list[str], typer.Argument()] = [],
        workspaces_path: Path | None = None,
        include_files: Annotated[
            bool, typer.Option("--files", help="Include list of files in the folder")
        ] = False,
    ) -> None:
        """Read the contents workspace folder and its associated subfolders."""
        from wa.workspace.read import read_workspace, read_workspace_folder

        if len(folder_name) > 0:
            try:
                folder = read_workspace_folder(
                    workspace_folder_name=folder_name,
                    workspace_name=workspace_name,
                    workspaces_path=workspaces_path,
                    include_files=include_files,
                )
                rprint(folder)
            except FileNotFoundError as e:
                rprint(e)
            except:
                rprint(
                    f"⚠️  [yellow]Unable to read workspace subfolder: {folder_name}[/yellow]"
                )
        else:
            try:
                workspace = read_workspace(
                    workspace_name=workspace_name, workspaces_path=workspaces_path
                )
                rprint(workspace)
            except:
                rprint(
                    f"⚠️  [yellow]Unable to read workspace: {workspace_name}[/yellow]"
                )
                _ = typer.Exit()

    return read
