import typer

from wa.cli.utils import print_list
from wa.workspace.list import list_workspaces


def register_list(app: typer.Typer):

    @app.command(name="list")
    def list() -> None:
        """List created workspaces."""
        workspace_names = list_workspaces()
        print_list("Workspaces", workspace_names)

    return list
