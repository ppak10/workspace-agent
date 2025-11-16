from pathlib import Path

from wa.models import Workspace
from wa.utils import get_project_root


def read_workspace_folder(
    name: str,
    workspaces_folder_path: Path | None = None,
) -> Workspace:
    """
    Loads workspace folder config file and returns Workspace object.
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

    return workspace
