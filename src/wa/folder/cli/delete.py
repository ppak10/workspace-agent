import typer

from pathlib import Path
from rich import print as rprint
from typing_extensions import Annotated


def register_workspace_folder_delete(app: typer.Typer):
    @app.command(name="delete")
    def workspace_folder_delete(
        name: str,
        workspaces_folder_path: Path | None = None,
        force: Annotated[
            bool, typer.Option("--force", help="Overwrite existing workspace")
        ] = False,
    ) -> None:
        """Delete a workspace folder and its associated subfolders."""
        from wa.folder.delete import delete_workspace_folder

        try:
            workspace_path = delete_workspace_folder(
                name=name, workspaces_folder_path=workspaces_folder_path, force=force
            )
            rprint(f"✅ Workspace deleted at: {workspace_path}")
        except FileExistsError as e:
            rprint(f"⚠️  [yellow]Workspace: `{name}` has subfolders.[/yellow]")
            rprint("Use [cyan]--force[/cyan] to delete workspace and its subfolders.")
            _ = typer.Exit()
        except:
            rprint("⚠️  [yellow]Unable to delete workspace directory[/yellow]")
            _ = typer.Exit()

    return workspace_folder_delete
