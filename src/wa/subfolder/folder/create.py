from pathlib import Path

from wa.workspace.model import Workspace
from wa.workspace.utils import get_project_root


def create_workspace_folder(
    name: str,
    workspaces_folder_path: Path | None = None,
    force: bool = False,
    **kwargs,
) -> Workspace:
    """
    Create Workspace class object and folder.
    """

    # Use the out_path if provided, otherwise default to package out_path.
    if workspaces_folder_path is None:
        workspaces_folder_path = get_project_root() / "workspaces"

    # Create the `out` directory if it doesn't exist.
    workspaces_folder_path.mkdir(exist_ok=True)

    workspace_path = workspaces_folder_path / name

    if workspace_path.exists() and not force:
        raise FileExistsError("Workspace already exists")

    workspace = Workspace(
        name=name, workspaces_folder_path=workspaces_folder_path, **kwargs
    )
    workspace.save()

    return workspace
