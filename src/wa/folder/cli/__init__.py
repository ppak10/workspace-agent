from .__main__ import app
from .create import register_workspace_folder_create
from .delete import register_workspace_folder_delete
from .list import register_workspace_folder_list
from .read import register_workspace_folder_read

_ = register_workspace_folder_create(app)
_ = register_workspace_folder_delete(app)
_ = register_workspace_folder_list(app)
_ = register_workspace_folder_read(app)

__all__ = ["app"]
