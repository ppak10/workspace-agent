import shutil

from pathlib import Path

from wa.workspace.model import Workspace
from wa.workspace.utils import get_project_root


def delete_workspace_folder(
    name: str,
    workspaces_folder_path: Path | None = None,
    force: bool = False,
) -> Path:
    """
    Deletes entire workspace folder and subfolders.
    """

    # Use the out_path if provided, otherwise default to package out_path.
    if workspaces_folder_path is None:
        workspaces_folder_path = get_project_root() / "workspaces"

    if not workspaces_folder_path.exists():
        raise FileNotFoundError("Workspaces folder does not exist.")

    workspace_path = workspaces_folder_path / name

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace folder: `{name}` does not exist.")

    workspace_file = workspace_path / "workspace.json"

    if not workspace_path.exists():
        raise FileNotFoundError(
            f"Config file (`workspace.json`) for workspace folder `{name}` does not exist."
        )

    workspace = Workspace.load(workspace_file)

    if not force:
        if len(workspace.subfolders) > 0:
            raise Exception("Workspace currently has subfolders, use --force to delete")

    shutil.rmtree(workspace_path)

    return workspace_path
