from pathlib import Path

from wa.models import WorkspaceSubfolder
from wa.folder.read import read_workspace_folder


def read_workspace_subfolder(
    workspace_subfolder_name: str | list[str],
    workspace_folder_name: str,
    workspaces_folder_path: Path | None = None,
) -> WorkspaceSubfolder:
    """
    Loads workspace folder config file and returns Workspace object.
    """

    workspace = read_workspace_folder(
        name=workspace_folder_name, workspaces_folder_path=workspaces_folder_path
    )

    if isinstance(workspace_subfolder_name, str):
        if workspace_subfolder_name not in workspace.subfolders.keys():
            raise Exception(
                f"Workspace subfolder `{workspace_subfolder_name}` not found in workspace."
            )

        return workspace.subfolders[workspace_subfolder_name]

    elif isinstance(workspace_subfolder_name, list):

        if len(workspace_subfolder_name) < 1:
            raise Exception("No subfolder names provided.")

        subfolder_names = workspace_subfolder_name.copy()

        if workspace_subfolder_name[0] not in subfolder_names:
            raise FileNotFoundError(
                f"Workspace subfolder `{workspace_subfolder_name[0]}` not found in workspace."
            )

        for index, subfolder_name in enumerate(subfolder_names):
            if index == 0:
                subfolder = workspace.subfolders[subfolder_name]
            else:
                if subfolder_name not in subfolder.subfolders.keys():
                    raise FileNotFoundError(
                        f"Workspace subfolder `{subfolder_names[-1]}` not found in workspace, missing `{subfolder_name}`."
                    )
                subfolder = subfolder.subfolders[subfolder_name]

        return subfolder
