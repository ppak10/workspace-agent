import os

from pathlib import Path

from wa.workspace.utils import get_project_root


def list_workspaces(workspaces_folder_path: Path | None = None) -> list[str] | None:
    """
    Lists workspace directories within out_path
    """
    if workspaces_folder_path is None:
        workspaces_folder_path = get_project_root() / "workspaces"

    if not workspaces_folder_path.exists():
        os.makedirs(workspaces_folder_path)

    if not workspaces_folder_path.is_dir():
        raise FileNotFoundError

    return [
        workspace_dir.name
        for workspace_dir in workspaces_folder_path.iterdir()
        if workspace_dir.is_dir()
    ]


def list_workspace_subfolders(
    name: str, workspaces_folder_path: Path | None = None
) -> list[str] | None:
    """
    Lists subfolders within a workspace.
    """
    if workspaces_folder_path is None:
        workspaces_folder_path = get_project_root() / "workspaces"

    if not workspaces_folder_path.exists() or not workspaces_folder_path.is_dir():
        raise FileNotFoundError

    workspace_path = workspaces_folder_path / name

    if not workspace_path.exists() or not workspaces_folder_path.is_dir():
        raise FileNotFoundError

    return [
        subfolder.name for subfolder in workspace_path.iterdir() if subfolder.is_dir()
    ]


def list_workspace_subfolder_content(
    name: str, subfolder: str, workspaces_folder_path: Path | None = None
) -> list[str] | None:
    """
    Lists the contents within a workspace subfolder.
    """

    if workspaces_folder_path is None:
        workspaces_folder_path = get_project_root() / "workspaces"

    if not workspaces_folder_path.exists() or not workspaces_folder_path.is_dir():
        raise FileNotFoundError

    subfolder_path = workspaces_folder_path / name / subfolder

    return [content.name for content in subfolder_path.iterdir()]
