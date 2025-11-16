import shutil

from pathlib import Path

from .read import read_workspace_folder


def delete_workspace_folder(
    name: str,
    workspaces_folder_path: Path | None = None,
    force: bool = False,
) -> Path:
    """
    Deletes entire workspace folder and subfolders.
    """
    workspace = read_workspace_folder(
        name=name, workspaces_folder_path=workspaces_folder_path
    )

    if not force:
        if len(workspace.subfolders) > 0:
            raise FileExistsError(
                "Workspace currently has subfolders, use --force to delete"
            )

    shutil.rmtree(workspace.path)

    return workspace.path
