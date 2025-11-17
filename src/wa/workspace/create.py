from pathlib import Path

from wa.models import Workspace, WorkspaceFolder
from wa.utils import get_project_root

from .read import read_workspace


def create_workspace(
    workspace_name: str,
    workspaces_path: Path | None = None,
    force: bool = False,
    **kwargs,
) -> Workspace:
    """
    Create Workspace class object and folder.
    """

    # Use the out_path if provided, otherwise default to package out_path.
    if workspaces_path is None:
        workspaces_path = get_project_root() / "workspaces"

    # Create the `out` directory if it doesn't exist.
    workspaces_path.mkdir(parents=True, exist_ok=True)

    workspace_path = workspaces_path / workspace_name

    if workspace_path.exists() and not force:
        raise FileExistsError("Workspace already exists")

    workspace = Workspace(
        name=workspace_name, workspaces_path=workspaces_path, **kwargs
    )
    workspace.save()

    return workspace


def create_workspace_folder(
    workspace_folder_name: str | list[str],
    workspace_name: str,
    workspaces_path: Path | None = None,
    force: bool = False,
    **kwargs,
) -> WorkspaceFolder:
    """
    Create workspace subfolder class object and folder.
    """
    if workspaces_path is None:
        workspaces_path = get_project_root() / "workspaces"

    workspace_path = workspaces_path / workspace_name

    # Creates workspace if not existant.
    if not workspace_path.exists():
        workspace = create_workspace(
            workspace_name=workspace_name,
            workspaces_path=workspaces_path,
        )
    else:
        workspace = read_workspace(
            workspace_name=workspace_name,
            workspaces_path=workspaces_path,
        )

    if isinstance(workspace_folder_name, str):
        workspace_folder = WorkspaceFolder(name=workspace_folder_name, **kwargs)
    elif isinstance(workspace_folder_name, list):

        folder_names = workspace_folder_name.copy()
        folder_names.reverse()

        for index, name in enumerate(folder_names):
            if index == 0:
                workspace_folder = WorkspaceFolder(name=name, **kwargs)
            else:
                folders = {
                    workspace_folder.name: workspace_folder,
                }
                workspace_folder = WorkspaceFolder(name=name, folders=folders, **kwargs)

    folder = workspace.initialize_folder(folder=workspace_folder, force=force)

    return folder
