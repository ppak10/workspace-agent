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

__all__ = [
    "create_workspace",
    "create_workspace_folder",
    "delete_workspace",
    "list_workspaces",
    "read_workspace",
    "read_workspace_folder",
]
