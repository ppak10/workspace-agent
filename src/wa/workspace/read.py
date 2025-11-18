from pathlib import Path

from wa.models import Workspace, WorkspaceFolder
from wa.utils import get_project_root


def include_files_recursive(
    folders: dict[str, WorkspaceFolder], parent_path: Path
) -> None:
    """
    Recursively populate files for all folders.
    """
    for name, folder in folders.items():
        folder_path = parent_path / name
        folder.path = folder_path
        if folder_path.exists():
            folder.files = [f.name for f in folder_path.iterdir() if f.is_file()]
        if folder.folders:
            include_files_recursive(folder.folders, folder_path)


def read_workspace(
    workspace_name: str,
    workspaces_path: Path | None = None,
    include_files: bool = False,
) -> Workspace:
    """
    Loads workspace folder config file and returns Workspace object.
    """

    # Use the out_path if provided, otherwise default to package out_path.
    if workspaces_path is None:
        workspaces_path = get_project_root() / "workspaces"

    if not workspaces_path.exists():
        raise FileNotFoundError("Workspaces folder does not exist.")

    workspace_path = workspaces_path / workspace_name

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace folder: `{workspace_name}` does not exist.")

    workspace_file = workspace_path / "workspace.json"

    if not workspace_path.exists():
        raise FileNotFoundError(
            f"Config file (`workspace.json`) for workspace `{workspace_name}` does not exist."
        )

    workspace = Workspace.load(workspace_file)

    # Populate files recursively if requested
    if include_files:
        include_files_recursive(workspace.folders, workspace.path)
        workspace.files = [f.name for f in workspace.path.iterdir() if f.is_file()]

    return workspace


def read_workspace_folder(
    workspace_folder_name: str | list[str],
    workspace_name: str,
    workspaces_path: Path | None = None,
    include_files: bool = False,
) -> WorkspaceFolder:
    """
    Loads workspace folder config file and returns Workspace object.
    """

    workspace = read_workspace(
        workspace_name=workspace_name,
        workspaces_path=workspaces_path,
    )

    if isinstance(workspace_folder_name, str):
        if workspace_folder_name not in workspace.folders.keys():
            raise Exception(
                f"Workspace subfolder `{workspace_folder_name}` not found in workspace."
            )

        folder = workspace.folders[workspace_folder_name]

    elif isinstance(workspace_folder_name, list):

        if len(workspace_folder_name) < 1:
            raise Exception("No folder names provided.")

        folder_names = workspace_folder_name.copy()

        if workspace_folder_name[0] not in folder_names:
            raise FileNotFoundError(
                f"Workspace subfolder `{workspace_folder_name[0]}` not found in workspace."
            )

        for index, folder_name in enumerate(folder_names):
            if index == 0:
                folder = workspace.folders[folder_name]
            else:
                if folder_name not in folder.folders.keys():
                    raise FileNotFoundError(
                        f"Workspace folder `{folder_names[-1]}` not found in workspace, missing `{folder_name}`."
                    )
                folder = folder.folders[folder_name]

    # Populate files if requested
    if include_files and folder.path.exists():
        include_files_recursive(folder.folders, folder.path)
        folder.files = [f.name for f in folder.path.iterdir() if f.is_file()]

    return folder
