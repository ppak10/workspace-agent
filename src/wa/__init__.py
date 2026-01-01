from importlib.metadata import version, PackageNotFoundError

__author__: str = "Peter Pak"
__email__: str = "ppak10@gmail.com"
__version__: str

try:
    __version__ = version("workspace-agent")
except PackageNotFoundError:
    __version__ = "unknown"

from .workspace.create import create_workspace, create_workspace_folder
from .workspace.delete import delete_workspace
from .workspace.list import list_workspaces
from .workspace.read import read_workspace, read_workspace_folder

from .workspace.models.workspace import Workspace
from .workspace.models.workspace_base_model import WorkspaceBaseModel
from .workspace.models.workspace_folder import WorkspaceFolder

__all__ = [
    "create_workspace",
    "create_workspace_folder",
    "delete_workspace",
    "list_workspaces",
    "read_workspace",
    "read_workspace_folder",
    "Workspace",
    "WorkspaceBaseModel",
    "WorkspaceFolder",
]
