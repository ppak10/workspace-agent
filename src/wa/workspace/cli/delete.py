import typer

from pathlib import Path
from rich import print as rprint
from typing_extensions import Annotated


def register_delete(app: typer.Typer):
    @app.command(name="delete")
    def delete(
        workspace_name: str,
        workspaces_path: Path | None = None,
        force: Annotated[
            bool, typer.Option("--force", help="Overwrite existing workspace")
        ] = False,
    ) -> None:
        """Delete a workspace folder and its associated subfolders."""
        from wa.workspace.delete import delete_workspace

        try:
            workspace_path = delete_workspace(
                workspace_name=workspace_name,
                workspaces_path=workspaces_path,
                force=force,
            )
            rprint(f"✅ Workspace deleted at: {workspace_path}")
        except FileExistsError as e:
            rprint(f"⚠️  [yellow]Workspace: `{workspace_name}` has folders.[/yellow]")
            rprint("Use [cyan]--force[/cyan] to delete workspace and its subfolders.")
            _ = typer.Exit()
        except:
            rprint("⚠️  [yellow]Unable to delete workspace directory[/yellow]")
            _ = typer.Exit()

    return delete
