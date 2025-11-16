from pathlib import Path

from wa.workspace.model import Workspace
from wa.workspace.utils import get_project_root


def create_workspace_subfolder(
    name: str,
    subfolder: str,
    out_path: Path | None = None,
    force: bool = False,
    **kwargs,
) -> Workspace:
    """
    Create a subfolder within a Workspace and register it in workspace.json.
    """

    # Use the out_path if provided, otherwise default to package out_path.
    if out_path is None:
        out_path = get_project_root() / "out"

    if not out_path.exists() or not out_path.is_dir():
        raise FileNotFoundError

    workspace_dict_path = out_path / name / "workspace.json"

    if not workspace_dict_path.exists():
        raise FileNotFoundError

    subfolder_path = out_path / name / subfolder

    if subfolder_path.exists() and not force:
        raise FileExistsError("Workspace subfolder already exists")

    workspace = Workspace.load(workspace_dict_path)
    workspace.add_subfolder(subfolder)

    return workspace
