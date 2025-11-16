import typer

from pathlib import Path
from rich import print as rprint
from typing_extensions import Annotated


def register_workspace_subfolder_create(app: typer.Typer):
    @app.command(name="create")
    def workspace_subfolder_create(
        workspace_name: str,
        subfolder_name: str,
        workspaces_folder_path: Path | None = None,
        force: Annotated[
            bool, typer.Option("--force", help="Overwrite existing subfolder")
        ] = False,
    ) -> None:
        """Create a folder to store data related to a workspace."""
        from wa.subfolder.create import create_workspace_subfolder

        try:
            workspace = create_workspace_subfolder(
                workspace_subfolder_name=subfolder_name,
                workspace_folder_name=workspace_name,
                workspaces_folder_path=workspaces_folder_path,
                force=force,
            )
            rprint(f"✅ Workspace subfolder created at: {workspace.path}")
        except FileExistsError as e:
            rprint(
                f"⚠️  [yellow]Workspace Subfolder: `{subfolder_name}` already exists.[/yellow]"
            )
            rprint("Use [cyan]--force[/cyan] to overwrite, or edit the existing file.")
            _ = typer.Exit()
        except:
            rprint("⚠️  [yellow]Unable to create workspace subfolder[/yellow]")
            _ = typer.Exit()

    return workspace_subfolder_create
