import typer

from wa.cli.utils import print_list


def register_workspace_folder_list(app: typer.Typer):
    from wa.folder.list import list_workspace_folders

    @app.command(name="list")
    def workspace_list() -> None:
        """List created workspaces."""
        workspace_names = list_workspace_folders()
        print_list("Workspaces", workspace_names)

    _ = workspace_list
