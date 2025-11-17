from pathlib import Path

from wa.models import WorkspaceSubfolder
from wa.folder.read import read_workspace_folder


def create_workspace_subfolder(
    workspace_subfolder_name: str | list[str],
    workspace_folder_name: str,
    workspaces_folder_path: Path | None = None,
    force: bool = False,
    **kwargs,
) -> WorkspaceSubfolder:
    """
    Create workspace subfolder class object and folder.
    """

    workspace = read_workspace_folder(
        name=workspace_folder_name,
        workspaces_folder_path=workspaces_folder_path,
    )

    if isinstance(workspace_subfolder_name, str):
        workspace_subfolder = WorkspaceSubfolder(
            name=workspace_subfolder_name, **kwargs
        )
    elif isinstance(workspace_subfolder_name, list):

        subfolder_names = workspace_subfolder_name.copy()
        subfolder_names.reverse()

        for index, name in enumerate(subfolder_names):
            if index == 0:
                workspace_subfolder = WorkspaceSubfolder(name=name, **kwargs)
            else:
                subfolders = {
                    workspace_subfolder.name: workspace_subfolder,
                }
                workspace_subfolder = WorkspaceSubfolder(
                    name=name, subfolders=subfolders, **kwargs
                )

    subfolder = workspace.initialize_subfolder(
        subfolder=workspace_subfolder,
        force=force,
    )

    return subfolder
