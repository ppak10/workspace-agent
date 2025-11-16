import typer

from pathlib import Path
from rich import print as rprint
from typing_extensions import Annotated


def register_workspace_folder_create(app: typer.Typer):
    @app.command(name="create")
    def workspace_folder_create(
        name: str,
        workspaces_folder_path: Path | None = None,
        force: Annotated[
            bool, typer.Option("--force", help="Overwrite existing workspace")
        ] = False,
    ) -> None:
        """Create a folder to store data related to a workspace."""
        from wa.folder.create import create_workspace_folder

        try:
            workspace = create_workspace_folder(
                name=name, workspaces_folder_path=workspaces_folder_path, force=force
            )
            rprint(f"✅ Workspace created at: {workspace.path}")
        except FileExistsError as e:
            rprint(f"⚠️  [yellow]Workspace: `{name}` already exists.[/yellow]")
            rprint("Use [cyan]--force[/cyan] to overwrite, or edit the existing file.")
            _ = typer.Exit()
        except:
            rprint("⚠️  [yellow]Unable to create workspace directory[/yellow]")
            _ = typer.Exit()

    return workspace_folder_create
