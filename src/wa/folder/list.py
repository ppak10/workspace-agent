import os

from pathlib import Path

from wa.utils import get_project_root


def list_workspace_folders(
    workspaces_folder_path: Path | None = None,
) -> list[str] | None:
    """
    Lists workspace directories with config file under workspaces folder.
    Doesn't load the workspace object and doesn't validate the config.
    Intended for getting a list of all workspaces.
    """
    if workspaces_folder_path is None:
        workspaces_folder_path = get_project_root() / "workspaces"

    if not workspaces_folder_path.exists():
        os.makedirs(workspaces_folder_path)

    if not workspaces_folder_path.is_dir():
        raise FileNotFoundError

    workspace_folders = []
    for workspace_dir in workspaces_folder_path.iterdir():
        if workspace_dir.is_dir():
            workspace_config_path = workspace_dir / "workspace.json"
            if workspace_config_path.exists():
                workspace_folders.append(workspace_dir.name)

    return [
        workspace_dir.name
        for workspace_dir in workspaces_folder_path.iterdir()
        if workspace_dir.is_dir()
    ]
