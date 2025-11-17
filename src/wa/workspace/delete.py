import shutil

from pathlib import Path

from .read import read_workspace


def delete_workspace(
    workspace_name: str,
    workspaces_path: Path | None = None,
    force: bool = False,
) -> Path:
    """
    Deletes entire workspace folder and subfolders.
    """
    workspace = read_workspace(
        workspace_name=workspace_name, workspaces_path=workspaces_path
    )

    if not force:
        if len(workspace.folders) > 0:
            raise FileExistsError(
                "Workspace currently has folders, use --force to delete"
            )

    shutil.rmtree(workspace.path)

    return workspace.path
