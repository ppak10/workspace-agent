from pathlib import Path

from wa.utils import get_project_root
from wa.workspace.models.workspace import Workspace
from wa.workspace.models.workspace_folder import WorkspaceFolder

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
    name_or_path: str | Path | list[str],
    workspace_name: str,
    workspaces_path: Path | None = None,
    append_timestamp: bool = False,
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

    # Use workspace.create_folder() to create the folder
    return workspace.create_folder(
        name_or_path=name_or_path,
        append_timestamp=append_timestamp,
        force=force,
        **kwargs,
    )
