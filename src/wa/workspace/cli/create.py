import typer

from pathlib import Path
from rich import print as rprint
from typing_extensions import Annotated


def register_create(app: typer.Typer):
    @app.command(name="create")
    def create(
        workspace_name: str,
        folder_name: Annotated[list[str], typer.Argument()] = [],
        workspaces_path: Path | None = None,
        force: Annotated[
            bool, typer.Option("--force", help="Overwrite existing subfolder")
        ] = False,
    ) -> None:
        """Create a folder to store data related to a workspace."""
        from wa.workspace.create import create_workspace, create_workspace_folder

        if len(folder_name) > 0:
            try:
                folder = create_workspace_folder(
                    workspace_folder_name=folder_name,
                    workspace_name=workspace_name,
                    workspaces_path=workspaces_path,
                    force=force,
                )
                rprint(f"✅ Workspace folder created at: {folder.path}")
            except FileExistsError:
                rprint(
                    f"⚠️  [yellow]Workspace folder: `{folder_name}` already exists.[/yellow]"
                )
                rprint(
                    "Use [cyan]--force[/cyan] to overwrite, or edit the existing file."
                )
                _ = typer.Exit()
            except:
                rprint("⚠️  [yellow]Unable to create workspace folder[/yellow]")
                _ = typer.Exit()
        else:
            try:
                workspace = create_workspace(
                    workspace_name=workspace_name,
                    workspaces_path=workspaces_path,
                    force=force,
                )
                rprint(f"✅ Workspace created at: {workspace.path}")
            except FileExistsError as e:
                rprint(
                    f"⚠️  [yellow]Workspace: `{workspace_name}` already exists.[/yellow]"
                )
                rprint(
                    "Use [cyan]--force[/cyan] to overwrite, or edit the existing file."
                )
                _ = typer.Exit()
            except:
                rprint("⚠️  [yellow]Unable to create workspace directory[/yellow]")
                _ = typer.Exit()

    return create
