import typer

from pathlib import Path
from rich import print as rprint

from .options import WorkspaceOption
from wa.utils import get_project_root


def print_list(name: str, values: list[str] | None = None):
    rprint(f"\n  {name}:")
    if values is None:
        rprint(f"  ⚠️  [yellow]No {name} found.[/yellow]")
    else:
        for index, value in enumerate(values):
            rprint(f"  {index + 1}. [cyan]{value}[/cyan]")


def get_workspace_path(
    workspace: WorkspaceOption,
    config_file: str = "workspace.json",
    workspaces_folder_name: str = "workspaces",
) -> Path:
    """
    Checks for workspace config file in current directory or throws error.
    """
    if workspace is not None:
        project_root = get_project_root()
        workspace_dir = project_root / workspaces_folder_name / workspace

    else:
        # Check for workspace config file in current directory
        workspace_dir = Path.cwd()

    workspace_config_path = workspace_dir / config_file

    if not workspace_config_path.exists():
        rprint(
            f"❌ [red]This is not a valid workspace folder. `{workspace_config_path}` not found.[/red]"
        )
        raise typer.Exit(code=1)

    return workspace_dir
